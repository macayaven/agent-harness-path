# S12 bridge — critic calibration (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/judge.py` (the seeded-defect
game, detection/false-positive rates, agreement math; Cohen’s κ is `None` when
undefined). Optional café-host lab: `sessions/s12-judge-calibration/lab.md`.

## The gap

The core toy labels before the judge and reports detection vs false positives
as a pair; `cafe/judge.py` is the calibration. CI `--replay` on the optional
café-host lab **does not grade the critic**. An unmeasured critic is decoration.

Build (local, not in git): a second-model or second-prompt critic that reads
spec + transcript, returns structured findings with turn references, and
**never** speaks to the customer.

Seed 5 defective fixtures (allergen leak in prose; ignored ceiling; PII in an item;
never called `close_shift`; hollow debrief with zero turn refs) and 5 clean
ones. Label **before** running the critic. Then: detection n/5, FP n/5,
agreement, κ (or `None`). Those four rates go in `labs/PROGRESS.md`. Any
later “judged-tier” number must carry them or stay labeled uncalibrated.

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s12-judge-calibration/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s12 --replay   # suite only
```

The seeded-defect game is a script you run locally.

## Predict-first

If the critic flags all 10 transcripts, what happens to FP and κ?

## Assistant: do / don't

Do: refuse to fill labels after seeing critic output. Don't: run the critic
then “help” relabel. Don't: let the critic talk to the customer. Don't: quote
κ as quality without the four rates.
