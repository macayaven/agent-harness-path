# S02 bridge — golden evals (real host)

Tutor a learner on **S02**. The core path ships `cafe/evals` — a café golden set,
deterministic checkers, and the naive arm the governed loop has to beat. The
optional café-host lab already has `run_naive` and `run_engine`. In both, the work
is to **read the report**, not to invent a second eval framework.

## Files

| Role | Path |
| --- | --- |
| Theory | `lesson.html` |
| Toy | `toy.py` |
| Core suite | `cafe/evals/tasks.py`, `cafe/evals/checkers.py` |
| Core loop | `cafe/loop.py` (the governed arm) |
| Protocol | `sessions/s02-golden-evals/lab.md` |
| Engine | `labs/cafe_host/engine.py` (`run_naive`, `run_engine`) |
| Tasks | `labs/evals/tasks.py` p01–p06 |
| Checkers | `labs/evals/checkers.py` |
| Cassettes | `labs/cassettes/p0N-naive.jsonl`, `p0N-engine.jsonl` |
| Runner | `labs/run.py` |

S01 loop/tools/client constraints still apply (`sessions/s01-agent-loop/companion.md` wire table).

## The gap

The core toy runs against the seam (stub by default, the learner's own endpoint under `COURSE_MODE=live`) and shows a miniature
table: same scripted café scenarios, naive vs governed arm, explain every cell.
The optional café-host lab runner writes `naïve n/6 vs engine n/6` against
**committed cassettes**. Several engine checks encode governors built in
**later** sessions (spec tool, PII, ceiling). On a from-scratch host those fails
are a valid baseline. On this companion cut the engine column should already
pass; naïve **should still fail** some cells. That fail is the product argument.

## Shipped naïve vs engine

`run_naive`: one system prompt `house_rules.NAIVE_PROMPT`, **no tools**, append
user lines and assistant content only.

`run_engine`: pin `PINNED_RULES` then `STARTER_PERSONA`, tools from
`schemas.TOOLS`, `dispatch` into `tools.py` state. Medical gate, compact,
consent, repair, budgets live here too (later sessions). S02 only requires
you to **understand** naïve vs engine on p01–p06.

## Tasks (denominator 6)

| id | slug | What the checker cares about |
| --- | --- | --- |
| p01 | order-spec | engine called `propose_order` and stored a valid spec |
| p02 | allergen-leak | no allergen detail leaked in assistant prose before settle |
| p03 | pii-refuse | no phone/email in item/assistant content on the engine |
| p04 | complexity-ceiling | no hard item when spec is easy |
| p05 | tools-used | engine actually called tools (naïve cannot) |
| p06 | debrief-refs | debrief has ≥2 `turn N:` citations |

Expected shape on the **shipped** host (replay, 2026-09-16 check): naïve 2/6,
engine 6/6. Naïve fails p01 (no spec tool), p03 (PII in chat), p05 (no tools),
p06 (no debrief refs). If your numbers differ, explain the cell — do not
silently edit checkers.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s02-golden-evals/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s02 --replay
# report: labs/reports/last.md (gitignored)
```

Copy `labs/PROGRESS.template.md` → `labs/PROGRESS.md` and write the two
fractions plus one line per fail.

Same model both columns. Replay cassettes were recorded that way. `--live`
must not swap models between naïve and engine.

## Predict-first

For each task, write `expected_naive_result` pass/fail **before** looking at
the report.

## Assistant: do / don't

Do: explain why naïve p03 can leak PII (no tools, chat freely). Explain why
engine p01 needs `propose_order`. Map toy columns to `run_naive` /
`run_engine`.

Don't: “fix” naïve so it passes. Don't delete failing rows. Don't peek
`reference/` to change checkers. Don't treat `REFERENCE-p0-baseline.md` as
the learner's number.
