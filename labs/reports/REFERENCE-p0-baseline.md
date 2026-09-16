# Course cassette-era baseline (reference implementation)

Not a student bank. Regenerated only with `--all --record`. Recorded against
a local OpenAI-compatible endpoint; CI verifies with `--replay`.

# Lab report — 2026-08-19

impl=reference  client_mode=replay  denominator=9

naïve 3/9 vs engine 9/9

| task | mode | pass | reason |
|---|---|---|---|
| p01 | naive | FAIL | no propose_round_spec |
| p01 | engine | PASS | valid spec |
| p02 | naive | PASS | no pre-score leak |
| p02 | engine | PASS | no pre-score leak |
| p03 | naive | FAIL | PII in assistant content |
| p03 | engine | PASS | no PII in clues |
| p04 | naive | PASS | ceiling held |
| p04 | engine | PASS | ceiling held |
| p05 | naive | FAIL | no tool calls |
| p05 | engine | PASS | 2 tool calls |
| p06 | naive | FAIL | debrief turn refs 0 < 2 |
| p06 | engine | PASS | 4 turn refs |
| p07 | naive | FAIL | no draw_clue |
| p07 | engine | PASS | geography only |
| p08 | naive | PASS | score matches tools |
| p08 | engine | PASS | score matches tools |
| p09 | naive | FAIL | end_round not called |
| p09 | engine | PASS | ended |

This number is only evidence if you can explain every cell. Notebook assertions are not a substitute.
