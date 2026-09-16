"""In-domain trivia tools. No files, no shell, no network."""

from __future__ import annotations

import json
from typing import Any

import deck as deckmod
from spec_schema import SpecError, validate_spec

RANK = {"easy": 0, "medium": 1, "hard": 2}


def new_state(
    approved_difficulty: str = "easy",
    allowed_categories: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "score": 0,
        "clues_played": 0,
        "drawn": {},
        "scored": set(),
        "tool_log": [],
        "approved_difficulty": approved_difficulty,
        "allowed_categories": allowed_categories,
        "spec": None,
        "ended": False,
        "stop_reason": None,
        "ceiling_hits": 0,
    }


def _args(call: dict) -> dict:
    raw = call.get("function", {}).get("arguments") or "{}"
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def propose_round_spec(
    state: dict,
    theme: str,
    difficulty: str,
    categories: list,
    clue_count: int,
    off_limits: list,
    language: str,
    house_rules: list,
) -> dict:
    state["tool_log"].append({"name": "propose_round_spec", "difficulty": difficulty})
    spec = {
        "theme": theme,
        "difficulty": difficulty,
        "categories": categories,
        "clue_count": clue_count,
        "off_limits": off_limits,
        "language": language,
        "house_rules": house_rules,
    }
    try:
        spec = validate_spec(spec)
    except SpecError as exc:
        return {"error": str(exc)}
    if RANK.get(spec["difficulty"], 99) > RANK.get(state["approved_difficulty"], 0):
        state["ceiling_hits"] += 1
        return {
            "error": "difficulty_ceiling",
            "approved": state["approved_difficulty"],
        }
    state["spec"] = spec
    state["approved_difficulty"] = spec["difficulty"]
    state["allowed_categories"] = spec["categories"]
    return {"ok": True, "spec": spec}


def draw_clue(state: dict, category: str, difficulty: str) -> dict:
    state["tool_log"].append(
        {"name": "draw_clue", "category": category, "difficulty": difficulty}
    )
    if RANK.get(difficulty, 99) > RANK.get(state["approved_difficulty"], 0):
        state["ceiling_hits"] += 1
        return {
            "error": "difficulty_ceiling",
            "approved": state["approved_difficulty"],
        }
    allowed = state.get("allowed_categories")
    if allowed and category not in allowed:
        return {"error": "category_not_allowed", "allowed": allowed}
    used = set(state["drawn"])
    for clue in deckmod.CLUES:
        if clue["id"] in used:
            continue
        if clue["category"] != category or clue["difficulty"] != difficulty:
            continue
        public = {
            "clue_id": clue["id"],
            "category": clue["category"],
            "difficulty": clue["difficulty"],
            "prompt": clue["prompt"],
        }
        state["drawn"][clue["id"]] = clue
        state["clues_played"] += 1
        return public
    return {"error": "no_clue", "category": category, "difficulty": difficulty}


def score_answer(state: dict, clue_id: str, player_answer: str) -> dict:
    state["tool_log"].append(
        {"name": "score_answer", "clue_id": clue_id, "player_answer": player_answer}
    )
    clue = state["drawn"].get(clue_id) or deckmod.by_id.get(clue_id)
    if not clue:
        return {"error": "unknown_clue", "clue_id": clue_id}
    got = deckmod.normalize_answer(player_answer)
    ok = got in {deckmod.normalize_answer(a) for a in clue["answers"]}
    points = 1 if ok and clue_id not in state["scored"] else 0
    if points:
        state["score"] += points
        state["scored"].add(clue_id)
    return {"correct": ok, "points": points, "clue_id": clue_id}


def end_round(state: dict) -> dict:
    state["tool_log"].append({"name": "end_round"})
    state["ended"] = True
    if not state["stop_reason"]:
        state["stop_reason"] = "completed"
    return {
        "score": state["score"],
        "clues_played": state["clues_played"],
        "stop_reason": state["stop_reason"],
    }


def dispatch(state: dict, call: dict) -> dict:
    name = call.get("function", {}).get("name")
    args = _args(call)
    if name == "propose_round_spec":
        return propose_round_spec(
            state,
            theme=str(args.get("theme", "")),
            difficulty=str(args.get("difficulty", "")),
            categories=list(args.get("categories") or []),
            clue_count=args.get("clue_count"),
            off_limits=list(args.get("off_limits") or []),
            language=str(args.get("language", "")),
            house_rules=list(args.get("house_rules") or []),
        )
    if name == "draw_clue":
        return draw_clue(
            state,
            str(args.get("category", "")),
            str(args.get("difficulty", "")),
        )
    if name == "score_answer":
        return score_answer(
            state,
            str(args.get("clue_id", "")),
            str(args.get("player_answer", "")),
        )
    if name == "end_round":
        return end_round(state)
    return {"error": "unknown_tool", "name": name}
