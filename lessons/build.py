#!/usr/bin/env python3
"""Render lessons/src/*.md to lessons/*.html using template.html.

Stdlib + the `markdown` package only (uv-managed, see pyproject.toml).
Mermaid code fences are converted to <pre class="mermaid"> so the template's
mermaid.js (vendored at lessons/vendor/, browser-side) can render them.
Each page also gets a prev/index/next nav bar, top and bottom of <main>.
"""

import datetime
import re
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

MD = markdown.Markdown(extensions=["tables", "fenced_code"])

# python-markdown emits mermaid fences as <pre><code class="language-mermaid">;
# mermaid.js wants <pre class="mermaid"> with raw text. role="img" + aria-label
# give screen readers a generic stand-in; the prose around each diagram carries
# the actual description (no per-diagram alt text).
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)
MERMAID_PRE = (
    r'<pre class="mermaid" role="img" '
    r'aria-label="Architecture diagram — described in surrounding prose">\1</pre>'
)

# Reading order for the prev/next nav bars: index first, then S01..S14.
LESSON_ORDER = [
    "index",
    "S01-agent-loop",
    "S02-golden-evals",
    "S03-context-engineering",
    "S04-structured-generation",
    "S05-consent-gate",
    "S06-layered-detection",
    "S07-repair-loop",
    "S08-observability-replay",
    "S09-evidence-reports",
    "S10-error-analysis",
    "S11-budgets-routing",
    "S12-judge-calibration",
    "S13-rebuild-from-memory",
    "S14-ship-and-pilot",
]


def render_body(source: Path) -> tuple[str, str, int]:
    """Convert one source file; return (body HTML, H1 title, mermaid count)."""
    MD.reset()
    body = MD.convert(source.read_text(encoding="utf-8"))
    body, n = MERMAID_RE.subn(MERMAID_PRE, body)
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    title = title_match.group(1) if title_match else source.stem
    return body, title, n


def build_nav(slug: str, order: list[str], titles: dict[str, str]) -> str:
    """Prev/index/next bar. Index gets only the forward link to S01; the
    last lesson gets no next. Link labels are the targets' rendered H1s."""
    i = order.index(slug)
    prev_link = index_link = next_link = ""
    if i > 0:
        prev = order[i - 1]
        prev_link = f'<a href="{prev}.html">&larr; Prev: {titles[prev]}</a>'
    if slug != "index":
        index_link = '<a href="index.html">Index</a>'
    if i < len(order) - 1:
        nxt = order[i + 1]
        next_link = f'<a href="{nxt}.html">Next: {titles[nxt]} &rarr;</a>'
    return (
        '<nav class="lesson-nav">'
        f'<span class="nav-prev">{prev_link}</span>'
        f'<span class="nav-index">{index_link}</span>'
        f'<span class="nav-next">{next_link}</span>'
        "</nav>"
    )


def render(source: Path, nav: str) -> tuple[str, int]:
    body, title, n = render_body(source)
    return (
        TEMPLATE.replace("{{ title }}", title)
        .replace("{{ nav }}", nav)
        .replace("{{ body }}", body)
        .replace("{{ date }}", datetime.date.today().isoformat())
        .replace("{{ source }}", source.name)
    ), n


def main() -> int:
    sources = {source.stem: source for source in SRC.glob("*.md")}
    if not sources:
        print("build.py: no sources in lessons/src/", file=sys.stderr)
        return 1
    order = [slug for slug in LESSON_ORDER if slug in sources]
    order += sorted(slug for slug in sources if slug not in LESSON_ORDER)
    # Titles are needed up front: each page's nav labels its neighbours.
    titles = {slug: render_body(source)[1] for slug, source in sources.items()}
    for slug in order:
        source = sources[slug]
        html, n_mermaid = render(source, build_nav(slug, order, titles))
        if n_mermaid == 0 and slug != "index":
            print(f"build.py: WARNING {source.name}: no mermaid diagram found")
        out = HERE / (slug + ".html")
        out.write_text(html, encoding="utf-8")
        print(f"{source.name} -> {out.name} ({n_mermaid} mermaid block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
