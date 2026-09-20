"""S08 - observability & replay.

`cafe/consent.run_shift` drives one protected shift. This module makes it observable
and repeatable:

* `Tracer` builds a tree of spans; a *generation* is a span that also carries the
  model's input, output and usage. Wrapped around `run_shift`, the tree is what
  turns "which turn burned the tokens?" into arithmetic.
* `RecordingClient` wraps any client and appends every `{request, response}` pair
  to a JSONL trace - your own live session, on disk, in order.
* `ReplayClient` serves those recorded responses back, strictly: the next
  recorded request must equal the one arriving, in order, and every recorded call
  must be consumed when the shift ends. Matching polices the calls that *arrive*;
  `assert_exhausted()` polices the calls that *should have arrived*.

A replay that is content-identical to the live run that produced it is the proof
that the transcript came from the harness, not from luck.

Nothing here writes anywhere on its own: every function that records takes the
path it writes to, and the notebook hands it a path inside a TemporaryDirectory.
"""

from __future__ import annotations

import contextlib
import copy
import json
import time
from pathlib import Path
from typing import Any, Iterator

from cafe.consent import run_shift
from collections.abc import Callable

__all__ = [
    "ReplayMismatch",
    "TickClock",
    "Tracer",
    "NullTracer",
    "NULL_TRACER",
    "TracingClient",
    "RecordingClient",
    "ReplayClient",
    "record_shift",
    "replay_shift",
    "load_records",
    "transcript",
    "cited_turns",
    "usage_of",
    "export_fail_soft",
]


class ReplayMismatch(AssertionError):
    """A replayed request did not match the next recorded request, or the
    recording was not fully consumed by the end of the shift."""


class TickClock:
    """Deterministic stand-in for the wall clock: `step` seconds per read.

    Real tracers call `time.monotonic()`. Injecting a tick clock keeps a rendered
    trace tree reproducible, which is what makes two replays comparable at all.
    """

    def __init__(self, step: float = 0.4) -> None:
        self.step = step
        self.t = 0.0

    def __call__(self) -> float:
        self.t += self.step
        return self.t


class Tracer:
    """Minimal trace tree: nested spans; generations carry input/output/usage."""

    def __init__(self, exporter: Any = None, clock: Any = None) -> None:
        self.clock = clock or time.monotonic
        self.exporter = exporter
        self.roots: list[dict] = []
        self._stack: list[dict] = []

    @contextlib.contextmanager
    def span(self, name: str, kind: str = "span", **attrs: Any) -> Iterator[dict]:
        """Open a span; the caller writes output/usage into the yielded dict."""
        node: dict[str, Any] = {
            "name": name,
            "kind": kind,
            "attrs": dict(attrs),
            "children": [],
            "t0": self.clock(),
            "duration_s": 0.0,
        }
        if self._stack:
            self._stack[-1]["children"].append(node)
        else:
            self.roots.append(node)
        self._stack.append(node)
        try:
            yield node["attrs"]
        finally:
            self._stack.pop()
            node["duration_s"] = round(self.clock() - node["t0"], 3)

    def generation(self, name: str, **attrs: Any) -> Any:
        """A span that also carries a model call: input, output, usage."""
        return self.span(name, kind="generation", **attrs)

    def nodes(self, kind: str | None = None) -> list[dict]:
        """Every node in the tree, depth-first, optionally filtered by kind."""
        found: list[dict] = []

        def walk(node: dict) -> None:
            if kind is None or node["kind"] == kind:
                found.append(node)
            for child in node["children"]:
                walk(child)

        for root in self.roots:
            walk(root)
        return found

    def generations(self) -> list[dict]:
        return self.nodes("generation")

    def export(self) -> None:
        """Ship the finished trace to the exporter.

        May raise - a dead telemetry backend is a *when*, not an *if*, so call
        `export_fail_soft` at the boundary and let the session survive it.
        """
        if self.exporter is not None:
            self.exporter({"spans": self.roots})

    def render(self) -> str:
        lines: list[str] = []

        def walk(node: dict, depth: int) -> None:
            extra = ""
            usage = node["attrs"].get("usage")
            if node["kind"] == "generation" and isinstance(usage, dict):
                extra = f"  ({usage.get('total_tokens')} tok)"
            lines.append(
                "  " * depth
                + f"{node['name']} [{node['kind']}] {node['duration_s']:.1f}s{extra}"
            )
            for child in node["children"]:
                walk(child, depth + 1)

        for root in self.roots:
            walk(root, 0)
        return "\n".join(lines) or "(empty trace)"


class NullTracer:
    """Same interface, no work: instrumentation without `if tracer:` branches."""

    def span(self, name: str, kind: str = "span", **attrs: Any) -> Any:
        return contextlib.nullcontext({})

    def generation(self, name: str, **attrs: Any) -> Any:
        return contextlib.nullcontext({})

    def export(self) -> None:
        return None

    def generations(self) -> list[dict]:
        return []

    def render(self) -> str:
        return "(tracing disabled)"


NULL_TRACER = NullTracer()


class TracingClient:
    """Wraps any client: one generation span per `chat` call."""

    def __init__(self, client: Any, tracer: Any = NULL_TRACER) -> None:
        self._client = client
        self.tracer = tracer
        self.calls = 0
        self.mode = getattr(client, "mode", "wrapped")
        self.model = getattr(client, "model", None)

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        self.calls += 1
        # The input is copied: the loop keeps mutating `messages` after the call.
        with self.tracer.generation(
            f"call-{self.calls}", model=self.model
        ) as attrs:
            attrs["input_messages"] = copy.deepcopy(messages)
            body = self._client.chat(
                messages, tools=tools, temperature=temperature, tool_choice=tool_choice
            )
            message = body["choices"][0]["message"]
            attrs["output"] = message.get("content")
            attrs["tool_calls"] = [
                call.get("function", {}).get("name")
                for call in message.get("tool_calls") or []
            ]
            attrs["usage"] = body.get("usage")
        return body


class RecordingClient:
    """Wraps any client and appends each `{request, response}` pair to a JSONL trace."""

    def __init__(self, client: Any, path: str | Path) -> None:
        self._client = client
        self.path = Path(path)
        self.calls = 0
        self.mode = getattr(client, "mode", "wrapped")
        self.model = getattr(client, "model", None)
        self.path.write_text("", encoding="utf-8")  # start a fresh trace

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        record = {
            "request": {
                "messages": copy.deepcopy(messages),
                "tools": tools,
                "temperature": temperature,
                "tool_choice": tool_choice,
            }
        }
        body = self._client.chat(
            messages, tools=tools, temperature=temperature, tool_choice=tool_choice
        )
        self.calls += 1
        record["response"] = body
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return body


class ReplayClient:
    """Serves a recording back, strictly. Never a guess: no match -> ReplayMismatch.

    Two separate invariants, because they catch two different regressions:

    * matching polices the calls that arrive - a changed request at position `n`
      raises instead of silently serving a response recorded for something else;
    * `assert_exhausted()` polices the calls that should have arrived - a
      regression that *deletes* the last model call sends nothing bad to match.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.entries = load_records(self.path)
        self._next = 0
        self.calls = 0
        self.mode = "replay"
        self.model = "replay"

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        tool_choice: Any = None,
    ) -> dict:
        request = {
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
            "tool_choice": tool_choice,
        }
        if self._next >= len(self.entries):
            raise ReplayMismatch(
                f"the recording holds {len(self.entries)} calls; this shift asked "
                f"for call {self._next + 1}. The harness now makes more calls than "
                "the run that was recorded."
            )
        entry = self.entries[self._next]
        if entry["request"] != request:
            raise ReplayMismatch(
                "call "
                f"{self._next + 1} does not match the recording. The harness has "
                "changed behaviour, or the recording is stale. Request was:\n"
                + json.dumps(request, ensure_ascii=False)[:400]
            )
        self._next += 1
        self.calls += 1
        return entry["response"]

    def assert_exhausted(self) -> None:
        """Session-end invariant: every recorded call must have been consumed."""
        unused = len(self.entries) - self._next
        if unused:
            noun = "entry" if unused == 1 else "entries"
            raise ReplayMismatch(
                f"{unused} recorded {noun} never used - the shift made fewer calls "
                "than the run that was recorded."
            )


def load_records(path: str | Path) -> list[dict]:
    """Read a JSONL trace back into records. Blank lines are ignored."""
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def record_shift(
    client: Any,
    user_turns: list[str] | tuple[str, ...],
    path: str | Path,
    *,
    responder: Callable[[str], tuple[str, Any]],
    tracer: Tracer | None = None,
    span_name: str = "shift",
    **kwargs: Any,
) -> dict:
    """Run one live shift with a recording client, inside a span.

    Returns a bundle: the run record, the tracer, and the two wrappers, so the
    notebook can show the tree and check the counters without reaching into the
    loop's internals.
    """
    tracer = tracer if tracer is not None else Tracer()
    recorder = RecordingClient(client, path)
    traced = TracingClient(recorder, tracer)
    with tracer.span(span_name, script=list(user_turns)):
        run = run_shift(traced, user_turns, responder, **kwargs)
    return {
        "run": run,
        "tracer": tracer,
        "recorder": recorder,
        "traced": traced,
        "path": Path(path),
    }


def replay_shift(
    path: str | Path,
    user_turns: list[str] | tuple[str, ...],
    *,
    responder: Callable[[str], tuple[str, Any]],
    tracer: Tracer | None = None,
    span_name: str = "replay",
    **kwargs: Any,
) -> dict:
    """Replay a recording offline. Raises unless every recorded call is consumed."""
    tracer = tracer if tracer is not None else Tracer()
    player = ReplayClient(path)
    traced = TracingClient(player, tracer)
    with tracer.span(span_name, script=list(user_turns)):
        run = run_shift(traced, user_turns, responder, **kwargs)
    player.assert_exhausted()
    return {"run": run, "tracer": tracer, "player": player, "traced": traced}


def transcript(run: dict) -> list[str]:
    """Canonical, comparable rendering of a run's conversation.

    Two runs are content-identical when their transcripts are equal. Nothing but
    the conversation enters this string, so a replay that differs is a real
    divergence, not a formatting artefact.
    """
    return [
        json.dumps(message, sort_keys=True, ensure_ascii=False)
        for message in run["messages"]
    ]


def cited_turns(run: dict) -> list[dict]:
    """The conversation as citable records: 1-based turn numbers, verbatim content."""
    return [
        {
            "turn": index,
            "role": message.get("role"),
            "content": message.get("content") or "",
        }
        for index, message in enumerate(run["messages"], start=1)
    ]


def usage_of(tracer: Any) -> dict:
    """Tokens and seconds summed over a tracer's generations."""
    tokens = 0
    latency = 0.0
    for node in tracer.generations():
        usage = node["attrs"].get("usage")
        if isinstance(usage, dict):
            tokens += int(usage.get("total_tokens") or 0)
        latency += float(node.get("duration_s") or 0.0)
    return {"total_tokens": tokens, "latency_s": round(latency, 3)}


def export_fail_soft(tracer: Any) -> str | None:
    """Export a finished trace, swallowing telemetry failure.

    Returns the error text when the exporter raised, `None` when it shipped.
    Telemetry degrades; the shift does not.
    """
    try:
        tracer.export()
    except Exception as exc:  # noqa: BLE001 - the whole point is the boundary
        return f"{type(exc).__name__}: {exc}"
    return None
