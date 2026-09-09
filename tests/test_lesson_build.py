"""Check the actual reader output and stale-source failure, without a browser dependency."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lessons'))
import build

class StaticReaderTests(unittest.TestCase):
    def test_pilot_diagram_is_static_with_meaningful_alternative_and_quiz_anchor(self):
        for name in ['S01-agent-loop','S02-golden-evals']:
            body,_,count=build.render_body(ROOT/f'lessons/src/{name}.md')
            self.assertEqual(count,1)
            self.assertIn('<img ',body)
            self.assertNotIn('<pre class="mermaid"',body)
            self.assertIn('id="self-check"',body)
            self.assertIn('<details><summary>',body)
            self.assertRegex(body,r'alt="[^\"]{70,}"')

    def test_changed_mermaid_source_is_rejected_until_rerendered(self):
        original=ROOT/'lessons/src/S01-agent-loop.md'
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/original.name
            source.write_text(original.read_text().replace('flowchart LR','flowchart TB'))
            with self.assertRaisesRegex(ValueError,'stale.*diagram'):
                build.render_body(source)

if __name__=='__main__':unittest.main()
