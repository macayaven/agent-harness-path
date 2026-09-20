import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import json
    import sys
    from pathlib import Path

    NOTEBOOK_FILE = Path(__file__).resolve()
    ROOT = NOTEBOOK_FILE.parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe.figures import embed_figures

    from cafe.consent import (
        IRREVERSIBLE_ACTION,
        check_fire,
        consent_gate,
        enrich_ticket,
        fire_requested,
        make_responder,
        render_ticket,
        run_shift,
    )
    from cafe.model import StubClient, get_client
    from cafe.tools import OrderState, fire_ticket


@app.cell
def s05_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s05_md_hook(mo):
    mo.md(r"""
    # S05 — The consent gate

    **Carried in:** `cafe/schema.py` and the ticket contract from S04. A ticket
    you can validate is a ticket you can approve.

    **Today you ship:** `cafe/consent.py` — the gate that stands between the
    model and the one irreversible action in the café.

    ## The hook

    A customer asks for a latte, the model calls `propose_order`, then — without
    waiting for anyone — it calls `fire_ticket`. A ticket is already in the
    kitchen before a human has read a word. `fire_ticket` is irreversible: you
    cannot un-make the coffee.

    S01's loop ran whatever the model asked for. It had no concept of *consent*.

    ## The promise

    By the end of this session you will have watched a rejected plan leave the
    world untouched, an edited plan change what actually executes, and a drifting
    model get stopped *before* dispatch — and you will be able to say which of
    those three is the property that matters.
    """)
    return


@app.cell(hide_code=True)
def s05_md_client(mo):
    mo.md(r"""
    ## Your model

    Same seam as every session: `get_client()` returns the offline stub unless
    `COURSE_MODE=live` points it at **your** endpoint.
    """)
    return


@app.cell
def s05_demo_client(mo):
    with mo.capture_stdout() as _output:
        client = get_client()
        print("mode :", client.mode)
        print("model:", getattr(client, "model", "stub"))
    mo.plain_text(_output.getvalue())
    return (client,)


@app.cell(hide_code=True)
def s05_md_theory(mo):
    mo.md(embed_figures(r"""
    ## The gate: propose → consent → fire

    The ticket is **data** (`{"items": [...], "table": int}`), so every later
    action can be checked against the approved one mechanically. A prose plan
    cannot be checked at all.

    ![Proposed ticket validates, renders for a human, and only fires on approval](public/diagrams/s05-consent.svg)

    Two properties carry the whole design:

    1. **The gate is the check, not the dialog.** The model can say anything; the
       check runs pre-dispatch, on the harness's own copy of the approved ticket.
    2. **Reject is a first-class outcome.** It returns `None`, and nothing
       downstream ever runs. "Nothing happens" is a claim — the tests below test it.
    """, NOTEBOOK_FILE))
    return


@app.cell(hide_code=True)
def s05_predict_gate(mo):
    mo.md(r"""
    **Predict first.** Below, the model proposes `latte + tomato toast`
    for table 4. The scripted customer edits it down to a single `espresso`,
    then approves. Before you run: what does the customer read, and what exactly
    ends up in the approved ticket?
    """)
    return


@app.cell
def s05_demo_gate(mo):
    with mo.capture_stdout() as _output:
        proposal = {"items": ["latte", "tomato toast"], "table": 4}
        print(render_ticket(enrich_ticket(proposal)))
        print()
        gate_approved, gate_log = consent_gate(
            proposal,
            make_responder(
                [("edit", {"items": ["espresso"], "table": 4}), ("approve", None)]
            ),
        )
        for gate_entry in gate_log:
            print(
                " ",
                gate_entry["decision"],
                gate_entry.get("ticket") or gate_entry.get("errors") or "",
            )
        print("approved:", gate_approved)
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s05_md_attempt(mo):
    mo.md(r"""
    ## Your turn — the enforcement point

    Write `attempt_gate`: given an approved ticket and a request to fire, decide
    whether the irreversible action runs. On a violation, **nothing may fire** —
    no ticket, no tool log. Return a record dict with at least `fired` and
    `action`. The starter returns `None` and the compare cell reports
    **Attempt pending**.
    """)
    return


@app.function
def attempt_gate(state, requested, approved):
    # Your attempt. Return a record; touch `state.fired` only when it is legal.
    return None


@app.cell(hide_code=True)
def s05_reveal_gate(mo):
    reveal_gate = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_gate
    return (reveal_gate,)


@app.function(hide_code=True)
def solution_gate(state, requested, approved):
    if approved is None:
        return {"fired": False, "action": "refused", "reason": "not approved"}
    clauses = check_fire(requested, approved)
    if clauses:
        return {"fired": False, "action": "aborted", "clauses": clauses}
    state.tool_log.append(IRREVERSIBLE_ACTION)
    fire_ticket(state, approved["items"], approved["table"])
    return {"fired": True, "action": "fired"}


@app.cell(hide_code=True)
def s05_reveal_source_gate(mo, reveal_gate):
    mo.stop(
        not reveal_gate.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_gate) + "```")
    return


@app.cell
def s05_demo_compare(mo):
    with mo.capture_stdout() as _output:
        compare_state = OrderState()
        compare_approved = {"items": ["espresso"], "table": 2}
        compare_record = attempt_gate(
            compare_state, {"items": ["latte"], "table": 2}, compare_approved
        )
        if compare_record is None:
            print("Attempt pending: return an enforcement record before comparing.")
        else:
            print("record   :", compare_record)
            print("fired    :", compare_state.fired)
            print("tool_log :", compare_state.tool_log)
    mo.plain_text(_output.getvalue())
    return


@app.cell
def test_s05_reject_leaves_zero_side_effects():
    reject_state = OrderState()
    rejected, reject_log = consent_gate(
        {"items": ["latte"], "table": 2}, make_responder([("reject", None)])
    )
    assert rejected is None
    assert reject_log[-1]["decision"] == "reject"
    reject_record = fire_requested(
        reject_state, {"items": ["latte"], "table": 2}, rejected
    )
    assert reject_record["fired"] is False
    assert reject_state.fired == [], "a rejected plan must leave zero tickets"
    assert reject_state.tool_log == [], "a rejected plan must leave no tool log"
    return


@app.cell
def test_s05_edit_rebinds_what_executes():
    edit_state = OrderState()
    edited = {"items": ["espresso"], "table": 2}
    edit_approved, _ = consent_gate(
        {"items": ["latte"], "table": 2},
        make_responder([("edit", edited), ("approve", None)]),
    )
    assert edit_approved["items"] == edited["items"], "the edited ticket is the one that binds"
    assert edit_approved["table"] == edited["table"]
    # The model asks for the ORIGINAL ticket: the edited one binds, nothing fires.
    blocked = fire_requested(
        edit_state, {"items": ["latte"], "table": 2}, edit_approved
    )
    assert blocked["action"] == "aborted" and edit_state.fired == []
    # The model asks for the EDITED ticket: that is what reaches the kitchen.
    fired = fire_requested(edit_state, dict(edited), edit_approved)
    assert fired["action"] == "fired"
    assert edit_state.fired[0]["items"] == ["espresso"]
    return


@app.cell
def test_s05_degrade_fires_exactly_the_approved_ticket():
    degrade_state = OrderState()
    degrade_approved = {"items": ["espresso"], "table": 2}
    degrade_record = fire_requested(
        degrade_state,
        {"items": ["latte", "espresso"], "table": 2},
        degrade_approved,
        on_violation="degrade",
    )
    assert degrade_record["action"] == "degraded" and degrade_record["clauses"]
    assert degrade_state.fired == [degrade_approved], (
        "degrade fires the APPROVED ticket, never the model's request"
    )
    return


@app.cell(hide_code=True)
def s05_md_loop(mo):
    mo.md(r"""
    ## The gate inside the loop

    `run_shift` intercepts `propose_order` to collect consent and stores the
    approved ticket on the run. A later `fire_ticket` is compared against it.
    Here the model is scripted so you can see the whole path once; the customer
    approves.
    """)
    return


@app.cell
def s05_demo_shift(mo):
    with mo.capture_stdout() as _output:
        def stub_tool(call_id, name, arguments):
            return {
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "tool_calls",
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": call_id,
                                    "type": "function",
                                    "function": {"name": name, "arguments": json.dumps(arguments)},
                                }
                            ],
                        },
                    }
                ]
            }

        scripted_script = [
            stub_tool("call_a", "propose_order", {"items": ["latte"], "table": 2}),
            stub_tool("call_b", "fire_ticket", {"items": ["latte"], "table": 2}),
            {
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "Coming right up, table 2."},
                    }
                ]
            },
        ]
        scripted = run_shift(
            StubClient(script=scripted_script),
            ["Get me a latte for table 2."],
            make_responder([("approve", None)]),
        )
        print("stop_reason:", scripted["stop_reason"])
        print("gate       :", [g["decision"] for g in scripted["gate_log"]])
        print("fired      :", scripted["state"].fired)
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s05_md_live(mo):
    mo.md(r"""
    ### Now your model

    Same run, live. A real endpoint usually does not rush to `fire_ticket` — and
    when it never proposes, the gate has nothing to hold. That is not a failure;
    it is the honest shape of the path. Watch what the model actually does.
    """)
    return


@app.cell
def s05_demo_live(client, mo):
    with mo.capture_stdout() as _output:
        live = run_shift(
            client,
            ["Get me a latte for table 2, and a chocolate croissant."],
            make_responder([("approve", None)]),
        )
        print("stop_reason:", live["stop_reason"])
        print("approved   :", live["approved"])
        print("gate       :", [g["decision"] for g in live["gate_log"]])
        print("fired      :", live["state"].fired)
    mo.plain_text(_output.getvalue())
    return


@app.cell(hide_code=True)
def s05_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Rejected three times, live: how many runs fired **nothing**? The claim
    "reject means nothing happens" is only worth what you have tested it against.

    ## What this unlocks

    You can now hold an irreversible action behind a check that runs before
    dispatch. But the gate only sees what it is *given*: a message from an
    untrusted customer still flows straight into the model. **S06-layered-detection**
    puts an ordered pipeline in front of the model — a deterministic keyword floor
    before any model call, an allergen classifier, and a scope governor — with a
    real allergen as the stake.
    """)
    return


@app.cell
def s05_demo_checkpoint(client, mo):
    with mo.capture_stdout() as _output:
        kept = 0
        for _ in range(3):
            run = run_shift(
                client, ["Get me an espresso."], make_responder([("reject", None)])
            )
            refused_everything = all(
                record["action"] == "refused" for record in run["fires"]
            )
            kept += int(refused_everything and run["state"].fired == [])
        print(f"S05 checkpoint: {kept}/3 live runs fired nothing after a rejection")
    mo.plain_text(_output.getvalue())
    return


if __name__ == "__main__":
    app.run()
