"""The app must send CLI tokens, preserve selections, and show learner failures."""

import contextlib
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import marimo as mo
from notebook_support import notebook_function

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "labs"))
import run as runner


class LabArgumentsTests(unittest.TestCase):
    def test_default_controls_are_accepted_by_real_parser(self):
        controls = notebook_function(ROOT / "labs/app.py", "lab_controls")(mo)
        _go, impl, mode, session, _tasks = controls
        args = runner.build_parser().parse_args(
            ["--session", session.value, "--impl", impl.value, "--" + mode.value])
        self.assertEqual((args.session, args.impl, args.replay), ("s01", "student", True))

    def test_every_combination_preserves_selected_tokens(self):
        from labs.ui import build_argv
        for session in [f"s{i:02d}" for i in range(1, 13)] + ["all"]:
            for impl in ("student", "reference"):
                for mode in ("replay", "live", "record"):
                    with self.subTest(session=session, impl=impl, mode=mode):
                        args = runner.build_parser().parse_args(build_argv(session, impl, mode))
                        self.assertEqual(args.impl, impl)
                        self.assertEqual(args.all, session == "all")
                        self.assertEqual(runner.parse_mode(args), mode)
        self.assertEqual(build_argv("all", "reference", "replay", " p01,p02 "),
                         ["--all", "--impl", "reference", "--replay", "--tasks", "p01,p02"])

    def test_descriptions_and_unknown_tokens_are_rejected(self):
        from labs.ui import build_argv
        for values in (("bad", "student", "replay"),
                       ("s01", "student (cafe_host)", "replay"),
                       ("s01", "student", "replay (default, offline)")):
            with self.subTest(values=values), self.assertRaises(ValueError):
                build_argv(*values)

    def test_broken_student_gate_has_nonzero_status(self):
        broken = SimpleNamespace(run_engine=lambda *a, **kw: {"stop_reason": "answered", "state": {}})
        for impl in ("student", "reference"):
            with self.subTest(impl=impl), patch.object(runner, "load_impl", return_value=(broken, None)), \
                    patch.dict(runner.SESSION_TASKS, {"s06": []}), contextlib.redirect_stdout(io.StringIO()) as out:
                code = runner.main(["--session", "s06", "--impl", impl, "--replay"])
            self.assertIn("FAIL s06 medical gate", out.getvalue())
            self.assertEqual(code, 1)
