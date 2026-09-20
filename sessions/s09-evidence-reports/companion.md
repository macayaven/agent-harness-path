# S09 bridge — debrief then one real shift (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/report.py` (`write_report`, the
citation validators). Optional café-host lab: `sessions/s09-evidence-reports/lab.md`,
`build_debrief` in `labs/cafe_host/engine.py`, p06 checker.

The core keeps the S05 consent gate while collecting evidence. A scripted
customer is an explicit fixture; a refused fire is not a served ticket.

## The gap

The core toy builds a depleted-reader café debrief with turn citations. The
optional café host’s `build_debrief(messages, state)` already emits markdown:
total, items served, `stop_reason`, and up to four `turn N:` lines (customer
text or assistant tool names). p06 requires ≥2 such citations. Shipped engine
p06 PASSes.

The **session work** that is not in CI: serve **one real shift** with a live
host or local model. Transcript stays in `labs/work/` — never git, never
paste into assistant chats. Time the debrief review (<5 min); only then open
the raw transcript to see if the debrief lied.

## Commands

```bash
# core path: offline by default; COURSE_MODE=live opts into your configured endpoint
uv run marimo edit sessions/s09-evidence-reports/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s09 --replay   # p06
# real shift: --live with your local/cloud lab credentials (not Cursor's
# tutor settings unless you intentionally share the same server)
```

## Predict-first

Can you tell from the debrief alone whether `close_shift` ran, without the
raw JSON? After the sitting, compare.

## Assistant: do / don't

Do: explain why turn citations beat “great job.” Don't: ask for the real
shift transcript. Don't: write a prettier debrief that invents turns. Don't:
commit `labs/work/`.
