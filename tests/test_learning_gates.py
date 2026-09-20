"""Labels must be independent; resetting an attempt closes every result gate."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from cafe import taxonomy
from notebook_support import notebook_function

ROOT = Path(__file__).resolve().parents[1]


class Paused(Exception):
    pass


class FakeMo:
    @staticmethod
    def stop(condition, output=None):
        if condition:
            raise Paused()

    @staticmethod
    def md(text):
        return text


class LearningGateTests(unittest.TestCase):
    def test_incomplete_or_invalid_labels_do_not_unlock_results(self):
        for labels in ({}, {"a": "pass", "b": None}, {"a": "pass", "b": "maybe"},
                       {"a": "pass", "b": " "}, {"a": "pass", "b": " pass "},
                       {"a": "pass", "b": "fail", "extra": "pass"}, []):
            with self.subTest(labels=labels):
                self.assertFalse(taxonomy.labels_ready(labels, {"a", "b"}, {"pass", "fail"}))
        self.assertFalse(taxonomy.labels_ready({}, set()))

    def test_complete_labels_allow_comparison(self):
        self.assertTrue(taxonomy.labels_ready({"a": "pass", "b": "fail"}, {"a", "b"}, {"pass", "fail"}))
        self.assertTrue(taxonomy.labels_ready({"a": "my category"}, {"a"}))

    def test_s10_taxonomy_never_substitutes_a_reference(self):
        path = ROOT / "sessions/s10-error-analysis/toy.py"
        cell = notebook_function(path, "s10_demo_labels")
        with self.assertRaises(Paused):
            cell(mine={}, mo=FakeMo, open_code_ready=False)
        labels = {"a": "my own category"}
        self.assertEqual(cell(mine=labels, mo=FakeMo, open_code_ready=True), (labels,))
        with self.assertRaises(Paused):
            cell(mine={}, mo=FakeMo, open_code_ready=False)

    def test_s12_judge_calls_require_ready_labels_and_close_on_reset(self):
        path = ROOT / "sessions/s12-judge-calibration/toy.py"
        judge = SimpleNamespace(run_judge_all=Mock(return_value={"a": {"verdict": "unparseable"}}),
                                RUBRIC_V1="v1", RUBRIC_V2="v2")
        for name in ("s12_demo_judge_v1", "s12_demo_judge_v2"):
            cell = notebook_function(path, name, {"judge": judge})
            args = {"client": object(), "transcripts": {"a": []}, "mo": FakeMo, "hand_labels_ready": False}
            before = judge.run_judge_all.call_count
            with self.assertRaises(Paused):
                cell(**args)
            self.assertEqual(judge.run_judge_all.call_count, before)
            cell(**{**args, "hand_labels_ready": True})
            self.assertEqual(judge.run_judge_all.call_count, before + 1)
            with self.assertRaises(Paused):
                cell(**args)
            self.assertEqual(judge.run_judge_all.call_count, before + 1)

    def test_reference_key_needs_both_complete_labels_and_reveal(self):
        path = ROOT / "sessions/s12-judge-calibration/toy.py"
        judge = SimpleNamespace(seeded_corpus=Mock(return_value=({"a": []}, {"a": None})))
        cell = notebook_function(path, "s12_demo_reference_key", {"judge": judge})
        for ready, reveal in ((False, False), (False, True), (True, False), (True, True), (False, True)):
            before = judge.seeded_corpus.call_count
            args = {"mo": FakeMo, "hand_labels_ready": ready, "reveal_hand_labels": SimpleNamespace(value=reveal)}
            if ready and reveal:
                self.assertEqual(cell(**args), ({"a": None},))
            else:
                with self.assertRaises(Paused):
                    cell(**args)
            self.assertEqual(judge.seeded_corpus.call_count, before + int(ready and reveal))
