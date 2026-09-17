"""The one seam between the course and a real model.

A notebook never constructs a client; it calls `get_client()`. That returns a
LiveClient for the learner and a deterministic StubClient in CI, so the same
notebook source is both a real experiment and an offline, zero-cost contract.

Wire format: OpenAI-compatible POST /chat/completions over urllib. No SDK.
The API key is never printed, logged, or included in an error message.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from cafe import domain

__all__ = [
    "ModelError",
    "MissingConfig",
    "OrphanedToolResult",
    "LiveClient",
    "StubClient",
    "get_client",
    "check_pairing",
]

TIMEOUT_DEFAULT = 120.0


class ModelError(RuntimeError):
    """Any failure talking to the endpoint. Never carries the API key."""


class MissingConfig(ModelError):
    """Live mode requested without the configuration to reach an endpoint."""


class OrphanedToolResult(ValueError):
    """A tool message whose tool_call_id no assistant message ever opened.

    One failure class, checked the way a real API checks it - not full protocol
    validation. S01 teaches why this single rule matters.
    """


def _env(*names: str) -> str | None:
    """First non-empty value among `names`. CAFE_* wins over OPENAI_*."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _redact(text: str) -> str:
    """Remove any configured secret from text before it reaches a human."""
    out = text
    for name in ("CAFE_API_KEY", "OPENAI_API_KEY"):
        secret = os.environ.get(name)
        if secret and secret in out:
            out = out.replace(secret, "[redacted]")
    return out


def check_pairing(messages: list[dict]) -> None:
    """Every tool result must answer an assistant tool_call that came before it."""
    opened: set[str] = set()
    for message in messages:
        role = message.get("role")
        if role == "assistant":
            for call in message.get("tool_calls") or []:
                if call.get("id"):
                    opened.add(call["id"])
        elif role == "tool":
            call_id = message.get("tool_call_id")
            if call_id not in opened:
                raise OrphanedToolResult(
                    f"orphaned tool result {call_id!r}: no assistant message opened it"
                )


def _slim(response: dict) -> dict:
    """Keep the protocol fields; drop provider-specific reasoning dumps."""
    try:
        choice = response["choices"][0]
        message = choice["message"]
    except (KeyError, IndexError):
        raise ModelError(
            "endpoint returned no choices[0].message; is the base URL an "
            "OpenAI-compatible /v1 root?"
        ) from None
    slim: dict[str, Any] = {
        "role": message.get("role", "assistant"),
        "content": message.get("content"),
    }
    if message.get("tool_calls"):
        slim["tool_calls"] = message["tool_calls"]
    out: dict[str, Any] = {
        "choices": [
            {"index": 0, "message": slim, "finish_reason": choice.get("finish_reason")}
        ]
    }
    if isinstance(response.get("usage"), dict):
        out["usage"] = response["usage"]
    return out


class _TransportError(RuntimeError):
    """A wire failure from _post_chat_completions, not yet a client error.

    The shared transport classifies the failure; each client renders its own
    message, so neither public error string changes.
    """

    def __init__(self, kind: str, detail: str = "", code: int | None = None) -> None:
        super().__init__(detail)
        self.kind = kind  # "timeout" | "http" | "url"
        self.detail = detail
        self.code = code


def _post_chat_completions(
    *, base_url: str, api_key: str, data: bytes, timeout: float
) -> bytes:
    """POST pre-serialized `data` to {base_url}/chat/completions; return raw bytes.

    The one transport both clients share (`cafe` live calls and `labs` live /
    record runs). Callers own serialization, redaction, and every error string.
    """
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except TimeoutError:
        raise _TransportError("timeout") from None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise _TransportError("http", detail, exc.code) from None
    except urllib.error.URLError as exc:
        raise _TransportError("url", str(exc.reason)) from None


class LiveClient:
    """Talks to a real OpenAI-compatible endpoint."""

    mode = "live"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.base_url = (base_url or _env("CAFE_BASE_URL", "OPENAI_BASE_URL") or "").rstrip("/")
        self._api_key = api_key or _env("CAFE_API_KEY", "OPENAI_API_KEY")
        self.model = model or _env("CAFE_MODEL", "OPENAI_MODEL")
        raw_timeout = timeout if timeout is not None else _env("CAFE_TIMEOUT")
        self.timeout = float(raw_timeout) if raw_timeout else TIMEOUT_DEFAULT
        self.calls = 0
        self.last_latency_ms: float | None = None
        missing = [
            name
            for name, value in (
                ("CAFE_BASE_URL", self.base_url),
                ("CAFE_API_KEY", self._api_key),
                ("CAFE_MODEL", self.model),
            )
            if not value
        ]
        if missing:
            raise MissingConfig(
                "live mode needs "
                + ", ".join(missing)
                + ".\nFor a local model:\n"
                "  export CAFE_BASE_URL=http://127.0.0.1:11434/v1\n"
                "  export CAFE_API_KEY=ollama        # any non-empty string\n"
                "  export CAFE_MODEL=qwen2.5:14b-instruct\n"
                "Or set COURSE_MODE=stub to run offline without a model."
            )

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        check_pairing(messages)
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools is not None:
            body["tools"] = tools
        if tool_choice is not None:
            body["tool_choice"] = tool_choice
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        started = time.monotonic()
        try:
            raw = _post_chat_completions(
                base_url=self.base_url,
                api_key=self._api_key,
                data=data,
                timeout=self.timeout,
            )
        except _TransportError as exc:
            if exc.kind == "timeout":
                raise ModelError(
                    f"/chat/completions timed out after {self.timeout:.0f}s"
                ) from None
            if exc.kind == "http":
                detail = _redact(exc.detail)
                raise ModelError(
                    f"HTTP {exc.code} from /chat/completions: {detail}"
                ) from None
            raise ModelError(
                f"cannot reach {self.base_url}: {_redact(exc.detail)}"
            ) from None
        self.calls += 1
        self.last_latency_ms = (time.monotonic() - started) * 1000.0
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            raise ModelError("endpoint returned a non-JSON body") from None
        return _slim(payload)


class StubClient:
    """Deterministic offline stand-in. CI only - never the learner default.

    It is intentionally mediocre: it answers, it sometimes skips a tool, and it
    never invents a price. That is enough to exercise the harness contracts
    without pretending to be a model.
    """

    mode = "stub"

    def __init__(self, script: list[dict] | None = None) -> None:
        self.script = list(script or [])
        self.calls = 0
        self.last_latency_ms = 0.0

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        check_pairing(messages)
        self.calls += 1
        if self.script:
            return self.script.pop(0)
        last = messages[-1]
        if last.get("role") == "tool":
            return self._text("Marchando. ¿Algo más?")
        text = str(last.get("content") or "").lower()
        if tools:
            for item in domain.MENU:
                if item.split()[0] in text:
                    return self._call("price_check", {"item": item})
        return self._text("Dime qué te pongo.")

    def _text(self, content: str) -> dict:
        return {
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 20, "completion_tokens": 8, "total_tokens": 28},
        }

    def _call(self, name: str, arguments: dict) -> dict:
        return {
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": f"call_{self.calls}",
                                "type": "function",
                                "function": {
                                    "name": name,
                                    "arguments": json.dumps(arguments, ensure_ascii=False),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 24, "completion_tokens": 12, "total_tokens": 36},
        }


def get_client(**kwargs: Any):
    """The seam. COURSE_MODE=stub gives the offline client; anything else is live."""
    if (os.environ.get("COURSE_MODE") or "live").strip().lower() == "stub":
        return StubClient()
    return LiveClient(**kwargs)
