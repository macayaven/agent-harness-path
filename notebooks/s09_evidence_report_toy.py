import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect

    from cafe.loop import run_shift
    from cafe.model import get_client
    from cafe.report import (
        capped_shift_trace,
        log_events,
        reassuring_variant,
        render_md,
        validate_citations,
        validate_coverage,
        write_report,
    )


@app.cell
def s09_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s09_md_hook(mo):
    mo.md(r"""
    # S09 — The shift debrief

    **Carried in:** `cafe/trace.py` from S08 — you can record a real shift and
    replay it exactly.

    **Today you ship:** `cafe/report.py` — a debrief a depleted reader can trust.

    ## The hook

    It is 23:40. Someone has to read what happened on this shift and decide
    whether to change something tomorrow. They will give your report **thirty
    seconds**.

    A chronological transcript fails that test. So does a cheerful summary — and
    the cheerful one fails worse, because every sentence in it can be *true* while
    the report as a whole lies by omission.

    ## The promise

    By the end of this session you can generate a debrief whose every claim
    resolves to a real turn, and you will have built the two validators that catch
    the two different ways a report lies: **fabrication** and **omission**.
    """)
    return


@app.cell
def s09_demo_client():
    client = get_client()
    shift_run = run_shift(
        client,
        [
            "Hola, soy alérgico a la leche. ¿El croissant lleva leche?",
            "Entonces ponme un café solo y una tostada con tomate.",
            "Nada más, gracias.",
        ],
    )
    events = log_events(shift_run)
    print("mode        :", client.mode)
    print("stop_reason :", shift_run["stop_reason"])
    print("events      :", len(events))
    return (events, shift_run)


@app.cell(hide_code=True)
def s09_md_theory(mo):
    mo.md(r"""
    ## The theory in depth

    ### Write for the depleted reader

    The reader is tired and accountable. They need six things fast: the goal, the
    outcome, the moments that mattered, anything safety-relevant, what to do next,
    and what it cost. `write_report` produces exactly those slots — not a
    narrative.

    ### A claim without a citation is a rumour

    Every claim carries the turn it came from and a verbatim quote. That makes the
    report *checkable*: `validate_citations` re-reads the trace and confirms each
    quote appears in the turn it cites. An LLM writing the same report will tidy a
    quote into something nicer — and the validator catches it precisely because it
    compares bytes, not vibes.

    ### The two lies are different, and you need both validators

    | lie | shape | caught by |
    |---|---|---|
    | fabrication | a quote that was never said, or a wrong turn | `validate_citations` |
    | omission | every sentence true, safety events quietly absent | `validate_coverage` |

    A report that passes one and fails the other is still dishonest. Honesty is
    the conjunction.
    """)
    return


@app.cell(hide_code=True)
def s09_predict_honest(mo):
    mo.md(r"""
    **Predict first.** The next cell writes the honest report from your live
    trace, then runs both validators over it.

    Before running: will either validator report a violation? If the answer is
    obviously "no", ask yourself what that proves — and what it does not.
    """)
    return


@app.cell
def s09_demo_honest(events, shift_run):
    honest_report = write_report(shift_run, events)
    print(render_md(honest_report)[:700])
    print("\ncitations:", validate_citations(honest_report, shift_run) or "clean")
    print("coverage :", validate_coverage(honest_report, events) or "clean")
    return (honest_report,)


@app.cell
def test_s09_honest_report_passes_both_validators(events, honest_report, shift_run):
    assert validate_citations(honest_report, shift_run) == []
    assert validate_coverage(honest_report, events) == []
    return


@app.cell(hide_code=True)
def s09_md_omission(mo):
    mo.md(r"""
    ## The omission lie

    `reassuring_variant` drops the safety events and keeps everything else. Every
    remaining sentence is still accurate. Watch the citation validator wave it
    through — and the coverage validator refuse.
    """)
    return


@app.cell
def s09_demo_omission(events, honest_report, shift_run):
    reassuring = reassuring_variant(honest_report)
    print("citations:", validate_citations(reassuring, shift_run) or "clean (nothing on the page is false)")
    for violation in validate_coverage(reassuring, events):
        print("  COVERAGE VIOLATION:", violation)
    return (reassuring,)


@app.cell
def test_s09_omission_passes_citations_but_fails_coverage(events, reassuring, shift_run):
    """The two validators are complementary; neither is sufficient alone."""
    citation_violations = validate_citations(reassuring, shift_run)
    coverage_violations = validate_coverage(reassuring, events)
    safety_events = [event for event in events if event["kind"].startswith("safety")]
    if safety_events:
        assert coverage_violations, "dropping a safety event must fail coverage"
        assert len(coverage_violations) >= len(citation_violations)
    return


@app.cell(hide_code=True)
def s09_md_attempt(mo):
    mo.md(r"""
    ## Your turn — the thirty-second test

    Write the check itself: given a rendered report, can a reader answer the six
    questions? Return the list of slots that are missing or empty.

    This is a proxy, not a judge — and knowing the difference is the point.
    """)
    return


@app.function
def attempt_thirty_second_test(report):
    missing = []  # Your attempt: which of the six slots cannot be answered?
    return missing


@app.cell(hide_code=True)
def s09_reveal_thirty_second(mo):
    reveal_thirty_second = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_thirty_second
    return (reveal_thirty_second,)


@app.function(hide_code=True)
def solution_thirty_second_test(report):
    required = ("goal", "outcome", "moments", "safety", "next_step", "cost")
    return [slot for slot in required if not report.get(slot)]


@app.cell(hide_code=True)
def s09_reveal_source_thirty_second(mo, reveal_thirty_second):
    mo.stop(
        not reveal_thirty_second.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_thirty_second_test) + "```")
    return


@app.cell
def s09_demo_compare(honest_report):
    mine = attempt_thirty_second_test(honest_report)
    reference = solution_thirty_second_test(honest_report)
    if not mine and reference:
        print("Attempt pending: implement the check; the reference finds", reference)
    else:
        print("your missing slots     :", mine)
        print("reference missing slots:", reference)
    return


@app.cell(hide_code=True)
def s09_md_failed_run(mo):
    mo.md(r"""
    ## A failed run still gets an honest report

    A shift that hit the turn cap is not an excuse to write nothing. The same
    generator, the same validators — the outcome slot simply says so.
    """)
    return


@app.cell
def s09_demo_failed_run():
    capped = capped_shift_trace()
    capped_events = log_events(capped)
    capped_report = write_report(capped, capped_events)
    print("stop_reason:", capped["stop_reason"])
    print("citations  :", validate_citations(capped_report, capped) or "clean")
    print("coverage   :", validate_coverage(capped_report, capped_events) or "clean")
    return


@app.cell(hide_code=True)
def s09_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Generate a debrief for every scenario in your S02 golden set and record **how
    many pass both validators**. Anything less than all of them is a generator
    bug, not a reporting style choice.

    ## What this unlocks

    You can now describe one shift honestly. You still have no idea which failures
    *recur*. **[S10 — Error analysis](S10-error-analysis.html)** turns a pile of
    real traces into a taxonomy, and the top category into a permanent eval task.
    """)
    return


@app.cell
def s09_demo_checkpoint(client):
    clean = 0
    scripts = (
        ["Ponme un cortado.", "Nada más."],
        ["Soy alérgico a la leche, ¿qué me recomiendas?", "Vale, gracias."],
        ["Una tortilla, por favor.", "Nada más."],
    )
    for script in scripts:
        run = run_shift(client, script)
        run_events = log_events(run)
        report = write_report(run, run_events)
        if not validate_citations(report, run) and not validate_coverage(report, run_events):
            clean += 1
    print(f"S09 baseline: {clean}/{len(scripts)} debriefs pass both validators")
    return


if __name__ == "__main__":
    app.run()
