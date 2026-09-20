"""Route labels and illustrative rates must not impersonate execution evidence."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest
import statistics
import marimo
from unittest.mock import patch

from cafe import domain, routing, trace
from cafe.model import _slim
from course_test_support import ScriptedClient, reply
from notebook_support import notebook_function

TABLE = {"read_note": "local-small", "draft_reply": "local-large", "till_summary": "cloud-frontier"}
MESSAGES = [{"role": "user", "content": "One synthetic order."}]


class RoutingEvidenceTests(unittest.TestCase):
    def test_notebook_checkpoint_uses_the_given_nonzero_spend(self):
        path = Path(__file__).resolve().parents[1] / "sessions/s11-budgets-routing/toy.py"
        predicate = lambda projected_usd, spent_usd, budget_usd: budget_usd is not None and spent_usd + projected_usd > budget_usd
        cell = notebook_function(path, "s11_demo_budget_gate", {"routing": routing,
            "attempt_budget_gate": predicate, "solution_budget_gate": predicate})
        output = StringIO()
        with redirect_stdout(output):
            cell(mo=SimpleNamespace(capture_stdout=marimo.capture_stdout, plain_text=print))
        self.assertNotIn("MISMATCH", output.getvalue())
        self.assertIn("module=True", output.getvalue())

    def test_every_route_uses_the_injected_client_and_labels_it(self):
        client = ScriptedClient([reply(usage={"total_tokens": 10}) for _ in range(3)])
        client.model = "fixture-client"
        client.last_latency_ms = 12.0
        run = routing.run_phases(client, TABLE, [(p, MESSAGES) for p in TABLE])
        self.assertEqual(client.calls, 3)
        for record in run["records"]:
            self.assertTrue(record["simulation"])
            self.assertEqual(record["client_model"], "fixture-client")
            self.assertEqual(record["route_model"], routing.ROUTES[record["route"]]["model"])
            self.assertTrue(record["usage_known"])
            self.assertIn("estimated_cost_usd", record)
            self.assertNotIn("cost_usd", record)

    def test_unknown_usage_is_not_free_and_blocks_the_next_budgeted_call(self):
        for usage in (None, {}, {"total_tokens": -1}, {"total_tokens": True},
                      {"total_tokens": "10"}, {"total_tokens": 1.5},
                      {"total_tokens": 10, "prompt_tokens": False},
                      {"total_tokens": 0, "prompt_tokens": 5000, "completion_tokens": 5000},
                      {"total_tokens": 11, "prompt_tokens": 4, "completion_tokens": 6},
                      {"total_tokens": 9, "prompt_tokens": 4, "completion_tokens": 6},
                      {"total_tokens": 10, "prompt_tokens": 11},
                      {"total_tokens": 10, "completion_tokens": 11}):
            with self.subTest(usage=usage):
                client = ScriptedClient([reply(usage=usage)])
                budget = routing.Budget(1.0)
                first = routing.metered_call(client, TABLE, "draft_reply", MESSAGES, budget=budget)
                self.assertFalse(first["usage_known"])
                self.assertIsNone(first["tokens"])
                self.assertIsNone(first["estimated_cost_usd"])
                self.assertFalse(budget.usage_complete)
                second = routing.metered_call(client, TABLE, "draft_reply", MESSAGES, budget=budget)
                self.assertFalse(second["dispatched"])
                self.assertEqual(second["refusal"], "usage_unknown")
                self.assertEqual(client.calls, 1)
                tracer = routing.publish({"records": budget.calls, "stop_reason": "usage_unknown"})
                self.assertIn("unknown", tracer.render())
                self.assertIsNone(trace.usage_of(tracer)["total_tokens"])
                self.assertFalse(trace.usage_of(tracer)["usage_complete"])

    def test_raw_trace_usage_cannot_accept_contradictory_components(self):
        tracer = trace.Tracer()
        with tracer.generation("synthetic order", usage={
                "total_tokens": 0, "prompt_tokens": 5000, "completion_tokens": 5000}):
            pass
        self.assertIn("usage unknown", tracer.render())
        summary = trace.usage_of(tracer)
        self.assertIsNone(summary["total_tokens"])
        self.assertFalse(summary["usage_complete"])
        self.assertEqual(summary["known_total_tokens"], 0)

    def test_consistent_usage_including_real_zero_remains_known(self):
        cases = [({"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}, 0),
                 ({"total_tokens": 10}, 10),
                 ({"total_tokens": 10, "prompt_tokens": 4, "completion_tokens": 6}, 10),
                 ({"total_tokens": 10, "prompt_tokens": 4}, 10),
                 ({"total_tokens": 10, "completion_tokens": 6}, 10)]
        for usage, expected in cases:
            with self.subTest(usage=usage):
                run = routing.run_phases(ScriptedClient([reply(usage=usage)]), TABLE,
                                         [("draft_reply", MESSAGES)], budget_usd=0.01)
                self.assertEqual(run["stop_reason"], "ok")
                self.assertTrue(run["budget"].usage_complete)
                self.assertEqual(run["records"][0]["tokens"], expected)
                tracer = trace.Tracer()
                with tracer.generation("synthetic order", usage=usage):
                    pass
                self.assertEqual(trace.usage_of(tracer)["total_tokens"], expected)
                self.assertNotIn("unknown", tracer.render())

    def test_no_budget_allows_unknown_usage_with_partial_accounting(self):
        client = ScriptedClient([reply(), reply(usage={"total_tokens": 20})])
        run = routing.run_phases(client, TABLE, [("draft_reply", MESSAGES)] * 2)
        self.assertEqual(client.calls, 2)
        self.assertFalse(run["budget"].usage_complete)
        self.assertEqual(run["budget"].spent_usd, 0.0012)

    def test_post_call_overrun_stops_further_phases(self):
        client = ScriptedClient([reply(usage={"total_tokens": 1000})])
        run = routing.run_phases(client, TABLE, [("draft_reply", MESSAGES)] * 2, budget_usd=0.01)
        self.assertEqual(client.calls, 1)
        self.assertEqual(run["stop_reason"], "budget_overrun")
        self.assertTrue(run["records"][0]["estimate_overrun"])
        self.assertGreater(run["budget"].spent_usd, 0.01)

    def test_notebook_reports_and_publishes_the_last_calls_accounting_stop(self):
        path = Path(__file__).resolve().parents[1] / "sessions/s11-budgets-routing/toy.py"
        cell = notebook_function(path, "s11_demo_checkpoint", {"routing": routing,
                                  "domain": domain, "statistics": statistics})
        for final_usage, expected in (({"total_tokens": 10000}, "budget_overrun"),
                                      (None, "usage_unknown")):
            with self.subTest(expected=expected):
                client = ScriptedClient([reply(usage={"total_tokens": 10}),
                                         reply(usage={"total_tokens": 10}),
                                         reply(usage=final_usage)])
                tracer = trace.Tracer()
                output = StringIO()
                with patch.object(trace, "Tracer", return_value=tracer), redirect_stdout(output):
                    cell(client, mo=SimpleNamespace(capture_stdout=marimo.capture_stdout, plain_text=print))
                self.assertEqual(client.calls, 3)
                self.assertIn("stop reason      : " + expected, output.getvalue())
                self.assertEqual(tracer.roots[0]["attrs"]["stop_reason"], expected)

    def test_zero_usage_is_known_and_reported_model_is_preserved(self):
        response = {**reply(usage={"total_tokens": 0}), "model": "fixture-reported"}
        slim = _slim(response)
        self.assertEqual(slim["model"], "fixture-reported")
        record = routing.metered_call(ScriptedClient([slim]), TABLE, "draft_reply", MESSAGES)
        self.assertTrue(record["usage_known"])
        self.assertEqual(record["estimated_cost_usd"], 0)
        self.assertEqual(record["reported_model"], "fixture-reported")

    def test_direct_meter_cannot_bypass_the_policy_validation(self):
        client = ScriptedClient([])
        with self.assertRaises(routing.RouteRefused):
            routing.metered_call(client, {**TABLE, "draft_reply": "cloud-frontier"}, "draft_reply", MESSAGES)
        self.assertEqual(client.calls, 0)

    def test_notebook_displays_unknown_usage_and_missing_latency(self):
        path = Path(__file__).resolve().parents[1] / "sessions/s11-budgets-routing/toy.py"
        cell = notebook_function(path, "s11_demo_checkpoint", {"routing": routing,
                                  "domain": domain, "statistics": statistics})
        client = ScriptedClient([reply()])
        output = StringIO()
        with redirect_stdout(output):
            cell(client, mo=SimpleNamespace(capture_stdout=marimo.capture_stdout, plain_text=print))
        self.assertEqual(client.calls, 1)
        self.assertIn("accounting complete: False", output.getvalue())
        self.assertIn("usage_unknown", output.getvalue())
