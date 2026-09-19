# S05 lab — consent gate

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S05-consent-gate](lesson.html) — approve / edit /
reject; the gate constrains execution; no third mid-shift ambush.

## Build

After a valid spec exists, render it (60-second read) and take
`approve | edit | reject`. Evals pass `auto_approve=True`. Your CLI path must
still work with stdin.

The CLI contract is exact:

- `approve` uses the displayed spec.
- `edit` prompts once more for one JSON object containing the complete replacement
  spec: all seven required fields, no extra fields, and the types/enums in
  `labs/schemas.py`. It is replacement, not a patch.
- malformed JSON or a schema-invalid replacement aborts with
  `stop_reason="invalid_edit"`; no model or tool call occurs.
- `reject` aborts with no items served. Any other decision also fails closed.

On approve, **code** enforces `scope` as a ceiling: `pull_item` beyond the
approved scope returns `scope_ceiling`, it does not pull.

## Verify (predict first)

1. Clean path: approve a counter-scope spec; a shift runs.
2. Adversarial: counter-scope approval, scripted customer demands a banquet
   kitchen item (`p04`). Predict: banquet-scope items never fire;
   state.pulled has no banquet-scope item.

```bash
uv run python labs/run.py --session s05 --replay
```

## Record

PROGRESS: one held ceiling + one clean approved run. One line on abort vs
degrade (the lesson's violation semantics).

## Done when

p04's checker passes on the engine column, and you have demonstrated reject
(no side effects) on a manual run.
