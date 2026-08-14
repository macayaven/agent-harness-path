# Agentic Harnessing — Study Companion

A scaffolded companion to [`agentic-harnessing-intensive`](../agentic-harnessing-intensive) (the course, v5).
It changes **the path, not the bar**: same fourteen sessions, same deliverables, same
evidence rules, same S13 rebuild-from-memory audit — with the accidental friction removed
and the deliberate friction kept and *labeled*.

**It also hosts a standalone course path**: **The Agent Harness Path** —
[`lessons/index.html`](lessons/index.html) is the entry point. Fourteen sessions, each
a deep HTML lesson plus a runnable stdlib-only toy notebook, followable entirely in
this workspace, with dated state-of-the-art sections. It teaches the same topics
self-contained; the original course's builds, baselines, and audit stay in the course
repo and are not replaced by anything here.

## Why this exists

The course is deliberately austere: you type every deliverable line, docs start as
`DRAFT FOR ATTACK`, and nothing counts until `evals/run.py` prints a number. That
austerity is load-bearing (see `WHY-THIS-DESIGN.md` for the evidence). But the course
has three accidental gaps:

1. **No worked examples.** Readings go straight to "build the real thing." This
   companion adds small, runnable *toy* examples for every core concept.
2. **No bridge layer.** Theory → practice is a cliff in several sessions. Each
   companion session inserts *bridge exercises*: small, guided reps on the exact moves
   the real build requires.
3. **No field guides.** Mechanical knowledge (what exit 97 means, how to tell a sub-step
   is done, common failure modes) lives nowhere. Each companion session has one.

## The one rule that keeps this honest

Everything in here is a **toy from a different domain** — a weather-bot loop, a
customer-support scripted user — never the course artifact itself. Nothing in this
folder is a solution to a course task, and it must never become one:

- Toy code is for **reading, running, and breaking** — not for copying into
  `harness/`, `evals/`, `capstone/`, `notes/`, or `scenarios/`.
- If a companion example ever looks like it could be pasted into an owned path, that's
  a defect in this companion — report it and it gets rewritten further away from the
  deliverable.
- The deliverables stay yours, typed by you, audited at S13. That rule is not hostility;
  it is the mechanism by which the course's certificate (a working platform you can
  rebuild unaided) means anything.

## How to use it

Per course session, before touching the deliverable:

1. **Concept** (10–20 min): the companion's short explainer + diagram. Replaces
   hunting through three blog posts for the one idea the session needs.
2. **Toy** (20–30 min): run the notebook, do the experiments. *Predict before you run* —
   the course's own discipline, applied to the toy.
3. **Bridge** (20–40 min): 2–4 small exercises on the toy. These are the physical
   motions of the real build, rehearsed on something you can afford to break.
4. **Build** (course repo): now do the real session from `syllabus.md`. The companion
   session ends with a "what transfers / what's new" map for exactly this moment.
5. **Self-check**: quiz with foldable answers, drawn from the session's understanding
   checklist.

## What's here

- `lessons/index.html` — **The Agent Harness Path**: the standalone course, fourteen
  sessions of HTML lessons + toy notebooks (`lessons/src/` is the editable source;
  `uv run python lessons/build.py` regenerates the HTML).
- `notebooks/` — twelve runnable toys (S1–S12): zero network, zero cost, stdlib-only,
  mock-backed. S13/S14 have no notebook by design.
- `WHY-THIS-DESIGN.md` — which parts of the course's difficulty are deliberate (with the
  evidence), which were defects, and the fix pattern applied everywhere.
- `sessions/S01-agent-loop.md`, `sessions/S02-golden-evals.md` — companion-layer session
  guides (concept → toy → bridge → build map → self-check → field guide) that feed the
  course repo's real build.
- `COURSE-MAP.md` — both layers' coverage of S1–S14: the concept gap, the toy, the
  bridge. Companion guides for S3+ are written when you approach the session —
  material written six sessions early would rot, and writing it *when needed* is part
  of how it stays honest.

## Setup

The course repo has no virtualenv — `uv` + PEP-723 inline dependencies is its toolchain,
with `requires-python = ">=3.11"`. This repo mirrors that: same `uv`, same Python floor,
exactly one declared dependency (`jupyterlab`) as the notebook runner.

```bash
uv sync            # creates .venv/ from pyproject.toml + uv.lock
uv run jupyter lab # or: uv run jupyter notebook, or open notebooks/ in VS Code
```

The notebooks themselves stay standard-library only (that's a hard rule, see
`COURSE-MAP.md`): the venv supplies Jupyter, nothing else. If you'd rather not create
the venv, any existing Jupyter frontend can open the notebooks directly.

## What this deliberately is not

- Not a replacement for `syllabus.md` — the course repo remains canonical.
- Not a video course. The interactivity here is the real kind: change a parameter,
  watch behavior change.
- Not a solution bank. See the rule above.
