# Labs — optional hard path

Two signed routes. Completing S01–S12 **never** requires a lab.

| Route | What you do | Keys |
|---|---|---|
| **Easy (default)** | Lesson → notebook → self-check | none |
| **Hard (optional)** | Same, **then** this directory | optional: `--replay` needs none |

`--replay` is a first-class hard-path mode, not a consolation. You build the
trivia host against committed traces from a real model. `--live` is how you
feel stochasticity, latency, and schema miss on *your* endpoint.

```bash
uv sync   # already done for the notebooks
# no key:
uv run python labs/run.py --session s02 --replay
# any OpenAI-compatible server:
export OPENAI_BASE_URL=https://api.openai.com/v1   # or http://127.0.0.1:11434/v1
export OPENAI_API_KEY=...                          # Ollama: any non-empty string
export OPENAI_MODEL=...
uv run python labs/run.py --session s02 --live
```

Default mode is **replay**. `--live` is never the default and is never used in CI.

## What you are building

One toy-domain spine: a **trivia host**. Tools stay in-domain
(`propose_round_spec`, `draw_clue`, `score_answer`, `end_round`). If this
drifts toward a paste-ready generic harness (files, shell, a workspace), that
is a defect — rewrite it back into pub quiz.

You type the meat in `trivia_host/`. `reference/` is the **spotter**: open only
if stuck. Peeking makes S13 a recognition test.

Two bars, do not conflate:

1. **Your session done-when** (each `sNN_*.md`): bank a number you can explain.
   Early sessions may fail later tasks. That is the point of a baseline.
2. **CI** runs `--impl reference --all --replay` so the course stays green
   without keys. CI never grades your tree.

## Wire contract (so `--replay` matches)

Course cassettes were recorded from the reference host. Replay matching is the
S08 contract: the **next** cassette entry must equal the canonical request
(`messages`, `tools`, `temperature`, `tool_choice`), in order; leftover entries
fail at the end of that file. `model` is stored but not matched, so you can
replay without the recording model.

Tool results are part of that public wire contract too. For every non-string
result, append the tool message with `content=client.canonicalize(result)`:
sorted object keys, compact separators, and `ensure_ascii=False` so UTF-8 /
non-ASCII text is preserved. Do not use a second `json.dumps` recipe.

The reference tool return envelopes are exact replay-facing shapes:

| Tool | Success envelope | Error envelope(s) |
|---|---|---|
| `propose_round_spec` | `{"ok": true, "spec": SPEC}` | `{"error": MESSAGE}` or `{"error": "difficulty_ceiling", "approved": LEVEL}` |
| `draw_clue` | `{"clue_id": ID, "category": CATEGORY, "difficulty": LEVEL, "prompt": TEXT}` | `{"error": "difficulty_ceiling", "approved": LEVEL}`, `{"error": "category_not_allowed", "allowed": CATEGORIES}`, or `{"error": "no_clue", "category": CATEGORY, "difficulty": LEVEL}` |
| `score_answer` | `{"correct": BOOL, "points": INT, "clue_id": ID}` | `{"error": "unknown_clue", "clue_id": ID}` |
| `end_round` | `{"score": INT, "clues_played": INT, "stop_reason": REASON}` | none |
| unknown dispatch name | none | `{"error": "unknown_tool", "name": NAME}` |

These are course-cassette wire contracts, not hidden spotter internals. Key
names, nesting, and tool-result serialization must match `reference/tools.py`.

Keep these unchanged if you want course-cassette replay:

- `labs/schemas.py` — tool JSON
- `labs/house_rules.py` — `PINNED_RULES` (message 0) and `STARTER_PERSONA`
  (message 1)

S03: writing your own persona is the lesson. That **will** mismatch course
cassettes. Offline path: keep `STARTER_PERSONA`, rerun the suite, and pass the
`compact()` pin test (`--session s03 --replay`). Custom persona: `--live` or
`--record` into gitignored `labs/work/`.

Copy `PROGRESS.template.md` to `labs/PROGRESS.md` (gitignored).

## Layout

- `s01_loop.md` … `s12_judge.md` — protocols (Build / Verify / Record / Done-when)
- `trivia_host/` — your implementation
- `client.py` — stdlib OpenAI-compatible POST + cassettes
- `run.py` — naïve vs engine, markdown report
- `cassettes/` — committed traces, one file per `(task, naïve|engine)` plus `s01-round.jsonl`
- `evals/` — golden tasks p01–p06 (S02), p07–p09 (S10)
- `reference/` — spotter

S13/S14: if you walked this path, the audit/ship target is `trivia_host/`
against this suite. Otherwise bring your own system (the easy-path rule).
