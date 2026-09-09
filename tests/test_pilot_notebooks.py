"""Verify added attempts are real learner work and original cells remain byte-semantically intact."""
import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

def digest(cell):
    return hashlib.sha256(json.dumps(cell,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class NotebookTests(unittest.TestCase):
    def test_original_cells_ids_sources_metadata_and_outputs_are_preserved(self):
        receipt=json.loads((ROOT/'tests/fixtures/original-notebook-cells.json').read_text())
        for name,original in receipt.items():
            cells=json.loads((ROOT/name).read_text())['cells']
            ids=[c['id'] for c in cells]
            self.assertEqual([i for i in ids if i in original],list(original))
            for cell in cells:
                if cell['id'] in original:self.assertEqual(digest(cell),original[cell['id']])
                if cell['cell_type']=='code':
                    self.assertIsNone(cell['execution_count']);self.assertEqual(cell['outputs'],[])

    def test_attempts_are_unanswered_and_references_stay_out_of_notebook_grounding(self):
        for name,prefix in [('s01_agent_loop_toy','s01'),('s02_scripted_user_eval_toy','s02')]:
            cells={c['id']:c for c in json.loads((ROOT/f'notebooks/{name}.ipynb').read_text())['cells']}
            self.assertIn(prefix+'-attempt-code',cells)
            code=''.join(cells[prefix+'-attempt-code']['source'])
            self.assertNotIn('SOLUTION',code)
            self.assertIn('Attempt pending',code)
            self.assertIn('proposed_results = []' if prefix=='s01' else 'return None',code)
            self.assertIn('turn cap' if prefix=='s01' else 'seeded', ''.join(cells[prefix+'-attempt-prompt']['source']))

if __name__=='__main__':unittest.main()
