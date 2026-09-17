# AGENTS.md — Repository Guidelines: The Agent Harness Path

A self-contained course on building, evaluating, and governing LLM agents:
14 HTML lessons in `lessons/`, twelve stdlib-only toy notebooks in `notebooks/`,
an optional hard path in `labs/`. There is **no product code and no product test
suite**. Entry point: `lessons/index.html`.

This file governs two audiences. Read the mode that matches what you were asked
to do, and say which mode you are in before editing anything.

| Mode | Trigger | Governed by |
|---|---|---|
| **A — Learner companion (tutor)** | Human is *taking* the course in Cursor | Read `.cursor/rules/ahp-companion.mdc`, then `bridges/sNN.md` before explaining a lab. Explain `labs/trivia_host/`; never silently rewrite it or fill predict-first work. Never open `labs/reference/` unless the learner is stuck. S13/S14: **process only** — never write the audit or the ship report. |
| **B — Contributor (redesign)** | Human is *editing* course content | Everything below. |

When a course-facing artifact and this file disagree, this file wins.

---

## Non-negotiables

These survive every rewrite, restyle, and re-theme. Breaking one is a defect.

1. **Toy-domain rule.** Every example is a toy from a domain the learner does not
   ship. If an example drifts close enough to be a drop-in harness, rewrite it
   *further away*. A paste-ready generic harness in `notebooks/` or `labs/` is a defect.
2. **Zero network, zero keys, zero cost** for S01–S12. Toys are stdlib-only
   Python (3.11+); `notebooks/` and notebook-style cells import **nothing** from
   `.venv/`. The venv supplies tooling only. `labs/` is the documented exception:
   `--replay` first-class, `--live` never the default and never in CI.
3. **Predict-first.** Markdown prompts before code; attempt cell before a clearly
   marked `# SOLUTION` cell. Never pre-fill a prediction.
4. **S13/S14 stay unaided.** No scaffolding, no generated audit, no generated ship
   report, from any mode.
5. **No secrets, raw chats, participant content, private hostnames, or home paths**
   in git, fixtures, cassettes, or recap blocks.
6. **Never break the verify workflow.** A change is done only when the commands in
   *Build, test, development commands* pass locally.
7. **Sourced claims.** SOTA rows link a URL and use exactly these tags:
   **already in this path**, **recognize**, **adopt**, **newer than this session**,
   **ignore**.
8. **English** for all prose, comments, and docs. Spanish only for toy dialogue
   where noted.

---

## Course experience mandate

The material is technically sound but reads as flat: sessions restart instead of
building, artifacts are split across three surfaces (HTML / `.ipynb` / terminal
scripts), and the payoff is delayed behind theory. Fix the experience **without**
lowering rigor. Symptom → rule:

| Symptom | Rule |
|---|---|
| Nothing carries forward; each session feels like session one | One continuous spine: the learner builds/reuses **one artifact** across S01–S12, and every session opens by naming what carries in and closes by naming what it enables. |
| No forward pull; long theory before any feedback | Session order is **hook → promise → theory → run → checkpoint → recap → bridge**. The "you will be able to" promise appears in the first screenful. |
| Three looks and feels; notebooks load like homework, labs like homework-adjacent scripts | **One interface, one runtime** (below). Never introduce a new surface without retiring one. |
| Domain the learner does not identify with (currently pub trivia) | Pick a **familiar, everyday domain the author knows firsthand** and re-skin the whole spine to it — see *Theme*. |
| Flat titles and boilerplate transitions | Every session ends with an explicit bridge sentence to the next slug, and the next begins by picking it up. No orphan sessions. |

### Theme

Trivia is the current default and may be replaced. Requirements for any
replacement: everyday and familiar to the learner, a different domain from a
production harness (rule 1), enough structure to hold all 14 concepts, and
dialogue-friendly. **Recommended default: the neighbourhood café / kitchen
shift** — orders, kitchen tickets, allergens, refunds, shift handover.

Re-skin by mapping beats, not by inventing a second course: trivia host →
counter assistant, `propose_round_spec` → propose the order ticket `draw_clue`
→ pull a menu item, `score_answer` → settle a ticket, `end_round` → close the
shift. Keep the *concepts* unchanged; keep tool names in-domain.

### One interface

Retire Jupyter as the notebook surface. Notebooks are old-feeling, hidden-state,
and un-diffable; they also fragment the path against `labs/`.

- Adopt **marimo** (pure-Python, reactive, git-diffable, offline) as the notebook
  format, added as tooling in `pyproject.toml` like `jupyterlab` is today.
- The same interface presents the **hard path**: `labs/` keeps its headless CLI
  (`labs/run.py`, used by CI and `--replay`) and gains a marimo app shell, so
  easy and hard paths look and behave identically.
- Cell code stays stdlib-only and dependency-free; the runtime is tooling.
- Migrate in one pass: convert notebooks, update lesson links, `bridges/`,
  `labs/*.md`, `notebooks/` references in `tests/`, and the CI loop, then delete
  the `.ipynb` files. Do not leave both formats in tree.

### Voice

Warm, direct, evidence-first. Dry humour tolerated; **no cheerleading, no filler,
no emoji headers**. Tables for comparison, Mermaid for structure. Keep
"naive baseline", "deterministic vs judged tier", "fixture invariant", "predict
first" as terms of art — reuse, never paraphrase. Prefer concrete payoffs
("you will bank a number you can defend") to adjectives.

---

## Repository layout

```
lessons/src/SNN-slug.md   lesson sources (editable)   → build.py → lessons/SNN-slug.html
lessons/build.py          md → html, injects prev/index/next nav
lessons/render_diagrams.py, vendor/mermaid  diagram regeneration (pinned renderer)
notebooks/sNN_*           stdlib-only toys, committed without outputs
labs/sNN_*.md             hard-path protocols; labs/run.py + cassettes + trivia_host/
bridges/sNN.md            Cursor companion rungs (distinct artifact, not lesson text)
tests/                    content + build contracts, fixtures
docs/, study/, scripts/   docs map, learner records, publish_videos.sh
```

Filenames `SNN` / `sNN` in `lessons/`, `labs/`, and `bridges/` are **different
artifacts**, not duplicated lesson text.

## Build, test, development commands

```bash
uv sync --frozen                              # pinned toolchain
uv run python lessons/build.py                # regenerate lessons/*.html
uv run python lessons/render_diagrams.py      # after editing a Mermaid block, then rebuild
uv run python -m unittest discover -s tests -v
uv run python lessons/check_links.py          # relative href/src; add --http for unique http refs
uv run python lessons/check_sota_urls.py      # every SOTA row carries a source URL
uv run python -m unittest labs/test_contracts.py
uv run python labs/run.py --all --replay      # never --live
```

Notebooks must execute top-to-bottom on 3.11 and 3.12 before you commit them.
If you rename a session slug, update all of: `lessons/src`, `notebooks`, `labs/*.md`,
`bridges/*.md`, `lessons/videos/SNN-slug.mp4`, the `DIAGRAMS` map in
`tests/test_lesson_build.py`, `COURSE-MAP.md`, `docs/`, and any GCS video path.

## Coding style and naming

- Python: 4 spaces, stdlib only in course code, snake_case functions, `SNN-slug` /
  `sNN_snake` filenames. Small, readable cells; comments explain *why*.
- Lessons: raw HTML on its own lines for `<details>` blocks; one diagram minimum
  per lesson; keep SOTA tables at Development | Status | Take.
- Match existing density. Tight sentences; no headers beyond the session structure.

## Testing guidelines

No product suite, but content is tested: `tests/` pins build output, diagram
freshness, notebook cell receipts, and transfer fixtures. Notebook verification is
execution in a clean venv; lab verification is contract tests plus `--replay`
against committed cassettes (reference implementation). CI must stay green on
Python 3.11 and 3.12, and HTML drift must be zero after a rebuild.

## Commit and pull request guidelines

Concise imperative commits naming the artifact and session
(`S03: rewrite transition into S04`, `notebooks: port s07 to marimo`). One
conceptual change per PR. PRs state the learner-facing effect, list regenerated
artifacts, and paste the command output that proves the verify workflow passed.
Link the issue for any re-theming or interface migration. No secrets, no
learner notebooks, no raw logs.

## Security and configuration

Nothing in S01–S12 reads network, keys, or credentials; keep it that way. The S01
statute intentionally demonstrates unsafe patterns inside labeled experiments —
do not "fix" the deliberately broken variants. Labs may read `OPENAI_API_KEY` from
the environment for `--live`; never print or commit it. Report real repo
vulnerabilities per `SECURITY.md`.

## Agent workflow for content changes

1. State your mode (A or B). Under B, name the session(s) and the experience
   symptom you are fixing.
2. Read the lesson source, its notebook/app, its bridge, and its lab protocol
   before editing; keep the concept and its evidence contract intact.
3. Edit sources, never generated HTML; regenerate and re-verify.
4. Preserve the arc: add the incoming recap and outgoing bridge when you touch a
   session, and update `COURSE-MAP.md` in the same change.
5. Report what you changed, which commands you ran, and any invariant you had to
   reinterpret — before claiming the change is done.
