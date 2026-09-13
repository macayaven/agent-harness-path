# Course release runbook

This runbook publishes `macayaven/agent-harness-path`. Keep the course, its tag,
course archive and course issues in this repository. CourseWeave remains a
separate application with its own version, artifacts and release. The native
course is independently usable; the optional macOS bundle belongs only to the
CourseWeave v0.2.0 release.

The existing course v0.1.0 is a public tag without a GitHub Release. v0.2.0 is a
candidate until every applicable gate below passes and the maintainer deliberately
publishes it. Preparing this file does not create a tag or public asset.

## 1. Select the exact candidate

Use a dedicated clean checkout on nonsynced local storage. Verify the public
remote by URL rather than assuming its alias:

```sh
git remote -v
git branch --show-current
git status --short
course_remote=upstream
git remote get-url "$course_remote"
git fetch "$course_remote" --tags
git rev-parse "$course_remote/main"
git rev-parse v0.1.0
git log --oneline v0.1.0..HEAD
```

Use `origin` instead when that is the verified
`https://github.com/macayaven/agent-harness-path` remote. Review every change
since v0.1.0. Confirm generated HTML and diagrams, notebook preservation
receipts, course licenses/notices, learner documentation, feedback template and
public evidence are present. Search public text for credentials, raw chats/logs,
participant content, private hostnames and machine paths.

Keep the changelog under `Unreleased` and the v0.2.0 notes marked Draft during
candidate review. The platform license decision is separate and must not be
inferred from this course's split license.

## 2. Run the course gates

Install only from the committed lock and run the existing course contracts. Run
the available local Python before publication, then require the hosted Python
3.11 and 3.12 matrix on the exact final course commit.

```sh
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -v
for nb in notebooks/s*.ipynb; do
  uv run --frozen jupyter nbconvert --to notebook --execute --stdout "$nb" > /dev/null
done
uv run --frozen python lessons/build.py
git diff --exit-code -- lessons/*.html lessons/index.html
test -z "$(git status --porcelain --untracked-files=all -- lessons/)"
uv run --frozen python lessons/check_sota_urls.py
uv run --frozen python lessons/check_links.py
uv run --frozen python -m unittest labs/test_contracts.py
uv run --frozen python labs/run.py --all --replay
uv run --frozen python lessons/check_links.py --http
```

The HTTP check needs network access and treats some access-control/rate-limit
responses as warnings. Never run lab `--live` as a course release gate. Replay
checks the committed reference and cassettes; it does not prove a learner's
implementation or arbitrary provider. Executed notebooks do not certify
learning, accessibility, teacher workflows or production readiness.

If Mermaid inputs, alternatives, renderer inputs or the diagram receipt changed,
run the pinned diagram workflow from `CONTRIBUTING.md` on the recorded renderer
and font host and inspect every changed SVG:

```sh
uv run --frozen --group diagrams python lessons/render_diagrams.py
uv run --frozen --group diagrams python lessons/render_diagrams.py --check
uv run --frozen python lessons/build.py
git diff --exit-code -- lessons/*.html lessons/index.html
```

## 3. Prove optional CourseWeave compatibility

This gate is required only for a release note that advertises the guided bundle.
Build the bundle from the selected clean course and platform commits using the
CourseWeave release runbook. Its embedded course tar must have
`pyproject.toml` and `courseweave.json` at archive root and must record this exact
course commit and version 0.2.0.

The existing platform `test:e2e:installed-adapter` command is a historical
S01/S02 regression fixture pinned to course commit
`776f64ae8ae5d1e4fceca3a93de89b9ebf446727`. Changing
`COURSEWEAVE_ADAPTER_ROOT` does not turn it into full-course acceptance.

Use the portable platform verifier for the current S01–S14 bundle. Run it from a
clean CourseWeave checkout with Node 22. Keep release, evidence and test-root
paths on nonsynced local storage and outside one another as required by its help:

```sh
node --experimental-transform-types scripts/verify_student_release.mjs \
  /absolute/path/to/CourseWeave\ Student\ Pilot\ v0.2.0 \
  /absolute/path/to/disposable-evidence \
  --test-root /absolute/path/to/disposable-root --no-live
```

Omitting live flags is also synthetic-only. The run must identify the candidate
wheel/course hashes and cover all fourteen readers, twelve notebook executions,
optional protocols, navigation, authored checks/hints, explicit scope/share,
restart/export/reset, preservation, credential scanning, kernel isolation and
process cleanup. A separately authorized `--live-only` run requires one explicit
environment-configured provider and proves only its bounded text observations.
Teacher/Author work remains outside the full-course student claim.

## 4. Freeze and review the release commit

The candidate metadata already uses 0.2.0. Verify it rather than bumping it again:

```sh
uv lock --check
uv run --frozen python - <<'PY'
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
locked = tomllib.loads(Path("uv.lock").read_text())["package"]
assert project["version"] == "0.2.0"
assert any(
    item["name"] == "agent-harness-path" and item["version"] == "0.2.0"
    for item in locked
)
PY
git status --short
```

After local gates and review pass:

1. Move the complete entries from `Unreleased` to
   `0.2.0 — YYYY-MM-DD`, leaving a new empty `Unreleased` heading.
2. Remove the Draft warning from `docs/releases/v0.2.0.md`, add the same date,
   and replace candidate/public-availability wording only with observed facts.
3. Re-run the documentation, generated HTML/link and version checks affected by
   that edit.
4. Commit the freeze, confirm a clean tree, push through a reviewed pull request,
   and require the repository `verify` workflow to pass on the resulting exact
   `main` commit. Inspect merge/squash differences and rerun affected checks.
5. Record `git rev-parse HEAD` and the matching hosted workflow before tagging.

Do not amend a candidate after recording evidence. A correction creates a new
candidate and invalidates affected artifact checks.

## 5. Tag and build course assets

Create the annotated tag only from the clean reviewed commit:

```sh
git status --short
git rev-parse HEAD
git tag -a v0.2.0 -m "The Agent Harness Path v0.2.0"
git show --no-patch --decorate v0.2.0
```

Build the optional course release archive from the tag in a new local directory:

```sh
course_release_root=$(mktemp -d)
git archive --format=tar.gz --prefix=agent-harness-path-v0.2.0/ \
  --output="$course_release_root/agent-harness-path-v0.2.0.tar.gz" v0.2.0
(cd "$course_release_root" && shasum -a 256 \
  agent-harness-path-v0.2.0.tar.gz > SHA256SUMS)
tar -tzf "$course_release_root/agent-harness-path-v0.2.0.tar.gz" | head
(cd "$course_release_root" && shasum -a 256 --check SHA256SUMS)
```

GitHub also provides source archives automatically. This explicit archive keeps
the course's existing LFS-pointer policy; lesson videos continue to stream from
the documented public bucket. Do not attach a CourseWeave wheel or macOS student
bundle to the course release. The platform runbook independently creates its
root-layout course tar from the selected commit for embedding in the CourseWeave
bundle.

## 6. Publish and verify deliberately

Push the annotated tag only after reviewing the exact commit, notes, archive and
checksums. Create the course GitHub Release from
`docs/releases/v0.2.0.md` and attach only the reviewed course assets. Keep v0.1.0
available.

After publication, verify from fresh nonsynced locations:

```sh
git clone --branch v0.2.0 --single-branch \
  https://github.com/macayaven/agent-harness-path.git agent-harness-path-v0.2.0-smoke
cd agent-harness-path-v0.2.0-smoke
uv sync --frozen
uv run --frozen jupyter nbconvert --to notebook --execute --stdout \
  notebooks/s01_agent_loop_toy.ipynb > /dev/null
```

Open `lessons/index.html` and the one-click course-feedback form in the rendered
public README; verify the form fields and label without submitting fabricated
feedback. Separately download the CourseWeave-owned bundle and `SHA256SUMS`,
require the named archive to report `OK`, then follow its README through
provider-off first setup. A local candidate does not prove the public URL.

Only after the public bytes pass those checks may the course and platform notes
describe them as available. Public evidence must identify exact commits, hashes,
commands and limitations without private paths, credentials, participant data or
raw logs.

## Migration and rollback

Use a fresh clone for v0.2.0. Copy learner-owned notebooks, notes and work output
into a separate local folder after comparing them with the new blank sources. Do
not overwrite the new checkout.

The CourseWeave v0.2.0 bundle selects a fresh versioned study home. Keep an
earlier S01/S02 or schema-v1 workspace until the new copy and records are
confirmed; no automatic migration is claimed. Returning to the native course
does not rewrite CourseWeave state.

To revisit course v0.1.0 without resetting current work:

```sh
git worktree add ../agent-harness-path-v0.1.0 v0.1.0
cd ../agent-harness-path-v0.1.0
uv sync --frozen
```

Application rollback is separate and must use the application version and state
directory documented as compatible. Returning the course tag does not downgrade
CourseWeave, and returning CourseWeave does not replace course or learner files.
