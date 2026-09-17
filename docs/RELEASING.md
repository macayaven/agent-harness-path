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
uv run --frozen python -m unittest discover -s tests -v
for nb in notebooks/s*.py; do
  COURSE_MODE=stub PYTHONPATH="$PWD/tests/no_network_site:$PWD" uv run --frozen python "$nb" > /dev/null
done
uv run --frozen marimo check --strict --ignore MF004 notebooks
uv run --frozen marimo check --fix --ignore MF004 notebooks
git diff --exit-code -- notebooks
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

## Migration

Use a fresh clone for v0.3.0. Copy learner-owned notebooks, notes and work
output into a separate local folder. To revisit v0.2.0 or v0.1.0 without
resetting current work, use a git worktree on that tag.
