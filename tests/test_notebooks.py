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
SESSIONS = ROOT / "sessions"

EXPECTED = {
    "s01-agent-loop": "cafe.loop",
    "s02-golden-evals": "cafe.evals",
    "s03-context-engineering": "cafe.context",
    "s04-structured-generation": "cafe.schema",
    "s05-consent-gate": "cafe.consent",
    "s06-layered-detection": "cafe.detect",
    "s07-repair-loop": "cafe.repair",
    "s08-observability-replay": "cafe.trace",
    "s09-evidence-reports": "cafe.report",
    "s10-error-analysis": "cafe.taxonomy",
    "s11-budgets-routing": "cafe.routing",
    "s12-judge-calibration": "cafe.judge",
}

CELL_NAME = re.compile(r"^(test_)?s(0[1-9]|1[0-2])_[a-z0-9]+(_[a-z0-9]+)*$")
STALE_DOMAIN = ("trivia", "pub quiz", "mopbot", "concierge", "weather_bot")

# Reviewed empty forms. Checking only function names allowed completed answers
# to slip into the learner's first run. Ignore docstrings, never executable code.
ATTEMPT_BODIES = {
    "attempt_tool_results": "proposed_results = []\nreturn proposed_results",
    "attempt_premature_fire": "return None",
    "attempt_keep_rule": "return None",
    "attempt_semantic": "return None",
    "attempt_gate": "return None",
    "attempt_route": "return None",
    "attempt_failure_view": "lines = []\nreturn '\\n'.join(lines)",
    "attempt_handover_note": "lines = []\nreturn lines",
    "attempt_thirty_second_test": "missing = []\nreturn missing",
    "attempt_open_code": "labels = {}\nreturn labels",
    "attempt_budget_gate": "refusal = None\nreturn refusal",
    "attempt_route_table": "table = {'read_note': None, 'draft_reply': None, 'till_summary': None}\nreturn table",
    "attempt_hand_labels": "return {tid: None for tid in transcripts}",
}


def unanswered_attempt(fn: ast.FunctionDef) -> bool:
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    expected = ATTEMPT_BODIES.get(fn.name)
    return expected is not None and ast.dump(ast.Module(body=body, type_ignores=[])) == ast.dump(ast.parse(expected))


def notebooks() -> list[Path]:
    return sorted(SESSIONS.glob("*/toy.py"))


def session_of(path: Path) -> str:
    return path.parent.name


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
        self.assertEqual(
            sorted(session_of(p) for p in notebooks()), sorted(EXPECTED))

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
            with self.subTest(notebook=session_of(path)):
                ast.parse(text)
                self.assertIn('__generated_with = "0.24.2"', text)
                self.assertIn('app = marimo.App(width="medium")', text)
                self.assertIn('if __name__ == "__main__":', text)

    def test_cells_are_named_and_scoped_to_their_session(self):
        for path in notebooks():
            cells = decorated(ast.parse(source(path)), "cell")
            names = [c.name for c in cells]
            with self.subTest(notebook=session_of(path)):
                self.assertNotIn("_", names, "unnamed cell: rename every `def _(`")
                self.assertEqual(len(names), len(set(names)))
                for name in names:
                    self.assertRegex(name, CELL_NAME)
                    self.assertIn(session_of(path)[:3], name)


class Seam(unittest.TestCase):
    """B1: exactly one way to reach a model."""

    def test_every_notebook_uses_the_single_model_seam(self):
        for path in notebooks():
            with self.subTest(notebook=session_of(path)):
                self.assertIn("get_client", source(path))

    def test_no_notebook_constructs_a_client_directly(self):
        for path in notebooks():
            text = source(path)
            with self.subTest(notebook=session_of(path)):
                self.assertNotIn("LiveClient(", text)
                self.assertNotIn("urllib.request", text)
                self.assertNotIn("OPENAI_API_KEY", text)


class Spine(unittest.TestCase):
    """B2: session N builds on the cafe/ module it claims."""

    def test_each_notebook_imports_the_module_its_session_ships(self):
        for path in notebooks():
            module = EXPECTED[session_of(path)]
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
            with self.subTest(notebook=session_of(path), module=module):
                self.assertTrue(found, f"{session_of(path)} must drive {module}")


class Safety(unittest.TestCase):
    def test_imports_are_stdlib_plus_marimo_and_cafe(self):
        allowed = set(sys.stdlib_module_names) | {"marimo", "cafe"}
        for path in notebooks():
            with self.subTest(notebook=session_of(path)):
                self.assertLessEqual(imported_roots(ast.parse(source(path))), allowed)

    def test_no_credentials_or_home_paths(self):
        for path in notebooks():
            text = source(path)
            with self.subTest(notebook=session_of(path)):
                self.assertNotIn("/Users/", text)
                self.assertIsNone(re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b", text))


class Domain(unittest.TestCase):
    """B3: one café, everywhere."""

    def test_no_pre_cafe_domain_nouns_survive(self):
        for path in notebooks():
            text = source(path).lower()
            for noun in STALE_DOMAIN:
                with self.subTest(notebook=session_of(path), noun=noun):
                    self.assertNotIn(noun, text)


class Pedagogy(unittest.TestCase):
    def test_every_notebook_has_two_assertion_cells(self):
        for path in notebooks():
            cells = decorated(ast.parse(source(path)), "cell")
            tests = [c for c in cells if c.name.startswith("test_")]
            with self.subTest(notebook=session_of(path)):
                self.assertGreaterEqual(len(tests), 2)

    def test_attempt_skeletons_are_unanswered(self):
        """An attempt unit must not contain the reference answer."""
        found = set()
        for path in notebooks():
            tree = ast.parse(source(path))
            attempts = [
                fn for fn in decorated(tree, "function") if fn.name.startswith("attempt_")
            ]
            for fn in attempts:
                with self.subTest(notebook=session_of(path), unit=fn.name):
                    found.add(fn.name)
                    self.assertTrue(unanswered_attempt(fn), "executable body is no longer an empty attempt")
        self.assertEqual(found, set(ATTEMPT_BODIES))

    def test_attempt_guard_rejects_prefilled_and_reference_call_mutations(self):
        for body in ("return {'a': 'pass'}", "return solution_hand_labels(key)",
                     "labels = {}\nlabels['a'] = 'pass'\nreturn labels"):
            fn = ast.parse("def attempt_hand_labels(transcripts):\n" + "\n".join("    " + line for line in body.splitlines())).body[0]
            self.assertFalse(unanswered_attempt(fn))

    def test_each_solution_is_gated_behind_a_reveal(self):
        for path in notebooks():
            tree = ast.parse(source(path))
            text = source(path)
            solutions = [
                fn for fn in decorated(tree, "function") if fn.name.startswith("solution_")
            ]
            if not solutions:
                continue
            with self.subTest(notebook=session_of(path)):
                self.assertIn("mo.ui.switch(", text)
                self.assertIn("mo.stop(", text)
                self.assertIn("inspect.getsource(", text)


if __name__ == "__main__":
    unittest.main()
