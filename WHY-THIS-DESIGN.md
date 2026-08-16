# Why this path is built this way

An honest split between **deliberate difficulty** (keep — it's the mechanism)
and **accidental difficulty** (fix — it's just missing scaffolding). Then the
pattern used in every session.

## The deliberate difficulty, and what it buys

A version of this material that hands you production harness code produces a
certificate you can't defend and a system you don't own. The path keeps the
moves that force ownership:

| Choice | Feels like | Buys |
|---|---|---|
| You type the real system yourself | Bureaucracy, slow | Generation effect + S13 auditability: what you typed, you can rebuild |
| Toys, not tutorials that finish the job | "Why won't it just explain?" | Critique and prediction beat copy-paste; the notebook is a worked example you break |
| No cumulative capstone repo in this tree | "Where is the product?" | S01–S12 teach mechanisms; S13/S14 apply them to a system *you* own |
| A number closes every measurement | Pressure | Evidence-over-claims, made mechanical |
| Predict before you run | Extra bookkeeping | Prediction misses are where the learning is |

Self-paced courses complete at ~20–30%; the dominant abandonment mechanism is
**re-entry friction**, not difficulty. The way to make this path kinder is not
to lower the bar — it's to make each session easier to **start** and easier to
**resume**.

**Verdict: keep the bar.** Lowering it produces fluency without recall.

## The accidental difficulty this path exists to remove

### 1. No purpose-built teaching examples

Concepts taught only through (a) readings about other people's systems and
(b) the learner's own unfinished product leave a gap. The worked-example effect
is one of the most replicated results in instructional science: studying a
small, complete, runnable example first measurably improves later independent
problem-solving — and the effect is *largest* for exactly the multi-step
procedures this path teaches (loops, drivers, checkers).

**Fix:** every core concept gets a toy — runnable, inspectable, from a domain
that is not a production harness.

### 2. Gaps between theory and practice

A blog post about eval philosophy does not teach what a scripted-user driver
is, how naive and governed modes diverge and rejoin, or how a transcript
becomes a checkable artifact.

**Fix:** the notebook is the missing middle — predict-first experiments on the
exact mechanical moves, with a "what transfers / what's new" cell at the end.

### 3. Hunting for mechanical trivia

Struggling with "what does this stop reason mean" or "which invariant did I
break" is productive. Struggling with missing field-guide knowledge that has
no pedagogical value to withhold is not.

**Fix:** each lesson ends with misconceptions, failure modes, and a self-check.
The protocol sessions (S13/S14) add "done when" lines.

### 4. Passive consumption

Video overviews exist as preview/review. The learning happens in the notebook:
change a parameter, watch the behavior change, miss a prediction on purpose.

## The fix pattern, applied everywhere

```
Concept (20–40 min)   → the one idea, with a diagram
Toy (30–60 min)       → run it, break it, predict-first experiments
Self-check (10 min)   → quiz with foldable answers
(Optional) S13 / S14  → apply the chain to a system you own
```

The bar doesn't move. S13 still audits — on *your* project. The path's job is
to make sure that when you're stuck, you're stuck on the *thing the session is
teaching* — never on avoidable confusion about mechanics.

## What this path refuses to do

- **No paste-ready harness.** Toys come from different domains specifically so
  they can't be dropped into production. If one drifts too close, it gets
  rewritten further away.
- **No lowered evidence bar.** A notebook assertion is not a banked baseline.
- **No silent SOTA rot.** Tables are dated; a row without a source is omitted.
