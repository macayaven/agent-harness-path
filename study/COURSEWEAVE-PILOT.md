# Optional S01/S02 CourseWeave pilot

The native course is independently usable: `uv sync --frozen`, open
`lessons/index.html`, and `uv run jupyter lab`. Notebooks are stdlib-only, zero
network, zero keys and zero cost. Public videos are optional streamed supporting
resources. The pilot adds a persistent Course assistant and explicit learner
records; it does not certify completion or replace the native lessons.

## Install the explicit local pilot artifact

This schema-v2 branch requires the coherent pilot wheel with `launch
--kernel-python` support. The earlier v0.1.0 release/source sibling is not a
compatible fallback. Obtain the verified wheel from the platform pilot build and
substitute its **absolute path** below. These are installation examples, not a
claim that a final wheel has already been built by this course commit.

```bash
uv venv --python 3.11 /absolute/path/courseweave-pilot-env
uv pip install --python /absolute/path/courseweave-pilot-env/bin/python /absolute/path/courseweave-pilot.whl
uv sync --frozen
/absolute/path/courseweave-pilot-env/bin/python -I scripts/verify_courseweave.py
./scripts/courseweave --platform-python /absolute/path/courseweave-pilot-env/bin/python --state-dir /absolute/path/pilot-learner-state
```

The launcher accepts `--platform-python` and `--state-dir` (both required),
`--kernel-python` (defaults to this course's `.venv/bin/python`), and `--port`
(default 8765). It prints the three selected paths and invokes:

```text
<platform-python> -m courseweave launch --course-root <this-course> --kernel-python <course-python> --state-dir <external-state> --port <port>
```

Keep interpreter paths pointing through their venv `bin/python`; resolving their
symlinks to a base interpreter loses environment selection. The platform hosts
CourseWeave/Jupyter and provider integration. The course interpreter runs notebooks
and has no CourseWeave/provider dependency requirement. Learner state belongs in a
separate external directory, never inside the course or at an ancestor of it.
The launcher fails clearly if the artifact lacks the explicit kernel interface;
it never discovers a sibling checkout, searches PATH for another CourseWeave,
reads lab commands or installs software on launch. Final installed-artifact
acceptance must verify the **actual** kernel executable and credential stripping;
printing a path alone is not isolation proof.

No provider credential is read by this course adapter. Configure an optional
provider through the platform's documented custody path. CourseWeave's session-only
raw conversation policy concerns its own storage; an upstream gateway/provider
can log prompts and responses. Review its retention settings before using Share.
For the prepared local gateway, controller checks on 2026-09-09 reported request/
response logging; verify that mutable setup at final acceptance. Use only public
toy material in exploratory probes. The lesson text and optional one-answer Share
have different scopes; inspect and clear lesson scope when appropriate.

## First route and actual contract

Start `s01/read` and open `lesson` at
`lessons/S01-agent-loop.html#the-theory-in-depth`. The optional `video` is in that
reading activity, with its Google Gemini Notebook attribution retained.

| Module/activity | Primary surface | Learner requirements | Formative checks |
|---|---|---|---|
| s01/read | lesson | s01-reading | none |
| s01/notebook | notebook | s01-prediction, s01-attempt, s01-observation | none |
| s01/self-check | self-check | s01-reflection | call-accounting, iteration-vs-time |
| s01/lab (optional) | lab-guide | s01-lab-evidence | none |
| s02/read | lesson | s02-reading | none |
| s02/notebook | notebook | s02-prediction, s02-attempt, s02-observation | none |
| s02/self-check | self-check | s02-reflection | refusal-only, stub-vs-measurement, controlled-comparison |
| s02/lab (optional) | lab-guide | s02-lab-evidence | none |

Only the same-activity prediction record gates optional notebook teacher help.
An experience label grants no authority. Saved text records show the learner's
own work, not its correctness. The optional lab evidence record requires a labeled
file or URL reference plus the learner's explanation. A check attempt gives deterministic formative
feedback, separately from the reflection requirement. Profile suggestions require
optional learning-memory consent and deliberate acceptance; no course/workspace
proposal is authorized by this adapter.

Notebook `s01/notebook` opens `notebooks/s01_agent_loop_toy.ipynb`; its first
selected cell is `5aa42bcc` (happy-path prediction). Other selected cells are
`69a77fc3`, `fd87655a`, `15f7e677`, `s01-attempt-prompt`, `s01-attempt-code`.
S02 selects `6e110918`, `9bdffa54`, `d3af51d7`, `s02-attempt-prompt`,
`s02-attempt-code` in `notebooks/s02_scripted_user_eval_toy.ipynb`.
Existing experiment cells remain in the full native notebook and run in order;
they are not selected as pre-attempt grounding. No old cell ID/source/metadata/
output is altered. Added boundary notes qualify the earlier simplified transfer
bullets without rewriting their original cells.

Self-check reopens the same module's HTML at `#self-check`. Native references use
keyboard-accessible details disclosures, excluded from explicit lesson grounding.
No independent transfer rubric is in the manifest. S03–S14 remain available as
optional native activities with limited guidance; their dated material has not
been newly reviewed by this pilot. S13/S14 use observer-only teacher access in the limited-guidance adapter.

## Optional hard lab commands

The exact terminal labels are “Copy S01 replay command (learner implementation)”,
“Copy S01 live command (optional network and cost)” and the corresponding S02
labels. Surface IDs are `replay-command` and `live-command`, cwd `.`. The command
vectors produce:

```bash
uv run python labs/run.py --session s01 --replay
uv run python labs/run.py --session s01 --live
uv run python labs/run.py --session s02 --replay
uv run python labs/run.py --session s02 --live
```

These target the learner implementation. They are **copy-only** in CourseWeave;
run them deliberately after reading the actual lab protocol. An unfinished learner
implementation can fail. S02's six-task denominator includes governors not built
at that stage; explain those failures. Live mode is optional, needs the lab's
explicit endpoint/credential/model setup, may incur cost and is never run in CI.
`uv run python labs/run.py --all --replay` verifies the committed reference and
cassettes; it does not prove the learner's solution works.

Start the exploratory interaction/learning protocol at
[FIRST-TEST.md](FIRST-TEST.md). Its independent immediate and delayed transfer
fixtures and separate rubric work without CourseWeave. No learning efficacy has
been measured by authoring these materials.
