# Security policy

This repository is educational material: static HTML lessons, Python-stdlib
notebooks that do not talk to a network, and an optional `labs/` hard path
whose CI job is cassette `--replay` only. There is no production service and
no authentication.

## What to report

- A notebook that, as committed, performs network I/O, reads credentials, or
  executes something beyond the labeled teaching examples.
- A committed `labs/` cassette, report, or source file that contains a live
  API key or a real-round transcript.
- A lesson that includes a real secret, a live credential, or instructions that
  would cause a reader to disable a real safety control in production without
  saying so.
- A supply-chain issue in `uv.lock` / vendored `lessons/vendor/mermaid.min.js`.

Do **not** report:

- Intentionally broken teaching variants (S01's loop that drops append-verbatim,
  S06's detector that false-triggers). Those are labeled. See `AGENTS.md`.
- "This toy is not a production harness." That is by design.

## How to report

Use [GitHub private vulnerability reporting](https://github.com/macayaven/agent-harness-path/security/advisories/new)
if it is enabled, or email macayaven@gmail.com with the file path and a
reproducer. Please do not open a public issue for a real secret.

We will acknowledge within a week. There is no bug bounty.
