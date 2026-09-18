import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe.evals import GOLDEN, checkers, naive_vs_governed
    from cafe.evals.tasks import empty_record, reference_record
    from cafe.model import get_client
    from cafe.tools import OrderState


@app.cell
def s02_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s02_md_hook(mo):
    mo.md(r"""
    # S02 — Golden evals: naive vs governed

    **Carried in:** `cafe/loop.py` — and the S01 number you banked, a handful of
    anecdotes repeated three times.

    **Today you ship:** `cafe/evals/` — a golden set, a deterministic checker whose
    failures you trust, and the naive baseline the harness has to beat.

    ## The hook

    Yesterday you replayed one café conversation three times and called the result
    a number. It is not one. A different customer, a declared allergy, a price that
    was never on the menu: any of those can turn a *looks fine to me* run into a
    written complaint. You cannot defend 3/3 anecdotes to your own barista, let
    alone to anyone who signs off on the shift.

    ## The promise

    By the end of this session you have a golden set of scripted café scenarios, a
    checker that an empty run fails and a hand-built reference run passes, and two
    pass rates measured on the same endpoint in the same session. The difference
    between those two numbers is the only claim you make — and it is attributable,
    because the script, the model and the checker are shared.
    """)
    return


@app.cell(hide_code=True)
def s02_md_client(mo):
    mo.md(r"""
    ## Your model

    Still one seam: `get_client()`. Both arms talk to the same endpoint, so neither
    gets to blame its model for the delta.
    """)
    return


@app.cell
def s02_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    return (client,)


@app.cell(hide_code=True)
def s02_md_golden(mo):
    mo.md(r"""
    ## What a golden set is, and what it is not

    A golden set is a fixed script of customer turns plus what the shift was asked
    to do. The script removes *user-side* variation — not model variation. That is
    the whole point: the conversation is reproducible, the model is not.

    Each scenario carries three facts the checker can use:

    | field | meaning |
    | --- | --- |
    | `turns` | the customer's lines, replayed verbatim |
    | `allergen` | a declared allergy, or `None` |
    | `confirm_text` | the line that authorises firing, or `None` |
    | `expect_tools` | the tools the task cannot be done without |

    ![Same scripted user feeds naive and governed engines; both transcripts meet the same deterministic checks](public/diagrams/S02-golden-evals.svg)
    """)
    return


@app.cell
def s02_demo_golden():
    print(f"{'id':<20} {'turns':<6} {'allergen':<10} {'confirm':<8} tools")
    for _scenario in GOLDEN:
        print(
            f"{_scenario.id:<20} {len(_scenario.turns):<6} "
            f"{_scenario.allergen or '-':<10} "
            f"{'yes' if _scenario.confirm_text else '-':<8} "
            f"{', '.join(_scenario.expect_tools) or '-'}"
        )
    print(f"\n{len(GOLDEN)} scenarios. Read every one before you score anything.")
    return


@app.cell(hide_code=True)
def s02_predict_arms(mo):
    mo.md(r"""
    **Predict first.** Write down, before running: which arm fails `p02-egg-allergy`,
    and why can it *never* pass it? Then estimate both rates out of four. A live
    model will not match your estimate exactly — the gap between prediction and
    result is the lesson, and the direction of the gap is the product argument.
    """)
    return


@app.cell
def s02_demo_arms(client):
    comparison = naive_vs_governed(client)
    print(f"{'arm':<10} {'pass rate':<12} failing scenarios")
    for _arm in ("naive", "governed"):
        _row = comparison[_arm]
        _failed = [d["id"] for d in _row["details"] if not d["ok"]]
        print(f"{_arm:<10} {_row['passes']}/{_row['total']:<10} {', '.join(_failed) or '-'}")
    print("\nSame scripts, same endpoint, same checker. Only the harness differs.")
    return (comparison,)


@app.cell(hide_code=True)
def s02_md_attempt(mo):
    mo.md(r"""
    ## Your turn — write one checker

    The deterministic tier is only worth trusting if you can write in it. Implement
    `attempt_premature_fire`: return one violation string for every `fire_ticket`
    call that had no proposal before it or no customer confirmation before it.

    Two fixtures are waiting below: one run that fires a ticket nobody confirmed,
    and one clean reference run. The starter reports **Attempt pending**, not pass.
    """)
    return


@app.function
def attempt_premature_fire(scenario, record):
    # Your attempt: walk record["messages"] and collect the unconfirmed fires.
    return None


@app.cell(hide_code=True)
def s02_predict_premature_fire(mo):
    mo.md(r"""
    **Predict first:** on the dirty fixture, how many violations should your checker
    return — one for the missing proposal, one for the missing confirmation, or
    both? On the clean fixture it must return an empty list. Write your answer down.
    """)
    return


@app.cell(hide_code=True)
def s02_reveal_premature_fire(mo):
    reveal_premature_fire = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_premature_fire
    return (reveal_premature_fire,)


@app.function(hide_code=True)
def solution_premature_fire(scenario, record):
    return checkers.ticket_only_after_confirmation(scenario, record)


@app.cell(hide_code=True)
def s02_reveal_source_premature_fire(mo, reveal_premature_fire):
    mo.stop(
        not reveal_premature_fire.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_premature_fire) + "```")
    return


@app.cell
def s02_demo_compare():
    scenario = GOLDEN[2]
    dirty = {
        "messages": [
            {"role": "user", "content": scenario.turns[-1]},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "fire_ticket",
                            "arguments": '{"items": ["latte"], "table": 1}',
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_1", "content": "{}"},
        ],
        "state": OrderState(),
        "stop_reason": "answered",
    }
    clean = reference_record(scenario)
    mine = attempt_premature_fire(scenario, dirty)
    if mine is None:
        print(
            "Attempt pending: write attempt_premature_fire, then compare it with "
            "the reference on both fixtures."
        )
    else:
        print("your violations, dirty run :", mine)
        print("dirty run vs reference    :", solution_premature_fire(scenario, dirty))
        print("clean run vs reference    :", solution_premature_fire(scenario, clean))
    return


@app.cell(hide_code=True)
def s02_md_checks(mo):
    mo.md(r"""
    ## The checker gets checked

    A checker that cannot fail asserts nothing. Every deterministic checker earns
    its keep with one fixture invariant: **an empty run must FAIL, a hand-built
    reference run must PASS.** If either half breaks, the number you are about to
    bank is measuring noise.

    The assertions below are the honest kind — mechanical facts about the checker
    and one *relative* comparison between the arms. With a live model we never
    assert an absolute score; a bad day must not turn truth into a red cell.
    """)
    return


@app.cell
def test_s02_checker_rejects_empty_and_accepts_reference():
    for _scenario in GOLDEN:
        assert checkers.evaluate(_scenario, empty_record()), _scenario.id
        assert checkers.evaluate(_scenario, reference_record(_scenario)) == [], _scenario.id
    print("fixture invariant holds: empty runs fail, reference runs pass")
    return


@app.cell
def test_s02_arms_share_one_golden_set(comparison):
    assert comparison["scenarios"] == tuple(scenario.id for scenario in GOLDEN)
    for _arm in ("naive", "governed"):
        assert comparison[_arm]["total"] == len(GOLDEN)
    print("both arms scored the same", len(GOLDEN), "scenarios, in the same order")
    return


@app.cell
def test_s02_governed_never_scores_below_naive(comparison):
    naive = comparison["naive"]
    governed = comparison["governed"]
    assert governed["passes"] >= naive["passes"], comparison
    print(f"naive {naive['passes']}/{naive['total']} vs governed "
          f"{governed['passes']}/{governed['total']} — the harness never does worse")
    return


@app.cell(hide_code=True)
def s02_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Two numbers, one session, one endpoint: **naive n/4 and governed n/4**. Bank
    the pair, not the governed one alone — a pass rate is only meaningful against
    the status quo it replaced. This is the number S03 must not lose while it
    compacts the context.

    ## What this unlocks

    You can now say *how often* the shift behaves, which is the only way to say
    whether a change helped. **S03-context-engineering** takes the governed arm
    into a long shift and asks the harder question: when the conversation grows
    past the window, which of your rules survives compaction — and how would you
    prove it?
    """)
    return


if __name__ == "__main__":
    app.run()
