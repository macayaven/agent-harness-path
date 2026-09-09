# First exploratory test — Carlos can start alone

This is an authored protocol, not a completed user study or evidence of efficacy.
Use the native course immediately, or the explicit pilot installation described in
[COURSEWEAVE-PILOT.md](COURSEWEAVE-PILOT.md). No participants need recruiting.
Keep observations outside the course checkout; copy the CSV template there.

## 1. Ten to fifteen minutes: interaction route, not a learning score

Start S01/read, open the lesson, inspect the static diagram, and optionally choose
Use this lesson. Ask a question if a provider is configured. Continue to the
notebook; verify that the notebook prediction prompt is visible and optional help
waits for your prediction record. Save a real brief prediction, then open the
notebook and inspect an existing predict-first cell. Navigate to self-check,
attempt a formative choice, and deliberately open its native reference. Confirm
that the same assistant conversation remains, including after closing/reopening
the guide. Open the optional lab and copy its replay command into a note; copying
must not execute it. Observe state outside the checkout and the course kernel
interpreter. Report an unavailable provider honestly; static hints still work.

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
| Weather failure | Explain where the fragile weather error appears. Static hint: follow dispatch's return value into the messages list; distinguish continuation from successful retrieval. | Explain your attempted trace to the Course assistant and ask for one next question about your uncertainty. |
| Fitness evidence | Explain whether the table's equal p50 values show equal speed. Static hint: find where drive creates each latency value and read the column label. | Give your attempted interpretation to the same assistant and ask for a targeted hint, not the final explanation. |

First tester: static weather, adapted fitness. If you repeat with another tester,
reverse which practice gets which help (adapted weather, static fitness). If only
Carlos repeats, report prior exposure. Within-person practice, different concepts,
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

Use [transfer/IMMEDIATE.md](transfer/IMMEDIATE.md) unaided, then the separate rubric.
Use [transfer/DELAYED.md](transfer/DELAYED.md) 24–72 hours later if desired, before
reviewing the immediate key. Record actual delay and missing results as missing.
The fixtures and starter use only Python's standard library with no course runtime
or model. The rubric is separate from the CourseWeave manifest and UI progress.

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
next improvement. After seeing actual calls, Carlos should record an acceptable
latency threshold before deciding whether to repeat. No statistical efficacy,
market demand, mastery or causal advantage follows from one tester. Missing delayed
results and known prior knowledge must remain visible in any report.
