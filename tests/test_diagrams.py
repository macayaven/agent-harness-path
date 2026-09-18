"""Session figures resolve to fresh committed SVGs in per-session public/ dirs."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import static_diagrams as sd  # noqa: E402

SESSIONS = ROOT / "sessions"
FIGURE = re.compile(r"\]\(public/diagrams/([^)]+\.svg)\)")


def notebook_sources():
    out = []
    for asset, session in sorted(sd.NOTEBOOK_SESSIONS.items()):
        out.append(SESSIONS / session / "public" / "diagrams" / f"{asset}.mmd")
    return out


def receipt():
    return json.loads((ROOT / "tools" / "receipt.json").read_text())["diagrams"]


class SessionDiagramTests(unittest.TestCase):
    def test_no_live_mermaid_in_toys(self):
        """Toys embed committed SVGs; no frontend mermaid rendering is used."""
        toys = sorted(SESSIONS.glob("*/toy.py"))
        self.assertEqual(len(toys), 12)
        for toy in toys:
            with self.subTest(toy=toy.parent.name):
                self.assertNotIn("mo.mermaid", toy.read_text())

    def test_notebook_renders_fresh(self):
        """Each .mmd source has a fresh receipt-pinned SVG next to it."""
        entries = receipt()
        sources = notebook_sources()
        self.assertTrue(sources, "no notebook .mmd sources")
        for src in sources:
            with self.subTest(asset=src.stem):
                svg = src.with_suffix(".svg")
                self.assertTrue(svg.is_file(), f"missing render for {src.name}")
                entry = entries.get(src.stem, {})
                self.assertEqual(
                    entry.get("inputs"), sd.inputs(src.read_text().strip())
                )
                self.assertEqual(entry.get("svg_sha256"), sd.sha(svg.read_bytes()))

    def test_lesson_renders_fresh(self):
        """Each lesson mermaid block has a fresh receipt-pinned SVG."""
        entries = receipt()
        for slug in sorted(sd.ALTERNATIVES):
            source = sd.lesson_source(slug).read_text()
            blocks = re.findall(r"```mermaid\n(.*?)```", source, re.S)
            expected = [sd.asset_name(slug, i) for i in range(len(blocks))]
            self.assertEqual(len(blocks), len(sd.ALTERNATIVES[slug]), slug)
            for asset in expected:
                with self.subTest(asset=asset):
                    svg = sd.diagram_path(slug, asset)
                    self.assertTrue(svg.is_file(), f"missing {svg}")
                    entry = entries.get(asset, {})
                    self.assertEqual(
                        entry.get("svg_sha256"), sd.sha(svg.read_bytes()))

    def test_session_figure_references_resolve(self):
        """Every markdown figure in every toy resolves to a real SVG."""
        toys = sorted(SESSIONS.glob("*/toy.py"))
        self.assertTrue(toys, "no toys found")
        for toy in toys:
            with self.subTest(session=toy.parent.name):
                refs = FIGURE.findall(toy.read_text())
                self.assertTrue(refs, f"{toy.parent.name} embeds no figure")
                for name in refs:
                    svg = toy.parent / "public" / "diagrams" / name
                    self.assertTrue(svg.is_file(), f"missing {svg}")
                    self.assertIn("<svg", svg.read_text(encoding="utf-8"))
