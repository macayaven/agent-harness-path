# Cassettes

Committed JSONL traces from a real OpenAI-compatible endpoint. CI and keyless
students `--replay` these.

Layout (one file per run — no combined tape, so `--session s02` cannot consume
S01 entries):

- `s01-round.jsonl`
- `p01-naive.jsonl` … `p09-engine.jsonl`

Each line: `{"model": "...", "request": {match key}, "response": {slim chat completion}}`.
Match key is `{messages, tools?, temperature, tool_choice?}` — not `model`.
A schema or tool-result wire change therefore requires either migrating every
committed `request.tools` value to the current `labs/schemas.py` exactly (when
responses remain valid) or re-recording the affected cassettes. Never update the
runtime schema and leave stale request metadata behind.

Re-record like a SOTA refresh, after the protocol or wire contract changes:

```bash
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=...
uv run python labs/run.py --all --record --impl reference
```

`--record` truncates each target file at the start of that run. Student recordings
belong in `labs/work/` (gitignored), not here.
