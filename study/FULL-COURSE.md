# Studying and giving feedback on S01–S14

The public starting point is this clone: follow the root README, run
`uv sync --frozen`, open [the course index](../sessions/index.html) in Cursor,
and run the marimo notebooks with `uv run marimo edit sessions/sNN-slug/toy.py`.

Keep learner work on nonsynced local storage outside the Git checkout. Copy an
edited notebook before a clean clone, branch switch or version change.

## The twelve-session route

For every S01–S12 module, follow **Read and trace the theory → Notebook: predict,
attempt, observe → Self-check and explain**. Course content is ordered by session.
Each of those twelve sessions has three required activities (read, notebook,
self-check), so 36 activities, not twelve automatically graded completions.
The twelve sessions accumulate **one** `cafe/` package
(`loop → evals → context → schema → consent → detect → repair → trace → report →
taxonomy → routing → judge`), not twelve separate toys.

Read the objectives and use the diagram. Write a prediction before the relevant
notebook result, attempt the authored work yourself and compare one observation
with the prediction. Save the notebook outside this checkout so a clean clone
does not eat your predictions.
Notebooks are marimo files that run **live** against your own OpenAI-compatible
endpoint through the single `cafe/` seam (`CAFE_BASE_URL`, `CAFE_API_KEY`,
`CAFE_MODEL`; smoke-test with `uv run python -m cafe.doctor`). Only CI is offline,
via `COURSE_MODE=stub`. Running all cells demonstrates execution; empty attempt
skeletons and reference-label scores do not become your independent work.

| Session | A useful feedback focus |
| --- | --- |
| S01 | Did message/call identity and the separate turn/time bounds become clear? |
| S02 | Did the checker’s usefulness blind spot and simulated metrics become clear? |
| S03 | Could you distinguish omitted rules from present-but-ignored rules? |
| S04 | Did you try the retry/schema work and label briefs before strict outputs? |
| S05 | Could you trace approved data through rejection, edits and degradation? |
| S06 | Could you explain both error directions at a chosen threshold? |
| S07 | Did the feedback show why repair differs from repeated sampling? |
| S08 | Could you distinguish matching, exhaustion and host nondeterminism? |
| S09 | Did the two validator attempts expose fabrication and omission separately? |
| S10 | Did your taxonomy and guard grow from traces, not the reference labels? |
| S11 | Could you explain both budget gates and the content-routing boundary? |
| S12 | Did you preserve blinded labels and inspect clean/defective strata? |
| S13, optional | Were the prerequisites, safe scratch setup and unaided boundary usable? |
| S14, optional | Was the criteria/holdout/pilot/evidence sequence understandable? |

Attempt the foldable self-checks in the lesson HTML before revealing answers.
Record your correction in your own words; a correct selection does not replace a
reflection or certify mastery.

## Assistance and optional material

The Cursor companion stays on the same chat across lesson, notebook, and lab.
Ground it with `@sessions/sNN-slug/companion.md` plus the HTML lesson you are on
(`docs/COMPANION.md`). Do not paste a whole notebook. Predict-first cells stay
empty until you write them. The assistant has no authority to complete activities
or execute copied commands. Authored hints and foldable self-checks live in the
lesson HTML and work without a provider. Record assistance and premature answer
exposure honestly.

The videos are optional Google Gemini Notebook previews/reviews, and may lag the
lesson. Hard labs remain optional and build a trivia host with their own scopes,
prerequisites and replay/live distinctions. S06's hard lab is pub-quiz policy only;
S09's real round stays private; S12's replay does not perform critic calibration.
Reference replay and real-provider evidence are different categories.

S13/S14 have **no notebooks**. Read their prerequisites before choosing to perform
them. Use [S13's audit card](S13-AUDIT.md), [S14's cold-run card](S14-RUNS.md),
[pilot-page prompts](S14-PILOT-PAGE.md) and [human-pilot card](S14-PILOT.md) together
with the original lessons. During unaided work, close the assistant chat; return
to review only after the sitting ends and evidence is saved.
Deferring either protocol does not block S01–S12. Record planned and performed
activities separately. No software test manufactures a rebuild, elapsed week,
consenting person, publication or learning result.

## Feedback that helps

Copy [the observation CSV](PILOT-OBSERVATIONS.template.csv) into your own nonsynced
notes folder outside the repository. Use the session/activity as `task_id`; the
template is optional. It remains local unless you choose to copy a short,
sanitized observation into the one-click
[course feedback form](https://github.com/macayaven/agent-harness-path/issues/new?template=course-feedback.yml).
The course does not send the CSV, notebooks, chat or telemetry to GitHub. Review
the issue preview and submit only when you intend to make it public.
For each friction point, record what you tried, expected and observed, how you
recovered, and whether the assistant/hint was grounded or exposed a solution too
soon. Keep the original prediction/attempt, your correction and actual study time.
Mark unobserved usage/cost and missing results as unavailable, never zero.

Do not include credentials, raw-chat exports or real participant/session content.
A short paraphrase normally suffices. Do not publish private project names or
machine-specific paths, full notebooks or work products. Include a public
session/activity or repository-relative path, the minimum reproduction, expected
and observed behavior, and any recovery. Record skipped material as skipped and
partial work as partial. Your observations can identify defects and guide course
improvement; they do not establish general learning gains or readiness.

The earlier [FIRST-TEST.md](FIRST-TEST.md) and immediate/delayed transfer fixtures
remain a separate optional S01/S02 study. Their answer keys stay outside the
lesson HTML. They are not substitutes for studying and reporting on the later
sessions.
