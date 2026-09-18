"""S07 - the repair loop, bounded.

The model produces a ticket; a deterministic scorer judges it; on failure the
harness re-asks **once per attempt, at most `cap` times**, feeding back only a
curated failure view. Three rules make the loop trustworthy:

  * **bounded** - `cap` attempts, never an open retry storm;
  * **curated context** - the retry sees the brief plus the named defects, not
    the failed drafts it would otherwise imitate;
  * **honest end** - every run returns a `stop_reason` from :data:`STOP_REASONS`,
    and nothing ships unless it passed.

A defect in the *request* (an injected brief, an order that is unsafe for the
declared allergy no matter how you write it) never enters the loop: it stops as
`policy_violation`, because regeneration cannot fix a bad request.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from cafe import detect, domain

try:  # S04 owns the ticket contract; S07 must still work before it lands.
    from cafe import schema
except ImportError:  # pragma: no cover - only before S04 exists
    schema = None

__all__ = [
    "STOP_REASONS",
    "CAP_DEFAULT",
    "brief_for",
    "contract_errors",
    "score_ticket",
    "failure_view",
    "retry_messages",
    "make_scripted_generator",
    "parse_ticket",
    "make_model_generator",
    "repair_ticket",
]

STOP_REASONS = frozenset({"passed", "retries_exhausted", "policy_violation"})
CAP_DEFAULT = 3

TICKET_SYSTEM = (
    "You work the counter. Return ONLY a JSON object with the keys "
    '"items" (list of menu strings) and "table" (integer). No extra text.'
)


def brief_for(spec: dict) -> str:
    """The customer's request, as the model receives it.

    ``spec["request"]`` carries the customer's own words when they matter (S06's
    untrusted text); otherwise the brief is built from the structured spec.
    """
    order = spec.get("request") or f"Order for table {spec['table']}: {', '.join(spec['items'])}."
    allergy = (
        f" Heads-up: the customer declared an allergy to {spec['allergen']}."
        if spec.get("allergen")
        else ""
    )
    return f"{order}{allergy} Return the ticket."


def contract_errors(ticket: Any) -> list[str]:
    """S04's contract when it exists; S05's local floor otherwise. Never optional."""
    if schema is not None:
        validator = getattr(schema, "validate_ticket", None)
        if validator is not None:
            return list(validator(ticket))
        generic = getattr(schema, "validate", None)
        ticket_schema = getattr(schema, "TICKET_SCHEMA", None)
        if generic is not None and ticket_schema is not None:
            return list(generic(ticket, ticket_schema))
    return list(detect.validate_ticket(ticket))


def score_ticket(ticket: Any, spec: dict) -> dict:
    """The deterministic tier: structure, safety and availability - not quality."""
    failures: list[dict] = []
    for error in contract_errors(ticket):
        failures.append({"check": "contract", "span": None, "constraint": error})
    items = ticket.get("items") if isinstance(ticket, dict) else None
    if isinstance(items, list):
        allergen = spec.get("allergen")
        if allergen and ticket.get("allergen_checked") is not True:
            failures.append({
                "check": "allergen_checked",
                "span": None,
                "constraint": (
                    "allergen_checked must be true: the customer declared an "
                    "allergy, so the menu was checked (S04's field, enforced)"
                ),
            })
        for item in items:
            if allergen and detect.contains_allergen(item, allergen):
                failures.append({
                    "check": "allergen",
                    "span": item,
                    "constraint": (
                        f"'{item}' contains {allergen}: the customer declared it "
                        "- swap it for something on the menu that doesn't"
                    ),
                })
            if item in domain.EIGHTY_SIXED:
                failures.append({
                    "check": "availability",
                    "span": item,
                    "constraint": (
                        f"'{item}' is 86'd tonight - offer the closest "
                        "alternative"
                    ),
                })
    return {"passed": not failures, "failures": failures}


def failure_view(failures: Iterable[dict], attempt: int) -> str:
    """The retry's only new information: name the check, quote the span, state it."""
    lines = [
        f"[feedback] ticket {attempt} rejected - fix exactly this, "
        "change nothing else:"
    ]
    lines += [f"- {failure['constraint']}" for failure in failures]
    return "\n".join(lines)


def retry_messages(
    brief: str,
    failures: Iterable[dict],
    attempt: int,
    mode: str = "curated",
) -> list[dict]:
    """What the retry actually gets to see. This is the recorded decision.

    ``naive`` re-sends the identical brief - resampling, not repair. ``curated``
    drops the failed drafts and keeps only the failure view, so the model cannot
    imitate the defect it is being asked to fix.
    """
    if mode == "naive":
        return [{"role": "user", "content": brief}]
    if mode != "curated":
        raise ValueError(mode)
    return [{"role": "user", "content": brief + "\n\n" + failure_view(failures, attempt)}]


def _request_is_policy_blocked(brief: str, spec: dict) -> dict | None:
    """Request-level defects that no amount of regeneration can repair."""
    pattern = detect.screen_injection(detect.normalize(brief), detect.POLICY)
    if pattern:
        return {"reason": "injection in the request", "detail": pattern}
    allergen = spec.get("allergen")
    items = list(spec.get("items") or [])
    if allergen and items and all(detect.contains_allergen(i, allergen) for i in items):
        return {
            "reason": f"every requested item contains {allergen}; the request is unsafe",
            "detail": items,
        }
    return None


def repair_ticket(
    spec: dict,
    generator: Callable[[list[dict]], Any],
    *,
    cap: int = CAP_DEFAULT,
    mode: str = "curated",
) -> dict:
    """Score -> re-ask with the failure view -> re-score, at most `cap` times.

    `generator(messages)` returns a candidate ticket (or anything, if the model
    returned junk). `stop_reason` is always one of :data:`STOP_REASONS`.
    """
    brief = brief_for(spec)
    blocked = _request_is_policy_blocked(brief, spec)
    if blocked is not None:
        return {
            "stop_reason": "policy_violation",
            "ticket": None,
            "attempts": [],
            "brief": brief,
            "blocked": blocked,
        }
    messages = retry_messages(brief, [], 0, mode)
    attempts: list[dict] = []
    for number in range(1, cap + 1):
        candidate = generator(messages)
        result = score_ticket(candidate, spec)
        attempts.append({"n": number, "ticket": candidate, "failures": result["failures"]})
        if result["passed"]:
            return {
                "stop_reason": "passed",
                "ticket": candidate,
                "attempts": attempts,
                "brief": brief,
            }
        messages = retry_messages(brief, result["failures"], number, mode)
    return {
        "stop_reason": "retries_exhausted",
        "ticket": None,
        "attempts": attempts,
        "brief": brief,
    }


def make_scripted_generator(outputs: Iterable[Any]) -> Callable[[list[dict]], Any]:
    """A scripted model: a queue of candidate tickets, for tests and notebooks."""
    queue = list(outputs)

    def generator(_messages: list[dict]) -> Any:
        if not queue:
            return {}
        return queue.pop(0)

    return generator


def parse_ticket(text: Any) -> Any:
    """Pull one JSON ticket out of a model reply. Junk stays junk - the scorer says so."""
    if not isinstance(text, str):
        return {"items": None, "table": None}
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return {"items": None, "table": None}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"items": None, "table": None}


def make_model_generator(client: Any, *, temperature: float = 0.0) -> Callable[[list[dict]], Any]:
    """A generator backed by the one model seam the notebook already holds."""

    def generator(messages: list[dict]) -> Any:
        body = client.chat(
            [{"role": "system", "content": TICKET_SYSTEM}, *messages],
            temperature=temperature,
        )
        return parse_ticket(body["choices"][0]["message"].get("content"))

    return generator
