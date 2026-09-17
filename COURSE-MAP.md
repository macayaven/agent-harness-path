# Course map — coverage S1–S14

The Agent Harness Path: self-contained HTML lessons and stdlib-only toys,
entry point `lessons/index.html`. SOTA tables are dated August 2026; re-date a
lesson's SOTA section when you refresh it.

S01–S12 are the self-contained path (lesson + notebook). Labs in `labs/` are
optional. S13 and S14 are optional protocols: easy path = a system they already
own; hard path = the `cafe/` package they built in S01–S12. The trivia host in
`labs/` is a separate optional hard path with its own replay/live contract.

## Model-layer boundary

The 14-session core teaches the harness around the model call: loops, evals,
context, boundaries, repair, replay, evidence, budgets, routing, and judge
calibration. It does not attempt to reproduce model-building or inference courses.
The optional [six-week study route](lessons/study-plan.html) is an overlay that
points to authoritative external work from CS336, DeepLearning.AI RLHF,
DeepLearning.AI vLLM, and the optional Anthropic API course, then defines the
evidence to bank. It is not a fifteenth session and copies none of those courses'
materials.

The overlay supports two complementary learning emphases:
harness/evals/inference-systems depth and model-layer fundamentals depth.

Each entry: the **concept gap** the material fills (what prose-only readings
don't teach), and the **toy** (runnable, a different domain from a production
harness).

| S | Lesson + toy | Concept gap | Toy |
|---|---|---|---|
| 1 | `lessons/src/S01-agent-loop.md` + `notebooks/s01_agent_loop_toy.py` (ships `cafe/loop.py`) | the loop is a `while` around a stateless API | one café shift: propose/pair/tool loop against your endpoint; optional `labs/s01_loop.md` |
| 2 | `lessons/src/S02-golden-evals.md` + `notebooks/s02_scripted_user_eval_toy.py` (ships `cafe/evals`) | eval suite as measurement instrument | scripted café scenarios + naive vs governed arm + deterministic checkers |
| 3 | `lessons/src/S03-context-engineering.md` + `notebooks/s03_context_engineering_toy.py` (ships `cafe/context.py`) | compaction & cache are invisible in prose | growing café conversation: four compaction policies; watch a pinned allergen rule survive |
| 4 | `lessons/src/S04-structured-generation.md` + `notebooks/s04_structured_generation_toy.py` (ships `cafe/schema.py`) | schema-constrained generation | café ticket contract + stdlib validator + bounded validate-and-retry |
| 5 | `lessons/src/S05-consent-gate.md` + `notebooks/s05_consent_gate_toy.py` (ships `cafe/consent.py`) | human-in-the-loop approval mechanics | gate (approve / edit / reject) before `fire_ticket`, with violation semantics |
| 6 | `lessons/src/S06-layered-detection.md` + `notebooks/s06_layered_detection_toy.py` (ships `cafe/detect.py`) | layered detection as data-driven policy | ordered screen over untrusted café text; pick an operating point, count false triggers |
| 7 | `lessons/src/S07-repair-loop.md` + `notebooks/s07_repair_loop_toy.py` (ships `cafe/repair.py`) | bounded regeneration with a curated failure view | repair loop: a bad ticket, real feedback, retries capped at 3 |
| 8 | `lessons/src/S08-observability-replay.md` + `notebooks/s08_observability_replay_toy.py` (ships `cafe/trace.py`) | spans, traces, deterministic replay | record a live café shift to JSONL; replay it exactly; diff two replays |
| 9 | `lessons/src/S09-evidence-reports.md` + `notebooks/s09_evidence_report_toy.py` (ships `cafe/report.py`) | evidence reports for a depleted reader | shift debrief from a transcript, with turn citations |
| 10 | `lessons/src/S10-error-analysis.md` + `notebooks/s10_error_analysis_toy.py` (ships `cafe/taxonomy.py`) | taxonomy from raw failures | cluster real café failure traces into ranked buckets, then a new eval task |
| 11 | `lessons/src/S11-budgets-routing.md` + `notebooks/s11_budgets_routing_toy.py` (ships `cafe/routing.py`) | policy-as-data routing & budgets | route table + budget gate over café phases; a leak route refuses to run |
| 12 | `lessons/src/S12-judge-calibration.md` + `notebooks/s12_judge_calibration_toy.py` (ships `cafe/judge.py`) | detection/false-positive measurement; judge agreement | seeded-defect game: 5 defective + 5 clean café transcripts, compute n/5 and FP n/5 |
| 13 | `lessons/src/S13-rebuild-from-memory.md` (optional protocol; no notebook) | none: the audit *is* the session | none — scaffolding the rebuild would defeat it |
| 14 | `lessons/src/S14-ship-and-pilot.md` (optional protocol; no notebook) | assembly, not composition | none |

## Session contract

1. Concept must fit in ~20–40 minutes of reading and one diagram.
2. Course logic is stdlib-only Python (3.11+); the only permitted non-stdlib
   imports are `marimo` and the course's own `cafe` package. The learner path is
   **live** against their own OpenAI-compatible endpoint through the single seam
   `get_client()` in `cafe/model.py` (`CAFE_BASE_URL` / `CAFE_API_KEY` /
   `CAFE_MODEL`); CI is zero network, zero keys, zero cost via `COURSE_MODE=stub`
   plus the socket guard. Toys come from a different domain than a production
   harness. **This rule binds `cafe/` and `notebooks/`.** `labs/` is the
   documented exception: optional, replay-first, keys never in git, `--live`
   never in CI. Trivia-domain tools only.
3. Nothing in it may be paste-ready into a production agent.
4. SOTA rows use exactly the five status tags in AGENTS.md and link a source.
