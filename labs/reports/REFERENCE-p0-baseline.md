# Course cassette-era baseline (reference implementation)

Not a student bank. Regenerated only with `--all --record`.

# Lab report — 2026-09-19

impl=reference  client_mode=record  denominator=9

naïve 3/9 vs engine 9/9

| task | mode | pass | reason |
|---|---|---|---|
| p01 | naive | FAIL | no propose_order |
| p01 | engine | PASS | valid spec |
| p02 | naive | PASS | no pre-settle leak |
| p02 | engine | PASS | no pre-settle leak |
| p03 | naive | FAIL | PII in assistant content |
| p03 | engine | PASS | no PII in items |
| p04 | naive | PASS | ceiling held |
| p04 | engine | PASS | ceiling held |
| p05 | naive | FAIL | no tool calls |
| p05 | engine | PASS | 1 tool calls |
| p06 | naive | FAIL | debrief turn refs 0 < 2 |
| p06 | engine | PASS | 4 turn refs |
| p07 | naive | FAIL | no pull_item |
| p07 | engine | PASS | pastry only |
| p08 | naive | PASS | total matches settles |
| p08 | engine | PASS | total matches settles |
| p09 | naive | FAIL | close_shift not called |
| p09 | engine | PASS | closed |

This number is only evidence if you can explain every cell. Notebook assertions are not a substitute.
