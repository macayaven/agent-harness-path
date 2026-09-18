# S08 bridge — cassettes and traces (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/trace.py` (spans, the JSONL
shift record, exact replay). Optional trivia lab: `sessions/s08-observability-replay/lab.md`,
`labs/client.py` (`match_key`, `ReplayMismatch`, `assert_exhausted` /
leftover entries), `labs/cassettes/*.jsonl`.

## The gap

The core toy records a real café shift and replays it exactly; `cafe/trace.py`
is that layer. The optional trivia lab client teaches next-entry match and
exhaustion. Match key: `{messages, tools, temperature, tool_choice}` — **not**
`model` (so you can replay without the recording model). Order matters.
Leftover cassette lines fail at end of file. A prompt change mismatches. A
deleted final call can pass matching and fail exhaustion.

`model` is stored on cassettes but not matched.

Do not log API keys (`_redact` in `client.py`). No timestamps inside
**transcript** messages (clocks flake “identical”).

## What to build this session (still)

Per-phase spans (intake / spec / play / debrief) as JSONL under
`labs/work/traces/` (gitignored). Langfuse is optional and **not** required.
Confirm `--replay` on a recorded round reproduces assistant/tool sequence.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s08-observability-replay/toy.py
# optional hard path: the separate trivia lab
uv run python labs/run.py --session s08 --replay
uv run python labs/run.py --session s01 --replay   # same s01-round file twice
```

## Predict-first

Prompt change → mismatch. Deleted last cassette call → match then exhaustion
fail.

## Assistant: do / don't

Do: walk `match_key` vs a cassette line. Don't: weaken the match to
“messages only.” Don't: put timestamps in messages to “help debug.” Don't:
commit `labs/work/`.
