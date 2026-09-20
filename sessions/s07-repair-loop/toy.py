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

    from cafe.model import get_client
    from cafe.repair import (
        CAP_DEFAULT,
        STOP_REASONS,
        brief_for,
        make_model_generator,
        make_scripted_generator,
        repair_ticket,
        score_ticket,
    )


@app.cell
def s07_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s07_md_hook(mo):
    mo.md(r"""
    # S07 — The repair loop

    **Carried in:** `cafe/detect.py` from S06 — you can now spot an unsafe or
    off-menu ticket before it reaches the pass.

    **Today you ship:** `cafe/repair.py` — bounded regeneration when the model
    gets it wrong.

    ## The hook

    S06 taught you to *reject* a bad ticket. So your shift now refuses a lot and
    serves nothing. Detection without repair is just a more articulate failure.

    The obvious fix — "ask again" — is where people quietly ship an infinite loop,
    or a loop that retries forever on a contradiction it can never satisfy.

    ## The promise

    By the end of this session your agent re-asks with a **curated view of what
    failed**, stops at a cap you chose, and never ends in a state you cannot name.
    You will also watch a contradiction burn all three attempts and stop honestly.
    """)
    return


@app.cell
def s07_demo_client(mo):
    with mo.capture_stdout() as _output:
        client = get_client()
        print("mode :", client.mode)
        print("cap  :", CAP_DEFAULT, "| stop reasons:", sorted(STOP_REASONS))
    mo.plain_text(_output.getvalue())
    return (client,)


@app.cell(hide_code=True)
def s07_md_theory(mo):
    mo.md(r"""
    ## The theory in depth

    ### A retry is not a resample

    Resampling asks the same question again and hopes the dice land better. A
    **repair** changes the input: it tells the model what was wrong with the last
    attempt. That difference is why `retry_messages` appends a *failure view*
    rather than simply re-sending the brief.

    ### What the retry is allowed to see

    Three modes, and the choice matters:

    | mode | the retry sees | risk |
    |---|---|---|
    | `naive` | nothing; just ask again | burns attempts on the same mistake |
    | `curated` | only the current failures | the default: focused, cheap |
    | `full_history` | every prior attempt and error | context grows; old errors distract |

    ### The cap converts a contradiction into an honest stop

    Some specs cannot be satisfied — ask for a dish with no allergens when every
    variant contains milk. Without a cap the loop spins. With one, the run ends
    `retries_exhausted` and the attempt log becomes the diagnosis a human reads.

    Every run ends with a `stop_reason` in `STOP_REASONS`, and a draft exists if
    and only if the reason is `passed`. That biconditional is the contract.

    ![Score deterministically: accept, retry with a failure view, or withhold](public/diagrams/S07-repair-loop.svg)
    """)
    return


@app.cell(hide_code=True)
def s07_predict_contradiction(mo):
    mo.md(r"""
    **Predict first.** The next cell uses a *scripted* generator (no model) that
    keeps alternating between two mistakes: it drops a required item, then adds a
    banned one, then drops the item again.

    Before running: which `stop_reason` comes back, how many attempts appear in
    the log, and is there a draft at the end? Write it down.
    """)
    return


@app.cell
def s07_demo_contradiction(mo):
    with mo.capture_stdout() as _output:
        contradiction_spec = {
            "table": 4,
            "items": ["latte", "chocolate croissant"],
            "avoid_allergens": ["milk"],
        }
        ping_pong = make_scripted_generator(
            [
                {"table": 4, "items": ["latte"]},
                {"table": 4, "items": ["latte", "chocolate croissant", "iced latte"]},
                {"table": 4, "items": ["latte"]},
            ]
        )
        contradiction_run = repair_ticket(contradiction_spec, ping_pong, cap=CAP_DEFAULT)
        print("stop_reason:", contradiction_run["stop_reason"])
        print("attempts   :", len(contradiction_run["attempts"]))
        print("ticket     :", contradiction_run["ticket"])
        for attempt in contradiction_run["attempts"]:
            print(f"  attempt {attempt['n']}: {attempt['failures']}")
    mo.plain_text(_output.getvalue())
    return (contradiction_run,)


@app.cell
def test_s07_every_run_ends_with_a_named_reason(contradiction_run):
    assert contradiction_run["stop_reason"] in STOP_REASONS, contradiction_run["stop_reason"]
    assert (contradiction_run["ticket"] is None) == (
        contradiction_run["stop_reason"] != "passed"
    ), "a ticket must exist if and only if the run passed"
    assert len(contradiction_run["attempts"]) <= CAP_DEFAULT
    return


@app.cell(hide_code=True)
def s07_md_attempt(mo):
    mo.md(r"""
    ## Your turn — the failure view

    The retry is only as good as what it tells the model. Write the curated view:
    given the failures of the last attempt, produce the short text the model sees.

    Keep it specific and keep it short. "Invalid ticket" teaches nothing; naming
    the missing item and the banned allergen teaches everything.
    """)
    return


@app.function
def attempt_failure_view(failures, attempt):
    lines = []  # Your attempt: one short, specific line per failure.
    return "\n".join(lines)


@app.cell(hide_code=True)
def s07_reveal_failure_view(mo):
    reveal_failure_view = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_failure_view
    return (reveal_failure_view,)


@app.function(hide_code=True)
def solution_failure_view(failures, attempt):
    lines = [f"Attempt {attempt} was rejected. Fix exactly these problems:"]
    for failure in failures:
        lines.append(f"- {failure}")
    lines.append("Return the corrected ticket as JSON only.")
    return "\n".join(lines)


@app.cell(hide_code=True)
def s07_reveal_source_failure_view(mo, reveal_failure_view):
    mo.stop(
        not reveal_failure_view.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_failure_view) + "```")
    return


@app.cell
def s07_demo_compare(mo):
    with mo.capture_stdout() as _output:
        sample_failures = ["missing required item: chocolate croissant", "contains banned allergen: milk"]
        mine = attempt_failure_view(sample_failures, 2)
        if not mine.strip():
            print("Attempt pending: write the curated view before comparing the reference.")
        else:
            print("your view:\n" + mine)
            print("\nnames every failure:", all(f.split(":")[0] in mine for f in sample_failures))
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s07_predict_live(mo):
    mo.md(r"""
    ## Against your model

    Now the real thing. The generator below is your endpoint. A small model often
    fails the contract on attempt 1 and recovers on attempt 2 — which is exactly
    the behaviour the repair loop exists to exploit.

    **Predict first:** how many attempts will your model need? Will it ever be
    `retries_exhausted`?
    """)
    return


@app.cell
def s07_demo_live(client, mo):
    with mo.capture_stdout() as _output:
        live_spec = {"table": 7, "items": ["latte", "tomato toast"], "avoid_allergens": []}
        live_run = repair_ticket(live_spec, make_model_generator(client), cap=CAP_DEFAULT)
        print("brief      :", brief_for(live_spec)[:88])
        print("stop_reason:", live_run["stop_reason"])
        print("attempts   :", len(live_run["attempts"]))
        print("ticket     :", live_run["ticket"])
    mo.plain_text(_output.getvalue())
    return live_run, live_spec


@app.cell
def test_s07_repair_never_exceeds_its_cap_on_a_live_model(live_run, live_spec):
    assert live_run["stop_reason"] in STOP_REASONS
    assert len(live_run["attempts"]) <= CAP_DEFAULT, "the cap is a harness promise"
    if live_run["stop_reason"] == "passed":
        assert score_ticket(live_run["ticket"], live_spec)["passed"], (
            "a passing run must produce a ticket that actually scores clean"
        )
    return


@app.cell(hide_code=True)
def s07_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Run the live repair over the S02 golden set and record **attempts-to-pass**:
    how many of your scenarios passed on attempt 1, on 2, on 3, and how many
    exhausted. That distribution is your S07 baseline.

    It is also a budget signal: if most scenarios need three attempts, you are
    paying triple for every order, and S11 will make you confront that.

    ## What this unlocks

    Your agent can now recover. It still cannot tell you *what happened* — the
    attempt log lives and dies inside one run. **S08 — Observability &
    replay** gives the shift a memory: spans, a
    recorded trace of your own live session, and a replay you can prove is
    identical.
    """)
    return


@app.cell
def s07_demo_checkpoint(client, mo):
    with mo.capture_stdout() as _output:
        distribution = {"passed_on_1": 0, "passed_on_2": 0, "passed_on_3": 0, "exhausted": 0}
        for table, items in ((4, ["latte"]), (5, ["croissant"]), (6, ["orange juice"])):
            run = repair_ticket(
                {"table": table, "items": items, "avoid_allergens": []},
                make_model_generator(client),
                cap=CAP_DEFAULT,
            )
            if run["stop_reason"] == "passed":
                distribution[f"passed_on_{min(len(run['attempts']), 3)}"] += 1
            else:
                distribution["exhausted"] += 1
        print("S07 baseline — attempts to pass:", distribution)
    mo.plain_text(_output.getvalue())
    return


if __name__ == "__main__":
    app.run()
