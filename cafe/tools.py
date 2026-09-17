"""The five in-domain tools. Local Python; the model only ever requests them."""

from __future__ import annotations

import json
from typing import Any

from cafe import domain

__all__ = ["TOOLS", "dispatch", "OrderState"]


class OrderState:
    """What the shift actually did. Side effects live here, never in the model."""

    def __init__(self) -> None:
        self.proposed: dict | None = None
        self.fired: list[dict] = []
        self.closed: list[int] = []
        self.tool_log: list[str] = []

    def snapshot(self) -> dict:
        return {
            "proposed": self.proposed,
            "fired": [dict(t) for t in self.fired],
            "closed": list(self.closed),
            "tool_log": list(self.tool_log),
        }


def price_check(state: OrderState, item: str) -> dict:
    entry = domain.MENU.get(item)
    if entry is None:
        return {"item": item, "on_menu": False, "reason": "not on the menu today"}
    return {
        "item": item,
        "on_menu": True,
        "price_eur": entry["price"],
        "allergens": list(entry["allergens"]),
        "station": entry["station"],
        "available": item not in domain.EIGHTY_SIXED,
    }


def check_allergens(state: OrderState, item: str, allergen: str) -> dict:
    entry = domain.MENU.get(item)
    if entry is None:
        return {"item": item, "on_menu": False, "safe": None}
    contains = allergen.strip().lower() in [a.lower() for a in entry["allergens"]]
    return {
        "item": item,
        "on_menu": True,
        "allergen": allergen,
        "contains": contains,
        "safe": not contains,
    }


def propose_order(state: OrderState, items: list, table: int) -> dict:
    unknown = [i for i in items if i not in domain.MENU]
    unavailable = [i for i in items if i in domain.EIGHTY_SIXED]
    total = round(sum(domain.MENU[i]["price"] for i in items if i in domain.MENU), 2)
    state.proposed = {"items": list(items), "table": table, "total_eur": total}
    return {
        "proposed": state.proposed,
        "unknown_items": unknown,
        "unavailable_items": unavailable,
        "needs_confirmation": True,
    }


def fire_ticket(state: OrderState, items: list, table: int) -> dict:
    """The irreversible one. S05 puts a consent gate in front of it."""
    ticket = {"items": list(items), "table": table}
    state.fired.append(ticket)
    return {"fired": ticket, "ticket_number": len(state.fired)}


def close_check(state: OrderState, table: int) -> dict:
    state.closed.append(table)
    total = round(
        sum(
            domain.MENU[i]["price"]
            for t in state.fired
            if t["table"] == table
            for i in t["items"]
            if i in domain.MENU
        ),
        2,
    )
    return {"table": table, "closed": True, "total_eur": total}


TOOLS = {
    "price_check": price_check,
    "check_allergens": check_allergens,
    "propose_order": propose_order,
    "fire_ticket": fire_ticket,
    "close_check": close_check,
}


def dispatch(state: OrderState, call: dict) -> Any:
    """Execute one tool_call locally. Errors become tool results, not crashes."""
    name = call.get("function", {}).get("name", "")
    raw = call.get("function", {}).get("arguments") or "{}"
    state.tool_log.append(name)
    try:
        arguments = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except json.JSONDecodeError:
        return {"error": "arguments were not valid JSON", "tool": name}
    handler = TOOLS.get(name)
    if handler is None:
        return {"error": f"unknown tool {name!r}", "available": list(TOOLS)}
    try:
        return handler(state, **arguments)
    except TypeError as exc:
        return {"error": f"bad arguments for {name}: {exc}"}
