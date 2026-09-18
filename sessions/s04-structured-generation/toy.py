import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import json
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe import domain
    from cafe.evals import checkers
    from cafe.model import check_pairing, get_client
    from cafe.schema import TICKET_SCHEMA, ask_ticket, parse_json, validate


@app.cell
def s04_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s04_md_hook(mo):
    mo.md(r"""
    # S04 — Structured generation: the ticket contract

    **Carried in:** `cafe/context.py` — the compacted context still governs, and
    the governed arm still scores. Now the *reply* has to cross a boundary: the
    kitchen's ticket system eats JSON and nothing else.

    **Today you ship:** `cafe/schema.py` — the ticket contract, a hand-rolled
    validator, and a bounded validate-and-retry loop.

    ## The hook

    A customer orders. The model answers with a friendly paragraph, a fenced code
    block, and a price nobody ever quoted. Your ticket system accepts none of it.
    You add a schema. The model now returns valid JSON every time — and one of
    those valid tickets asks the kitchen to cook an item it ran out of two hours
    ago, at a total that is wrong by eighty cents.

    ## The promise

    By the end of this session you will have a ticket contract, a validator you
    wrote yourself, and a capped retry loop that turns validation errors into
    messages the model can act on. You will also be able to explain why *valid is
    not correct*, and point at the checker that catches the difference.
    """)
    return


@app.cell(hide_code=True)
def s04_md_client(mo):
    mo.md(r"""
    ## Your model

    Same seam: `get_client()`. A small local model is genuinely bad at this session
    — that is the point, not a bug. You are about to build the machinery that
    catches it.
    """)
    return


@app.cell
def s04_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    return (client,)


@app.cell(hide_code=True)
def s04_md_contract(mo):
    mo.md(r"""
    ## The contract, and the line between shape and meaning

    The schema is the ticket system's data model. The validator is a stdlib subset
    of JSON Schema — `type`, `required`, `properties`, `enum`, `items`, `minItems`
    — because the checks *are* the lesson. A library is these same checks with more
    keywords.

    ![Parse, validate, return specific errors for another bounded attempt; exhausted attempts escalate](public/diagrams/S04-structured-generation.svg)
    """)
    mo.md(r"""
    Two gates, not one. The first is *shape*: is this the object the contract
    describes? The second is *meaning*: does it agree with tonight's menu and
    prices? The second gate is S02's checker, doing exactly what a checker is for.
    """)
    return


@app.cell(hide_code=True)
def s04_predict_validator(mo):
    mo.md(r"""
    **Predict first.** Before running: which of these two tickets does `validate`
    accept, and what exact error does it give the other one?

    1. a ticket missing `total_eur`, with `"table": "four"`;
    2. a ticket whose `items` are two dishes from tonight's menu, priced correctly.
    """)
    return


@app.cell
def s04_demo_validator():
    _items = [sorted(domain.MENU)[0], sorted(domain.MENU)[1]]
    _reference_ticket = {
        "table": 4,
        "items": _items,
        "total_eur": round(sum(domain.MENU[item]["price"] for item in _items), 2),
        "allergen_checked": True,
    }
    _broken_ticket = {"table": "four", "items": [_items[0]]}
    print("reference ticket :", validate(_reference_ticket, TICKET_SCHEMA) or "valid")
    print("broken ticket    :")
    for _problem in validate(_broken_ticket, TICKET_SCHEMA):
        print("  -", _problem)
    print("\nfenced reply parses too:",
          parse_json('Claro:\n```json\n{"table": 1}\n```'))
    return


@app.function
def attempt_semantic(ticket):
    # Your attempt: return one violation per ticket that disagrees with tonight's
    # menu (an 86'd item) or invents a total.
    return None


@app.cell(hide_code=True)
def s04_predict_semantic(mo):
    mo.md(r"""
    **Predict first.** The ticket below is *schema-valid*. Write down how many
    semantic violations it should earn, and name them. Then write
    `attempt_semantic` — it must check the shift data, not the schema.
    """)
    return


@app.cell(hide_code=True)
def s04_reveal_semantic(mo):
    reveal_semantic = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_semantic
    return (reveal_semantic,)


@app.function(hide_code=True)
def solution_semantic(ticket):
    return checkers.ticket_matches_menu(ticket)


@app.cell(hide_code=True)
def s04_reveal_source_semantic(mo, reveal_semantic):
    mo.stop(
        not reveal_semantic.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_semantic) + "```")
    return


@app.cell
def s04_demo_semantic():
    _valid_but_wrong = {
        "table": 4,
        "items": [sorted(domain.EIGHTY_SIXED)[0], "latte"],
        "total_eur": 99.0,
        "allergen_checked": True,
    }
    print("schema says        :", validate(_valid_but_wrong, TICKET_SCHEMA) or "valid")
    mine = attempt_semantic(_valid_but_wrong)
    if mine is None:
        print(
            "Attempt pending: write attempt_semantic, then compare it with the "
            "reference on this ticket."
        )
    else:
        print("your violations    :", mine)
        print("reference          :", solution_semantic(_valid_but_wrong))
    return


@app.cell(hide_code=True)
def s04_md_loop(mo):
    mo.md(r"""
    ## The retry loop, and why it is capped

    Errors become **messages**, exactly as in S01: a `PARSE ERROR` or
    `VALIDATION ERRORS` turn goes back to the model, and the model re-asks. The
    assistant turn is appended verbatim before the feedback, so the protocol stays
    legal across attempts.

    The loop is capped at three attempts. An uncapped retry loop is a
    non-terminating agent with your budget in its hand.

    The next cell runs the real thing against your endpoint. With a small model,
    expect some briefs to fail all three attempts — that is data, not an error.
    """)
    return


@app.cell(hide_code=True)
def s04_predict_retry(mo):
    mo.md(r"""
    **Predict first.** For each brief below, write down: parse error, schema
    invalid, semantically wrong, or accepted — and on which attempt. Then run.
    """)
    return


@app.cell
def s04_demo_live(client):
    briefs = (
        "Table 4: a latte and tomato toast, please.",
        "Table 2 wants two chocolate croissants and an orange juice.",
        "I'm Lucia, table 7. I want a cheese omelette, but I'm not sure it'll sit well.",
    )
    print(f"{'brief':<6} {'outcome':<12} {'attempts':<9} detail")
    for _index, _brief in enumerate(briefs):
        _ticket, _messages, _attempts = ask_ticket(client, _brief)
        if _ticket is None:
            _outcome, _detail = "no ticket", "loop hit the cap"
        elif checkers.ticket_matches_menu(_ticket):
            _outcome, _detail = "semantic", checkers.ticket_matches_menu(_ticket)[0]
        else:
            _outcome, _detail = "accepted", str(_ticket.get("items"))
        print(f"{_index:<6} {_outcome:<12} {_attempts:<9} {_detail[:52]}")
    print("\nRead the failures: a repeated identical error is the contract talking, "
          "\nnot the model.")
    return


@app.cell(hide_code=True)
def s04_md_checks(mo):
    mo.md(r"""
    ## The assertions that survive a bad model

    A live model will not always produce a valid ticket, so none of the cells below
    assert that it does. They assert the machinery: the validator accepts exactly
    what it should, the semantic checker catches what the schema cannot, and the
    retry loop keeps the conversation protocol-legal whatever the model says.
    """)
    return


@app.cell
def test_s04_validator_accepts_reference_and_rejects_enum_miss():
    _item = sorted(domain.MENU)[0]
    _reference_ticket = {
        "table": 1,
        "items": [_item],
        "total_eur": round(domain.MENU[_item]["price"], 2),
        "allergen_checked": False,
    }
    off_menu = {**_reference_ticket, "items": ["pizza"]}
    assert validate(_reference_ticket, TICKET_SCHEMA) == []
    errors = validate(off_menu, TICKET_SCHEMA)
    assert errors and "$.items[0]" in errors[0], errors
    print("validator: reference passes, an off-menu item fails on the enum")
    return


@app.cell
def test_s04_valid_is_not_correct():
    _valid_but_wrong = {
        "table": 4,
        "items": [sorted(domain.EIGHTY_SIXED)[0], "latte"],
        "total_eur": 99.0,
        "allergen_checked": True,
    }
    assert validate(_valid_but_wrong, TICKET_SCHEMA) == []
    problems = checkers.ticket_matches_menu(_valid_but_wrong)
    assert any("86'd" in problem for problem in problems), problems
    assert any("total_eur" in problem for problem in problems), problems
    print("schema-valid, semantically wrong:", problems)
    return


@app.cell
def test_s04_retry_loop_stays_protocol_legal(client):
    _, messages, attempts = ask_ticket(client, "Table 3: an espresso.")
    check_pairing(messages)
    assert 1 <= attempts <= 3, attempts
    assert messages[0]["role"] == "system" and messages[1]["role"] == "user"
    assert len(messages) >= 3, "the model turn must be recorded even when it fails"
    print(f"retry loop: {attempts} attempt(s), {len(messages)} messages, pairing legal")
    return


@app.cell(hide_code=True)
def s04_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Two numbers from the run above: **how many of the three briefs produced a valid
    ticket**, and **how many of those valid tickets were also correct**. The gap
    between the two is the whole session. A small model usually shows the first
    number comfortably above the second.

    ## What this unlocks

    You can now force a shape and tell a valid reply from a correct one. But a
    perfectly valid, perfectly correct ticket is still just a proposal — and
    `fire_ticket` is irreversible. **S05-consent-gate** puts a human confirmation
    between the two, and asks what your harness does when the customer says no.
    """)
    return


if __name__ == "__main__":
    app.run()
