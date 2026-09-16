# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve notebook sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot). The default core is zero network, zero API
keys: every "model" in the notebooks is a plain Python function. This
**v0.1.1-companion** cut keeps that v0.1.0 core, adds the optional hard-path
`labs/` (complete trivia host, not stubs), and adds **session bridges** so a
Cursor assistant can explain the jump from toy → lab.

**Take it in Cursor:** open this folder, read [docs/COMPANION.md](docs/COMPANION.md)
(local OpenAI-compatible models = override base URL + key), then start
`lessons/S01-agent-loop.html` with `@bridges/s01.md` in chat.

**Start here (HTML):** [`lessons/index.html`](lessons/index.html) — or the hosted
[lesson reader](https://macayaven.github.io/agent-harness-path/). A 9-minute
[course overview](lessons/videos/S00-course-overview.mp4) covers the arc first
(the videos lag the lessons; they are Google Gemini Notebook overviews; the
lesson + notebook are canonical).

S01–S12 are the self-contained path. S13 and S14 are optional unaided
protocols. The optional hard path in `labs/` grows one trivia-host spine
against committed cassettes (`--replay`) or a live OpenAI-compatible endpoint
(`--live`). Completing S01–S12 never requires a lab.

## Who it's for

Engineers who already call an LLM API and want the discipline around it: eval suites
that produce defensible numbers, context that survives compaction, consent gates,
safety layers, traces you can replay, judges you've calibrated, budgets that hold.
Not an intro to prompting — the premise is that the model call is the easy
part and the harness is the product.

## What a session looks like

1. **Read the lesson** (20–40 min) — theory in depth, a diagram, and a dated
   state-of-the-art table (what the industry currently does about it, with sources).
2. **Run the notebook** (30–60 min) — a small complete system from a real domain
   (a hotel concierge, a repair shop, a trivia host), with **predict-first**
   experiments and attempt-before-solution exercises.
3. **Self-check** — foldable quiz questions at the end of the lesson.
4. **(Optional) hard path** — after the notebook, `labs/sNN_*.md` against
   cassettes (`--replay`) or your OpenAI-compatible endpoint (`--live`).
   `@bridges/sNN.md` is what the Cursor companion should read first.
5. Sessions 13–14 invert the pattern: a closed-book rebuild audit and a
   ship/pilot protocol. Easy path: a system you own. Hard path:
   `labs/trivia_host/`. The assistant must not do these for you.

The curriculum: agent loop → golden sets & baselines → context engineering →
structured generation → consent gate → layered detection → repair loop →
observability & replay → evidence reports → error analysis → budgets & routing →
judge calibration → (optional) rebuild from memory → (optional) ship & pilot.

## Quickstart

```bash
# Code and lessons only (~small). Skip the ~1.2 GB of preview videos:
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/macayaven/agent-harness-path.git

# Or clone with videos (requires Git LFS):
git lfs install
git clone https://github.com/macayaven/agent-harness-path.git

cd agent-harness-path
uv sync --frozen   # creates .venv/ (Python 3.11+, pinned by uv.lock)
# Open this folder in Cursor (companion rule in .cursor/rules/).
# Notebooks: Cursor's notebook UI, or:
uv run jupyter lab
```

Optional hard path (complete host already in `labs/trivia_host/`):

```bash
uv run python labs/run.py --session s01 --replay
uv run python labs/run.py --session s02 --replay
```

The notebooks are Python standard library only — the venv supplies just the tooling
(`jupyterlab` to run them, `markdown` to render the lessons). Open
`lessons/index.html` locally (diagrams work from `file://`); the hosted reader is
the same HTML. Local **tutor** models: [docs/COMPANION.md](docs/COMPANION.md).
Lab `--live` uses shell `OPENAI_*` and is a different credential than Cursor chat.

## Repository layout

- `lessons/index.html` — the course entry point (generated from `lessons/src/`;
  rebuild with `uv run python lessons/build.py`)
- `lessons/S01…S14-*.html` — the lessons; `lessons/videos/` — one video overview per
  session (NotebookLM-generated; previews/reviews, not substitutes for the work)
- `notebooks/` — twelve runnable toys (S1–S12), committed output-free
- `labs/` — optional hard path: complete trivia host, cassettes, `run.py`
- `bridges/` — one authored rung per session for the Cursor companion
- `.cursor/rules/ahp-companion.mdc` — learner tutor rule (do not take the course for them)
- `docs/COMPANION.md` — wire Cursor (or Continue) to a local OpenAI-compatible model
- `AGENTS.md` — contributor conventions; learners follow the companion rule first
- `COURSE-MAP.md` — coverage map
- `CONTRIBUTING.md` — how to propose a change

## The toy-domain rule

Everything here is a **toy from a real domain** (a weather bot, a mopbot, a trivia
host) — never a paste-ready production harness. Toy code is for reading, running,
and breaking. The numbers you print in a notebook do not substitute for a banked
eval baseline on a system you own.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, `labs/**/*.py`, build tooling, CI
- **CC BY 4.0** — lessons, videos, `labs/**/*.md`, `bridges/`, documentation

Vendored Mermaid.js remains MIT; see `NOTICE`. Projects you build while following
the path are yours. See `LICENSE` for the file-by-file split.
