# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
fourteen sessions, each pairing a deep HTML lesson with a runnable toy notebook and a
short video overview. Zero network, zero API keys, zero cost: every "model" in the
notebooks is a plain Python function you can read, so the mechanics are never hidden
behind an API call.

**Start here:** [`lessons/index.html`](lessons/index.html) — or watch the 9-minute
[course overview](lessons/videos/S00-course-overview.mp4) first.

## Who it's for

Engineers who already call an LLM API and want the discipline around it: eval suites
that produce defensible numbers, context that survives compaction, consent gates,
safety layers, traces you can replay, judges you've calibrated, budgets that hold.
Not an intro to prompting — the course's premise is that the model call is the easy
part and the harness is the product.

## What a session looks like

1. **Read the lesson** (20–40 min) — theory in depth, a diagram, and a dated
   state-of-the-art table (what the industry currently does about it, with sources).
2. **Run the notebook** (30–60 min) — a small complete system from a real domain
   (a hotel concierge, a repair shop, a trivia host), with **predict-first**
   experiments and attempt-before-solution exercises.
3. **Self-check** — foldable quiz questions at the end of the lesson.
4. Sessions 13–14 invert the pattern: a closed-book rebuild audit and a ship/pilot
   protocol. No notebooks — scaffolding those would defeat them.

The curriculum: agent loop → golden sets & baselines → context engineering →
structured generation → consent gate → layered detection → repair loop →
observability & replay → evidence reports → error analysis → budgets & routing →
judge calibration → rebuild from memory → ship & pilot.

## Quickstart

```bash
uv sync            # creates .venv/ (Python 3.11+, pinned by uv.lock)
uv run jupyter lab # run the notebooks; or open notebooks/ in any Jupyter frontend
```

The notebooks are Python standard library only — the venv supplies just the tooling
(`jupyterlab` to run them, `markdown` to render the lessons). Clone with Git LFS
installed if you want the videos (`lessons/videos/`, mp4).

## Repository layout

- `lessons/index.html` — the course entry point (generated from `lessons/src/`;
  rebuild with `uv run python lessons/build.py`)
- `lessons/S01…S14-*.html` — the lessons; `lessons/videos/` — one video overview per
  session (NotebookLM-generated; previews/reviews, not substitutes for the notebooks)
- `notebooks/` — twelve runnable toys (S1–S12), committed output-free
- `AGENTS.md` — contributor/agent conventions: the lesson format, the notebook
  contract, the one rule
- `COURSE-MAP.md` — coverage map for both layers of the repo

## The companion layer

This repo began as the study companion to a separate, deliberately austere course
(`agentic-harnessing-intensive`, private). That layer survives in `sessions/`
(six-part guides feeding the course's real builds) and `WHY-THIS-DESIGN.md` (the
evidence for which difficulty is deliberate). The Agent Harness Path above is the
standalone version of the same topics and is what you are meant to share or teach
from; the companion layer assumes the course repo and references it freely.

The one rule that keeps both layers honest: everything here is a **toy from a
different domain** — nothing is paste-able into the course's deliverable paths, and
no number here substitutes for a real, banked eval baseline.

## License

Copyright © 2026 the repository owner. All rights reserved. You may view and clone
this repository for personal learning. Any other use — redistribution, teaching
materials derived from it, commercial use — requires the owner's permission. (If you
are the owner and intend to open it up, replace this section with the license of
your choice; see `LICENSE`.)
