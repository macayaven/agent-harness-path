import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe import domain
    from cafe.loop import run_shift
    from cafe.model import get_client
    from cafe.report import log_events
    from cafe.taxonomy import (
        agreed,
        classify_naive,
        harvest,
        promote,
        check_task,
        naive_engine,
        guarded_engine,
        rank,
        shift_summary,
    )


@app.cell
def s10_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s10_md_hook(mo):
    mo.md(r"""
    # S10 — Error analysis

    **Carried in:** `cafe/report.py` — S09's honest, citation-checked debrief.

    **Today you ship:** `cafe/taxonomy.py` — a pile of real failures becomes a
    ranked taxonomy, and the top category becomes a permanent eval task.

    ## The hook

    You can now describe one shift honestly. You still cannot say which failures
    *recur*. Until you can, every fix is a guess dressed as a decision.

    ## The promise

    By the end of this session you will harvest failures from several live
    shifts, label them by close reading, rank them by frequency × severity, and
    promote the winner into a task that fails on the engine that produced the
    pile and passes on the fix.
    """)
    return


@app.cell(hide_code=True)
def s10_md_theory(mo):
    mo.md(r"""
    ## The theory in depth

    ### Open coding, then axial coding

    Open coding means read one failure and write what went wrong in your own
    words. Axial coding means group those notes into categories narrow enough to
    be wrong. The order matters: if you invent the taxonomy first, you will find
    only the failures it can name.

    ### Rank, but do not count alone

    A category's weight is frequency × severity. A safety failure that happens
    twice can outrank an annoyance that happens five times. The ranking is a
    reading priority, not a verdict.

    ### Promotion is the payoff

    The top category earns a scripted customer, the tool calls its trace must
    show, and a deterministic check. The task must fail on the old engine and
    pass on the fix; that delta is what makes it worth a slot in the suite.

    ![Open coding, axial grouping, count-by-severity ranking; top categories drive fixes](public/diagrams/S10-error-analysis.svg)
    """)
    return


@app.cell
def s10_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    return (client,)


@app.cell(hide_code=True)
def s10_md_shifts(mo):
    mo.md(r"""
    ## Drive the pile

    These are three live café shifts. Each script declares what the customer
    asked for and which tool the shift must call. The turn cap is deliberately
    tight: a shift that runs out of turns before the customer is answered is a
    real harness failure, not a model-quality score.
    """)
    return


@app.cell
def s10_demo_shifts(client):
    allergy_item = next(
        item for item, details in domain.MENU.items() if "milk" in details["allergens"]
    )
    unavailable_item = domain.EIGHTY_SIXED[0]
    plain_item = next(
        item for item, details in domain.MENU.items() if not details["allergens"]
    )
    second_plain_item = next(
        item
        for item, details in domain.MENU.items()
        if not details["allergens"] and item != plain_item
    )

    shift_scripts = (
        {
            "id": "s10-allergy",
            "user_turns": (
                f"I'm allergic to milk. Can I order a {allergy_item}?",
                "OK.",
                "Nothing else, thanks.",
                "Thanks.",
            ),
            "expects": ("check_allergens",),
        },
        {
            "id": "s10-unavailable",
            "user_turns": (
                f"I'd like a {unavailable_item}, please.",
                "Yes, confirm it.",
                "To go.",
                "Thanks.",
            ),
            "expects": ("price_check", "propose_order"),
        },
        {
            "id": "s10-plain",
            "user_turns": (
                f"A {plain_item} and a {second_plain_item}.",
                "Yes, that's everything.",
                "Perfect.",
                "Thanks.",
            ),
            "expects": ("propose_order",),
        },
    )

    shifts = []
    for script in shift_scripts:
        run = run_shift(client, script["user_turns"], max_turns=3)
        shifts.append({"script": script, "run": run})
        summary = shift_summary(run)
        print(
            script["id"],
            "| stop:", run["stop_reason"],
            "| tools:", ",".join(summary["tool_log"]) or "none",
            "| events:", len(log_events(run)),
        )
    return (shifts,)


@app.cell(hide_code=True)
def s10_md_harvest(mo):
    mo.md(r"""
    ## Harvest only what the trace shows

    `harvest` compares each script with its recorded run. A missing expected tool,
    a ticket fired without a proposal, an 86'd item sent to the kitchen, or a
    turn cap becomes a record with an id, a severity, and a verbatim quote. If
    the trace does not show it, it is not in the pile.
    """)
    return


@app.cell
def s10_demo_harvest(client, shifts):
    pile = harvest(shifts)
    if not pile:
        # A small model can be unexpectedly well behaved. Keep the method alive
        # with one more real, deliberately capped shift; say so, do not hide it.
        fallback_script = {
            "id": "s10-capped",
            "user_turns": ("An espresso, please.", "Ready?"),
            "expects": ("propose_order",),
        }
        fallback_run = run_shift(client, fallback_script["user_turns"], max_turns=1)
        shifts.append({"script": fallback_script, "run": fallback_run})
        pile = harvest(shifts)
        print("The first pass produced no failures; one deliberately capped shift was added.")

    print("harvested failures:", len(pile))
    for record in pile:
        print(
            f"{record['id']:<18} {record['severity']:<7} {record['signal']}"
        )
    return (pile,)


@app.cell(hide_code=True)
def s10_predict_open_code(mo):
    mo.md(r"""
    **Predict first.** Before the next cell, write down the two or three category
    names you expect this pile to contain. Do not run the cell first: the point
    is to keep your guess and compare it with what the traces actually show.
    """)
    return


@app.function
def attempt_open_code(records):
    """Your attempt: one category per failure, read from the records.

    Return `{record_id: category}`. Leave the dictionary empty until you have
    read the pile; the reference solution stays hidden until you flip the switch.
    """
    labels = {}  # Your attempt: labels[record["id"]] = "your-category"
    return labels


@app.cell(hide_code=True)
def s10_reveal_open_code(mo):
    reveal_open_code = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_open_code
    return (reveal_open_code,)


@app.function(hide_code=True)
def solution_open_code(records):
    """One consistent reading of the signals; yours may use different names."""
    labels = {}
    for record in records:
        signal = record["signal"].lower()
        expects = record.get("expects", ())
        if "turn cap" in signal:
            category = "never-answered"
        elif "run out of" in signal:
            category = "unsafe-item-fired"
        elif "check_allergens" in expects:
            category = "unchecked-safety-step"
        elif "propose_order" in expects:
            category = "fired-without-confirmation"
        else:
            category = "other"
        labels[record["id"]] = category
    return labels


@app.cell(hide_code=True)
def s10_reveal_source_open_code(mo, reveal_open_code):
    mo.stop(
        not reveal_open_code.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_open_code) + "```")
    return


@app.cell
def s10_demo_attempt(pile):
    mine = attempt_open_code(pile)
    reference = solution_open_code(pile)
    if not mine:
        print("Attempt pending: implement attempt_open_code before revealing the reference.")
    else:
        print("your labels    :", mine)
        print("reference labels:", reference)
    return mine, reference


@app.cell
def s10_demo_labels(mine, pile, reference):
    expected_ids = {record["id"] for record in pile}
    attempt_is_complete = bool(mine) and set(mine) == expected_ids
    if attempt_is_complete:
        labels = mine
        print("Using your complete labels for the taxonomy.")
    else:
        labels = reference
        print("Attempt pending: using the reference labels so the tour can continue.")
    return (labels,)


@app.cell
def s10_demo_ranking(labels, pile):
    ranked = rank(labels, pile)
    agreement = agreed(labels, pile, classify=classify_naive)
    print(f"agreement with the auto-filer: {agreement}/{len(pile)}")
    print(f"{'category':<28}{'n':<4}{'freq × sev':<12}refs")
    for row in ranked:
        print(
            f"{row['category']:<28}{row['count']:<4}{row['weight']:<12}"
            + ",".join(row["refs"])
        )
    top_category = ranked[0]["category"] if ranked else None
    print("top category:", top_category or "none")
    return (top_category,)


@app.cell(hide_code=True)
def s10_predict_promotion(mo):
    mo.md(r"""
    **Predict first.** The top category is about to become an eval task. Will the
    task fail on `naive_engine`, pass on `guarded_engine`, or fail on both? Write
    your answer before running the promotion cell.
    """)
    return


@app.cell
def s10_demo_promotion(labels, pile, top_category):
    if top_category is None:
        task = None
        print("No category to promote: the pile is empty.")
    else:
        task = promote(top_category, pile, labels)
        print("promoted:", task["id"])
        print("expects :", ", ".join(task["expects"]))
        print("refs    :", ", ".join(task["refs"]))
    return (task,)


@app.cell
def s10_demo_engines(task):
    if task is None:
        naive_shift = guarded_shift = None
        naive_result = guarded_result = None
        print("No promoted task, so no engine comparison.")
    else:
        naive_shift = naive_engine(task)
        guarded_shift = guarded_engine(task)
        naive_result = check_task(task, naive_shift)
        guarded_result = check_task(task, guarded_shift)
        print("naive  :", "PASS" if naive_result[0] else "FAIL", naive_result[1])
        print("guarded:", "PASS" if guarded_result[0] else "FAIL", guarded_result[1])
    return guarded_result, guarded_shift, naive_result, naive_shift


@app.cell
def test_s10_harvest_labels_are_complete(labels, pile):
    """Protocol invariant: every harvested record has exactly one non-empty label."""
    record_ids = {record["id"] for record in pile}
    assert set(labels) == record_ids
    assert len(labels) == len(pile)
    assert all(category for category in labels.values())
    return


@app.cell
def test_s10_promoted_task_discriminates(
    guarded_result,
    guarded_shift,
    naive_result,
    naive_shift,
    task,
):
    """Fixture invariant: the promoted task fails the old engine, passes the fix."""
    assert task is not None
    assert naive_shift is not None and guarded_shift is not None
    assert naive_result == (False, naive_result[1])
    assert guarded_result == (True, guarded_result[1])
    assert check_task(task, naive_engine(task))[0] is False
    assert check_task(task, guarded_engine(task))[0] is True
    return


@app.cell(hide_code=True)
def s10_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Record two things from this run: the agreement count between your hand labels
    and the auto-filer, and the ranked top category. Both are session-relative
    facts about this pile, not universal model-quality scores.

    ## What this unlocks

    You now know which failures recur and have a task that proves the fix. But a
    taxonomy does not tell you what each check should cost. **[S11 — Budgets &
    routing](S11-budgets-routing.html)** turns those categories into spending
    limits and routing choices.
    """)
    return


if __name__ == "__main__":
    app.run()
