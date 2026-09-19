"""Canned café menu. Fixture data — not the student implementation."""

from __future__ import annotations

MENU: list[dict] = [
    {
        "id": "m01",
        "section": "espresso",
        "scope": "counter",
        "name": "espresso",
        "detail": "A double shot, crema intact.",
        "allergens": [],
    },
    {
        "id": "m02",
        "section": "espresso",
        "scope": "counter",
        "name": "oat-milk latte",
        "detail": "Steamed oat milk over a double shot.",
        "allergens": ["oats", "gluten"],
    },
    {
        "id": "m03",
        "section": "espresso",
        "scope": "kitchen",
        "name": "cappuccino",
        "detail": "Dry foam, cocoa dust, double shot.",
        "allergens": ["dairy", "lactose", "cocoa"],
    },
    {
        "id": "m04",
        "section": "espresso",
        "scope": "banquet",
        "name": "affogato",
        "detail": "Vanilla gelato drowned in a double shot.",
        "allergens": ["dairy", "eggs"],
    },
    {
        "id": "m05",
        "section": "pastry",
        "scope": "counter",
        "name": "butter croissant",
        "detail": "Laminated, baked at dawn.",
        "allergens": ["wheat", "gluten", "dairy"],
    },
    {
        "id": "m06",
        "section": "pastry",
        "scope": "counter",
        "name": "blueberry muffin",
        "detail": "Buttermilk crumb, fresh berries.",
        "allergens": ["wheat", "eggs", "dairy"],
    },
    {
        "id": "m07",
        "section": "pastry",
        "scope": "kitchen",
        "name": "banana bread",
        "detail": "Toasted, salted butter on request.",
        "allergens": ["wheat", "eggs", "walnuts"],
    },
    {
        "id": "m08",
        "section": "pastry",
        "scope": "banquet",
        "name": "almond tart",
        "detail": "Frangipane, blind-baked shell.",
        "allergens": ["almonds", "tree nuts", "wheat", "dairy", "eggs"],
    },
    {
        "id": "m09",
        "section": "kitchen",
        "scope": "counter",
        "name": "tomato toast",
        "detail": "Sourdough, crushed tomato, olive oil.",
        "allergens": ["wheat", "gluten"],
    },
    {
        "id": "m10",
        "section": "kitchen",
        "scope": "counter",
        "name": "grilled cheese",
        "detail": "Three cheeses, pressed sourdough.",
        "allergens": ["wheat", "dairy"],
    },
    {
        "id": "m11",
        "section": "kitchen",
        "scope": "kitchen",
        "name": "shakshuka",
        "detail": "Baked eggs, harissa, flatbread.",
        "allergens": ["eggs", "wheat"],
    },
    {
        "id": "m12",
        "section": "kitchen",
        "scope": "banquet",
        "name": "full breakfast",
        "detail": "Eggs, sausage, beans, toast, tea.",
        "allergens": ["eggs", "dairy", "wheat", "pork"],
    },
]

by_id = {item["id"]: item for item in MENU}


def normalize_answer(text: str) -> str:
    return " ".join(text.casefold().split())
