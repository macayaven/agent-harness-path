# Full-course CourseWeave student pilot

The native course is independently usable: `uv sync --frozen`, open
`lessons/index.html`, and `uv run jupyter lab`. Notebooks are stdlib-only, zero
network, zero keys and zero cost. Public videos are optional streamed supporting
resources. The pilot adds a persistent Course assistant and explicit learner
records; it does not certify completion or replace the native lessons.

## Public availability

The course and CourseWeave are separate releases. Their v0.2.0 candidates and
the CourseWeave-owned macOS student bundle are prepared but **not published
yet**. Public CourseWeave v0.1.0 cannot load this schema-v2 manifest. Until the
[CourseWeave v0.2.0 release page](https://github.com/macayaven/courseweave/releases/tag/v0.2.0)
lists and verifies the named bundle and checksum file, use the native route.

## Install the macOS bundle after publication

You need macOS, internet access for the first setup, and
[uv](https://docs.astral.sh/uv/getting-started/installation/). Change Terminal
to a nonsynced local download folder and run:

```sh
curl -fLO https://github.com/macayaven/courseweave/releases/download/v0.2.0/agent-harness-path-courseweave-0.2.0-macos.tar.gz
curl -fLO https://github.com/macayaven/courseweave/releases/download/v0.2.0/SHA256SUMS
shasum -a 256 --check SHA256SUMS --ignore-missing | grep -F 'agent-harness-path-courseweave-0.2.0-macos.tar.gz: OK'
tar -xzf agent-harness-path-courseweave-0.2.0-macos.tar.gz
cd "CourseWeave Student Pilot v0.2.0"
./"Start Course.command" --no-provider
```

Continue only when the checksum command reports the named archive as `OK`. The
archive expands to one top-level `CourseWeave Student Pilot v0.2.0` folder. Its
seven files contain the exact application wheel, course archive and runtime
constraints selected for the release. The launcher builds separate application
and course interpreters, and the notebook interpreter receives no provider key.
It does not discover a sibling checkout, another CourseWeave installation or a
private receipt.

First start creates the versioned study home
`~/Library/Application Support/CourseWeave/Agent Harness Path v0.2.0`. Do not
point it at an earlier S01/S02 workspace and do not delete that workspace after
the new route opens. A different course edition is refused rather than merged.
There is no automatic state migration. Learner-edited notebooks, progress notes
and experiment output remain learner-owned files; returning to the native course
or an older CourseWeave environment does not rewrite them.

The assistant is off by default, including when inherited API-key variables
exist. For one deliberate interactive launch, use `--provider openai --model
YOUR_OPENAI_MODEL` or the corresponding `anthropic` command; the launcher asks
for the key with hidden input. A credential manager may inject the selected
provider/model/key variables for `--provider-env`. No `.env` file is loaded and
keys never belong in arguments, course files, notebooks, feedback or evidence.
An upstream gateway/provider can log prompts and responses, so review its
retention before using Share. The accepted bundle profile is text-only; one live
result does not establish tool or arbitrary-provider compatibility.

## Guided route and actual contract

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

S03–S12 use the same three required activities plus optional hard lab. Their
reading, prediction/attempt/observation and reflection prompts, objectives,
progressive hints and checks are specific to each lesson. The canonical manifest
defines **36 required activities** and all original twelve notebooks. Notebook
selection includes actual learner attempts and omits answer-bearing S10 guard
code and the S12 `TRUTH` key. All original cells remain in the full native notebooks.
The notebook source remains output-free; saved student answers belong in the
separate study copy. See [the full-course study guide](FULL-COURSE.md).

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
No independent transfer rubric is in the manifest. All lesson diagrams are static
SVG, including multiple diagrams in S08/S14. The dated readings stay in their
authored context; adding student guidance does not refresh their research claims.

S13 remains optional and notebook-free: preparation → unaided audit → review and
delayed-repeat planning. S14 remains optional and notebook-free: preparation →
cold acceptance/holdout → the learner's pilot page with optional critique → unaided
human pilot → evidence assembly/review. The unaided phases are observer-only,
with no provider calls, sharing, proposals or authored hints. Review requires an
explicit same-activity attestation that no unaided sitting is in progress.
Preparation does not authorize solving the audited core; S14 critique does not
authorize writing the learner's final words or inventing a participant.

Prerequisites remain in the lesson and activity overview. External project state,
consent, elapsed delay and actual human work are not automatically verified by a
course record. The packaged study copy is not a Git repository; a learner auditing
their completed lab first prepares a separate local versioned target as described
in [the audit card](S13-AUDIT.md). Neither audit nor shipping commands run on the
learner's behalf. S01–S12 is complete without either practical session.

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

For course publication, asset creation, migration and rollback boundaries, see
[the release runbook](../docs/RELEASING.md). A CourseWeave wheel belongs to the
application release and is never a course release asset.
