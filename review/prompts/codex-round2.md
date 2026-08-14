# Adversarial review, ROUND 2 — The Agent Harness Path (post-remediation)

You are an external reviewer for a self-contained course on building, evaluating,
and governing LLM agents, soon to be published. Repo root (your working directory):
`/Volumes/mac-studio-ssd/education/agentic-harnessing-companion`. You are READ-ONLY:
do not edit, create, or delete any file. Return Markdown only, to stdout.

This is round 2. Round 1 (another reviewer, verdict "major rework needed") produced
the report at `review/reports/codex.md`; the maintainers' disposition of every item
is in `review/synthesis.md`; all claimed fixes are committed in the working tree you
are reading.

## Your two jobs

### Job 1 — Validate the round-1 fixes

Read `review/reports/codex.md` and `review/synthesis.md`, then CHECK the actual
files: for each round-1 finding, is the fix real, correct, and complete — or
cosmetic, partial, or a new inconsistency introduced by the edit? Pay special
attention to:

- `notebooks/s08_observability_replay_toy.ipynb` — does the Replayer now truly
  enforce cassette order, and do the experiments still teach what the markdown says?
- `notebooks/s11_budgets_routing_toy.ipynb` — is the pre-dispatch budget gate
  coherent (estimate == actual for these mocks), and is the median/p50 wording now
  honest?
- `notebooks/s05_consent_gate_toy.ipynb` and `s12_judge_calibration_toy.ipynb` —
  bool rejection, every-call fencing, kappa guard.
- `lessons/src/S09-evidence-reports.md` — are the validator claims now exactly as
  strong as the code, no stronger?
- `lessons/src/S13-rebuild-from-memory.md` and `S14-ship-and-pilot.md` — the
  own-project reframing, git-based audit procedure, second-holdout gate, SemVer and
  EU AI Act precision.
- SOTA corrections (EU AI Act Reg. 2026/1744, OpenAI Responses API, MCP 2026-07-28,
  OTel GenAI repo, Apple PCC, OWASP Agentic Top 10, Anthropic Structured Outputs) —
  now correct and internally consistent?
- Infra: `lessons/template.html` footer, `lessons/build.py` nav, vendored mermaid,
  exact status tags, README/index opening lines.

A fix that introduces a NEW contradiction between lesson prose and notebook behavior
counts as not fixed.

### Job 2 — Fresh sweep

Hunt for anything round 1 missed, same standards: technical accuracy, pedagogy
(ordering, scaffolding, exercises that don't teach what the lesson claims),
SOTA currency, publication readiness. Read `lessons/src/index.md`, all
`lessons/src/S01–S14-*.md`, skim `notebooks/s01–s12`, `README.md`, `AGENTS.md`.

## Constraints (unchanged — do not recommend violating)

Notebooks stdlib-only / zero network / no outputs committed; attempt-then-solution
cells; predict-first discipline; SOTA sections dated August 2026 with the five exact
status tags; direct dry tone; deliberate difficulty is intentional (predict-first,
closed-book audit) — flag friction that isn't doing pedagogical work instead.

## Report format

1. **Round-1 validation** — per finding: FIXED / PARTIAL / NOT FIXED / NEW ISSUE
   INTRODUCED, one line each with file:section evidence.
2. **New findings** — same specificity bar as round 1 (file + section + what the
   truth is), ordered by severity.
3. **Top 3 remaining changes by impact** with effort (S/M/L).

End with `VERDICT: publish as-is | publish after fixes | major rework needed`.
