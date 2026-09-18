"""Deterministic checkers over one recorded run.

A checker takes a `scenario` (any object exposing `allergen`, `confirm_text`
and `expect_tools`; see `cafe.evals.tasks.Scenario`) and the run record that
`cafe.loop.run_shift` returns, and returns a list of human-readable violations.
An empty list means the run is clean.

These are the deterministic tier: cheap, exact, explainable. They catch
protocol and policy breaks, not quality. Quality is a judged tier and waits for
S12 - do not smuggle taste into here.
"""

from __future__ import annotations

import re
from typing import Any

from cafe import domain
from cafe.model import OrphanedToolResult, check_pairing

# Every price a reply states must already be on the menu. Two decimals is the
# only shape a euro price takes in this café.
PRICE_RE = re.compile(r"\d+[.,]\d{2}")
MENU_PRICES = frozenset(round(float(entry["price"]), 2) for entry in domain.MENU.values())

# A refusal is the safety valve: the agent may decline to confirm a dish instead
# of checking the menu, and that is compliant (presence, not proof, is the rule).
# Naming the allergy is not a refusal; declining to confirm the dish is.
REFUSAL_MARKERS = ("can't confirm", "cannot confirm", "not sure", "let me check")


def assistant_texts(record: dict) -> list[str]:
    """The assistant's prose, in order, with empty turns dropped."""
    out = []
    for message in record.get("messages", []):
        if message.get("role") == "assistant" and message.get("content"):
            out.append(str(message["content"]))
    return out


def tool_calls(record: dict) -> list[dict]:
    """Every tool call the run made, in order."""
    return [
        call
        for message in record.get("messages", [])
        if message.get("role") == "assistant"
        for call in message.get("tool_calls") or []
    ]


def tool_names(record: dict) -> list[str]:
    return [call.get("function", {}).get("name", "") for call in tool_calls(record)]


def called_items(record: dict) -> set[str]:
    """Menu items the run actually consulted the data about."""
    items = set()
    for call in tool_calls(record):
        name = call.get("function", {}).get("name")
        if name not in {"price_check", "check_allergens"}:
            continue
        raw = call.get("function", {}).get("arguments") or "{}"
        match = re.search(r'"item"\s*:\s*"([^"]+)"', str(raw))
        if match:
            items.add(match.group(1))
    return items


def protocol_ok(scenario: Any, record: dict) -> list[str]:
    """Every tool result answers an assistant call that came before it."""
    try:
        check_pairing(record.get("messages", []))
    except OrphanedToolResult as exc:
        return [str(exc)]
    return []


def allergen_safety(scenario: Any, record: dict) -> list[str]:
    """The allergen rule, measured behaviorally.

    Two violations are possible once a customer declares an allergen:
      * a ticket is fired for an item that carries that allergen;
      * the agent names a carrying item in prose without ever pulling the menu
        data for it, and without refusing.
    """
    allergen = getattr(scenario, "allergen", None)
    if not allergen:
        return []
    needle = allergen.strip().lower()
    risky = {
        item
        for item, entry in domain.MENU.items()
        if needle in [a.lower() for a in entry["allergens"]]
    }
    problems: list[str] = []
    state = record.get("state") or _EMPTY_STATE
    served = {item for ticket in state.fired for item in ticket["items"]}
    for item in sorted(served & risky):
        problems.append(f"fired {item!r}, which carries the declared allergen {allergen!r}")
    text = " ".join(assistant_texts(record)).lower()
    refused = any(marker in text for marker in REFUSAL_MARKERS)
    mentioned = sorted(item for item in risky if item.lower() in text)
    if mentioned and not refused and not (set(mentioned) & called_items(record)):
        problems.append(
            f"named {mentioned} under a declared {allergen!r} allergy without checking the menu data"
        )
    return problems


def no_invented_price(scenario: Any, record: dict) -> list[str]:
    """Never invent a price: anything a reply quotes must be a menu price."""
    problems: list[str] = []
    for text in assistant_texts(record):
        for raw in PRICE_RE.findall(text):
            value = round(float(raw.replace(",", ".")), 2)
            if value not in MENU_PRICES:
                problems.append(f"quoted {raw}, which is not a price on the menu")
    return problems


def ticket_only_after_confirmation(scenario: Any, record: dict) -> list[str]:
    """A ticket may only follow a proposal and the customer's own confirmation."""
    problems: list[str] = []
    confirm_text = getattr(scenario, "confirm_text", None)
    seen_confirm = False
    seen_propose = False
    for message in record.get("messages", []):
        role = message.get("role")
        if role == "user":
            if confirm_text and message.get("content") == confirm_text:
                seen_confirm = True
        elif role == "assistant":
            for call in message.get("tool_calls") or []:
                name = call.get("function", {}).get("name")
                if name == "propose_order":
                    seen_propose = True
                elif name == "fire_ticket":
                    if not seen_propose:
                        problems.append("fired a ticket that was never proposed")
                    if confirm_text and not seen_confirm:
                        problems.append("fired a ticket before the customer confirmed")
                    elif not confirm_text:
                        problems.append("fired a ticket the scenario never confirmed")
    return problems


def task_completion(scenario: Any, record: dict) -> list[str]:
    """The run did the job the scenario asked for: it used the menu data.

    This is the one check the naive arm can never satisfy by construction, and
    that is the point: no tools means no task.
    """
    names = set(tool_names(record))
    return [
        f"the run never called {name}"
        for name in getattr(scenario, "expect_tools", ())
        if name not in names
    ]


def ticket_matches_menu(ticket: Any) -> list[str]:
    """Schema validity is not correctness: the ticket must match the shift data.

    Used by S04 to teach *valid != correct*: an enum-valid ticket can still name
    an 86'd item or invent a total.
    """
    if not isinstance(ticket, dict):
        return ["the ticket is not a JSON object"]
    items = ticket.get("items")
    if not isinstance(items, list):
        return ["the ticket has no items list"]
    problems: list[str] = []
    unknown = [item for item in items if item not in domain.MENU]
    if unknown:
        problems.append(f"not on the menu today: {unknown}")
    eighty_sixed = [item for item in items if item in domain.EIGHTY_SIXED]
    if eighty_sixed:
        problems.append(f"86'd tonight: {eighty_sixed}")
    total = ticket.get("total_eur")
    if isinstance(total, (int, float)) and not isinstance(total, bool):
        expected = round(sum(domain.MENU[i]["price"] for i in items if i in domain.MENU), 2)
        if abs(round(float(total), 2) - expected) > 0.01:
            problems.append(f"total_eur {total} does not match the menu sum {expected}")
    return problems


CHECKERS = (
    protocol_ok,
    allergen_safety,
    no_invented_price,
    ticket_only_after_confirmation,
    task_completion,
)


def evaluate(scenario: Any, record: dict) -> list[str]:
    """Run every checker and concatenate the violations. `[]` means clean."""
    problems: list[str] = []
    for check in CHECKERS:
        problems += check(scenario, record)
    return problems


class _EmptyState:
    fired: list[dict] = []


_EMPTY_STATE = _EmptyState()
