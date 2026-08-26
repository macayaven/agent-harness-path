# S02 lab — golden set and a naïve baseline

**Optional. After the notebook.**

**Read:** [S02-golden-evals](../lessons/S02-golden-evals.html) — the suite is a
measurement instrument; naïve vs harness on the **same** model; the naïve row
is the product argument.

## Build

1. `trivia_host/engine.py` — `run_naive(client, script)`: one system prompt
   (`house_rules.NAIVE_PROMPT`), no tools, same scripted user as the engine.
2. Confirm `run_engine` still uses tools. Do not peek at `reference/` unless
   stuck.
3. Copy `PROGRESS.template.md` → `labs/PROGRESS.md`.

The tasks are `p01`–`p06` in `labs/evals/tasks.py`. Several engine checks
encode governors you have not built yet (ceiling, PII, spec tool). **Failing
them at S02 is a valid baseline** if you can explain the cell. The denominator
is 6. S10 grows it.

## Verify (predict first)

Per task, write `expected_naive_result` (pass/fail) before the run.

```bash
uv run python labs/run.py --session s02 --replay
```

Same model for both columns: replay cassettes were recorded that way; live
must not swap models between naïve and engine.

## Record

PROGRESS: `naïve n/6 vs engine n/6`. The report lands in `labs/reports/last.md`
(gitignored). Do not treat it as the course's `REFERENCE-p0-baseline.md`.

## Done when

The report exists, both columns share a denominator, and you can explain every
cell — including the fails.
