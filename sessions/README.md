# Sessions

One directory per session holds everything that session needs. Learners start at
`index.html` in this folder, the course home; this page says what each file in a
session folder is and who it is for.

| File | For | What it is |
| --- | --- | --- |
| `lesson.html` | you | The lesson. Read this; it is built in place from `lesson.md`, never hand-edited. |
| `toy.py` | you | The marimo notebook (S01–S12): stdlib + `cafe`, offline stub or your own model. |
| `lab.md` | you, optional | Hard-path protocol (S01–S12): Build / Verify / Record / Done-when. See `labs/README.md`. |
| `audit-card.md` (S13); `cold-run-card.md`, `pilot-page-card.md`, `pilot-card.md` (S14) | you, optional | Working cards for the unaided protocols: prepare before the sitting, record after it. |
| `companion.md` | your AI tutor | Tutor context: maps the session's `cafe/` module to the optional café-host lab and sets what the tutor may do. Attach it in editor chat; you don't need to read it. |
| `recordings/model.jsonl` (S04, S05, S07, S09) | you, optional | Real-model comparisons, replayed offline by `uv run python tools/record_fixtures.py`. |
| `public/diagrams/` | both | Committed figures: the lesson SVG plus any toy-only `.mmd`/`.svg`. |
| `lesson.md` | contributors | Authoring source of `lesson.html`: edit it, then rebuild. |

`index.md` / `study-plan.md` at this root build to the course home and the
post-core overlay. `S00-course-overview.mp4` is the course home's preview.

Same session numbers elsewhere are different artifacts, not extra lessons —
but they now live next to each other instead of in parallel trees.

Rebuild: `uv run python tools/build.py`. Check links:
`uv run python tools/check_links.py`.
