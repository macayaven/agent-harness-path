#!/usr/bin/env python3
"""Render lessons/src/*.md to lessons/*.html using template.html.

Stdlib + the `markdown` package only (uv-managed, see pyproject.toml).
Mermaid fences use committed static SVG with input/asset freshness checks.
Each page also gets a prev/index/next nav bar, top and bottom of <main>.
"""

import re
import html
import sys
from itertools import count
from pathlib import Path

import markdown

from site_urls import rewrite_video_hrefs
from static_diagrams import STATIC_LESSONS, static_image

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

MD = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

# python-markdown emits mermaid fences as <pre><code class="language-mermaid">.
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)

# Reading order for the prev/next nav bars: index, study plan, then S01..S14.
LESSON_ORDER = [
    "index",
    "study-plan",
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

READ_FRAGMENTS = {
    slug: 'the-protocol' if slug.startswith(('S13-', 'S14-'))
    else 'the-theory-in-depth'
    for slug in LESSON_ORDER
    if slug.startswith('S')
}
LOCAL_LESSON_HREF_RE = re.compile(
    r'(?P<prefix>href=")(?P<path>(?:\.\.?/)*'
    r'(?P<slug>S[0-9]{2}-[A-Za-z0-9-]+)\.html)(?P<suffix>")'
)


def canonical_lesson_hrefs(rendered: str) -> str:
    """Give cross-page lesson links the manifest's canonical read fragment."""
    def replace(match: re.Match[str]) -> str:
        fragment = READ_FRAGMENTS.get(match.group('slug'))
        if fragment is None:
            return match.group(0)
        return (
            f'{match.group("prefix")}{match.group("path")}#{fragment}'
            f'{match.group("suffix")}'
        )

    return LOCAL_LESSON_HREF_RE.sub(replace, rendered)


def render_body(source: Path) -> tuple[str, str, int]:
    """Convert one source file; return (body HTML, H1 title, mermaid count)."""
    MD.reset()
    body = MD.convert(source.read_text(encoding="utf-8"))
    if source.stem in STATIC_LESSONS:
        indices = count()
        body, n = MERMAID_RE.subn(
            lambda match: static_image(
                source.stem,
                next(indices),
                html.unescape(match.group(1)),
            ),
            body,
        )
    else:
        n = len(MERMAID_RE.findall(body))
        if n:
            raise ValueError(f'{source.name}: no static diagram configuration')
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    title = title_match.group(1) if title_match else source.stem
    return body, title, n


def build_nav(slug: str, order: list[str], titles: dict[str, str]) -> str:
    """Prev/index/next bar. Index gets only the forward link; the last
    lesson gets no next. Link labels are the targets' rendered H1s."""
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
    rendered = (
        TEMPLATE.replace("{{ title }}", title)
        .replace("{{ nav }}", nav)
        .replace("{{ body }}", body)
        .replace("{{ source }}", source.name)
    )
    return canonical_lesson_hrefs(rendered), n


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
        html = rewrite_video_hrefs(html)
        if n_mermaid == 0 and slug != "index":
            print(f"build.py: WARNING {source.name}: no mermaid diagram found")
        out = HERE / (slug + ".html")
        out.write_text(html, encoding="utf-8")
        print(f"{source.name} -> {out.name} ({n_mermaid} mermaid block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
