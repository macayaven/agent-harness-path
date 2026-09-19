"""Codespace surface contract: container config, extension parity, rules mirror.

.vscode/extensions.json and .devcontainer/devcontainer.json must agree, and
the VS Code instructions must stay a verbatim mirror (past frontmatter) of
the Cursor companion rule.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from check_devcontainer import (  # noqa: E402
    check_devcontainer,
    check_extension_parity,
    check_instructions_mirror,
    load_jsonc,
    strip_jsonc,
)


class StripJsoncTests(unittest.TestCase):
    def test_trailing_and_full_line_comments_stripped(self) -> None:
        src = '{\n// lead\n"a": 1, // trail\n"b": "x // not a comment"\n}\n'
        self.assertEqual(json.loads(strip_jsonc(src)), {"a": 1, "b": "x // not a comment"})


class NegativeTests(unittest.TestCase):
    def test_bad_configs_are_rejected(self) -> None:
        dev = load_jsonc(ROOT / ".devcontainer" / "devcontainer.json")
        cases = {
            "root user": {**dev, "remoteUser": "root"},
            "unpinned uv": {
                **dev,
                "postCreateCommand": "pip install uv && uv sync --frozen",
            },
            "curl pipe": {
                **dev,
                "postCreateCommand": "curl https://astral.sh/uv/install.sh | sh",
            },
            "home dependent": {
                **dev,
                "postCreateCommand": "pip install --user uv==0.12.17",
            },
        }
        for name, bad in cases.items():
            with self.subTest(name=name):
                self.assertNotEqual(check_devcontainer(bad), [])
        recs = load_jsonc(ROOT / ".vscode" / "extensions.json")["recommendations"]
        with self.subTest(name="drifted recommendations"):
            self.assertNotEqual(
                check_extension_parity(dev, [*recs, "someone.else-ext"]), []
            )


class DevcontainerTests(unittest.TestCase):
    def test_surface_validates_clean(self) -> None:
        dev = load_jsonc(ROOT / ".devcontainer" / "devcontainer.json")
        self.assertEqual(check_devcontainer(dev), [])

    def test_container_and_recommendations_match_exactly(self) -> None:
        dev = load_jsonc(ROOT / ".devcontainer" / "devcontainer.json")
        recs = load_jsonc(ROOT / ".vscode" / "extensions.json")["recommendations"]
        self.assertEqual(check_extension_parity(dev, recs), [])

    def test_instructions_mirror_cursor_rule(self) -> None:
        mdc = (ROOT / ".cursor" / "rules" / "ahp-companion.mdc").read_text(
            encoding="utf-8"
        )
        instructions = (
            ROOT / ".github" / "instructions" / "ahp-companion.instructions.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(check_instructions_mirror(mdc, instructions), [])


if __name__ == "__main__":
    unittest.main()
