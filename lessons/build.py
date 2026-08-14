#!/usr/bin/env python3
"""Render lessons/src/*.md to lessons/*.html using template.html.

Stdlib + the `markdown` package only (uv-managed, see pyproject.toml).
Mermaid code fences are converted to <pre class="mermaid"> so the template's
mermaid.js (CDN, browser-side) can render them.
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
# mermaid.js wants <pre class="mermaid"> with raw text.
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)


def render(source: Path) -> tuple[str, int]:
    MD.reset()
    body = MD.convert(source.read_text(encoding="utf-8"))
    body, n = MERMAID_RE.subn(r'<pre class="mermaid">\1</pre>', body)
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    title = title_match.group(1) if title_match else source.stem
    return (
        TEMPLATE.replace("{{ title }}", title)
        .replace("{{ body }}", body)
        .replace("{{ date }}", datetime.date.today().isoformat())
        .replace("{{ source }}", source.name)
    ), n


def main() -> int:
    sources = sorted(SRC.glob("*.md"))
    if not sources:
        print("build.py: no sources in lessons/src/", file=sys.stderr)
        return 1
    for source in sources:
        html, n_mermaid = render(source)
        if n_mermaid == 0 and source.stem != "index":
            print(f"build.py: WARNING {source.name}: no mermaid diagram found")
        out = HERE / (source.stem + ".html")
        out.write_text(html, encoding="utf-8")
        print(f"{source.name} -> {out.name} ({n_mermaid} mermaid block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
