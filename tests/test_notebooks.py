"""Structural contracts for the marimo notebooks.

These are the mechanical guards for the four boredom makers: one model seam
(B1), one spine (B2), one domain (B3) and one canonical surface (B4).
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

EXPECTED = {
    "s01_agent_loop_toy.py": "cafe.loop",
    "s02_scripted_user_eval_toy.py": "cafe.evals",
    "s03_context_engineering_toy.py": "cafe.context",
    "s04_structured_generation_toy.py": "cafe.schema",
    "s05_consent_gate_toy.py": "cafe.consent",
    "s06_layered_detection_toy.py": "cafe.detect",
    "s07_repair_loop_toy.py": "cafe.repair",
    "s08_observability_replay_toy.py": "cafe.trace",
    "s09_evidence_report_toy.py": "cafe.report",
    "s10_error_analysis_toy.py": "cafe.taxonomy",
    "s11_budgets_routing_toy.py": "cafe.routing",
    "s12_judge_calibration_toy.py": "cafe.judge",
}

CELL_NAME = re.compile(r"^(test_)?s(0[1-9]|1[0-2])_[a-z0-9]+(_[a-z0-9]+)*$")
STALE_DOMAIN = ("trivia", "pub quiz", "mopbot", "concierge", "weather_bot")


def notebooks() -> list[Path]:
    return sorted(NOTEBOOKS.glob("s*_toy.py"))


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def decorated(tree: ast.Module, attr: str) -> list[ast.FunctionDef]:
    out = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Attribute) and target.attr == attr:
                out.append(node)
                break
    return out


def imported_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


class Inventory(unittest.TestCase):
    def test_exactly_the_twelve_expected_notebooks(self):
        self.assertEqual(sorted(p.name for p in notebooks()), sorted(EXPECTED))

    def test_no_ipynb_is_tracked(self):
        tracked = subprocess.run(
            ["git", "ls-files", "*.ipynb"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.split()
        self.assertEqual(tracked, [])


class Structure(unittest.TestCase):
    def test_each_notebook_declares_a_marimo_app(self):
        for path in notebooks():
            text = source(path)
            with self.subTest(notebook=path.name):
                ast.parse(text)
                self.assertIn('__generated_with = "0.24.2"', text)
                self.assertIn('app = marimo.App(width="medium")', text)
                self.assertIn('if __name__ == "__main__":', text)

    def test_cells_are_named_and_scoped_to_their_session(self):
        for path in notebooks():
            cells = decorated(ast.parse(source(path)), "cell")
            names = [c.name for c in cells]
            with self.subTest(notebook=path.name):
                self.assertNotIn("_", names, "unnamed cell: rename every `def _(`")
                self.assertEqual(len(names), len(set(names)))
                for name in names:
                    self.assertRegex(name, CELL_NAME)
                    self.assertIn(path.name[:3], name)


class Seam(unittest.TestCase):
    """B1: exactly one way to reach a model."""

    def test_every_notebook_uses_the_single_model_seam(self):
        for path in notebooks():
            with self.subTest(notebook=path.name):
                self.assertIn("get_client", source(path))

    def test_no_notebook_constructs_a_client_directly(self):
        for path in notebooks():
            text = source(path)
            with self.subTest(notebook=path.name):
                self.assertNotIn("LiveClient(", text)
                self.assertNotIn("urllib.request", text)
                self.assertNotIn("OPENAI_API_KEY", text)


class Spine(unittest.TestCase):
    """B2: session N builds on the cafe/ module it claims."""

    def test_each_notebook_imports_the_module_its_session_ships(self):
        for path in notebooks():
            module = EXPECTED[path.name]
            leaf = module.split(".")[1]
            tree = ast.parse(source(path))
            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    # from cafe.<leaf> import ...
                    if node.module == module or node.module.startswith(module + "."):
                        found = True
                    # from cafe import <leaf>[, other]
                    if node.module == "cafe" and any(
                        alias.name == leaf for alias in node.names
                    ):
                        found = True
                elif isinstance(node, ast.Import):
                    if any(
                        alias.name == module or alias.name.startswith(module + ".")
                        for alias in node.names
                    ):
                        found = True
            with self.subTest(notebook=path.name, module=module):
                self.assertTrue(found, f"{path.name} must drive {module}")


class Safety(unittest.TestCase):
    def test_imports_are_stdlib_plus_marimo_and_cafe(self):
        allowed = set(sys.stdlib_module_names) | {"marimo", "cafe"}
        for path in notebooks():
            with self.subTest(notebook=path.name):
                self.assertLessEqual(imported_roots(ast.parse(source(path))), allowed)

    def test_no_credentials_or_home_paths(self):
        for path in notebooks():
            text = source(path)
            with self.subTest(notebook=path.name):
                self.assertNotIn("/Users/", text)
                self.assertIsNone(re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b", text))


class Domain(unittest.TestCase):
    """B3: one café, everywhere."""

    def test_no_pre_cafe_domain_nouns_survive(self):
        for path in notebooks():
            text = source(path).lower()
            for noun in STALE_DOMAIN:
                with self.subTest(notebook=path.name, noun=noun):
                    self.assertNotIn(noun, text)


class Pedagogy(unittest.TestCase):
    def test_every_notebook_has_two_assertion_cells(self):
        for path in notebooks():
            cells = decorated(ast.parse(source(path)), "cell")
            tests = [c for c in cells if c.name.startswith("test_")]
            with self.subTest(notebook=path.name):
                self.assertGreaterEqual(len(tests), 2)

    def test_attempt_skeletons_are_unanswered(self):
        """An attempt unit must not contain the reference answer."""
        for path in notebooks():
            tree = ast.parse(source(path))
            attempts = [
                fn for fn in decorated(tree, "function") if fn.name.startswith("attempt_")
            ]
            for fn in attempts:
                with self.subTest(notebook=path.name, unit=fn.name):
                    self.assertNotIn("solution", fn.name)

    def test_each_solution_is_gated_behind_a_reveal(self):
        for path in notebooks():
            tree = ast.parse(source(path))
            text = source(path)
            solutions = [
                fn for fn in decorated(tree, "function") if fn.name.startswith("solution_")
            ]
            if not solutions:
                continue
            with self.subTest(notebook=path.name):
                self.assertIn("mo.ui.switch(", text)
                self.assertIn("mo.stop(", text)
                self.assertIn("inspect.getsource(", text)


if __name__ == "__main__":
    unittest.main()
