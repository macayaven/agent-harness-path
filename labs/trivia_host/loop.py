"""S01: implement the client-owned loop. See labs/s01_loop.md.

Signatures must stay stable: course cassettes match this call shape. Non-string
tool results use client.canonicalize(result); see the public wire contract in
labs/README.md.
"""

from __future__ import annotations

from typing import Any, Callable


def run_loop(
    client: Any,
    messages: list[dict],
    tools: list[dict],
    dispatch: Callable[[dict], Any],
    *,
    max_turns: int = 8,
) -> tuple[list[dict], str]:
    raise NotImplementedError("labs/s01_loop.md — implement run_loop")
