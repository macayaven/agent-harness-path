# S05 lab — consent gate

**Optional. After the notebook.**

**Read:** [S05-consent-gate](../lessons/S05-consent-gate.html) — approve / edit /
reject; the gate constrains execution; no third mid-round ambush.

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
- `reject` aborts with no clues played. Any other decision also fails closed.

On approve, **code** enforces `difficulty` as a ceiling: `draw_clue` harder
than approved returns `difficulty_ceiling`, it does not draw.

## Verify (predict first)

1. Clean path: approve an easy spec; a round runs.
2. Adversarial: approved easy, scripted player demands a championship/hard
   clue (`p04`). Predict: hard-deck prompts never appear; state.drawn has no
   hard clue.

```bash
uv run python labs/run.py --session s05 --replay
```

## Record

PROGRESS: one held ceiling + one clean approved run. One line on abort vs
degrade (the lesson's violation semantics).

## Done when

p04's checker passes on the engine column, and you have demonstrated reject
(no side effects) on a manual run.
