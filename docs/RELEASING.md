# Course release runbook

This runbook prepares releases of `macayaven/agent-harness-path`. Keep the course
in this repository: its public `v0.1.0` history, issues and clone URL already live
here. Release CourseWeave independently from `macayaven/courseweave`; course and
application versions do not need to match.

The existing `v0.1.0` course publication is a Git tag; no GitHub Release was
created for it. Creating a GitHub Release for `v0.2.0` is therefore an explicit
new publication step, not an automatic consequence of pushing the tag.

The recommended next course version is `v0.2.0` because the unreleased work adds
the optional lab spine, full-course schema-v2 adapter and study overlay while
preserving the S01–S14 curriculum. `v0.2.0` is only a proposal until the gates
below pass and a maintainer deliberately creates the tag and GitHub Release.

## Promotion boundary

The native course is releasable on its own. A clone plus `uv sync --frozen`,
`lessons/index.html` and `uv run jupyter lab` is the public user path.

CourseWeave is an optional interface. Its public `v0.1.0` wheel cannot load the
schema-v2 manifest. The compatible pilot wheel used in local acceptance is not a
public asset and has no public download URL. Until CourseWeave publishes a
compatible version, release notes must state that limitation and must not offer a
fabricated install command, sibling-checkout fallback or private asset location.
A future claim that CourseWeave is publicly installable requires an independent
platform release, an immutable wheel URL and checksum, and a fresh installed-wheel
acceptance against the course release candidate.

## 1. Prepare the candidate

Work from a dedicated branch or worktree and confirm the intended repository and
base. Do not release from learner state or a packaged study copy.

```bash
git remote -v
git branch --show-current
git status --short
course_remote=upstream # use origin in a clone where origin is the public GitHub remote
git remote get-url "$course_remote"
git fetch "$course_remote" --tags
git rev-parse "$course_remote/main"
git rev-parse v0.1.0
git log --oneline v0.1.0..HEAD
```

The prepared maintainer checkout names the canonical public remote `upstream`;
its `source-local` remote is read-only local provenance and is not a publication
target. A fresh public clone normally names GitHub `origin`, so choose the alias by
verified URL rather than assuming either name.

Review every change since `v0.1.0`. Confirm that generated HTML, diagram assets,
notebook preservation receipts, licenses, notices and public evidence are present.
Search new public text for credentials, raw logs, private hostnames, participant
content and machine-specific paths. The candidate must not change a learner's
external work or claim that an old CourseWeave workspace was migrated.

Keep `CHANGELOG.md` under `Unreleased` and the draft notes under
`docs/releases/v0.2.0.md` during review. Add the release date and move the entries
to a `0.2.0` heading only in the final release commit after all checks pass.

## 2. Run the course gates

Install only from the committed lock, then run the same portable contracts as CI
on Python 3.11 and 3.12. The two-version matrix is performed by GitHub Actions;
run the available local interpreter before publication and require the hosted
matrix to pass on the exact release commit.

```bash
uv sync --frozen
uv run python -m unittest discover -s tests -v
for nb in notebooks/s*.ipynb; do
  uv run jupyter nbconvert --to notebook --execute --stdout "$nb" > /dev/null
done
uv run python lessons/build.py
git diff --exit-code -- lessons/*.html lessons/index.html
uv run python lessons/check_sota_urls.py
uv run python lessons/check_links.py
uv run python -m unittest labs/test_contracts.py
uv run python labs/run.py --all --replay
uv run python lessons/check_links.py --http
```

Also fail the candidate if `git status --porcelain -- lessons/` shows an untracked
generated HTML file. Never run lab `--live` as a release gate. Replays prove the
committed reference/cassette contract; they do not prove a learner implementation
or arbitrary provider. Unit and notebook execution do not certify learning gains,
accessibility, teacher workflows or production readiness.

If Mermaid source, alternatives, renderer inputs or the diagram lock changed,
use the pinned optional diagram environment described in `CONTRIBUTING.md`, run
`lessons/render_diagrams.py --check` on the recorded renderer/font host, and
inspect every changed SVG. Cross-host byte identity is not a release claim.

For an explicitly supplied compatible CourseWeave candidate, run the installed
wheel check with the platform venv interpreter:

```bash
/absolute/path/courseweave-release-env/bin/python -I scripts/verify_courseweave.py
```

Then perform the platform-owned installed browser, provider and kernel-isolation
acceptance described in `study/COURSEWEAVE-PILOT.md`. Record the exact platform
commit, wheel digest and observations in the bounded verification receipt. This is
required for a CourseWeave compatibility claim, not for the native course release.

## 3. Freeze the release commit

After review and gates pass:

1. Set `[project].version` in `pyproject.toml` to `0.2.0`, run `uv lock`, and
   confirm the root `agent-harness-path` entry in `uv.lock` is also `0.2.0`.
2. Because the diagram freshness receipt includes the lock hash, run
   `uv run --group diagrams python lessons/render_diagrams.py`, then
   `uv run --group diagrams python lessons/render_diagrams.py --check`. Inspect
   the receipt diff and any SVG diff; a version-only lock change should not alter
   diagram appearance.
3. Change `CHANGELOG.md` from `Unreleased` to `0.2.0 — YYYY-MM-DD`, retaining a new
   empty `Unreleased` heading above it.
4. Remove the draft warning from `docs/releases/v0.2.0.md`, add the same date and
   ensure its claims match the changelog and verification receipt.
5. Re-run the course gates because the lock and diagram receipt changed. Then
   verify the two version sources and the clean tree:

   ```bash
   uv lock --check
   uv run --frozen python - <<'PY'
   import tomllib
   from pathlib import Path

   project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
   locked = tomllib.loads(Path("uv.lock").read_text())["package"]
   assert project["version"] == "0.2.0"
   assert any(p["name"] == "agent-harness-path" and p["version"] == "0.2.0" for p in locked)
   PY
   git status --short
   ```

6. Commit the release metadata and generated receipt. Confirm `git status --short`
   is empty.
7. Push the reviewed candidate branch to the verified public remote and open a
   pull request so hosted checks can run. After review and merge, select the
   resulting `main` commit as the release candidate in a dedicated release
   checkout. A merge or squash may change the commit identity; inspect that
   result and repeat affected gates if its content changed.
8. Require the repository's `verify` workflow for the push to `main` to pass on
   that exact release commit. A green pull-request merge preview alone does not
   identify the final release commit.
9. Record the immutable commit with `git rev-parse HEAD`; compare it with the
   commit shown by the workflow before tagging.

Do not amend the candidate after recording evidence. A correction creates a new
candidate and requires the affected gates again.

## 4. Tag and build course assets

Create the annotated course tag only from the clean, verified release commit:

```bash
git status --short
git rev-parse HEAD
git tag -a v0.2.0 -m "The Agent Harness Path v0.2.0"
git show --no-patch --decorate v0.2.0
```

Build archives from the tag in a new local release directory, not from the working
tree. GitHub will provide source archives automatically; a maintainer may also
attach an explicit course archive and checksum manifest:

```bash
mkdir -p dist
git archive --format=tar.gz --prefix=agent-harness-path-v0.2.0/ \
  --output=dist/agent-harness-path-v0.2.0.tar.gz v0.2.0
shasum -a 256 dist/agent-harness-path-v0.2.0.tar.gz \
  > dist/SHA256SUMS
tar -tzf dist/agent-harness-path-v0.2.0.tar.gz | head
shasum -a 256 -c dist/SHA256SUMS
```

The archive contains course source and the existing LFS pointer policy; Video
Overviews continue to stream from the documented public bucket. A CourseWeave
wheel is an application asset and must never be attached to the course release or
renamed to look like one.

## 5. Publish deliberately

The reviewed release commit is already public from the candidate review above.
Push its annotated tag only after the maintainer reviews the exact commit, notes
and checksums. Create a GitHub Release for `v0.2.0` from
`docs/releases/v0.2.0.md`, attach only the reviewed course assets, and verify the
tag, archive and checksum from a fresh download. None of those external actions is
performed by preparing this runbook.

After publication, clone the public tag into a new directory with Git LFS smudging
disabled by the repository policy, run the native quickstart, open
`lessons/index.html`, and execute one notebook. This is a release smoke test, not
a substitute for the pre-tag gates.

## Migration and rollback

Use a fresh clone for `v0.2.0`. Copy only learner-owned notebooks, notes and work
outputs into a separate, non-Git folder after comparing them with the new blank
sources. Do not overwrite the new course checkout and do not treat CourseWeave
activity records as notebook contents.

CourseWeave learners should start with a fresh external state directory for the
full-course manifest. The earlier S01/S02 workspace remains readable with the
application version that created it; no automatic migration is claimed. Keep that
workspace until the learner has confirmed the new study copy and records.

To return to the public course `v0.1.0`, create another clone or worktree at the
existing tag and run its locked environment. Do not reset or delete the current
workspace:

```bash
git worktree add ../agent-harness-path-v0.1.0 v0.1.0
cd ../agent-harness-path-v0.1.0
uv sync --frozen
```

Rollback of CourseWeave is separate: reinstall its previous public package in a
new platform venv and reopen only the state directory documented as compatible
with that version. Returning the course tag does not downgrade the application,
and returning the application does not rewrite course or learner files.
