# The Agent Harness Path

A self-contained course on building, evaluating, and governing LLM agents — twelve
notebook sessions plus two optional protocol sessions (S13 rebuild audit, S14 ship
& pilot). Zero network, zero API keys, zero cost: every "model" in the notebooks
is a plain Python function you can read, so the mechanics are never hidden behind
an API call.

**New here?** Watch the 9-minute [course overview](videos/S00-course-overview.mp4)
for the whole arc — core mechanics → context & boundaries → safety & governance →
observability → production — then start at S01. The videos are Google Gemini
Notebook overviews (formerly NotebookLM; generated 14 Aug 2026) and may lag the
lesson text; the lesson and notebook are canonical. Google branding in the
files is Google's. Click ▶: the mp4 streams in the browser. Clone the repo to
run the notebooks.

S01–S12 are the self-contained path. S13 and S14 are optional labs you run against
a system you already own.

## How to work a session

1. **Read the lesson** (20–40 min). The theory-in-depth section is the core; the
   state-of-the-art table tells you what the industry currently does about it.
2. **Run the notebook** (30–60 min). Every experiment has a **Predict first** prompt —
   write the prediction down *before* running the cell. Prediction misses are where
   the learning is; a prediction you didn't write down is one you'll retroactively fix.
3. **Do the exercises.** Attempt cells come before solution cells. The attempt is the
   rep; the solution is the spotter, not the lift.
4. **Self-check.** Foldable questions at the end of the lesson. Nobody is grading
   you. S13 is an optional closed-book audit of a system you own, and it is strict.

Setup: `uv sync` once, then `uv run jupyter lab` (or open the notebooks in any
Jupyter frontend). Notebook code is Python standard library only.

## The sessions

| # | Session | Teaches | Notebook | Video |
|---|---|---|---|---|
| 1 | [The agent loop](S01-agent-loop.html) | A client-side loop around a stateless API; append-verbatim and tool-pairing invariants | [s01_agent_loop_toy.ipynb](../notebooks/s01_agent_loop_toy.ipynb) | [▶](videos/S01-agent-loop.mp4) |
| 2 | [Golden sets & baselines](S02-golden-evals.html) | Evals as measurement instruments; scripted users, two-tier checkers, fixture invariant, naive baseline | [s02_scripted_user_eval_toy.ipynb](../notebooks/s02_scripted_user_eval_toy.ipynb) | [▶](videos/S02-golden-evals.mp4) |
| 3 | [Context engineering](S03-context-engineering.html) | Compaction, pinning, attention decay; watch a buried rule die across a compaction boundary | [s03_context_engineering_toy.ipynb](../notebooks/s03_context_engineering_toy.ipynb) | [▶](videos/S03-context-engineering.mp4) |
| 4 | [Structured generation](S04-structured-generation.html) | Schema as contract; validate-and-retry; valid ≠ correct | [s04_structured_generation_toy.ipynb](../notebooks/s04_structured_generation_toy.ipynb) | [▶](videos/S04-structured-generation.mp4) |
| 5 | [The consent gate](S05-consent-gate.html) | Plan-then-execute; approve/edit/reject; violation semantics; abort vs degrade | [s05_consent_gate_toy.ipynb](../notebooks/s05_consent_gate_toy.ipynb) | [▶](videos/S05-consent-gate.mp4) |
| 6 | [Layered detection](S06-layered-detection.html) | Keyword-floor + classifier pipeline; policy as data; the false-trigger counter | [s06_layered_detection_toy.ipynb](../notebooks/s06_layered_detection_toy.ipynb) | [▶](videos/S06-layered-detection.mp4) |
| 7 | [The repair loop](S07-repair-loop.html) | Bounded regeneration; the curated failure view; what context a retry gets | [s07_repair_loop_toy.ipynb](../notebooks/s07_repair_loop_toy.ipynb) | [▶](videos/S07-repair-loop.mp4) |
| 8 | [Observability & replay](S08-observability-replay.html) | Spans and traces; fail-soft telemetry; record/replay content-identical; hunt planted nondeterminism | [s08_observability_replay_toy.ipynb](../notebooks/s08_observability_replay_toy.ipynb) | [▶](videos/S08-observability-replay.mp4) |
| 9 | [Evidence reports](S09-evidence-reports.html) | Reports a depleted reader can trust; citation and coverage validators; the 30-second test | [s09_evidence_report_toy.ipynb](../notebooks/s09_evidence_report_toy.ipynb) | [▶](videos/S09-evidence-reports.mp4) |
| 10 | [Error analysis](S10-error-analysis.html) | Failure logs → taxonomy → new evals; open and axial coding on real traces | [s10_error_analysis_toy.ipynb](../notebooks/s10_error_analysis_toy.ipynb) | [▶](videos/S10-error-analysis.mp4) |
| 11 | [Budgets & routing](S11-budgets-routing.html) | Budgets as runtime invariants; routing as policy-as-data; the privacy boundary; latency math | [s11_budgets_routing_toy.ipynb](../notebooks/s11_budgets_routing_toy.ipynb) | [▶](videos/S11-budgets-routing.mp4) |
| 12 | [Judge calibration](S12-judge-calibration.html) | Seeded-defect games; label-before-you-see-the-judge; Cohen's κ; rates → policy | [s12_judge_calibration_toy.ipynb](../notebooks/s12_judge_calibration_toy.ipynb) | [▶](videos/S12-judge-calibration.mp4) |
| 13 | [Rebuild from memory](S13-rebuild-from-memory.html) | Optional lab: closed-book audit of a system you own | — (the audit is the exercise) | [▶](videos/S13-rebuild-from-memory.mp4) |
| 14 | [Ship & pilot](S14-ship-and-pilot.html) | Optional lab: cold acceptance run, first real user, public artifact | — (protocol, not notebook) | [▶](videos/S14-ship-and-pilot.mp4) |

S13 and S14 have no notebook by design: they are optional *bring your own system*
labs — you apply them to a project you already own, from this path, from
work, or from elsewhere. Completing S01–S12 does not require them.

The videos are Google Gemini Notebook overviews of the lessons (formerly
NotebookLM; in `lessons/videos/`; generated 14 Aug 2026). Use them as preview or
review — the learning happens in the notebook (S01–S12) or the protocol
(S13/S14), not the video. Google branding in the files is Google's.

## The pedagogical commitments

- **Toys from real domains, never the artifact.** Every notebook is a small complete
  system — a hotel concierge, a repair shop, a mopbot, a trivia host — chosen so the
  mechanics are identical to production and the stakes are not.
- **Predict first, always.** Written predictions before every run; the suite of
  habits this builds is the actual curriculum.
- **Failure is on the syllabus.** Each toy contains deliberately broken variants
  (labeled) so you meet the failure modes cheaply, where the fix is one cell away.
- **State of the art, dated.** Each lesson's SOTA table is stamped "as of August 2026"
  and every claim carries a source. Treat anything older than a year as history.

## License

Apache-2.0 for notebooks and tooling; CC BY 4.0 for lessons, videos, and docs.
Cited sources remain their authors'. Google branding in the Video Overviews is
Google's. See `LICENSE` in the repository root.
