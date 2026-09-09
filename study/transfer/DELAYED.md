# Delayed unaided transfer — museum tickets

Use 24–72 hours after the immediate task and record the actual elapsed delay.
Immediate feedback may already have been read **after saving the immediate
attempt**. Record whether and when you read it. The delayed observation includes
possible immediate-feedback effects; it does not isolate course-only retention.

Work without consulting the assistant, hints, scoring dimensions or either key
during this attempt. Do not open the delayed key before saving your answer. If
it was exposed earlier, record that prior assistance in `help_used` and notes and
do not label the delayed score unaided. This is a written option, not a reminder
or scheduled automation. Different wording is not proven equivalent difficulty.
Plan 8–12 minutes; missing results stay missing.

Open `fixtures.json` at `delayed`, or run:

```bash
python study/transfer/attempt.py --variant delayed
```

1. Diagnose the exact message bookkeeping problem in the `list_sessions` transcript
   and repair it while preserving the assistant call message. Explain whether the
   separate ordinary entrance explanation needs any result.
2. A ticket operation never returns. Explain what a model-turn budget bounds and
   name another bound for this case.
3. Examine the two fixed user questions and the three sets of replies, shown in a
   different order from the immediate task. Predict the current second-reply
   check's outcomes. Supply both a refusal check and a useful-seat-answer check;
   explain one boundary of your code or written criterion.
4. Distinguish fixing the scripted user from fixing model randomness. Name controls
   and a remaining limitation before interpreting a one-run score increase.

## After saving the delayed attempt

Save the complete answer, reasoning and actual time. Only then open the
[general scoring dimensions](RUBRIC.md) and the [delayed reference](DELAYED-KEY.md).
Keep any assisted correction separate from the saved attempt. Record immediate
feedback history and any premature delayed-key exposure as described above; an
exposed answer cannot later become an unaided result. A matching ID is bookkeeping
evidence, not proof of truthful seat data or authorized execution.
