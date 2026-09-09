# Immediate reference — open only after saving the immediate attempt

First save your complete unaided library attempt, reasoning and actual time.
Only then read this reference and the [general scoring dimensions](RUBRIC.md).
Immediate feedback is allowed at this point, before the optional delay. Keep
corrections separate and record whether and when you read this feedback; later
delayed observations may reflect it as well as the course and practice.

Immediate reference: `branches-18` lacks a result. Preserve the original two-call
assistant message, keep result `lookup-17`, append a `branches-18` tool result with
clearly made-up branch data, then continue. No tool result follows from the separate
ordinary explanation. Five turns do not time out an unresponsive operation.

The refusal check passes selective and refuses-everything. A check such as
`replies[0] == "Yes, available at Central."` distinguishes useful behavior for this
fixture, while rejecting valid paraphrases and failing to establish real inventory
truth. Keep the useful and refusal criteria as separate observations.

Examples of controls include script, fixtures/tool outputs,
checker and model versions/settings, with the edited instruction identified. A
fixed user script removes user-side variation; a stochastic model may still vary.
Repeated runs and wider task coverage answer questions that one probe cannot.

Keep the original unaided result. Mark any help used before it was saved; feedback
or corrections afterward do not replace that original result. This file contains
only the immediate reference. The delayed key must remain unopened until after
its own saved attempt; accidental early exposure is prior assistance and must be
reported rather than counted as an unaided delayed result.
