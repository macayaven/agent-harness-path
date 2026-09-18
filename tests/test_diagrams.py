"""Notebook figures resolve to fresh committed SVGs under notebooks/public/."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lessons"))

import static_diagrams as sd  # noqa: E402

PUBLIC = ROOT / "notebooks" / "public" / "diagrams"
FIGURE = re.compile(r"\]\(public/diagrams/([^)]+\.svg)\)")


def notebook_sources():
    return sorted(PUBLIC.glob("*.mmd"))


def receipt():
    return json.loads(
        (ROOT / "lessons" / "diagrams" / "receipt.json").read_text()
    )["diagrams"]


class NotebookDiagramTests(unittest.TestCase):
    def test_no_live_mermaid_in_notebooks(self):
        """Cells embed committed SVGs; no frontend mermaid rendering is used."""
        for nb in sorted((ROOT / "notebooks").glob("s*_toy.py")):
            with self.subTest(notebook=nb.name):
                self.assertNotIn("mo.mermaid", nb.read_text())

    def test_notebook_renders_fresh(self):
        """Each .mmd source has a fresh receipt-pinned SVG under public/."""
        entries = receipt()
        sources = notebook_sources()
        self.assertTrue(sources, "no notebook .mmd sources")
        for src in sources:
            with self.subTest(asset=src.stem):
                svg = PUBLIC / f"{src.stem}.svg"
                self.assertTrue(svg.is_file(), f"missing render for {src.name}")
                entry = entries.get(src.stem, {})
                self.assertEqual(
                    entry.get("inputs"), sd.inputs(src.read_text().strip())
                )
                self.assertEqual(entry.get("svg_sha256"), sd.sha(svg.read_bytes()))

    def test_lesson_copies_identical(self):
        """public/ lesson copies are byte-identical to lessons/diagrams/."""
        entries = receipt()
        self.assertTrue(sd.PUBLIC_LESSON_ASSETS, "no public lesson assets listed")
        for asset in sorted(sd.PUBLIC_LESSON_ASSETS):
            with self.subTest(asset=asset):
                original = ROOT / "lessons" / "diagrams" / f"{asset}.svg"
                copy = PUBLIC / f"{asset}.svg"
                self.assertTrue(original.is_file(), f"missing {original}")
                self.assertTrue(copy.is_file(), f"missing {copy}")
                self.assertEqual(copy.read_bytes(), original.read_bytes())
                entry = entries.get(f"public/{asset}", {})
                self.assertEqual(
                    entry.get("svg_sha256"), sd.sha(copy.read_bytes())
                )

    def test_notebook_figure_references_resolve(self):
        """Every markdown figure in every notebook resolves to a real SVG."""
        notebooks = sorted((ROOT / "notebooks").glob("s*_toy.py"))
        self.assertTrue(notebooks, "no notebooks found")
        for nb in notebooks:
            with self.subTest(notebook=nb.name):
                refs = FIGURE.findall(nb.read_text())
                self.assertTrue(refs, f"{nb.name} embeds no figure")
                for name in refs:
                    svg = PUBLIC / name
                    self.assertTrue(svg.is_file(), f"missing {svg}")
                    self.assertIn("<svg", svg.read_text(encoding="utf-8"))
