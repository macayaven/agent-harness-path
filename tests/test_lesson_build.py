"""Check the actual reader output and stale-source failure, without a browser dependency."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build
import static_diagrams as sd

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
    def test_every_lesson_diagram_is_static_with_a_specific_alternative(self):
        alternatives = []
        for name, expected_assets in DIAGRAMS.items():
            body,_,count=build.render_body(sd.lesson_source(name),name)
            self.assertEqual(count,len(expected_assets),name)
            self.assertNotIn('<pre class="mermaid"',body)
            images = re.findall(
                r'<img class="static-diagram" src="public/diagrams/([^\"]+)" alt="([^\"]+)"',
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
            body,_,_=build.render_body(sd.lesson_source(name),name)
            self.assertIn('id="self-check"',body)
            self.assertIn('<details><summary>',body)
        rendered,_=build.render(
            sd.lesson_source('S14-ship-and-pilot'),
            'S14-ship-and-pilot',
            ROOT/'sessions/s14-ship-and-pilot/lesson.html',
            '<nav></nav>',
        )
        self.assertNotIn('mermaid.min.js',rendered)
        self.assertNotIn('<script',rendered)

    def test_wide_diagram_keeps_its_readable_width_in_a_scroll_region(self):
        body,_,_=build.render_body(
            sd.lesson_source('S13-rebuild-from-memory'),'S13-rebuild-from-memory')
        self.assertIn('<div class="static-diagram-scroll" tabindex="0">',body)
        self.assertIn('style="--diagram-width: 2215px"',body)

    def test_static_svg_preserves_comparison_text(self):
        svg=sd.diagram_path(
            'S06-layered-detection','S06-layered-detection').read_text()
        self.assertNotIn('&amp;gt;=',svg)
        self.assertIn('confidence &gt;= threshold?',svg)

    def test_changed_mermaid_source_in_a_multi_diagram_lesson_is_rejected(self):
        original=sd.lesson_source('S14-ship-and-pilot')
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/original.name
            source.write_text(original.read_text().replace('flowchart LR','flowchart TB'))
            with self.assertRaisesRegex(ValueError,'stale.*diagram'):
                build.render_body(source,'S14-ship-and-pilot')

    def test_unconfigured_mermaid_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'new-lesson.md'
            source.write_text('# New lesson\n\n```mermaid\nflowchart LR\nA --> B\n```\n')
            with self.assertRaisesRegex(ValueError,'no static diagram configuration'):
                build.render_body(source,'new-lesson')

class SourceLinkTests(unittest.TestCase):
    def test_py_and_md_hrefs_are_unlinked_but_text_survives(self):
        html = build.unlink_source_hrefs(
            '<p>Open <a href="toy.py"><code>toy.py</code></a> and '
            '<a href="../s02-golden-evals/toy.py">the toy</a>; '
            'read <a href="lab.md"><code>lab.md</code></a>.</p>'
        )
        self.assertNotIn('<a', html)
        self.assertIn('<code>toy.py</code>', html)
        self.assertIn('the toy', html)
        self.assertIn('<code>lab.md</code>', html)

    def test_lesson_and_external_hrefs_survive(self):
        html = build.unlink_source_hrefs(
            '<a href="../s02-golden-evals/lesson.html#the-theory-in-depth">'
            'S02</a> <a href="https://example.com/x.py">docs</a>'
        )
        self.assertIn('href="../s02-golden-evals/lesson.html#the-theory-in-depth"', html)
        self.assertIn('href="https://example.com/x.py"', html)

    def test_built_pages_carry_no_local_source_hrefs(self):
        seen = []
        for directory, slug, out in build.PAGES:
            rendered, _ = build.render(
                build.page_source(directory, slug), slug,
                ROOT / 'sessions' / directory / out, '<nav></nav>',
            )
            seen += re.findall(r'href="([^"]+)"', rendered)
        local_source = [
            href for href in seen
            if '://' not in href
            and href.split('#', 1)[0].split('?', 1)[0].endswith(('.py', '.md'))
        ]
        self.assertEqual(local_source, [])
        s01, _ = build.render(
            build.page_source('s01-agent-loop', 'S01-agent-loop'),
            'S01-agent-loop',
            ROOT / 'sessions/s01-agent-loop/lesson.html', '<nav></nav>',
        )
        self.assertIn('<code>toy.py</code>', s01)
        self.assertIn('../s02-golden-evals/lesson.html#the-theory-in-depth', s01)

if __name__=='__main__':unittest.main()
