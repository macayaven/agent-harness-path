# Course release runbook

This runbook publishes `macayaven/agent-harness-path`. **v0.3.0 supersedes
v0.2.0:** take the course from a clone in Cursor. Preparing this file does not
create a tag or public asset.

## 1. Select the exact candidate

Use a dedicated clean checkout on nonsynced local storage. Verify the public
remote by URL. Review every change since the last tag. Confirm generated HTML
and diagrams, notebook structural contracts, licenses, learner documentation
and public evidence. Search public text for credentials, raw chats/logs,
participant content, private hostnames and machine paths.

## 2. Run the course gates

```sh
uv sync --frozen
COURSE_MODE=stub uv run --frozen python -m unittest discover -s tests -v
for nb in notebooks/s*_toy.py; do
  COURSE_MODE=stub PYTHONPATH="$PWD/tests/no_network_site:$PWD" uv run --frozen python "$nb" > /dev/null
done
uv run --frozen marimo check --strict --ignore MF004 notebooks labs/app.py
uv run --frozen marimo check --fix --ignore MF004 notebooks labs/app.py
git diff --exit-code -- notebooks labs/app.py
uv run --frozen python lessons/build.py
git diff --exit-code -- lessons/*.html lessons/index.html
test -z "$(git status --porcelain --untracked-files=all -- lessons/)"
uv run --frozen python lessons/check_sota_urls.py
uv run --frozen python lessons/check_links.py
uv run --frozen python -m unittest labs/test_contracts.py
uv run --frozen python labs/run.py --all --replay
uv run --frozen python lessons/check_links.py --http
```

Never run lab `--live` as a course release gate. If Mermaid inputs changed, run
the pinned diagram workflow in `CONTRIBUTING.md` on the recorded renderer/font
host and inspect every changed SVG.

## 3. Freeze, tag and publish

Confirm `pyproject.toml` and `uv.lock` both say `0.3.0`. Move changelog entries
out of `Unreleased`, commit through a reviewed pull request, and require the
`verify` workflow on the exact `main` commit.

```sh
git tag -a v0.3.0 -m "The Agent Harness Path v0.3.0"
git archive --format=tar.gz --prefix=agent-harness-path-v0.3.0/ \
  --output=agent-harness-path-v0.3.0.tar.gz v0.3.0
```

Attach only the course archive. Do not attach a third-party application bundle.

## 4. Re-record the video previews (human step, after the cut lands)

The `▶` previews are Google Gemini Notebook Video Overviews, archived in Git
LFS under `lessons/videos/` and served from the GCS bucket in
`scripts/publish_videos.sh` (`lessons/site_urls.py` rewrites the hrefs at
build time). Generation is interactive and cannot run in CI; the lessons carry
an explicit lag label until this is done.

```sh
# 1. In Gemini Notebook, one Video Overview per lesson from the matching
#    lessons/src/SNN-*.md (English), plus S00 from lessons/src/index.md.
#    Download each as SNN-<slug>.mp4 (S00-course-overview.mp4).
# 2. Replace the LFS files (needs smudge: git lfs pull first on a fresh clone).
cp ~/Downloads/'S'*.mp4 lessons/videos/
# 3. Publish to the bucket (needs gcloud auth).
BUCKET=macayaven-agent-harness-path-videos PROJECT=<id> scripts/publish_videos.sh
# 4. Drop the lag label in lessons/src/S01..S12 (keep the rest of the line):
#    "**Video:** [Gemini Notebook overview](videos/SNN-slug.mp4) — generated
#    with Google Gemini Notebook; preview or review, never a substitute for
#    the notebook." Then rebuild the HTML and re-run section 2.
```

Do not commit a half-published set: LFS files, bucket objects, and the
Video lines move together, in one reviewed PR.

## Migration

Use a fresh clone for v0.3.0. Copy learner-owned notebooks, notes and work
output into a separate local folder. To revisit v0.2.0 or v0.1.0 without
resetting current work, use a git worktree on that tag.
