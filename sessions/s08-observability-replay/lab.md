# S08 lab — traces and cassette replay

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S08-observability-replay](lesson.html).

The lab client **is** the cassette layer the notebook taught: next unused
entry, full match key, exhaustion as a separate invariant. Do not weaken it.

## Build

1. Write per-phase spans (intake / spec / serve / debrief) as JSONL under
   `labs/work/traces/` (gitignored). No timestamps in the **transcript**
   messages — clocks make "identical" a flake. Langfuse is optional and
   **not** required.
2. Confirm `--replay` on a recorded shift reproduces the assistant/tool
   sequence. `Client.assert_exhausted()` must run at the end of each cassette
   file.

## Verify (predict first)

Predict: a prompt change mismatches; a deleted final call passes matching and
fails exhaustion.

```bash
uv run python labs/run.py --session s08 --replay
uv run python labs/run.py --session s01 --replay   # same s01-round file twice
```

## Record

PROGRESS: one trace file (local) + "replay matched and exhausted".

## Done when

One full trace exists locally and one offline replay consumed its cassette
exactly.
