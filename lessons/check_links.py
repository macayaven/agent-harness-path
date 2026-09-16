#!/usr/bin/env python3
"""Fail if lesson HTML has a broken relative href/src (and optionally http URLs).

Stdlib only. Run after `lessons/build.py`. Skips mailto, data, and in-page
anchors. LFS pointer files count as present (CI checks out without smudging).
Checks <a href>, <script src>, <img src>, <link href>, <video src>, <source src>.

  uv run python lessons/check_links.py         # generated HTML in lessons/
  uv run python lessons/check_links.py --http  # also GET unique http hrefs
"""

from __future__ import annotations

import argparse
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent

SOFT_HTTP = {401, 403, 429}
UA = (
    "Mozilla/5.0 (compatible; AgentHarnessPath-linkcheck/1.0; "
    "+https://github.com/macayaven/agent-harness-path)"
)
SRC_TAGS = {"script", "img", "video", "source", "iframe"}
HREF_TAGS = {"a", "link"}


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        wanted = []
        if tag in HREF_TAGS:
            wanted.append("href")
        if tag in SRC_TAGS:
            wanted.append("src")
        for key, value in attrs:
            if key in wanted and value:
                self.refs.append(value)


def is_external(ref: str) -> bool:
    return ref.startswith(("http://", "https://", "mailto:", "data:"))


def collect_pages(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*.html") if p.name != "template.html")


def check_relative(pages: list[Path]) -> tuple[list[str], int]:
    missing: list[str] = []
    checked = 0
    for page in pages:
        parser = ResourceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for ref in parser.refs:
            if is_external(ref) or ref.startswith("#"):
                continue
            target = ref.split("#", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{page.name} -> {ref}")
    return missing, checked


def unique_http(pages: list[Path]) -> list[str]:
    found: set[str] = set()
    for page in pages:
        parser = ResourceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for ref in parser.refs:
            if ref.startswith(("http://", "https://")):
                found.add(ref.split("#", 1)[0])
    return sorted(found)


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # present in the uv tooling venv; optional for stdlib-only runs
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _get(url: str, timeout: float) -> int | None:
    req = urllib.request.Request(
        url, method="GET", headers={"User-Agent": UA, "Accept": "*/*"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            resp.read(1024)
            return resp.status
    except urllib.error.HTTPError as e:
        try:
            e.read(256)
        except Exception:
            pass
        return e.code
    except Exception:
        return None


def probe_http(url: str, timeout: float = 20.0) -> tuple[str, int | None, bool]:
    """Return (url, status, hard_fail). 401/403/429 are soft."""
    status = _get(url, timeout)
    # Retry once on rate-limit or transport failure (timeout, DNS, reset).
    if status == 429 or status is None:
        time.sleep(2)
        status = _get(url, timeout)
    if status is not None and 200 <= status < 400:
        return url, status, False
    if status in SOFT_HTTP:
        return url, status, False
    return url, status, True


def check_http(urls: list[str]) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    soft: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(probe_http, u) for u in urls]
        for fut in as_completed(futs):
            url, status, failed = fut.result()
            label = f"{status} {url}"
            if failed:
                hard.append(label)
            elif status in SOFT_HTTP:
                soft.append(label)
    return sorted(hard), sorted(soft)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=HERE,
        help="Directory of HTML to check (default: lessons/)",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Also GET unique http(s) refs; 404/5xx fail, 401/403/429 warn",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    pages = collect_pages(root)
    if not pages:
        print(f"check_links.py: no HTML in {root}", file=sys.stderr)
        return 1
    missing, checked = check_relative(pages)
    if missing:
        print("check_links.py: broken relative refs:", file=sys.stderr)
        for row in missing:
            print(f"  {row}", file=sys.stderr)
        return 1
    print(f"check_links.py: {len(pages)} pages, {checked} relative refs ok")
    if not args.http:
        return 0
    urls = unique_http(pages)
    hard, soft = check_http(urls)
    for row in soft:
        print(f"check_links.py: soft {row}", file=sys.stderr)
    if hard:
        print("check_links.py: broken http refs:", file=sys.stderr)
        for row in hard:
            print(f"  {row}", file=sys.stderr)
        return 1
    print(f"check_links.py: {len(urls)} unique http refs ok ({len(soft)} soft)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
