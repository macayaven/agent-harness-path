# S10 lab — taxonomy and three new tasks

**Optional. After the notebook.**

**Read:** [S10-error-analysis](../lessons/S10-error-analysis.html).

## Build

1. Read failing **fixture** transcripts from your S02–S09 suite runs (not the
   S09 real round). Open-code causes; group them.
2. Write `labs/work/failure-taxonomy.md` (gitignored) with ≥1 trace reference
   per row. Expected buckets, to be corrected by the data: spec-miss,
   spoiler-leak, PII-overtrigger, ceiling-miss, category-drift,
   score-without-tool, missing `end_round`.
3. The course already ships `p07`–`p09` as the grown suite (category, scoring
   integrity, `end_round`). If your taxonomy names a different top-3, add
   checkers in your workdir — do not silently delete p07–p09; they are the
   regression ledger CI uses.

## Verify (predict first)

```bash
uv run python labs/run.py --session s10 --replay
```

Denominator is now 9. Note it forever.

## Record

PROGRESS: naïve ?/9 vs engine ?/9; taxonomy path (local).

## Done when

Taxonomy exists with trace refs and the 9-task report has a recorded run.
