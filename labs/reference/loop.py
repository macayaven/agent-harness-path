"""Client-owned tool loop. Append assistant messages verbatim (protocol fields only)."""

from __future__ import annotations

from typing import Any, Callable

from client import canonicalize


def _assistant_message(raw: dict) -> dict:
    """Keep the protocol fields; drop vendor extras (reasoning, index, …)."""
    msg = raw["choices"][0]["message"]
    clean: dict[str, Any] = {
        "role": "assistant",
        "content": msg.get("content") if msg.get("content") else None,
    }
    calls = msg.get("tool_calls") or []
    if calls:
        clean["tool_calls"] = [
            {
                "id": c["id"],
                "type": c.get("type", "function"),
                "function": {
                    "name": c["function"]["name"],
                    "arguments": c["function"].get("arguments") or "{}",
                },
            }
            for c in calls
        ]
    return clean


def run_loop(
    client: Any,
    messages: list[dict],
    tools: list[dict],
    dispatch: Callable[[dict], Any],
    *,
    max_turns: int = 8,
) -> tuple[list[dict], str]:
    for _ in range(max_turns):
        raw = client.chat(messages, tools=tools, temperature=0.0)
        assistant = _assistant_message(raw)
        messages.append(assistant)
        calls = assistant.get("tool_calls") or []
        if not calls:
            return messages, "completed"
        for call in calls:
            result = dispatch(call)
            if not isinstance(result, str):
                result = canonicalize(result)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                }
            )
    return messages, "turn_cap"
