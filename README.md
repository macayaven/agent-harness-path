# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve notebook sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot). Zero network, zero API keys, zero cost: every
"model" in the notebooks is a plain Python function you can read, so the mechanics
are never hidden behind an API call.

**Start here:** clone the repo and open
[`lessons/index.html`](lessons/index.html). Click ▶ to watch a preview (streams
from a public bucket). A 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
covers the arc first (the videos lag the lessons; they are Google Gemini Notebook
overviews, formerly NotebookLM; the lesson + notebook are canonical). Then run
the notebooks.

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
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync            # creates .venv/ (Python 3.11+, pinned by uv.lock)
uv run jupyter lab # run the notebooks; or open notebooks/ in any Jupyter frontend
```

The clone is small: preview mp4s stream from the web when you click ▶, so you do
not need Git LFS. The notebooks are Python standard library only — the venv
supplies just the tooling (`jupyterlab` to run them, `markdown` to render the
lessons). Open `lessons/index.html` locally (diagrams work from `file://`).

## Repository layout

- `lessons/index.html` — the course entry point (generated from `lessons/src/`;
  rebuild with `uv run python lessons/build.py`)
- `lessons/S01…S14-*.html` — the lessons; `lessons/videos/` — one Video Overview per
  session, generated with Google Gemini Notebook (formerly NotebookLM) on 14 Aug 2026
  (maintainer archive via Git LFS; generated HTML streams the public copy).
  Previews/reviews, not substitutes for the work. Google branding in the files is
  Google's; see `NOTICE`.
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

## Contributing

Reports and patches that make the path more accurate, easier to start, or
honest about its limits are welcome. The bar is the same as the lessons:
evidence over claims, no paste-ready harness, no secrets in the tree.

1. Open an [issue](https://github.com/macayaven/agent-harness-path/issues) for a
   broken link, a SOTA source that moved, or a lesson/notebook contradiction.
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) before a pull request (how to edit
   sources, the verify commands, what maintainers will reject).
3. By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
4. Real secrets or unsafe committed code: [SECURITY.md](SECURITY.md), not a
   public issue.

Good first contributions are a dead URL, a SOTA row whose Take overstates the
linked abstract, or a predict-first prompt that leaks the answer.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, build tooling, CI (`LICENSES/Apache-2.0.txt`)
- **CC BY 4.0** — lessons, videos, and documentation (`LICENSES/CC-BY-4.0.txt`)

Vendored Mermaid.js remains MIT; see `NOTICE`. Video Overviews were generated with
Google Gemini Notebook; Google's marks in those files are not part of the CC BY
grant. Cited papers and vendor docs remain their authors'. Projects you build
while following the path are yours. See `LICENSE` for the file-by-file split.
