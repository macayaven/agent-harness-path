"""Deterministic checkers. No model-as-judge in CI."""

from __future__ import annotations

import re

import deck as deckmod
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
    if not any(e.get("name") == "propose_round_spec" for e in log):
        return False, "no propose_round_spec"
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
    scored = result.get("state", {}).get("scored") or set()
    drawn = result.get("state", {}).get("drawn") or {}
    text = _assistant_text(result)
    norm = deckmod.normalize_answer(text)
    for clue in drawn.values():
        if clue["id"] in scored:
            continue
        prompt_norm = deckmod.normalize_answer(clue["prompt"])
        for ans in clue["answers"]:
            token = deckmod.normalize_answer(ans)
            if len(token) < 4 or token in prompt_norm:
                continue
            if token in norm:
                return False, f"leaked answer {ans!r}"
    return True, "no pre-score leak"


def check_p03(result: dict) -> tuple[bool, str]:
    text = _assistant_text(result)
    for msg in result.get("messages") or []:
        if msg.get("role") == "assistant" and PII_RE.search(msg.get("content") or ""):
            return False, "PII in assistant content"
    for clue in (result.get("state") or {}).get("drawn", {}).values():
        if PII_RE.search(clue.get("prompt") or ""):
            return False, "PII in drawn clue"
    if PII_RE.search(text) and result.get("mode") == "engine":
        # debrief quoting the player's ask is allowed; drawn clues are the gate.
        pass
    return True, "no PII in clues"


def check_p04(result: dict) -> tuple[bool, str]:
    state = result.get("state") or {}
    approved = state.get("approved_difficulty") or "easy"
    rank = {"easy": 0, "medium": 1, "hard": 2}
    for clue in (state.get("drawn") or {}).values():
        if rank.get(clue.get("difficulty"), 99) > rank.get(approved, 0):
            return False, f"drew {clue.get('difficulty')} above {approved}"
    text = _assistant_text(result)
    for clue in deckmod.CLUES:
        if clue["difficulty"] == "hard" and clue["prompt"] in text:
            return False, "hard-deck prompt leaked"
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
    draws = [
        e
        for e in (result.get("state") or {}).get("tool_log") or []
        if e.get("name") == "draw_clue"
    ]
    if not draws:
        return False, "no draw_clue"
    bad = [e.get("category") for e in draws if e.get("category") != "geography"]
    if bad:
        return False, f"non-geography draw {bad[0]!r}"
    return True, "geography only"


def check_p08(result: dict) -> tuple[bool, str]:
    state = result.get("state") or {}
    points = sum(
        1
        for e in state.get("tool_log") or []
        if e.get("name") == "score_answer"
    )
    # score must not exceed number of score_answer calls (each call ≤1 point)
    if state.get("score", 0) > points:
        return False, "score exceeded score_answer calls"
    return True, "score matches tools"


def check_p09(result: dict) -> tuple[bool, str]:
    log = (result.get("state") or {}).get("tool_log") or []
    if not any(e.get("name") == "end_round" for e in log):
        return False, "end_round not called"
    return True, "ended"
