# S09 lab — debrief, then one real shift

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S09-evidence-reports](lesson.html) — a
depleted reader, turn references, the 30-second test.

## Build

`build_debrief(messages, state)` → markdown: total, `stop_reason`, **≥2**
`turn N:` citations. p06's checker looks for that pattern.

Then serve **one real shift** with the live host (or a local model). Content
stays in `labs/work/` — never commit a real-shift transcript. Time your
debrief review; open the raw transcript only afterward to see if the debrief
lied.

## Verify (predict first)

```bash
uv run python labs/run.py --session s09 --replay
```

p06 must pass on the engine column. The real shift is a sitting, not a CI job.

## Record

PROGRESS: debrief reviewed in under 5 minutes; honest against the transcript.
No excerpts of the real shift in git or in assistant chats.

## Done when

p06 passes and the real-shift debrief was judged honest in <5 min.
