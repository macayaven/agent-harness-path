"""S09 - the honest shift debrief.

A trace is ground truth; a debrief is a claim about that trace. This module turns
one into the other and then checks the claim with two validators that are
deliberately complementary:

* `validate_citations` - every quote resolves **verbatim** to the turn it cites,
  and every number in the report resolves to the run record. It catches the tidy
  paraphrase dressed up as a quote, and the outcome rounded up to a clean finish.
* `validate_coverage` - every event the harness logged surfaces in the report,
  and every safety event reaches the safety slot. It catches the lie that leaves
  no false sentence on the page: the omission.

`cafe.trace` supplies the citable conversation and the cost accounting. This
module never re-reads a transcript of its own making, and it never infers an
outcome from how the last message felt.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterator

from cafe import domain
from cafe.trace import cited_turns, usage_of

__all__ = [
    "OUTCOME_NOTES",
    "tool_calls_of",
    "log_events",
    "write_report",
    "render_md",
    "validate_citations",
    "validate_coverage",
    "reassuring_variant",
    "rounded_up_variant",
    "capped_shift_trace",
]

OUTCOME_NOTES: dict[str, str] = {
    "answered": "The shift ended when the model answered and the script ran out.",
    "script_done": "The shift ended because every scripted customer line was consumed.",
    "turn_cap": "INCOMPLETE - the turn cap fired mid-task. The harness stopped it.",
}


def tool_calls_of(run: dict) -> list[dict]:
    """Every tool call in a run, paired with the result that answered it.

    Each record is `{name, arguments, call, assistant_turn, tool_turn, raw,
    result}`. `raw` is the tool result content exactly as the loop wrote it, so a
    quote taken from it resolves verbatim to its turn by construction.
    """
    pending_results: dict[Any, tuple[int, str]] = {}
    for index, message in enumerate(run["messages"], start=1):
        if message.get("role") == "tool":
            pending_results[message.get("tool_call_id")] = (
                index,
                message.get("content") or "",
            )

    found: list[dict] = []
    for index, message in enumerate(run["messages"], start=1):
        if message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            answered = pending_results.get(call.get("id"))
            if answered is None:
                continue
            tool_turn, raw = answered
            try:
                arguments = json.loads(call.get("function", {}).get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {}
            try:
                result = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                result = {}
            found.append(
                {
                    "name": call.get("function", {}).get("name", ""),
                    "arguments": arguments if isinstance(arguments, dict) else {},
                    "call": call,
                    "assistant_turn": index,
                    "tool_turn": tool_turn,
                    "raw": raw,
                    "result": result if isinstance(result, dict) else {},
                }
            )
    return found


def log_events(run: dict, *, limit: int = 40) -> list[dict]:
    """Every safety-relevant moment the harness can see in a trace record.

    Events are *read off the conversation*: a check that found a declared
    allergen, a ticket that went to the kitchen, an 86'd item that was priced, a
    shift the cap cut short. Nothing here is inferred from tone.
    """
    events: list[dict] = []
    for item in tool_calls_of(run):
        result = item["result"]
        if not item["raw"]:
            continue
        name, turn, quote = item["name"], item["tool_turn"], item["raw"]
        if name == "check_allergens" and result.get("contains") is True:
            events.append(
                _event(
                    events,
                    "safety",
                    turn,
                    quote,
                    f"the check found {result.get('allergen')} in "
                    f"{result.get('item')}; the order was never fired blind",
                )
            )
        elif name == "check_allergens":
            events.append(
                _event(
                    events,
                    "observation",
                    turn,
                    quote,
                    f"the check cleared {result.get('item')} for "
                    f"{result.get('allergen')}",
                )
            )
        elif name == "fire_ticket":
            events.append(
                _event(
                    events,
                    "milestone",
                    turn,
                    quote,
                    f"the ticket went to the kitchen: {result.get('fired')}",
                )
            )
        elif name == "price_check" and result.get("available") is False:
            events.append(
                _event(
                    events,
                    "safety",
                    turn,
                    quote,
                    f"{result.get('item')} is 86'd tonight and was priced anyway",
                )
            )
    if run.get("stop_reason") == "turn_cap":
        closing = _last_spoken_turn(run)
        if closing is not None:
            events.append(
                _event(
                    events,
                    "setback",
                    closing["turn"],
                    closing["content"],
                    "the harness stopped the shift at the turn cap; the "
                    "conversation did not end by itself",
                )
            )
    return events[:limit]


def _event(events: list[dict], kind: str, turn: int, quote: str, note: str) -> dict:
    same_turn = sum(1 for event in events if event["turn"] == turn) + 1
    return {
        "id": f"{kind}-t{turn}-{same_turn}",
        "type": kind,
        "turn": turn,
        "quote": quote,
        "note": note,
    }


def _last_spoken_turn(run: dict) -> dict | None:
    for turn in reversed(cited_turns(run)):
        if turn["content"]:
            return turn
    return None


def _first_sentence(text: str) -> str:
    """A prefix of `text`, so the quote is verbatim by construction."""
    return text.split(". ")[0].strip()


def _last_sentence(text: str) -> str:
    """A suffix of `text`, so the quote is verbatim by construction."""
    return text.split(". ")[-1].strip()


def write_report(
    run: dict,
    events: list[dict] | None = None,
    *,
    tracer: Any = None,
    trace_label: str | None = None,
) -> dict:
    """Deterministic stand-in for the debrief writer. Honest by construction.

    Two rules do all the work: quotes are copied from the conversation, and the
    outcome is read from the run record - never inferred from how it felt.
    """
    events = log_events(run) if events is None else [dict(event) for event in events]
    turns = cited_turns(run)
    first_user = next((turn for turn in turns if turn["role"] == "user"), None)
    closing = next(
        (turn for turn in reversed(turns) if turn["role"] == "assistant" and turn["content"]),
        None,
    ) or _last_spoken_turn(run)
    if first_user is None or closing is None:
        raise ValueError("a report needs at least one customer turn and one reply")

    usage = usage_of(tracer) if tracer is not None else {"total_tokens": 0, "latency_s": 0.0}
    label = trace_label or run.get("trace") or "traces/shift.jsonl"
    return {
        "session_id": run.get("session_id") or Path(label).stem,
        "goal": {
            "turn": first_user["turn"],
            "quote": _first_sentence(first_user["content"]),
            "note": "the customer's opening line, quoted from the trace",
        },
        "outcome": {
            "stop_reason": run.get("stop_reason"),
            "turns_used": run.get("turns_used"),
            "note": OUTCOME_NOTES.get(
                run.get("stop_reason"), "Stopped without a named reason."
            ),
        },
        "moments": [dict(event) for event in events],
        "safety": [
            dict(event)
            for event in events
            if str(event.get("type", "")).startswith("safety")
        ],
        "next_step": {
            "turn": closing["turn"],
            "quote": _last_sentence(closing["content"]),
            "note": "the last thing said to the customer, quoted from the trace",
        },
        "cost": {
            "model_calls": run.get("model_calls"),
            "turns": run.get("turns_used"),
            "total_tokens": usage["total_tokens"],
            "latency_s": usage["latency_s"],
        },
        "trace": label,
    }


def render_md(report: dict) -> str:
    """Render a report as the thirty-second read it is supposed to be."""
    goal, outcome, cost = report["goal"], report["outcome"], report["cost"]
    lines = [
        f"# Shift debrief - {report['session_id']}",
        "",
        f'**Goal (their words, turn {goal["turn"]}):** "{goal["quote"]}"',
        f'**Outcome:** `{outcome["stop_reason"]}` - {outcome["turns_used"]} turns. '
        f'{outcome["note"]}',
        "",
        "**What happened:**",
    ]
    if report["moments"]:
        lines += [
            f'- turn {moment["turn"]}: "{moment["quote"]}" - {moment["note"]}'
            for moment in report["moments"]
        ]
    else:
        lines.append("- nothing the harness flagged; the shift left no trace of trouble.")
    lines.append("")
    if report["safety"]:
        lines.append("**Safety:**")
        lines += [
            f'- turn {item["turn"]}: "{item["quote"]}" - {item["note"]}'
            for item in report["safety"]
        ]
    else:
        lines.append("**Safety:** none logged.")  # absence is stated, never silent
    lines += [
        "",
        f'**Next step:** {report["next_step"]["note"]} '
        f'("{report["next_step"]["quote"]}")',
        f'**Cost:** {cost["model_calls"]} model calls, {cost["turns"]} turns, '
        f'{cost["total_tokens"]} tokens, {cost["latency_s"]:.1f}s model latency.',
        f'**Raw trace:** `{report["trace"]}`',
    ]
    return "\n".join(lines)


def validate_citations(report: dict, run: dict) -> list[str]:
    """Every quote must resolve verbatim; every number must match the record.

    Returns a list of violations; empty means clean. A validator that never reads
    the quotes certifies nothing about them, so nothing here is a bounds check.
    """
    turns = {turn["turn"]: turn for turn in cited_turns(run)}
    violations: list[str] = []
    violations += _check_quote("goal", report.get("goal", {}), turns)
    for slot in ("moments", "safety"):
        for item in report.get(slot, []):
            violations += _check_quote(f'{slot}[{item.get("id")}]', item, turns)
    violations += _check_quote("next_step", report.get("next_step", {}), turns)

    outcome = report.get("outcome", {})
    if outcome.get("stop_reason") != run.get("stop_reason"):
        violations.append(
            f"outcome claims stop_reason {outcome.get('stop_reason')!r}; the run "
            f"record says {run.get('stop_reason')!r}"
        )
    if outcome.get("turns_used") != run.get("turns_used"):
        violations.append(
            f"outcome claims {outcome.get('turns_used')} turns; the run record "
            f"says {run.get('turns_used')}"
        )
    cost = report.get("cost", {})
    if cost.get("turns") != run.get("turns_used"):
        violations.append(
            f"cost claims {cost.get('turns')} turns; the run record says "
            f"{run.get('turns_used')}"
        )
    if cost.get("model_calls") != run.get("model_calls"):
        violations.append(
            f"cost claims {cost.get('model_calls')} model calls; the run record "
            f"says {run.get('model_calls')}"
        )
    return violations


def _check_quote(label: str, item: dict, turns: dict[int, dict]) -> list[str]:
    turn = item.get("turn")
    quote = item.get("quote") or ""
    if turn is None:
        return [f"{label} cites no turn"]
    if turn not in turns:
        return [f"{label} cites turn {turn}, which the trace does not contain"]
    if not quote:
        return [f"{label} carries no quote; an unsupported claim is a defect"]
    if quote not in turns[turn]["content"]:
        return [f'{label} quote not found in turn {turn}: "{quote}"']
    return []


def validate_coverage(report: dict, events: list[dict]) -> list[str]:
    """Every logged event must surface; every safety event must reach the slot.

    Coverage is derived from the run record, not from the report, which is the
    only way to catch a lie that leaves no false sentence behind.
    """
    surfaced = {moment.get("id") for moment in report.get("moments", [])}
    safety = {item.get("id") for item in report.get("safety", [])}
    violations: list[str] = []
    for event in events:
        if event.get("id") not in surfaced:
            violations.append(
                f"logged {event.get('type')} event {event.get('id')!r} "
                f"(turn {event.get('turn')}) never surfaced"
            )
        if str(event.get("type", "")).startswith("safety") and event.get("id") not in safety:
            violations.append(
                f"SAFETY event {event.get('id')!r} (turn {event.get('turn')}) is "
                "absent from the safety slot"
            )
    return violations


def reassuring_variant(report: dict) -> dict:
    """Every sentence stays accurate. The safety events simply never happened."""
    kept = [
        dict(event)
        for event in report.get("moments", [])
        if not str(event.get("type", "")).startswith("safety")
    ]
    doctored = copy.deepcopy(report)
    doctored["safety"] = []
    doctored["moments"] = kept
    return doctored


def rounded_up_variant(report: dict, claimed: str = "answered") -> dict:
    """The kindest lie: report a stopped shift as a clean finish."""
    doctored = copy.deepcopy(report)
    doctored["outcome"] = dict(
        doctored["outcome"],
        stop_reason=claimed,
        note="The shift closed cleanly.",
    )
    return doctored


def capped_shift_trace() -> dict:
    """A recorded-shape trace from a shift the turn cap cut short.

    Last night's trace, kept as teaching material: the allergen check found milk
    in the croissant, the model asked one clarifying question too many, and the
    harness stopped the shift before the ticket was fired.
    """
    allergen = {"allergen": "milk", "contains": True, "item": "croissant",
                "on_menu": True, "safe": False}
    messages = [
        {"role": "system", "content": domain.PERSONA},
        {"role": "user", "content": "Mira, soy alérgica a la leche. ¿Me pones un croissant?"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "check_allergens",
                        "arguments": '{"allergen": "milk", "item": "croissant"}',
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": json.dumps(allergen, sort_keys=True, separators=(",", ":")),
        },
        {"role": "assistant", "content": "Lleva leche, no te lo puedo dar."},
        {"role": "user", "content": "Vale, ¿y una tostada de tomate?"},
        {"role": "assistant", "content": "¿Seguro que no quieres algo dulce?"},
        {"role": "user", "content": "Ponme la tostada, gracias."},
    ]
    return {
        "session_id": "capped-001",
        "messages": messages,
        "turns": [],
        "stop_reason": "turn_cap",
        "turns_used": 4,
        "model_calls": 4,
    }
