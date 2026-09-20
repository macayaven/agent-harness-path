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

S01–S12 are the self-contained path. S13 and S14 are optional labs you run against
your core `cafe/` artifact, your optional `labs/cafe_host/` artifact, or another
system you own. Use the chosen artifact's own suite and banked baseline.

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

## How to work a session

1. **Read the lesson** (20–40 min). The theory-in-depth section is the core; the
   state-of-the-art table tells you what the industry currently does about it.
2. **Run the notebook** (30–60 min). Every experiment has a **Predict first** prompt —
   write the prediction down *before* running the cell. Prediction misses are where
   the learning is; a prediction you didn't write down is one you'll retroactively fix.
3. **Do the exercises.** Attempt cells come before solution cells. The attempt is the
   rep; the solution is the spotter, not the lift.
4. **Self-check.** Foldable questions at the end of the lesson. Nobody is grading
   you.
5. **(Optional) hard path.** After the notebook: [`labs/README.md`](../labs/README.md).
   Replay committed cassettes (`uv run python labs/run.py --session sNN --replay`)
   or call any OpenAI-compatible endpoint (`--live`). S13 is an optional
   closed-book audit of one chosen artifact against its own banked suite.
   Core `cafe/`, optional `labs/cafe_host/` and bring-your-own results stay separate.

Setup: `uv sync --frozen` once, then `uv run python -m cafe.doctor` checks the
offline stub without keys. For live work, explicitly set `COURSE_MODE=live` plus
`CAFE_BASE_URL` / `CAFE_API_KEY` / `CAFE_MODEL` for your own endpoint and rerun
doctor. Open a session with
`uv run marimo edit sessions/s01-agent-loop/toy.py`. Course logic is Python
standard library only; `marimo` is the runtime.

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

S13 and S14 have no notebook by design. Choose core `cafe/`, optional
`labs/cafe_host/`, or a system you own, and retain that artifact's baseline. Completing S01–S12 does not require them, and does not require `labs/`.

Per-session videos were removed in September 2026: they lagged the lessons and
cost more to re-record than they taught. The learning happens in the notebook
(S01–S12) or the protocol (S13/S14). The single course overview above stays as
an optional preview of the arc.

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
