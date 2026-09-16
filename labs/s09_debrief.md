# S09 lab — debrief, then one real round

**Optional. After the notebook.**

**Read:** [S09-evidence-reports](../lessons/S09-evidence-reports.html) — a
depleted reader, turn references, the 30-second test.

## Build

`build_debrief(messages, state)` → markdown: score, `stop_reason`, **≥2**
`turn N:` citations. p06's checker looks for that pattern.

Then play **one real round** with the live host (or a local model). Content
stays in `labs/work/` — never commit a real-round transcript. Time your
debrief review; open the raw transcript only afterward to see if the debrief
lied.

## Verify (predict first)

```bash
uv run python labs/run.py --session s09 --replay
```

p06 must pass on the engine column. The real round is a sitting, not a CI job.

## Record

PROGRESS: debrief reviewed in under 5 minutes; honest against the transcript.
No excerpts of the real round in git or in assistant chats.

## Done when

p06 passes and the real-round debrief was judged honest in <5 min.
