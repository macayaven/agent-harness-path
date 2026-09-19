# Your workdir — complete host (companion cut)

This folder is a **working café host**, copied from the course reference
spine so you can run `--replay` and study real moving parts with the Cursor
companion. It is still a toy café domain: four tools, no files, no shell.
It is a separate system from the notebook's `cafe/` toy — same domain,
different artifact.

```bash
uv run python labs/run.py --session s01 --replay   # default --impl student
```

Read with `bridges/README.md`. Protocols live in `sessions/sNN-slug/lab.md`.

`labs/reference/` is the same spine imported as `reference.*` for CI
`--impl reference`. You do not need both to *take* the course.

S13 is still unaided: do not ask the assistant to write the rebuild audit.
