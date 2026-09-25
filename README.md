# The Agent Harness Path

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/macayaven/agent-harness-path)

A self-contained course on **building, evaluating, and governing LLM agents**:
twelve build sessions plus two optional apply-to-your-system protocols (S13
rebuild audit, S14 ship & pilot).

**You grow one café agent, offline first or against your own model.** Across
S01–S12 you grow a single café-counter agent in `cafe/`: loop → evals → context →
schema → consent → detection → repair → tracing → reports → taxonomy → routing →
judge. Every session starts from the artifact and the number the last one
produced.

Notebooks run offline on a deterministic stub unless you point them at **your**
OpenAI-compatible endpoint; a local model costs nothing. Against a live model the
mocks are gone: a prediction is only worth writing down when the thing you are
predicting can surprise you.

Optional preview: a 9-minute
[course overview](https://storage.googleapis.com/macayaven-agent-harness-path-videos/S00-course-overview.mp4)
of the whole arc. It is a Google Gemini Notebook overview and may lag the
lessons; the lessons and notebooks are canonical.

## Who it's for

Engineers who already call an LLM API and want the discipline around it: eval suites
that produce defensible numbers, context that survives compaction, consent gates,
safety layers, traces you can replay, judges you've calibrated, and explicit budget limits and accounting gaps.
Not an intro to prompting. The model call is the easy part; the harness is the
product.

## Start

The native route works on macOS or Linux with Git, Python 3.11+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/). It reads no API
credentials. Clone onto local storage, outside iCloud Drive and Google Drive:

```bash
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync --frozen              # creates .venv/ (Python 3.11+, pinned by uv.lock)
uv run python -m cafe.doctor  # offline stub; no endpoint contacted, no key needed
```

Then open **`sessions/index.html`**, the course home. From here on it is the only
page you need: how to work a session, how to run the notebooks against your own
model, and all fourteen sessions in order. Every lesson links to the one before
and after it. The first notebook is:

```bash
uv run marimo edit sessions/s01-agent-loop/toy.py
```

Notebooks are [marimo](https://marimo.io) files: plain Python, reactive, diffable.
In VS Code or Cursor (local or Codespaces), Markdown opens as preview and session
notebooks open as marimo notebooks. `lesson.html` files have no default viewer:
right-click → Open Preview reads them in the embedded browser, or open them in any
browser. Diagrams work from `file://`.

**Keep your work outside the checkout.** Course source, blank templates and
generated lessons belong in Git. Your edited notebooks, progress notes,
observations and experiment output belong in a separate local, nonsynced folder, so they
survive a clean clone, branch switch or course upgrade. A clean clone is the
migration boundary; no release script rewrites an old workspace.

The clone is small: preview mp4s stream from the web when you click ▶, so you do
not need Git LFS. Course logic is Python standard library only; the venv supplies
just the tooling (`marimo` to run the notebooks, `markdown` to render the lessons).

## Other ways to take it

### In the browser, no install (GitHub Codespaces)

Click the badge above. Setup (interpreter, pinned deps, marimo extension) runs
itself; when the terminal returns, prove it and start:

```bash
uv run python -m unittest discover -s tests   # green baseline, no keys needed
uv run marimo edit sessions/s01-agent-loop/toy.py
```

The Codespace is created under *your* GitHub account, so usage bills to you,
not the maintainer — see [about billing for Codespaces](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces).
Included allowances depend on your account and can change; check your account
billing settings before starting. Stop the machine when you stop (`Ctrl+Shift+P` →
"Codespaces: Stop Current Codespace") and delete it when done; an idle machine
burns hours, a kept one burns storage. Codespaces support in this release is the
offline path. A live endpoint requires a separately verified private route from
the Codespace; its loopback address is not your laptop. Never expose a local
model publicly just to connect it.

### Against your own model

Set `COURSE_MODE=live` and three `CAFE_*` variables, then prove the endpoint with
`cafe.doctor`. The course home's **Run against your own model** section has the
commands and says which sessions need a stronger model.

### With an AI tutor in VS Code/Copilot or Cursor

[docs/COMPANION.md](docs/COMPANION.md) selects and verifies the learner role: a
tutor that explains and reviews your own work but never completes it. Its model
is configured in the editor, separately from the course variables.

### The hard path

After a session's notebook, build a separate café host against committed
recordings of a real model: [labs/README.md](labs/README.md). Replay needs no
key; `--live` is never the default and never runs in CI. Completing S01–S12 never
requires a lab.

### After the core

The [six-week post-core overlay](sessions/study-plan.html) schedules
authoritative external work (CS336, DeepLearning.AI RLHF and vLLM, optionally the
Anthropic API course) with explicit evidence to bank. It is not part of the
fourteen sessions.

## Where things live

Each topic has one owner file. The others link to it instead of repeating it.

| You want to… | Open |
| --- | --- |
| Take the course | `sessions/index.html` (built from [sessions/index.md](sessions/index.md)) |
| Know what each file in a session folder is for | [sessions/README.md](sessions/README.md) |
| Study with an AI tutor | [docs/COMPANION.md](docs/COMPANION.md) |
| Take the optional hard path | [labs/README.md](labs/README.md) |
| Give feedback, or run the pilot and transfer protocols | [study/FEEDBACK.md](study/FEEDBACK.md) |
| Contribute | [CONTRIBUTING.md](CONTRIBUTING.md); coding agents follow [AGENTS.md](AGENTS.md) |
| See what changed | [CHANGELOG.md](CHANGELOG.md) |
| Report a secret or unsafe committed code | [SECURITY.md](SECURITY.md) |

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
   telemetry or files to GitHub. [study/FEEDBACK.md](study/FEEDBACK.md) says what
   to include and what to leave out.
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) before a pull request (how to edit
   sources, the verify commands, what maintainers will reject).
3. By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
4. Real secrets or unsafe committed code: [SECURITY.md](SECURITY.md), not a
   public issue.

Good first contributions are a dead URL, a SOTA row whose Take overstates the
linked abstract, or a predict-first prompt that leaks the answer.

Tagged releases remain historical evidence about their named artifacts;
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
