#!/usr/bin/env python3
"""Render sessions/*/lesson.md (+ index, study plan) to HTML in place.

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

HERE = Path(__file__).resolve().parent  # tools/
ROOT = HERE.parent
SESSIONS = ROOT / "sessions"
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

MD = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

# python-markdown emits mermaid fences as <pre><code class="language-mermaid">.
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)

# Reading order for the prev/next nav bars. Each entry is
# (directory relative to sessions/, SNN slug, output file name).
PAGES = [
    (".", "index", "index.html"),
    (".", "study-plan", "study-plan.html"),
    ("s01-agent-loop", "S01-agent-loop", "lesson.html"),
    ("s02-golden-evals", "S02-golden-evals", "lesson.html"),
    ("s03-context-engineering", "S03-context-engineering", "lesson.html"),
    ("s04-structured-generation", "S04-structured-generation", "lesson.html"),
    ("s05-consent-gate", "S05-consent-gate", "lesson.html"),
    ("s06-layered-detection", "S06-layered-detection", "lesson.html"),
    ("s07-repair-loop", "S07-repair-loop", "lesson.html"),
    ("s08-observability-replay", "S08-observability-replay", "lesson.html"),
    ("s09-evidence-reports", "S09-evidence-reports", "lesson.html"),
    ("s10-error-analysis", "S10-error-analysis", "lesson.html"),
    ("s11-budgets-routing", "S11-budgets-routing", "lesson.html"),
    ("s12-judge-calibration", "S12-judge-calibration", "lesson.html"),
    ("s13-rebuild-from-memory", "S13-rebuild-from-memory", "lesson.html"),
    ("s14-ship-and-pilot", "S14-ship-and-pilot", "lesson.html"),
]

READ_FRAGMENTS = {
    slug: 'the-protocol' if slug.startswith(('S13-', 'S14-'))
    else 'the-theory-in-depth'
    for _, slug, _ in PAGES
    if slug.startswith('S')
}

# Cross-session lesson links in sources, e.g. ../s02-golden-evals/lesson.html.
LOCAL_LESSON_HREF_RE = re.compile(
    r'(?P<prefix>href=")(?P<path>(?:\.\./)*'
    r'(?P<session>s[0-9]{2}-[a-z0-9-]+)/lesson\.html)(?P<suffix>")'
)

# Bucket object per page: the session video, or the overview for the index.
# The study plan carries no video, so it has no entry.
VIDEO_ASSET = {
    slug: f"{slug}.mp4" for _, slug, _ in PAGES if slug.startswith("S")
}
VIDEO_ASSET["index"] = "S00-course-overview.mp4"


def page_source(directory: str, slug: str) -> Path:
    if directory == ".":
        return SESSIONS / f"{slug}.md"
    return SESSIONS / directory / "lesson.md"


def rel_href(from_dir: str, to_dir: str, to_file: str) -> str:
    if from_dir == to_dir:
        return to_file
    if from_dir == ".":
        return f"{to_dir}/{to_file}"
    if to_dir == ".":
        return f"../{to_file}"
    return f"../{to_dir}/{to_file}"


def canonical_lesson_hrefs(rendered: str) -> str:
    """Give cross-page lesson links the manifest's canonical read fragment."""
    def replace(match: re.Match[str]) -> str:
        slug = "S" + match.group("session")[1:]
        fragment = READ_FRAGMENTS.get(slug)
        if fragment is None:
            return match.group(0)
        return (
            f'{match.group("prefix")}{match.group("path")}#{fragment}'
            f'{match.group("suffix")}'
        )

    return LOCAL_LESSON_HREF_RE.sub(replace, rendered)


def render_body(source: Path, slug: str) -> tuple[str, str, int]:
    """Convert one source file; return (body HTML, H1 title, mermaid count)."""
    MD.reset()
    body = MD.convert(source.read_text(encoding="utf-8"))
    if slug in STATIC_LESSONS:
        indices = count()
        body, n = MERMAID_RE.subn(
            lambda match: static_image(
                slug,
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
    title = title_match.group(1) if title_match else slug
    return body, title, n


def build_nav(directory: str, order: list[tuple[str, str, str]],
              titles: dict[str, str]) -> str:
    """Prev/index/next bar. Index gets only the forward link; the last
    lesson gets no next. Link labels are the targets' rendered H1s."""
    keys = [(d, f) for d, _, f in order]
    i = keys.index((directory, out_name(directory)))
    prev_link = index_link = next_link = ""
    if i > 0:
        prev_dir, prev_file = keys[i - 1]
        prev_link = (
            f'<a href="{rel_href(directory, prev_dir, prev_file)}">'
            f"&larr; Prev: {titles[keys[i - 1]]}</a>"
        )
    if directory != "." or out_name(directory) != "index.html":
        index_link = (
            f'<a href="{rel_href(directory, ".", "index.html")}">Index</a>'
        )
    if i < len(keys) - 1:
        next_dir, next_file = keys[i + 1]
        next_link = (
            f'<a href="{rel_href(directory, next_dir, next_file)}">'
            f"Next: {titles[keys[i + 1]]} &rarr;</a>"
        )
    return (
        '<nav class="lesson-nav">'
        f'<span class="nav-prev">{prev_link}</span>'
        f'<span class="nav-index">{index_link}</span>'
        f'<span class="nav-next">{next_link}</span>'
        "</nav>"
    )


def out_name(directory: str) -> str:
    for d, _, out in PAGES:
        if d == directory:
            return out
    raise ValueError(f"{directory}: not a course page")


def render(source: Path, slug: str, out: Path, nav: str) -> tuple[str, int]:
    body, title, n = render_body(source, slug)
    rendered = (
        TEMPLATE.replace("{{ title }}", title)
        .replace("{{ nav }}", nav)
        .replace("{{ body }}", body)
        .replace("{{ source }}", str(source.relative_to(ROOT)))
    )
    return canonical_lesson_hrefs(rendered), n


def main() -> int:
    for directory, slug, _ in PAGES:
        source = page_source(directory, slug)
        if not source.is_file():
            print(f"build.py: missing source {source.relative_to(ROOT)}",
                  file=sys.stderr)
            return 1
    known = {SESSIONS / d / "lesson.md" for d, _, _ in PAGES if d != "."}
    strays = sorted(p for p in SESSIONS.glob("*/lesson.md") if p not in known)
    if strays:
        print("build.py: lesson sources outside the manifest: "
              + ", ".join(str(p.relative_to(ROOT)) for p in strays),
              file=sys.stderr)
        return 1
    # Titles are needed up front: each page's nav labels its neighbours.
    titles = {}
    for directory, slug, out in PAGES:
        titles[(directory, out)] = render_body(
            page_source(directory, slug), slug)[1]
    order = [(d, s, o) for d, s, o in PAGES]
    for directory, slug, out in order:
        source = page_source(directory, slug)
        out_path = SESSIONS / directory / out
        html, n_mermaid = render(
            source, slug, out_path, build_nav(directory, order, titles))
        if slug in VIDEO_ASSET:
            html = rewrite_video_hrefs(html, VIDEO_ASSET[slug])
        if n_mermaid == 0 and slug != "index":
            print(f"build.py: WARNING {source.relative_to(ROOT)}: "
                  "no mermaid diagram found")
        out_path.write_text(html, encoding="utf-8")
        print(f"{source.relative_to(ROOT)} -> {out_path.relative_to(ROOT)} "
              f"({n_mermaid} mermaid block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
