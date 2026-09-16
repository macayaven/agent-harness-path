# Take The Agent Harness Path in Cursor

This tree is v0.1.0 lessons and notebooks, plus the optional v0.2.0 hard-path
`labs/`, plus **session bridges** so a Cursor (or other OpenAI-compatible)
assistant can stand in the gap between a tiny toy and the trivia-host lab.

You still clone the course. You do not install CourseWeave or JupyterLab as
the product. Cursor is the window; the companion is chat with a project rule.

## 1. Open the course

```bash
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
git checkout v0.1.1-companion   # this companion cut; or main once published
GIT_LFS_SKIP_SMUDGE=1           # optional: skip preview videos
uv sync --frozen                # notebooks + lesson build tooling
```

Open **this folder** in Cursor. Confirm `.cursor/rules/ahp-companion.mdc` is
present (always-on learner rule).

A session:

1. Open `lessons/SNN-*.html` (preview or browser).
2. Open `notebooks/sNN_*_toy.ipynb` and run cells (Cursor or `uv run jupyter lab`).
3. Predict-first: write your guess **before** asking the assistant to confirm.
4. Optional hard path: open `labs/sNN_*.md` and `@bridges/sNN.md` in chat.

## 2. Wire the assistant (local or cloud)

The companion is whatever model Cursor is using. To use a **local** server,
point Cursor at an OpenAI-compatible base URL. You are not patching course
code. You are changing the editor's model endpoint.

### Cursor (current UI, names drift)

1. Cursor Settings → **Models**.
2. Enable or add a model that talks **OpenAI Chat Completions** (`/v1/chat/completions`).
3. Set **OpenAI API Base URL** (or “Override OpenAI Base URL”) to your local
   server, including `/v1`.
4. Set **OpenAI API Key** to any non-empty string if the server requires a
   header (`ollama` is fine). For a cloud-compatible local proxy, use that
   proxy’s key.
5. Select that model in the chat picker.

Examples:

| Server | Base URL | Key |
| --- | --- | --- |
| [Ollama](https://github.com/ollama/ollama) | `http://127.0.0.1:11434/v1` | `ollama` |
| [LM Studio](https://lmstudio.ai/) local server | `http://127.0.0.1:1234/v1` | `lm-studio` |
| vLLM / llama.cpp OpenAI shim | `http://127.0.0.1:PORT/v1` | any non-empty string |
| OpenAI | leave base URL default | your real key (never commit it) |
| Anthropic | use Cursor’s Anthropic model entries | Anthropic key in Cursor, not in this repo |

Ollama one-shot:

```bash
ollama pull llama3.2
# serve is default on 11434; then set Cursor base URL as above
```

If chat fails with 404, the base URL is usually missing `/v1` or the server
is not OpenAI-compatible. If it fails with 401, the key header is empty.

**Continue.dev (optional).** Only if you already use it in VS Code/Cursor.
Same idea in `~/.continue/config.json`: `provider: openai`,
`apiBase: http://127.0.0.1:11434/v1`, `apiKey: ollama`. Prefer the repo rule
in `.cursor/rules/` over a second personality in Continue.

## 3. Two different OpenAI env vars

Do not mix these up.

| What | Where | Purpose |
| --- | --- | --- |
| **Tutor** | Cursor model settings (base URL + key) | Explains lessons/labs |
| **Lab `--live`** | shell `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` | Optional trivia-host against a real/local chat API |

Hard path default is **`--replay`** (no keys). `--live` is never required to
finish S01–S12 easy path, and never runs in CI.

```bash
# optional lab live, local model — separate from Cursor chat
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=llama3.2
uv run python labs/run.py --session s01 --live
```

Never put keys in `bridges/`, notebooks, `labs/trivia_host/`, or issues.

## 4. What the assistant is allowed to do

See `.cursor/rules/ahp-companion.mdc` and `bridges/sNN.md`. Short version:
same face everywhere; fill context, not the homework; no `labs/reference/`
unless you say you are stuck; S13/S14 stay unaided.

## 5. Native route still works

`uv run jupyter lab` and opening `lessons/index.html` remain the zero-assistant
path. This companion cut does not remove them.
