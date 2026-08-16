# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve notebook sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot). Zero network, zero API keys, zero cost: every
"model" in the notebooks is a plain Python function you can read, so the mechanics
are never hidden behind an API call.

**Start here:** [`lessons/index.html`](lessons/index.html) — or the hosted
[lesson reader](https://macayaven.github.io/agent-harness-path/). A 9-minute
[course overview](lessons/videos/S00-course-overview.mp4) covers the arc first
(the videos lag the lessons; the lesson + notebook are canonical).

S01–S12 are the self-contained path. S13 and S14 are optional labs you run against
a system you already own — this course does not accumulate a capstone artifact
across sessions.

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
4. Sessions 13–14 invert the pattern: a closed-book rebuild audit and a ship/pilot
   protocol, applied to *your* project. No notebooks — scaffolding those would
   defeat them.

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
uv sync            # creates .venv/ (Python 3.11+, pinned by uv.lock)
uv run jupyter lab # run the notebooks; or open notebooks/ in any Jupyter frontend
```

The notebooks are Python standard library only — the venv supplies just the tooling
(`jupyterlab` to run them, `markdown` to render the lessons). Open
`lessons/index.html` locally (diagrams work from `file://`); the hosted reader is
the same HTML.

## Repository layout

- `lessons/index.html` — the course entry point (generated from `lessons/src/`;
  rebuild with `uv run python lessons/build.py`)
- `lessons/S01…S14-*.html` — the lessons; `lessons/videos/` — one video overview per
  session (NotebookLM-generated; previews/reviews, not substitutes for the work)
- `notebooks/` — twelve runnable toys (S1–S12), committed output-free
- `AGENTS.md` — contributor/agent conventions: the lesson format, the notebook
  contract, the toy-domain rule
- `COURSE-MAP.md` — coverage map
- `CONTRIBUTING.md` — how to propose a change

## The toy-domain rule

Everything here is a **toy from a real domain** (a weather bot, a mopbot, a trivia
host) — never a paste-ready production harness. Toy code is for reading, running,
and breaking. The numbers you print in a notebook do not substitute for a banked
eval baseline on a system you own.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, build tooling, CI (`LICENSES/Apache-2.0.txt`)
- **CC BY 4.0** — lessons, videos, and documentation (`LICENSES/CC-BY-4.0.txt`)

Vendored Mermaid.js remains MIT; see `NOTICE`. Projects you build while following
the path are yours. See `LICENSE` for the file-by-file split.
