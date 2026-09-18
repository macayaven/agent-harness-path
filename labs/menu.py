"""Canned café menu. Fixture data — not the student implementation."""

from __future__ import annotations

MENU: list[dict] = [
    {
        "id": "m01",
        "section": "espresso",
        "difficulty": "easy",
        "name": "espresso",
        "detail": "A double shot, crema intact.",
        "allergens": [],
    },
    {
        "id": "m02",
        "section": "espresso",
        "difficulty": "easy",
        "name": "oat-milk latte",
        "detail": "Steamed oat milk over a double shot.",
        "allergens": ["oats", "gluten"],
    },
    {
        "id": "m03",
        "section": "espresso",
        "difficulty": "medium",
        "name": "cappuccino",
        "detail": "Dry foam, cocoa dust, double shot.",
        "allergens": ["dairy", "lactose", "cocoa"],
    },
    {
        "id": "m04",
        "section": "espresso",
        "difficulty": "hard",
        "name": "affogato",
        "detail": "Vanilla gelato drowned in a double shot.",
        "allergens": ["dairy", "eggs"],
    },
    {
        "id": "m05",
        "section": "pastry",
        "difficulty": "easy",
        "name": "butter croissant",
        "detail": "Laminated, baked at dawn.",
        "allergens": ["wheat", "gluten", "dairy"],
    },
    {
        "id": "m06",
        "section": "pastry",
        "difficulty": "easy",
        "name": "blueberry muffin",
        "detail": "Buttermilk crumb, fresh berries.",
        "allergens": ["wheat", "eggs", "dairy"],
    },
    {
        "id": "m07",
        "section": "pastry",
        "difficulty": "medium",
        "name": "banana bread",
        "detail": "Toasted, salted butter on request.",
        "allergens": ["wheat", "eggs", "walnuts"],
    },
    {
        "id": "m08",
        "section": "pastry",
        "difficulty": "hard",
        "name": "almond tart",
        "detail": "Frangipane, blind-baked shell.",
        "allergens": ["almonds", "tree nuts", "wheat", "dairy", "eggs"],
    },
    {
        "id": "m09",
        "section": "kitchen",
        "difficulty": "easy",
        "name": "tomato toast",
        "detail": "Sourdough, crushed tomato, olive oil.",
        "allergens": ["wheat", "gluten"],
    },
    {
        "id": "m10",
        "section": "kitchen",
        "difficulty": "easy",
        "name": "grilled cheese",
        "detail": "Three cheeses, pressed sourdough.",
        "allergens": ["wheat", "dairy"],
    },
    {
        "id": "m11",
        "section": "kitchen",
        "difficulty": "medium",
        "name": "shakshuka",
        "detail": "Baked eggs, harissa, flatbread.",
        "allergens": ["eggs", "wheat"],
    },
    {
        "id": "m12",
        "section": "kitchen",
        "difficulty": "hard",
        "name": "full breakfast",
        "detail": "Eggs, sausage, beans, toast, tea.",
        "allergens": ["eggs", "dairy", "wheat", "pork"],
    },
]

by_id = {item["id"]: item for item in MENU}


def normalize_answer(text: str) -> str:
    return " ".join(text.casefold().split())
