# Course map — coverage S1–S14

This map tracks both layers of the repo:

- **Companion layer** (`sessions/`): six-part session guides that feed the course
  repo's real build. Written *when you approach the session* — material written six
  sessions early rots, and attacking a fresh draft is where engagement happens (see
  WHY-THIS-DESIGN.md). S1–S2 exist; S3+ get written on approach.
- **Standalone path** (`lessons/` + `notebooks/`): The Agent Harness Path —
  self-contained HTML lessons and toys for all fourteen sessions, entry point
  `lessons/index.html`. Written in one pass (August 2026) at the owner's direction;
  the rot risk is accepted and managed by re-dating each lesson's SOTA section when
  refreshed.

Each entry: the **concept gap** the material fills (what the readings don't teach),
the **toy** (runnable, different domain), and the **bridge** (guided reps before the
real build).

| S | Companion guide | Standalone lesson + toy | Concept gap | Toy | Bridge |
|---|---|---|---|---|---|
| 1 | ✅ `sessions/S01-agent-loop.md` | ✅ `lessons/src/S01-agent-loop.md` + `s01_agent_loop_toy.ipynb` | the loop is a `while` around a stateless API | weather-bot loop on a mock model | add a tool; cap output; break preservation |
| 2 | ✅ `sessions/S02-golden-evals.md` | ✅ `lessons/src/S02-golden-evals.md` + `s02_scripted_user_eval_toy.ipynb` | eval suite as measurement instrument | scripted user + naive/governed engines + checks | write a check from scratch; p50 plumbing |
| 3 | ⬜ skeleton | ✅ `lessons/src/S03-context-engineering.md` + `s03_context_engineering_toy.ipynb` | compaction & cache are invisible in prose | growing-conversation simulator: truncation vs summary vs pinning; watch a buried rule die (Governance Decay, hands-on) | measure rule-survival across a compaction boundary on the toy |
| 4 | ⬜ skeleton | ✅ `lessons/src/S04-structured-generation.md` + `s04_structured_generation_toy.ipynb` | schema-constrained generation | JSON-schema validator over mock outputs + retry-on-invalid loop | design the session-spec schema on paper; attack a draft spec |
| 5 | ⬜ skeleton | ✅ `lessons/src/S05-consent-gate.md` + `s05_consent_gate_toy.ipynb` | human-in-the-loop approval mechanics | gate (approve / edit / reject) over a fake spec, with violation semantics (abort lives in execution) | the abort-vs-degrade thought experiment that feeds D-08 |
| 6 | ⬜ skeleton | ✅ `lessons/src/S06-layered-detection.md` + `s06_layered_detection_toy.ipynb` | layered detection as data-driven policy | keyword-floor + classifier pipeline over fixture strings, with false-trigger counter | draft your red-team list against the toy before the real policy |
| 7 | ⬜ skeleton | ✅ `lessons/src/S07-repair-loop.md` + `s07_repair_loop_toy.ipynb` | bounded regeneration with a curated failure view | mock scorer fails first N attempts; regeneration loop capped at 3 | decide D-11 (what context a retry gets) on the toy first |
| 8 | ⬜ skeleton | ✅ `lessons/src/S08-observability-replay.md` + `s08_observability_replay_toy.ipynb` | spans, traces, deterministic replay | record a mock session to JSONL; replay it offline byte-identical; diff two replays | find the nondeterminism planted in the toy |
| 9 | ⬜ skeleton | ✅ `lessons/src/S09-evidence-reports.md` + `s09_evidence_report_toy.ipynb` | evidence reports for a depleted reader | generate a debrief from a fake transcript, with turn references | the 30-second review test: can you trust it without opening the raw log? |
| 10 | ⬜ skeleton | ✅ `lessons/src/S10-error-analysis.md` + `s10_error_analysis_toy.ipynb` | taxonomy from raw failures | cluster a pile of fake failure logs into categories | apply your taxonomy to the course's real failure list |
| 11 | ⬜ skeleton | ✅ `lessons/src/S11-budgets-routing.md` + `s11_budgets_routing_toy.ipynb` | policy-as-data routing & budgets | route table over fake phases; a misconfigured route refuses to run | voice turn-taking latency math (doubles as interview material) |
| 12 | ⬜ skeleton | ✅ `lessons/src/S12-judge-calibration.md` + `s12_judge_calibration_toy.ipynb` | detection/false-positive measurement; judge agreement | seeded-defect game: 5 mutated + 5 clean mock transcripts, compute n/5 and FP n/5 | rehearse the hand-labeling protocol (label before seeing judge output) |
| 13 | ⬜ — by design | ✅ `lessons/src/S13-rebuild-from-memory.md` (protocol; no notebook) | none: the audit *is* the session | none — scaffolding the rebuild would defeat it | a blank template + timer protocol, that's all |
| 14 | ⬜ skeleton | ✅ `lessons/src/S14-ship-and-pilot.md` (protocol; no notebook) | assembly, not composition | none | dry-run the acceptance run end-to-end on a fixture before the real one |

## How a session gets its companion guide

When you start a session (or one sitting before), ask for its companion piece. The
contract for what gets written:

1. Concept must fit in ~20 minutes of reading and one diagram.
2. Toy must be runnable with zero network, zero keys, zero cost, and come from a
   different domain than the deliverable.
3. Bridge exercises must rehearse the real build's exact mechanical moves.
4. Nothing in it may be paste-able into an owned path.
5. Field guide lists the failure modes you'll actually meet, with their fixes.

The standalone lessons follow their own contract — see AGENTS.md ("Lesson format").
