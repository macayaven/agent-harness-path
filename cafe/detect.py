"""S06 - layered detection: an ordered pipeline over untrusted customer text.

Every customer message is untrusted input. The pipeline routes each one to
exactly one action:

  * ``blocked`` - a prompt injection: the model never sees the message.
  * ``handoff`` - an allergen question the data cannot clear: a human takes over.
  * ``refuse``  - off-menu or out of scope (money, legal, card data).
  * ``pass``    - screened, safe and in scope: the model may reply.

The **order is the safety invariant**: the deterministic keyword floor runs
*before any model call*, then the model-based allergen classifier, then the
scope governor. A trigger is a terminal state with its own stop reason - never a
log line and continue.

All behaviour lives in :data:`POLICY`, and every safety decision that can be
made from data - is this item on the menu, does it contain this allergen - is
made from ``cafe.tools`` data, never from a model's opinion. The model may say
"an allergy was declared"; only the menu may say "this is safe".
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

from cafe import domain
from cafe.consent import IRREVERSIBLE_ACTION, validate_ticket

__all__ = [
    "POLICY",
    "ACTIONS",
    "normalize",
    "screen_injection",
    "declared_allergens",
    "named_items",
    "contains_allergen",
    "lexical_classifier",
    "allergen_verdict",
    "scope_verdict",
    "decide",
    "screen_ticket",
    "evaluate",
    "mock_assistant",
]

ACTIONS = ("handoff", "refuse", "blocked", "pass")

# --- policy as data --------------------------------------------------------
# A behaviour change is a data edit here, reviewable as a diff. The injection
# list deliberately includes the irreversible tool name: a customer message that
# names it is never trusted text.

POLICY: dict[str, dict] = {
    "injection": {
        "patterns": (
            "ignore all previous",
            "ignore previous",
            "ignore your instructions",
            "disregard previous",
            "previous instructions",
            "system prompt",
            "forward this",
            "bank details",
            "card data",
            "card number",
            "credit card",
            IRREVERSIBLE_ACTION,
        ),
    },
    "allergen": {
        # The classifier (model-based in production) decides *whether* an allergy
        # was declared; the surface words below only map to canonical allergens.
        "threshold": 0.5,
        "surface": {
            "milk": "milk",
            "dairy": "milk",
            "lactose": "milk",
            "gluten": "gluten",
            "wheat": "gluten",
            "egg": "egg",
            "eggs": "egg",
            "tree nuts": "nuts",
            "peanut": "nuts",
            "walnut": "nuts",
            "fish": "fish",
            "shellfish": "shellfish",
            "soy": "soy",
            "sesame": "sesame",
        },
    },
    "scope": {
        "markers": (
            "chargeback",
            "refund",
            "lawyer",
            "lawsuit",
            "legal",
            "court",
            "tax",
            "tip",
        ),
        # words for things this café plainly does not serve tonight
        "off_menu_words": ("burger", "pizza", "beer", "sushi"),
        "refusal_text": (
            "That's not counter business: for refunds, legal matters, or payment "
            "data, talk to the shift lead. Can I help with the menu?"
        ),
    },
}


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace - attackers pad and vary casing."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def screen_injection(norm_text: str, policy: dict) -> str | None:
    """The deterministic keyword floor. Returns the pattern that fired, or None.

    Cheap, free, auditable - and it runs before anything model-shaped sees the
    text, which is the point. A floor, not a ceiling.
    """
    for pattern in policy["injection"]["patterns"]:
        if pattern in norm_text:
            return pattern
    return None


def declared_allergens(norm_text: str, policy: dict) -> list[str]:
    """Surface words -> canonical EU allergen names, in order, without repeats."""
    found: list[str] = []
    for surface, canonical in policy["allergen"]["surface"].items():
        if surface in norm_text and canonical not in found:
            found.append(canonical)
    return found


def named_items(norm_text: str) -> list[str]:
    """Menu items the message actually names. Data, not inference."""
    return [item for item in domain.MENU if item in norm_text]


def contains_allergen(item: str, allergen: str) -> bool:
    """Ask the menu, not the model. `None` (unknown item) is never 'safe'."""
    entry = domain.MENU.get(item)
    if entry is None:
        return True  # unknown is treated as unsafe, the conservative default
    return allergen.strip().lower() in [a.lower() for a in entry["allergens"]]


def lexical_classifier(norm_text: str) -> dict:
    """Readable stand-in for the model-based classifier.

    Returns an API-shaped payload: label + confidence + the cues that fired. A
    real classifier is semantic; that difference is the lesson, not a defect.
    """
    strong = [c for c in ("allerg", "intoleran", "celiac")
              if c in norm_text]
    weak = [c for c in ("milk", "gluten", "egg", "tree nuts", "lactose",
                        "gluten-free", "lactose-free")
            if c in norm_text]
    confidence = min(1.0, 0.5 * len(strong) + 0.2 * len(weak))
    return {
        "label": "allergen" if confidence > 0 else "benign",
        "confidence": round(confidence, 2),
        "cues": strong + weak,
    }


def allergen_verdict(
    norm_text: str,
    policy: dict,
    classifier: Callable[[str], dict],
    *,
    threshold: float | None = None,
) -> dict | None:
    """Layer 2. The classifier decides intent; the menu data decides safety.

    Returns a terminal verdict, or None when the message may continue.
    """
    result = classifier(norm_text)
    confidence = float(result.get("confidence") or 0.0)
    cut = policy["allergen"]["threshold"] if threshold is None else threshold
    if confidence < cut or confidence <= 0:
        return None
    allergens = declared_allergens(norm_text, policy)
    items = named_items(norm_text)
    if not allergens or not items:
        # The classifier says there is an allergen question but we cannot pin it
        # to menu data: hand off rather than guess. Never confirm safety blind.
        return {
            "action": "handoff",
            "layer": "allergen classifier",
            "detail": result.get("cues", []),
            "confidence": confidence,
            "stop_reason": "safety_handoff",
            "response": domain.ALLERGEN_REFUSAL,
        }
    unsafe = [
        item
        for item in items
        for allergen in allergens
        if contains_allergen(item, allergen)
    ]
    if unsafe:
        return {
            "action": "handoff",
            "layer": "allergen data",
            "detail": {"items": unsafe, "allergens": allergens},
            "confidence": confidence,
            "stop_reason": "safety_handoff",
            "response": domain.ALLERGEN_REFUSAL,
        }
    return None  # declared, but the named items are clear: continue


def scope_verdict(norm_text: str, policy: dict) -> dict | None:
    """Layer 3, the governor. Money and legal out of scope; availability data."""
    for marker in policy["scope"]["markers"]:
        if marker in norm_text:
            return {
                "action": "refuse",
                "layer": "scope governor",
                "detail": marker,
                "stop_reason": "out_of_scope",
                "response": policy["scope"]["refusal_text"],
            }
    for word in policy["scope"]["off_menu_words"]:
        if word in norm_text:
            return {
                "action": "refuse",
                "layer": "scope governor",
                "detail": word,
                "stop_reason": "off_menu",
                "response": domain.OFF_MENU_REFUSAL,
            }
    for item in named_items(norm_text):
        if item in domain.EIGHTY_SIXED:
            return {
                "action": "refuse",
                "layer": "scope governor",
                "detail": item,
                "stop_reason": "off_menu",
                "response": domain.OFF_MENU_REFUSAL,
            }
    return None


def decide(
    text: str,
    policy: dict | None = None,
    *,
    classifier: Callable[[str], dict] | None = None,
    threshold: float | None = None,
    use_floor: bool = True,
    use_classifier: bool = True,
    use_scope: bool = True,
) -> dict:
    """Route one untrusted message. The layer order is the safety invariant."""
    policy = POLICY if policy is None else policy
    classify = classifier or lexical_classifier
    norm = normalize(text)
    # 1. deterministic keyword floor - BEFORE any model call
    if use_floor:
        pattern = screen_injection(norm, policy)
        if pattern:
            return {
                "action": "blocked",
                "layer": "injection floor",
                "detail": pattern,
                "stop_reason": "injection_blocked",
            }
    # 2. model-based classifier (allergen intent)
    if use_classifier:
        verdict = allergen_verdict(norm, policy, classify, threshold=threshold)
        if verdict is not None:
            return verdict
    # 3. scope governor
    if use_scope:
        verdict = scope_verdict(norm, policy)
        if verdict is not None:
            return verdict
    # 4. screened, safe and in scope - the model may see it
    return {"action": "pass", "layer": "model", "stop_reason": "answered"}


def screen_ticket(
    ticket: dict,
    *,
    declared_allergen: str | None = None,
) -> dict:
    """Clearing a *ticket* (not a message): contract first, then allergen data.

    This is what S07 feeds its repair loop. The structural contract is S04/S05's
    `validate_ticket`; the safety layer is the menu, again - never a model.
    """
    errors = validate_ticket(ticket)
    if errors:
        return {"action": "refuse", "layer": "contract", "errors": errors}
    if declared_allergen:
        unsafe = [i for i in ticket["items"] if contains_allergen(i, declared_allergen)]
        if unsafe:
            return {
                "action": "handoff",
                "layer": "allergen data",
                "items": unsafe,
                "allergen": declared_allergen,
                "stop_reason": "safety_handoff",
            }
    return {"action": "pass", "layer": "allergen data", "stop_reason": "answered"}


def evaluate(
    bank: Iterable[tuple[str, str]],
    verbose: bool = True,
    **knobs: Any,
) -> dict:
    """Run a bank through `decide()`; count what matters, including false triggers."""
    rows = [(expected, text, decide(text, **knobs)) for expected, text in bank]
    if verbose:
        print(f"{'expected':<9} {'action':<9} {'layer':<20} message")
        for expected, text, decision in rows:
            mark = "" if decision["action"] == expected else "  <-- WRONG"
            print(f"{expected:<9} {decision['action']:<9} {decision['layer']:<20} "
                  f"{text[:46]}{mark}")
    false_triggers = [
        i for i, (expected, _, decision) in enumerate(rows)
        if expected == "pass" and decision["action"] != "pass"
    ]
    caught = sum(
        1 for expected, _, decision in rows
        if expected == "handoff" and decision["action"] == "handoff"
    )
    stopped = sum(
        1 for expected, _, decision in rows
        if expected == "blocked" and decision["action"] == "blocked"
    )
    summary = {
        "caught": caught,
        "handoff_total": sum(1 for expected, _, _ in rows if expected == "handoff"),
        "stopped": stopped,
        "blocked_total": sum(1 for expected, _, _ in rows if expected == "blocked"),
        "false_triggers": false_triggers,
    }
    if verbose:
        print(f"allergen handoffs: {caught}/{summary['handoff_total']}   "
              f"injections blocked: {stopped}/{summary['blocked_total']}   "
              f"false triggers: {len(false_triggers)} {false_triggers}")
    return summary


def mock_assistant(text: str) -> str:
    """Downstream mock model. Mimics production: it OBEYS injected instructions.

    Labelled, deliberately unsafe teaching material - do not "fix" it. Its
    willingness to hand over till data is the argument for a screen that runs
    before it ever sees the message.
    """
    low = text.lower()
    if "card" in low or "bank details" in low:
        # Placeholder digits only: a fixture must never carry a real-looking PAN.
        return ("Sure, no problem: the customer's card is 0000 0000 0000 0000 "
                "and the phone 000 000 000.")
    if "allerg" in low or "safe for" in low:
        return "Yes, don't worry, that's safe for your allergy."
    return "Coming right up! Anything else?"
