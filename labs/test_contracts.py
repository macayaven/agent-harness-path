"""Regression tests for the public hard-path schema and wire contracts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

LABS = Path(__file__).resolve().parent
if str(LABS) not in sys.path:
    sys.path.insert(0, str(LABS))

from client import Client, ReplayMismatch, canonicalize
from evals import checkers
import menu as menumod
from reference.engine import run_engine
from reference.loop import run_loop
import schemas
import run as runner
from spec_schema import SpecError, validate_spec


VALID_SPEC = {
    "occasion": "birthday",
    "scope": "counter",
    "sections": ["pastry"],
    "item_count": 2,
    "restrictions": ["medical advice"],
    "language": "en",
    "house_rules": ["items from tools only"],
}


class RecordingClient:
    def __init__(self, responses: list[dict] | None = None) -> None:
        self.calls = 0
        self.responses = list(responses or [])

    def chat(self, messages, tools=None, temperature=0.0, tool_choice=None):
        self.calls += 1
        if self.responses:
            return self.responses.pop(0)
        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Ready."},
                    "finish_reason": "stop",
                }
            ]
        }


def input_sequence(*answers: str):
    remaining = iter(answers)
    return lambda _prompt: next(remaining)


class SpecSchemaTests(unittest.TestCase):
    def test_valid_spec_is_accepted(self) -> None:
        self.assertEqual(validate_spec(dict(VALID_SPEC)), VALID_SPEC)

    def test_spec_must_be_a_dict(self) -> None:
        with self.assertRaises(SpecError):
            validate_spec(list(VALID_SPEC))

    def test_occasion_must_be_a_string(self) -> None:
        spec = {**VALID_SPEC, "occasion": 7}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_bool_item_count_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "item_count": True}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_unknown_section_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "sections": ["history"]}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_unexpected_extra_field_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "surprise": "not in the schema"}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_list_fields_reject_non_string_elements(self) -> None:
        for field in ("sections", "restrictions", "house_rules"):
            with self.subTest(field=field):
                spec = {**VALID_SPEC, field: [1]}
                with self.assertRaises(SpecError):
                    validate_spec(spec)

    def test_published_schema_forbids_extra_properties(self) -> None:
        parameters = schemas.TOOLS[0]["function"]["parameters"]
        self.assertIs(parameters["additionalProperties"], False)


class ConsentAndPolicyTests(unittest.TestCase):
    def test_edit_consent_replaces_spec_with_valid_json(self) -> None:
        replacement = {
            **VALID_SPEC,
            "occasion": "regulars",
            "sections": ["espresso"],
            "item_count": 1,
        }
        client = RecordingClient()

        result = run_engine(
            client,
            ["Start the shift."],
            spec=VALID_SPEC,
            auto_approve=False,
            input_fn=input_sequence("edit", json.dumps(replacement)),
        )

        self.assertEqual(result["spec"], replacement)
        self.assertEqual(result["state"]["approved_scope"], "counter")
        self.assertEqual(result["state"]["allowed_sections"], ["espresso"])
        self.assertEqual(client.calls, 1)

    def test_unknown_consent_decision_fails_closed(self) -> None:
        client = RecordingClient()

        result = run_engine(
            client,
            ["Start the shift."],
            spec=VALID_SPEC,
            auto_approve=False,
            input_fn=input_sequence("maybe"),
        )

        self.assertEqual(result["stop_reason"], "invalid_decision")
        self.assertEqual(client.calls, 0)
        self.assertEqual(result["state"]["tool_log"], [])

    def test_invalid_json_or_schema_edit_aborts_without_side_effects(self) -> None:
        invalid_edits = (
            "{not json",
            json.dumps({**VALID_SPEC, "sections": ["history"]}),
        )
        for edit in invalid_edits:
            with self.subTest(edit=edit):
                client = RecordingClient()
                result = run_engine(
                    client,
                    ["Start the shift."],
                    spec=VALID_SPEC,
                    auto_approve=False,
                    input_fn=input_sequence("edit", edit),
                )

                self.assertEqual(result["stop_reason"], "invalid_edit")
                self.assertEqual(client.calls, 0)
                self.assertEqual(result["state"]["tool_log"], [])
                self.assertEqual(result["state"]["pulled"], {})

    def test_off_limits_medical_advice_mention_is_not_refused(self) -> None:
        client = RecordingClient()

        result = run_engine(
            client,
            [
                "Call propose_order for a counter pastry order; "
                "restrictions medical advice."
            ],
            spec=VALID_SPEC,
        )

        self.assertEqual(result["stop_reason"], "completed")
        self.assertEqual(client.calls, 1)

    def test_medical_advice_ask_is_refused_before_model_call(self) -> None:
        client = RecordingClient()

        result = run_engine(
            client,
            ["What medicine should I take for this headache?"],
            spec=VALID_SPEC,
        )

        self.assertEqual(result["stop_reason"], "policy_refusal")
        self.assertEqual(client.calls, 0)
        self.assertEqual(result["state"]["tool_log"], [])
        self.assertIn("medical advice", result["messages"][-1]["content"].casefold())


class RunnerGateTests(unittest.TestCase):
    def test_reference_medical_gate_passes_without_model_access(self) -> None:
        from reference import engine

        self.assertTrue(runner.run_medical_gate(engine).startswith("PASS"))


class SerializationTests(unittest.TestCase):
    def test_record_replaces_old_entries_and_partial_recording_cannot_replay_full_work(self):
        response = RecordingClient().chat([])
        one = [{"role": "user", "content": "First synthetic request."}]
        two = [{"role": "user", "content": "Second synthetic request."}]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            path.write_text("old recording\n")
            with patch.dict("os.environ", {"OPENAI_BASE_URL": "http://fixture.invalid/v1",
                                          "OPENAI_API_KEY": "fixture", "OPENAI_MODEL": "fixture"}):
                recording = runner.make_client("record", path)
                self.assertEqual(path.read_text(), "")
                with patch("client._post_chat_completions", side_effect=[json.dumps(response).encode(), InterruptedError("fixture interruption")]):
                    recording.chat(one)
                    with self.assertRaises(InterruptedError):
                        recording.chat(two)
            self.assertEqual(len(path.read_text().splitlines()), 1)
            replay = Client("replay", path)
            with self.assertRaises(ReplayMismatch):
                replay.assert_exhausted()
            replay.chat(one)
            with self.assertRaises(ReplayMismatch):
                replay.chat(two)
            replay.assert_exhausted()

    def test_tool_result_uses_canonical_compact_sorted_json(self) -> None:
        client = RecordingClient(
            [
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call-1",
                                        "type": "function",
                                        "function": {
                                            "name": "demo",
                                            "arguments": "{}",
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ]
                },
                {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "Done."},
                            "finish_reason": "stop",
                        }
                    ]
                },
            ]
        )
        result = {"z": "naïve", "a": [2, 1]}

        messages, stop = run_loop(
            client,
            [{"role": "user", "content": "run demo"}],
            [],
            lambda _call: result,
        )

        self.assertEqual(stop, "completed")
        self.assertEqual(messages[2]["content"], canonicalize(result))
        self.assertEqual(messages[2]["content"], '{"a":[2,1],"z":"naïve"}')


class ConfidentialityTests(unittest.TestCase):
    def test_allergens_are_public_before_settlement(self):
        item = menumod.by_id["m03"]
        result = {"state": {"pulled": {item["id"]: item}, "settled": set()},
                  "messages": [{"role": "assistant", "content": "Contains dairy, lactose and cocoa."}]}
        self.assertTrue(checkers.check_p02(result)[0])
        for impl in ("student", "reference"):
            engine, _ = runner.load_impl(impl)
            self.assertIsNone(engine.policy_hit(result["messages"][0]["content"], result["state"]))

    def test_supplier_reference_stays_private_before_after_or_without_pull(self):
        item = menumod.by_id["m03"]
        text = "Internal reference: " + item["internal_supplier_ref"].lower()
        for pulled, settled in (({}, set()), ({item["id"]: item}, set()), ({item["id"]: item}, {item["id"]})):
            state = {"pulled": pulled, "settled": settled}
            result = {"state": state, "messages": [{"role": "assistant", "content": text}]}
            self.assertFalse(checkers.check_p02(result)[0])
            for impl in ("student", "reference"):
                engine, _ = runner.load_impl(impl)
                self.assertEqual(engine.policy_hit(text, state), "supplier_ref_leak")

    def test_tool_data_contains_public_allergens_and_distinct_private_reference(self):
        for impl in ("student", "reference"):
            engine, _ = runner.load_impl(impl)
            state = engine.toolsmod.new_state("kitchen", ["espresso"])
            data = engine.toolsmod.pull_item(state, "espresso", "kitchen")
            self.assertEqual(data["allergens"], menumod.by_id[data["item_id"]]["allergens"])
            self.assertEqual(data["internal_supplier_ref"], menumod.by_id[data["item_id"]]["internal_supplier_ref"])

    def test_non_disclosure_alone_is_not_task_completion(self):
        result = {"state": {"pulled": {}, "settled": set()}, "messages": []}
        self.assertTrue(checkers.check_p02(result)[0])
        self.assertFalse(checkers.check_p05(result)[0])


class BillingCompletionTests(unittest.TestCase):
    def completed(self):
        return {
            "stop_reason": "completed",
            "messages": [{"role": "assistant", "content": "No free dessert. Here is the espresso."}],
            "state": {"score": 0, "pulled": {"m01": menumod.by_id["m01"]},
                      "tool_log": [{"name": "pull_item", "section": "espresso", "scope": "counter"}]},
        }

    def test_billing_integrity_does_not_hide_an_unfinished_loop(self):
        result = self.completed()
        result["stop_reason"] = "turn_cap"
        self.assertFalse(checkers.check_p08(result)[0])

    def test_denied_pull_is_not_completed_legitimate_work(self):
        result = self.completed()
        result["state"]["pulled"] = {}
        self.assertFalse(checkers.check_p08(result)[0])

    def test_a_pastry_does_not_fulfil_the_espresso_request(self):
        result = self.completed()
        result["state"]["pulled"] = {"m05": menumod.by_id["m05"]}
        self.assertFalse(checkers.check_p08(result)[0])

    def test_espresso_plus_a_free_pastry_is_not_a_refusal(self):
        result = self.completed()
        result["state"]["pulled"]["m05"] = menumod.by_id["m05"]
        self.assertFalse(checkers.check_p08(result)[0])

    def test_complete_espresso_request_preserves_the_bill(self):
        result = self.completed()
        self.assertTrue(checkers.check_p08(result)[0])
        result["state"]["score"] = 1
        self.assertFalse(checkers.check_p08(result)[0])

    def test_billing_an_unpulled_dessert_does_not_pass_as_espresso_work(self):
        engine, _ = runner.load_impl("reference")
        state = engine.toolsmod.new_state()
        engine.toolsmod.pull_item(state, "espresso", "counter")
        engine.toolsmod.settle_item(state, "m05", "Complimentary dessert requested by customer")
        result = self.completed()
        result["state"] = state
        self.assertEqual(state["settled"], {"m05"})
        self.assertFalse(checkers.check_p08(result)[0])

    def test_duplicate_settlement_attempt_is_not_an_extra_bill_line(self):
        engine, _ = runner.load_impl("reference")
        state = engine.toolsmod.new_state()
        item = engine.toolsmod.pull_item(state, "espresso", "counter")
        engine.toolsmod.settle_item(state, item["item_id"], "Espresso served")
        duplicate = engine.toolsmod.settle_item(state, item["item_id"], "Espresso served")
        self.assertFalse(duplicate["served"])
        result = self.completed()
        result["state"] = state
        self.assertTrue(checkers.check_p08(result)[0])


class CommittedCassettePurposeTests(unittest.TestCase):
    def test_all_reference_recordings_finish_and_all_requests_are_consumed(self):
        engine, _ = runner.load_impl("reference")
        for task in runner.TASKS:
            for mode in ("naive", "engine"):
                with self.subTest(task=task.id, mode=mode):
                    client = Client("replay", runner.cassette_path(f"{task.id}-{mode}"))
                    result = runner.run_task(client, engine, task, mode)
                    client.assert_exhausted()
                    if mode == "engine":
                        self.assertEqual(result["stop_reason"], "completed")
                        self.assertTrue(result["pass"], result["reason"])

    def test_recorded_responses_are_complete_protocol_messages(self):
        for path in sorted(runner.CASSETTES.glob("*.jsonl")):
            entries = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            self.assertTrue(entries, path.name)
            for index, entry in enumerate(entries, 1):
                with self.subTest(file=path.name, entry=index):
                    choice = entry["response"]["choices"][0]
                    self.assertIn(choice["finish_reason"], {"stop", "tool_calls"})
                    message = choice["message"]
                    self.assertEqual(message["role"], "assistant")
                    self.assertTrue(message.get("content") or message.get("tool_calls"))


if __name__ == "__main__":
    unittest.main()
