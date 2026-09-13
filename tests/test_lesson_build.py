"""Check the actual reader output and stale-source failure, without a browser dependency."""
import importlib.util
import json
from pathlib import Path
import posixpath
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lessons'))
import build

DIAGRAMS = {
    'study-plan': ['study-plan.svg'],
    'S01-agent-loop': ['S01-agent-loop.svg'],
    'S02-golden-evals': ['S02-golden-evals.svg'],
    'S03-context-engineering': ['S03-context-engineering.svg'],
    'S04-structured-generation': ['S04-structured-generation.svg'],
    'S05-consent-gate': ['S05-consent-gate.svg'],
    'S06-layered-detection': ['S06-layered-detection.svg'],
    'S07-repair-loop': ['S07-repair-loop.svg'],
    'S08-observability-replay': [
        'S08-observability-replay.svg',
        'S08-observability-replay-2.svg',
    ],
    'S09-evidence-reports': ['S09-evidence-reports.svg'],
    'S10-error-analysis': ['S10-error-analysis.svg'],
    'S11-budgets-routing': ['S11-budgets-routing.svg'],
    'S12-judge-calibration': ['S12-judge-calibration.svg'],
    'S13-rebuild-from-memory': ['S13-rebuild-from-memory.svg'],
    'S14-ship-and-pilot': [
        'S14-ship-and-pilot.svg',
        'S14-ship-and-pilot-2.svg',
    ],
}

class StaticReaderTests(unittest.TestCase):
    def test_generated_native_links_resolve_to_one_allowlisted_surface(self):
        manifest = json.loads((ROOT / 'courseweave.json').read_text())
        surfaces = [
            surface
            for module in manifest['modules']
            for phase in module['phases']
            for surface in phase['surfaces']
            if surface.get('path')
        ]
        failures = []
        for page in sorted((ROOT / 'lessons').glob('*.html')):
            document = page.read_text()
            ids = set(re.findall(r'\bid="([A-Za-z][A-Za-z0-9_.:-]*)"', document))
            for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', document):
                target = urlsplit(href)
                if target.scheme:
                    self.assertEqual(target.scheme, 'https', href)
                    continue
                self.assertFalse(target.netloc, href)
                self.assertFalse(target.query, href)
                path = posixpath.normpath(
                    posixpath.join('lessons', page.name, '..', unquote(target.path))
                )
                fragment = unquote(target.fragment)
                matches = [
                    surface
                    for surface in surfaces
                    if surface['path'] == path
                    and (
                        surface['type'] != 'html'
                        or surface.get('fragment', '') == fragment
                    )
                ]
                same_document = (
                    path == f'lessons/{page.name}' and fragment in ids
                )
                if len(matches) != 1 and not (len(matches) == 0 and same_document):
                    failures.append((page.name, href, len(matches)))
        self.assertEqual(failures, [])

    def test_every_lesson_diagram_is_static_with_a_specific_alternative(self):
        alternatives = []
        for name, expected_assets in DIAGRAMS.items():
            body,_,count=build.render_body(ROOT/f'lessons/src/{name}.md')
            self.assertEqual(count,len(expected_assets),name)
            self.assertNotIn('<pre class="mermaid"',body)
            images = re.findall(
                r'<img class="static-diagram" src="diagrams/([^\"]+)" alt="([^\"]+)"',
                body,
            )
            self.assertEqual([asset for asset, _ in images], expected_assets, name)
            for _, alternative in images:
                self.assertGreaterEqual(len(alternative), 70, name)
                self.assertNotIn('described in surrounding prose', alternative)
                alternatives.append(alternative)

        self.assertEqual(len(alternatives), 17)
        self.assertEqual(len(set(alternatives)), 17)

    def test_reader_keeps_quiz_anchors_and_needs_no_mermaid_javascript(self):
        for name in (name for name in DIAGRAMS if name.startswith('S')):
            body,_,_=build.render_body(ROOT/f'lessons/src/{name}.md')
            self.assertIn('id="self-check"',body)
            self.assertIn('<details><summary>',body)
        rendered,_=build.render(
            ROOT/'lessons/src/S14-ship-and-pilot.md',
            '<nav></nav>',
        )
        self.assertNotIn('mermaid.min.js',rendered)
        self.assertNotIn('<script',rendered)

    def test_wide_diagram_keeps_its_readable_width_in_a_scroll_region(self):
        body,_,_=build.render_body(ROOT/'lessons/src/S13-rebuild-from-memory.md')
        self.assertIn('<div class="static-diagram-scroll" tabindex="0">',body)
        self.assertIn('style="--diagram-width: 2215px"',body)

    def test_static_svg_preserves_comparison_text(self):
        svg=(ROOT/'lessons/diagrams/S06-layered-detection.svg').read_text()
        self.assertNotIn('&amp;gt;=',svg)
        self.assertIn('confidence &gt;= threshold?',svg)

    def test_changed_mermaid_source_in_a_multi_diagram_lesson_is_rejected(self):
        original=ROOT/'lessons/src/S14-ship-and-pilot.md'
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/original.name
            source.write_text(original.read_text().replace('flowchart LR','flowchart TB'))
            with self.assertRaisesRegex(ValueError,'stale.*diagram'):
                build.render_body(source)

    def test_unconfigured_mermaid_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'new-lesson.md'
            source.write_text('# New lesson\n\n```mermaid\nflowchart LR\nA --> B\n```\n')
            with self.assertRaisesRegex(ValueError,'no static diagram configuration'):
                build.render_body(source)

if __name__=='__main__':unittest.main()
