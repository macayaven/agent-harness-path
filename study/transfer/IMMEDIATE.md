# Immediate unaided transfer — library reservations

Do this after S01/S02, before looking at the separate RUBRIC.md. This is a new toy
domain, not a real library service. Plan 8–12 minutes, but record actual time. Use
paper or a local copy of `attempt.py` and `fixtures.json`. No CourseWeave or model
is needed. Leave the assistant closed and don't read the delayed variant yet.

Open `fixtures.json` at `immediate`, or run:

```bash
python study/transfer/attempt.py --variant immediate
```

A library assistant requests `find_book` (ID `lookup-17`) and `list_branches`
(ID `branches-18`) in one assistant message. Only the book result is present,
followed by an ordinary assistant answer. The file gives the exact message objects
and a separate opening-hours explanation with no tool calls.

1. Identify the precise unresolved obligation. Explain whether the separate
   ordinary explanation needs a tool result.
2. Sketch a repaired first transcript, preserving the original assistant call
   message and matching results by ID. Use a made-up branch result labeled fixture
   data. You are showing bookkeeping, not querying a library.
3. The loop allows five model turns. `list_branches` never returns. Does the turn
   budget alone ensure termination? Name an additional bound and what it limits.

Now inspect the fixed two-turn user script and the three fixture assistants.
The current check looks **only** at the second reply and passes if it equals
`I can only help with library reservations.`

4. Predict which assistants this check passes. What conclusion does it support,
   and what useful behavior could it miss?
5. Write one deterministic, task-specific useful-answer assertion that the
   selective assistant passes and the refuses-everything assistant fails. Name a
   boundary of your proposed assertion.
6. An instruction edit raises the score in one real-model run. Name at least two
   controls to hold fixed or report, and one limitation of that single run.

Save the unaided reasoning **before** checking it. Afterward compare with the
separate rubric and retain corrections separately. Hint-assisted corrections must
not replace the original unaided result. If you used any help, mark that fact.
