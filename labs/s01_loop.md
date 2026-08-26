# S01 lab — the trivia-host loop

**Optional. After the notebook.** The easy path is complete without this.

**Read:** [S01-agent-loop](../lessons/S01-agent-loop.html) — the loop is a `while`
around a stateless API; append the assistant message verbatim; pair every
`tool_call_id`.

## Build

In `trivia_host/`:

1. `tools.py` — `new_state` and `dispatch` for `draw_clue`, `score_answer`,
   `end_round` (and `propose_round_spec` if you wire it now; S04 tightens it).
   Use `labs/deck.py`. Do not fork `labs/schemas.py`.
2. `loop.py` — `run_loop(client, messages, tools, dispatch, max_turns=8)`.
   Append the assistant message (protocol fields only). If `tool_calls` is
   empty, stop. Else dispatch, append `role=tool` results, repeat. Turn cap is
   the harness's, not the model's.
3. `engine.py` — `run_engine` that starts from `house_rules.PINNED_RULES` then
   `STARTER_PERSONA` and drives one scripted user line through the loop.

The client is `labs.client.Client`. It already rejects an orphaned tool result
(the S01 failure class) before any network or cassette lookup. Before coding,
read the public tool-result serialization and return-envelope contract in
[`labs/README.md`](README.md#wire-contract-so---replay-matches); cassette replay
matches those shapes exactly.

## Verify (predict first)

Write the expected transcript shape (roles, whether a tool fires) *before*
running.

```bash
uv run python labs/run.py --session s01 --replay
# or --live with OPENAI_* set
```

## Record

A row in `labs/PROGRESS.md`.

## Done when

One scripted round completes (a tool actually ran) **and** the pairing check
prints that an orphaned tool result is rejected.
