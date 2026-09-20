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
import ast
import re
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
    blob = json.dumps(dev)
    if any(
        token in post or token in blob for token in (".local/bin", "$HOME", "~/", "--user")
    ):
        problems.append("uv install must not depend on HOME resolution")
    if "containerEnv" in blob or "remoteEnv" in blob:
        problems.append("uv install must not depend on remoteEnv")
    return problems


def check_extension_parity(dev: dict, recommended: list[str]) -> list[str]:
    exts = (dev.get("customizations", {}).get("vscode", {}).get("extensions") or [])
    if sorted(exts) != sorted(recommended):
        return [
            "container extensions and recommendations diverged: "
            f"{sorted(exts)} vs {sorted(recommended)}"
        ]
    return []


def frontmatter(text: str) -> tuple[dict, str]:
    """The flat YAML subset used by these course files, including inline lists."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter is required")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("frontmatter must have a closing delimiter")
    fields = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError("expected a flat frontmatter field")
        key, value = (part.strip() for part in line.split(":", 1))
        if key in fields:
            raise ValueError(f"duplicate frontmatter field: {key}")
        if value in {"true", "false"}:
            fields[key] = value == "true"
        elif value.startswith(("[", '"', "'")):
            try:
                fields[key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                raise ValueError(f"invalid course frontmatter field: {key}") from None
        else:
            fields[key] = value
    return fields, "".join(lines[end + 1:])


def check_tutor_policy(text: str) -> list[str]:
    """Structural safeguards; editor/model behavior still needs a live tutor bank."""
    normalized = " ".join(text.casefold().split())
    problems = []
    if re.search(r"unless.{0,80}peek", normalized) or "contributor exception" in normalized:
        problems.append("tutor policy contains a peek or contributor exception")
    for required in ("either in files or in chat", "does not change this role",
                     "s13/s14 assistance is process-only", "never request, open, print, log, copy, or commit credentials"):
        if required not in normalized:
            problems.append(f"tutor boundary missing: {required}")
    return problems


def check_instructions_mirror(mdc: str, instructions: str) -> list[str]:
    try:
        cursor_meta, cursor_body = frontmatter(mdc)
        copilot_meta, copilot_body = frontmatter(instructions)
    except ValueError as exc:
        return [str(exc)]
    problems = []
    if cursor_meta.get("alwaysApply") is not True:
        problems.append("Cursor rule must declare alwaysApply: true")
    if copilot_meta.get("applyTo") != "**":
        problems.append('Copilot instructions must declare applyTo: "**"')
    if cursor_body != copilot_body:
        problems.append("instructions body diverged from the .cursor rule")
    return problems + check_tutor_policy(cursor_body)


def check_tutor_agent(text: str) -> list[str]:
    try:
        fields, body = frontmatter(text)
    except ValueError as exc:
        return [str(exc)]
    expected = {"name": "AHP Tutor", "tools": ["read", "search"], "agents": [],
                "user-invocable": True, "disable-model-invocation": True}
    problems = [f"AHP Tutor requires {key}={value!r}" for key, value in expected.items()
                if fields.get(key) != value]
    if any(key in fields for key in ("handoffs", "hooks", "mcp-servers")):
        problems.append("AHP Tutor must not add handoffs, hooks or MCP servers")
    if "../instructions/ahp-companion.instructions.md" not in body:
        problems.append("AHP Tutor must reference the shared learner policy")
    return problems


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
    problems += check_tutor_agent((ROOT / ".github/agents/ahp-tutor.agent.md").read_text())
    settings = load_jsonc(ROOT / ".vscode/settings.json")
    for name in ("chat.includeApplyingInstructions", "chat.includeReferencedInstructions"):
        if settings.get(name) is not True:
            problems.append(f"{name} must be enabled for the learner policy")
    for problem in problems:
        print(f"FAIL {problem}", file=sys.stderr)
    if problems:
        return 1
    print("devcontainer surface ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
