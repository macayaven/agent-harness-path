# The Agent Harness Path

A self-contained course on **building, evaluating, and governing LLM agents** —
twelve notebook sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot). The default core notebook path is zero network, zero API
keys, zero cost: every "model" in the notebooks is a plain Python function you
can read. An **optional hard path** (`labs/`) grows one toy trivia-host spine
against a real OpenAI-compatible endpoint *or* committed cassettes. Completing
S01–S12 never requires a lab.

**Start here:** choose the native route below, then open
[`lessons/index.html`](lessons/index.html) and begin S01. Click ▶ to watch an
optional preview (streams from a public bucket). A 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
covers the arc first (the videos lag the lessons; they are Google Gemini Notebook
overviews, formerly NotebookLM; the lesson + notebook are canonical). Then run
the notebooks.

S01–S12 are the self-contained path. S13 and S14 are optional labs you run against
a system you already own — or, if you walked the hard path, against
`labs/trivia_host/`. The notebooks do not accumulate a capstone; the optional
spine does.

## Core route and post-core overlay

- **Core harness route (start here):** work through S01–S12, then optionally use
  S13/S14 and `labs/`. If you are new to harnesses, complete S01–S12 before using
  the overlay.
- **Calibrated six-week post-core overlay:** use the
  [study-plan overlay](lessons/study-plan.html) to schedule authoritative external
  work from CS336, DeepLearning.AI RLHF, DeepLearning.AI vLLM, and the optional
  Anthropic API course, with explicit evidence to bank. The overlay is not part of
  the 14-session core and contains no copied external-course materials. It requires
  either completed core/hard-path work or equivalent harness experience, plus an
  inspectable agent/eval artifact with a green, banked baseline.

The overlay supports two complementary learning emphases:
harness/evals/inference-systems depth and model-layer fundamentals depth.

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
5. Sessions 13–14 invert the pattern: a closed-book rebuild audit and a ship/pilot
   protocol. Easy path: a system you own. Hard path: `labs/trivia_host/`.

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
uv sync --frozen
uv run jupyter lab
```

Open `lessons/index.html` in a browser and `notebooks/s01_agent_loop_toy.ipynb`
in JupyterLab. Read the theory and diagram, write your prediction before running
the corresponding cell, attempt the exercise, then answer the lesson self-check.
Repeat that route through S12. Copy edited notebooks, progress notes and
experiment output outside the Git checkout so they survive a clean clone, branch
switch or course upgrade.

## Recommended optional CourseWeave experience

CourseWeave is an optional continuous guide for the same course. Its v0.2.0
macOS bundle is prepared but **not published yet**. Do not run the commands below
until the [CourseWeave v0.2.0 release page](https://github.com/macayaven/courseweave/releases/tag/v0.2.0)
lists both `agent-harness-path-courseweave-0.2.0-macos.tar.gz` and
`SHA256SUMS`. Public CourseWeave v0.1.0 uses schema v1 and is incompatible with
this course.

After publication, install [uv](https://docs.astral.sh/uv/getting-started/installation/),
change Terminal to a nonsynced local download folder, and run:

```sh
curl -fLO https://github.com/macayaven/courseweave/releases/download/v0.2.0/agent-harness-path-courseweave-0.2.0-macos.tar.gz
curl -fLO https://github.com/macayaven/courseweave/releases/download/v0.2.0/SHA256SUMS
shasum -a 256 --check SHA256SUMS --ignore-missing | grep -F 'agent-harness-path-courseweave-0.2.0-macos.tar.gz: OK'
tar -xzf agent-harness-path-courseweave-0.2.0-macos.tar.gz
cd "CourseWeave Student Pilot v0.2.0"
./"Start Course.command" --no-provider
```

Continue only when the checksum command reports the named bundle as `OK`. First
start installs isolated runtimes and creates
`~/Library/Application Support/CourseWeave/Agent Harness Path v0.2.0`; it does
not migrate or overwrite an earlier workspace. No source checkout, Node, separate
Jupyter installation or API key is required. Keep the Terminal open while
studying, save notebooks and press Ctrl-C there to stop. Run the same Start
command to resume.

The assistant remains off even if the shell contains provider keys. Reading,
notebooks, hints and self-checks still work. To opt in for one launch, use hidden
key input and name the model:

```sh
./"Start Course.command" --provider openai --model YOUR_OPENAI_MODEL
./"Start Course.command" --provider anthropic --model YOUR_ANTHROPIC_MODEL
```

Add `--base-url` only when required. Never put a key in a command argument,
notebook or issue. Credential-manager users can set `COURSEWEAVE_PROVIDER`, the
matching model/key variables and optional base URL, then use `--provider-env`.
The launcher loads no `.env` file and sends no key to the course kernel. The
supported assistant profile is text-only; provider configuration is checked on
the first question and does not prove arbitrary live or tool behavior.

Contributors validating a source-built application keep that route separate:
`scripts/courseweave` requires an explicit `--platform-python` and external
`--state-dir`, as documented in its help. It does not replace the checksum-bound
student bundle.

See the [guided installation and contract](study/COURSEWEAVE-PILOT.md),
[full-course study guide](study/FULL-COURSE.md), and optional
[first-test protocol](study/FIRST-TEST.md). S01–S12 offer reading → notebook
prediction/attempt/observation → self-check → optional hard lab.
S13/S14 remain optional notebook-free protocols, with unaided work separated from
permitted preparation and review. The original `uv run jupyter lab` route above remains the
independent zero-network, zero-key core path, apart from deliberately opening a
public video preview.

### Two paths

| | Easy (default) | Hard (optional) |
|---|---|---|
| Work | lesson → notebook → self-check | same, then `labs/sNN_*.md` |
| Command | `uv run jupyter lab` | `uv run python labs/run.py --session s02 --replay` |
| Keys | none | none for `--replay`; `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL` for `--live` |
| S13/S14 target | a system you own | `labs/trivia_host/` if you built it |

`--live` is never the default and never runs in CI. It uses an OpenAI-compatible
chat endpoint; confirm that the selected model supports the lab's requests before
interpreting live results. See `labs/README.md`.

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
- `labs/` — optional hard path: cassette client, trivia-host spine, session protocols
- `AGENTS.md` — contributor/agent conventions: the lesson format, the notebook
  contract, the toy-domain rule
- `COURSE-MAP.md` — coverage map
- `CONTRIBUTING.md` — how to propose a change
- `docs/` — documentation map, release process and draft release notes
- `study/` — optional study, pilot and transfer protocols; learner results belong
  outside the checkout

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
   for setup or study friction. Submission is deliberate; the course and
   CourseWeave send no telemetry or files to GitHub. Include the public
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
release material. The [release runbook](docs/RELEASING.md) records the checks and
publication boundary for the recommended next course release, `v0.2.0`; no tag or
release has been made for it. The bounded local pilot receipt is available as a
[reader-facing report](docs/verification/student-pilot-2026-09-13.md) and
[machine-readable record](docs/verification/student-pilot-2026-09-13.json). It is
evidence about named artifacts and checks, not a general product or learning claim.

## License

Split license, 2026 Carlos Crespo Macaya:

- **Apache-2.0** — notebooks, labs Python (`labs/**/*.py`), build tooling, CI (`LICENSES/Apache-2.0.txt`)
- **CC BY 4.0** — lessons, videos, documentation, and lab protocols (`labs/**/*.md`) (`LICENSES/CC-BY-4.0.txt`)

Vendored Mermaid.js remains MIT; see `NOTICE`. Video Overviews were generated with
Google Gemini Notebook; Google's marks in those files are not part of the CC BY
grant. Cited papers and vendor docs remain their authors'. Projects you build
while following the path are yours. See `LICENSE` for the file-by-file split.
