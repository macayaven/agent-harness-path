#!/usr/bin/env python3
"""Fail if generated lesson HTML has a broken relative href.

Stdlib only. Run after `lessons/build.py`. Skips http(s), mailto, and in-page
anchors. LFS pointer files count as present (CI checks out without smudging).
"""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent


class HrefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:", "data:"))


def main() -> int:
    pages = sorted(HERE.glob("*.html"))
    if not pages:
        print("check_links.py: no generated HTML in lessons/", file=sys.stderr)
        return 1
    missing: list[str] = []
    checked = 0
    for page in pages:
        parser = HrefParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            if is_external(href) or href.startswith("#"):
                continue
            target = href.split("#", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{page.name} -> {href}")
    if missing:
        print("check_links.py: broken relative links:", file=sys.stderr)
        for row in missing:
            print(f"  {row}", file=sys.stderr)
        return 1
    print(f"check_links.py: {len(pages)} pages, {checked} relative hrefs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
