"""S04 - the ticket contract: a hand-rolled validator and a bounded retry loop.

Everything that crosses a boundary gets validated, so the ticket the model emits
is checked twice: first against the schema (shape), then against the shift data
(meaning). A schema-valid ticket can still be wrong - it can name an item the
kitchen is out of, or invent a total - and S02's checker is what catches that.

The validator is a stdlib subset of JSON Schema (`type`, `required`,
`properties`, `enum`, `items`, `minItems`). The checks are the lesson; a library
is these same checks with more keywords.

Nothing in this module constructs a client; the caller injects one.
"""

from __future__ import annotations

import json
from typing import Any

from cafe import domain
from cafe.evals import checkers
from cafe.model import ModelRequestError

# The kitchen's contract. `items` enumerates the menu, but availability and
# prices still need the semantic checker; an enum alone cannot make a ticket correct.
TICKET_SCHEMA: dict = {
    "type": "object",
    "required": ["table", "items", "total_eur", "allergen_checked"],
    "properties": {
        "table": {"type": "integer"},
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "enum": sorted(domain.MENU)},
        },
        "total_eur": {"type": "number"},
        "allergen_checked": {"type": "boolean"},
        "notes": {"type": "string"},
    },
}

TYPE_CHECKS = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    # bool IS an int in Python; real validators exclude it, so do we.
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
}

TICKET_SYSTEM = (
    domain.TICKET_INSTRUCTIONS
    + "\n\nTrusted menu (prices in EUR):\n" + json.dumps(domain.MENU, sort_keys=True)
    + "\n86'd tonight:\n" + json.dumps(list(domain.EIGHTY_SIXED))
)

TICKET_PROMPT = domain.TICKET_PROMPT


def validate(instance: Any, schema: dict, path: str = "$") -> list[str]:
    """JSON-Schema subset. Returns human-readable errors; `[]` means valid."""
    if "type" in schema and not TYPE_CHECKS[schema["type"]](instance):
        return [f"{path}: expected {schema['type']}, got {json.dumps(instance)[:50]}"]
    errors: list[str] = []
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {json.dumps(instance)} is not one of {schema['enum']}")
    if schema.get("type") == "object":
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{path}: missing required field {field!r}")
        for field, sub in schema.get("properties", {}).items():
            if field in instance:
                errors += validate(instance[field], sub, f"{path}.{field}")
    if schema.get("type") == "array":
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for index, element in enumerate(instance):
                errors += validate(element, schema["items"], f"{path}[{index}]")
    return errors


def parse_json(text: Any) -> Any:
    """Recover a JSON object from a chat reply, fences and prose included."""
    if not isinstance(text, str):
        return None
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = [line for line in candidate.splitlines() if not line.strip().startswith("```")]
        candidate = "\n".join(lines).strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return None


def _assistant_message(message: dict) -> dict:
    """Append the assistant turn verbatim - the S01 invariant, reused."""
    out: dict[str, Any] = {"role": "assistant", "content": message.get("content")}
    if message.get("tool_calls"):
        out["tool_calls"] = message["tool_calls"]
    return out


def ask_ticket_run(
    client: Any,
    brief: str,
    *,
    schema: dict = TICKET_SCHEMA,
    max_attempts: int = 3,
    system: str = TICKET_SYSTEM,
) -> dict:
    """Ask for a ticket, validate, feed the errors back, retry. Always capped.

    Retain every outcome before retrying: final acceptance must not hide a
    schema-valid but semantically wrong first attempt.
    """
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": TICKET_PROMPT + brief},
    ]
    outcomes = []
    for attempt in range(1, max_attempts + 1):
        try:
            body = client.chat(list(messages), temperature=0.0)
        except ModelRequestError as exc:
            # A timeout may leave upstream inference running. Retain evidence
            # and stop; do not turn transport failure into another model retry.
            outcomes.append({
                "attempt": attempt, "parsed": False, "shape_ok": False,
                "semantic_ok": None, "shape_errors": [], "semantic_errors": [],
                "stage": "transport", "errors": [str(exc)], "reply": None,
            })
            return {"ticket": None, "messages": messages, "attempts": attempt,
                    "outcomes": outcomes, "stop_reason": "transport_error"}
        choice = body["choices"][0]
        message = choice["message"]
        messages.append(_assistant_message(message))
        tool_calls = message.get("tool_calls") or []
        for call in tool_calls:
            # An unexpected channel must never execute an order. Pair a denial
            # with each call so the next attempt still has a legal transcript.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps({"error": "tools_disabled", "executed": False}),
                }
            )
        if choice.get("finish_reason") == "length":
            outcomes.append({
                "attempt": attempt, "parsed": False, "shape_ok": False,
                "semantic_ok": None, "shape_errors": [], "semantic_errors": [],
                "stage": "budget", "errors": ["Completion budget exhausted; no ticket accepted."],
                "reply": message.get("content"),
            })
            return {"ticket": None, "messages": messages, "attempts": attempt,
                    "outcomes": outcomes, "stop_reason": "completion_limit"}
        ticket = None if tool_calls else parse_json(message.get("content"))
        shape_errors = validate(ticket, schema) if ticket is not None else []
        meaning_errors = checkers.ticket_matches_menu(ticket) if ticket is not None and not shape_errors else []
        if tool_calls:
            stage, errors = "channel", ["Tool calls are disabled; return the JSON ticket in text. No tool was executed."]
        elif ticket is None:
            stage, errors = "parse", ["No JSON ticket could be parsed from the text reply."]
        elif shape_errors:
            stage, errors = "shape", shape_errors
        elif meaning_errors:
            stage, errors = "meaning", meaning_errors
        else:
            stage, errors = "accepted", []
        outcomes.append({
            "attempt": attempt, "parsed": ticket is not None,
            "shape_ok": ticket is not None and not shape_errors,
            "semantic_ok": (not meaning_errors) if ticket is not None and not shape_errors else None,
            "shape_errors": shape_errors, "semantic_errors": meaning_errors,
            "stage": stage, "errors": errors, "reply": message.get("content"),
        })
        if tool_calls:
            feedback = "CHANNEL ERROR: " + errors[0]
        elif ticket is None:
            feedback = (
                "PARSE ERROR: reply with the raw JSON ticket object only - "
                "no prose, no code fences."
            )
        else:
            if not shape_errors and not meaning_errors:
                return {"ticket": ticket, "messages": messages, "attempts": attempt,
                        "outcomes": outcomes, "stop_reason": "accepted"}
            if shape_errors:
                feedback = "VALIDATION ERRORS:\n" + "\n".join(f"- {e}" for e in shape_errors)
            else:
                feedback = "SEMANTIC ERRORS:\n" + "\n".join(f"- {e}" for e in meaning_errors)
        messages.append({"role": "user", "content": feedback})
    return {"ticket": None, "messages": messages, "attempts": len(outcomes),
            "outcomes": outcomes, "stop_reason": "attempt_cap"}


def ask_ticket(
    client: Any, brief: str, *, schema: dict = TICKET_SCHEMA,
    max_attempts: int = 3, system: str = TICKET_SYSTEM,
) -> tuple[Any, list[dict], int]:
    """Compatibility view: accepted ticket, full transcript and attempt count."""
    run = ask_ticket_run(client, brief, schema=schema, max_attempts=max_attempts, system=system)
    return run["ticket"], run["messages"], run["attempts"]
