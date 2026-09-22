"""The S04 checkpoint must retain valid-but-wrong first attempts."""

import json
import os
import unittest
from unittest.mock import patch

from cafe import domain, schema
from cafe.model import ModelError, check_pairing, get_client
from course_test_support import ScriptedClient, call, reply


class SchemaOutcomeTests(unittest.TestCase):
    def test_ticket_request_supplies_menu_facts_without_offering_tools(self):
        good = {"table": 1, "items": ["latte"], "total_eur": 1.60, "allergen_checked": False}
        client = ScriptedClient([reply(json.dumps(good))])
        schema.ask_ticket_run(client, "One latte.")
        request = client.requests[0]
        self.assertIsNone(request["tools"])
        context = request["messages"][0]["content"]
        self.assertIn(json.dumps(domain.MENU, sort_keys=True), context)
        self.assertIn(json.dumps(list(domain.EIGHTY_SIXED)), context)

    @patch.dict(os.environ, {"COURSE_MODE": "live"})
    def test_offline_scenario_is_not_sent_to_the_live_endpoint(self):
        good = {"table": 1, "items": ["latte"], "total_eur": 1.60, "allergen_checked": False}
        client = get_client(stub_scenario="tickets", base_url="https://model.invalid/v1",
                            api_key="test-key", model="test-model")
        with patch("cafe.model._post_chat_completions",
                   return_value=json.dumps(reply(json.dumps(good))).encode()) as transport:
            run = schema.ask_ticket_run(client, "One latte.")
        self.assertEqual(run["ticket"], good)
        self.assertEqual(client.mode, "live")
        body = json.loads(transport.call_args.kwargs["data"])
        self.assertEqual(body["model"], "test-model")
        self.assertNotIn("tools", body)
        self.assertNotIn("stub_scenario", body)

    @patch.dict(os.environ, {"COURSE_MODE": "stub"})
    def test_edited_brief_cannot_silently_reuse_an_unrelated_fixture(self):
        client = get_client(stub_scenario="tickets")
        with self.assertRaisesRegex(ModelError, "offline ticket fixtures"):
            schema.ask_ticket_run(client, "Table 3: an espresso.")
        self.assertEqual(client.calls, 1)

    def test_unexpected_tool_calls_are_denied_even_alongside_a_valid_ticket(self):
        good = {"table": 1, "items": ["latte"], "total_eur": 1.60, "allergen_checked": False}
        calls = [call("fire_ticket", {"items": ["latte"], "table": 1}, "fire"),
                 call("close_check", {"table": 1}, "close")]
        client = ScriptedClient([reply(json.dumps(good), tool_calls=calls), reply(json.dumps(good))])
        run = schema.ask_ticket_run(client, "One latte.")
        self.assertEqual(run["attempts"], 2)
        self.assertEqual(run["ticket"], good)
        self.assertEqual(run["outcomes"][0]["stage"], "channel")
        denied = [m for m in run["messages"] if m["role"] == "tool"]
        self.assertEqual([m["tool_call_id"] for m in denied], ["fire", "close"])
        self.assertEqual([json.loads(m["content"])["error"] for m in denied],
                         ["tools_disabled", "tools_disabled"])
        self.assertIn("CHANNEL ERROR", client.requests[1]["messages"][-1]["content"])
        check_pairing(run["messages"])

    @patch.dict(os.environ, {"COURSE_MODE": "stub"})
    def test_offline_briefs_exercise_each_gate_and_repeat_on_the_same_client(self):
        client = get_client(stub_scenario="tickets")
        expected_stages = [["parse", "shape", "accepted"],
                           ["meaning", "accepted"], ["meaning"] * 3]
        for _ in range(2):  # marimo reruns must not consume a global fixture queue
            runs = [schema.ask_ticket_run(client, brief) for brief in domain.TICKET_BRIEFS]
            self.assertEqual([[o["stage"] for o in r["outcomes"]] for r in runs], expected_stages)
            self.assertEqual(runs[0]["ticket"], {
                "table": 4, "items": ["latte", "tomato toast"],
                "total_eur": 4.0, "allergen_checked": False})
            self.assertEqual(runs[1]["ticket"], {
                "table": 2, "items": ["chocolate croissant", "chocolate croissant", "orange juice"],
                "total_eur": 6.7, "allergen_checked": False})
            self.assertIsNone(runs[2]["ticket"])
            for run in runs:
                check_pairing(run["messages"])
                self.assertLessEqual(run["attempts"], 3)
                for outcome in run["outcomes"]:
                    if outcome["stage"] != "accepted":
                        self.assertTrue(outcome["errors"])

    def test_semantic_failure_survives_a_successful_repair(self):
        good = {"table": 1, "items": ["latte"], "total_eur": 1.60, "allergen_checked": False}
        client = ScriptedClient([reply(json.dumps({**good, "total_eur": 2.50})), reply(json.dumps(good))])
        run = schema.ask_ticket_run(client, "One latte.")
        self.assertEqual(run["ticket"], good)
        self.assertEqual(run["attempts"], 2)
        self.assertEqual([(o["parsed"], o["shape_ok"], o["semantic_ok"]) for o in run["outcomes"]],
                         [(True, True, False), (True, True, True)])
        self.assertTrue(run["outcomes"][0]["semantic_errors"])
        self.assertIn("SEMANTIC ERRORS", client.requests[1]["messages"][-1]["content"])

    def test_parse_and_shape_failures_remain_visible_at_the_cap(self):
        client = ScriptedClient([reply("No object"), reply('{"table": true}')])
        run = schema.ask_ticket_run(client, "One latte.", max_attempts=2)
        self.assertIsNone(run["ticket"])
        self.assertEqual(run["attempts"], 2)
        self.assertEqual([(o["parsed"], o["shape_ok"], o["semantic_ok"]) for o in run["outcomes"]],
                         [(False, False, None), (True, False, None)])
        self.assertTrue(run["outcomes"][1]["shape_errors"])

    def test_tuple_wrapper_still_returns_the_accepted_ticket(self):
        good = {"table": 1, "items": ["latte"], "total_eur": 1.60, "allergen_checked": False}
        result = schema.ask_ticket(ScriptedClient([reply(json.dumps(good))]), "One latte.")
        self.assertEqual(result[0], good)
        self.assertEqual(result[2], 1)
