# S01 bridge — the agent loop (real host)

You are tutoring a learner on **S01**. The core path is the HTML lesson plus the
marimo toy notebook, and it ships `cafe/loop.py` — the café order-taking loop
every later session extends. The optional hard path is a separate, **complete**
café host in `labs/cafe_host/` (this companion cut). Your job is to connect
the core loop to that host when they take it, not to hide either side, and not
to rewrite the host unless asked.

## Files to keep in context

| Role | Path |
| --- | --- |
| Theory | `lesson.html` or `lesson.md` |
| Toy | `toy.py` |
| Core loop | `cafe/loop.py` (`run_shift`, `Turn`) |
| Core seam | `cafe/model.py` (`get_client`, `check_pairing`, `OrphanedToolResult`) |
| Core tools | `cafe/tools.py` (`price_check`, `check_allergens`, `propose_order`, `fire_ticket`, `close_check`) |
| Domain strings | `cafe/domain.py` |
| Protocol | `sessions/s01-agent-loop/lab.md` |
| Loop | `labs/cafe_host/loop.py` |
| Tools | `labs/cafe_host/tools.py` |
| Engine | `labs/cafe_host/engine.py` |
| Client | `labs/client.py` (`canonicalize`, `check_orphans`, cassette replay) |
| Wire strings | `labs/house_rules.py` (`PINNED_RULES`, `STARTER_PERSONA`) |
| Tool JSON | `labs/schemas.py` |
| Menu | `labs/menu.py` |
| Runner | `labs/run.py` |

Do **not** open `labs/reference/` unless the learner is stuck. In this
companion cut `cafe_host/` **is the complete host** (same spine). Study
it via the bridges; S13 is still unaided.

## Global companion constraints (every session)

- Same voice on lesson, notebook, and lab.
- Predict-first cells and “write expected …” stay empty until the learner writes.
- No API keys in files or recap blocks.
- No paste-ready generic harness (no file/shell tools).
- Do not invent a second JSON envelope. Use the table below.
- S13/S14: clarify the protocol; do not perform the audit or ship writeup.

## The gap this session exists to close

The toy runs **live** against the learner's own OpenAI-compatible endpoint via
`get_client()` from `cafe/model.py`. It walks one café shift: the assistant
proposes an order, the harness pairs every `tool_call_id`, and the turn cap
belongs to the loop. Café tools are `price_check`, `check_allergens`,
`propose_order`, `fire_ticket`, `close_check`.

The optional lab is a **client-owned loop** against `labs.client.Client`, which
either replays committed JSONL cassettes or POSTs to an OpenAI-compatible
`/v1/chat/completions`. Its tools are counter-side (`pull_item`, `settle_item`,
`close_shift`, plus `propose_order` used from S04). House rules occupy
messages[0]–[1]. Replay matching is exact on
`{messages, tools, temperature, tool_choice}`.

Same ideas: append the assistant **verbatim** (protocol fields only); pair every
`tool_call_id`; the turn cap is the harness’s; an orphaned tool result is a
**client** error, not a model error.

## Core map → optional lab host

| Core | Optional café host |
| --- | --- |
| `cafe.model.get_client()` → `LiveClient.chat` | `Client.chat(messages, tools=…, temperature=0.0)` |
| `cafe.loop.run_shift(client, state, …, max_turns=…)` | `cafe_host.loop.run_loop` |
| `cafe.tools.dispatch(state, call)` | `cafe_host.tools.dispatch(state, call)` |
| dropped assistant message | `client.check_orphans` / `OrphanedToolResult` (runs before network/cassette) |
| `max_turns` | `run_loop(..., max_turns=8)` then `stop_reason=turn_cap` |
| tool result as JSON text | `content=canonicalize(result)` if the result is not already a str |

## Shipped loop (`cafe_host/loop.py`)

For up to `max_turns`:

1. `raw = client.chat(...)`.
2. `_assistant_message` keeps `role`, `content`, and slim `tool_calls` (id, type,
   function.name, function.arguments). Drops vendor extras (reasoning, index).
3. Append that assistant dict onto `messages`.
4. If no `tool_calls`, return `(messages, "completed")`.
5. Else for each call: `dispatch(call)`; if the result is not a `str`,
   `canonicalize` it (sorted keys, compact separators, `ensure_ascii=False`).
6. Append `{role: tool, tool_call_id, content}`.
7. If the cap hits: `(messages, "turn_cap")`.

## Wire envelopes (replay)

Non-string tool results **must** be canonicalized. Do not `json.dumps` a second
recipe.

| Tool | Success | Errors |
| --- | --- | --- |
| `propose_order` | `{"ok": true, "spec": SPEC}` | `{"error": MESSAGE}` or `{"error": "scope_ceiling", "approved": LEVEL}` |
| `pull_item` | `item_id, section, scope, name, detail` | `scope_ceiling`, `section_not_allowed`, `no_item` |
| `settle_item` | `served, line_total, item_id` | `unknown_item` |
| `close_shift` | `total, items_served, stop_reason` | none |
| unknown name | — | `{"error": "unknown_tool", "name": NAME}` |

Changing `PINNED_RULES` or `STARTER_PERSONA` breaks course-cassette `--replay`.

## Commands

```bash
# core path: run the notebook live against your own endpoint
uv run marimo edit sessions/s01-agent-loop/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s01 --replay
# optional lab live local model — NOT the Cursor tutor credentials
# export OPENAI_BASE_URL=http://127.0.0.1:11434/v1
# export OPENAI_API_KEY=ollama
# export OPENAI_MODEL=llama3.2
# uv run python labs/run.py --session s01 --live
```

Default `--impl student` loads `cafe_host.*`. `--impl reference` is CI.

## Predict-first

In the café notebook, before the first call: expected roles, and whether a tool
fires. After: the pairing check must print that an orphaned tool result is
rejected, and one scripted shift must have actually called a tool.

## Assistant: do / don't

Do: walk `cafe/loop.py` `run_shift` next to the notebook loop; explain why
`_assistant_message` exists; point at `check_pairing`; if the learner continues
to the lab, explain why its replay needs canonicalize.

Don't: replace `cafe/loop.py` or `cafe_host/loop.py` with a “simpler” version;
skip pairing;
tell them to put keys in `.env` inside the course tree; open the spotter.
