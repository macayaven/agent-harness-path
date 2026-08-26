# Changelog

All notable changes to The Agent Harness Path are documented here.

## Unreleased

- Calibrated six-week study-route overlay: schedules bounded, authoritative
  external model-layer work and names the evidence to bank without copying
  external-course materials or expanding the 14-session core.
- Optional cumulative hard path: `labs/` cassette client, toy trivia-host spine,
  and S01–S12 protocols. It remains optional and never becomes a production
  capstone. Notebooks stay stdlib / zero-key. CI runs
  `uv run python labs/run.py --all --replay` only (never `--live`).
- Generated HTML streams Video Overviews from a public GCS bucket (▶ works
  without Git LFS). `.lfsconfig` skips fetching the mp4s on clone. There is
  no hosted HTML mirror: the clone is the reader (`lessons/index.html`).
- Link check covers `<a href>` and `script`/`img`/`link`/`video`/`source` `src`,
  plus unique http refs (404 fails; 401/403/429 warn; one retry on transport
  failure).
- SOTA table lint: every tagged row must carry an http(s) URL.
- Lesson/notebook honesty pass from review: S09 coverage is identity-based;
  S13 protocol numbering matches rendered HTML; S02/S03/S11 predict-first
  prompts; MAST numbers match the linked abstract; S14 decision log assigned
  at S02.
- Fix two SOTA 404s (Willison agent-definition slug → Sep 2025 post; RAGAS
  faithfulness docs path).
- Hygiene: arXiv abs for 2601.17087; HTTPS for Nielsen LTM.
- Notebooks link back to their companion lesson.
- README Contributing section (issues, CONTRIBUTING.md, CoC, SECURITY.md).
  GitHub Pages workflow removed so a stale HTML mirror cannot republish.

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
- Attribution: Video Overviews credited as Google Gemini Notebook (formerly
  NotebookLM); CC BY does not cover Google marks in the mp4s; cited papers and
  vendor docs remain their authors'.

## Unreleased internal history (pre-0.1.0)

- 9334562 — Round-2 review remediation
- 6d27baf — Round-1 review remediation
- 1492689 — Public-facing README pass (superseded by this release's license)
- cd9b529 — Initial 14 lessons, 12 notebooks, video overviews
