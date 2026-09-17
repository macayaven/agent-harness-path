"""S11 - budgets as runtime invariants, routing as policy-as-data.

Two rules this module makes mechanical:

  * a call whose *projected* cost would cross the run budget is REFUSED before
    dispatch, so that cost never lands. The gate reads ahead with an estimate;
    the ledger records what the endpoint actually reported;
  * customer card/phone content never routes off-local. A misconfigured table
    raises before any model call. It never falls back silently.

Nothing here simulates a model. Tokens come from `response["usage"]` and latency
from `client.last_latency_ms`, both measured on the client the notebook was
handed. `cafe.evals` (S02) and `cafe.trace` (S08) are imported when present and
degraded politely when absent, so this session can land before its neighbours.
"""

from __future__ import annotations

import math
from typing import Any

try:
    from cafe import evals as _evals
except ImportError:  # S02 has not landed yet; the route table still stands alone
    _evals = None

try:
    from cafe import trace as _trace
except ImportError:  # S08 has not landed yet; the ledger stays in memory
    _trace = None

__all__ = [
    "Budget",
    "CONTENT",
    "METADATA",
    "PHASES",
    "ROUTES",
    "RouteRefused",
    "checker_names",
    "companion_note",
    "describe_routes",
    "estimate_prompt_tokens",
    "metered_call",
    "projected_usd",
    "publish",
    "run_phases",
    "validate_policy",
]

CONTENT = "content"
METADATA = "metadata"

# What each phase of a shift carries. Classification is a property of the data,
# not of the vendor: `read_note` sees the customer's handwritten note, which is
# exactly where a card number or a phone number shows up.
PHASES: dict[str, str] = {
    "read_note": CONTENT,
    "draft_reply": CONTENT,
    "till_summary": METADATA,
}

# Policy-as-data: a diffable table, reviewable without touching the engine.
# `model` is the label you booked, `location` is the boundary that cannot move,
# `usd_per_1k` is what the call costs if it is dispatched.
ROUTES: dict[str, dict] = {
    "local-small": {
        "location": "local",
        "model": "qwen2.5:3b-instruct",
        "usd_per_1k": 0.01,
    },
    "local-large": {
        "location": "local",
        "model": "qwen2.5:14b-instruct",
        "usd_per_1k": 0.06,
    },
    "cloud-frontier": {
        "location": "cloud",
        "model": "a-frontier-instruct",
        "usd_per_1k": 0.30,
    },
}

# A pre-dispatch estimate is all a budget gate can have: the endpoint has not
# spoken yet. Roughly four characters per token, plus room for the reply.
CHARS_PER_TOKEN = 4
ASSUMED_COMPLETION_TOKENS = 120


class RouteRefused(RuntimeError):
    """A route table that would leak content or name an unknown route."""


def validate_policy(route_table: dict[str, str], routes: dict[str, dict] | None = None) -> None:
    """Refuse a table that sends content off-local, before any model call.

    Validated against the SAME mapping the run will use - validating one table
    while running another is no validation. Raises; it does not warn and does
    not fall back to a "safe" route, because a silent fallback is the bug.
    """
    routes = ROUTES if routes is None else routes
    for phase, classification in PHASES.items():
        name = route_table.get(phase)
        if name is None:
            raise RouteRefused(f"{phase}: no route configured")
        if name not in routes:
            raise RouteRefused(f"{phase}: unknown route {name!r}")
        location = routes[name]["location"]
        if classification == CONTENT and location != "local":
            raise RouteRefused(
                f"{phase} handles {classification} data but routes to {name} "
                f"({location}) - content phases stay local"
            )


def estimate_prompt_tokens(messages: list[dict]) -> int:
    """A character-count estimate. The estimate is the gate, the usage is the truth."""
    chars = sum(len(str(message.get("content") or "")) for message in messages)
    return max(1, math.ceil(chars / CHARS_PER_TOKEN))


def projected_usd(route: dict, messages: list[dict]) -> float:
    """What the next call on this route is expected to cost before it is made."""
    tokens = estimate_prompt_tokens(messages) + ASSUMED_COMPLETION_TOKENS
    return tokens / 1000.0 * route["usd_per_1k"]


class Budget:
    """The run's money: the gate reads it, the post-call meter writes it."""

    def __init__(self, budget_usd: float | None = None) -> None:
        self.budget_usd = budget_usd
        self.spent_usd = 0.0
        self.calls: list[dict] = []

    def would_exceed(self, projected: float) -> bool:
        """True when dispatching this call could cross the budget. No budget, no limit."""
        return self.budget_usd is not None and self.spent_usd + projected > self.budget_usd


def metered_call(
    client: Any,
    route_table: dict[str, str],
    phase: str,
    messages: list[dict],
    *,
    budget: Budget | None = None,
    routes: dict[str, dict] | None = None,
    tools: list[dict] | None = None,
    temperature: float = 0.0,
) -> dict:
    """One metered call, or a refusal record with `dispatched=False`.

    A refused call is never sent, so `client.calls` and `client.last_latency_ms`
    keep the values of the previous dispatched call - which is how the notebook
    proves the refusal happened before the wire.
    """
    routes = ROUTES if routes is None else routes
    budget = budget if budget is not None else Budget()
    name = route_table[phase]
    route = routes[name]
    projected = projected_usd(route, messages)

    if budget.would_exceed(projected):
        record = {
            "phase": phase,
            "route": name,
            "model": route["model"],
            "dispatched": False,
            "refusal": "projected_over_budget",
            "projected_usd": round(projected, 6),
            "spent_usd": round(budget.spent_usd, 6),
            "tokens": None,
            "cost_usd": None,
            "latency_ms": None,
        }
        budget.calls.append(record)
        return record

    response = client.chat(messages, tools=tools, temperature=temperature)
    usage = response.get("usage") or {}
    tokens = int(usage.get("total_tokens") or 0)
    cost = round(tokens / 1000.0 * route["usd_per_1k"], 6)
    budget.spent_usd = round(budget.spent_usd + cost, 6)
    record = {
        "phase": phase,
        "route": name,
        "model": route["model"],
        "dispatched": True,
        "refusal": None,
        "projected_usd": round(projected, 6),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "tokens": tokens,
        "cost_usd": cost,
        "latency_ms": getattr(client, "last_latency_ms", None),
        "spent_usd": budget.spent_usd,
        "response": response,
    }
    budget.calls.append(record)
    return record


def run_phases(
    client: Any,
    route_table: dict[str, str],
    phases: list[tuple[str, list[dict]]],
    *,
    budget_usd: float | None = None,
    routes: dict[str, dict] | None = None,
) -> dict:
    """Validate, then run `(phase, messages)` pairs until one call is refused."""
    routes = ROUTES if routes is None else routes
    validate_policy(route_table, routes)
    budget = Budget(budget_usd)
    stop_reason = "ok"
    for phase, messages in phases:
        record = metered_call(
            client, route_table, phase, messages, budget=budget, routes=routes
        )
        if not record["dispatched"]:
            stop_reason = "budget_exceeded"
            break
    return {"stop_reason": stop_reason, "budget": budget, "records": list(budget.calls)}


def describe_routes(routes: dict[str, dict] | None = None) -> list[str]:
    routes = ROUTES if routes is None else routes
    return [
        f"{name:14s} {route['location']:5s} ${route['usd_per_1k']:.2f}/1k  {route['model']}"
        for name, route in routes.items()
    ]


def checker_names() -> tuple[str, ...]:
    """S02's deterministic checkers, when that package is importable. Else empty."""
    if _evals is None:
        return ()
    table = getattr(_evals, "CHECKERS", None)
    if isinstance(table, dict):
        return tuple(table)
    if isinstance(table, (list, tuple)):
        return tuple(table)
    return ()


def companion_note() -> str:
    """Say out loud which neighbouring sessions this run could actually see."""
    evals_note = (
        f"cafe.evals: importable ({len(checker_names())} S02 checkers)"
        if _evals is not None
        else "cafe.evals: absent - the route table cites no checker this run"
    )
    trace_note = (
        "cafe.trace: importable"
        if _trace is not None
        else "cafe.trace: absent - the ledger stays in memory this run"
    )
    return f"{evals_note}; {trace_note}"


def publish(run: dict, tracer: Any = None) -> Any:
    """Mirror a routed run into S08's span tree when that module exists.

    Returns the tracer it used, or `None` when `cafe.trace` is absent - the run
    itself is unaffected either way. One span per dispatched call (kind
    `generation`, carrying the measured usage) and one per refused call, so the
    refusal is visible in the trace and not only in the ledger.
    """
    if tracer is None:
        if _trace is None:
            return None
        factory = getattr(_trace, "Tracer", None)
        if not callable(factory):
            return None
        tracer = factory()
    span = getattr(tracer, "span", None)
    if not callable(span):
        return None
    with span("routed_shift", stop_reason=run.get("stop_reason")):
        for record in run.get("records", []):
            if record["dispatched"]:
                with span(
                    record["phase"],
                    kind="generation",
                    route=record["route"],
                    usage={"total_tokens": record["tokens"]},
                ) as attrs:
                    attrs["latency_ms"] = record["latency_ms"]
            else:
                with span(
                    record["phase"],
                    kind="span",
                    route=record["route"],
                    refusal=record["refusal"],
                ):
                    pass
    return tracer
