"""Real-model comparison fixtures must replay their intended teaching outcomes."""

import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cafe import domain, schema
from cafe.trace import RecordingClient, ReplayClient
from course_test_support import ScriptedClient, reply

ROOT = Path(__file__).resolve().parents[1]


class RecordedFixtureTests(unittest.TestCase):
    def tool(self):
        self.assertTrue((ROOT / "tools/record_fixtures.py").is_file(), "record/replay entry point missing")
        return importlib.import_module("tools.record_fixtures")

    def test_s04_recording_accepts_ordinary_orders_and_withholds_unavailable_order(self):
        path = ROOT / "sessions/s04-structured-generation/recordings/model.jsonl"
        self.assertTrue(path.is_file(), "S04 real-model recording missing")
        client = ReplayClient(path)
        runs = [schema.ask_ticket_run(client, brief) for brief in domain.TICKET_BRIEFS]
        client.assert_exhausted()
        self.assertEqual(runs[0]["ticket"]["items"], ["latte", "tomato toast"])
        self.assertEqual(runs[1]["ticket"]["items"], ["chocolate croissant", "chocolate croissant", "orange juice"])
        self.assertIsNone(runs[2]["ticket"])
        self.assertEqual(runs[2]["stop_reason"], "attempt_cap")
        self.assertEqual(runs[2]["attempts"], 3)
        self.assertTrue(any(o["stage"] == "meaning" for o in runs[2]["outcomes"]))

    def test_every_recorded_comparison_replays_and_exercises_its_purpose(self):
        tool = self.tool()
        for session, path in tool.CASES.items():
            with self.subTest(session=session):
                self.assertTrue(path.is_file(), f"{session} recording missing")
                client = ReplayClient(path)
                result = tool.run_case(session, client)
                client.assert_exhausted()
                self.assertEqual(tool.admission_errors(session, result), [])
                for entry in client.entries:
                    self.assertIn(entry["response"]["choices"][0]["finish_reason"], {"stop", "tool_calls"})

    def test_public_recording_preserves_protocol_but_removes_provider_metadata(self):
        tool = self.tool()
        response = reply("One synthetic fixture reply.", usage={"prompt_tokens": 4, "completion_tokens": 3, "total_tokens": 7})
        response["model"] = "private-route-alias"
        response["choices"][0]["message"]["reasoning_content"] = "private reasoning"
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "recording.jsonl"
            recorder = RecordingClient(tool.PublicFixtureClient(ScriptedClient([response])), path)
            recorder.chat([{"role": "user", "content": "A synthetic café request."}])
            saved = json.loads(path.read_text())
        self.assertNotIn("model", saved["response"])
        self.assertNotIn("private reasoning", json.dumps(saved))
        self.assertEqual(saved["response"]["choices"][0]["message"]["content"], "One synthetic fixture reply.")
        self.assertEqual(saved["response"]["usage"]["total_tokens"], 7)
