# S04 lab — schema-constrained round spec

**Optional. After the notebook.**

**Read:** [S04-structured-generation](../lessons/S04-structured-generation.html)
— schema as contract; validate-and-retry; valid ≠ correct.

## Build

Wire `propose_round_spec` (schema in `labs/schemas.py`). On invalid arguments,
the tool returns `{"error": ...}` — that is the retry context, not a crash.
Cap retries by the loop's turn cap. Persist a valid spec on `state["spec"]`.

Fields that earn their place at the consent gate (S05): `theme`, `difficulty`,
`categories`, `clue_count` (1–5), `off_limits`, `language` (`en`|`es`),
`house_rules`. Do not add fields a player cannot say yes/no to in a minute.

## Verify (predict first)

Five briefs (mix specific / vague / overloaded; one Spanish if you want).
Write your expected theme / difficulty / off-limits **before** generation.
Then:

```bash
uv run python labs/run.py --session s04 --replay   # includes p01
```

Plus five live or recorded `propose_round_spec` runs if you are measuring
agreement. n/5 is the session number.

## Record

PROGRESS: 5 briefs → 5 valid specs; agreement n/5.

## Done when

Five valid specs and an agreement count you can defend. p01's checker is the
regression guard: the engine called `propose_round_spec` and stored a valid
spec.
