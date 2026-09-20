# S07 lab — bounded regeneration

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S07-repair-loop](lesson.html) — cap retries;
curated failure view; honest `stop_reason`.

## Build

If a host turn hits policy (supplier-reference leak, PII), do not keep it as the product
turn. Append a short repair instruction, regenerate, **≤3** attempts. Never
grow the approved scope on a retry.

Every run ends with
`stop_reason ∈ {completed, retries_exhausted, turn_cap, budget_exceeded, rejected}`.
Print it. Store it. No ambiguous exits.

## Verify (predict first)

```bash
uv run python labs/run.py --session s07 --replay
```

Delta vs S05/S06: which tasks moved, one-line diagnosis each. Remaining
failures also get a line.

## Record

PROGRESS: delta table + stop_reason examples.

## Done when

The delta is recorded and every remaining failure has a one-line diagnosis.
