"""S01 - the order-taking loop.

The agent is not the model. The agent is this `while`: you own the message list,
you decide whether a requested tool runs, and you decide when to stop.

Two invariants keep it alive:
  1. append the assistant message verbatim, before any tool result;
  2. every tool_call gets a tool result carrying its id, before the next call.
"""

from __future__ import annotations

import json
from typing import Any

from cafe import domain
from cafe.tools import OrderState, dispatch

__all__ = ["run_shift", "Turn"]

MAX_TURNS_DEFAULT = 8


class Turn:
    """One pass through the loop, kept so S08 can trace it and S09 can cite it."""

    __slots__ = ("index", "request_messages", "response", "tool_results")

    def __init__(self, index: int, request_messages: list[dict], response: dict) -> None:
        self.index = index
        self.request_messages = request_messages
        self.response = response
        self.tool_results: list[dict] = []


def run_shift(
    client: Any,
    user_turns: list[str],
    *,
    state: OrderState | None = None,
    max_turns: int = MAX_TURNS_DEFAULT,
    tools: list[dict] | None = None,
    system: str | None = None,
) -> dict:
    """Drive one customer conversation to a stop. Returns the run record.

    `stop_reason` is always set, and is one of:
      answered      - the model replied with no tool call and the script is done
      turn_cap      - the harness stopped it; a harness property, not a model one
      script_done   - every scripted customer line was consumed
    """
    state = state if state is not None else OrderState()
    schemas = domain.TOOL_SCHEMAS if tools is None else tools
    messages: list[dict] = [
        {"role": "system", "content": system or _system_prompt()}
    ]
    turns: list[Turn] = []
    pending = list(user_turns)
    stop_reason = "script_done"
    turn_index = 0

    while turn_index < max_turns:
        if pending and not _awaiting_model(messages):
            messages.append({"role": "user", "content": pending.pop(0)})
        elif not pending and not _awaiting_model(messages):
            stop_reason = "script_done"
            break

        turn_index += 1
        body = client.chat(messages, tools=schemas, temperature=0.0)
        turn = Turn(turn_index, list(messages), body)
        turns.append(turn)

        message = body["choices"][0]["message"]
        # INVARIANT 1: the assistant message goes in verbatim, before any result.
        messages.append(_assistant_message(message))

        calls = message.get("tool_calls") or []
        if not calls:
            if not pending:
                stop_reason = "answered"
                break
            continue

        # INVARIANT 2: one result per call, carrying that call's id.
        for call in calls:
            result = dispatch(state, call)
            turn.tool_results.append({"call": call, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps(result, sort_keys=True,
                                          separators=(",", ":"), ensure_ascii=False),
                }
            )
    else:
        stop_reason = "turn_cap"

    return {
        "messages": messages,
        "turns": turns,
        "state": state,
        "stop_reason": stop_reason,
        "turns_used": turn_index,
        "model_calls": getattr(client, "calls", turn_index),
    }


def _awaiting_model(messages: list[dict]) -> bool:
    """True when the last message still needs a model response."""
    return bool(messages) and messages[-1]["role"] in {"user", "tool"}


def _assistant_message(message: dict) -> dict:
    """Preserve the protocol fields; never rebuild a tool_call by hand."""
    out: dict[str, Any] = {"role": "assistant", "content": message.get("content")}
    if message.get("tool_calls"):
        out["tool_calls"] = message["tool_calls"]
    return out


def _system_prompt() -> str:
    rules = "\n".join(f"- {rule}" for rule in domain.SHIFT_RULES)
    return f"{domain.PERSONA}\n\nShift rules:\n{rules}"
