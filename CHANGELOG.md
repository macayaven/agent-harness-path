# Changelog

All notable changes to The Agent Harness Path are documented here.

## 0.1.1-companion — 2026-09-16

Companion learning cut on top of **v0.1.0** (not a replacement of v0.2.0's
CourseWeave packaging).

- Keep v0.1.0 lessons and stdlib notebooks.
- Add the v0.2.0 optional hard path (`labs/`) with a **complete**
  `trivia_host/` (same spine as `labs/reference/`), so `--replay` runs without
  filling stubs.
- Add `bridges/s01.md`–`s14.md`: authored toy→lab context, wire envelopes,
  predict-first, and assistant do/don't.
- Add Cursor learner rule `.cursor/rules/ahp-companion.mdc` and
  `docs/COMPANION.md` (local OpenAI-compatible tutor = override base URL + key;
  lab `--live` uses separate shell `OPENAI_*`).
- S13/S14 remain unaided.

## 0.1.0 — 2026-08-17

Public release.

- Split license: Apache-2.0 (code) and CC BY 4.0 (lessons, videos, docs); mermaid MIT notice.
- Standalone identity: the public tree is The Agent Harness Path. Companion-layer
  session guides removed. S01–S12 are the self-contained path; S13/S14 are optional
  apply-to-your-system labs.
- Contributor surface: CONTRIBUTING.md, Contributor Covenant, SECURITY.md, issue
  and PR templates, GitHub Actions verification (notebooks, HTML rebuild, links).
- Cross-artifact honesty: S02 latency column labeled a stub; S07/S08/COURSE-MAP
  say content-identical rather than byte-identical; S13/S14 video lines name the
  protocol; Cohen's κ returns `None` when undefined; S05 SOTA links the 2026
  OWASP LLM Top 10.
- Generated HTML no longer stamps today's date (reproducible rebuilds).
- Clone paths documented with and without Git LFS (~1.2 GB videos).

## Unreleased internal history (pre-0.1.0)

- 9334562 — Round-2 review remediation
- 6d27baf — Round-1 review remediation
- 1492689 — Public-facing README pass (superseded by this release's license)
- cd9b529 — Initial 14 lessons, 12 notebooks, video overviews
