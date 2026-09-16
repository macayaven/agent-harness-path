"""OpenAI function schemas for the trivia host. Shared so replay match keys stay stable."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "propose_round_spec",
            "description": "Propose a round spec for the consent gate. All fields required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["science", "geography", "literature"],
                        },
                    },
                    "clue_count": {"type": "integer", "minimum": 1, "maximum": 5},
                    "off_limits": {"type": "array", "items": {"type": "string"}},
                    "language": {"type": "string", "enum": ["en", "es"]},
                    "house_rules": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "theme",
                    "difficulty",
                    "categories",
                    "clue_count",
                    "off_limits",
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
            "name": "draw_clue",
            "description": "Draw the next unused clue from the canned deck.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["science", "geography", "literature"],
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                    },
                },
                "required": ["category", "difficulty"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "score_answer",
            "description": "Score the player's answer against the drawn clue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clue_id": {"type": "string"},
                    "player_answer": {"type": "string"},
                },
                "required": ["clue_id", "player_answer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_round",
            "description": "End the round and return the tally.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
