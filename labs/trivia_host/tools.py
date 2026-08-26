"""S01: implement draw_clue / score_answer / end_round using labs.deck.

Tool *schemas* live in labs/schemas.py — do not fork them if you want --replay
against the course cassettes. Exact success/error envelope keys are the public
wire contract documented in labs/README.md.
"""

from __future__ import annotations

from typing import Any


def new_state(approved_difficulty: str = "easy") -> dict[str, Any]:
    raise NotImplementedError("labs/s01_loop.md — implement new_state")


def dispatch(state: dict, call: dict) -> dict:
    raise NotImplementedError("labs/s01_loop.md — implement dispatch")
