# S04 lab — schema-constrained order spec

**Optional. After the notebook.**

**Hard-path note:** this lab builds the café host in `labs/cafe_host/` — a separate system from the notebook's `cafe/` toy. The session's `companion.md` gives the exact mapping.

**Read:** [S04-structured-generation](lesson.html)
— schema as contract; validate-and-retry; valid ≠ correct.

## Build

Wire `propose_order` (schema in `labs/schemas.py`). On invalid arguments,
the tool returns `{"error": ...}` — that is the retry context, not a crash.
Cap retries by the loop's turn cap. Persist a valid spec on `state["spec"]`.

Fields that earn their place at the consent gate (S05): `occasion`, `scope`
(counter, kitchen, banquet — how far the order may reach), `sections`,
`item_count` (1–5), `restrictions`, `language` (`en`),
`house_rules`. Do not add fields a customer cannot say yes/no to in a minute.

## Verify (predict first)

Five briefs (mix specific / vague / overloaded).
Write your expected occasion / scope / restrictions **before** generation.
Then:

```bash
uv run python labs/run.py --session s04 --replay   # includes p01
```

Plus five live or recorded `propose_order` runs if you are measuring
agreement. n/5 is the session number.

## Record

PROGRESS: 5 briefs → 5 valid specs; agreement n/5.

## Done when

Five valid specs and an agreement count you can defend. p01's checker is the
regression guard: the engine called `propose_order` and stored a valid
spec.
