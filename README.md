# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve build sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot).

**You build one agent, against a real model.** Across S01–S12 you grow a single
café-counter agent in `cafe/`: loop → evals → context → schema → consent →
detection → repair → tracing → reports → taxonomy → routing → judge. Every
session starts from the artifact and the number the last one produced.

Every experiment runs against **your** OpenAI-compatible endpoint — a local model
costs nothing. The mocks are gone: a prediction is only worth writing down when
the thing you are predicting can surprise you.

```bash
export CAFE_BASE_URL=http://127.0.0.1:11434/v1   # Ollama, LM Studio, anything OpenAI-compatible
export CAFE_API_KEY=ollama                       # any non-empty string for a local server
export CAFE_MODEL=qwen2.5:14b-instruct
uv run python -m cafe.doctor                     # one live call; proves your endpoint
uv run marimo edit notebooks/s01_agent_loop_toy.py
```

`CAFE_*` is read before `OPENAI_*`, so the course never collides with production
credentials. No key is ever committed, printed, or logged. Notebooks are
[marimo](https://marimo.io) files — plain Python, reactive, diffable.

**Model size matters.** Most sessions are *better* with a mediocre model: bad
output is exactly what S02, S07 and S10 measure and repair. S04
(structured generation) and S12 (judge calibration) need a mid-size instruct
model with real tool-calling support.

**Take it in Cursor:** open this folder, read [docs/COMPANION.md](docs/COMPANION.md),
then start `lessons/S01-agent-loop.html` with `@bridges/s01.md` in chat.

**Start here (HTML):** [`lessons/index.html`](lessons/index.html). Click ▶ to
watch an optional preview (streams from a public bucket). A 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
covers the arc first (the videos lag the lessons; they are Google Gemini Notebook
overviews; the lesson + notebook are canonical).

S01–S12 are the core path and they **do** accumulate: the capstone is the `cafe/`
package you finish with. S13 and S14 are optional unaided protocols — rebuild
`cafe/loop.py` closed-book, judged by the eval suite you built.

## Core route and post-core overlay

- **Core harness route (start here):** work through S01–S12, then optionally use
  S13/S14 and `labs/`. If you are new to harnesses, complete S01–S12 before using
  the overlay.
- **Calibrated six-week post-core overlay:** use the
  [study-plan overlay](lessons/study-plan.html) to schedule authoritative external
  work from CS336, DeepLearning.AI RLHF, DeepLearning.AI vLLM, and the optional
  Anthropic API course, with explicit evidence to bank. The overlay is not part of
  the 14-session core and contains no copied external-course materials.

## Who it's for

Engineers who already call an LLM API and want the discipline around it: eval suites
that produce defensible numbers, context that survives compaction, consent gates,
safety layers, traces you can replay, judges you've calibrated, budgets that hold.
Not an intro to prompting. The model call is the easy part; the harness is the
product.

## What a session looks like

1. **Read the lesson** (20–40 min) — theory in depth, a diagram, and a dated
   state-of-the-art table (what the industry currently does about it, with sources).
2. **Run the notebook** (30–60 min) — the session's slice of the café-counter
   agent in `cafe/`, against your live endpoint, with **predict-first**
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

The native route works on macOS or Linux with Git, Python 3.11+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/). It reads no API
credentials. Clone onto local storage, outside iCloud Drive and Google Drive:

```bash
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync --frozen   # creates .venv/ (Python 3.11+, pinned by uv.lock)
# Open this folder in Cursor (companion rule in .cursor/rules/).
# Point the course at your OpenAI-compatible endpoint, prove it, open S01:
export CAFE_BASE_URL=http://127.0.0.1:11434/v1   # Ollama, LM Studio, anything OpenAI-compatible
export CAFE_API_KEY=ollama                       # any non-empty string for a local server
export CAFE_MODEL=qwen2.5:14b-instruct
uv run python -m cafe.doctor
uv run marimo edit notebooks/s01_agent_loop_toy.py
```

Optional hard path (complete host already in `labs/trivia_host/`):

```bash
uv run python labs/run.py --session s01 --replay
uv run python labs/run.py --session s02 --replay
```

Copy edited notebooks, progress notes and experiment output outside the Git
checkout so they survive a clean clone, branch switch or course upgrade.

`--live` is never the default and never runs in CI. Tutor credentials are
Cursor's; lab `--live` uses separate shell `OPENAI_*`. See
[docs/COMPANION.md](docs/COMPANION.md) and `labs/README.md`.

The clone is small: preview mp4s stream from the web when you click ▶, so you do
not need Git LFS. Course logic is Python standard library only — the venv
supplies just the tooling (`marimo` to run the notebooks, `markdown` to render
the lessons). Open `lessons/index.html` locally (diagrams work from `file://`).

## Repository layout

There is **one** lesson book. `lessons/*.html` is what you read;
`lessons/src/*.md` is what authors edit (`uv run python lessons/build.py`).
See [lessons/README.md](lessons/README.md).

| Path | Role |
| --- | --- |
| `lessons/SNN-*.html` | Learner lesson (plus `videos/`) |
| `lessons/src/SNN-*.md` | Authoring source — not a second course |
| `notebooks/sNN_*_toy.py` | Marimo toy driving `cafe/` (S01–S12) |
| `labs/sNN_*.md` | Optional hard-path protocol, not lesson text |
| `bridges/sNN.md` | Cursor companion rung |
| `.cursor/rules/ahp-companion.mdc` | Learner tutor rule |
| `docs/COMPANION.md` | Local OpenAI-compatible tutor wiring |
| `study/` | Optional study, pilot and transfer protocols |
| `AGENTS.md` / `CONTRIBUTING.md` | Contributor map |

## The toy-domain rule

Everything in the core path is **one toy from one familiar domain** — a
neighbourhood-café counter assistant (orders, tickets, allergens, the till) —
never a paste-ready production harness. Toy code is for reading, running,
and breaking. The numbers you print in a notebook do not substitute for a banked
eval baseline on a system you own. The optional labs are a **separate** trivia-host
spine — still a toy domain. If either spine grows file/shell tools, rewrite it back.

## Contributing

Reports and patches that make the path more accurate, easier to start, or
honest about its limits are welcome. The bar is the same as the lessons:
evidence over claims, no paste-ready harness, no secrets in the tree.

1. Use the one-click
   [course feedback form](https://github.com/macayaven/agent-harness-path/issues/new?template=course-feedback.yml)
   for setup or study friction. Submission is deliberate; the course sends no
   telemetry or files to GitHub. Include the public
   session/activity, what you tried, expected and observed, and any recovery.
   Remove credentials, raw chats, participant content, private project details,
   local paths and full notebook/work products.
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) before a pull request (how to edit
   sources, the verify commands, what maintainers will reject).
3. By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
4. Real secrets or unsafe committed code: [SECURITY.md](SECURITY.md), not a
   public issue.

Good first contributions are a dead URL, a SOTA row whose Take overstates the
linked abstract, or a predict-first prompt that leaks the answer.

The [documentation map](docs/README.md) separates learner, contributor, and pilot
material. The v0.2.0 [GitHub release](https://github.com/macayaven/agent-harness-path/releases/tag/v0.2.0)
remains historical evidence about named artifacts.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, labs Python (`labs/**/*.py`), build tooling, CI (`LICENSES/Apache-2.0.txt`)
- **CC BY 4.0** — lessons, videos, documentation, lab protocols (`labs/**/*.md`), and `bridges/` (`LICENSES/CC-BY-4.0.txt`)

Vendored Mermaid.js remains MIT; see `NOTICE`. Video Overviews were generated with
Google Gemini Notebook; Google's marks in those files are not part of the CC BY
grant. Cited papers and vendor docs remain their authors'. Projects you build
while following the path are yours. See `LICENSE` for the file-by-file split.
