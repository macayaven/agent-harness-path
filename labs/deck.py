"""Canned pub-quiz clues. Fixture data — not the student implementation."""

from __future__ import annotations

CLUES: list[dict] = [
    {
        "id": "c01",
        "category": "science",
        "difficulty": "easy",
        "prompt": "What is the chemical formula for water?",
        "answers": ["h2o", "water", "dihydrogen monoxide"],
    },
    {
        "id": "c02",
        "category": "science",
        "difficulty": "easy",
        "prompt": "How many planets are in the Solar System as currently recognized?",
        "answers": ["8", "eight"],
    },
    {
        "id": "c03",
        "category": "science",
        "difficulty": "medium",
        "prompt": "What particle carries a negative electric charge in an atom?",
        "answers": ["electron", "the electron"],
    },
    {
        "id": "c04",
        "category": "science",
        "difficulty": "hard",
        "prompt": "What is the name of the theorem that the square of the hypotenuse equals the sum of the squares of the other two sides?",
        "answers": ["pythagorean theorem", "pythagoras", "pythagorean"],
    },
    {
        "id": "c05",
        "category": "geography",
        "difficulty": "easy",
        "prompt": "What is the capital city of France?",
        "answers": ["paris"],
    },
    {
        "id": "c06",
        "category": "geography",
        "difficulty": "easy",
        "prompt": "Which ocean is the largest by area?",
        "answers": ["pacific", "pacific ocean", "the pacific"],
    },
    {
        "id": "c07",
        "category": "geography",
        "difficulty": "medium",
        "prompt": "On which continent is the Nile River primarily located?",
        "answers": ["africa"],
    },
    {
        "id": "c08",
        "category": "geography",
        "difficulty": "hard",
        "prompt": "What is the highest mountain outside Asia, by elevation above sea level?",
        "answers": ["aconcagua"],
    },
    {
        "id": "c09",
        "category": "literature",
        "difficulty": "easy",
        "prompt": "Who wrote the play Hamlet?",
        "answers": ["shakespeare", "william shakespeare"],
    },
    {
        "id": "c10",
        "category": "literature",
        "difficulty": "easy",
        "prompt": "What is the title of Cervantes' novel about a knight and a windmill?",
        "answers": ["don quixote", "don quijote", "don quijote de la mancha"],
    },
    {
        "id": "c11",
        "category": "literature",
        "difficulty": "medium",
        "prompt": "In The Odyssey, who is the protagonist trying to return to Ithaca?",
        "answers": ["odysseus", "ulysses"],
    },
    {
        "id": "c12",
        "category": "literature",
        "difficulty": "hard",
        "prompt": "Who wrote the Divine Comedy?",
        "answers": ["dante", "dante alighieri"],
    },
]

by_id = {c["id"]: c for c in CLUES}


def normalize_answer(text: str) -> str:
    return " ".join(text.casefold().split())
