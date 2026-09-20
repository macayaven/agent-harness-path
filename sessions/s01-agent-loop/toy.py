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
    from cafe.loop import run_shift
    from cafe.model import OrphanedToolResult, StubClient, check_pairing, get_client
    from cafe.tools import OrderState, dispatch


@app.cell
def s01_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s01_md_hook(mo):
    mo.md(r"""
    # S01 — The order-taking loop

    **Carried in:** nothing yet. This is where the café opens.

    **Today you ship:** `cafe/loop.py` — the loop every later session extends.

    ## The hook

    A customer says *"get me a latte and a chocolate croissant"*. Your model replies with
    a tool call. You run the tool. You send the result back — and the endpoint
    rejects the whole conversation with a `400`.

    Nothing about the model caused that. You broke a bookkeeping rule that is
    invisible until the moment it isn't.

    ## The promise

    By the end of this session you can state, from memory, the two invariants that
    keep a tool-calling conversation legal, and you will have watched the local
    client reject an orphaned result before sending a request.
    """)
    return


@app.cell(hide_code=True)
def s01_md_client(mo):
    mo.md(r"""
    ## Your model

    `get_client()` is the only seam between this course and a model. It returns
    the offline stub unless `COURSE_MODE=live` points it at **your** endpoint.

    Run the cell: `mode: stub` means offline and deterministic. To run against
    a real model, set `COURSE_MODE=live` plus the three `CAFE_*` variables —
    and `uv run python -m cafe.doctor` proves the endpoint before you continue.
    """)
    return


@app.cell
def s01_demo_client(mo):
    with mo.redirect_stdout():
        client = get_client()
        print("mode :", client.mode)
        print("model:", getattr(client, "model", "stub"))
    return (client,)


@app.cell(hide_code=True)
def s01_md_api_shape(mo):
    mo.md(r"""
    ## The API is stateless; the loop is the agent

    One request in, one response out. Every request carries the **entire**
    `messages` list — the endpoint remembers nothing. Two response shapes matter:
    a final answer (`content`, no `tool_calls`), or a request to run a tool.

    ![Client-owned loop: answers end the loop, tool calls execute locally and persist before the next call](public/diagrams/S01-agent-loop.svg)

    The arrow back to the model carries **history**, not an invocation of the tool
    inside the model. Trace that with your finger before reading the code.
    """)
    return


@app.cell(hide_code=True)
def s01_predict_first_call(mo):
    mo.md(r"""
    **Predict first.** You are about to send one customer line and the five café
    tool schemas to a real model. Before running: does it call a tool, or answer
    in words? Which tool? Write your prediction down — with a live model you will
    sometimes be wrong, and that gap is the lesson.
    """)
    return


@app.cell
def s01_demo_first_call(client, mo):
    with mo.redirect_stdout():
        first = client.chat(
            [
                {"role": "system", "content": domain.PERSONA},
                {"role": "user", "content": "Get me a latte, please."},
            ],
            tools=domain.TOOL_SCHEMAS,
            temperature=0.0,
        )
        first_message = first["choices"][0]["message"]
        print("content    :", first_message.get("content"))
        print("tool_calls :", [c["function"]["name"] for c in first_message.get("tool_calls") or []])
    return


@app.cell(hide_code=True)
def s01_md_invariants(mo):
    mo.md(r"""
    ## The two invariants

    1. **Append the assistant message verbatim** — including `tool_calls`, with
       their ids — *before* you append any tool result. Rebuild it by hand and you
       will drop the id the result has to match.
    2. **Every `tool_call` gets a result carrying its `tool_call_id`**, before the
       next model call. One assistant message may request several tools; the
       results form a group.

    Break either one and you create an *orphaned tool result*: a result answering
    a call the conversation no longer contains.
    """)
    return


@app.cell
def test_s01_orphaned_tool_result_is_rejected():
    try:
        check_pairing([{"role": "tool", "tool_call_id": "nope", "content": "{}"}])
    except OrphanedToolResult as exc:
        assert "nope" in str(exc)
    else:
        raise AssertionError("an orphaned tool result was accepted")
    return


@app.cell(hide_code=True)
def s01_md_broken(mo):
    mo.md(r"""
    ## Experiment — break invariant 1 on purpose

    This loop is **deliberately wrong**: it forgets to append the assistant
    message. It is teaching material; do not "fix" it. Watch the failure class it
    produces.
    """)
    return


@app.cell
def s01_demo_broken(client, mo):
    with mo.redirect_stdout():
        broken_state = OrderState()
        broken_messages = [
            {"role": "system", "content": domain.PERSONA},
            {"role": "user", "content": "Get me a latte, please."},
        ]
        broken_body = client.chat(broken_messages, tools=domain.TOOL_SCHEMAS, temperature=0.0)
        broken_reply = broken_body["choices"][0]["message"]
        broken_calls = broken_reply.get("tool_calls") or []
        if not broken_calls:
            print("the model answered in words this turn; rerun to get a tool call")
        else:
            # BUG on purpose: the assistant message is never appended.
            for broken_call in broken_calls:
                broken_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": broken_call["id"],
                        "content": json.dumps(dispatch(broken_state, broken_call)),
                    }
                )
            try:
                client.chat(broken_messages, tools=domain.TOOL_SCHEMAS, temperature=0.0)
                print("no rejection — this endpoint is lenient; the conversation is still wrong")
            except OrphanedToolResult as exc:
                print("rejected before it ever left the machine:", exc)
    return


@app.cell(hide_code=True)
def s01_md_attempt(mo):
    mo.md(r"""
    ## Your turn — supply the tool results

    The assistant asked for two lookups. Return the result records that keep the
    conversation legal. Do **not** change `pending_calls` to hide a missing result.

    The starter reports **Attempt pending**, not success.
    """)
    return


@app.function
def attempt_tool_results(pending_calls, state):
    proposed_results = []  # Your attempt; one record per call, carrying its id.
    return proposed_results


@app.cell(hide_code=True)
def s01_reveal_tool_results(mo):
    reveal_tool_results = mo.ui.switch(
        value=False, label="Reveal the reference solution (after your attempt)"
    )
    reveal_tool_results
    return (reveal_tool_results,)


@app.function(hide_code=True)
def solution_tool_results(pending_calls, state):
    return [
        {
            "role": "tool",
            "tool_call_id": call["id"],
            "content": json.dumps(dispatch(state, call), sort_keys=True, ensure_ascii=False),
        }
        for call in pending_calls
    ]


@app.cell(hide_code=True)
def s01_reveal_source_tool_results(mo, reveal_tool_results):
    mo.stop(
        not reveal_tool_results.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_tool_results) + "```")
    return


@app.cell
def s01_demo_compare(mo):
    with mo.redirect_stdout():
        pending_calls = [
            {"id": "call_a", "type": "function",
             "function": {"name": "price_check", "arguments": '{"item": "latte"}'}},
            {"id": "call_b", "type": "function",
             "function": {"name": "price_check", "arguments": '{"item": "chocolate croissant"}'}},
        ]
        supplied = attempt_tool_results(pending_calls, OrderState())
        if not supplied:
            print("Attempt pending: supply one result record per call before comparing.")
        else:
            requested = {call["id"] for call in pending_calls}
            covered = {record.get("tool_call_id") for record in supplied}
            print("covered  :", sorted(covered))
            print("uncovered:", sorted(requested - covered))
    return


@app.cell(hide_code=True)
def s01_md_whole_loop(mo):
    mo.md(r"""
    ## The whole loop

    `cafe/loop.py` is the two invariants plus a turn cap. Read it, then run a real
    shift against your model.
    """)
    return


@app.cell
def s01_demo_shift(client, mo):
    with mo.redirect_stdout():
        shift = run_shift(
            client,
            ["Hi, get me a latte and a chocolate croissant.", "Nothing else, thanks."],
        )
        print("stop_reason:", shift["stop_reason"])
        print("turns_used :", shift["turns_used"], "| model calls:", shift["model_calls"])
        print("tools run  :", shift["state"].tool_log)
    return (shift,)


@app.cell
def test_s01_every_tool_call_has_a_paired_result(shift):
    check_pairing(shift["messages"])
    opened = [
        call["id"]
        for message in shift["messages"]
        if message["role"] == "assistant"
        for call in message.get("tool_calls") or []
    ]
    answered = [
        message["tool_call_id"] for message in shift["messages"] if message["role"] == "tool"
    ]
    assert sorted(opened) == sorted(answered), (opened, answered)
    assert shift["stop_reason"] in {"answered", "turn_cap", "script_done"}
    return


@app.cell
def test_s01_turn_cap_is_a_harness_property():
    capped = run_shift(
        StubClient(script=[
            {"choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None,
                "tool_calls": [{"id": f"c{i}", "type": "function", "function": {
                    "name": "price_check", "arguments": '{"item": "latte"}'}}]}}]}
            for i in range(20)
        ]),
        ["Get me something."],
        max_turns=3,
    )
    assert capped["stop_reason"] == "turn_cap"
    assert capped["turns_used"] == 3
    return


@app.cell(hide_code=True)
def s01_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the number you bank

    Run the shift three times and record **how many of the three produced a legal,
    fully paired conversation**. With a live model this is rarely 3/3 on a small
    endpoint, and that number is your S01 baseline. S02 turns it into an eval.

    ## What this unlocks

    You have a loop, and a number you cannot yet defend — one anecdote repeated
    three times. **S02-golden-evals** turns it into a measurement instrument:
    a golden set, a checker whose failures you trust, and a naive baseline to beat.
    """)
    return


@app.cell
def s01_demo_checkpoint(client, mo):
    with mo.redirect_stdout():
        legal = 0
        for _ in range(3):
            run = run_shift(client, ["Get me a latte.", "Nothing else."])
            try:
                check_pairing(run["messages"])
                legal += 1
            except OrphanedToolResult:
                pass
        print(f"S01 baseline: {legal}/3 legal conversations")
    return


if __name__ == "__main__":
    app.run()
