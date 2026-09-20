import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import sys
    from pathlib import Path

    NOTEBOOK_FILE = Path(__file__).resolve()
    ROOT = NOTEBOOK_FILE.parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe import context, domain
    from cafe.figures import embed_figures
    from cafe.model import get_client


@app.cell
def s03_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s03_md_hook(mo):
    mo.md(r"""
    # S03 — Context engineering: what survives compaction

    **Carried in:** `cafe/evals/` — its `allergen_safety` checker grades every probe
    in this session, so "the rule still works" means the same thing here as it did
    in the golden set.

    **Today you ship:** `cafe/context.py` — four compaction policies and the
    measurement that tells them apart.

    ## The hook

    The shift runs long. A regular orders, asks about the patio, asks the price
    of three things, then says *I'm allergic to egg, can I have the cheese
    omelette?* Your conversation outgrew the window two turns ago, so your
    compaction policy did its job — the transcript still reads perfectly.

    The allergen rule you wrote on the first line is gone. Nothing announced it.
    The agent answers with confidence, and the checker catches it.

    ## The promise

    By the end of this session you will be able to state, with a number behind it,
    which compaction policies keep the allergen rule governing behaviour across a
    boundary and which bury it — and you will have seen the rule vanish from the
    assembled context, deterministically, before you ever trust a model to notice.
    """)
    return


@app.cell(hide_code=True)
def s03_md_client(mo):
    mo.md(r"""
    ## Your model

    One seam again: `get_client()`. The policies are pure functions over a message
    list; the model only sees whatever they leave behind.
    """)
    return


@app.cell
def s03_demo_client(mo):
    with mo.capture_stdout() as _output:
        client = get_client()
        print("mode :", client.mode)
        print("model:", getattr(client, "model", "stub"))
    mo.plain_text(_output.getvalue())
    return (client,)


@app.cell(hide_code=True)
def s03_md_window(mo):
    mo.md(embed_figures(r"""
    ## A window you have to fit, and a wall you cannot cross

    Two numbers, and they are different kinds of number.

    - `BUDGET` is what the harness *aims* to stay under. It is yours to set.
    - `HARD_LIMIT` is a teaching limit over a word-count proxy. The guard stops
      before dispatch; it is not a measurement of the endpoint's token window.

    Compaction happens when the conversation outgrows the budget. **It rewrites the
    stored history** — what gets dropped is gone from every later turn too, not
    just from this request. That is what makes it dangerous.

    ![Over budget, compact; past the hard limit the call fails instead of degrading](public/diagrams/s03-window.svg)
    """, NOTEBOOK_FILE))
    return


@app.cell(hide_code=True)
def s03_predict_boundary(mo):
    mo.md(r"""
    **Predict first.** Below, one long history goes through all four policies. Write
    down which ones still contain the allergen rule afterwards — and for the ones
    that lose it, say in one sentence what a *transcript reader* would see that a
    *checker* would not.
    """)
    return


@app.cell
def s03_demo_boundary(mo):
    with mo.capture_stdout() as _output:
        _history = [{"role": "system", "content": domain.PERSONA}, context.rule_message()]
        _history += [
            {"role": "user", "content": f"Question {index} about the menu and today's service."}
            for index in range(20)
        ]
        print(f"before compaction: {context.tokens(_history)} words (proxy), "
              f"rule present: {context.rule_is_present(_history)}\n")
        print(f"{'policy':<11} {'compacted':<11} {'words':<8} rule survives")
        for _name, _policy in context.POLICIES.items():
            _new, _compacted = _policy(_history, context.BUDGET_DEFAULT)
            print(f"{_name:<11} {str(_compacted):<11} {context.tokens(_new):<8} "
                  f"{context.rule_is_present(_new)}")
        print("\nRetained text is visible here. Whether it governs requires the behavioral probe.")
    mo.plain_text(_output.getvalue())
    return


@app.cell
def test_s03_buried_rule_dies_pinned_rule_survives(mo):
    with mo.capture_stdout() as _output:
        _history = [{"role": "system", "content": domain.PERSONA}, context.rule_message()]
        _history += [
            {"role": "user", "content": f"Question {index} about the menu and today's service."}
            for index in range(20)
        ]
        _buried, _compacted = context.policy_truncate(_history, context.BUDGET_DEFAULT)
        _kept, _ = context.policy_pinned(_history, context.BUDGET_DEFAULT)
        assert _compacted, "the fixture must be long enough to compact"
        assert not context.rule_is_present(_buried), "the unpinned rule should have died"
        assert context.rule_is_present(_kept), "the pinned rule must survive"
        print(f"buried: {context.tokens(_buried)} words (proxy), rule gone | "
              f"pinned: {context.tokens(_kept)} words (proxy), rule kept")
    mo.plain_text(_output.getvalue())
    return


@app.cell
def test_s03_keep_all_overflows_the_window(client, mo):
    # hard_limit=1 trips the guard before the first model call, so this cell
    # costs nothing no matter which endpoint is behind the seam.
    with mo.capture_stdout() as _output:
        try:
            context.drive(client, context.POLICIES["keep_all"], 1, hard_limit=1)
        except context.ContextWindowExceeded as exc:
            assert "context_length_exceeded" in str(exc)
        else:
            raise AssertionError("keep_all was allowed past the hard limit")
        print("keep_all exceeds the teaching limit before any endpoint call")
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s03_md_attempt(mo):
    mo.md(r"""
    ## Your turn — make the rule survive compaction

    `policy_truncate` drops the oldest unpinned messages and the rule goes with
    them. Implement `attempt_keep_rule`: take a history and a budget, return
    `(new_history, compacted)` — and make sure the rule text is still in the
    result while the history fits the budget.

    Do not rewrite the rule into a summary sentence. "The client asked about the
    menu" is not a constraint, and the checker below will not count it.
    """)
    return


@app.function
def attempt_keep_rule(history, budget):
    # Your attempt: return (new_history, compacted). The rule must survive.
    return None


@app.cell(hide_code=True)
def s03_predict_keep_rule(mo):
    mo.md(r"""
    **Predict first:** what is the cheapest thing you can change that keeps the rule
    across the boundary? Guess the word-count cost it adds to *every* request — then run
    the fixture and check whether the surviving history fits the budget at all.
    """)
    return


@app.cell(hide_code=True)
def s03_reveal_keep_rule(mo):
    reveal_keep_rule = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_keep_rule
    return (reveal_keep_rule,)


@app.function(hide_code=True)
def solution_keep_rule(history, budget):
    return context.policy_pinned(history, budget)


@app.cell(hide_code=True)
def s03_reveal_source_keep_rule(mo, reveal_keep_rule):
    mo.stop(
        not reveal_keep_rule.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_keep_rule) + "```")
    return


@app.cell
def s03_demo_compare(mo):
    with mo.capture_stdout() as _output:
        _history = [{"role": "system", "content": domain.PERSONA}, context.rule_message()]
        _history += [
            {"role": "user", "content": f"Question {index} about the menu and today's service."}
            for index in range(20)
        ]
        mine = attempt_keep_rule(_history, context.BUDGET_DEFAULT)
        if mine is None:
            print(
                "Attempt pending: write attempt_keep_rule, then compare it with the "
                "reference on the same fixture."
            )
        else:
            _new, _compacted = mine
            print("your policy  : compacted", _compacted, "| words (proxy)", context.tokens(_new),
                  "| rule present", context.rule_is_present(_new))
            _ref, _ref_compacted = solution_keep_rule(_history, context.BUDGET_DEFAULT)
            print("reference    : compacted", _ref_compacted, "| words (proxy)", context.tokens(_ref),
                  "| rule present", context.rule_is_present(_ref))
            print("rule rent    :", context.tokens([context.rule_message()]),
                  "tokens on every request, forever")
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s03_md_measure(mo):
    mo.md(r"""
    ## Measure it, do not read it off the transcript

    A checker cares about *behaviour*: the scripted guest interrupts with the
    allergen probe every third turn, and each probe is graded by S02's
    `allergen_safety`. Replay the same script through every policy, against the
    same endpoint, in the same session — the only difference is what survived
    compaction.

    Pinning guarantees retained text, not a better observed rate. Report the
    ordering you measured, including reversals and sample counts. A policy that
    reaches the teaching limit reports its stop. Rates use answered probes;
    capped probes are counted separately, without inventing a safety violation.
    An answered turn reached a final reply; that alone does not prove usefulness.
    """)
    return


@app.cell(hide_code=True)
def s03_predict_survival(mo):
    mo.md(r"""
    **Predict first.** For each policy, write down the probe survival you expect
    *after* the first compaction boundary. Then look at the `truncate` and `pinned`
    rows specifically: if they are not equal, which one should be higher, and what
    would it mean if the live numbers came out the other way?
    """)
    return


@app.cell
def s03_demo_survival(client, mo):
    with mo.capture_stdout() as _output:
        survival = context.survival_table(client)
        print(f"{'policy':<11} {'boundary':<10} {'before':<10} {'after':<10} probes | status")
        for _name, _row in survival.items():
            _before = "—" if _row["before_rate"] is None else f"{_row['before_rate']:.0%}"
            _after = "—" if _row["after_rate"] is None else f"{_row['after_rate']:.0%}"
            print(f"{_name:<11} {str(_row['boundary'] or '—'):<10} {_before:<10} "
                  f"{_after:<10} {_row['probes']}/{_row['attempted_probes']} answered probes; "
                  f"{_row['capped_probes']} capped | {_row['stop_reason']} "
                  f"({_row['completed_turns']} answered / {_row['processed_turns']} processed / "
                  f"{_row['requested_turns']} requested turns; {_row['capped_turns']} capped)")
        print("\nA rate is only a claim if you can say what it was measured on: same "
              "script,\nsame endpoint, same checker, one policy different.")
    mo.plain_text(_output.getvalue())
    return (survival,)


@app.cell
def test_s03_probe_rates_are_observations(mo, survival):
    with mo.capture_stdout() as _output:
        for name, row in survival.items():
            rate = row["overall_rate"]
            assert rate is None or 0 <= rate <= 1, (name, row)
            assert row["probes"] >= 0, (name, row)
        print("Observed rates may reverse; pinning guarantees retained text, not compliance.")
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s03_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Bank **probe survival after the boundary, per policy**: `truncate` vs
    `summarize` vs `pinned`, over answered probes. Bank answered/attempted probe
    counts and capped turns beside the rate; zero answered probes gives no rate.
    Name the rent you paid for the best policy — the pinned rule rides every
    single request.

    ## What this unlocks

    You now choose what the model *sees*, and you can prove which choice holds. But
    a surviving rule is only useful if the reply can be trusted downstream.
    **S04-structured-generation** turns the ticket into a contract: a schema, a
    hand-rolled validator, and a bounded retry loop — plus the uncomfortable
    discovery that a schema-valid ticket can still be wrong.
    """)
    return


if __name__ == "__main__":
    app.run()
