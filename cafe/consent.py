"""S05 - the consent gate: propose, confirm, and only then fire.

`cafe.tools.fire_ticket` is the one irreversible action in the café. S01 let the
model reach it directly. This module puts a gate in front: the model *proposes*
a ticket, the customer confirms it (approve / edit / reject), and only the
approved ticket may reach the kitchen.

Three semantics, pinned here because they are the whole lesson:

  * **reject leaves zero side effects** - no ticket, no tool log, no order;
  * an **edit** rebinds the ticket that actually executes: the approved object,
    never the model's original request, is what fires;
  * a **violation** aborts by default; `degrade` fires exactly the approved
    ticket while logging, loudly, what it refused.

The gate is not the dialog. The gate is the check, and it runs before dispatch.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from cafe import domain
from cafe.tools import OrderState, dispatch
from cafe.tools import fire_ticket as _fire_ticket

try:  # S04 owns the ticket contract; S05 must still work before it lands.
    from cafe import schema
except ImportError:  # pragma: no cover - only before S04 exists
    schema = None

__all__ = [
    "IRREVERSIBLE_ACTION",
    "DECISIONS",
    "REQUIRED_FIELDS",
    "enrich_ticket",
    "validate_ticket",
    "render_ticket",
    "make_responder",
    "consent_gate",
    "check_fire",
    "fire_requested",
    "run_shift",
]

# The name the fence keys off. Only `fire_requested` may call the real tool.
IRREVERSIBLE_ACTION = "fire_ticket"

# Decision tokens are code, not dialogue; the render below is what the customer reads.
DECISIONS = ("approve", "edit", "reject")

# S04's ticket contract, carried forward. The gate never lets a ticket that fails
# these through to a human, so a customer only ever reads a valid order.
REQUIRED_FIELDS = ("table", "items", "total_eur", "allergen_checked")

MAX_TURNS_DEFAULT = 8


def enrich_ticket(ticket: Any) -> dict:
    """Attach the data-derived fields S04's contract requires.

    The price total comes from the menu, never from the model or the customer.
    `allergen_checked` defaults to False: this gate never claims an allergy was
    cleared - S06 owns that decision, and it is made from menu data.
    """
    if not isinstance(ticket, dict):
        return {
            "table": ticket,
            "items": None,
            "total_eur": None,
            "allergen_checked": False,
        }
    enriched = dict(ticket)
    total = enriched.get("total_eur")
    if not isinstance(total, (int, float)) or isinstance(total, bool):
        items = enriched.get("items")
        if isinstance(items, list):
            enriched["total_eur"] = round(
                sum(domain.MENU[i]["price"] for i in items if i in domain.MENU), 2
            )
    enriched.setdefault("allergen_checked", False)
    return enriched


def validate_ticket(ticket: Any) -> list[str]:
    """A ticket that fails validation never reaches the customer.

    The local floor mirrors S04's contract (`table`, `items`, `total_eur`,
    `allergen_checked`) and runs even before `cafe.schema` exists. When S04 does
    expose `validate_ticket`, its verdict is consulted too, so the gate inherits
    every later tightening of the contract.
    """
    errors: list[str] = []
    if not isinstance(ticket, dict):
        return ["ticket must be a dict"]
    for field in REQUIRED_FIELDS:
        if field not in ticket:
            errors.append(f"missing required field {field!r}")
    items = ticket.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
    else:
        unknown = [item for item in items if item not in domain.MENU]
        if unknown:
            errors.append(f"items not on today's menu: {unknown}")
    # bool is an int in Python; a table number of True is not a table.
    table = ticket.get("table")
    if not isinstance(table, int) or isinstance(table, bool):
        errors.append("table must be an int")
    total = ticket.get("total_eur")
    if not isinstance(total, (int, float)) or isinstance(total, bool):
        errors.append("total_eur must be a number")
    if not isinstance(ticket.get("allergen_checked"), bool):
        errors.append("allergen_checked must be a bool")
    validator = getattr(schema, "validate_ticket", None) if schema is not None else None
    if validator is not None and not errors:
        for extra in validator(ticket):
            if extra not in errors:
                errors.append(extra)
    return errors


def render_ticket(ticket: dict) -> str:
    """What the customer actually reads. Short enough to read is a safety property."""
    lines = [f"=== TICKET · table {ticket['table']} · please confirm ==="]
    for item in ticket["items"]:
        entry = domain.MENU.get(item)
        if entry is None:
            lines.append(f"  - {item}   (not on the menu)")
        else:
            lines.append(f"  - {item}   {entry['price']:.2f} EUR")
    total = ticket.get("total_eur")
    shown = f"{total:.2f}" if isinstance(total, (int, float)) and not isinstance(total, bool) else "?"
    lines.append(f"  total: {shown} EUR")
    lines.append(
        "  [approve] send to kitchen · [edit] change and re-read · "
        "[reject] send nothing"
    )
    return "\n".join(lines)


def make_responder(
    decisions: Iterable[tuple[str, Any]],
) -> Callable[[str], tuple[str, Any]]:
    """A scripted customer: a queue of (decision, payload).

    In production this is a human at a terminal. A customer who walks away
    without answering is a rejection - the safe default.
    """
    queue = list(decisions)

    def responder(_rendered: str) -> tuple[str, Any]:
        if not queue:
            return "reject", None
        return queue.pop(0)

    return responder


def consent_gate(
    proposal: dict,
    responder: Callable[[str], tuple[str, Any]],
    *,
    max_rounds: int = 6,
) -> tuple[dict | None, list[dict]]:
    """Render -> decide -> loop on edits. Returns (approved ticket or None, log).

    A proposal is enriched from menu data and validated **before** it reaches a
    human. An edit is revalidated and re-presented **in full**: an amended plan
    restarts the flow, no partial state carries over. Reject returns `None` and
    nothing downstream ever runs.
    """
    log: list[dict] = []
    current = enrich_ticket(proposal)
    errors = validate_ticket(current)
    if errors:
        log.append({"decision": "proposal_refused", "errors": errors})
        return None, log
    for _ in range(max_rounds):
        rendered = render_ticket(current)
        decision, payload = responder(rendered)
        if decision == "approve":
            log.append({"decision": "approve", "ticket": dict(current)})
            return dict(current), log
        if decision == "reject":
            log.append({"decision": "reject", "ticket": None})
            return None, log
        if decision == "edit":
            candidate = enrich_ticket(payload)
            errors = validate_ticket(candidate)
            if errors:
                log.append({"decision": "edit_refused", "errors": errors})
                continue  # re-present the *current* ticket, unchanged, in full
            current = candidate
            log.append({"decision": "edit", "ticket": dict(current)})
            continue
        log.append({"decision": "unknown", "value": decision})
        return None, log
    log.append({"decision": "rounds_exhausted", "ticket": None})
    return None, log


def check_fire(requested: dict, approved: dict | None) -> list[str]:
    """Compare one requested ticket against the APPROVED ticket. [] means permitted.

    The request is checked, but the request is never the authority - `approved`
    is. A model that drifts (or a customer who edited the order) must not be able
    to talk the harness into firing something else.
    """
    if approved is None:
        return ["no approved ticket: the customer never confirmed"]
    clauses: list[str] = []
    if not isinstance(requested, dict):
        return [f"malformed request: {requested!r}"]
    if requested.get("table") != approved.get("table"):
        clauses.append(
            f"table {requested.get('table')!r} is not the approved {approved.get('table')!r}"
        )
    requested_items = list(requested.get("items") or [])
    approved_items = list(approved.get("items") or [])
    if requested_items != approved_items:
        clauses.append(
            f"items {requested_items} are not the approved {approved_items}"
        )
    return clauses


def fire_requested(
    state: OrderState,
    requested: dict,
    approved: dict | None,
    *,
    on_violation: str = "abort",
) -> dict:
    """The enforcement point: the only caller of `fire_ticket` that S05 allows.

    Returns a record. On a rejection (`approved is None`) and on `abort`, the
    ticket log on `state` is untouched - zero side effects, by construction.
    `degrade` is the other product choice: fire exactly the approved ticket and
    keep a loud record of what was refused.
    """
    if approved is None:
        return {"fired": False, "action": "refused", "reason": "not approved"}
    clauses = check_fire(enrich_ticket(requested), approved)
    if clauses and on_violation == "abort":
        return {
            "fired": False,
            "action": "aborted",
            "clauses": clauses,
            "approved": dict(approved),
        }
    # Both the clean path and the degraded path fire the APPROVED ticket.
    state.tool_log.append(IRREVERSIBLE_ACTION)
    result = _fire_ticket(state, approved["items"], approved["table"])
    if clauses:
        return {
            "fired": True,
            "action": "degraded",
            "clauses": clauses,
            "approved": dict(approved),
            "result": result,
        }
    return {"fired": True, "action": "fired", "result": result}


def run_shift(
    client: Any,
    user_turns: list[str],
    responder: Callable[[str], tuple[str, Any]],
    *,
    state: OrderState | None = None,
    max_turns: int = MAX_TURNS_DEFAULT,
    on_violation: str = "abort",
    system: str | None = None,
) -> dict:
    """The S01 loop with a gate on the irreversible call.

    `propose_order` is intercepted: it renders the ticket, collects consent and
    stores the approved ticket on the run. A later `fire_ticket` is compared to
    that approved ticket; a mismatch aborts (or degrades) instead of firing.

    `stop_reason` is always set, and is one of:
      answered          - the model replied and the scripted lines ran out
      script_done       - every customer line was consumed
      turn_cap          - the harness stopped it; a harness property
      consent_violation - a fire was refused by the gate
    """
    state = state if state is not None else OrderState()
    messages: list[dict] = [
        {"role": "system", "content": system or _system_prompt()}
    ]
    gate_log: list[dict] = []
    approved: dict | None = None
    fires: list[dict] = []
    pending = list(user_turns)
    stop_reason = "script_done"
    turn_index = 0
    aborted = False

    while turn_index < max_turns and not aborted:
        if pending and not _awaiting_model(messages):
            messages.append({"role": "user", "content": pending.pop(0)})
        elif not pending and not _awaiting_model(messages):
            stop_reason = "script_done"
            break

        turn_index += 1
        body = client.chat(messages, tools=domain.TOOL_SCHEMAS, temperature=0.0)
        message = body["choices"][0]["message"]
        messages.append(_assistant_message(message))
        calls = message.get("tool_calls") or []
        if not calls:
            if not pending:
                stop_reason = "answered"
                break
            continue

        for call in calls:
            name = call.get("function", {}).get("name", "")
            if name == "propose_order":
                proposal = _parse_arguments(call)
                approved, log = consent_gate(proposal, responder)
                gate_log.extend(log)
                result: dict = {"proposed": proposal, "approved": approved}
            elif name == IRREVERSIBLE_ACTION:
                requested = _parse_arguments(call)
                record = fire_requested(
                    state, requested, approved, on_violation=on_violation
                )
                fires.append(record)
                result = record
                if record["action"] == "aborted":
                    stop_reason = "consent_violation"
                    aborted = True
            else:
                result = dispatch(state, call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps(
                        result, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                    ),
                }
            )
            if aborted:
                break
    else:
        if not aborted:
            stop_reason = "turn_cap"

    return {
        "messages": messages,
        "state": state,
        "approved": approved,
        "gate_log": gate_log,
        "fires": fires,
        "stop_reason": stop_reason,
        "turns_used": turn_index,
        "model_calls": getattr(client, "calls", turn_index),
    }


def _parse_arguments(call: dict) -> dict:
    """One tool call -> its arguments. An unreadable request is `{}`, never a crash."""
    try:
        parsed = json.loads(call["function"]["arguments"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _awaiting_model(messages: list[dict]) -> bool:
    return bool(messages) and messages[-1]["role"] in {"user", "tool"}


def _assistant_message(message: dict) -> dict:
    out: dict[str, Any] = {"role": "assistant", "content": message.get("content")}
    if message.get("tool_calls"):
        out["tool_calls"] = message["tool_calls"]
    return out


def _system_prompt() -> str:
    rules = "\n".join(f"- {rule}" for rule in domain.SHIFT_RULES)
    return f"{domain.PERSONA}\n\nShift rules:\n{rules}"
