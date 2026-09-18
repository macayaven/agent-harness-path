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
Use the course-feedback form for study friction, but submit only a short,
non-sensitive account. Do not attach credentials, raw chats, private participant
material, local filesystem paths or a learner's full work product.

## Setup

Python 3.11+, `uv`, Git. Preview videos stream from the public bucket; Git LFS
only if you are replacing an mp4.

```bash
git clone https://github.com/macayaven/agent-harness-path.git
cd agent-harness-path
uv sync
```

## Edit, then verify

1. Edit sources in `lessons/src/*.md`, `notebooks/*.py`, or `labs/`
   (protocols and Python). Never hand-edit generated `lessons/*.html`. Learners read the generated HTML from a clone
   (`lessons/index.html`). GitHub's file view of `lessons/src/` is not a
   supported reader — relative `videos/` paths are rewritten to the public
   bucket at build time.
   Edits to `lessons/src/study-plan.md` must preserve its authoritative external
   links and workload honesty, then rebuild `lessons/study-plan.html`.
2. Run the content contracts:

   ```bash
   COURSE_MODE=stub uv run python -m unittest discover -s tests
   ```

3. Rebuild: `uv run python lessons/build.py`
4. Check links: `uv run python lessons/check_links.py`
   After a lesson or SOTA change, also:

   ```bash
   uv run python lessons/check_links.py --http
   uv run python lessons/check_sota_urls.py
   uv run python labs/run.py --all --replay
   ```

   Re-publish videos after adding or replacing an mp4: `scripts/publish_videos.sh`.
5. Execute any notebook you touched (and its neighbours if you changed a shared
   claim) headless, then check canonical form:

   ```bash
   COURSE_MODE=stub PYTHONPATH="$PWD/tests/no_network_site:$PWD" uv run python notebooks/sNN_….py
   uv run marimo check --strict --ignore MF004 notebooks labs/app.py
   uv run marimo check --fix --ignore MF004 notebooks labs/app.py && git diff --exit-code -- notebooks labs/app.py
   ```

   Commit **only** the form `marimo check --fix --ignore MF004` produces; the
   `git diff --exit-code` line is the contract. **Never `--unsafe-fixes`** — it
   deletes comment-only cells, i.e. every predict-first and attempt skeleton.
6. marimo notebooks are plain Python: they have no stored outputs to clear, but
   they **must** be committed in canonical form (previous step).
7. If you touched `labs/`:

   ```bash
   uv run python -m unittest labs/test_contracts.py
   uv run python labs/run.py --all --replay
   ```

8. If you changed a SOTA row, open the source URL and confirm it still says what
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

## Static diagrams

Run `uv run python -m unittest discover -s tests -v` for content and static
freshness checks (also run in CI). Notebook structure is protected by contracts
in `tests/test_notebooks.py`; add `attempt_<topic>` units and other learner work
without renaming or rewriting the existing named cells. Execute notebooks after
edits as above.

Every lesson diagram is a committed SVG, so offline clone-and-read and ordinary
HTML builds need no browser or Node. S08 and S14 each contain two diagrams.
Notebook diagrams are committed SVGs too: shared sessions inline the lesson
asset, and the five notebook-only diagrams render from `notebooks/diagrams/`
`.mmd` sources in the same command. Notebook cells inline bytes via
`cafe.diagrams.inline` — never `mo.mermaid`, whose frontend island does not
render in the Cursor extension. To change any Mermaid source, diagram
alternative, renderer, options, vendored Mermaid asset or Python lock:

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
alternatives. Generated HTML stays script-free; do not add in-browser Mermaid.

## Documentation and releases

[docs/README.md](docs/README.md) maps the public documentation and names its
authoritative sources. Keep setup commands in this file and link to them instead
of duplicating variants. Use [docs/RELEASING.md](docs/RELEASING.md) for the course
release process.

Documentation-only changes still require the unit suite, clean lesson rebuild,
relative-link check and SOTA source check. Execute notebooks or replay labs when
their source or contract changed. Run the HTTP check when lesson/SOTA URLs changed.
Do not convert a locally observed pilot into a general accessibility, learning,
provider, teacher-workflow or production-readiness claim.
