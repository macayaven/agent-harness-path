# Cassettes

Committed JSONL traces from a real OpenAI-compatible endpoint. CI and keyless
students `--replay` these.

Layout (one file per run — no combined tape, so `--session s02` cannot consume
S01 entries):

- `s01-round.jsonl`
- `p01-naive.jsonl` … `p09-engine.jsonl`

Each line: `{"model": "...", "request": {match key}, "response": {slim chat completion}}`.
Match key is `{messages, tools?, temperature, tool_choice?}` — not `model`.
A prompt, schema or tool-result wire change requires re-recording affected
cassettes and replaying the full suite with exact matching and exhaustion. Do not
rewrite requests or responses to manufacture a pass. Keep a private snapshot before
recording: a partial run is not a replacement for the complete set.

Re-record like a SOTA refresh, after the protocol or wire contract changes:

```bash
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=...
uv run python labs/run.py --all --record --impl reference
```

`--record` truncates each target file at the start of that run. Student recordings
belong in `labs/work/` (gitignored), not here.

The confidentiality fixture uses opaque synthetic `internal_supplier_ref` values
from `cafe/domain.py`. They are tool-only before and after settlement; allergens
remain public. The checker detects known normalized reference strings, not every
possible paraphrase or encoding. Non-disclosure alone does not prove task completion.

For an existing 1Password environment mount, inject it only for the recording process:

```bash
op run --env-file="./.env" -- uv run python labs/run.py --all --record --impl reference
```

No preliminary `git rm` is needed: record mode clears each target before writing.
After completion, verify all 19 files are nonempty and run `--all --replay --impl reference`.
