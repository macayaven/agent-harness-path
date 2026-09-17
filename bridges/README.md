# Session bridges

Each `sNN.md` is the **authored rung** between the inspectable toy notebook
and the optional trivia-host lab. In the core path the artifact is the `cafe/`
package the learner grows session by session; the trivia lab is a separate,
optional hard path. The Cursor companion rule tells the assistant to read the
current bridge before explaining a lab.

Easy path (lesson → notebook → self-check) never requires a lab. Open the
bridge when you start the optional hard path, or when the toy feels too
small and the lab feels too sudden.

| Session | Lesson | Toy | Core module | Lab protocol | Bridge |
| --- | --- | --- | --- | --- | --- |
| S01 | `lessons/S01-agent-loop.html` | `notebooks/s01_agent_loop_toy.py` | `cafe/loop.py` | `labs/s01_loop.md` | [s01.md](s01.md) |
| S02 | `lessons/S02-golden-evals.html` | `notebooks/s02_scripted_user_eval_toy.py` | `cafe/evals` | `labs/s02_evals.md` | [s02.md](s02.md) |
| S03 | `lessons/S03-context-engineering.html` | `notebooks/s03_context_engineering_toy.py` | `cafe/context.py` | `labs/s03_context.md` | [s03.md](s03.md) |
| S04 | `lessons/S04-structured-generation.html` | `notebooks/s04_structured_generation_toy.py` | `cafe/schema.py` | `labs/s04_schema.md` | [s04.md](s04.md) |
| S05 | `lessons/S05-consent-gate.html` | `notebooks/s05_consent_gate_toy.py` | `cafe/consent.py` | `labs/s05_consent.md` | [s05.md](s05.md) |
| S06 | `lessons/S06-layered-detection.html` | `notebooks/s06_layered_detection_toy.py` | `cafe/detect.py` | `labs/s06_policy.md` | [s06.md](s06.md) |
| S07 | `lessons/S07-repair-loop.html` | `notebooks/s07_repair_loop_toy.py` | `cafe/repair.py` | `labs/s07_repair.md` | [s07.md](s07.md) |
| S08 | `lessons/S08-observability-replay.html` | `notebooks/s08_observability_replay_toy.py` | `cafe/trace.py` | `labs/s08_replay.md` | [s08.md](s08.md) |
| S09 | `lessons/S09-evidence-reports.html` | `notebooks/s09_evidence_report_toy.py` | `cafe/report.py` | `labs/s09_debrief.md` | [s09.md](s09.md) |
| S10 | `lessons/S10-error-analysis.html` | `notebooks/s10_error_analysis_toy.py` | `cafe/taxonomy.py` | `labs/s10_errors.md` | [s10.md](s10.md) |
| S11 | `lessons/S11-budgets-routing.html` | `notebooks/s11_budgets_routing_toy.py` | `cafe/routing.py` | `labs/s11_budgets.md` | [s11.md](s11.md) |
| S12 | `lessons/S12-judge-calibration.html` | `notebooks/s12_judge_calibration_toy.py` | `cafe/judge.py` | `labs/s12_judge.md` | [s12.md](s12.md) |
| S13 | `lessons/S13-rebuild-from-memory.html` | — | `cafe/` whole package (hard path) | protocol in the lesson | [s13.md](s13.md) |
| S14 | `lessons/S14-ship-and-pilot.html` | — | `cafe/` whole package (hard path) | protocol in the lesson | [s14.md](s14.md) |

Notebooks are **marimo** files run live against the learner's own
OpenAI-compatible endpoint (single seam `get_client()` in `cafe/model.py`,
configured by `CAFE_BASE_URL` / `CAFE_API_KEY` / `CAFE_MODEL`). Open one with
`uv run marimo edit notebooks/sNN_…_toy.py`; only CI uses `COURSE_MODE=stub`.

How to take the course in Cursor, including a **local** OpenAI-compatible
model: [docs/COMPANION.md](../docs/COMPANION.md).
