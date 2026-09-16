#!/usr/bin/env python3
"""Fail if a SOTA table row has a status tag but no http(s) URL.

Stdlib only. Run against lessons/src/*.md.

  uv run python lessons/check_sota_urls.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
TAG_RE = re.compile(
    r"\*\*(?:already in this path|recognize|adopt|newer than this session|ignore)\*\*"
)


def main() -> int:
    missing: list[str] = []
    checked = 0
    for path in sorted(SRC.glob("S*.md")):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue
            if not TAG_RE.search(line):
                continue
            checked += 1
            if "http://" not in line and "https://" not in line:
                missing.append(f"{path.name}:{i}")
    if missing:
        print(
            "SOTA rows with a status tag but no http(s) URL:",
            file=sys.stderr,
        )
        for row in missing:
            print(f"  {row}", file=sys.stderr)
        return 1
    print(f"check_sota_urls.py: {checked} tagged rows, all have a URL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
