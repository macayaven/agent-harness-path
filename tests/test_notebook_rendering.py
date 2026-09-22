"""Evidence and complete explanations must survive marimo's preview surface."""

from contextlib import redirect_stdout
import ast
import base64
from importlib.util import module_from_spec, spec_from_file_location
from inspect import signature
from io import StringIO
import os
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import marimo as mo

from cafe import domain, judge, schema
from cafe.model import get_client
from notebook_support import notebook_function

ROOT = Path(__file__).resolve().parents[1]


class NotebookRenderingTests(unittest.TestCase):
    @patch.dict(os.environ, {"COURSE_MODE": "stub"})
    def test_s04_renders_replies_and_errors_from_the_actual_offline_runs(self):
        path = ROOT / "sessions/s04-structured-generation/toy.py"
        display, console = StringIO(), StringIO()
        view = SimpleNamespace(capture_stdout=mo.capture_stdout, plain_text=display.write)
        create_client = notebook_function(path, "s04_demo_client", {"get_client": get_client})
        run_tickets = notebook_function(path, "s04_demo_live", {
            "domain": domain, "ask_ticket_run": schema.ask_ticket_run})
        with redirect_stdout(console):
            (client,) = create_client(view)
            (runs,) = run_tickets(client, view)
        self.assertEqual(console.getvalue(), "")
        self.assertEqual([r["ticket"] is not None for r in runs], [True, True, False])
        for brief in domain.TICKET_BRIEFS:
            self.assertIn(brief, display.getvalue())
        for run in runs:
            for outcome in run["outcomes"]:
                self.assertIn(outcome["reply"], display.getvalue())
                for error in outcome["errors"]:
                    self.assertIn(error, display.getvalue())

    def test_every_notebook_figure_embeds_the_committed_svg_without_a_request(self):
        figures = 0
        for path in sorted((ROOT / "sessions").glob("*/toy.py")):
            source = path.read_text()
            spec = spec_from_file_location("figures_" + path.parent.name[:3], path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            for cell in ast.parse(source).body:
                if not isinstance(cell, ast.FunctionDef):
                    continue
                assets = re.findall(r"public/diagrams/([A-Za-z0-9_-]+\.svg)",
                                    ast.get_source_segment(source, cell))
                if not assets:
                    continue
                with self.subTest(session=path.parent.name, cell=cell.name):
                    output, _ = getattr(module, cell.name).run(mo=mo)
                    images = re.findall(r'<img\b[^>]*src="([^"]+)"', output.text)
                    self.assertEqual(len(images), len(assets))
                    for image, asset in zip(images, assets):
                        self.assertTrue(image.startswith("data:image/svg+xml;base64,"))
                        self.assertEqual(base64.b64decode(image.split(",", 1)[1]),
                                         (path.parent / "public/diagrams" / asset).read_bytes())
                        figures += 1
        self.assertEqual(figures, 12)

    def test_multi_argument_prints_remain_one_readable_cell_output(self):
        spec = spec_from_file_location("render_s01", ROOT / "sessions/s01-agent-loop/toy.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        output, _ = module.s01_demo_client.run(
            mo=mo, get_client=lambda: SimpleNamespace(mode="stub", model="synthetic-model"))
        self.assertIsNotNone(output)
        self.assertEqual(output.text.count("<pre"), 1)
        self.assertIn("mode : stub\nmodel: synthetic-model\n", output.text)

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
        view = SimpleNamespace(capture_stdout=mo.capture_stdout, plain_text=display.write)
        args = {"mo": view} if "mo" in signature(cell).parameters else {}
        with redirect_stdout(console):
            (transcripts,) = cell(**args)
        self.assertEqual(console.getvalue(), "")
        self.assertIn("menu facts for your labels:", display.getvalue())
        self.assertEqual(len(transcripts), 6)
        for transcript_id in transcripts:
            self.assertIn("--- " + transcript_id + " ---", display.getvalue())
