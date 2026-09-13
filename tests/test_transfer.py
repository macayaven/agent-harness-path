import json
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]

class TransferTests(unittest.TestCase):
    def test_two_concrete_variants_are_available_without_answers_or_network(self):
        path=ROOT/'study/transfer/fixtures.json'
        self.assertTrue(path.is_file())
        fixtures=json.loads(path.read_text())
        self.assertEqual(set(fixtures),{'immediate','delayed'})
        for variant,fixture in fixtures.items():
            self.assertEqual(len(fixture['user_script']),2)
            self.assertEqual(len(fixture['assistant_replies']),3)
            self.assertNotIn('correct',json.dumps(fixture))
            result=subprocess.run([sys.executable,str(ROOT/'study/transfer/attempt.py'),'--variant',variant],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Attempt pending',result.stdout)
            self.assertNotIn('rubric',result.stdout.lower())

if __name__=='__main__':unittest.main()
