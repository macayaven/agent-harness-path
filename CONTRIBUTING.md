# Contributing

Thanks for wanting to make the path better. Read `AGENTS.md` first — it is the
contract for lesson format, notebook conventions, and the toy-domain rule.

## What belongs here

Fixes and improvements to **this** course: lesson accuracy, notebook bugs, SOTA
drift, broken links, accessibility, and the build. Not a production harness, and
not a solution to someone else's take-home.

## Setup

Python 3.11+, `uv`, Git. Git LFS only if you need the videos.

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync
```

## Edit, then verify

1. Edit sources in `lessons/src/*.md` or `notebooks/*.ipynb`. Never hand-edit
   generated `lessons/*.html`.
2. Rebuild: `uv run python lessons/build.py`
3. Check links: `uv run python lessons/check_links.py`
4. Execute any notebook you touched (and its neighbours if you changed a shared
   claim):

   ```bash
   uv run jupyter nbconvert --to notebook --execute --stdout notebooks/sNN_….ipynb > /dev/null
   ```

5. Commit notebooks **without outputs** (`execution_count` null, empty
   `outputs`). If Jupyter wrote outputs, clear them before the commit.
6. If you changed a SOTA row, open the source URL and confirm it still says what
   the Take column claims. Re-date the section header if you refresh the table.

## Pull requests

Use the PR template. One concern per PR when you can (SOTA refresh ≠ notebook
refactor). Maintainers will reject:

- toys that are paste-ready production harnesses
- network calls, API keys, or non-stdlib imports in `notebooks/`
- SOTA rows without a source, or status tags other than the five in `AGENTS.md`
- cheerleading or padded prose that drops the existing density

## Code of conduct

`CODE_OF_CONDUCT.md`. Report CoC issues via GitHub issues (maintainers will
convert to private if needed) or email macayaven@gmail.com.
