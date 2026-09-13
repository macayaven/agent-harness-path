# Documentation map

The course has one public repository and two ways to read it. The native route is
available from a clone today. CourseWeave is an optional application with its own
repository, package version and release process.

## Start and contribute

- [README](../README.md) — course scope, native quickstart and route comparison.
- [Course map](../COURSE-MAP.md) — the S01–S14 curriculum contract.
- [Contributor guide](../CONTRIBUTING.md) — authoritative environment, edit and
  validation commands.
- [Engineering and content rules](../AGENTS.md) — toy-domain, lesson, notebook,
  diagram and public-documentation conventions.
- [Design rationale](../WHY-THIS-DESIGN.md) — deliberate difficulty and the fix
  pattern.

## Optional study interfaces

- [Full-course study guide](../study/FULL-COURSE.md) — the 12 required notebook
  sessions and two optional protocols.
- [CourseWeave pilot contract](../study/COURSEWEAVE-PILOT.md) — schema-v2 manifest,
  installation boundary and adapter behavior.
- [First exploratory test](../study/FIRST-TEST.md) — reusable S01/S02 interaction
  and transfer protocol.

The public CourseWeave `v0.1.0` wheel is not compatible with this course's
schema-v2 manifest. The v0.2.0 macOS bundle and its public URL are documented as
a release candidate, but they are not available while the linked release notes
remain Draft. Outside learners can use the native route without CourseWeave.
After publication, verify the named bundle against the CourseWeave-owned
`SHA256SUMS` before extraction; the course tag does not version the application.

## Release evidence

- [Release runbook](RELEASING.md) — promotion gates, assets, migration and
  rollback for the course repository.
- [Draft v0.2.0 notes](releases/v0.2.0.md) — proposed next course release; no tag
  or publication is implied.
- [Bounded student-pilot report](verification/student-pilot-2026-09-13.md) and
  [JSON receipt](verification/student-pilot-2026-09-13.json) — exact local
  artifacts and observed checks, with private paths and raw logs excluded.

`CHANGELOG.md` is the complete reader-facing history. Draft release notes summarize
one proposed release and link back to it; they do not replace the changelog.

## Ownership and privacy

Course source, blank templates and generated lesson artifacts belong in Git.
Learner-edited notebooks, progress, observations and work outputs belong in a
separate local folder chosen by the learner. A clean clone or fresh CourseWeave
state directory is the migration boundary; no release script rewrites an old
workspace.

Public feedback should contain the smallest useful reproduction. Exclude
credentials, raw chats, participant content, private project names, machine paths
and raw operational logs. A local acceptance report supports only the named
artifact, environment and checks. It does not establish general accessibility,
learning efficacy, teacher workflows, live-provider behavior, compliance or
production readiness.

The one-click
[course feedback form](https://github.com/macayaven/agent-harness-path/issues/new?template=course-feedback.yml)
covers native study, optional labs, the CourseWeave route and S13/S14. Submission
is learner-controlled; neither course route sends telemetry, notebooks, chats or
the optional observation CSV to GitHub automatically.
