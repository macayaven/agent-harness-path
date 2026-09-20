# S07 bridge — bounded repair (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/repair.py` (bounded regeneration on a
bad ticket). Optional café-host lab: `sessions/s07-repair-loop/lab.md`, repair
`while hit and retries < 3` in `labs/cafe_host/engine.py`, `stop_reason`
values in `tools.close_shift` / engine.

## The gap

The core toy retries a bad model turn with a cap; `cafe/repair.py` is that
bounded re-ask. The optional café host, after each user line and `run_loop`,
calls `turn_policy_hit` on the new suffix. If hit and `retries < 3`: delete
messages from `after_user:`, append a short repair user line
(`Policy {hit}: do not leak… Use tools only.`), run the loop again. Never raise
approved scope on retry. If still hit: `stop_reason=retries_exhausted`.

Every run should end with
`stop_reason ∈ {completed, retries_exhausted, turn_cap, budget_exceeded, rejected, invalid_edit, invalid_decision, policy_refusal}`.
Print it (the returned dict and `state["stop_reason"]`). No ambiguous exits.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s07-repair-loop/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s07 --replay
```

Record a delta vs S05/S06: which tasks moved, one line each. Remaining
fails also get a line. On the shipped host, engine p01–p06 already pass;
the delta may be “none, still 6/6” — that is a valid record if true.

## Predict-first

If a supplier-reference leak happens, does the bad assistant turn remain in the
product transcript? (No: suffix is deleted before retry.)

## Assistant: do / don't

Do: show the delete-and-retry slice. Don't: infinite repair. Don't: grow
the approved scope to “get a better item” on retry.
