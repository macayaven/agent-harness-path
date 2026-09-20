# S11 lab — budgets, routing, refusal

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S11-budgets-routing](lesson.html).

There is no LiteLLM vault in this path. Routing is an env var and a code
check: session-content phases refuse `OPENAI_ROUTE_KIND=cloud`. This is a declared
route kind, not proof of endpoint locality. Verify the actual transport before
sending sensitive input; course fixtures remain synthetic.

## Build

1. Turn cap and an approximate token budget (`len(json)/4` is enough). Breach
   → `stop_reason=budget_exceeded`.
2. Optional: send spec vs serve to different `OPENAI_MODEL` values
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
