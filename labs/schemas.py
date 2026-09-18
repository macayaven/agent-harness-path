"""OpenAI function schemas for the café host. Shared so replay match keys stay stable."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "propose_order",
            "description": "Propose an order spec for the consent gate. All fields required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "occasion": {"type": "string"},
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                    },
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["espresso", "pastry", "kitchen"],
                        },
                    },
                    "item_count": {"type": "integer", "minimum": 1, "maximum": 5},
                    "restrictions": {"type": "array", "items": {"type": "string"}},
                    "language": {"type": "string", "enum": ["en"]},
                    "house_rules": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "occasion",
                    "difficulty",
                    "sections",
                    "item_count",
                    "restrictions",
                    "language",
                    "house_rules",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pull_item",
            "description": "Pull the next unserved menu item from the kitchen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["espresso", "pastry", "kitchen"],
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                    },
                },
                "required": ["section", "difficulty"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "settle_item",
            "description": "Settle a pulled item against the ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["item_id", "note"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_shift",
            "description": "Close the shift and return the bill.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
