# S05 bridge — consent gate (real host)

## Files

Core: `lesson.html`,
`toy.py`, `cafe/consent.py` (`run_shift`,
`check_fire`, `fire_requested`) — the gate before `fire_ticket`. Optional café-host
lab: `sessions/s05-consent-gate/lab.md`, `run_engine` consent block in
`labs/cafe_host/engine.py`, ceiling in `labs/cafe_host/tools.py`
`pull_item` / `propose_order`.

## The gap

The core toy is a live approve/edit/reject gate over `propose_order` before the
irreversible `fire_ticket`. The optional café host’s
`run_engine(..., auto_approve=True)` is what evals use. CLI path
(`auto_approve=False`) uses `input_fn` or `input`:

- `approve` — keep spec.
- `edit` — one JSON object, **full replacement**, `validate_spec`. Failure →
  `stop_reason="invalid_edit"`, no model/tool call (`_stopped_result`).
- `reject` — `stop_reason="rejected"`, empty messages, no items.
- anything else → `invalid_decision`.

After approve, **code** holds the ceiling: `pull_item` beyond the approved
scope returns `scope_ceiling` and puts nothing in `state["pulled"]`.
p04 scripts “fire a banquet kitchen item” against a counter-scope spec.
Engine must PASS. Naïve has no tools; its “ceiling held (nothing pulled)”
is a different (weaker) story — still explain the cell.

## Commands

```bash
# core path: offline by default; COURSE_MODE=live opts into your configured endpoint
uv run marimo edit sessions/s05-consent-gate/toy.py
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s05 --replay
```

Manually demonstrate `reject` once (no side effects). Do not skip that sitting.

## Predict-first

Approved counter scope + p04 demand: banquet-scope items never appear; no
banquet-scope id in `state["pulled"]`.

## Assistant: do / don't

Do: distinguish auto_approve (suite) vs stdin (human). Point at `pull_item`
not the system prompt for the ceiling. Don't: allow a mid-shift second
consent. Don't: implement “edit” as a JSON patch.
