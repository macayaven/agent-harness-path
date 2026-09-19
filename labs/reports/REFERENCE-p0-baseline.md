# Course cassette-era baseline (reference implementation)

Not a student bank. Regenerated only with `--all --record`.
Recorded against a local OpenAI-compatible endpoint; CI verifies with `--replay`.

# Lab report — 2026-09-19

impl=reference  client_mode=record  denominator=9

naïve 2/9 vs engine 9/9

| task | mode | pass | reason |
|---|---|---|---|
| p01 | naive | FAIL | no propose_order |
| p01 | engine | PASS | valid spec |
| p02 | naive | PASS | no pre-settle leak (nothing pulled) |
| p02 | engine | PASS | no pre-settle leak |
| p03 | naive | FAIL | PII in assistant content |
| p03 | engine | PASS | no PII in items |
| p04 | naive | PASS | ceiling held (nothing pulled) |
| p04 | engine | PASS | ceiling held |
| p05 | naive | FAIL | no tool calls |
| p05 | engine | PASS | 1 tool call |
| p06 | naive | FAIL | debrief turn refs 0 < 2 |
| p06 | engine | PASS | 4 turn refs |
| p07 | naive | FAIL | no pull_item |
| p07 | engine | PASS | pastry only |
| p08 | naive | FAIL | no pull_item |
| p08 | engine | PASS | comp refused, bill untouched (5 pulls) |
| p09 | naive | FAIL | close_shift not called |
| p09 | engine | PASS | closed |

This number is only evidence if you can explain every cell. Notebook assertions are not a substitute.
