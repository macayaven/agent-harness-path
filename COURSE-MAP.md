# Course map — coverage S1–S14

The Agent Harness Path: self-contained HTML lessons and stdlib-only toys,
entry point `lessons/index.html`. SOTA tables are dated August 2026; re-date a
lesson's SOTA section when you refresh it.

S01–S12 are the self-contained path (lesson + notebook). S13 and S14 are
optional protocols the learner applies to a system they already own.

Each entry: the **concept gap** the material fills (what prose-only readings
don't teach), and the **toy** (runnable, a different domain from a production
harness).

| S | Lesson + toy | Concept gap | Toy |
|---|---|---|---|
| 1 | `lessons/src/S01-agent-loop.md` + `s01_agent_loop_toy.ipynb` | the loop is a `while` around a stateless API | weather-bot loop on a mock model |
| 2 | `lessons/src/S02-golden-evals.md` + `s02_scripted_user_eval_toy.ipynb` | eval suite as measurement instrument | scripted user + naive/governed engines + checks |
| 3 | `lessons/src/S03-context-engineering.md` + `s03_context_engineering_toy.ipynb` | compaction & cache are invisible in prose | growing-conversation simulator: truncation vs summary vs pinning; watch a buried rule die |
| 4 | `lessons/src/S04-structured-generation.md` + `s04_structured_generation_toy.ipynb` | schema-constrained generation | JSON-schema validator over mock outputs + retry-on-invalid loop |
| 5 | `lessons/src/S05-consent-gate.md` + `s05_consent_gate_toy.ipynb` | human-in-the-loop approval mechanics | gate (approve / edit / reject) over a fake spec, with violation semantics |
| 6 | `lessons/src/S06-layered-detection.md` + `s06_layered_detection_toy.ipynb` | layered detection as data-driven policy | keyword-floor + classifier pipeline over fixture strings, with false-trigger counter |
| 7 | `lessons/src/S07-repair-loop.md` + `s07_repair_loop_toy.ipynb` | bounded regeneration with a curated failure view | mock scorer fails first N attempts; regeneration loop capped at 3 |
| 8 | `lessons/src/S08-observability-replay.md` + `s08_observability_replay_toy.ipynb` | spans, traces, deterministic replay | record a mock session to JSONL; replay it offline content-identical; diff two replays |
| 9 | `lessons/src/S09-evidence-reports.md` + `s09_evidence_report_toy.ipynb` | evidence reports for a depleted reader | generate a debrief from a fake transcript, with turn references |
| 10 | `lessons/src/S10-error-analysis.md` + `s10_error_analysis_toy.ipynb` | taxonomy from raw failures | cluster a pile of fake failure logs into categories |
| 11 | `lessons/src/S11-budgets-routing.md` + `s11_budgets_routing_toy.ipynb` | policy-as-data routing & budgets | route table over fake phases; a misconfigured route refuses to run |
| 12 | `lessons/src/S12-judge-calibration.md` + `s12_judge_calibration_toy.ipynb` | detection/false-positive measurement; judge agreement | seeded-defect game: 5 mutated + 5 clean mock transcripts, compute n/5 and FP n/5 |
| 13 | `lessons/src/S13-rebuild-from-memory.md` (optional protocol; no notebook) | none: the audit *is* the session | none — scaffolding the rebuild would defeat it |
| 14 | `lessons/src/S14-ship-and-pilot.md` (optional protocol; no notebook) | assembly, not composition | none |

## Session contract

1. Concept must fit in ~20–40 minutes of reading and one diagram.
2. Toy must be runnable with zero network, zero keys, zero cost, and come from a
   different domain than a production harness.
3. Nothing in it may be paste-ready into a production agent.
4. SOTA rows use exactly the five status tags in AGENTS.md and link a source.
