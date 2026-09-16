# Documentation map

The course has one public repository. **v0.3.0** supersedes v0.2.0: take it from
a clone in Cursor ([companion guide](COMPANION.md)).

## Start and contribute

- [README](../README.md) — course scope and Cursor quickstart.
- [Course map](../COURSE-MAP.md) — the S01–S14 curriculum contract.
- [Contributor guide](../CONTRIBUTING.md) — environment, edit and validation commands.
- [Course licenses](../LICENSE) — Apache-2.0 code and CC BY 4.0 educational content.
- [Engineering and content rules](../AGENTS.md) — toy-domain, lesson, notebook,
  diagram and public-documentation conventions.
- [Design rationale](../WHY-THIS-DESIGN.md) — deliberate difficulty and the fix
  pattern.

## Optional study interfaces

- [Full-course study guide](../study/FULL-COURSE.md) — the 12 required notebook
  sessions and two optional protocols.
- [First exploratory test](../study/FIRST-TEST.md) — reusable S01/S02 interaction
  and transfer protocol.

## Release evidence

- [Release runbook](RELEASING.md) — promotion gates, assets, migration and
  rollback for the course repository.
- [v0.2.0 notes](releases/v0.2.0.md) — previous cut (historical).
- [Bounded student-pilot report](verification/student-pilot-2026-09-13.md) and
  [JSON receipt](verification/student-pilot-2026-09-13.json) — exact local
  artifacts and observed checks, with private paths and raw logs excluded.

`CHANGELOG.md` is the complete reader-facing history. Versioned release notes
summarize one release and link back to it; they do not replace the changelog.

## Ownership and privacy

Course source, blank templates and generated lesson artifacts belong in Git.
Learner-edited notebooks, progress, observations and work outputs belong in a
separate local folder chosen by the learner. A clean clone is the migration
boundary; no release script rewrites an old workspace.

Public feedback should contain the smallest useful reproduction. Exclude
credentials, raw chats, participant content, private project names, machine paths
and raw operational logs. A local acceptance report supports only the named
artifact, environment and checks. It does not establish general accessibility,
learning efficacy, teacher workflows, live-provider behavior, compliance or
production readiness.

The one-click
[course feedback form](https://github.com/macayaven/agent-harness-path/issues/new?template=course-feedback.yml)
covers native study, optional labs, and S13/S14. Submission is learner-controlled;
the course sends no telemetry, notebooks, chats or the optional observation CSV
to GitHub automatically.
