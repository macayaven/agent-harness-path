"""Every domain string in one place, so re-theming stays a one-module change.

Dialogue is Spanish (the café is a Spanish-speaking neighbourhood place); all
prose, comments and identifiers are English.
"""

from __future__ import annotations

# --- the menu -------------------------------------------------------------
# price in euros; allergens use the EU 14-allergen short names.
MENU: dict[str, dict] = {
    "cortado": {"price": 1.60, "allergens": ["milk"], "station": "bar"},
    "café solo": {"price": 1.30, "allergens": [], "station": "bar"},
    "leche merengada": {"price": 2.80, "allergens": ["milk"], "station": "bar"},
    "tostada con tomate": {"price": 2.40, "allergens": ["gluten"], "station": "kitchen"},
    "tortilla": {"price": 3.20, "allergens": ["egg"], "station": "kitchen"},
    "croissant": {"price": 1.90, "allergens": ["gluten", "milk", "egg"], "station": "pastry"},
    "napolitana": {"price": 2.10, "allergens": ["gluten", "milk", "egg"], "station": "pastry"},
    "zumo de naranja": {"price": 2.50, "allergens": [], "station": "bar"},
}

# Items the kitchen has run out of tonight. "86'd" is the trade term.
EIGHTY_SIXED: tuple[str, ...] = ("tortilla",)

# --- shift rules ----------------------------------------------------------
SHIFT_RULES: tuple[str, ...] = (
    "Never confirm a dish is safe for a declared allergy without checking the menu data.",
    "Never invent a price; every price comes from the menu tool.",
    "Never fire a ticket the customer has not confirmed.",
    "Items that are 86'd cannot be ordered; offer the closest alternative.",
)

PERSONA = (
    "Eres quien atiende la barra de un café de barrio. Tomas pedidos, confirmas "
    "alergias y cobras. Responde en español, breve y claro."
)

# --- refusal / safety texts ----------------------------------------------
ALLERGEN_REFUSAL = (
    "No puedo confirmar que eso sea seguro con tu alergia. Déjame comprobar la "
    "carta antes de pedirlo."
)
OFF_MENU_REFUSAL = "Eso no está en la carta hoy. ¿Te ofrezco algo parecido?"

# --- tool schemas (in-domain, fixed by plan 0002 §5.2) --------------------
TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "price_check",
            "description": "Look up one menu item: price, allergens, station, availability.",
            "parameters": {
                "type": "object",
                "properties": {"item": {"type": "string"}},
                "required": ["item"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_allergens",
            "description": "Check one menu item against a declared allergen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "allergen": {"type": "string"},
                },
                "required": ["item", "allergen"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_order",
            "description": "Draft the order for the customer to confirm. Does not fire it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"type": "string"}},
                    "table": {"type": "integer"},
                },
                "required": ["items", "table"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fire_ticket",
            "description": "Send a CONFIRMED order to the kitchen. Irreversible side effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"type": "string"}},
                    "table": {"type": "integer"},
                },
                "required": ["items", "table"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_check",
            "description": "Settle and close the table's check.",
            "parameters": {
                "type": "object",
                "properties": {"table": {"type": "integer"}},
                "required": ["table"],
            },
        },
    },
]

TOOL_NAMES: tuple[str, ...] = tuple(s["function"]["name"] for s in TOOL_SCHEMAS)
