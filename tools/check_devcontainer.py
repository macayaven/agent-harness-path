#!/usr/bin/env python3
"""Validate the student container surface (stdlib only).

Checks .devcontainer/devcontainer.json (JSONC: full-line and trailing //
comments allowed, never inside strings), the .vscode extension
recommendations, and that the VS Code instructions mirror the Cursor
companion rule. Called by .github/workflows/devcontainer.yml and covered by
tests/test_codespaces.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def strip_jsonc(src: str) -> str:
    out: list[str] = []
    in_str = False
    esc = False
    i = 0
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ""
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            out.append(ch)
        elif ch == "/" and nxt == "/":
            while i < len(src) and src[i] != "\n":
                i += 1
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def load_jsonc(path: Path) -> dict:
    return json.loads(strip_jsonc(path.read_text(encoding="utf-8")))


def check_devcontainer(dev: dict) -> list[str]:
    problems: list[str] = []
    image = dev.get("image", "")
    if not image.startswith("mcr.microsoft.com/devcontainers/python:"):
        problems.append(f"unexpected base image {image!r}")
    if dev.get("remoteUser") != "vscode":
        problems.append("remoteUser must be vscode (image default is root)")
    post = dev.get("postCreateCommand", "")
    if "uv sync --frozen" not in post:
        problems.append("postCreateCommand must run uv sync --frozen")
    if "astral.sh" in post or "| sh" in post:
        problems.append("unpinned curl|sh installer in postCreateCommand")
    if "uv==" not in post:
        problems.append("uv install must be version-pinned (uv==X.Y.Z)")
    if ".local/bin" in post or "containerEnv" in json.dumps(dev):
        problems.append("uv install must not depend on HOME resolution")
    return problems


def check_extension_parity(dev: dict, recommended: list[str]) -> list[str]:
    exts = (dev.get("customizations", {}).get("vscode", {}).get("extensions") or [])
    if sorted(exts) != sorted(recommended):
        return [
            "container extensions and recommendations diverged: "
            f"{sorted(exts)} vs {sorted(recommended)}"
        ]
    return []


def check_instructions_mirror(mdc: str, instructions: str) -> list[str]:
    def body(text: str) -> str:
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            end = lines.index("---", 1)
            lines = lines[end + 1 :]
        return "\n".join(lines).strip() + "\n"

    if body(mdc) != body(instructions):
        return ["instructions body diverged from the .cursor rule"]
    return []


def main() -> int:
    problems: list[str] = []
    dev = load_jsonc(ROOT / ".devcontainer" / "devcontainer.json")
    problems += check_devcontainer(dev)
    recs = load_jsonc(ROOT / ".vscode" / "extensions.json")["recommendations"]
    problems += check_extension_parity(dev, recs)
    problems += check_instructions_mirror(
        (ROOT / ".cursor" / "rules" / "ahp-companion.mdc").read_text(
            encoding="utf-8"
        ),
        (ROOT / ".github" / "instructions" / "ahp-companion.instructions.md").read_text(
            encoding="utf-8"
        ),
    )
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if problems:
        return 1
    print("devcontainer surface ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
