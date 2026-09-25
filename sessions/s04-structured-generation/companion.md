# S04 companion — structured shift spec (real host)

> Tutor context for this session. Attach it in editor chat (`@sessions/s04-structured-generation/companion.md`); you do not need to read it to finish the session.

## Files

Core: `lesson.html`,
`toy.py`, `cafe/schema.py` (the ticket
contract, `ask_ticket`, the stdlib validator and bounded retry). Optional café-host
lab: `sessions/s04-structured-generation/lab.md`, `labs/cafe_host/tools.py`
(`propose_order`), `labs/schemas.py`, `labs/spec_schema.py`
(`validate_spec`).

## The gap

The core toy validates a ticket and retries through the model seam. Its checkpoint
compares first-attempt shape and meaning, then final acceptance separately;
`ask_ticket_run` retains the errors a successful repair would otherwise hide.
The core requests JSON text with trusted menu facts and offers no tools. Offline
mode uses authored teaching fixtures, not the lab's live-model cassettes; edited
briefs require live mode. A passed ticket means shape and menu agreement only,
not allergy clearance, customer agreement or permission to send an order.
Transport failures retain earlier outcomes and stop the remaining brief batch.
The protocol assertion inspects those saved runs; it does not launch another request.
An optional [recorded comparison](recordings/model.jsonl) preserves a genuine
model run separately from the authored controls. See the
[fixture review](../../docs/cassette-review-2026-09-22.md) for provenance and limits.
In the lab, the same validation-and-error-feedback idea applies to **tool
arguments**, with the host responsible for tool execution and state.
The café host’s
`propose_order` already:

- Builds a spec dict from tool arguments.
- `validate_spec` → on `SpecError` returns `{"error": str(exc)}` (retry
  context, not a crash).
- If the requested scope reaches past `state["approved_scope"]` (counter <
  kitchen < banquet), returns `{"error": "scope_ceiling", "approved": LEVEL}`
  and increments `ceiling_hits`.
- Else stores `state["spec"]`, updates the approved scope and allowed
  sections, returns `{"ok": True, "spec": spec}`.

Fields (must be approvable in a minute at S05): `occasion`, `scope`,
`sections`, `item_count` (1–5), `restrictions`, `language` (`en`),
`house_rules`. No extra keys.

p01’s checker: engine called this tool and stored a valid spec. On the
shipped host, p01 engine already PASSes.

## Commands

```bash
# core path: offline by default; COURSE_MODE=live opts into your configured endpoint
uv run marimo edit sessions/s04-structured-generation/toy.py
# after your prediction and attempt: replay the recorded model comparison offline
uv run python tools/record_fixtures.py --session s04
# optional hard path: the separate café-host lab
uv run python labs/run.py --session s04 --replay   # includes p01
```

Optional: five briefs (specific / vague / overloaded) for an
agreement n/5 if measuring with `--live` / `--record`. Replay cannot score
“agreement with your intent” beyond schema validity.

## Predict-first

For each brief: expected occasion, scope, restrictions **before** generation.

## Assistant: do / don't

Do: show the success/error envelopes; explain valid ≠ customer-true occasion.
Don't: add hidden fields. Don't fork `schemas.py`. Don't skip validation
because “the model is usually right.”
