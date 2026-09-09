# After-attempt rubric — exploratory, separate from course progress

Read only after saving the unaided attempt. No automatic assistant grounding or
manifest surface points to this file. It is inspectable course-owned teaching
material, not a secret test or psychometrically validated scale.

Score each dimension 0/1/2 and preserve the reason. The total 0–8 is an exploratory
observation. A correction after help does not become an unaided pass.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Call accounting | Misses unresolved/wrong ID or demands tools after ordinary text | Finds the error but loses call metadata or misses a requested result | Preserves assistant calls, matches all IDs, distinguishes ordinary text |
| Execution bound | Treats turn cap as timeout | Notices waiting without naming a concrete bound | Distinguishes model-turn cap from per-operation timeout/deadline |
| Checker blind spot | Equates refusal-only pass with usefulness | Notices a blind spot but cannot give a useful check | Explains selective/always-refusing tie and supplies a fixture-specific useful check |
| Interpretable delta | Claims one score proves general improvement | Names one control/limitation | Names controls and remaining single-run/model-variance limitation |

Immediate reference: `branches-18` lacks a result. Preserve the original two-call
assistant message, keep result `lookup-17`, append a `branches-18` tool result with
clearly made-up branch data, then continue. No tool result follows from the separate
ordinary explanation. Five turns do not time out an unresponsive operation.

The refusal check passes selective and refuses-everything. A check such as
`replies[0] == "Yes, available at Central."` distinguishes useful behavior for this
fixture, while rejecting valid paraphrases and failing to establish real inventory
truth. Keep the useful and refusal criteria as separate observations.

Delayed reference: preserve `sessions-31` and correct the mismatched result ID
`sessions-13` to `sessions-31`; in a real system first verify that the result belongs
to that call rather than blindly relabeling unrelated data. This fixture supplies
the intended session result. Ordinary entrance text introduces no tool obligation.
Use a timeout/deadline to bound waiting. Check the useful first reply (15:00 and 12
seats in this fixture) as well as the refusal second reply. Selective and
refuses-everything tie under the current refusal-only criterion.

For both variants, examples of controls include script, fixtures/tool outputs,
checker and model versions/settings, with the edited instruction identified. A
fixed user script removes user-side variation; a stochastic model may still vary.
Repeated runs and wider task coverage answer questions that one probe cannot.

Record variant/delay, unaided scores and reasoning, any help already used, then a
separate corrected explanation if desired. Do not copy this key into a pre-attempt
lesson scope or learner prediction field to make progress look complete.
