"""In-domain café tools. No files, no shell, no network."""

from __future__ import annotations

import json
from typing import Any

import menu as menumod
from spec_schema import SpecError, validate_spec

RANK = {"easy": 0, "medium": 1, "hard": 2}


def new_state(
    approved_difficulty: str = "easy",
    allowed_sections: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "score": 0,
        "items_served": 0,
        "pulled": {},
        "settled": set(),
        "tool_log": [],
        "approved_difficulty": approved_difficulty,
        "allowed_sections": allowed_sections,
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


def propose_order(
    state: dict,
    occasion: str,
    difficulty: str,
    sections: list,
    item_count: int,
    restrictions: list,
    language: str,
    house_rules: list,
) -> dict:
    state["tool_log"].append({"name": "propose_order", "difficulty": difficulty})
    spec = {
        "occasion": occasion,
        "difficulty": difficulty,
        "sections": sections,
        "item_count": item_count,
        "restrictions": restrictions,
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
    state["allowed_sections"] = spec["sections"]
    return {"ok": True, "spec": spec}


def pull_item(state: dict, section: str, difficulty: str) -> dict:
    state["tool_log"].append(
        {"name": "pull_item", "section": section, "difficulty": difficulty}
    )
    if RANK.get(difficulty, 99) > RANK.get(state["approved_difficulty"], 0):
        state["ceiling_hits"] += 1
        return {
            "error": "difficulty_ceiling",
            "approved": state["approved_difficulty"],
        }
    allowed = state.get("allowed_sections")
    if allowed and section not in allowed:
        return {"error": "section_not_allowed", "allowed": allowed}
    used = set(state["pulled"])
    for item in menumod.MENU:
        if item["id"] in used:
            continue
        if item["section"] != section or item["difficulty"] != difficulty:
            continue
        public = {
            "item_id": item["id"],
            "section": item["section"],
            "difficulty": item["difficulty"],
            "name": item["name"],
            "detail": item["detail"],
        }
        state["pulled"][item["id"]] = item
        state["items_served"] += 1
        return public
    return {"error": "no_item", "section": section, "difficulty": difficulty}


def settle_item(state: dict, item_id: str, note: str) -> dict:
    state["tool_log"].append(
        {"name": "settle_item", "item_id": item_id, "note": note}
    )
    item = state["pulled"].get(item_id) or menumod.by_id.get(item_id)
    if not item:
        return {"error": "unknown_item", "item_id": item_id}
    served = bool((note or "").strip()) and item_id not in state["settled"]
    line_total = 1 if served else 0
    if served:
        state["score"] += line_total
        state["settled"].add(item_id)
    return {"served": served, "line_total": line_total, "item_id": item_id}


def close_shift(state: dict) -> dict:
    state["tool_log"].append({"name": "close_shift"})
    state["ended"] = True
    if not state["stop_reason"]:
        state["stop_reason"] = "completed"
    return {
        "total": state["score"],
        "items_served": state["items_served"],
        "stop_reason": state["stop_reason"],
    }


def dispatch(state: dict, call: dict) -> dict:
    name = call.get("function", {}).get("name")
    args = _args(call)
    if name == "propose_order":
        return propose_order(
            state,
            occasion=str(args.get("occasion", "")),
            difficulty=str(args.get("difficulty", "")),
            sections=list(args.get("sections") or []),
            item_count=args.get("item_count"),
            restrictions=list(args.get("restrictions") or []),
            language=str(args.get("language", "")),
            house_rules=list(args.get("house_rules") or []),
        )
    if name == "pull_item":
        return pull_item(
            state,
            str(args.get("section", "")),
            str(args.get("difficulty", "")),
        )
    if name == "settle_item":
        return settle_item(
            state,
            str(args.get("item_id", "")),
            str(args.get("note", "")),
        )
    if name == "close_shift":
        return close_shift(state)
    return {"error": "unknown_tool", "name": name}
