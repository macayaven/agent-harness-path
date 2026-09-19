# S11 bridge — budgets and route refusal (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/routing.py` (budget gate, route
table, the boundary that refuses a leak). Optional café-host lab:
`sessions/s11-budgets-routing/lab.md`, `run_engine` `max_approx_tokens` / `RouteRefused` in
`labs/cafe_host/engine.py`, `client.RouteRefused`.

## The gap

The core toy runs live: a turn cap, a token counter, and a route table that
refuses a leak. The optional café host:

- Approximates tokens as `len(json.dumps(messages)) // 4`. Breach →
  `stop_reason=budget_exceeded` (no LiteLLM).
- `route_kind` argument or `OPENAI_ROUTE_KIND` env: if `cloud`, raise
  `RouteRefused` **before any POST** (`session-content phase refuses …`).
- Optional: different `OPENAI_MODEL` for spec vs serve — not required.

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s11-budgets-routing/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s11 --replay
# expect: PASS s11: cloud route refused
```

`--live` timing/p50 is the only honest latency story; replay cannot time a
model. Record a small matrix in PROGRESS if you live-run.

## Predict-first

Does `OPENAI_ROUTE_KIND=cloud` still run `client.chat`? (No.)

## Assistant: do / don't

Do: point at the raise before `run_loop`. Don't: add a cloud provider “just
for spec generation” in this path. Don't: confuse Cursor tutor routing with
`OPENAI_ROUTE_KIND` for the café host.
