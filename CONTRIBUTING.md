# Contributing

Thanks for wanting to make the path better. Read `AGENTS.md` first — it is the
contract for lesson format, notebook conventions, and the toy-domain rule.

## What belongs here

Fixes and improvements to **this** course: lesson accuracy, notebook bugs, SOTA
drift, broken links, accessibility, and the build. Not a production harness, and
not a solution to someone else's take-home.

## Issues

Use GitHub Issues for defects a learner can hit (broken links, lesson/notebook
mismatch, build or CI failures). One problem per issue, with the file path and
what you expected. Security reports go to `SECURITY.md`, not the public tracker.

## Setup

Python 3.11+, `uv`, Git. Preview videos stream from the public bucket; Git LFS
only if you are replacing an mp4.

```bash
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync
```

## Edit, then verify

1. Edit sources in `lessons/src/*.md`, `notebooks/*.ipynb`, or `labs/`
   (protocols and Python). Never hand-edit generated `lessons/*.html`. Learners read the generated HTML from a clone
   (`lessons/index.html`). GitHub's file view of `lessons/src/` is not a
   supported reader — relative `videos/` paths are rewritten to the public
   bucket at build time.
   Edits to `lessons/src/study-plan.md` must preserve its authoritative external
   links and workload honesty, then rebuild `lessons/study-plan.html`.
2. Rebuild: `uv run python lessons/build.py`
3. Check links: `uv run python lessons/check_links.py`
   After a lesson-HTML change, also:

   ```bash
   uv run python lessons/check_links.py --http
   uv run python lessons/check_sota_urls.py
   uv run python labs/run.py --all --replay
   ```

   Re-publish videos after adding or replacing an mp4: `scripts/publish_videos.sh`.
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
- `--live` in CI, or secrets committed under `labs/`
- SOTA rows without a source, or status tags other than the five in `AGENTS.md`
- cheerleading or padded prose that drops the existing density

## Code of conduct

`CODE_OF_CONDUCT.md`. Report CoC issues via GitHub issues (maintainers will
convert to private if needed) or email macayaven@gmail.com.

## Pilot adapter and static diagrams

Run `uv run python -m unittest discover -s tests -v` for native adapter/content
checks (also run in CI). Original notebook cells are protected by a checked-in
semantic hash receipt; add learner attempt cells without changing original IDs,
sources, metadata or outputs. Execute notebooks after edits as above.

S01/S02 use committed SVG, so offline clone-and-read and ordinary HTML builds need
no browser or Node. To change a Mermaid source, renderer, options or Python lock:

```bash
uv sync --frozen --group diagrams
uv run --group diagrams playwright install chromium
uv run --group diagrams python lessons/render_diagrams.py
uv run --group diagrams python lessons/render_diagrams.py --check
uv run python lessons/build.py
```

The course owns the pinned `playwright==1.58.0` optional dependency and uses its
vendored Mermaid under the existing MIT notice. It never imports sibling
node_modules. The renderer fixes options, viewport and source-seeded IDs, renders
each diagram in two fresh pages and records Chromium/host/font details plus source,
vendor, renderer, config, lock and SVG hashes. Ordinary builds fail on stale hashes.
`--check` additionally compares fresh output to committed bytes on the recorded
renderer/font host; cross-OS/font determinism is **not** claimed. CI performs the
portable source/asset freshness checks, not a false cross-host byte equivalence
claim. Inspect regenerated diagrams visually and retain their meaningful text
alternatives. Other lessons keep the original native browser Mermaid path; never
relax CourseWeave's scripts-disabled reader to accommodate them.

Real compatibility is a separate mandatory installed-artifact check, with no
conditional sibling skip:

```bash
/absolute/path/courseweave-pilot-env/bin/python -I scripts/verify_courseweave.py
```

Use the final wheel, not an editable install. See study/COURSEWEAVE-PILOT.md for the
explicit launcher/kernel/state interface and the platform-owned installed browser,
provider and kernel isolation acceptance beyond this read-only contract check.
