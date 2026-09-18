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

    from cafe import judge
    from cafe.model import get_client


@app.cell
def s12_imports():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def s12_md_hook(mo):
    mo.md(r"""
    # S12 — Judge calibration

    **Carried in:** `cafe/routing.py` — S11's route table, its budget gate, and
    the token and latency numbers it measured on your endpoint. You now know what
    a call costs; tonight you find out whether the verdict it returns is worth
    anything.

    **Today you ship:** `cafe/judge.py` — the seeded-defect game and the
    agreement math.

    ## The hook

    Your judge scored the shift **9/10**, so you let it gate the release. A week
    later a customer found two defects it had waved through — and one clean order
    it had failed for being "too terse". You never measured either number. The 9/10
    was never a measurement; it was an opinion with a decimal point.

    ## The promise

    By the end of this session you will have seeded known defects into clean café
    transcripts, labeled the corpus yourself **before** any judge output existed
    on your screen, and reported detection rate, false-positive rate, and Cohen's
    κ — and you will be able to say exactly what that κ licenses and what it does
    not.

    A note you should read before the numbers: a small local model will be a bad
    judge. That is the finding, not a bug in the notebook.
    """)
    return


@app.cell(hide_code=True)
def s12_md_client(mo):
    mo.md(r"""
    ## Your model, as ever

    `get_client()` returns the one seam to your endpoint. Tonight the model only
    ever produces verdicts; the counting, the κ and the answer key are ordinary
    Python, so the measurement is trustworthy even when the judge is not.
    """)
    return


@app.cell
def s12_demo_client():
    client = get_client()
    print("mode :", client.mode)
    print("model:", getattr(client, "model", "stub"))
    print("neighbours:", judge.companion_note())
    print("defect classes in play:", judge.defect_classes())
    _aliases = judge.taxonomy_aliases()
    print("S10's name for them:", _aliases or "(no overlap available this run)")
    return (client,)


@app.cell(hide_code=True)
def s12_md_theory(mo):
    mo.md(r"""
    ## The theory in depth

    ### 1. A judge is an instrument; an uncalibrated instrument is an opinion

    A rubric judge is a model call that returns pass/fail. Nothing in that call
    tells you how often it is right, and a verdict is far more persuasive than it
    deserves to be. Calibration is the act of measuring the instrument against
    something you already know.

    ### 2. You need an answer key you built

    So you seed the defects yourself. Take clean café transcripts, mutate a known
    number of them in ways the harness can prove: an allergen served with no
    warning, a price that is not on the menu, a ticket fired before the customer
    confirmed. Now every transcript has a key: defective class, or clean. The
    judge never sees the key.

    Defects must be *quiet*. A judge that only catches blatant garbage is useless;
    the seeded ones have to be the kind a tired shift actually ships.

    ### 3. The order of operations is the protocol

    ![Seed defects, hand-label blind, calibrate the rubric, re-measure with chance-corrected agreement](public/diagrams/s12-judge.svg)
    """)
    mo.md(r"""
    Hand labels come **before** judge output, because a seen verdict anchors your
    label and the measurement dies quietly. Detection reported without false
    positives is half a number: a judge that fails everything detects everything.
    And a judge you tuned against this corpus has stopped measuring it.

    ### 4. κ, and what "undefined" means

    Raw agreement flatters a judge when one class dominates. Cohen's κ subtracts
    the agreement chance would produce anyway:

    κ = (p_observed − p_expected) / (1 − p_expected)

    If the chance term is degenerate — every transcript in both vectors carries
    the same label — κ is **undefined**, not 1.0. The helper returns `None`, and a
    report that turns that into 1.0 is lying to you. `κ = 0.4` is a judge that has
    earned a bigger calibration set, not one you can gate on.
    """)
    return


@app.cell(hide_code=True)
def s12_md_corpus(mo):
    mo.md(r"""
    ## The corpus

    Six clean café transcripts, three of them mutated with exactly one seeded
    defect each. The order is fixed and mixed, so "the defective ones are first"
    never becomes a habit. Read a couple before you go on — the key stays out of
    the notebook until the labeling section.
    """)
    return


@app.cell
def s12_demo_corpus():
    transcripts, key = judge.seeded_corpus()
    print("corpus size:", len(transcripts), list(transcripts))
    print("defects seeded:", sum(1 for value in key.values() if value), "of", len(key))
    print()
    print("--- a sample transcript ---")
    print(judge.render_transcript(transcripts[list(transcripts)[0]]))
    return key, transcripts


@app.cell(hide_code=True)
def s12_md_judge_v1(mo):
    mo.md(r"""
    ## Judge v1 — the rubric you write on the first try

    One pass/fail verdict per transcript, returned as JSON. This rubric is
    deliberately uncalibrated: strict, style-sensitive, and told to distrust short
    answers. It is the judge most people ship.
    """)
    return


@app.cell
def s12_demo_judge_v1(client, transcripts):
    verdicts_v1 = judge.run_judge_all(client, transcripts, judge.RUBRIC_V1)
    _sample = list(verdicts_v1)[0]
    print(f"sample {_sample}:", verdicts_v1[_sample])
    print("one verdict per transcript:", len(verdicts_v1) == len(transcripts))
    return (verdicts_v1,)


@app.cell
def s12_demo_scores_v1(key, verdicts_v1):
    _det = judge.detection_rate(key, verdicts_v1)
    _fp = judge.false_positive_rate(key, verdicts_v1)
    _unreadable = [tid for tid, verdict in verdicts_v1.items() if verdict["verdict"] == "unparseable"]
    print("v1 detection       :", judge.fmt_rate(_det))
    print("v1 false positives :", judge.fmt_rate(_fp))
    print("v1 unparseable     :", f"{len(_unreadable)}/{len(verdicts_v1)}", _unreadable)
    print()
    print("Both numbers or neither. A judge that fails everything detects everything.")
    print("The misses:", [tid for tid in key if key[tid] and verdicts_v1[tid]["verdict"] != "fail"])
    return


@app.cell(hide_code=True)
def s12_md_hand_labels(mo):
    mo.md(r"""
    ## Hand-label first — this is the protocol, not a warm-up

    Before the key and before any more judge output, label all six transcripts
    yourself against the rubric: does the barista answer the actual question,
    respect declared constraints, stay consistent, and not abandon a correct
    answer under pressure?

    A verdict you have already seen anchors your label, and an anchored label
    measures the judge's influence on you, not the judge.
    """)
    return


@app.cell(hide_code=True)
def s12_predict_hand_labels(mo):
    mo.md(r"""
    **Predict first.** Write your six labels in `attempt_hand_labels`, and predict
    the pair: how many of the defective transcripts judge v1 will catch, and how
    many clean ones it will fail. Write both numbers down before running the
    calibration cell — this is the whole protocol in one line.
    """)
    return


@app.function
def attempt_hand_labels(transcripts):
    # Your attempt: "pass" or "fail" per id.
    return {tid: None for tid in transcripts}


@app.cell(hide_code=True)
def s12_reveal_hand_labels(mo):
    reveal_hand_labels = mo.ui.switch(
        value=False, label="Reveal the seed-derived reference labels (after your attempt)"
    )
    reveal_hand_labels
    return (reveal_hand_labels,)


@app.function(hide_code=True)
def solution_hand_labels(key):
    return judge.reference_labels(key)


@app.cell(hide_code=True)
def s12_reveal_source_hand_labels(mo, reveal_hand_labels):
    mo.stop(
        not reveal_hand_labels.value,
        mo.md("*Reference hidden. Label the transcripts yourself first.*"),
    )
    mo.md("```python\n" + inspect.getsource(solution_hand_labels) + "```")
    return


@app.cell
def s12_demo_hand_labels(key, transcripts):
    _labels = attempt_hand_labels(transcripts)
    _unfilled = [tid for tid, label in _labels.items() if label is None]
    if _unfilled:
        print("Attempt pending: label every transcript before scoring yourself.")
        print("still unlabeled:", _unfilled)
    else:
        _reference = judge.reference_labels(key)
        _ids = list(transcripts)
        _agree = sum(_labels[tid] == _reference[tid] for tid in _ids)
        _mine = [_labels[tid] for tid in _ids]
        _ref = [_reference[tid] for tid in _ids]
        print(f"you vs the seed key: {_agree}/{len(_ids)} agreement")
        print(f"your κ vs the key  : {judge.fmt_kappa(judge.cohens_kappa(_ref, _mine))}")
    return


@app.cell
def s12_demo_kappa_v1(key, transcripts, verdicts_v1):
    _reference = judge.reference_labels(key)
    _ids = list(transcripts)
    _ref = [_reference[tid] for tid in _ids]
    _v1 = [verdicts_v1[tid]["verdict"] for tid in _ids]
    _agree = sum(left == right for left, right in zip(_ref, _v1))
    _kappa = judge.cohens_kappa(_ref, _v1)
    print(f"judge v1 vs the seed key: {_agree}/{len(_ids)} agreement, κ = {judge.fmt_kappa(_kappa)}")
    print()
    for _label, _group in (("defective", [t for t in _ids if key[t]]),
                           ("clean", [t for t in _ids if not key[t]])):
        _hits = sum(_reference[tid] == verdicts_v1[tid]["verdict"] for tid in _group)
        _misses = [tid for tid in _group if _reference[tid] != verdicts_v1[tid]["verdict"]]
        print(f"{_label:<10} {_hits}/{len(_group)}  misses: {_misses}")
    print()
    print("An aggregate hides this. Split it by the class you care about before believing it.")
    return


@app.cell(hide_code=True)
def s12_md_judge_v2(mo):
    mo.md(r"""
    ## Judge v2 — calibrated against the failure classes

    The v1 misses are not mysteries; they are classes. Spell them out in the
    rubric: the seeded allergen miss, the invented price, the ticket fired without
    confirmation — and delete the style bias, which was doing the judging. Same
    corpus, same model, same order. Only the rubric changed.
    """)
    return


@app.cell
def s12_demo_judge_v2(client, transcripts):
    verdicts_v2 = judge.run_judge_all(client, transcripts, judge.RUBRIC_V2)
    print("sample v2 verdict:", verdicts_v2[list(verdicts_v2)[0]])
    return (verdicts_v2,)


@app.cell
def s12_demo_scores_v2(key, verdicts_v1, verdicts_v2):
    _fp1 = judge.false_positive_rate(key, verdicts_v1)
    _fp2 = judge.false_positive_rate(key, verdicts_v2)
    _det2 = judge.detection_rate(key, verdicts_v2)
    print("v2 detection       :", judge.fmt_rate(_det2))
    print(f"v2 false positives : {judge.fmt_rate(_fp2)}  (v1 was {judge.fmt_rate(_fp1)})")
    print()
    print("The claim this session makes is relative and measured in one session:")
    print("the calibrated rubric does not produce MORE false alarms than the")
    print("uncalibrated one on the same corpus. It makes no promise about detection:")
    print("a better rubric, not a better model, is all you changed.")
    return


@app.cell
def test_s12_kappa_is_undefined_for_constant_vectors():
    assert judge.cohens_kappa(["pass"] * 6, ["pass"] * 6) is None
    assert judge.cohens_kappa(["fail"] * 4, ["fail"] * 4) is None
    assert judge.cohens_kappa([], []) is None
    return


@app.cell
def test_s12_every_transcript_gets_exactly_one_verdict(
    transcripts,
    verdicts_v1,
    verdicts_v2,
):
    for verdicts in (verdicts_v1, verdicts_v2):
        assert set(verdicts) == set(transcripts)
        assert all(verdict["verdict"] in judge.VERDICTS for verdict in verdicts.values())
        assert len(verdicts) == len(transcripts)
    return


@app.cell
def test_s12_key_and_verdicts_have_the_same_length(
    key,
    transcripts,
    verdicts_v1,
):
    assert len(key) == len(transcripts) == len(verdicts_v1)
    assert set(key) == set(transcripts) == set(verdicts_v1)
    return


@app.cell
def test_s12_calibrated_false_positive_rate_does_not_worsen(
    key,
    verdicts_v1,
    verdicts_v2,
):
    _fp1 = judge.false_positive_rate(key, verdicts_v1)
    _fp2 = judge.false_positive_rate(key, verdicts_v2)
    assert _fp2[2] <= _fp1[2], (_fp1, _fp2)
    return


@app.cell
def test_s12_reference_labels_cover_every_transcript(key, transcripts):
    _reference = judge.reference_labels(key)
    assert set(_reference) == set(transcripts)
    assert all(label in ("pass", "fail") for label in _reference.values())
    assert sum(1 for label in _reference.values() if label == "fail") == sum(
        1 for defect in key.values() if defect
    )
    return


@app.cell(hide_code=True)
def s12_md_checkpoint(mo):
    mo.md(r"""
    ## Checkpoint — the numbers you bank

    You are done when you can put these in one sentence and defend it: **6
    transcripts, 3 seeded defects, detection n/3, false positives n/3, κ = …** for
    the calibrated rubric — with the uncalibrated pair next to it so the change is
    attributable. On a small local model those numbers may be poor. That is your
    instrument's actual precision, and it is worth more than a 9/10 you cannot
    reproduce.

    ## What this unlocks

    That is the core path closed. Twelve sessions, one `cafe/` package, and a
    number banked per session — a loop with proven invariants, a golden set, a
    context budget, a ticket contract, a consent gate, layered detection, bounded
    repair, a replayable trace, an evidence report, a failure taxonomy, a cost and
    latency ledger, and a calibrated judge.

    You are not done, but the next step is deliberately **unaided**:
    **S13-rebuild-from-memory** is the optional closed-book audit. Close every
    notebook and rebuild the harness from memory — no scaffolding, no generated
    answers, nothing filled in for you. Everything you would need is already in
    what you built; the audit only tells you whether it is in *you*.
    """)
    return


@app.cell
def s12_demo_checkpoint(key, transcripts, verdicts_v1, verdicts_v2):
    _det1 = judge.detection_rate(key, verdicts_v1)
    _fp1 = judge.false_positive_rate(key, verdicts_v1)
    _det2 = judge.detection_rate(key, verdicts_v2)
    _fp2 = judge.false_positive_rate(key, verdicts_v2)
    _ids = list(transcripts)
    _ref = [judge.reference_labels(key)[tid] for tid in _ids]
    _k1 = judge.cohens_kappa(_ref, [verdicts_v1[tid]["verdict"] for tid in _ids])
    _k2 = judge.cohens_kappa(_ref, [verdicts_v2[tid]["verdict"] for tid in _ids])
    print(f"bank this line — {len(transcripts)} transcripts, {_det1[1]} seeded defects")
    print(f"  v1: detection {judge.fmt_rate(_det1)}  false positives {judge.fmt_rate(_fp1)}  κ {judge.fmt_kappa(_k1)}")
    print(f"  v2: detection {judge.fmt_rate(_det2)}  false positives {judge.fmt_rate(_fp2)}  κ {judge.fmt_kappa(_k2)}")
    return


if __name__ == "__main__":
    app.run()
