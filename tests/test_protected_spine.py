"""Recording, reporting and taxonomy must not undo the S05 consent gate."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cafe import consent, report, taxonomy, trace
from course_test_support import ScriptedClient, call, reply

TICKET = {"table": 1, "items": ["latte"]}


class ProtectedSpineTests(unittest.TestCase):
    def test_unapproved_fire_stays_blocked_when_recorded_and_replayed(self):
        client = ScriptedClient([reply(None, [call("fire_ticket", TICKET)])])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "shift.jsonl"
            recorded = trace.record_shift(client, ["Start."], path,
                                          responder=consent.make_responder([]))
            replayed = trace.replay_shift(path, ["Start."],
                                          responder=consent.make_responder([]))
        for bundle in (recorded, replayed):
            self.assertEqual(bundle["run"]["state"].fired, [])
            self.assertEqual(bundle["run"]["stop_reason"], "consent_violation")
        self.assertEqual(trace.transcript(recorded["run"]), trace.transcript(replayed["run"]))
        self.assertEqual(client.calls, 1)

    def test_aborted_batch_cancels_remaining_tools_and_reports_no_ticket(self):
        calls = [call("fire_ticket", TICKET, "a"), call("close_check", {"table": 1}, "b")]
        run = consent.run_shift(ScriptedClient([reply(None, calls)]), ["Start."],
                                consent.make_responder([]), max_turns=1)
        self.assertEqual(run["stop_reason"], "consent_violation")
        self.assertEqual(run["state"].tool_log, [])
        results = [m for m in run["messages"] if m["role"] == "tool"]
        self.assertEqual([m["tool_call_id"] for m in results], ["a", "b"])
        self.assertEqual(taxonomy.shift_summary(run)["fired"], [])
        events = report.log_events(run)
        self.assertFalse(any(e["type"] == "milestone" for e in events))
        self.assertTrue(any(e["type"].startswith("safety") for e in events))
        written = report.write_report(run, events)
        self.assertEqual(report.validate_citations(written, run), [])
        self.assertEqual(report.validate_coverage(written, events), [])
        self.assertIn("consent", written["outcome"]["note"].lower())
        failures = taxonomy.detect_failures(run, {"id": "blocked", "user_turns": ["Start."], "expects": []})
        self.assertEqual(len(failures), 1)
        self.assertIn("consent", failures[0]["signal"])
        self.assertNotIn("ticket fired", failures[0]["signal"])

    def test_approved_and_edited_payloads_are_the_only_tickets_reported(self):
        edited = {"table": 1, "items": ["espresso"]}
        for requested, decisions in ((TICKET, [("approve", None)]),
                                     (edited, [("edit", edited), ("approve", None)])):
            with self.subTest(requested=requested):
                client = ScriptedClient([reply(None, [call("propose_order", TICKET, "p"),
                    call("fire_ticket", requested, "f")]), reply()])
                run = consent.run_shift(client, ["Start."], consent.make_responder(decisions))
                self.assertEqual(run["state"].fired[0]["items"], requested["items"])
                self.assertEqual(taxonomy.shift_summary(run)["fired"],
                                 [{"items": requested["items"], "table": 1}])
                self.assertEqual(sum(e["type"] == "milestone" for e in report.log_events(run)), 1)

    def test_rejection_exhaustion_and_malformed_decisions_fail_closed(self):
        responders = [consent.make_responder([]), consent.make_responder([("reject", None)]),
                      lambda _: ("maybe", None), lambda _: "approve", lambda _: None]
        for responder in responders:
            with self.subTest(responder=responder):
                approved, log = consent.consent_gate(TICKET, responder)
                self.assertIsNone(approved)
                self.assertTrue(log)

    def test_trace_requires_explicit_consent_source(self):
        with TemporaryDirectory() as directory, self.assertRaises(TypeError):
            trace.record_shift(ScriptedClient([reply()]), ["Start."], Path(directory) / "shift.jsonl")
