"""The S04 checkpoint must retain valid-but-wrong first attempts."""

import json
import unittest
from cafe import schema
from course_test_support import ScriptedClient, reply


class SchemaOutcomeTests(unittest.TestCase):
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
