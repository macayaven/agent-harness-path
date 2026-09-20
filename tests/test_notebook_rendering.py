"""Evidence and complete explanations must survive marimo's preview surface."""

from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
from inspect import signature
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest

import marimo as mo

from cafe import domain, judge
from notebook_support import notebook_function

ROOT = Path(__file__).resolve().parents[1]


class NotebookRenderingTests(unittest.TestCase):
    def test_theory_output_contains_the_diagram_and_surrounding_explanation(self):
        cases = (
            ("s01-agent-loop", "s01_md_api_shape", "The API is stateless", "Trace that"),
            ("s04-structured-generation", "s04_md_contract", "The contract", "shape"),
            ("s05-consent-gate", "s05_md_theory", "The gate", "consent"),
            ("s06-layered-detection", "s06_md_theory", "The order is the safety invariant", "classifier"),
            ("s08-observability-replay", "s08_md_record", "A recording is a contract", "ReplayClient"),
            ("s11-budgets-routing", "s11_md_theory", "The theory in depth", "budget"),
            ("s12-judge-calibration", "s12_md_theory", "The theory in depth", "undefined"),
        )
        for slug, name, before, after in cases:
            with self.subTest(session=slug):
                spec = spec_from_file_location("render_" + slug[:3], ROOT / "sessions" / slug / "toy.py")
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                output, _ = getattr(module, name).run(mo=mo)
                self.assertIn(before, output.text)
                self.assertIn(after, output.text)
                self.assertIn("<img", output.text)

    def test_blind_corpus_is_a_cell_output_not_only_console_history(self):
        cell = notebook_function(ROOT / "sessions/s12-judge-calibration/toy.py",
                                 "s12_demo_corpus", {"domain": domain, "judge": judge})
        display, console = StringIO(), StringIO()
        view = SimpleNamespace(redirect_stdout=lambda: redirect_stdout(display))
        args = {"mo": view} if "mo" in signature(cell).parameters else {}
        with redirect_stdout(console):
            (transcripts,) = cell(**args)
        self.assertEqual(console.getvalue(), "")
        self.assertIn("menu facts for your labels:", display.getvalue())
        self.assertEqual(len(transcripts), 6)
        for transcript_id in transcripts:
            self.assertIn("--- " + transcript_id + " ---", display.getvalue())
