import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import datetime
    import inspect
    import json
    import os
    import random
    import sys
    import tempfile
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe.consent import make_responder
    from cafe.model import get_client
    from cafe.trace import (
        ReplayMismatch,
        TickClock,
        Tracer,
        export_fail_soft,
        load_records,
        record_shift,
        replay_shift,
        transcript,
        usage_of,
    )

    # A synthetic customer approves the first valid proposal; exhaustion rejects.
    SCRIPT = (
        "Hi, get me a latte and a chocolate croissant.",
        "Nothing else, thanks.",
    )

    FLOURISH = (
        "Coming right up.",
        "Carefully does it.",
        "Ready.",
        "Right away.",
        "On its way.",
    )


@app.cell
def s08_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s08_md_hook(mo):
    mo.md(r"""
    # S08 — Observability & replay

    **Carried in:** `cafe/repair.py` — S07's bounded re-ask, the last piece of the
    loop that only ever ran in your terminal.

    **Today you ship:** `cafe/trace.py` — spans, a JSONL record of a real shift,
    and a replay that is content-identical to the run that produced it.

    ## The hook

    A customer calls back. *"You charged me twice yesterday."* You open a terminal and
    scroll: the shift printed a perfectly nice transcript, and it is gone. You
    cannot show what the model actually saw, you cannot re-run the shift, and you
    cannot prove which turn produced the second ticket. The debrief is your memory
    against theirs, and memory loses.

    ## The promise

    By the end of this session you will have recorded **your own live shift** to a
    JSONL trace, replayed it with **zero model calls**, and printed a transcript
    that is content-identical to the live run. Then you will do the part that
    separates a recording from a replay: prove determinism by injecting the two
    things that quietly break it — the wall clock and the RNG.
    """)
    return


@app.cell(hide_code=True)
def s08_md_client(mo):
    mo.md(r"""
    ## Your model, one seam

    `get_client()` is the only way this course reaches a model: the offline stub
    by default, live against your endpoint under `COURSE_MODE=live`. The recording
    wrappers below take whatever that seam returns and wrap it — they never
    construct a client of their own.
    """)
    return


@app.cell
def s08_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    return (client,)


@app.cell(hide_code=True)
def s08_md_record(mo):
    mo.md(r"""
    ## A recording is a contract, not a printout

    `RecordingClient` wraps any client and appends one JSONL line per call:
    `{"request": ..., "response": ...}`, in order. `ReplayClient` serves those
    responses back and refuses to guess:

    ![Recording relays to the model and appends trace lines; replay serves them back and raises on mismatch](public/diagrams/s08-replay.svg)
    """)
    mo.md(r"""
    Two invariants, and they catch two different regressions. **Matching** polices
    the calls that *arrive*: a changed request raises instead of receiving a
    response recorded for something else. **Exhaustion** polices the calls that
    *should have arrived*: a regression that deletes the last model call sends
    nothing bad to match, so only `assert_exhausted()` sees it.

    Everything below writes inside a `tempfile.TemporaryDirectory()`. Nothing —
    not one `.jsonl` — lands under the repo root.
    """)
    return


@app.cell
def s08_demo_record(client):
    workdir = tempfile.TemporaryDirectory()
    trace_path = Path(workdir.name) / "shift.jsonl"
    repo_root = Path(__file__).resolve().parents[1]
    repo_before = repo_files(repo_root)
    recording = record_shift(client, SCRIPT, trace_path, responder=make_responder([("approve", None)]), tracer=Tracer(clock=TickClock()))
    repo_after = repo_files(repo_root)
    run = recording["run"]
    print("trace    :", trace_path)
    print("calls    :", run["model_calls"], "| stop:", run["stop_reason"])
    print("tools run:", run["state"].tool_log)
    print("usage    :", usage_of(recording["tracer"]))
    print()
    print(recording["tracer"].render())
    return recording, repo_after, repo_before, repo_root, trace_path


@app.function
def repo_files(root):
    """Every file under the repo root, minus caches: a no-side-effects baseline."""
    ignore = {".git", "__pycache__", ".venv", "node_modules"}
    found = set()
    for base, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in ignore]
        found.update(str(Path(base) / name) for name in names)
    return found


@app.cell(hide_code=True)
def s08_predict_replay(mo):
    mo.md(r"""
    **Predict first.** Before running the next cell, write down: how many times
    will the live model fire during the replay? Will the replayed transcript be
    content-identical to the recorded one — and if not, what could possibly
    differ, given that the responses are frozen on disk?
    """)
    return


@app.cell
def s08_demo_replay(client, recording, trace_path):
    live_calls_before = client.calls
    first = replay_shift(trace_path, SCRIPT, responder=make_responder([("approve", None)]), tracer=Tracer(clock=TickClock()))
    second = replay_shift(trace_path, SCRIPT, responder=make_responder([("approve", None)]), tracer=Tracer(clock=TickClock()))
    live_calls_after = client.calls
    print("recording       :", len(load_records(trace_path)), "JSONL lines")
    print("replay 1        : stop", first["run"]["stop_reason"], "| calls",
          first["run"]["model_calls"])
    print("live == replay 1:", transcript(recording["run"]) == transcript(first["run"]))
    print("replay 1 == 2   :", transcript(first["run"]) == transcript(second["run"]))
    print("live model calls during the replays:", live_calls_after - live_calls_before)
    print()
    print(first["tracer"].render())
    return first, live_calls_after, live_calls_before, second


@app.cell
def test_s08_replay_is_content_identical_and_makes_no_model_calls(
    first,
    live_calls_after,
    live_calls_before,
    recording,
    trace_path,
):
    assert transcript(recording["run"]) == transcript(first["run"]), "replay diverged"
    assert recording["run"]["stop_reason"] == first["run"]["stop_reason"]
    assert recording["run"]["turns_used"] == first["run"]["turns_used"]
    assert live_calls_after == live_calls_before, "replay touched the live model"
    assert first["player"]._next == len(load_records(trace_path)), "recording not consumed"
    return


@app.cell
def test_s08_stale_recording_is_refused(trace_path):
    stale = SCRIPT[1:]  # the customer's first line changed; the recording is stale
    try:
        replay_shift(trace_path, stale, responder=make_responder([("approve", None)]))
    except ReplayMismatch:
        pass
    else:
        raise AssertionError("a stale replay was accepted")
    return


@app.cell
def test_s08_no_writes_outside_the_tempdir(
    repo_after,
    repo_before,
    repo_root,
    trace_path,
):
    stray = sorted(repo_after - repo_before)
    assert not stray, f"the recording wrote inside the repo: {stray[:5]}"
    assert str(trace_path).startswith(tempfile.gettempdir()), trace_path
    assert not (repo_root / "shift.jsonl").exists()
    return


@app.cell(hide_code=True)
def s08_md_fail_soft(mo):
    mo.md(r"""
    ## The exporter is down

    A tracing backend is a network call you do not own. It fails. The one thing
    that must never fail with it is the shift.

    `Tracer.export()` raises when the exporter raises — deliberately, so nobody can
    pretend telemetry errors are invisible. `export_fail_soft` is the boundary
    where you decide what a dead exporter costs you: the traces, or the shift.
    """)
    return


@app.function
def dead_exporter(payload):
    raise ConnectionError("tracing backend unreachable (simulated)")


@app.cell
def s08_demo_fail_soft(trace_path):
    doomed = replay_shift(trace_path, SCRIPT, responder=make_responder([("approve", None)]), tracer=Tracer(exporter=dead_exporter))
    problem = export_fail_soft(doomed["tracer"])
    print("the shift still ran to:", doomed["run"]["stop_reason"])
    print("export_fail_soft returned:", problem)
    print("telemetry degrades; the shift does not.")
    return


@app.cell(hide_code=True)
def s08_md_hunt(mo):
    mo.md(r"""
    ## The hunt — two replays of one recording disagree

    A teammate ships a "harmless" PR: a timestamped header, a livelier closing
    line. Now two replays of the **same recording** differ. The recorded responses
    are frozen JSON, so replay cannot add variance. The nondeterminism is in the
    host, and the diff names the two suspects: a wall clock read and an unseeded
    RNG draw.

    Determinism is not a property you hope for; it is a property you *wire in*.
    Pass the clock and the RNG as parameters, and create a **fresh seeded
    instance per run** — one shared `Random(7)` reproduces across processes but
    drifts between two runs inside one process.
    """)
    return


@app.function
def time_stamped_note(run):
    """The teammate's PR: a dated header and a livelier closing line.

    Both reads are defects in a replay: the wall clock is not an input, and the
    process-wide RNG is not an input either.
    """
    return [
        f"FICHA DEL TURNO - {datetime.datetime.now().isoformat()}",
        f"cerrado: {run['stop_reason']} | turnos: {run['turns_used']}",
        f"tickets: {len(run['state'].fired)}",
        random.choice(FLOURISH),
    ]


@app.cell(hide_code=True)
def s08_predict_handover_note(mo):
    mo.md(r"""
    **Predict first.** Write the handover note the owner would actually read: the
    timestamp, what the shift did, how many tickets went to the kitchen, and a
    closing line. Then mark, before running anything, which of those four lines
    can change between two replays of one recording — and how you would make it
    not change without deleting it.

    The starter reports **Attempt pending**, not success.
    """)
    return


@app.function
def attempt_handover_note(run, *, clock, rng):
    lines = []  # Your attempt: every changing value must come from clock or rng.
    return lines


@app.cell(hide_code=True)
def s08_reveal_handover_note(mo):
    reveal_handover_note = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_handover_note
    return (reveal_handover_note,)


@app.function(hide_code=True)
def solution_handover_note(run, *, clock, rng):
    return [
        f"FICHA DEL TURNO - {clock()}",
        f"cerrado: {run['stop_reason']} | turnos: {run['turns_used']}",
        f"tickets: {len(run['state'].fired)}",
        rng.choice(FLOURISH),
    ]


@app.cell(hide_code=True)
def s08_reveal_source_handover_note(mo, reveal_handover_note):
    mo.stop(
        not reveal_handover_note.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_handover_note) + "```")
    return


@app.cell
def s08_demo_handover_note(first, second):
    injected_clock = lambda: "2026-09-17T21:00:00Z"  # noqa: E731 - a fixture literal
    attempt = attempt_handover_note(
        first["run"], clock=injected_clock, rng=random.Random(7)
    )
    reference = solution_handover_note(
        first["run"], clock=injected_clock, rng=random.Random(7)
    )
    print("teammate's version, lines 1 and 4, two replays of one recording:")
    print("  ", time_stamped_note(first["run"])[0])
    print("  ", time_stamped_note(second["run"])[0])
    print("  ", time_stamped_note(first["run"])[3], "|", time_stamped_note(second["run"])[3])
    if not attempt:
        print("Attempt pending: fill in the note before comparing the reference.")
    else:
        print("your note matches the reference:", attempt == reference)
    return


@app.cell
def test_s08_injected_dependencies_are_reproducible(first, second):
    injected = lambda: "2026-09-17T21:00:00Z"  # noqa: E731 - a fixture literal
    left = solution_handover_note(first["run"], clock=injected, rng=random.Random(7))
    right = solution_handover_note(second["run"], clock=injected, rng=random.Random(7))
    assert left == right, "an injected clock and RNG must be reproducible"
    # The wall clock cannot equal an injected literal, so this difference is exact.
    assert left[0] != time_stamped_note(first["run"])[0]
    return


@app.cell(hide_code=True)
def s08_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the numbers you bank

    Two numbers, and both are exact, not statistical:

    - **model calls during replay: 0.** The replay you just ran is offline by
      construction, not by policy.
    - **transcript sha-free equality: live == replay.** Content-identical, turn
      for turn, because the responses were frozen on disk and everything else —
      clock, RNG, system prompt, tool schemas — is now an input.

    That is the S08 contract, and S09 spends it: a debrief that cites turns of a
    trace you can hand someone else and they can replay.

    ## What this unlocks

    You have a trace and a replay. What you do not have is anything a busy owner
    would read. **S09-evidence-reports** turns this JSONL into a shift debrief with
    turn citations, and builds the two validators that catch the two lies a report
    tells: the tidy paraphrase presented as a quote, and the omission that leaves
    no false sentence behind.
    """)
    return


if __name__ == "__main__":
    app.run()
