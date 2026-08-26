# S11 lab — budgets, routing, refusal

**Optional. After the notebook.**

**Read:** [S11-budgets-routing](../lessons/S11-budgets-routing.html).

There is no LiteLLM vault in this path. Routing is an env var and a code
check: session-content phases refuse `OPENAI_ROUTE_KIND=cloud`.

## Build

1. Turn cap and an approximate token budget (`len(json)/4` is enough). Breach
   → `stop_reason=budget_exceeded`.
2. Optional: send spec-generation vs play to different `OPENAI_MODEL` values
   if you have two. Defaults may be the same model.
3. `run_engine(..., route_kind="cloud")` must raise before any POST.

## Verify (predict first)

```bash
uv run python labs/run.py --session s11 --replay
```

You should see `PASS s11: cloud route refused`. If you `--live`, fill a small
matrix in PROGRESS: pass rate / notes on p50 — replay cannot honestly time a
model.

## Record

PROGRESS: matrix (live) or "replay: refusal demonstrated"; default config
cites it.

## Done when

The refusal is demonstrated and the suite still runs.
