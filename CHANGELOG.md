# Changelog

All notable changes to The Agent Harness Path are documented here.

## 0.4.0 — 2026-09-18

- One directory per session: `sessions/sNN-slug/` holds `lesson.md` (builds to
  `lesson.html` in place), `toy.py`, `lab.md`, `companion.md` and
  `public/diagrams/`; shared spine (`cafe/`, lab runner) and `tools/`, `tests/`,
  `study/`, `docs/` stay top-level.
- Per-session Video Overviews removed (all 14 `video.mp4` files, their lesson
  header lines, the index table column, and the per-session CDN rewrite): the
  recordings lagged the lessons and cost more to re-record than they taught.
  The S00 course overview stays as the single optional preview.
- Repo hygiene: remove `COURSE-MAP.md` and `WHY-THIS-DESIGN.md` (superseded by
  `AGENTS.md` + `docs/README.md`); remove `docs/plans/`, `docs/verification/`,
  and the release tooling (`scripts/`, `docs/RELEASING.md`, `docs/releases/`) —
  build-log history now lives outside this repo, unreferenced;
  `study/PROGRESS.md` ignored; `.vscode/` ships the md-preview default.
- Notebooks embed committed SVGs as markdown figures from
  `sessions/sNN-slug/public/diagrams/` (served by marimo at runtime, resolved
  statically against the notebook file); no `mo.mermaid`, no `cafe.diagrams`.
  The five notebook-only diagrams live next to their renders and render
  through the same pinned pipeline and receipt.
- `get_client()` is offline by default: unset `COURSE_MODE` returns the
  deterministic stub on every platform; `COURSE_MODE=live` opts into the
  learner's endpoint. Notebook setups put the repo root on `sys.path` so
  `import cafe` works in any kernel.
- Retire Spanish toy dialogue: the café menu, customer lines, model prompts,
  refusal texts, detection policy, and judge corpus are English throughout.
  `AGENTS.md` non-negotiable 8 now requires English everywhere.
- Rewrite leftover CourseWeave application wording in `study/` (Use this lesson,
  Continue, Course assistant, guide records) so study protocols match the Cursor
  companion path.
- Rebuild the course on one live-model seam, one café spine, and one marimo
  surface (`feat/course-rebuild-v2`): `cafe/` grows loop → judge across S01–S12,
  all twelve notebooks are live-by-default marimo files with an offline
  `COURSE_MODE=stub` CI path, lessons are arc-shaped with carried-in/bridge
  links, and labs stay a separate trivia hard path with a new `labs/app.py`
  marimo shell over the unchanged runner.
- Unify the live transport: `labs/client.py` shares `_post_chat_completions`
  with `cafe/model.py`; replay/record behavior and every error string are
  unchanged (`--replay` output byte-identical).

## 0.3.0 — 2026-09-16

Supersedes **v0.2.0**. Take the course in Cursor, with authored session bridges
and a complete trivia host. CourseWeave packaging from v0.2.0 is removed.

- Keep v0.2.0 lessons, notebooks, labs contracts, study overlay, and CI.
- Remove `courseweave.json`, the adapter launcher, and CourseWeave study/pilot
  docs. This cut is a clone plus Cursor, not an application host.
- Ship a **complete** `labs/trivia_host/` (same spine as `labs/reference/`), so
  `--replay` runs without filling stubs.
- Add `bridges/s01.md`–`s14.md`, `.cursor/rules/ahp-companion.mdc`, and
  `docs/COMPANION.md` (local OpenAI-compatible tutor = override base URL + key;
  lab `--live` uses separate shell `OPENAI_*`).
- Spell out that `lessons/*.html` is the reader and `lessons/src/` is authoring
  source (`lessons/README.md`). S13/S14 remain unaided.

## [0.2.0](https://github.com/macayaven/agent-harness-path/releases/tag/v0.2.0)

Versioned changes below are frozen for v0.2.0. Publication status, date and exact
artifacts are recorded on the linked GitHub release; a Pre-release remains a
verification candidate. The compatible wheel used by the earlier local pilot is
distinct from the public CourseWeave v0.2.0 assets.

### Added

- A complete schema-v2 CourseWeave curriculum manifest for all 14 modules: 12
  required notebook sessions with reading, notebook and self-check activities,
  plus the optional notebook-free S13 rebuild and S14 pilot protocols. The
  manifest defines 36 required S01–S12 activities while preserving the native
  course as the independent default route.
- Full-course study guidance, observation templates, optional S13/S14 activity
  cards, and separate immediate/delayed S01/S02 transfer fixtures. Undeclared
  transfer answers, answer keys and private participant evidence remain outside
  application grounding and public reports; learner material enters assistant
  context only through an explicit scope or Share action.
- An optional cumulative hard path in `labs/`: a cassette client, replay-first
  toy trivia-host spine, S01–S12 protocols, contract tests and a reference
  baseline. Live provider use remains explicit, optional and absent from CI.
- A calibrated six-week post-core overlay that schedules bounded external work
  and names evidence to bank without copying external course material or
  expanding the 14-session course.
- Static SVG assets and meaningful alternatives for every course diagram,
  including multiple diagrams in S08 and S14. A pinned Playwright/Mermaid
  renderer records input and output hashes and can compare fresh renders on the
  recorded renderer/font host.
- Course adapter, launcher and installed-artifact verification contracts for an
  explicitly supplied compatible CourseWeave wheel, separate platform/course
  interpreters and learner state outside the repository.
- A one-click course-feedback form for native study, optional labs, the guided
  CourseWeave route and S13/S14, with deliberate submission and explicit
  redaction of credentials, chats, participant content, private paths and work.
- Course content, adapter and preservation tests. The current suite covers 24
  unit tests; CI also executes all 12 notebooks, rebuilds the 16 generated HTML
  pages, checks SOTA URLs and links, tests lab contracts and replays committed
  cassettes on Python 3.11 and 3.12.

### Changed

- Clarified the licensing boundary with the optional CourseWeave application,
  which adopts PolyForm Shield 1.0.0. This course retains Apache-2.0 code and
  CC BY 4.0 educational content, including their commercial-reuse permissions;
  learner-created work remains the learner's.
- Generated lessons now use script-free static diagrams and stream optional
  Video Overviews from the public GCS replica. `.lfsconfig` skips video smudging
  on ordinary clones; the local `lessons/index.html` is the only supported
  reader, with no hosted HTML mirror.
- S01 and S02 gained explicit learner attempt cells and course guidance; S03–S12
  gained complete adapter coverage. Missing installed-course kernel metadata was
  corrected in S09 and S10. Semantic receipts protect all original notebook cell
  IDs, sources, metadata and output-free state.
- The optional CourseWeave experience now keeps one assistant session across
  permitted activities, uses explicit lesson scope and one-answer sharing, gates
  notebook help on the learner's prediction record, and keeps saved learner state
  outside the course checkout. These records do not certify correctness or
  completion.
- Course navigation, generated native links and notebook kernel selection now
  cover the full S01–S14 route. Lab command surfaces are copy-only and match the
  learner replay/live commands in the authored protocols.
- Link validation now covers relative `href` and resource `src` attributes plus
  unique HTTP references; 404/5xx fail while 401/403/429 warn. SOTA lint requires
  an HTTP(S) source in every tagged row.
- README and contributor guidance now describe the native route, full-course
  adapter, all-diagram workflow, public/private evidence boundary and separate
  course/platform releases. GitHub Pages automation was removed to avoid serving
  stale generated HTML.
- Learner documentation now gives complete native and post-publication guided
  macOS setup, verifies the exact CourseWeave-owned bundle against `SHA256SUMS`,
  starts provider-off in a fresh v0.2.0 study home, and keeps source development
  as contributor material. The optional observation CSV stays local unless the
  learner deliberately submits a sanitized summary.

### Fixed

- Corrected native previous/index/next navigation and ensured all 12 notebooks
  select the installed course kernel without changing their authored behavior.
- Qualified S11's gateway budget examples so local reservation and reconciliation
  claims do not imply provider-wide hard spending guarantees.
- Separated immediate and delayed transfer feedback, preserved unaided attempt
  boundaries and narrowed fixture observations so they do not imply learning
  efficacy.
- Corrected lesson/notebook contradictions: S09 coverage is identity-based; S13
  protocol numbering matches generated HTML; S02/S03/S11 predict-first prompts
  match their exercises; MAST figures match the linked abstract; and S14 assigns
  the decision log at S02.
- Repaired the Willison agent-definition and RAGAS faithfulness links, normalized
  the arXiv and Nielsen references, and linked notebooks back to their companion
  lessons.

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
