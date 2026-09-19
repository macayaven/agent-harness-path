# Session bridges

Each `sNN.md` is the **authored rung** between the inspectable toy notebook
and the optional café-host lab. In the core path the artifact is the `cafe/`
package the learner grows session by session; the café-host lab is a separate,
optional hard path. The Cursor companion rule tells the assistant to read the
current bridge before explaining a lab.

Easy path (lesson → notebook → self-check) never requires a lab. Open the
bridge when you start the optional hard path, or when the toy feels too
small and the lab feels too sudden.

| Session | Lesson | Toy | Core module | Lab protocol | Bridge |
| --- | --- | --- | --- | --- | --- |
| S01 | `sessions/s01-agent-loop/lesson.html` | `sessions/s01-agent-loop/toy.py` | `cafe/loop.py` | `sessions/s01-agent-loop/lab.md` | [s01.md](../sessions/s01-agent-loop/companion.md) |
| S02 | `sessions/s02-golden-evals/lesson.html` | `sessions/s02-golden-evals/toy.py` | `cafe/evals` | `sessions/s02-golden-evals/lab.md` | [s02.md](../sessions/s02-golden-evals/companion.md) |
| S03 | `sessions/s03-context-engineering/lesson.html` | `sessions/s03-context-engineering/toy.py` | `cafe/context.py` | `sessions/s03-context-engineering/lab.md` | [s03.md](../sessions/s03-context-engineering/companion.md) |
| S04 | `sessions/s04-structured-generation/lesson.html` | `sessions/s04-structured-generation/toy.py` | `cafe/schema.py` | `sessions/s04-structured-generation/lab.md` | [s04.md](../sessions/s04-structured-generation/companion.md) |
| S05 | `sessions/s05-consent-gate/lesson.html` | `sessions/s05-consent-gate/toy.py` | `cafe/consent.py` | `sessions/s05-consent-gate/lab.md` | [s05.md](../sessions/s05-consent-gate/companion.md) |
| S06 | `sessions/s06-layered-detection/lesson.html` | `sessions/s06-layered-detection/toy.py` | `cafe/detect.py` | `sessions/s06-layered-detection/lab.md` | [s06.md](../sessions/s06-layered-detection/companion.md) |
| S07 | `sessions/s07-repair-loop/lesson.html` | `sessions/s07-repair-loop/toy.py` | `cafe/repair.py` | `sessions/s07-repair-loop/lab.md` | [s07.md](../sessions/s07-repair-loop/companion.md) |
| S08 | `sessions/s08-observability-replay/lesson.html` | `sessions/s08-observability-replay/toy.py` | `cafe/trace.py` | `sessions/s08-observability-replay/lab.md` | [s08.md](../sessions/s08-observability-replay/companion.md) |
| S09 | `sessions/s09-evidence-reports/lesson.html` | `sessions/s09-evidence-reports/toy.py` | `cafe/report.py` | `sessions/s09-evidence-reports/lab.md` | [s09.md](../sessions/s09-evidence-reports/companion.md) |
| S10 | `sessions/s10-error-analysis/lesson.html` | `sessions/s10-error-analysis/toy.py` | `cafe/taxonomy.py` | `sessions/s10-error-analysis/lab.md` | [s10.md](../sessions/s10-error-analysis/companion.md) |
| S11 | `sessions/s11-budgets-routing/lesson.html` | `sessions/s11-budgets-routing/toy.py` | `cafe/routing.py` | `sessions/s11-budgets-routing/lab.md` | [s11.md](../sessions/s11-budgets-routing/companion.md) |
| S12 | `sessions/s12-judge-calibration/lesson.html` | `sessions/s12-judge-calibration/toy.py` | `cafe/judge.py` | `sessions/s12-judge-calibration/lab.md` | [s12.md](../sessions/s12-judge-calibration/companion.md) |
| S13 | `sessions/s13-rebuild-from-memory/lesson.html` | — | `cafe/` whole package (hard path) | protocol in the lesson | [s13.md](../sessions/s13-rebuild-from-memory/companion.md) |
| S14 | `sessions/s14-ship-and-pilot/lesson.html` | — | `cafe/` whole package (hard path) | protocol in the lesson | [s14.md](../sessions/s14-ship-and-pilot/companion.md) |

Notebooks are **marimo** files, offline by default (deterministic stub via the
single seam `get_client()` in `cafe/model.py`). Set `COURSE_MODE=live` plus
`CAFE_BASE_URL` / `CAFE_API_KEY` / `CAFE_MODEL` to run against the learner's own
OpenAI-compatible endpoint. Open one with
`uv run marimo edit sessions/sNN-slug/toy.py`.

How to take the course in Cursor, including a **local** OpenAI-compatible
model: [docs/COMPANION.md](../docs/COMPANION.md).
