# Why the course feels hostile — and what this companion does about it

An honest anatomy of the friction in `agentic-harnessing-intensive`, separated into
**deliberate difficulty** (keep — it's the mechanism) and **accidental difficulty**
(fix — it's just missing scaffolding). Then the fix pattern used throughout this
companion.

## The deliberate difficulty, and the evidence for it

The course was not born austere. V3 had gates, rubrics, hint ladders, and long-form
guidance — and it produced, in its own words, *"zero lines of harness code and no valid
eval number"* in four sessions (CURRICULUM-HISTORY.md, V3.1→V4). The one documented
moment of real engagement was adversarial: attacking a finished document and finding
four defects. V4/V5 are built around that observation.

The design choices that feel hostile, and what buys them:

| Choice | Feels like | Buys |
|---|---|---|
| You type every deliverable line | Bureaucracy, slow | Generation effect + S13 auditability: what you typed, you can rebuild |
| DRAFT FOR ATTACK, not tutorials | "Why won't it just explain?" | Critique of a finished artifact is the one engagement mode this course *measured* as working for you |
| No step-by-step build instructions | "Lack of instructions" | The path *is* the skill; S13 tests the path, not the artifact |
| A number closes every session | Pressure | Evidence-over-claims, made mechanical; the course's core doctrine |
| Predict before you run | Extra bookkeeping | Prediction misses are where the learning is; the suite reports them |

The completion research behind V2 (CURRICULUM-HISTORY.md, V1→V2 finding 6) adds:
self-paced courses complete at ~20–30%, and the dominant abandonment mechanism is
**re-entry friction**, not difficulty. Which inverts the naive conclusion: the way to
make this course *kinder* is not to lower the bar — it's to make each session easier
to **start** and easier to **resume**.

**Verdict: keep all of it.** A version of this course that hands you the code produces
a certificate you can't defend at S13 and a platform you don't own. That's the friendly
tutorial trap, and it's why regular courses feel nicer and teach less.

## The accidental difficulty — real defects you spotted

Your four complaints, adjudicated:

### 1. "The examples are not ideal for teaching the concepts" — TRUE, and it's the biggest defect

The course has **no purpose-built teaching examples at all**. Concepts are taught only
through (a) readings about other people's systems and (b) the deliverable itself. The
worked-example effect is one of the most replicated results in instructional science:
studying a small, complete, runnable example first measurably improves later
independent problem-solving — and the effect is *largest* for exactly the multi-step
procedures this course teaches (loops, drivers, checkers).

Note the asymmetry: the course *does* apply this insight to prose (DRAFT FOR ATTACK is
a worked example you critique) and *fails* to apply it to code, where you need it more.

**Fix:** every core concept gets a toy worked example — runnable, inspectable, from a
different domain than the deliverable.

### 2. "Gaps between theory → practice" — TRUE

Example: S2 assigns a blog post about eval philosophy, then says "extend `run.py` with
`type: rehearsal` support: drive the engine with `script.jsonl` as the simulated user."
Between those two sits: what a scripted-user driver is, how it differs from a single
prompt, where naive and harness modes diverge and rejoin, how a transcript becomes a
checkable artifact. None of that is in the reading; all of it is assumed.

**Fix:** the bridge layer — 2–4 small exercises on the toy that rehearse the exact
mechanics of the real build, with a "what transfers / what's new" map at the end.

### 3. "Lack of instructions" — HALF TRUE

The session-level instructions are actually fine (Read → Build → Verify → Record, with
commands). What's missing is the **field guide**: the mechanical reference knowledge
that has no pedagogical value to withhold — what exit 97 vs 98 means in `run.py`, what
`runner.sh`'s SKIP means, how to tell whether a sub-step is done, the three ways the
LiteLLM route usually fails. Hunting for these is *unproductive* friction: struggling
with them teaches nothing about harness engineering.

The productive kind — deciding how the rehearsal driver should be structured — stays
with you.

**Fix:** each companion session ends with a field guide: exit codes, invariants,
"done means…" lines, and the failure modes you'll actually meet.

### 4. "No interactive, rich multimedia content" — TRUE, within limits

Can't fix the video part (nothing in this toolchain produces video). But "interactive"
done properly is better than video for this material anyway: runnable notebooks where
you change a parameter and watch the behavior change, and diagrams that make the
invisible structure (message lists, state machines, diverge/rejoin points) visible.

**Fix:** one notebook per core concept, mock-backed (zero network, zero cost, zero
privacy surface), each with predict-first experiments; Mermaid diagrams for every
structure the course currently describes only in prose.

## The fix pattern, applied everywhere

```
Concept (10–20 min)   → the one idea, with a diagram
Toy (20–30 min)       → run it, break it, predict-first experiments
Bridge (20–40 min)    → small guided reps on the real build's exact moves
Build (course repo)   → the unchanged, austere, owned deliverable
Self-check (10 min)   → quiz with foldable answers
Field guide           → the mechanical reference, always visible
```

The bar doesn't move. S13 still audits. Owned paths stay yours. The companion's job is
to make sure that when you're stuck, you're stuck on the *thing the session is
teaching* — never on avoidable confusion about mechanics.

## What this companion refuses to do

- **No deliverable solutions.** Toys come from different domains (weather bots,
  customer support) specifically so they can't be pasted into owned paths. If one
  drifts too close to a deliverable, it gets rewritten further away.
- **No lowered evidence bar.** The companion never replaces a `run.py` number, a
  banked baseline, or a PROGRESS row.
- **No pre-written future sessions.** COURSE-MAP.md sketches S3–S14; each is written
  when you approach it, because companion material written six sessions early rots —
  and because attacking a fresh draft is, per this course's own evidence, where you
  actually engage.
