"""Check the selected course mode before S01; offline unless explicitly live.

    uv run python -m cafe.doctor
"""

from __future__ import annotations

import sys

from cafe.model import ModelError, get_client


def main() -> int:
    try:
        client = get_client()
    except ModelError as exc:
        print(f"configuration problem:\n{exc}", file=sys.stderr)
        return 1
    print(f"mode  : {client.mode}")
    print(f"model : {getattr(client, 'model', 'stub')}")
    print(f"url   : {getattr(client, 'base_url', 'n/a')}")
    try:
        body = client.chat(
            [{"role": "user", "content": "Reply with only: ready"}],
            temperature=0.0,
        )
    except ModelError as exc:
        print(f"call failed: {exc}", file=sys.stderr)
        return 1
    reply = body["choices"][0]["message"].get("content")
    latency = getattr(client, "last_latency_ms", None)
    print(f"reply : {reply!r}")
    if latency:
        print(f"latency: {latency:.0f} ms")
    message = (
        "offline stub works; no endpoint was contacted"
        if client.mode == "stub" else "live endpoint responded"
    )
    print(f"\n{message}. Start at sessions/s01-agent-loop/lesson.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
