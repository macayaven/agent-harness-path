import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import contextlib
    import html
    import io
    import sys
    from pathlib import Path

    LABS = Path(__file__).resolve().parent
    if str(LABS) not in sys.path:
        sys.path.insert(0, str(LABS))

    import run as runner
    from ui import build_argv


@app.cell
def lab_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def lab_md_intro(mo):
    mo.md(r"""
    # Labs — the café-host hard path, one surface

    This page is a shell over `labs/run.py`: same runner, same cassettes, same
    report. Pick a session, pick an implementation, run. Replay is the default;
    `--live` and `--record` need shell `OPENAI_BASE_URL` / `OPENAI_API_KEY` /
    `OPENAI_MODEL`, exactly as on the terminal.
    """)
    return


@app.cell
def lab_controls(mo):
    session = mo.ui.dropdown(
        {f"s{i:02d}": f"s{i:02d}" for i in range(1, 13)}
        | {"all (selected implementation)": "all"},
        value="s01",
        label="Session",
    )
    impl = mo.ui.dropdown(
        {"student (cafe_host)": "student", "reference (spotter)": "reference"},
        value="student (cafe_host)",
        label="Implementation",
    )
    mode = mo.ui.dropdown(
        {"replay (default, offline)": "replay", "live": "live", "record": "record"},
        value="replay (default, offline)",
        label="Client mode",
    )
    tasks = mo.ui.text(
        value="",
        label="Tasks (optional)",
        placeholder="p01,p02 — blank means the session default",
    )
    go = mo.ui.run_button(label="Run lab")
    mo.vstack([session, impl, mode, tasks, go])
    return go, impl, mode, session, tasks


@app.cell
def lab_run(go, impl, mo, mode, session, tasks):
    mo.stop(not go.value)
    argv = build_argv(session.value, impl.value, mode.value, tasks.value)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = runner.main(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        print(f"argument error: {exc}", file=buf)
    mo.vstack([
        mo.md(f"**`run.py {' '.join(argv)}` → exit code {code}**"),
        mo.Html("<pre>" + html.escape(buf.getvalue()) + "</pre>"),
    ])
    return


@app.cell(hide_code=True)
def lab_md_notes(mo):
    mo.md(r"""
    ## Notes

    - The markdown report also lands in `labs/reports/last.md` (gitignored), as
      on the terminal. Replay never writes to `cassettes/`.
    - A red engine cell is the lesson, not a broken runner: read the reason, open
      the protocol (`sessions/sNN-slug/lab.md`), fix the host, re-run.
    - `--live` is never the default and never runs in CI.
    """)
    return


if __name__ == "__main__":
    app.run()
