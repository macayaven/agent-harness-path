"""Contracts for the live-model seam, the domain module and the tools."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cafe import domain, tools  # noqa: E402
from cafe.model import (  # noqa: E402
    LiveClient,
    MissingConfig,
    OrphanedToolResult,
    StubClient,
    check_pairing,
    get_client,
)

CAFE_ENV = ("CAFE_BASE_URL", "CAFE_API_KEY", "CAFE_MODEL", "OPENAI_BASE_URL",
            "OPENAI_API_KEY", "OPENAI_MODEL", "COURSE_MODE")


class Seam(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in CAFE_ENV}
        for k in CAFE_ENV:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_stub_mode_returns_the_offline_client(self):
        os.environ["COURSE_MODE"] = "stub"
        self.assertIsInstance(get_client(), StubClient)

    def test_stub_is_the_default_mode(self):
        self.assertIsInstance(get_client(), StubClient)

    def test_live_needs_an_explicit_opt_in(self):
        os.environ.update(
            COURSE_MODE="live",
            CAFE_BASE_URL="http://127.0.0.1:11434/v1",
            CAFE_API_KEY="local",
            CAFE_MODEL="test-model",
        )
        self.assertIsInstance(get_client(), LiveClient)

    def test_unconfigured_live_names_every_missing_variable(self):
        os.environ["COURSE_MODE"] = "live"
        with self.assertRaises(MissingConfig) as caught:
            get_client()
        message = str(caught.exception)
        for name in ("CAFE_BASE_URL", "CAFE_API_KEY", "CAFE_MODEL"):
            self.assertIn(name, message)
        self.assertIn("COURSE_MODE", message)

    def test_cafe_variables_win_over_openai_variables(self):
        os.environ.update(
            COURSE_MODE="live",
            OPENAI_BASE_URL="http://production.invalid/v1",
            OPENAI_API_KEY="prod",
            OPENAI_MODEL="prod-model",
            CAFE_BASE_URL="http://127.0.0.1:11434/v1",
            CAFE_API_KEY="local",
            CAFE_MODEL="local-model",
        )
        client = get_client()
        self.assertEqual(client.base_url, "http://127.0.0.1:11434/v1")
        self.assertEqual(client.model, "local-model")


class Safety(unittest.TestCase):
    def test_api_key_is_never_an_attribute_or_repr(self):
        os.environ.update(
            COURSE_MODE="live",
            CAFE_BASE_URL="http://127.0.0.1:11434/v1",
            CAFE_API_KEY="super-secret-value",
            CAFE_MODEL="m",
        )
        try:
            client = get_client()
            self.assertNotIn("super-secret-value", repr(client))
            self.assertNotIn("super-secret-value", str(vars(client).get("base_url", "")))
            self.assertFalse(hasattr(client, "api_key"), "key must not be public")
        finally:
            for k in ("COURSE_MODE", "CAFE_BASE_URL", "CAFE_API_KEY", "CAFE_MODEL"):
                os.environ.pop(k, None)

    def test_error_text_redacts_the_key_even_if_the_server_echoes_it(self):
        """Verified against a live endpoint that echoes the key in a 500 body."""
        from cafe.model import _redact
        os.environ["CAFE_API_KEY"] = "sk-LEAKME123"
        try:
            leaked = '{"error":"key sk-LEAKME123 was rejected"}'
            cleaned = _redact(leaked)
            self.assertNotIn("sk-LEAKME123", cleaned)
            self.assertIn("[redacted]", cleaned)
        finally:
            os.environ.pop("CAFE_API_KEY", None)

    def test_no_credential_literals_in_the_package(self):
        for path in sorted((ROOT / "cafe").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertNotIn("sk-", text)
                self.assertNotIn("/Users/", text)
                self.assertNotIn("/home/", text)

    def test_package_imports_stdlib_only(self):
        allowed = set(sys.stdlib_module_names) | {"cafe"}
        for path in sorted((ROOT / "cafe").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertIn(alias.name.split(".")[0], allowed, path.name)
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    self.assertIn(node.module.split(".")[0], allowed, path.name)

    def test_stub_mode_opens_no_socket(self):
        script = (
            "from cafe.model import get_client\n"
            "c = get_client()\n"
            "c.chat([{'role':'user','content':'a latte'}])\n"
            "print('ok', c.mode)\n"
        )
        env = dict(
            os.environ,
            COURSE_MODE="stub",
            PYTHONPATH=f"{ROOT / 'tests' / 'no_network_site'}{os.pathsep}{ROOT}",
        )
        done = subprocess.run(
            [sys.executable, "-c", script], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(done.returncode, 0, done.stderr[-1500:])
        self.assertIn("ok stub", done.stdout)


class Pairing(unittest.TestCase):
    def test_orphaned_tool_result_is_rejected(self):
        with self.assertRaises(OrphanedToolResult):
            check_pairing([{"role": "tool", "tool_call_id": "nope", "content": "{}"}])

    def test_paired_tool_result_is_accepted(self):
        check_pairing([
            {"role": "assistant", "tool_calls": [
                {"id": "c1", "type": "function",
                 "function": {"name": "price_check", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "c1", "content": "{}"},
        ])

    def test_stub_enforces_pairing_like_a_real_endpoint(self):
        with self.assertRaises(OrphanedToolResult):
            StubClient().chat([{"role": "tool", "tool_call_id": "x", "content": "{}"}])


class Domain(unittest.TestCase):
    def test_tool_names_are_in_domain_and_match_the_plan(self):
        self.assertEqual(
            set(domain.TOOL_NAMES),
            {"price_check", "check_allergens", "propose_order", "fire_ticket", "close_check"},
        )

    def test_every_schema_has_a_handler_and_every_handler_a_schema(self):
        self.assertEqual(set(domain.TOOL_NAMES), set(tools.TOOLS))

    def test_menu_entries_are_complete(self):
        for item, entry in domain.MENU.items():
            with self.subTest(item=item):
                self.assertIsInstance(entry["price"], float)
                self.assertIsInstance(entry["allergens"], list)
                self.assertIn(entry["station"], {"bar", "kitchen", "pastry"})

    def test_eighty_sixed_items_exist_on_the_menu(self):
        for item in domain.EIGHTY_SIXED:
            self.assertIn(item, domain.MENU)


class Tools(unittest.TestCase):
    def test_price_check_reports_availability_for_an_eighty_sixed_item(self):
        result = tools.price_check(tools.OrderState(), "cheese omelette")
        self.assertTrue(result["on_menu"])
        self.assertFalse(result["available"])

    def test_allergen_check_is_data_driven_not_guessed(self):
        state = tools.OrderState()
        self.assertFalse(tools.check_allergens(state, "croissant", "milk")["safe"])
        self.assertTrue(tools.check_allergens(state, "espresso", "milk")["safe"])

    def test_propose_does_not_fire_and_fire_records_a_side_effect(self):
        state = tools.OrderState()
        tools.propose_order(state, ["latte"], 4)
        self.assertEqual(state.fired, [], "proposing must not fire a ticket")
        tools.fire_ticket(state, ["latte"], 4)
        self.assertEqual(len(state.fired), 1)

    def test_dispatch_turns_a_bad_call_into_a_tool_result(self):
        state = tools.OrderState()
        bad = {"function": {"name": "price_check", "arguments": "{not json"}}
        self.assertIn("error", tools.dispatch(state, bad))
        unknown = {"function": {"name": "sauté", "arguments": "{}"}}
        self.assertIn("error", tools.dispatch(state, unknown))

    def test_dispatch_executes_a_real_call(self):
        state = tools.OrderState()
        call = {"function": {"name": "price_check",
                             "arguments": json.dumps({"item": "latte"})}}
        self.assertEqual(tools.dispatch(state, call)["price_eur"], 1.60)
        self.assertEqual(state.tool_log, ["price_check"])


if __name__ == "__main__":
    unittest.main()
