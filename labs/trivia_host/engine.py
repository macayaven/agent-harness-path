"""Wire naïve vs engine here as the labs ask. Keep house_rules.PINNED_RULES pinned.

S03+: persona below the pin is yours — after you change it, --replay against
course cassettes will mismatch; use --live or --record into labs/work/. The
public replay wire contract is documented in labs/README.md.
"""

from __future__ import annotations

from typing import Any, Callable


def run_naive(client: Any, script: list[str]) -> dict[str, Any]:
    raise NotImplementedError("labs/s02_evals.md — implement run_naive")


def run_engine(
    client: Any,
    script: list[str],
    *,
    spec: dict | None = None,
    generate_from_brief: bool = False,
    auto_approve: bool = True,
    input_fn: Callable[[str], str] | None = None,
    max_turns: int = 8,
    max_messages: int | None = None,
    max_approx_tokens: int = 20000,
    route_kind: str | None = None,
) -> dict[str, Any]:
    raise NotImplementedError("labs/s01_loop.md — implement run_engine")


def compact(messages: list[dict], *, keep: int) -> list[dict]:
    raise NotImplementedError("labs/s03_context.md — implement compact")
