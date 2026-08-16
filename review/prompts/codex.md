# Adversarial pre-publication review — The Agent Harness Path

You are an external reviewer for a soon-to-be-published self-contained course on
building, evaluating, and governing LLM agents. Repo root:
`.` (your working
directory). You are READ-ONLY: do not edit, create, or delete any file. Return
Markdown only, to stdout.

## What to review (all paths relative to repo root)

- `lessons/src/index.md` — the course entry point and structure.
- `lessons/src/S01-*.md` … `lessons/src/S14-*.md` — the fourteen lessons. This is the
  core content. Read ALL of them, in order.
- `notebooks/s01_*.ipynb` … `notebooks/s12_*.ipynb` — the twelve toy notebooks
  (stdlib-only Python, mock models). Skim structure; read code where correctness
  matters for your findings. S13/S14 have no notebooks by design (audit + protocol
  sessions) — that is intentional, not a gap.
- `README.md`, `AGENTS.md` — public face and authoring conventions.

Non-authoritative inputs: everything is a draft for attack. There is no upstream
authority to defer to except cited external sources.

## Constraints that must be preserved (do not recommend violating these)

- Notebooks are Python standard library only, zero network, zero API keys; every
  "model" is a plain Python function returning API-shaped dicts.
- Notebooks are committed without outputs; exercises are attempt-cell → solution-cell.
- Each lesson's state-of-the-art section is dated "as of August 2026" and tags each
  development as **already in this path / recognize / adopt / newer than this
  session / ignore**.
- Tone: direct, evidence-first, no cheerleading.
- The course deliberately keeps deliberate difficulty: predict-first discipline,
  attempt-before-solution, closed-book audit at S13. Do not recommend removing
  friction that is doing pedagogical work — but DO call out friction that is not.

## Review sections (use exactly these headings)

1. **Critical technical errors** — claims that are wrong, outdated, or miscited;
   code in lessons/notebooks that would not behave as the prose claims. File +
   section + what the truth is. This section gates publication.
2. **Pedagogical structure** — ordering, prerequisites, scaffolding gaps, exercises
   that don't teach what the lesson claims, predict-first prompts that are
   unguessable or trivially guessable.
3. **State-of-the-art alignment** — SOTA table entries that are stale, wrong, or
   missing something a 2026 practitioner would consider table stakes.
4. **Publication readiness** — structure, naming, accessibility to a reader who has
   NOT taken any other course, consistency across sessions, anything that would
   embarrass the author in public.
5. **Top 5 changes by impact** — ordered, each with effort estimate (S/M/L).

Be specific. "Section X is confusing" is useless; "S07's retry-context table
contradicts the S07 notebook's full_history experiment because…" is useful. If you
verify a claim against your own knowledge and find it solid, do not pad the report
with confirmations — silence means acceptable.

End with a one-line verdict: `VERDICT: publish as-is | publish after fixes | major rework needed`.
