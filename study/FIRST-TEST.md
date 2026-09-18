# First self-guided exploratory test

This is an authored protocol, not a completed user study or evidence of efficacy.
Use this clone immediately. See [docs/COMPANION.md](../docs/COMPANION.md). No
participants need recruiting.
Keep observations outside the course checkout; copy the CSV template there.

## 1. Ten to fifteen minutes: interaction route, not a learning score

Start S01: open `sessions/s01-agent-loop/lesson.html`, inspect the static diagram, and
optionally `@sessions/s01-agent-loop/companion.md` in Cursor chat. Ask a question if a model is
configured. Open the notebook; verify that the prediction prompt is visible and
do not ask the companion to fill it first. Save a real brief prediction, then
inspect an existing predict-first cell. Navigate to self-check, attempt a
formative choice, and deliberately open its native reference. Confirm that the
same chat remains when you switch files. Open the optional lab and copy its
replay command into a note; copying must not execute it. Keep observations
outside the checkout. Report an unavailable model honestly; static hints in the
lesson still work.

This route discovers interaction problems. It is not the full course session and
does not test unaided learning. Do not manufacture progress records for a score.

## 2. Two practice conditions before transfer

Complete the S01/S02 reading and notebook attempts at your own pace. Active-study
estimates are 20–40 min reading, 30–60 min notebook, and 5–10 min self-check per
session; time the work, don't wait for a clock to validate a label. Optional lab
blocks are separate and may need multiple sittings.

For a small help comparison use these **coached practice items**, distinct from the
library/museum assessment. Write an attempt before any hint:

| Practice | Static condition prompt/hint | Adapted condition prompt |
|---|---|---|
| Weather failure | Explain where the fragile weather error appears. Static hint: follow dispatch's return value into the messages list; distinguish continuation from successful retrieval. | Explain your attempted trace to the Cursor companion and ask for one next question about your uncertainty. |
| Fitness evidence | Explain whether the table's equal p50 values show equal speed. Static hint: find where drive creates each latency value and read the column label. | Give your attempted interpretation to the same assistant and ask for a targeted hint, not the final explanation. |

For a first self-guided run, use static weather and adapted fitness. If another
tester repeats the protocol, reverse which practice gets which help (adapted
weather, static fitness). If the same learner repeats it, report prior exposure.
Within-person practice, different concepts,
order and tester knowledge confound the comparison: it can expose friction and
errors, not isolate a causal learning effect. Static means the ordinary course and
authored hints; adapted means optional help using the learner's supplied evidence.
Learning memory/optional suggestions can stay off throughout.

Before help, record the attempted reasoning. Afterward record whether the hint was
correct and grounded, whether it exposed the answer too early, and whether you can
explain the correction in your own words. Keep the original attempt. Record an
optional suggestion as offered/accepted/declined/not offered; accepting one is not
a success requirement.

## 3. Unaided transfer, then optional delayed check

1. Follow [transfer/IMMEDIATE.md](transfer/IMMEDIATE.md) unaided. Save the complete
   answer, reasoning and actual time before opening scoring material. Only after
   saving, use the general scoring dimensions and immediate reference linked at
   the end of that prompt. Immediate feedback is allowed then; keep corrections
   separate and record whether and when you read it.
2. If desired, follow [transfer/DELAYED.md](transfer/DELAYED.md) 24–72 hours later.
   Record actual delay and prior immediate feedback. Do not consult feedback,
   hints or the assistant during this attempt. Save the complete delayed answer
   before opening the scoring dimensions and delayed reference linked at its end.
   The delayed key must remain unopened until that saved attempt. Record any
   accidental early exposure as prior assistance in `help_used` and notes, rather
   than reporting an unaided delayed score.

Delayed observations include possible immediate-feedback effects as well as course
and practice exposure; they do not isolate retention from the course alone.
Missing results stay missing. The fixtures and starter use only Python's standard
library with no course runtime or model. General scoring dimensions and the two
separate references remain outside the lesson HTML.

## 4. What to record and when to continue

Use [PILOT-OBSERVATIONS.template.csv](PILOT-OBSERVATIONS.template.csv): condition and
order, task ID, reasoning plus 0–8 unaided rubric, assistance/hint level, factual
error or premature answer, own-words explanation, suggestion relevance/acceptance,
confusing or unnecessary actions, elapsed response time, and actual available token
usage/cost. Enter `unavailable` for missing usage/cost, never zero. No secrets, no
automatic raw-chat export; a short paraphrased observation normally suffices.

Predeclared continuation criteria: no known authority/privacy failure, no unresolved
material answer leakage, completion of the basic interaction route, and an accurate
explanation that adaptation and labs are optional. Pause expansion and fix any
failure in those areas. Use unaided reasoning, delay and friction to choose the
next improvement. After seeing actual calls, the learner should record an acceptable
latency threshold before deciding whether to repeat. No statistical efficacy,
market demand, mastery or causal advantage follows from one tester. Missing delayed
results and known prior knowledge must remain visible in any report.
