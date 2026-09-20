# S03 bridge — pinned context (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/context.py` (`policy_summarize`,
`summarize_turns`, the compaction policies). Optional café-host lab:
`sessions/s03-context-engineering/lab.md`, `labs/cafe_host/engine.py` (`compact`, `run_engine`
message prefix), `labs/house_rules.py`.

Wire table: `sessions/s01-agent-loop/companion.md`. Eval suite: `sessions/s02-golden-evals/companion.md`.

## The gap

The core toy measures retained instructions separately from observed behavior;
`cafe/context.py` is the four-policy answer. The optional café host already
pins **two** leading system messages:

1. `PINNED_RULES` — never drop (index 0).
2. `STARTER_PERSONA` — may sit under the pin.

`compact(messages, keep=…)` in `engine.py`: if `keep < 2` or the list is
short, return as-is. Else keep `messages[0]`, insert a system note that N
messages were compacted, keep the tail of length `keep-1`. Governors
(ceiling, PII) are **code** in `tools.py` / `engine.py`, not only the pin.
The pin is a copy the model sees; enforcement is `pull_item` returning
`scope_ceiling` and `policy_hit`.

## Replay hazard

Replacing `STARTER_PERSONA` changes message[1] and **mismatches** course
cassettes (S08 match key includes full `messages`). Offline path: keep the
starter persona, pass the pin test. Custom persona: `--live` or `--record`
into `labs/work/`.

## Commands

```bash
# core path: offline by default; COURSE_MODE=live opts into your configured endpoint
uv run marimo edit sessions/s03-context-engineering/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s03 --replay
```

Expect `PASS s03: pin survived compact`. Re-read the S02 suite; every flip
vs S02 needs a one-line cause (on the shipped host, flips should be rare).

## Predict-first

After `keep=6` on a long list, is `messages[0]` still `PINNED_RULES`?

## Assistant: do / don't

Do: walk `compact` line by line next to the notebook compaction experiment.
Don't: rewrite `PINNED_RULES` to be “safer.” Don't drop the pin to save
tokens. Don't claim the pin alone stops banquet-scope pulls (that's `pull_item`).
