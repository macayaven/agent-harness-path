# Execution Plan 0002 — Course Rebuild v2: kill all four boredom makers at once

| Field | Value |
|---|---|
| **Status** | Landing: WP0–WP6 + WP8 done, WP7 shell done (re-theme scoped out: labs stay trivia), §12.1 unification paid. Lock regenerated. §11 live gate: GO, 12/12 notebooks live-green (receipt `docs/verification/live-gate-2026-09-17.md`; one real S09 bug found and fixed). One human step remains: diagram re-render (sandboxed browsers segfault) |
| **Created** | 2026-09-17 |
| **Base** | `feat/course-rebuild-v2` off `plan/marimo-migration` (`678f614`) |
| **Supersedes** | Plan 0001 is **absorbed**, not discarded: its marimo findings (P1–P27) and canonical-serialization rules are reused verbatim as §6 here |
| **Runtime** | marimo `==0.24.2`, Python `>=3.11`, stdlib-only course logic |
| **Model** | **Live-first.** Any OpenAI-compatible endpoint. Deterministic stub for CI only |

---

## 0. The diagnosis, restated honestly

The learner's complaint is "technically sound, but I open it and want to close
it." Four mechanical causes, ranked by how much boredom each produces:

| # | Cause | Why it bores | Fix |
|---|---|---|---|
| **B1** | **Fake models.** Every "model" in S01–S12 is a Python function returning API-shaped dicts | Predict-first against a deterministic mock is a formality: you predict what the code plainly says and it does exactly that. The harness never feels *necessary* because the thing it wraps is never unpredictable | One injected client; live by default (§3) |
| **B2** | **No arc.** Sessions restart; nothing carries forward | Twelve disconnected exercises, no accumulation, no payoff | One spine artifact; fixed session shape (§4) |
| **B3** | **Unfamiliar domain.** Pub trivia, plus seven other unrelated toys | Nothing to identify with; no continuity between sessions either | One domain, everywhere (§5) |
| **B4** | **Three surfaces.** HTML + `.ipynb` + terminal scripts | Each context switch costs momentum; labs feel like a different product | marimo for both paths (§6) |

B1 is the deepest and was under-weighted in Plan 0001. **Fixing B4 alone would
have produced "runs nicer, still flat."** This plan fixes all four in one pass.

### 0.1 Why doing all four at once is *cheaper* than doing them in sequence

Each of B1–B4 rewrites the same twelve notebooks. Sequenced, the notebooks are
rewritten four times. Together, once.

The learner confirmed they always run live and do not use cassettes. That removes
the single most expensive item in a live migration — recording and maintaining
fixture traces for twelve sessions. Nothing here records a cassette.

---

## 1. What "done" looks like

A learner clones the repo, points `CAFE_BASE_URL` at their local model, opens
S01, and works twelve sessions that build **one café-ordering agent**, each
session starting from the artifact and the number the previous one produced,
every experiment hitting a real model that genuinely surprises them.

---

## 2. Non-negotiables (unchanged from `AGENTS.md` unless listed in §9)

1. **Toy-domain rule.** Café/kitchen, never a paste-ready production harness.
   Tools stay in-domain. A generic agent framework in this repo is a defect.
2. **Course logic is stdlib-only.** The two permitted non-stdlib imports are
   `marimo` (notebook runtime) and nothing else. No SDKs: the client is
   `urllib.request` against `/chat/completions`.
3. **Predict-first survives.** With a live model the prediction is now genuinely
   uncertain, which is the point.
4. **S13/S14 stay unaided.** No scaffolding, no generated audit or ship report.
5. **No secrets in git.** Keys come from the environment and are never printed,
   logged, or written to any artifact.
6. **CI stays green with no key, no network, zero cost.** Enforced structurally
   by the stub client and a socket guard, not by policy text.
7. **Sourced SOTA rows**, five status tags, unchanged.
8. **English prose; Spanish for café dialogue** (the author works in Spanish and
   the domain is a Spanish-speaking neighbourhood café).

---

## 3. B1 — The live-model seam

### 3.1 The single design decision

**A notebook never constructs a model. It receives one.**

```python
from cafe.model import get_client
client = get_client()        # live for the learner, stub in CI
```

`get_client()` reads `COURSE_MODE`:

| `COURSE_MODE` | Client | Who |
|---|---|---|
| unset or `live` | `LiveClient` → your OpenAI-compatible endpoint | the learner (default) |
| `stub` | `StubClient` → deterministic, offline | CI only |

One seam, two behaviours, identical notebook source. This also happens to teach
dependency injection at the model boundary, which is the subject of the course.

### 3.2 Configuration (exact)

| Variable | Required for live | Default | Notes |
|---|---|---|---|
| `CAFE_BASE_URL` | yes | falls back to `OPENAI_BASE_URL` | e.g. `http://127.0.0.1:11434/v1` |
| `CAFE_MODEL` | yes | falls back to `OPENAI_MODEL` | e.g. `qwen2.5:14b-instruct` |
| `CAFE_API_KEY` | yes | falls back to `OPENAI_API_KEY` | Ollama/LM Studio: any non-empty string |
| `COURSE_MODE` | no | `live` | `stub` in CI |
| `CAFE_TIMEOUT` | no | `120` | seconds |

`CAFE_*` is checked first so the course never collides with a learner's existing
`OPENAI_*` production credentials. Missing variables raise one actionable error
naming exactly what is unset and showing an Ollama example. **The key is never
included in an error, a traceback, or a printed request.**

### 3.3 What changes in the teaching, honestly

Exact-value assertions die. `assert survival_rates(...) == (7, "100% (2/2)", "0% (0/6)")`
is not true of a real model. They become **invariant and statistical** checks:

| Old (mock) | New (live) |
|---|---|
| `assert caught == 4` | `assert caught >= baseline_caught` — the layered policy never does worse than the floor |
| `assert survival == "0% (0/6)"` | `assert pinned_rate > unpinned_rate` — pinning beats burying, measured over N probes |
| `assert a == b == c` | replay of *your own* recorded trace is byte-identical to the live run that produced it |

This is more truthful. The deterministic version taught a claim the real world
only holds probabilistically, which is precisely the lesson S12 is about.

**Flaky-test discipline.** A live assertion that can fail on a good day is a
defect. Every live assertion is one of:

- a **protocol invariant** (message pairing, schema validity, no tool ran after a
  refusal) — always true regardless of model quality;
- a **relative comparison** (governed ≥ naive on the same golden set) — run both
  arms against the same endpoint in the same session;
- a **bounded statistic** over `N >= 10` samples with an explicit tolerance,
  printed alongside the number so the learner sees the spread.

Never assert an absolute quality score against a live model.

### 3.4 Cassettes become content, not plumbing

S08 stops replaying someone else's recording. The learner records **their own**
live session and proves a replay is content-identical. That is the real
production skill and it is intrinsically motivating.

### 3.5 Model-capability note (state it in the README, do not hide it)

A small local model will be genuinely bad at S04 (structured generation) and S12
(judge calibration). For S02, S07 and S10 that is a *feature* — bad output is
exactly what those sessions measure and repair. S04 and S12 need a mid-size
instruct model with real tool-calling support. The README says so plainly and
recommends a floor.

---

## 4. B2 — The arc

### 4.1 One spine artifact

`cafe/` is a package the learner grows, one module per session. Session N
imports session N−1's module. This is the accumulation that was missing.

| S | Module added | Depends on |
|---|---|---|
| 01 | `cafe/loop.py` — the order-taking loop | `cafe/model.py`, `cafe/tools.py` |
| 02 | `cafe/evals/` — golden set, checkers, baseline | `loop` |
| 03 | `cafe/context.py` — compaction, pinning | `loop`, `evals` |
| 04 | `cafe/schema.py` — the ticket contract | `loop`, `evals` |
| 05 | `cafe/consent.py` — confirm before firing | `schema` |
| 06 | `cafe/detect.py` — allergen + off-menu layers | `evals`, `consent` |
| 07 | `cafe/repair.py` — bounded re-ask | `schema`, `evals` |
| 08 | `cafe/trace.py` — spans, record, replay | all above |
| 09 | `cafe/report.py` — shift debrief | `trace`, `evals` |
| 10 | `cafe/taxonomy.py` — failure classes from real traces | `trace`, `report` |
| 11 | `cafe/routing.py` — budgets, model routing | `evals`, `trace` |
| 12 | `cafe/judge.py` — calibrated judge | `evals`, `taxonomy` |

### 4.2 Fixed session shape (every lesson, no exceptions)

```
# SNN-slug — Title
**Carried in:** <artifact + the number S(N-1) banked>
**Today you ship:** <the module this session adds>
**Time / Prereqs / Hands-on / Video:** <header block>

## The hook            — a concrete failure of yesterday's artifact, shown first
## The promise         — "by the end you will be able to X", in the first screenful
## The theory in depth — 3-5 subsections, >=1 mermaid diagram
## Build               — the notebook, predict-first
## Checkpoint          — the number you bank, and how to explain it
## State of the art    — dated table, sourced (unchanged format)
## Annotated readings
## Misconceptions and failure modes
## Self-check          — foldable details
## What this unlocks   — explicit bridge naming the next slug
```

`Carried in` / `What this unlocks` are mechanically checked: S(N)'s "carried in"
must name S(N−1)'s module, and S(N)'s bridge must name S(N+1)'s slug.

---

## 5. B3 — The domain

### 5.1 Choice

**The neighbourhood café — one evening shift.** Everyday, familiar, dialogue-rich,
structurally deep enough for all fourteen concepts, and nowhere near a
paste-ready production harness.

Entities: customers, orders, tickets, the menu, allergens, the pass, the till,
shift handover. Dialogue is Spanish; all prose, comments and docs are English.

### 5.2 Tool names (in-domain, fixed)

`propose_order`, `check_allergens`, `price_check`, `fire_ticket`, `close_check`.

### 5.3 Concept mapping (old → new, binding)

| Old toy | New café equivalent |
|---|---|
| trivia host / weather bot / concierge / mopbot / repair shop / recipe bot / DIY assistant | **one** café counter assistant |
| `propose_round_spec` | `propose_order` |
| `draw_clue` | `price_check` (pull a menu item) |
| `score_answer` | `fire_ticket` (send to the kitchen) |
| `end_round` | `close_check` (settle and close) |
| pub-quiz house rules | shift rules: allergens, 86'd items, till limits |
| medical-advice refusal | **allergen safety** refusal — same mechanics, real stakes |
| PII leak | customer card/phone data |

### 5.4 Swap procedure (the theme stays cheap to change)

All domain strings live in `cafe/domain.py`: entity names, menu fixtures, tool
names, refusal texts. Re-theming later = rewrite that one module + the lesson
prose nouns. Do not scatter domain literals across notebooks.

---

## 6. B4 — One interface

Adopt Plan 0001 wholesale. Binding rules carried over verbatim:

- marimo `==0.24.2`; notebooks are `notebooks/sNN_*_toy.py`.
- **Canonical serialization (Plan 0001 §6.11).** Commit only what
  `marimo check --fix --ignore MF004` produces; gate with `git diff --exit-code`.
  `--strict` alone cannot enforce this.
- **Never `--unsafe-fixes`** — it deletes comment-only cells, i.e. every
  predict-first and attempt skeleton.
- A pure single-function cell is hoisted to `@app.function`; setup globals are
  never cell parameters. Attempt/solution are `attempt_<topic>` /
  `solution_<topic>` top-level units.
- Hidden solutions via `mo.ui.switch` + `mo.stop` + `inspect.getsource`.
- `labs/app.py` marimo shell over the unchanged `labs/run.py`.

The full probe evidence (P1–P27) stays in
`docs/plans/2026-09-17-marimo-migration.md`; it is not repeated here.

---

## 7. Architecture

```
cafe/                     the spine the learner grows (stdlib + marimo only)
  model.py                LiveClient | StubClient | get_client()   [WP1]
  domain.py               menu, rules, tool schemas, refusal texts [WP1]
  tools.py                the five in-domain tools                 [WP1]
  loop.py .. judge.py     one module per session                   [WP3-WP6]
notebooks/sNN_*_toy.py    marimo, drives cafe/, live by default
lessons/src/SNN-*.md      arc-shaped lesson sources
labs/                     unchanged runner + new app.py shell
tests/                    contracts: arc, domain, live-safety, canonical form
```

**`labs/client.py` is not touched.** Its cassette-matching logic is the S08
contract and CI depends on it. `cafe/model.py` is a separate, simpler,
live-first client. The small duplication is deliberate: it keeps a green CI
while the course path changes. Recorded as follow-up debt in §12.

---

## 8. Test and gate specification

| ID | Invariant | Guard |
|---|---|---|
| A1 | 12 notebooks, canonical marimo form | `test_notebooks_are_canonically_serialized` |
| A2 | No `.ipynb` tracked; no stale Jupyter instructions | `test_no_current_ipynb_files_remain` |
| A3 | Course logic imports stdlib + `marimo` + `cafe` only | `test_imports_are_stdlib_only` |
| A4 | **No notebook constructs a client directly** — all go through `get_client()` | `test_single_model_seam` |
| A5 | **CI never reaches the network**: stub mode + socket guard | `sitecustomize.py` + `test_stub_mode_makes_no_socket` |
| A6 | No key, base URL or token value in any tracked file or error string | `test_no_credentials_anywhere`, `test_error_messages_redact_key` |
| A7 | Every lesson has all ten arc sections in order | `test_lesson_arc_sections` |
| A8 | S(N) "Carried in" names S(N−1)'s module; bridge names S(N+1)'s slug | `test_arc_chain_is_continuous` |
| A9 | No pre-café domain nouns remain in course surfaces | `test_domain_is_uniform` |
| A10 | Attempt skeletons unanswered; solutions gated | `test_attempt_functions_are_unanswered` |
| A11 | No live assertion asserts an absolute quality score | `test_no_absolute_quality_assertions` |
| A12 | `labs/run.py --all --replay` unchanged and green | existing CI step |

**CI command block** (replaces the nbconvert steps):

```bash
COURSE_MODE=stub uv run python -m unittest discover -s tests -v
for nb in notebooks/s*_toy.py; do
  PYTHONPATH="$PWD/tests/no_network_site" COURSE_MODE=stub \
    MARIMO_SKIP_UPDATE_CHECK=1 uv run python "$nb" > /dev/null
done
uv run marimo check --strict --ignore MF004 notebooks labs/app.py
uv run marimo check --fix --ignore MF004 notebooks labs/app.py
git diff --exit-code -- notebooks labs/app.py
uv run python -m unittest labs/test_contracts.py
uv run python labs/run.py --all --replay
```

**Learner smoke test** (documented in README, never in CI):

```bash
export CAFE_BASE_URL=http://127.0.0.1:11434/v1 CAFE_API_KEY=ollama CAFE_MODEL=qwen2.5:14b-instruct
uv run python -m cafe.doctor      # one live call, prints model + latency, redacts key
```

---

## 9. Governance amendments to `AGENTS.md`

Three invariants genuinely change. State them, do not let an executor infer them.

1. **Zero-network becomes CI-scoped.** Old: "notebooks are zero network, zero
   keys, zero cost." New: *"CI is zero network, zero keys, zero cost, enforced by
   `COURSE_MODE=stub` and a socket guard. The learner path is live by default
   against an OpenAI-compatible endpoint they choose; a local model costs
   nothing. No key is ever committed, printed or logged."*
2. **Stdlib rule gains two named exceptions:** `marimo` (runtime) and `cafe`
   (the course's own package). No third-party SDK, ever.
3. **Toy-domain rule is re-pointed** at the café and gains the swap procedure in
   §5.4.

`COURSE-MAP.md` session-contract rule 2 is amended identically.

---

## 10. Work packages

Disjoint write scopes. WP1–WP2 are sequential; WP3–WP6 run in parallel; WP7–WP9
close out.

| WP | Title | Write scope | Parallel |
|---|---|---|---|
| WP0 | Branch + baseline green | — | — |
| WP1 | **Foundation**: `cafe/model.py`, `domain.py`, `tools.py`, `doctor.py`, stub, socket guard, foundation tests | `cafe/**`, `tests/no_network_site/**`, `tests/test_cafe_foundation.py`, `pyproject.toml` | — |
| WP2 | **S01 locked template**: lesson + marimo notebook + `cafe/loop.py` | `lessons/src/S01-*.md`, `notebooks/s01_*.py`, `cafe/loop.py` | — |
| WP3 | Sessions 02–04 | those lessons, notebooks, `cafe/{evals,context,schema}` | WP4, WP5, WP6 |
| WP4 | Sessions 05–07 | those lessons, notebooks, `cafe/{consent,detect,repair}` | WP3, WP5, WP6 |
| WP5 | Sessions 08–10 | those lessons, notebooks, `cafe/{trace,report,taxonomy}` | WP3, WP4, WP6 |
| WP6 | Sessions 11–12 + S13/S14 re-point | those lessons, notebooks, `cafe/{routing,judge}` | WP3, WP4, WP5 |
| WP7 | Labs re-theme + `labs/app.py` | `labs/**` except `run.py`/`client.py`/cassettes | — |
| WP8 | Docs, arc tests, CI, governance | `README.md`, `AGENTS.md`, `COURSE-MAP.md`, `bridges/**`, `docs/**`, `.github/**`, `tests/test_arc.py` | — |
| WP9 | Rebuild HTML, full gate, push | generated `lessons/*.html` | — |

**Dispatch contract for every WP:** write scope; the exact §8 gates it must pass;
"never touch `labs/run.py`, `labs/client.py`, cassettes, or another WP's files";
"live assertions must follow §3.3"; return the files changed.

---

## 11. Sequencing rule (the make-or-break gate)

After **WP2**, stop and evaluate S01 against a real local model before spending
anything on WP3–WP6. If a live S01 does not feel dramatically better, the arc and
theme work will not save it, and that is worth knowing after one session rather
than twelve.

---

## 12. Known debt, stated rather than hidden

1. ~~`cafe/model.py` duplicates the live half of `labs/client.py`.~~ **Paid on
   this branch:** both clients share `_post_chat_completions` in `cafe/model.py`;
   each keeps its own serialization, redaction, and error strings (parity-probed,
   `--replay` output byte-identical).
2. Live sessions are non-deterministic by design; the SOTA tables and the
   "expected output" prose must describe *shapes*, not exact strings.
3. Small local models will underperform on S04/S12 (§3.5).
4. Preview videos (`lessons/videos/`) still show trivia. They are explicitly
   labelled as lagging previews; the re-record procedure is `docs/RELEASING.md`
   §4 (interactive generation + LFS + bucket publish, one PR).
