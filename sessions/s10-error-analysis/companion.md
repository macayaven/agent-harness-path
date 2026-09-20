# S10 bridge — error taxonomy and grown suite (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/taxonomy.py` (failure bucketing →
ranked taxonomy → new eval task). Optional café-host lab: `sessions/s10-error-analysis/lab.md`,
`labs/evals/tasks.py` p07–p09, `labs/run.py` `S10_IDS` (denominator **9**).

The core keeps the S05 consent gate while collecting evidence. A scripted
customer is an explicit fixture; a refused fire is not a served ticket.
Core taxonomy and promotion wait for complete learner labels. An empty pile
produces no calibration evidence, and reference labels never fill missing work.

## The gap

The core toy open-codes a handful of real café failures into buckets. The
optional café-host lab asks you to read **fixture** transcripts from S02–S09 suite
runs (not the S09 real shift), group them, and write
`labs/work/failure-taxonomy.md` (gitignored) with ≥1 trace reference per row.

Expected buckets (correct from data, do not force): spec-miss, supplier-ref-leak,
PII-overtrigger, ceiling-miss, section-drift, comp-without-settle, missing
`close_shift`.

Course ships p07–p09 as the grown suite (section, billing integrity,
`close_shift`). Do not delete them. If your taxonomy’s top-3 differ, extra
checkers belong in `labs/work/`, not by silently dropping CI tasks.

On the shipped host, engine should still be strong on 9; naïve remains the
contrast. Record naïve ?/9 vs engine ?/9.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s10-error-analysis/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s10 --replay
```

## Predict-first

Which of p07–p09 can naïve pass, and why?

## Assistant: do / don't

Do: help name buckets from reasons already in the report table. Don't:
rewrite checkers to inflate the engine score. Don't: use the S09 live
transcript as a fixture.
