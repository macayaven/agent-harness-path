# S09 bridge — debrief then one real round (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/report.py` (`write_report`, the
citation validators). Optional trivia lab: `sessions/s09-evidence-reports/lab.md`,
`build_debrief` in `labs/trivia_host/engine.py`, p06 checker.

## The gap

The core toy builds a depleted-reader café debrief with turn citations. The
optional trivia host’s `build_debrief(messages, state)` already emits markdown:
score, clues, `stop_reason`, and up to four `turn N:` lines (player text or host
tool names). p06 requires ≥2 such citations. Shipped engine p06 PASSes.

The **session work** that is not in CI: play **one real round** with a live
host or local model. Transcript stays in `labs/work/` — never git, never
paste into assistant chats. Time the debrief review (<5 min); only then open
the raw transcript to see if the debrief lied.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s09-evidence-reports/toy.py
# optional hard path: the separate trivia lab
uv run python labs/run.py --session s09 --replay   # p06
# real round: --live with your local/cloud lab credentials (not Cursor's
# tutor settings unless you intentionally share the same server)
```

## Predict-first

Can you tell from the debrief alone whether `end_round` ran, without the
raw JSON? After the sitting, compare.

## Assistant: do / don't

Do: explain why turn citations beat “great job.” Don't: ask for the real
round transcript. Don't: write a prettier debrief that invents turns. Don't:
commit `labs/work/`.
