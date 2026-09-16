# S12 lab — critic calibration

**Optional. After the notebook.**

**Read:** [S12-judge-calibration](../lessons/S12-judge-calibration.html) —
label before you see the judge; detection and false positives as a pair;
Cohen's κ.

CI `--all --replay` does **not** grade this. An unmeasured critic is
decoration; measuring it is the lab.

## Build

A second-model (or second-prompt) critic that reads spec + transcript and
returns structured findings with turn references. It must not speak to the
player.

Seed 5 fixture transcripts with one defect each (spoiler in prose; ignored
ceiling; PII in a clue; never called `end_round`; hollow "great job" debrief
with zero turn refs) and keep 5 clean fixtures. Label them **before** running
the critic.

## Verify (predict first)

Detection n/5, false positives n/5, then κ against your labels. Four rates
go in PROGRESS. From here, any judged-tier number you quote in later writeups
carries these rates or stays labeled uncalibrated.

```bash
uv run python labs/run.py --session s12 --replay   # suite only
```

The seeded-defect game is a script you run locally; it is not in CI.

## Record

PROGRESS: detection n/5, FP n/5, agreement, κ (or `None` if undefined, as the
notebook does).

## Done when

All four rates are recorded. The judged tier is no longer "uncalibrated"
unless those rates say it should be demoted.
