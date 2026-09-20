"""In-domain café tools. No files, no shell, no network."""

from __future__ import annotations

import json
from typing import Any

import menu as menumod
from spec_schema import SpecError, validate_spec

RANK = {"counter": 0, "kitchen": 1, "banquet": 2}


def new_state(
    approved_scope: str = "counter",
    allowed_sections: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "score": 0,
        "items_served": 0,
        "pulled": {},
        "settled": set(),
        "tool_log": [],
        "approved_scope": approved_scope,
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
    scope: str,
    sections: list,
    item_count: int,
    restrictions: list,
    language: str,
    house_rules: list,
) -> dict:
    state["tool_log"].append({"name": "propose_order", "scope": scope})
    spec = {
        "occasion": occasion,
        "scope": scope,
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
    if RANK.get(spec["scope"], 99) > RANK.get(state["approved_scope"], 0):
        state["ceiling_hits"] += 1
        return {
            "error": "scope_ceiling",
            "approved": state["approved_scope"],
        }
    state["spec"] = spec
    state["approved_scope"] = spec["scope"]
    state["allowed_sections"] = spec["sections"]
    return {"ok": True, "spec": spec}


def pull_item(state: dict, section: str, scope: str) -> dict:
    state["tool_log"].append(
        {"name": "pull_item", "section": section, "scope": scope}
    )
    if RANK.get(scope, 99) > RANK.get(state["approved_scope"], 0):
        state["ceiling_hits"] += 1
        return {
            "error": "scope_ceiling",
            "approved": state["approved_scope"],
        }
    allowed = state.get("allowed_sections")
    if allowed and section not in allowed:
        return {"error": "section_not_allowed", "allowed": allowed}
    used = set(state["pulled"])
    for item in menumod.MENU:
        if item["id"] in used:
            continue
        if item["section"] != section or item["scope"] != scope:
            continue
        tool_data = {
            "item_id": item["id"],
            "section": item["section"],
            "scope": item["scope"],
            "name": item["name"],
            "detail": item["detail"],
            "allergens": list(item["allergens"]),
            "internal_supplier_ref": item["internal_supplier_ref"],
        }
        state["pulled"][item["id"]] = item
        state["items_served"] += 1
        return tool_data
    return {"error": "no_item", "section": section, "scope": scope}


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
            scope=str(args.get("scope", "")),
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
            str(args.get("scope", "")),
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
