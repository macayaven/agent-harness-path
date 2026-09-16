# Full-course student pilot acceptance — 2026-09-13

This is a maintainer-recorded acceptance of the exact local pilot listed below. It supports the documented macOS single-user student trial. It is not a claim that the future public release or another wheel with the same version has been tested. The [machine-readable record](student-pilot-2026-09-13.json) contains public prompts, observed live answers and per-module results without private machine paths, endpoint addresses, credentials or student data.

## Tested inputs

| Input | Identity |
| --- | --- |
| Course source | `585b45eb3186404b8445cae64126ab9929c22b87` |
| Course archive SHA256 | `0bc19b9452187372314a1337c46e64a04c7152aeddc09f6859c5ed8b2b93e562` |
| Platform source | `f1134590cced78a6bd5202062178eba1f1edc0ae` |
| Platform wheel SHA256 | `1bd186b07af5d3a89b6c77dbce1cccfb3cef1fe76f91aa40dec8e2c4f361e923` |
| Verification source | `46b2b45e6f60c3e6a0121343836e4d849886cba2` |

The tested wheel still carries metadata version `0.1.0`; the publicly released CourseWeave `v0.1.0` wheel is a different, incompatible artifact. A distinct public version and an exact-artifact release check are required before distributing this integration. See [release preparation](../RELEASING.md) and [the CourseWeave setup boundary](../../study/COURSEWEAVE-PILOT.md).

## Per-module evidence

Every row includes its installed reader, native self-check disclosures, authored hints, optional references and activity navigation. Notebook rows include real Jupyter Run All, edits, saves, preserved cell identities and zero unhandled notebook error outputs.

| Module | Guided checks / options | Native self-checks | Executed notebook code cells | Practical protocol |
| --- | ---: | ---: | ---: | --- |
| S01 — The agent loop | 2 / 6 | 4 | 8 | — |
| S02 — Golden sets and baselines | 3 / 9 | 4 | 7 | — |
| S03 — Context engineering | 2 / 6 | 4 | 15 | — |
| S04 — Structured generation | 3 / 9 | 4 | 14 | — |
| S05 — Consent gates | 2 / 6 | 4 | 14 | — |
| S06 — Layered detection | 2 / 6 | 4 | 16 | — |
| S07 — Bounded repair | 2 / 6 | 4 | 14 | — |
| S08 — Observability and replay | 3 / 9 | 4 | 15 | — |
| S09 — Evidence reports | 3 / 9 | 4 | 13 | — |
| S10 — Error analysis | 2 / 6 | 4 | 10 | — |
| S11 — Budgets and routing | 3 / 9 | 4 | 14 | — |
| S12 — Judge calibration | 3 / 9 | 4 | 14 | — |
| S13 — Closed-book rebuild audit | 2 / 6 | 4 | No notebook | Optional; interactions and assistance gates verified |
| S14 — Ship and pilot | 3 / 9 | 4 | No notebook | Optional; interactions and assistance gates verified |

Seventeen static diagrams were inspected, including the study plan and multiple diagrams in S08/S14. Native navigation exercised 108 local links across sixteen HTML documents. Guided checks exercised all 105 options of 35 checks with their authored feedback. The twelve notebook sources remain output free; their 154 code cells executed in disposable study copies. Four early-session attempt cells supplement 277 protected original cells.

## Assistant, records and recovery

The installed synthetic journey retained one conversation across fourteen modules and seventeen provider requests. It exercised explicit lesson scope, deliberate retention and replacement of an earlier excerpt, one-answer notebook sharing, all twelve prediction gates, and exactly 36 required activity records. A prediction or check answer alone did not complete its activity.

S13 audit and S14 cold acceptance/human-pilot activities disabled discussion and sharing and made no provider calls. Both review activities required a true saved attestation after a false one remained blocked. Acceptance used synthetic records; it did not perform these real-world activities.

Fresh setup and repeat setup preserved existing work. Records and all twelve edited notebooks survived restart; export reproduced records; reset removed records while preserving notebooks. The original student workspace and rollback package remained unchanged. Owned services and disposable homes were cleaned, and credential scans passed. The course kernel had no provider key, browser capability or Jupyter token. Its loopback TCP was authenticated but unencrypted.

Three separate real-provider questions used public course material: S03 pinning versus attention, S11 estimated versus actual costs, and an explicitly typed synthetic S14 draft contradiction. The selected HTML/Markdown scopes and exact activity coordinates were confirmed. A separate automated reviewer read the answers against the course and accepted their narrow grounding; durable state did not change. This was text-only evidence. Workspace Share has separate synthetic coverage.

## Review and limits

The bounded independent automated review resolved practical-suite selection, ambiguous retained-scope labels, asynchronous navigation order, early native-link interaction and overstated budget wording. No substantive finding remained in that review. The full installed run reported 154 known Jupyter `No active debugger session` diagnostics and no other page errors or notebook error outputs.

The platform repository retains the verification implementation (`scripts/verify_student_release.mjs`, shared navigation/kernel/process helpers) and the detailed acceptance/review documents. The machine-readable record here is a deliberately bounded public summary; raw machine logs are not published as learner evidence. Reproduce source contracts with the course checks in [CONTRIBUTING](../../CONTRIBUTING.md), and run the platform’s exact-package gates before attaching a newly built student distribution.

These checks do not establish learning gains, actual human pilot work, live tool support, paid/live lab behavior, general production readiness or a complete screen-reader audit. Optional video URLs were checked and bound, but every video was not played. Three DOI-linked publishers returned HTTP 403; their access remains outside the local course guarantee. Teacher/author workflows were outside this student trial.
