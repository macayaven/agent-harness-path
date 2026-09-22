# The Agent Harness Path

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/macayaven/agent-harness-path)

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve build sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot).

**You grow one café agent, offline first or against your own model.** Across S01–S12 you grow a single
café-counter agent in `cafe/`: loop → evals → context → schema → consent →
detection → repair → tracing → reports → taxonomy → routing → judge. Every
session starts from the artifact and the number the last one produced.

Notebooks run offline on a deterministic stub unless you point them at
**your** OpenAI-compatible endpoint — a local model costs nothing. Against a
live model the mocks are gone: a prediction is only worth writing down when
the thing you are predicting can surprise you.

```bash
export COURSE_MODE=live
export CAFE_BASE_URL=http://127.0.0.1:11434/v1   # Ollama, LM Studio, anything OpenAI-compatible
export CAFE_API_KEY=ollama                       # any non-empty string for a local server
export CAFE_MODEL=qwen2.5:14b-instruct
uv run python -m cafe.doctor                     # one live call; proves your endpoint
uv run marimo edit sessions/s01-agent-loop/toy.py
```

`CAFE_*` takes precedence over `OPENAI_*`, with a fallback for each variable.
Use a dedicated shell and set all three explicitly before live work so a missing
course variable cannot select an unrelated credential or endpoint. No key is ever committed, printed, or logged. Notebooks are
[marimo](https://marimo.io) files — plain Python, reactive, diffable.

**Model size matters.** Most sessions are *better* with a mediocre model: bad
output is exactly what S02, S07 and S10 measure and repair. S04
(structured generation) and S12 (judge calibration) need a mid-size instruct
model with real tool-calling support.

**Take it in VS Code/Copilot or Cursor:** open this folder, read [docs/COMPANION.md](docs/COMPANION.md),
then start `sessions/s01-agent-loop/lesson.html` with
`@sessions/s01-agent-loop/companion.md` in chat.

**Take it in GitHub Codespaces (no local install):** click the badge above.
Setup (interpreter, pinned deps, marimo extension) runs itself; when the
terminal returns, prove it and start:

```bash
uv run python -m unittest discover -s tests   # green baseline, no keys needed
uv run marimo edit sessions/s01-agent-loop/toy.py
```

The Codespace is created under *your* GitHub account, so usage bills to you,
not the maintainer — see [about billing for Codespaces](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces).
Included allowances depend on your account and can change; check your account
billing settings before starting. Stop the machine when you stop (`Ctrl+Shift+P` →
"Codespaces: Stop Current Codespace") and delete it when done; an idle machine
burns hours, a kept one burns storage. The default path runs offline on the deterministic
stub. Codespaces support in this release is the offline path. A live endpoint
requires a separately verified private route from the Codespace; its loopback
address is not your laptop. Never expose a local model publicly just to connect it.

Editor defaults (local and Codespaces): Markdown opens as preview, session
notebooks open as marimo notebooks. For `lesson.html` files there is no
default to set — right-click → Open Preview reads them in the embedded
browser.

**Start here (HTML):** [`sessions/index.html`](sessions/index.html). A 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
covers the arc first (it may lag the lessons; it is a Google Gemini Notebook
overview; the lesson + notebook are canonical).

S01–S12 are the core path and they **do** accumulate: the capstone is the `cafe/`
package you finish with. S13 and S14 are optional unaided protocols. For the core
path, audit `cafe/loop.py` against the café golden set. For the optional hard path,
audit your `labs/cafe_host/` loop against its own banked lab suite. A system you
already own uses its own component and suite; do not mix their baselines.

## Core route and post-core overlay

- **Core harness route (start here):** work through S01–S12, then optionally use
  S13/S14 and `labs/`. If you are new to harnesses, complete S01–S12 before using
  the overlay.
- **Calibrated six-week post-core overlay:** use the
  [study-plan overlay](sessions/study-plan.html) to schedule authoritative external
  work from CS336, DeepLearning.AI RLHF, DeepLearning.AI vLLM, and the optional
  Anthropic API course, with explicit evidence to bank. The overlay is not part of
  the 14-session core and contains no copied external-course materials.

## Who it's for

Engineers who already call an LLM API and want the discipline around it: eval suites
that produce defensible numbers, context that survives compaction, consent gates,
safety layers, traces you can replay, judges you've calibrated, and explicit budget limits and accounting gaps.
Not an intro to prompting. The model call is the easy part; the harness is the
product.

## What a session looks like

1. **Read the lesson** (20–40 min) — theory in depth, a diagram, and a dated
   state-of-the-art table (what the industry currently does about it, with sources).
2. **Run the notebook** (30–60 min) — the session's slice of the café-counter
   agent in `cafe/`, on the stub or your live endpoint, with **predict-first**
   experiments and attempt-before-solution exercises.
3. **Self-check** — foldable quiz questions at the end of the lesson.
4. **(Optional) hard path** — after the notebook, `sessions/sNN-slug/lab.md`
   against cassettes (`--replay`) or your OpenAI-compatible endpoint (`--live`).
   `sessions/sNN-slug/companion.md` is what the Cursor companion should read first.
5. Sessions 13–14 invert the pattern: a closed-book rebuild audit and a
   ship/pilot protocol. Easy path: a system you own. Hard path:
   `labs/cafe_host/`. The assistant must not do these for you.

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
# No .env file or key is needed. Select the learner role in docs/COMPANION.md.
uv run python -m cafe.doctor  # offline stub; no endpoint contacted
uv run marimo edit sessions/s01-agent-loop/toy.py
```

Optional hard path (complete host already in `labs/cafe_host/`):

```bash
uv run python labs/run.py --session s01 --replay
uv run python labs/run.py --session s02 --replay
```

Copy edited notebooks, progress notes and experiment output outside the Git
checkout so they survive a clean clone, branch switch or course upgrade.

`--live` is never the default and never runs in CI. Tutor credentials belong to
your editor; lab `--live` uses separate shell `OPENAI_*`. See
[docs/COMPANION.md](docs/COMPANION.md) and `labs/README.md`.

The clone is small: preview mp4s stream from the web when you click ▶, so you do
not need Git LFS. Course logic is Python standard library only — the venv
supplies just the tooling (`marimo` to run the notebooks, `markdown` to render
the lessons). Open `sessions/index.html` locally (diagrams work from `file://`).

## Repository layout

There is **one** lesson book, one directory per session. `sessions/sNN-slug/`
holds everything that session needs: `lesson.md` (authoring source) builds to
`lesson.html` (what you read) in place (`uv run python tools/build.py`).
See [sessions/README.md](sessions/README.md).

| Path | Role |
| --- | --- |
| `sessions/sNN-slug/` | One session: lesson, toy, lab, companion, figures |
| `sessions/sNN-slug/lesson.md` → `lesson.html` | Authoring source → learner lesson |
| `sessions/sNN-slug/toy.py` | Marimo toy driving `cafe/` (S01–S12) |
| `sessions/sNN-slug/lab.md` | Optional hard-path protocol, not lesson text |
| `sessions/sNN-slug/companion.md` | Cursor companion rung |
| `.cursor/rules/ahp-companion.mdc` | Learner tutor rule |
| `docs/COMPANION.md` | Select and verify the editor tutor; separate model settings |
| `study/` | Optional study, pilot and transfer protocols |
| `AGENTS.md` / `CONTRIBUTING.md` | Contributor map |

## The toy-domain rule

Everything in the core path is **one toy from one familiar domain** — a
neighbourhood-café counter assistant (orders, tickets, allergens, the till) —
never a paste-ready production harness. Toy code is for reading, running,
and breaking. The numbers you print in a notebook do not substitute for a banked
eval baseline on a system you own. The optional labs are a **separate** café-host
spine — same toy domain, different artifact. If either spine grows file/shell tools, rewrite it back.

## Contributing

Installing dependencies and container images is a networked bootstrap. After
installation, the runtime verification gate uses the offline stub, committed
cassettes and a socket guard. The separate manual source-link workflow checks
external websites; it is not part of the offline execution claim.

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
material. Tagged releases remain historical evidence about their named artifacts;
[CHANGELOG.md](CHANGELOG.md) distinguishes released versions from pending changes.

## How this course was created

This course was created with substantial help in **design, planning, and
implementation** from **Codex using multiple GPT-family models**, **Claude Code**,
and **Muse Code**. Carlos Crespo Macaya remains responsible for the course's
direction, editorial decisions, and published content. Acknowledging these tools
does not imply endorsement by their providers.

### Validation model and offline replay

For the `v0.6.0-rc.1` validation and recording pass, the maintainer used
[NVIDIA Nemotron 3.5 Lightning 30B A3B (NVFP4)](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/modelcard),
running locally on an [NVIDIA DGX Spark workstation](https://build.nvidia.com/spark).
This setup powered live checks of all 12 S01–S12 notebooks and the recording of
the [hard-path lab cassettes](labs/cassettes/README.md): 19 files containing 43
model responses for reproducible replay of the recorded lab scenarios.

The [22 September fixture review](docs/cassette-review-2026-09-22.md) refreshed
all 10 governed lab recordings after clarifying the house rules and retained the
nine deliberate naïve baselines. The current lab set has 36 responses across
19 files. Four additional recorded notebook comparisons contain 16 responses
from the same local model; their provenance and limits are documented in the review.

The course supports offline study in two ways:

- **Notebooks:** a deterministic Python stub provides scripted and rule-based
  responses by default. Optional S04/S05/S07/S09 model recordings can also be
  checked offline with `uv run python tools/record_fixtures.py` after your attempts.
- **Hard-path labs:** `--replay` uses the committed request/response recordings
  from the real model.

After installing the course tooling, these defaults require no API key, running
LLM, provider connection, or NVIDIA hardware. A live OpenAI-compatible endpoint
is optional for exploring actual model behavior with your own inputs.

## License

Copyright 2026 Carlos Crespo Macaya. Contributors retain copyright in their own
contributions. These licenses grant reuse rights; they do not transfer copyright
ownership or place the work in the public domain.

- **Open source code — [Apache License 2.0](LICENSES/Apache-2.0.txt):** the
  `cafe/` Python artifact, session toys, labs Python, build tooling, and CI.
  This [OSI-approved license](https://opensource.org/license/apache-2-0) permits
  commercial use, modification, and redistribution, with an explicit patent
  grant from contributors. When redistributing, include the license, preserve
  applicable copyright and attribution notices (including [NOTICE](NOTICE)),
  and identify modified files as the license requires.
- **Open educational content — [CC BY 4.0](LICENSES/CC-BY-4.0.txt):** lessons,
  educational figures, course videos, documentation, lab protocols, and
  companions. You may share and adapt the material, including commercially,
  with appropriate credit, a license link, and an indication of changes.
  See the [CC BY 4.0 summary](https://creativecommons.org/licenses/by/4.0/).

Suggested attribution for reused educational material:

> [The Agent Harness Path](https://github.com/macayaven/agent-harness-path) by
> Carlos Crespo Macaya, licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

If you adapt the material, add a brief description of your changes.

Vendored Mermaid.js remains MIT; see [NOTICE](NOTICE). The course overview was generated with
Google Gemini Notebook; Google's marks in that file are not part of the CC BY
grant. Cited papers and vendor docs remain their authors'. Projects you build
while following the path are yours; reused course material keeps its license.
See [LICENSE](LICENSE) for the file-by-file split and third-party exceptions.
