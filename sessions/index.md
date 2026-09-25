# The Agent Harness Path

A self-contained course on building, evaluating, and governing LLM agents — twelve
notebook sessions plus two optional protocol sessions (S13 rebuild audit, S14 ship
& pilot). The **default core notebook route** is zero network, zero API keys, zero
cost: every "model" in those notebooks is a plain Python function you can read, so
the mechanics are never hidden behind an API call. The post-core overlay links to
external courses and does not inherit that zero-network, zero-key, zero-cost
guarantee.

**New here?** Watch the 9-minute [course overview](S00-course-overview.mp4)
for the whole arc — core mechanics → context & boundaries → safety & governance →
observability → production — then [start at S01](s01-agent-loop/lesson.html). The overview is a Google Gemini
Notebook overview (formerly NotebookLM; generated 14 Aug 2026) and may lag the
lesson text; the lesson and notebook are canonical. Google branding in the
file is Google's. Clone the repo to run the notebooks.

This page is the course home: how to work a session, how to run the notebooks
against your own model, and every session in order. Each lesson links to the one
before and after it, so from S01 you can follow the chain.

S01–S12 are the self-contained path, and they accumulate: the capstone is the
`cafe/` package you finish with. S13 and S14 are optional protocols you run against
your core `cafe/` artifact, your optional `labs/cafe_host/` artifact, or another
system you own. Use the chosen artifact's own suite and banked baseline, and never
mix baselines between them.

## How to work a session

1. **Read the lesson** (20–40 min). The theory-in-depth section is the core; the
   state-of-the-art table tells you what the industry currently does about it.
2. **Run the notebook** (30–60 min): `uv run marimo edit sessions/sNN-slug/toy.py`.
   Every experiment has a **Predict first** prompt —
   write the prediction down *before* running the cell, then compare what you
   observed with what you wrote. Prediction misses are where the learning is; a
   prediction you didn't write down is one you'll retroactively fix.
3. **Do the exercises.** Attempt cells come before solution cells. The attempt is the
   rep; the solution is the spotter, not the lift. Running every cell demonstrates
   execution; an empty attempt skeleton or a score against reference labels is not
   your independent work.
4. **Self-check** (5–10 min). Foldable questions at the end of the lesson. Attempt
   each one before revealing it, then record the correction in your own words; a
   correct selection does not certify mastery. Nobody is grading you.
5. **(Optional) hard path.** After the notebook: [`labs/README.md`](../labs/README.md).
   Before a lab, read the session's `companion.md`: it maps the notebook's `cafe/`
   module to the café host's code, which helps when the toy feels too small and the
   lab feels too sudden. Replay committed cassettes
   (`uv run python labs/run.py --session sNN --replay`) or call any
   OpenAI-compatible endpoint (`--live`).

That is three required activities per session (read, notebook, self-check): 36
across S01–S12, not twelve automatic completions. The authored hints and
self-checks live in the lesson and work without any model or tutor. If you study
with an AI tutor in VS Code or Cursor, set it up with
[`docs/COMPANION.md`](../docs/COMPANION.md): it explains and reviews, and your
predictions and attempts stay yours.

Setup is `uv sync --frozen` once (the repository README), then
`uv run python -m cafe.doctor` checks the offline stub without keys. Course logic
is Python standard library only; `marimo` is the runtime.

## Run against your own model

Notebooks run on the deterministic offline stub by default: no network, no key, no
environment file. To run them against your own OpenAI-compatible endpoint, use a
dedicated shell and set all three course variables explicitly:

```bash
export COURSE_MODE=live
export CAFE_BASE_URL=http://127.0.0.1:11434/v1   # Ollama, LM Studio, anything OpenAI-compatible
export CAFE_API_KEY=ollama                       # any non-empty string for a local server
export CAFE_MODEL=qwen2.5:14b-instruct
uv run python -m cafe.doctor                     # one live call; proves your endpoint
```

`CAFE_*` takes precedence over `OPENAI_*`, with a fallback for each variable;
setting all three means a missing course variable cannot select an unrelated
credential or endpoint. No key is ever committed, printed, or logged. CI sets stub
mode and blocks sockets. These variables configure only the notebooks: an editor
tutor's model is set in the editor, and the hard path's `--live` reads its own
`OPENAI_*` variables ([`labs/README.md`](../labs/README.md)).

**Model size matters.** Most sessions are *better* with a mediocre model: bad
output is exactly what S02, S07 and S10 measure and repair. S04 (structured
generation) and S12 (judge calibration) need a mid-size instruct model with real
tool-calling support.

## The sessions

| # | Session | Teaches | Notebook | Lab |
|---|---|---|---|---|
| 1 | [The agent loop](s01-agent-loop/lesson.html) | A client-side loop around a stateless API; append-verbatim and tool-pairing invariants | [toy.py](s01-agent-loop/toy.py) | [lab.md](s01-agent-loop/lab.md) |
| 2 | [Golden sets & baselines](s02-golden-evals/lesson.html) | Evals as measurement instruments; scripted users, two-tier checkers, fixture invariant, naive baseline | [toy.py](s02-golden-evals/toy.py) | [lab.md](s02-golden-evals/lab.md) |
| 3 | [Context engineering](s03-context-engineering/lesson.html) | Compaction, pinning, attention decay; measure retained rules and behavior across a compaction boundary | [toy.py](s03-context-engineering/toy.py) | [lab.md](s03-context-engineering/lab.md) |
| 4 | [Structured generation](s04-structured-generation/lesson.html) | Schema as contract; validate-and-retry; valid ≠ correct | [toy.py](s04-structured-generation/toy.py) | [lab.md](s04-structured-generation/lab.md) |
| 5 | [The consent gate](s05-consent-gate/lesson.html) | Plan-then-execute; approve/edit/reject; violation semantics; abort vs degrade | [toy.py](s05-consent-gate/toy.py) | [lab.md](s05-consent-gate/lab.md) |
| 6 | [Layered detection](s06-layered-detection/lesson.html) | Keyword-floor + classifier pipeline; policy as data; the false-trigger counter | [toy.py](s06-layered-detection/toy.py) | [lab.md](s06-layered-detection/lab.md) |
| 7 | [The repair loop](s07-repair-loop/lesson.html) | Bounded regeneration; the curated failure view; what context a retry gets | [toy.py](s07-repair-loop/toy.py) | [lab.md](s07-repair-loop/lab.md) |
| 8 | [Observability & replay](s08-observability-replay/lesson.html) | Spans and traces; fail-soft telemetry; record/replay content-identical; hunt planted nondeterminism | [toy.py](s08-observability-replay/toy.py) | [lab.md](s08-observability-replay/lab.md) |
| 9 | [Evidence reports](s09-evidence-reports/lesson.html) | Reports a depleted reader can trust; citation and coverage validators; the 30-second test | [toy.py](s09-evidence-reports/toy.py) | [lab.md](s09-evidence-reports/lab.md) |
| 10 | [Error analysis](s10-error-analysis/lesson.html) | Failure logs → taxonomy → new evals; open and axial coding on real traces | [toy.py](s10-error-analysis/toy.py) | [lab.md](s10-error-analysis/lab.md) |
| 11 | [Budgets & routing](s11-budgets-routing/lesson.html) | Simulated routing over one client; cost estimates, missing usage and budget refusals; latency math | [toy.py](s11-budgets-routing/toy.py) | [lab.md](s11-budgets-routing/lab.md) |
| 12 | [Judge calibration](s12-judge-calibration/lesson.html) | Seeded-defect games; label-before-you-see-the-judge; Cohen's κ; rates → policy | [toy.py](s12-judge-calibration/toy.py) | [lab.md](s12-judge-calibration/lab.md) |
| 13 | [Rebuild from memory](s13-rebuild-from-memory/lesson.html) | Optional lab: closed-book audit of a system you own | — (the audit is the exercise) | hard path: `cafe_host/`; else BYO |
| 14 | [Ship & pilot](s14-ship-and-pilot/lesson.html) | Optional lab: cold acceptance run, first real user, public artifact | — (protocol, not notebook) | hard path: fixture run of the host; else BYO |

S13 and S14 invert the pattern: no notebook by design, and an unaided protocol on
the artifact you choose. Read each lesson's prerequisites before deciding to
perform it. Their working cards sit beside the lessons: `audit-card.md` for S13;
`cold-run-card.md`, `pilot-page-card.md` and `pilot-card.md` for S14. During
unaided work, close the assistant chat and return to review only after the sitting
ends and the evidence is saved. Deferring either protocol does not block S01–S12,
and completing S01–S12 requires neither them nor `labs/`. Record planned and
performed activities separately; no software test manufactures a rebuild, an
elapsed week, a consenting person, a publication or a learning result.

Per-session videos were removed in September 2026: they lagged the lessons and
cost more to re-record than they taught. The learning happens in the notebook
(S01–S12) or the protocol (S13/S14). The single course overview above stays as
an optional preview of the arc.

## Core route and post-core overlay

- **Core harness route (start here):** work through S01–S12, then optionally use
  S13/S14 and `labs/`. If you are new to harnesses, complete S01–S12 before using
  the overlay.
- **Calibrated six-week post-core overlay:** use the
  [study-plan overlay](study-plan.html) to schedule authoritative external work
  from CS336, DeepLearning.AI RLHF, DeepLearning.AI vLLM, and the optional Anthropic
  API course, with explicit evidence to bank. The overlay is not part of the
  14-session core and contains no copied external-course materials. It requires
  either completed core/hard-path work or equivalent harness experience, plus an
  inspectable agent/eval artifact with a green, banked baseline.

The model call is the easy part; the harness is the product. The overlay supports
two complementary learning emphases: harness/evals/inference-systems depth and
model-layer fundamentals depth.

## Your work and your feedback

Keep your edited notebooks, predictions and notes in a local, nonsynced folder
outside this checkout: a clean clone, branch switch or version change replaces the
course files.
To report friction, [`study/FEEDBACK.md`](../study/FEEDBACK.md) gives one useful
question per session and says what to include and what to leave out. The course
sends no telemetry.

## The pedagogical commitments

- **One toy domain, never the artifact.** Every notebook grows the same
  neighbourhood-café counter assistant — orders, tickets, allergens, the till —
  chosen so the mechanics are identical to production and the stakes are not.
- **Predict first, always.** Written predictions before every run; the suite of
  habits this builds is the actual curriculum.
- **Failure is on the syllabus.** Each toy contains deliberately broken variants
  (labeled) so you meet the failure modes cheaply, where the fix is one cell away.
- **State of the art, dated.** Each lesson's SOTA table states its review date
  and every row carries a source. Check evolving specifications and distinguish
  preprint findings from general guarantees.

## License

Apache-2.0 for notebooks, labs Python, and tooling; CC BY 4.0 for lessons,
the course overview video, docs, and lab protocols. Cited sources remain their
authors'. Google branding in the course overview is Google's. See `LICENSE`
in the repository root.
