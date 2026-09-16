"""OpenAI-compatible chat client with cassette replay/record.

Match contract (S08, not weaker): the next unused cassette entry must equal the
canonical request, in order. Exhaustion is a separate invariant.
The match key is {messages, tools, temperature, tool_choice} — not `model`.
Never print or log the API key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class ReplayMismatch(AssertionError):
    """Next cassette entry does not match the request, or entries remain unused."""


class OrphanedToolResult(ValueError):
    """A tool message whose tool_call_id was never opened by an assistant call."""


class RouteRefused(RuntimeError):
    """Session-content phase pointed at a disallowed route."""


def canonicalize(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def match_key(
    messages: list[dict],
    tools: list[dict] | None,
    temperature: float,
    tool_choice: Any,
) -> dict:
    key: dict[str, Any] = {
        "messages": messages,
        "temperature": temperature,
    }
    if tools is not None:
        key["tools"] = tools
    if tool_choice is not None:
        key["tool_choice"] = tool_choice
    return key


def check_orphans(messages: list[dict]) -> None:
    """One failure class, same as the S01 toy mock — not full protocol validation."""
    seen: set[str] = set()
    for msg in messages:
        role = msg.get("role")
        if role == "assistant":
            for call in msg.get("tool_calls") or []:
                call_id = call.get("id")
                if call_id:
                    seen.add(call_id)
        elif role == "tool":
            tid = msg.get("tool_call_id")
            if tid not in seen:
                raise OrphanedToolResult(f"orphaned tool result {tid}")


def _redact(text: str) -> str:
    key = os.environ.get("OPENAI_API_KEY") or ""
    if key and key in text:
        return text.replace(key, "[redacted]")
    return text


def _slim_response(response: dict) -> dict:
    """Keep protocol fields from a real endpoint; drop reasoning dumps."""
    try:
        choice = response["choices"][0]
        msg = choice["message"]
    except (KeyError, IndexError):
        return response
    slim_msg: dict[str, Any] = {
        "role": msg.get("role", "assistant"),
        "content": msg.get("content"),
    }
    if msg.get("tool_calls"):
        slim_msg["tool_calls"] = msg["tool_calls"]
    return {
        "choices": [
            {
                "index": 0,
                "message": slim_msg,
                "finish_reason": choice.get("finish_reason"),
            }
        ]
    }


class Client:
    def __init__(
        self,
        mode: str,
        cassette_path: Path | None = None,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 300.0,
    ) -> None:
        if mode not in {"replay", "live", "record"}:
            raise ValueError(f"unknown mode {mode!r}; expected replay, live, or record")
        self.mode = mode
        self.cassette_path = Path(cassette_path) if cassette_path else None
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "").rstrip("/")
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL")
        self.timeout = timeout
        self._entries: list[dict] = []
        self._next = 0
        if mode == "replay":
            if not self.cassette_path or not self.cassette_path.is_file():
                raise ReplayMismatch(
                    f"replay requires a cassette file; got {self.cassette_path}"
                )
            lines = self.cassette_path.read_text(encoding="utf-8").splitlines()
            self._entries = [json.loads(line) for line in lines if line.strip()]
        elif mode == "record":
            if not self.cassette_path:
                raise ValueError("record requires cassette_path")
            self.cassette_path.parent.mkdir(parents=True, exist_ok=True)

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        check_orphans(messages)
        key = match_key(messages, tools, temperature, tool_choice)
        if self.mode == "replay":
            return self._replay(key)
        return self._live(key, write=self.mode == "record")

    def _replay(self, key: dict) -> dict:
        if self._next >= len(self._entries):
            raise ReplayMismatch(
                "cassette exhausted before this request: " + canonicalize(key)
            )
        entry = self._entries[self._next]
        recorded = entry.get("request")
        if canonicalize(recorded) != canonicalize(key):
            raise ReplayMismatch(
                "next cassette entry does not match request: " + canonicalize(key)
            )
        self._next += 1
        return entry["response"]

    def _live(self, key: dict, *, write: bool) -> dict:
        missing = [
            name
            for name, val in (
                ("OPENAI_BASE_URL", self.base_url),
                ("OPENAI_API_KEY", self.api_key),
                ("OPENAI_MODEL", self.model),
            )
            if not val
        ]
        if missing:
            raise RuntimeError("unset: " + ", ".join(missing))
        body: dict[str, Any] = {
            "model": self.model,
            "messages": key["messages"],
            "temperature": key["temperature"],
        }
        if "tools" in key:
            body["tools"] = key["tools"]
        if "tool_choice" in key:
            body["tool_choice"] = key["tool_choice"]
        data = json.dumps(body).encode("utf-8")
        url = self.base_url + "/chat/completions"
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except TimeoutError:
            raise RuntimeError("chat/completions timed out") from None
        except urllib.error.HTTPError as exc:
            detail = _redact(exc.read().decode("utf-8", errors="replace")[:500])
            raise RuntimeError(f"HTTP {exc.code} from chat/completions: {detail}") from None
        except urllib.error.URLError as exc:
            raise RuntimeError(f"chat/completions failed: {exc.reason}") from None
        response = json.loads(raw.decode("utf-8"))
        response = _slim_response(response)
        if write:
            assert self.cassette_path is not None
            with self.cassette_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {"model": self.model, "request": key, "response": response},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return response

    def assert_exhausted(self) -> None:
        if self.mode != "replay":
            return
        unused = len(self._entries) - self._next
        if unused:
            raise ReplayMismatch(
                f"{unused} cassette {'entry' if unused == 1 else 'entries'} never used"
            )
