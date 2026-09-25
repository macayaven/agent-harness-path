# S09 companion — debrief then one real shift (real host)

> Tutor context for this session. Attach it in editor chat (`@sessions/s09-evidence-reports/companion.md`); you do not need to read it to finish the session.

## Files

Core: `lesson.html`,
`toy.py`, `cafe/report.py` (`write_report`, the
citation validators). Optional café-host lab: `sessions/s09-evidence-reports/lab.md`,
`build_debrief` in `labs/cafe_host/engine.py`, p06 checker.

The core keeps the S05 consent gate while collecting evidence. A scripted
customer is an explicit fixture; a refused fire is not a served ticket.
The omission control requires an actual safety event. When the selected run has
none, it announces a separate authored trace instead of silently passing both
validators. The [recorded comparison](recordings/model.jsonl) supplies a real-model
example with a safety event; it does not replace your own shift.

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
# after your prediction and attempt: replay the recorded omission comparison
uv run python tools/record_fixtures.py --session s09
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
