"""Teaching controls must exercise the failure they ask learners to explain."""

from io import StringIO
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import marimo as mo

from cafe import consent, domain, repair, report, schema
from cafe.evals import checkers, tasks
from cafe.model import LiveClient, StubClient, _TransportError, check_pairing
from cafe.tools import OrderState
from course_test_support import ScriptedClient, call, reply
from notebook_support import notebook_function

ROOT = Path(__file__).resolve().parents[1]


class FixturePurposeTests(unittest.TestCase):
    def view(self):
        output = StringIO()
        return output, SimpleNamespace(capture_stdout=mo.capture_stdout, plain_text=output.write)

    def test_s02_dirty_fixture_has_neither_proposal_nor_confirmation(self):
        observed = []

        def inspect_attempt(scenario, record):
            observed.extend(checkers.ticket_only_after_confirmation(scenario, record))
            return None

        cell = notebook_function(ROOT / "sessions/s02-golden-evals/toy.py", "s02_demo_compare", {
            "GOLDEN": tasks.GOLDEN, "OrderState": OrderState,
            "reference_record": tasks.reference_record, "attempt_premature_fire": inspect_attempt,
        })
        _, view = self.view()
        cell(view)
        self.assertEqual(len(observed), 2, observed)

    def consent_checkpoint(self, client):
        cell = notebook_function(ROOT / "sessions/s05-consent-gate/toy.py", "s05_demo_checkpoint", {
            "run_shift": consent.run_shift, "make_responder": consent.make_responder,
        })
        output, view = self.view()
        cell(client, view)
        return output.getvalue()

    def test_s04_timeout_stops_the_batch_and_protocol_check_reuses_its_evidence(self):
        path = ROOT / "sessions/s04-structured-generation/toy.py"
        demo = notebook_function(path, "s04_demo_live", {
            "domain": domain, "ask_ticket_run": schema.ask_ticket_run,
        })
        protocol_check = notebook_function(path, "test_s04_retry_loop_stays_protocol_legal", {
            "check_pairing": check_pairing,
        })
        client = LiveClient(base_url="https://model.invalid/v1", api_key="test", model="test")
        _, view = self.view()
        with patch("cafe.model._post_chat_completions", side_effect=[
            json.dumps(reply('{"items": []}')).encode(), _TransportError("timeout"),
        ]) as transport:
            runs = demo(client, view)[0]
            protocol_check(view, runs)
        self.assertEqual(transport.call_count, 2)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["stop_reason"], "transport_error")
        self.assertEqual([o["stage"] for o in runs[0]["outcomes"]], ["shape", "transport"])

    def test_s05_no_proposal_is_unexercised_not_a_successful_rejection(self):
        result = self.consent_checkpoint(StubClient())
        self.assertIn("0 / 0 observed rejections fired nothing", result)
        self.assertIn("unexercised: 3 of 3 runs", result)
        self.assertIn("No rejection evidence", result)

    def test_protected_shift_supplies_case_sensitive_menu_names_before_a_tool_call(self):
        client = ScriptedClient([reply("Which table?")])
        consent.run_shift(client, ["An espresso, please."], consent.make_responder([]))
        prompt = client.requests[0]["messages"][0]["content"]
        self.assertIn("case-sensitive", prompt)
        for item in domain.MENU:
            self.assertIn(item, prompt)

    def test_s05_observed_rejections_with_blocked_fires_count(self):
        responses = []
        for n in range(3):
            ticket = {"table": 1, "items": ["espresso"]}
            responses += [reply(tool_calls=[call("propose_order", ticket, f"p{n}")]),
                          reply(tool_calls=[call("fire_ticket", ticket, f"f{n}")])]
        result = self.consent_checkpoint(ScriptedClient(responses))
        self.assertIn("3 / 3 observed rejections fired nothing", result)
        self.assertIn("unexercised: 0 of 3 runs", result)

    def test_s07_cap_fixture_alternates_contract_and_availability_failures(self):
        cell = notebook_function(ROOT / "sessions/s07-repair-loop/toy.py", "s07_demo_contradiction", {
            "CAP_DEFAULT": repair.CAP_DEFAULT, "make_scripted_generator": repair.make_scripted_generator,
            "repair_ticket": repair.repair_ticket,
        })
        _, view = self.view()
        run = cell(view)[0]
        self.assertEqual(run["stop_reason"], "retries_exhausted")
        self.assertIsNone(run["ticket"])
        self.assertEqual([[f["check"] for f in a["failures"]] for a in run["attempts"]],
                         [["contract"], ["availability"], ["contract"]])

    def test_s07_generator_receives_the_inherited_contract_and_trusted_menu(self):
        client = ScriptedClient([reply('{"table": 1, "items": ["espresso"], '
                                       '"total_eur": 1.3, "allergen_checked": false}')])
        generator = repair.make_model_generator(client)
        ticket = generator([{"role": "user", "content": "One espresso for table 1."}])
        self.assertTrue(repair.score_ticket(ticket, {"table": 1, "items": ["espresso"]})["passed"])
        prompt = client.requests[0]["messages"][0]["content"]
        for field in ("items", "table", "total_eur", "allergen_checked"):
            self.assertIn(field, prompt)
        self.assertIn("1.3", prompt)
        self.assertIn("86", prompt)

    def test_s09_omission_control_exercises_coverage_even_without_live_events(self):
        empty_run = consent.run_shift(StubClient(), ["Hello."], consent.make_responder([]))
        events = report.log_events(empty_run)
        self.assertEqual(events, [])
        honest = report.write_report(empty_run, events)
        cell = notebook_function(ROOT / "sessions/s09-evidence-reports/toy.py", "s09_demo_omission", {
            "reassuring_variant": report.reassuring_variant,
            "validate_citations": report.validate_citations, "validate_coverage": report.validate_coverage,
            "capped_shift_trace": report.capped_shift_trace, "log_events": report.log_events,
            "write_report": report.write_report,
        })
        output, view = self.view()
        result = cell(events, honest, view, empty_run)
        self.assertIn("COVERAGE VIOLATION", output.getvalue())
        omission_events, omission_run, reassuring = result
        self.assertTrue(any(e["type"] == "safety" for e in omission_events))
        self.assertEqual(report.validate_citations(reassuring, omission_run), [])
        self.assertTrue(report.validate_coverage(reassuring, omission_events))
