# Review synthesis — pre-publication pass (August 2026)

Reviewer: Codex CLI (`gpt-5.6-sol`, reasoning effort xhigh), read-only, adversarial
prompt in `review/prompts/codex.md`. Full report: `review/reports/codex.md`.
Verdict issued: *major rework needed*. This file records what we do about it.
External factual claims were independently verified before acceptance (see
"Verification" notes inline).

## Accepted Improvements

### Correctness (all of report §1, applied)

1. **S09 "honest iff" overclaim** — reword to the exact properties the validators
   check (citation presence, event coverage); state that entailment/relevance is a
   separate, judged-tier property. Fix Anthropic Citations framing.
2. **S08 replayer accepts reordering** — fix `Replayer.__call__` to match only the
   next unused cassette entry (sequence enforced); adjust "frozen bytes" wording to
   content equality.
3. **S11 budget is postpaid soft stop** — teach soft vs hard stop explicitly; fix
   `run_pipeline` to reserve the estimated worst-case call cost before dispatch (hard
   stop in the toy); fix `validate_policy` to consult the passed `routes` mapping.
4. **S11 p50 mislabel** — rename to "median of three deterministic fixtures";
   lesson text explains what a real latency distribution needs.
5. **S12 label-before-judge "enforces" → "instructs"**; add zero-division guard to
   `cohens_kappa`; note single-author labels are reference judgments.
6. **S14 holdout contamination** — protocol now reserves a fresh unseen fixture for
   the final acceptance gate after any fix cycle.
7. **S13 oracle overclaim + unsafe `mv`** — tolerance is a decision instrument, not a
   guarantee; procedure uses a git branch/worktree instead of `mv` to /tmp.
8. **S05 bool-as-int validator** — reject `bool` explicitly (consistent with S04);
   loop over all tool calls, not just the first.
9. **S01 mock-validation claim** — soften to "reproduces the orphan-tool-result
   failure like a real API" (no full-sequence-validation claim). Same fix in
   AGENTS.md's notebook-conventions sentence.
10. **Fixture safety** — replace S10's carbonara/raw-egg "ground truth" with an
    unambiguous case; replace S06's valid-looking IBAN and bare `112` with
    unmistakably invalid/placeholder values.

### Pedagogy (report §2)

11. **S13/S14 prerequisites reframed** — the audit/ship protocols apply to any
    non-trivial project the learner owns (from this path or elsewhere); the "you
    spent twelve sessions building a system" line is corrected. (See Open Questions
    for the larger capstone-spine idea — not done in this pass.)
12. **Private-course bridges removed from standalone notebooks** — the closing
    "what transfers" cells in s01/s02 (and any course-repo references in s03+)
    become generic. The companion layer keeps its references in `sessions/` only.
13. **Lesson exercise lists audited 1:1 against notebook cells** (S01, S02 mainly) —
    lists rewritten to match what the notebooks actually contain.
14. **Promise wording** — index/AGENTS now say "predict-first, with
    attempt-then-solution cells where implementation is required."
15. **S02 false dichotomy** — exercise 4's takeaway reworded: deterministic checks
    *can* encode task-specific usefulness; the toy's checker is weak, not the tier.
16. **S06 detection ≠ boundary** — lesson now frames classifiers/keyword floors as
    fallible signals; enforcement belongs to capability isolation, least privilege,
    tool authorization, and egress control.
17. **S13 recall clarification** — the audit targets restating/rebuilding core
    abstractions and invariants, not memorizing implementation trivia.

### SOTA (report §3 — each applied only if verification confirmed)

18. EU AI Act dates corrected from EUR-Lex (per verification result).
19. S01 scoped to client-owned loop; stateful Responses API acknowledged.
20. MCP citations refreshed to the current spec release.
21. OTel GenAI conventions link updated; Langfuse "generation" framed as vendor term.
22. Apple PCC row corrected (constrained processing, not "content never leaves").
23. S14 SemVer row fixed (v1.0 = defined public API; evidence policy is ours).
24. OWASP Top 10 for Agentic Applications added to S05/S06 SOTA tables.
25. S04 Anthropic Structured Outputs row refreshed.
26. S12 "what a real gate requires" paragraph: multi-annotator adjudication,
    uncertainty intervals, repeated judge runs, position swaps, prevalence-aware κ.

### Publication (report §4)

27. Template footer rewritten for the standalone path (no "companion" framing).
28. Opening lines fixed: "twelve notebook sessions plus two protocols."
29. S13/S14 header blocks repaired (Video line placement).
30. Mermaid vendored locally (`lessons/vendor/`) — lessons work fully offline.
31. SOTA status tags normalized to the exact five; qualifiers moved to Take column.
32. Prev/next/index navigation added to the lesson template (build.py).
33. README/license clarified: learners' own work is theirs; the license restricts
    redistributing the course content itself.

## Rejected Suggestions

- **"Remove S13/S14 from the standalone path or build a full cumulative capstone
  spine."** Removal rejected — the audit and ship gate are the path's point of
  highest leverage, and reframing prerequisites (item 11) makes them honest. The
  full capstone spine is a real idea but a separate project; see Open Questions.
- **"n=1 pilot cannot certify the house is not on fire."** Partially rejected — the
  lesson already frames the pilot as a smoke detector, not certification. We accept
  strengthening the wording only.
- **Domain replacement for S09 (DIY shelves).** Rejected — the domain is
  appropriately low-stakes; the flagged fixtures are fixed (item 10), and the safety
  event in the toy is about reporting honesty, not advice quality.

## Open Questions

- Should the standalone path grow its own cumulative capstone project (one system
  built across S03–S12, then audited at S13 and shipped at S14)? Highest-value
  structural improvement available; out of scope for this pass. Decide before any
  paid/cohort version.
- Reviewer consensus: single reviewer this pass. A second independent CLI review
  (different model family) before public release would raise confidence.

## Spec Or Code Changes

Items 1–33 above; tracked in the commit(s) following this synthesis. Every notebook
edit re-verified by executing top-to-bottom; every lesson edit re-rendered.

## Residual Risks

- SOTA tables age; the August 2026 stamp is honest but the content will drift.
- The videos remain NotebookLM-generated summaries of pre-fix lesson text; if the
  lesson edits above are substantial for a session, its video is now slightly out of
  sync (acceptable for preview/review use; regenerate before any paid distribution).
- A second adversarial review may find issues this pass missed — schedule it after
  these fixes land.

## Publication pass (17 August 2026)

Standalone public release. Companion-layer `sessions/` removed; dual license
(Apache-2.0 / CC BY 4.0) plus mermaid MIT notice; S01–S12 framed as the
self-contained path and S13/S14 as optional labs; leftover overclaims (S02
latency stub, content-identical replay, undefined κ → `None`, OWASP 2026
primary links) corrected; CONTRIBUTING / CoC / SECURITY / CI / Pages added.
Video corpus is still the 14 August NotebookLM set — README and index state
that videos may lag and that lesson + notebook are canonical.
