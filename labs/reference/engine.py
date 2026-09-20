"""Governed café host. Spotter — open only if stuck. Peeking weakens S13."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Callable

import menu as menumod
import house_rules
import schemas
from client import RouteRefused
from reference.loop import run_loop
from reference import tools as toolsmod
from spec_schema import PII_RE, SpecError, validate_spec


MEDICAL_TERM_RE = re.compile(
    r"\b(medical|medicine|medication|diagnos(?:e|is)|headache|symptom|treatment|dose|prescription)\b",
    re.I,
)
MEDICAL_ADVICE_RE = re.compile(
    r"\b(should i|what (?:should i do|medicine|medication)|which (?:medicine|medication)|"
    r"recommend|how should i treat|can you diagnose|diagnose me|"
    r"(?:give|provide|offer) me medical advice|i need medical advice)\b",
    re.I,
)


def medical_advice_hit(text: str | None) -> bool:
    """Toy deny signal for medical-advice asks; not clinical classification."""
    if not text:
        return False
    return bool(MEDICAL_TERM_RE.search(text) and MEDICAL_ADVICE_RE.search(text))


def _stopped_result(spec: dict, stop_reason: str, debrief: str) -> dict[str, Any]:
    state = toolsmod.new_state(spec["scope"], spec["sections"])
    state["stop_reason"] = stop_reason
    return {
        "messages": [],
        "state": state,
        "spec": spec,
        "debrief": debrief,
        "mode": "engine",
        "stop_reason": stop_reason,
    }


def compact(messages: list[dict], *, keep: int) -> list[dict]:
    """Drop middle turns; never drop the pinned house-rules system message."""
    if keep < 2 or len(messages) <= keep:
        return messages
    pin = messages[0]
    dropped = len(messages) - keep
    tail = messages[-(keep - 1) :]
    note = {
        "role": "system",
        "content": f"[compacted {dropped} earlier messages; house rules still pinned]",
    }
    return [pin, note, *tail]


def policy_hit(text: str | None, state: dict) -> str | None:
    if not text:
        return None
    if PII_RE.search(text):
        return "pii"
    rank = {"counter": 0, "kitchen": 1, "banquet": 2}
    approved = rank.get(state.get("approved_scope") or "counter", 0)
    norm = menumod.normalize_answer(text)
    for item in menumod.MENU:
        if item["detail"] in text:
            if item["id"] not in state["pulled"]:
                return "invented_item"
            if rank.get(item["scope"], 0) > approved:
                return "ceiling"
        if menumod.normalize_answer(item["internal_supplier_ref"]) in norm:
            return "supplier_ref_leak"
    return None


def turn_policy_hit(messages: list[dict], start: int, state: dict) -> str | None:
    for msg in messages[start:]:
        if msg.get("role") == "assistant":
            hit = policy_hit(msg.get("content"), state)
            if hit:
                return hit
    return None


def build_debrief(messages: list[dict], state: dict) -> str:
    refs: list[str] = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "user":
            refs.append(f"turn {i}: customer said {(msg.get('content') or '')[:80]!r}")
        elif msg.get("role") == "assistant" and msg.get("tool_calls"):
            names = ", ".join(c["function"]["name"] for c in msg["tool_calls"])
            refs.append(f"turn {i}: assistant called {names}")
    refs = refs[:4] or ["turn 0: (empty shift)"]
    return "\n".join(
        [
            "# Shift debrief",
            f"Total {state['score']} / items {state['items_served']}.",
            f"stop_reason={state.get('stop_reason') or 'completed'}.",
            "Moments:",
            *(f"- {r}" for r in refs[:4]),
        ]
    )


def run_naive(client: Any, script: list[str]) -> dict[str, Any]:
    messages = [{"role": "system", "content": house_rules.NAIVE_PROMPT}]
    for line in script:
        messages.append({"role": "user", "content": line})
        raw = client.chat(messages, tools=None, temperature=0.0)
        content = raw["choices"][0]["message"].get("content")
        messages.append({"role": "assistant", "content": content})
    return {
        "messages": messages,
        "state": toolsmod.new_state(),
        "spec": None,
        "debrief": "",
        "mode": "naive",
    }


def run_engine(
    client: Any,
    script: list[str],
    *,
    spec: dict | None = None,
    generate_from_brief: bool = False,
    auto_approve: bool = True,
    input_fn: Callable[[str], str] | None = None,
    max_turns: int = 8,
    max_messages: int | None = None,
    max_approx_tokens: int = 20000,
    route_kind: str | None = None,
) -> dict[str, Any]:
    del generate_from_brief  # specs come from propose_order, not a side channel
    kind = route_kind if route_kind is not None else os.environ.get("OPENAI_ROUTE_KIND")
    if kind == "cloud":
        raise RouteRefused("session-content phase refuses OPENAI_ROUTE_KIND=cloud")
    spec = spec or {
        "occasion": "regulars",
        "scope": "counter",
        "sections": ["espresso"],
        "item_count": 2,
        "restrictions": ["medical advice"],
        "language": "en",
        "house_rules": ["items from tools only"],
    }
    spec = validate_spec(spec)
    if not auto_approve:
        fn = input_fn or input
        decision = fn("approve / edit / reject: ").strip().casefold()
        if decision == "reject":
            return {
                "messages": [],
                "state": toolsmod.new_state(spec["scope"]),
                "spec": spec,
                "debrief": "rejected",
                "mode": "engine",
                "stop_reason": "rejected",
            }
        if decision == "edit":
            try:
                replacement = json.loads(fn("replacement spec JSON: "))
                spec = validate_spec(replacement)
            except (json.JSONDecodeError, SpecError) as exc:
                return _stopped_result(spec, "invalid_edit", f"invalid edit: {exc}")
        elif decision != "approve":
            return _stopped_result(
                spec,
                "invalid_decision",
                "invalid consent decision: expected approve, edit, or reject",
            )
    state = toolsmod.new_state(spec["scope"], spec["sections"])
    messages: list[dict] = [
        {"role": "system", "content": house_rules.PINNED_RULES},
        {"role": "system", "content": house_rules.STARTER_PERSONA},
    ]
    retries = 0

    def dispatch(call: dict) -> dict:
        return toolsmod.dispatch(state, call)

    for line in script:
        if state["ended"]:
            break
        approx = len(json.dumps(messages, ensure_ascii=False)) // 4
        if approx > max_approx_tokens:
            state["stop_reason"] = "budget_exceeded"
            break
        messages.append({"role": "user", "content": line})
        if medical_advice_hit(line):
            messages.append(
                {
                    "role": "assistant",
                    "content": "I'm the counter assistant, not a clinician — "
                    "I can't give medical advice.",
                }
            )
            state["stop_reason"] = "policy_refusal"
            break
        after_user = len(messages)
        if max_messages:
            messages[:] = compact(messages, keep=max_messages)
            after_user = len(messages)
        messages, stop = run_loop(
            client, messages, schemas.TOOLS, dispatch, max_turns=max_turns
        )
        hit = turn_policy_hit(messages, after_user, state)
        while hit and retries < 3:
            retries += 1
            del messages[after_user:]
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Policy {hit}: do not disclose internal_supplier_ref, PII, "
                        "or unpulled item text. Allergens are public. Use tools only."
                    ),
                }
            )
            messages, stop = run_loop(
                client, messages, schemas.TOOLS, dispatch, max_turns=max_turns
            )
            hit = turn_policy_hit(messages, after_user, state)
        if hit:
            state["stop_reason"] = "retries_exhausted"
            break
        if stop == "turn_cap":
            state["stop_reason"] = "turn_cap"
            break
    debrief = build_debrief(messages, state)
    return {
        "messages": messages,
        "state": state,
        "spec": state.get("spec") or spec,
        "debrief": debrief,
        "mode": "engine",
        "stop_reason": state.get("stop_reason") or "completed",
    }
