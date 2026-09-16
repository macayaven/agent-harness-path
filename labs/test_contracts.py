"""Regression tests for the public hard-path schema and wire contracts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

LABS = Path(__file__).resolve().parent
if str(LABS) not in sys.path:
    sys.path.insert(0, str(LABS))

from client import canonicalize
from reference.engine import run_engine
from reference.loop import run_loop
import schemas
import run as runner
from spec_schema import SpecError, validate_spec


VALID_SPEC = {
    "theme": "world capitals",
    "difficulty": "easy",
    "categories": ["geography"],
    "clue_count": 2,
    "off_limits": ["medical advice"],
    "language": "en",
    "house_rules": ["clues from tools only"],
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

    def test_theme_must_be_a_string(self) -> None:
        spec = {**VALID_SPEC, "theme": 7}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_bool_clue_count_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "clue_count": True}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_unknown_category_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "categories": ["history"]}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_unexpected_extra_field_is_rejected(self) -> None:
        spec = {**VALID_SPEC, "surprise": "not in the schema"}
        with self.assertRaises(SpecError):
            validate_spec(spec)

    def test_list_fields_reject_non_string_elements(self) -> None:
        for field in ("categories", "off_limits", "house_rules"):
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
            "theme": "women in science",
            "categories": ["science"],
            "clue_count": 1,
        }
        client = RecordingClient()

        result = run_engine(
            client,
            ["Start the round."],
            spec=VALID_SPEC,
            auto_approve=False,
            input_fn=input_sequence("edit", json.dumps(replacement)),
        )

        self.assertEqual(result["spec"], replacement)
        self.assertEqual(result["state"]["approved_difficulty"], "easy")
        self.assertEqual(result["state"]["allowed_categories"], ["science"])
        self.assertEqual(client.calls, 1)

    def test_unknown_consent_decision_fails_closed(self) -> None:
        client = RecordingClient()

        result = run_engine(
            client,
            ["Start the round."],
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
            json.dumps({**VALID_SPEC, "categories": ["history"]}),
        )
        for edit in invalid_edits:
            with self.subTest(edit=edit):
                client = RecordingClient()
                result = run_engine(
                    client,
                    ["Start the round."],
                    spec=VALID_SPEC,
                    auto_approve=False,
                    input_fn=input_sequence("edit", edit),
                )

                self.assertEqual(result["stop_reason"], "invalid_edit")
                self.assertEqual(client.calls, 0)
                self.assertEqual(result["state"]["tool_log"], [])
                self.assertEqual(result["state"]["drawn"], {})

    def test_off_limits_medical_advice_mention_is_not_refused(self) -> None:
        client = RecordingClient()

        result = run_engine(
            client,
            [
                "Call propose_round_spec for an easy geography round; "
                "off_limits medical advice."
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
        result = {"z": "España", "a": [2, 1]}

        messages, stop = run_loop(
            client,
            [{"role": "user", "content": "run demo"}],
            [],
            lambda _call: result,
        )

        self.assertEqual(stop, "completed")
        self.assertEqual(messages[2]["content"], canonicalize(result))
        self.assertEqual(messages[2]["content"], '{"a":[2,1],"z":"España"}')


if __name__ == "__main__":
    unittest.main()
