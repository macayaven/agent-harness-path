# Lessons

**Read the HTML.** `index.html` and `S01-agent-loop.html` … `S14-*.html` are the
course. Open those in a browser (or the hosted reader).

`src/` is the Markdown authors edit. `build.py` renders it into the HTML files
next to this README. The `.md` and `.html` pairs are **source and output**, not
two copies of the curriculum. Do not hand-edit the HTML.

Same session numbers elsewhere are different artifacts, not extra lessons:

| Path | What it is |
| --- | --- |
| `lessons/SNN-*.html` | Learner lesson (read this) |
| `lessons/src/SNN-*.md` | Authoring source (edit this, then rebuild) |
| `notebooks/sNN_*.ipynb` | Stdlib toy |
| `labs/sNN_*.md` | Optional hard-path protocol |
| `bridges/sNN.md` | Cursor companion rung |

Rebuild: `uv run python lessons/build.py`. Check links:
`uv run python lessons/check_links.py`.
