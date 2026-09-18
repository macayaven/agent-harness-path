# Sessions

One directory per session holds everything that session needs:

| File | What it is |
| --- | --- |
| `lesson.md` | Authoring source (edit this, then rebuild) |
| `lesson.html` | Learner lesson (read this; built in place, never hand-edit) |
| `toy.py` | Marimo toy (stdlib + `cafe`, live model) |
| `lab.md` | Optional hard-path protocol (S01–S12 only) |
| `companion.md` | Cursor companion rung |
| `video.mp4` | Video Overview preview (Git LFS) |
| `public/diagrams/` | Committed figures: the lesson SVG plus any toy-only `.mmd`/`.svg` |

`index.md` / `study-plan.md` at this root build to the course index and the
post-core overlay. `S00-course-overview.mp4` is the index page's preview.

Same session numbers elsewhere are different artifacts, not extra lessons —
but they now live next to each other instead of in parallel trees.

Rebuild: `uv run python tools/build.py`. Check links:
`uv run python tools/check_links.py`.
