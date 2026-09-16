# S03 lab — pinned house rules

**Optional. After the notebook.**

**Read:** [S03-context-engineering](../lessons/S03-context-engineering.html) and
the Governance Decay result the lesson cites: in-context constraints die
across compaction unless they are pinned **and** enforced in code.

## Build

1. Keep two leading system messages: `PINNED_RULES` (never compacted), then
   persona.
2. Implement `compact(messages, keep=…)` so index 0 always survives.
3. Optional: replace `STARTER_PERSONA` with one you wrote after attacking two
   drafts. That **breaks course-cassette replay** (S08 matching is the full
   request). Offline path: keep the starter persona, still pass the pin test.
   Custom persona: `--live` or `--record` into `labs/work/`.

Governors that must hold (ceiling, PII) belong in `tools.py` / `engine.py`,
not only in the pin. The pin is a copy, not the enforcement.

## Verify (predict first)

Predict whether the pin is still `messages[0]` after `keep=6` on a long list.

```bash
uv run python labs/run.py --session s03 --replay
```

Rerun the S02 suite. For every task that flipped vs S02, one-line cause.

## Record

PROGRESS: suite number + pin-test line + flip causes.

## Done when

`PASS s03: pin survived compact` and every flip has a one-line cause.
