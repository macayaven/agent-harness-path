# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve notebook sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot). **v0.3.0 supersedes v0.2.0.** Take it in
**Cursor**: this clone, session bridges, and a complete trivia host.

The default core notebook path is zero network, zero API keys, zero cost: every
"model" in the notebooks is a plain Python function you can read. An **optional
hard path** (`labs/`) grows one toy trivia-host spine against committed
cassettes (`--replay`) or a live OpenAI-compatible endpoint (`--live`).
Completing S01–S12 never requires a lab.

**Take it in Cursor:** open this folder, read [docs/COMPANION.md](docs/COMPANION.md)
(local OpenAI-compatible models = override base URL + key), then start
`lessons/S01-agent-loop.html` with `@bridges/s01.md` in chat.

**Start here (HTML):** [`lessons/index.html`](lessons/index.html). Click ▶ to
watch an optional preview (streams from a public bucket). A 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
covers the arc first (the videos lag the lessons; they are Google Gemini Notebook
overviews; the lesson + notebook are canonical).

S01–S12 are the self-contained path. S13 and S14 are optional unaided protocols.
Easy path: a system you own. Hard path: `labs/trivia_host/`. The notebooks do
not accumulate a capstone; the optional spine does.

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

The native route works on macOS or Linux with Git, Python 3.11+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/). It reads no API
credentials. Clone onto local storage, outside iCloud Drive and Google Drive:

```bash
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

Copy edited notebooks, progress notes and experiment output outside the Git
checkout so they survive a clean clone, branch switch or course upgrade.

`--live` is never the default and never runs in CI. Tutor credentials are
Cursor's; lab `--live` uses separate shell `OPENAI_*`. See
[docs/COMPANION.md](docs/COMPANION.md) and `labs/README.md`.

The clone is small: preview mp4s stream from the web when you click ▶, so you do
not need Git LFS. The notebooks are Python standard library only — the venv
supplies just the tooling (`jupyterlab` to run them, `markdown` to render the
lessons). Open `lessons/index.html` locally (diagrams work from `file://`).

## Repository layout

There is **one** lesson book. `lessons/*.html` is what you read;
`lessons/src/*.md` is what authors edit (`uv run python lessons/build.py`).
See [lessons/README.md](lessons/README.md).

| Path | Role |
| --- | --- |
| `lessons/SNN-*.html` | Learner lesson (plus `videos/`) |
| `lessons/src/SNN-*.md` | Authoring source — not a second course |
| `notebooks/sNN_*.ipynb` | Stdlib toy (S01–S12) |
| `labs/sNN_*.md` | Optional hard-path protocol, not lesson text |
| `bridges/sNN.md` | Cursor companion rung |
| `.cursor/rules/ahp-companion.mdc` | Learner tutor rule |
| `docs/COMPANION.md` | Local OpenAI-compatible tutor wiring |
| `study/` | Optional study, pilot and transfer protocols |
| `AGENTS.md` / `COURSE-MAP.md` / `CONTRIBUTING.md` | Contributor map |

## The toy-domain rule

Everything here is a **toy from a real domain** (a weather bot, a mopbot, a trivia
host) — never a paste-ready production harness. Toy code is for reading, running,
and breaking. The numbers you print in a notebook do not substitute for a banked
eval baseline on a system you own. The optional labs accumulate **one** trivia-host
spine — still a toy domain. If that spine grows file/shell tools, rewrite it back.

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

The [documentation map](docs/README.md) separates learner, contributor, pilot and
release material. The [release runbook](docs/RELEASING.md) records publication
gates. The v0.2.0 [GitHub release](https://github.com/macayaven/agent-harness-path/releases/tag/v0.2.0)
and [pilot receipt](docs/verification/student-pilot-2026-09-13.md) remain
historical evidence about named artifacts.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, labs Python (`labs/**/*.py`), build tooling, CI (`LICENSES/Apache-2.0.txt`)
- **CC BY 4.0** — lessons, videos, documentation, lab protocols (`labs/**/*.md`), and `bridges/` (`LICENSES/CC-BY-4.0.txt`)

Vendored Mermaid.js remains MIT; see `NOTICE`. Video Overviews were generated with
Google Gemini Notebook; Google's marks in those files are not part of the CC BY
grant. Cited papers and vendor docs remain their authors'. Projects you build
while following the path are yours. See `LICENSE` for the file-by-file split.
