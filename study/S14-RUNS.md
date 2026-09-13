# S14 — cold acceptance and holdout card

Follow the [authored S14 protocol](../lessons/S14-ship-and-pilot.html#the-protocol) on a non-trivial system you own, or your completed trivia host. This session is optional and has no notebook. Its prerequisites remain S01–S13 vocabulary and mechanisms plus the actual system and evidence instruments. Reading the card does not establish those prerequisites.

## Freeze before running

- Write dated pass criteria that another person could apply without your explanation.
- Freeze two previously unseen scenarios: the acceptance fixture and a **separate untouched holdout** for the final gate. Keep the holdout unopened during diagnosis and fixing. Do not share it with the assistant.
- Record the target version, fixture identities, criteria and clean-state setup in your own local project. A pointer in the guide is a record, not proof the run occurred.

## Run without steering

Start cold, with clean state and traces enabled. No warmup, narration or assistant steering. The **Cold acceptance and untouched holdout** activity disables provider calls, sharing and proposals. Run your system yourself; copied commands never execute automatically.

If acceptance fails, retain the failure trace and original criteria, amend the system and rerun. The diagnosed fixture is now a tuning case. Its green rerun is regression evidence; it does not become unseen again. The final gate is one cold run on the still-untouched holdout. If that gate fails, record the failure and stop claiming acceptance. Do not quietly recycle an exposed fixture as a new holdout.

The supplied trivia cassettes and reference suite are useful regression material. They are already published and do not supply new unseen acceptance scenarios for your own finished host.

For published-fixture regression on your completed trivia host, use
`uv run python labs/run.py --all --impl student --replay`. Confirm **`impl=student`**
in the report and inspect task results and skipped/not-implemented notices; an
exit code alone is insufficient. `--all` without `--impl student` runs the reference.
Neither reference smoke results nor student regression replay replaces your fresh
acceptance and untouched holdout.

## Save actual results

After the run, preserve target version, fixture/criteria identities, actual state setup, trace and eval references, stop reason, failures, fixes and outcome. Separate acceptance, tuning reruns and final holdout in your notes. Leave unperformed run records unsubmitted.

Continue in the authored order: write your pilot page, obtain the participant’s consent, then run the human pilot. For diagnosis between sittings, return to a permitted review activity only after the cold run ends and its evidence is saved. Do not confuse help fixing a system between runs with an unaided acceptance run.
