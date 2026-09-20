import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import inspect
    import statistics
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cafe import domain, routing
    from cafe.model import get_client


@app.cell
def s11_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s11_md_hook(mo):
    mo.md(r"""
    # S11 — Budgets and routing

    **Carried in:** `cafe/taxonomy.py` — S10's failure classes — and the debrief
    number S10 banked. Your shift can now name what went wrong; tonight it learns
    what a call is allowed to cost and where it is allowed to run.

    **Today you ship:** `cafe/routing.py` — an estimate gate and routing-policy simulation.

    ## The hook

    Last Thursday the till showed **€0.42** of model spend on a task the shift
    prices at **€0.05**. Nothing errored. The loop kept refining, each call looked
    reasonable, and the moment anyone could see the total was the moment the
    invoice existed. Money spent on a call you did not need is not refundable by
    adding an `if` afterwards.

    Same evening, a "performance tweak" pointed the phase that reads the
    customer's handwritten note — card number, phone number, the lot — at a cloud
    route. It worked beautifully. It was also a leak, and it happened at the
    routing decision, not inside the model.

    ## The promise

    By the end of this session you can reject projected overages before dispatch
    and validate a classification policy. **The route labels are simulated:** all
    calls use the same configured client. They do not select models or establish
    locality. Bank reported usage, missing accounting, and latency separately from
    the illustrative cost estimates. Use synthetic café input only.
    """)
    return


@app.cell(hide_code=True)
def s11_md_client(mo):
    mo.md(r"""
    ## Your model, still the same seam

    `get_client()` is the only seam between this course and a model. Tonight the
    interesting numbers are the ones the endpoint itself reports: `usage` on the
    response, and `client.last_latency_ms` measured around the request. Live mode measures the endpoint; stub mode reports deterministic fixture values.
    """)
    return


@app.cell
def s11_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    print("neighbours:", routing.companion_note())
    return (client,)


@app.cell(hide_code=True)
def s11_md_theory(mo):
    mo.md(r"""
    ## The theory in depth

    ### 1. A budget is a runtime invariant, not a finance report

    The invoice is a lagging indicator. By the time it exists the calls have been
    paid for. So the budget lives **inside** the loop, and it reads *ahead*: the
    route prices its own call before the call happens, and a call that would cross
    the line is refused. `stop_reason="budget_exceeded"` is a first-class outcome —
    a run that costs more than the task is worth has failed, even mid-progress.

    The projection is uncertain. The ledger multiplies reported usage by an
    illustrative rate card, so both money figures are estimates. Missing or invalid
    usage stays unknown. With a cap, unknown accounting blocks the next call;
    a completed overrun stops later phases but cannot undo that call's cost.
    This is not a hard spending cap.

    ### 2. Routing is policy-as-data

    A route table is a dict: café phase → route name. Each route carries a
    location, a model label, and a price per 1k tokens. It is diffable, reviewable,
    and validatable without changing the client. None of these labels changes
    the actual model selected through `get_client()`.

    ![Simulated policy and illustrative cost estimates gate calls to one configured client](public/diagrams/s11-budget.svg)
    """)
    mo.md(r"""
    ### 3. Classification policy is separate from transport

    `validate_policy` rejects a simulated content-to-cloud mapping. It does not
    inspect endpoint location or prove that a payload is metadata-only. All allowed
    routes still call the same client; a real deployment needs actual data and
    transport boundaries.

    ### 4. What "measured" means tonight

    In live mode, valid `response["usage"]` counts and `client.last_latency_ms`
    are observations. A configured alias is printed beside the simulated route;
    optional `reported_model` says what the provider returned. Missing usage is
    unknown, and every money figure uses illustrative rates rather than billing.
    """)
    return


@app.cell
def s11_demo_routes():
    print("phase        classification")
    for phase, classification in routing.PHASES.items():
        print(f"  {phase:12s} {classification}")
    print()
    print(routing.describe_routes())
    return


@app.cell(hide_code=True)
def s11_predict_budget_gate(mo):
    mo.md(r"""
    ## Your turn — the gate predicate

    Before the call goes out, the harness knows `spent_usd` and the route's
    `projected_usd` for the call about to happen. Write the predicate that
    refuses it. Return a bool — the harness, not the predicate, does the refusing.

    Edge case that matters: no budget means no limit. Write it down before you run.
    """)
    return


@app.function
def attempt_budget_gate(projected_usd, spent_usd, budget_usd):
    refusal = None  # Your attempt: True when this call must be refused before dispatch.
    return refusal


@app.cell(hide_code=True)
def s11_reveal_budget_gate(mo):
    reveal_budget_gate = mo.ui.switch(
        value=False, label="Reveal the reference gate (after your attempt)"
    )
    reveal_budget_gate
    return (reveal_budget_gate,)


@app.function(hide_code=True)
def solution_budget_gate(projected_usd, spent_usd, budget_usd):
    return budget_usd is not None and spent_usd + projected_usd > budget_usd


@app.cell(hide_code=True)
def s11_reveal_source_budget_gate(mo, reveal_budget_gate):
    mo.stop(
        not reveal_budget_gate.value,
        mo.md("*Solution hidden. Flip the switch once you have run your attempt.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_budget_gate) + "```")
    return


@app.cell
def s11_demo_budget_gate():
    _examples = [
        {"projected_usd": 0.04, "spent_usd": 0.00, "budget_usd": 0.25},
        {"projected_usd": 0.04, "spent_usd": 0.23, "budget_usd": 0.25},
        {"projected_usd": 9.99, "spent_usd": 0.00, "budget_usd": None},
    ]
    for _example in _examples:
        _yours = attempt_budget_gate(**_example)
        _reference = solution_budget_gate(**_example)
        _example_budget = routing.Budget(_example["budget_usd"])
        _example_budget.spent_usd = _example["spent_usd"]
        _module = _example_budget.would_exceed(_example["projected_usd"])
        if _yours is None:
            print(f"{_example} -> Attempt pending: return True or False, not None")
        else:
            print(
                f"{_example} -> you={_yours} reference={_reference} module={_module}"
                f" {'OK' if _yours == _reference == _module else 'MISMATCH'}"
            )
    return


@app.cell(hide_code=True)
def s11_md_meter(mo):
    mo.md(r"""
    ## The metered call, on your endpoint

    One `draft_reply` call uses your configured client and the simulated
    `local-large` rate card. Compare the projection with the usage-based estimate,
    and keep unknown values visible. The route label does not switch endpoints.
    """)
    return


@app.cell
def s11_demo_metered_call(client):
    local_table = {
        "read_note": "local-small",
        "draft_reply": "local-large",
        "till_summary": "local-small",
    }
    routing.validate_policy(local_table)
    _draft = [
        {"role": "system", "content": domain.PERSONA},
        {"role": "user", "content": "Get me a latte and a chocolate croissant, please."},
    ]
    _record = routing.metered_call(client, local_table, "draft_reply", _draft)
    _usage = _record["response"].get("usage") or {}
    print("simulated route  :", _record["route"], "->", _record["route_model"])
    print("configured client:", _record["client_model"])
    print("reported model   :", _record.get("reported_model", "not reported"))
    print("dispatched       :", _record["dispatched"])
    print("usage from wire  :", _usage)
    print("tokens recorded  :", _record["tokens"])
    print("client latency ms:", _record["latency_ms"])
    print("usage known      :", _record["usage_known"])
    print("cost estimates   :", "projected", _record["projected_usd"],
          "usage-based", _record["estimated_cost_usd"], "USD at illustrative rates")
    return


@app.cell(hide_code=True)
def s11_predict_route_table(mo):
    mo.md(r"""
    ## Your turn — a route table that survives validation

    Fill `attempt_route_table()` so that `validate_policy` accepts it. The phases
    are `read_note` and `draft_reply` (content) and `till_summary` (metadata); the
    routes are `local-small`, `local-large` and `cloud-frontier`.

    The boundary answers "is it allowed". It never answers "is it wise" — that is
    the measurement you would run next, on the S02 checkers this run can see.
    """)
    return


@app.function
def attempt_route_table():
    table = {
        "read_note": None,  # Your attempt: a route name per phase.
        "draft_reply": None,
        "till_summary": None,
    }
    return table


@app.cell(hide_code=True)
def s11_reveal_route_table(mo):
    reveal_route_table = mo.ui.switch(
        value=False, label="Reveal a reference route table (after your attempt)"
    )
    reveal_route_table
    return (reveal_route_table,)


@app.function(hide_code=True)
def solution_route_table():
    return {
        "read_note": "local-small",
        "draft_reply": "local-large",
        "till_summary": "local-small",
    }


@app.cell(hide_code=True)
def s11_reveal_source_route_table(mo, reveal_route_table):
    mo.stop(
        not reveal_route_table.value,
        mo.md("*Solution hidden. Flip the switch once you have written your own.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_route_table) + "```")
    return


@app.cell
def s11_demo_route_table():
    _table = attempt_route_table()
    if any(name is None for name in _table.values()):
        print("Attempt pending: give every phase a route name before validating.")
    else:
        try:
            routing.validate_policy(_table)
            print("valid :", _table)
        except routing.RouteRefused as exc:
            print("REFUSED before any call:", exc)
        _reference = solution_route_table()
        routing.validate_policy(_reference)
        print("reference valid too:", _reference)
    return


@app.cell
def test_s11_projected_over_budget_is_never_dispatched():
    _probe = get_client()
    _table = {
        "read_note": "local-small",
        "draft_reply": "local-small",
        "till_summary": "local-small",
    }
    # A zero budget makes every projection an overage: the first call is refused.
    _ledger = routing.Budget(budget_usd=0.0)
    _before = _probe.calls
    _record = routing.metered_call(
        _probe,
        _table,
        "draft_reply",
        [{"role": "user", "content": "Get me a latte."}],
        budget=_ledger,
    )
    assert _record["dispatched"] is False
    assert _record["refusal"] == "projected_over_budget"
    assert _probe.calls == _before, "a refused call must never reach the endpoint"
    assert _ledger.spent_usd == 0.0
    return


@app.cell
def test_s11_content_phase_on_a_cloud_route_raises():
    _misconfigured = {
        "read_note": "cloud-frontier",
        "draft_reply": "local-large",
        "till_summary": "local-small",
    }
    try:
        routing.validate_policy(_misconfigured)
    except routing.RouteRefused as exc:
        assert "read_note" in str(exc)
    else:
        raise AssertionError("a content phase on a cloud route was allowed")

    # The metadata phase on the same cloud route is permitted: classification
    # decides what is allowed, not the vendor's reputation.
    routing.validate_policy(
        {
            "read_note": "local-small",
            "draft_reply": "local-large",
            "till_summary": "cloud-frontier",
        }
    )
    return


@app.cell
def test_s11_metered_tokens_match_the_endpoint_usage():
    _probe = get_client()
    _table = {
        "read_note": "local-small",
        "draft_reply": "local-large",
        "till_summary": "local-small",
    }
    _record = routing.metered_call(
        _probe,
        _table,
        "draft_reply",
        [{"role": "user", "content": "How much is a croissant?"}],
    )
    assert _record["dispatched"] is True
    _usage = _record["response"].get("usage") or {}
    assert _record["tokens"] == routing.usage_tokens(_usage)
    assert _record["usage_known"] == (_record["tokens"] is not None)
    assert _record["latency_ms"] == _probe.last_latency_ms
    return


@app.cell(hide_code=True)
def s11_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the numbers you bank

    Two invariants you can now demonstrate on demand:

    - a call whose projected cost crosses the budget is refused **before**
      dispatch, so `client.calls` does not move and its cost never lands;
    - a content phase pointed at a simulated cloud route raises, while a metadata
      phase on that route is permitted by the teaching policy.

    Bank known token counts, accounting completeness, and median latency when
    available, beside the illustrative cost estimate. Stub results are fixtures;
    live results describe your configured client. S12 reuses this estimate.

    ## What this unlocks

    You have a harness that can refuse work before paying for it, and a table you
    can review in a diff. What you do not have is any idea whether the thing
    producing the answers is any good: **S12-judge-calibration** turns a model
    into an instrument, seeds defects you already know the answer to, and makes
    you measure detection and false positives before you trust a single verdict.
    """)
    return


@app.cell
def s11_demo_checkpoint(client):
    _table = {
        "read_note": "local-small",
        "draft_reply": "local-large",
        "till_summary": "local-small",
    }
    _prompts = [
        "What do you recommend for breakfast?",
        "I'm allergic to milk, what can I have?",
        "Two espressos, please.",
    ]
    _phases = [("draft_reply", [{"role": "system", "content": domain.PERSONA},
                               {"role": "user", "content": _line}])
               for _line in _prompts]
    _run = routing.run_phases(client, _table, _phases, budget_usd=0.50)
    _ledger = _run["budget"]
    _dispatched = [record for record in _ledger.calls if record["dispatched"]]
    _tokens = [record["tokens"] for record in _dispatched]
    _latencies = sorted(record["latency_ms"] for record in _dispatched
                        if type(record["latency_ms"]) in (int, float))
    _median = statistics.median(_latencies) if _latencies else None
    print("calls dispatched :", len(_dispatched), "of", len(_prompts), "requested")
    print("tokens (usage)   :", _tokens, "known sum", sum(t for t in _tokens if t is not None))
    print("accounting complete:", _ledger.usage_complete)
    print(f"latency samples  : {[round(value, 1) for value in _latencies]} ms")
    print("median latency ms:", _median)
    print(f"known cost estimate at illustrative $0.06/1k: ${_ledger.spent_usd:.4f} of ${_ledger.budget_usd:.2f}")
    print("stop reason      :", _run["stop_reason"])
    _tracer = routing.publish(_run)
    if _tracer is None:
        print()
        print("cafe.trace not importable: the ledger stays in memory, no span tree.")
    else:
        print()
        print("--- S08 span tree, mirrored from this run ---")
        print(_tracer.render())
    return


if __name__ == "__main__":
    app.run()
