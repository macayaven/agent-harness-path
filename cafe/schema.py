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
from cafe.tools import OrderState, dispatch

# The kitchen's contract. `items` enumerates the menu: enums are policy, and
# S04's third experiment is about what happens when the policy is wrong.
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
    domain.PERSONA
    + "\n\nShift rules:\n"
    + "\n".join(f"- {rule}" for rule in domain.SHIFT_RULES)
    + "\n\nReturn ONLY one JSON ticket object, no prose, no code fences."
)

TICKET_PROMPT = (
    "Read the customer note and reply with ONE JSON object shaped like this: "
    '{"table": int, "items": [str], "total_eur": number, "allergen_checked": bool, '
    '"notes": str (optional)}. Prices come from the menu.\n\nCustomer note:\n'
)


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


def ask_ticket(
    client: Any,
    brief: str,
    *,
    schema: dict = TICKET_SCHEMA,
    max_attempts: int = 3,
    system: str = TICKET_SYSTEM,
) -> tuple[Any, list[dict], int]:
    """Ask for a ticket, validate, feed the errors back, retry. Always capped.

    Returns `(ticket_or_None, messages, attempts)`. The message list is the
    receipt: it shows exactly what the model was told after each failure.
    """
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": TICKET_PROMPT + brief},
    ]
    state = OrderState()
    for attempt in range(1, max_attempts + 1):
        body = client.chat(list(messages), tools=domain.TOOL_SCHEMAS, temperature=0.0)
        message = body["choices"][0]["message"]
        messages.append(_assistant_message(message))
        for call in message.get("tool_calls") or []:
            result = dispatch(state, call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps(result, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False),
                }
            )
        ticket = parse_json(message.get("content"))
        if ticket is None:
            feedback = (
                "PARSE ERROR: reply with the raw JSON ticket object only - "
                "no prose, no code fences."
            )
        else:
            shape_errors = validate(ticket, schema)
            meaning_errors = checkers.ticket_matches_menu(ticket) if not shape_errors else []
            if not shape_errors and not meaning_errors:
                return ticket, messages, attempt
            if shape_errors:
                feedback = "VALIDATION ERRORS:\n" + "\n".join(f"- {e}" for e in shape_errors)
            else:
                feedback = "SEMANTIC ERRORS:\n" + "\n".join(f"- {e}" for e in meaning_errors)
        messages.append({"role": "user", "content": feedback})
    return None, messages, max_attempts
