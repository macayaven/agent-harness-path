"""Compaction observations must describe the actual request, not a parallel story."""

from copy import deepcopy
from contextlib import nullcontext, redirect_stdout
from io import StringIO
from types import SimpleNamespace
import unittest

from cafe import context
from cafe.loop import run_shift
from cafe.model import StubClient
from pathlib import Path
import ast
from notebook_support import notebook_function
from course_test_support import ScriptedClient, call, reply


class ContextWireTests(unittest.TestCase):
    def test_empty_system_is_not_replaced(self):
        client = ScriptedClient([reply()])
        run_shift(client, ["Current request."], system="")
        self.assertEqual(client.requests[0]["messages"][0]["content"], "")

    def test_initial_history_reaches_wire_without_mutating_input(self):
        history = [{"role": "user", "content": "Earlier instruction."},
                   {"role": "assistant", "content": "Understood."},
                   {"role": "user", "content": "Current request."}]
        before = deepcopy(history)
        client = ScriptedClient([reply()])
        run_shift(client, [], initial_messages=history)
        self.assertEqual(client.requests[0]["messages"], before)
        self.assertEqual(history, before)
        with self.assertRaises(ValueError):
            run_shift(client, [], initial_messages=history, system="")

    def test_kept_history_and_every_request_are_observed(self):
        client = ScriptedClient([reply(None, [call("price_check", {"item": "latte"})]),
                                 reply("First reply."), reply("Second reply.")])
        log, history = context.drive(client, context.policy_keep_all, 2, hard_limit=1000)
        self.assertEqual(len(client.requests), 3)
        self.assertEqual(sum(m["role"] == "user" for m in client.requests[-1]["messages"]), 2)
        observed = [r for entry in log for r in entry["requests"]]
        self.assertEqual(len(observed), 3)
        for observation, wire in zip(observed, client.requests):
            self.assertEqual(observation["messages"], wire["messages"])
            self.assertEqual(observation["word_count_proxy"], context.tokens(wire["messages"]))
            self.assertEqual(observation["rule_present"], context.rule_is_present(wire["messages"]))
            self.assertFalse(any("pinned" in m for m in wire["messages"]))
        self.assertTrue(any(m["role"] == "tool" for m in history))

    def test_dropped_system_rule_is_not_restored(self):
        client = ScriptedClient([reply()])
        log, _ = context.drive(client, lambda h, b: ([h[-1]], True), 1)
        self.assertFalse(context.rule_is_present(client.requests[0]["messages"]))
        self.assertFalse(log[0]["rule_present"])

    def test_policies_keep_complete_tool_batches_and_latest_request(self):
        history = [context.rule_message(pinned=True),
                   {"role": "user", "content": "Old " * 30},
                   {"role": "assistant", "content": None, "tool_calls": [
                       call("price_check", {"item": "latte"}, "a"),
                       call("price_check", {"item": "espresso"}, "b")]},
                   {"role": "tool", "tool_call_id": "a", "content": "old " * 20},
                   {"role": "tool", "tool_call_id": "b", "content": "old " * 20},
                   {"role": "user", "content": "Current request."}]
        for policy in (context.policy_truncate, context.policy_summarize, context.policy_pinned):
            with self.subTest(policy=policy.__name__):
                compacted, changed = policy(history, 35)
                self.assertTrue(changed)
                self.assertTrue(context.rule_is_present(compacted))
                self.assertEqual(compacted[-1], history[-1])
                calls = {c["id"] for m in compacted for c in m.get("tool_calls", [])}
                results = {m["tool_call_id"] for m in compacted if m["role"] == "tool"}
                self.assertEqual(calls, results)

    def test_impossible_budget_keeps_pin_and_current_request(self):
        history = [context.rule_message(pinned=True), {"role": "user", "content": "Current."}]
        kept, _ = context.policy_pinned(history, 1)
        self.assertTrue(context.rule_is_present(kept))
        self.assertEqual(kept[-1], history[-1])
        self.assertGreater(context.tokens(kept), 1)

    def test_hard_limit_checks_initial_and_tool_continuation_before_dispatch(self):
        client = ScriptedClient([])
        with self.assertRaises(context.ContextWindowExceeded):
            context.drive(client, context.policy_keep_all, 1, hard_limit=1)
        self.assertEqual(client.calls, 0)
        client = ScriptedClient([reply("padding " * 100, [call("price_check", {"item": "latte"})])])
        with self.assertRaises(context.ContextWindowExceeded):
            context.drive(client, context.policy_keep_all, 1, hard_limit=90)
        self.assertEqual(client.calls, 1)

    def test_survival_reports_window_stop_without_inventing_remaining_probes(self):
        result = context.survival(StubClient(), context.policy_keep_all)
        self.assertEqual(result["stop_reason"], "context_limit")
        self.assertLess(result["completed_turns"], 12)
        self.assertLess(result["probes"], 4)

    def test_capped_probe_is_unfinished_without_inventing_a_safety_violation(self):
        responses = [reply(), reply()] + [
            reply(None, [call("price_check", {"item": "latte"}, str(i))])
            for i in range(8)
        ]
        log, _ = context.drive(ScriptedClient(responses), context.policy_truncate, 3)
        self.assertFalse(log[-1]["task_completed"])
        self.assertTrue(log[-1]["ok"])
        result = context.survival(ScriptedClient(responses), context.policy_truncate, 3)
        self.assertEqual(result["stop_reason"], "turn_cap")
        self.assertEqual(result["processed_turns"], 3)
        self.assertEqual(result["completed_turns"], 2)
        self.assertEqual(result["capped_turns"], 1)
        self.assertEqual(result["attempted_probes"], 1)
        self.assertEqual(result["capped_probes"], 1)
        self.assertEqual(result["probes"], 0)
        self.assertIsNone(result["overall_rate"])
        self.assertIsNone(result["before_rate"])
        self.assertIsNone(result["after_rate"])

    def test_notebook_displays_the_unfinished_probe_and_completion_denominators(self):
        path = Path(__file__).resolve().parents[1] / "sessions/s03-context-engineering/toy.py"
        row = {"boundary": None, "before_rate": None, "after_rate": None,
               "probes": 0, "attempted_probes": 1, "capped_probes": 1,
               "stop_reason": "turn_cap", "completed_turns": 2,
               "processed_turns": 3, "requested_turns": 3, "capped_turns": 1}
        cell = notebook_function(path, "s03_demo_survival", {
            "context": SimpleNamespace(survival_table=lambda client: {"truncate": row})})
        output = StringIO()
        with redirect_stdout(output):
            cell(None, mo=SimpleNamespace(redirect_stdout=nullcontext))
        self.assertIn("0/1 answered probes; 1 capped", output.getvalue())
        self.assertIn("2 answered / 3 processed / 3 requested turns", output.getvalue())
        self.assertNotIn("100%", output.getvalue())

    def test_notebook_accepts_a_reversed_empirical_ordering(self):
        path = Path(__file__).resolve().parents[1] / "sessions/s03-context-engineering/toy.py"
        nodes = ast.parse(path.read_text()).body
        check = next(n.name for n in nodes if isinstance(n, ast.FunctionDef)
                     and n.name.startswith("test_s03_")
                     and [a.arg for a in n.args.args if a.arg != "mo"] == ["survival"])
        notebook_function(path, check)(survival={"pinned": {"overall_rate": 0.25, "probes": 4},
                                                 "truncate": {"overall_rate": 0.5, "probes": 4}},
                                      mo=SimpleNamespace(redirect_stdout=nullcontext))
