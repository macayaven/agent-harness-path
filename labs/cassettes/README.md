# Cassettes

Committed JSONL traces from a real OpenAI-compatible endpoint. CI and keyless
students `--replay` these.

The `v0.6.0-rc.1` set was recorded on 20 September 2026 using NVIDIA Nemotron 3.5
Lightning 30B A3B (NVFP4), served locally on the maintainer's NVIDIA DGX Spark:
19 files with 43 model responses. See the
[model and hardware acknowledgment](../../README.md#validation-model-and-offline-replay).
Core notebooks use a separate deterministic Python stub by default; these
cassettes provide offline replay for the hard-path labs.

On 22 September the 10 governed recordings (`s01-round` and `p01`–`p09-engine`)
were re-recorded after clarifying scope and billing rules. The nine naïve
recordings remain byte-identical to the original set. The current set contains
**19 files and 36 responses**. Each governed run completes, including p08's
legitimate espresso request; an exhausted turn budget no longer passes its
checker. See the [review and recording provenance](../../docs/cassette-review-2026-09-22.md).

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
Inspect the assistant's explanation and actual tool effects as well as the score:
the scope checker alone cannot distinguish a truthful refusal from an invented
capacity limit. Deliberately failing naïve examples should remain failures.
