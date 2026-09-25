# S07 companion — bounded repair (real host)

> Tutor context for this session. Attach it in editor chat (`@sessions/s07-repair-loop/companion.md`); you do not need to read it to finish the session.

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

The core's authored cap control alternates contract and availability failures;
it does not claim an unsatisfiable allergy request entered the loop. Its model
prompt includes the inherited fields and menu facts. The
[recorded comparison](recordings/model.jsonl) replays the ordinary demonstration
and three checkpoint orders; it is a selected example, not a quality estimate.

Every run should end with
`stop_reason ∈ {completed, retries_exhausted, turn_cap, budget_exceeded, rejected, invalid_edit, invalid_decision, policy_refusal}`.
Print it (the returned dict and `state["stop_reason"]`). No ambiguous exits.

## Commands

```bash
# core path: offline by default; COURSE_MODE=live opts into your configured endpoint
uv run marimo edit sessions/s07-repair-loop/toy.py
# after your prediction and attempt: replay the recorded model comparison offline
uv run python tools/record_fixtures.py --session s07
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
