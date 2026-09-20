"""Onboarding reports what actually ran and checks the learner's implementation."""

import contextlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cafe import doctor, model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "labs"))
import run as runner


class DoctorTests(unittest.TestCase):
    def run_doctor(self, env, **transport_options):
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env, clear=True), \
                patch.object(model, "_post_chat_completions", **transport_options) as transport, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = doctor.main()
        return code, out.getvalue(), err.getvalue(), transport

    def test_default_proves_only_stub_and_never_contacts_transport(self):
        code, out, err, transport = self.run_doctor({})
        self.assertEqual((code, err), (0, ""))
        self.assertIn("offline stub works; no endpoint was contacted", out)
        self.assertNotIn("endpoint works", out)
        transport.assert_not_called()

    def test_unconfigured_live_fails_before_transport(self):
        code, out, err, transport = self.run_doctor({"COURSE_MODE": "live"})
        self.assertEqual(code, 1)
        self.assertIn("configuration problem", err)
        self.assertIn("CAFE_BASE_URL", err)
        self.assertNotIn("responded", out)
        transport.assert_not_called()

    def test_live_success_follows_a_real_client_transport_response(self):
        env = {"COURSE_MODE": "live", "CAFE_BASE_URL": "http://model.invalid/v1",
               "CAFE_API_KEY": "synthetic-test-credential", "CAFE_MODEL": "test-model"}
        response = {"choices": [{"message": {"role": "assistant", "content": "ready"}}]}
        code, out, err, transport = self.run_doctor(env, return_value=json.dumps(response).encode())
        self.assertEqual((code, err), (0, ""))
        transport.assert_called_once()
        self.assertIn("live endpoint responded", out)
        self.assertNotIn(env["CAFE_API_KEY"], out + err)

    def test_live_transport_failure_does_not_claim_success(self):
        env = {"COURSE_MODE": "live", "CAFE_BASE_URL": "http://model.invalid/v1",
               "CAFE_API_KEY": "synthetic-test-credential", "CAFE_MODEL": "test-model"}
        code, out, err, transport = self.run_doctor(
            env, side_effect=model._TransportError("timeout", "test timeout"))
        self.assertEqual(code, 1)
        transport.assert_called_once()
        self.assertIn("call failed", err)
        self.assertNotIn("responded", out)


class DocumentedCommandsTests(unittest.TestCase):
    def test_s06_command_exposes_a_broken_student_medical_gate(self):
        text = (ROOT / "sessions/s06-layered-detection/lab.md").read_text()
        command = re.search(r"^uv run python labs/run.py --session s06[^\n]*", text, re.M).group()
        broken = SimpleNamespace(run_engine=lambda *args, **kwargs: {"stop_reason": "answered"})
        reference = SimpleNamespace(run_engine=lambda *args, **kwargs: {"stop_reason": "policy_refusal"})
        with patch.object(runner, "load_impl", side_effect=lambda name: (
                broken if name == "student" else reference, None)) as load_impl, \
                patch.dict(runner.SESSION_TASKS, {"s06": []}), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = runner.main(shlex.split(command)[4:])
        load_impl.assert_called_once_with("student")
        self.assertEqual(code, 1)
        self.assertIn("FAIL s06 medical gate", out.getvalue())
