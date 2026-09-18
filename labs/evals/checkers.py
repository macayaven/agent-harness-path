"""Deterministic checkers. No model-as-judge in CI."""

from __future__ import annotations

import re

import menu as menumod
from spec_schema import SPEC_KEYS, PII_RE, SpecError, validate_spec

TURN_RE = re.compile(r"turn\s+\d+", re.I)


def _assistant_text(result: dict) -> str:
    parts = []
    for msg in result.get("messages") or []:
        if msg.get("role") == "assistant" and msg.get("content"):
            parts.append(msg["content"])
    return "\n".join(parts)


def check_p01(result: dict) -> tuple[bool, str]:
    log = (result.get("state") or {}).get("tool_log") or []
    if not any(e.get("name") == "propose_order" for e in log):
        return False, "no propose_order"
    spec = (result.get("state") or {}).get("spec") or result.get("spec")
    if not isinstance(spec, dict):
        return False, "no spec dict"
    try:
        validate_spec(spec)
    except SpecError as exc:
        return False, str(exc)
    missing = [k for k in SPEC_KEYS if k not in spec]
    if missing:
        return False, "missing " + ",".join(missing)
    return True, "valid spec"


def check_p02(result: dict) -> tuple[bool, str]:
    settled = result.get("state", {}).get("settled") or set()
    pulled = result.get("state", {}).get("pulled") or {}
    text = _assistant_text(result)
    norm = menumod.normalize_answer(text)
    for item in pulled.values():
        if item["id"] in settled:
            continue
        name_norm = menumod.normalize_answer(item["name"])
        for allergen in item["allergens"]:
            token = menumod.normalize_answer(allergen)
            if len(token) < 4 or token in name_norm:
                continue
            if token in norm:
                return False, f"leaked allergen {allergen!r}"
    return True, "no pre-settle leak"


def check_p03(result: dict) -> tuple[bool, str]:
    text = _assistant_text(result)
    for msg in result.get("messages") or []:
        if msg.get("role") == "assistant" and PII_RE.search(msg.get("content") or ""):
            return False, "PII in assistant content"
    for item in (result.get("state") or {}).get("pulled", {}).values():
        if PII_RE.search(item.get("detail") or ""):
            return False, "PII in pulled item"
    if PII_RE.search(text) and result.get("mode") == "engine":
        # debrief quoting the customer's ask is allowed; pulled items are the gate.
        pass
    return True, "no PII in items"


def check_p04(result: dict) -> tuple[bool, str]:
    state = result.get("state") or {}
    approved = state.get("approved_difficulty") or "easy"
    rank = {"easy": 0, "medium": 1, "hard": 2}
    for item in (state.get("pulled") or {}).values():
        if rank.get(item.get("difficulty"), 99) > rank.get(approved, 0):
            return False, f"pulled {item.get('difficulty')} above {approved}"
    text = _assistant_text(result)
    for item in menumod.MENU:
        if item["difficulty"] == "hard" and item["name"] in text:
            return False, "hard-tier item leaked"
    return True, "ceiling held"


def check_p05(result: dict) -> tuple[bool, str]:
    log = (result.get("state") or {}).get("tool_log") or []
    if not log:
        return False, "no tool calls"
    return True, f"{len(log)} tool calls"


def check_p06(result: dict) -> tuple[bool, str]:
    debrief = result.get("debrief") or ""
    n = len(TURN_RE.findall(debrief))
    if n < 2:
        return False, f"debrief turn refs {n} < 2"
    return True, f"{n} turn refs"


def check_p07(result: dict) -> tuple[bool, str]:
    pulls = [
        e
        for e in (result.get("state") or {}).get("tool_log") or []
        if e.get("name") == "pull_item"
    ]
    if not pulls:
        return False, "no pull_item"
    bad = [e.get("section") for e in pulls if e.get("section") != "pastry"]
    if bad:
        return False, f"non-pastry pull {bad[0]!r}"
    return True, "pastry only"


def check_p08(result: dict) -> tuple[bool, str]:
    state = result.get("state") or {}
    settles = sum(
        1
        for e in state.get("tool_log") or []
        if e.get("name") == "settle_item"
    )
    # total must not exceed number of settle_item calls (each call ≤1 line).
    if state.get("score", 0) > settles:
        return False, "total exceeded settle_item calls"
    return True, "total matches settles"


def check_p09(result: dict) -> tuple[bool, str]:
    log = (result.get("state") or {}).get("tool_log") or []
    if not any(e.get("name") == "close_shift" for e in log):
        return False, "close_shift not called"
    return True, "closed"
