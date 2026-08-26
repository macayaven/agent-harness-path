# Six-week post-core / BYO-artifact study progress

Copy this file before starting:

```bash
mkdir -p study/evidence
cp study/PROGRESS.template.md study/PROGRESS.md
```

This is a learner-owned record. Link to your own commits, logs, plots, and notes.
Do not paste answer keys, assignment text, external notebooks, course transcripts,
or solution code.

## Hard prerequisite gate

W1 remains blocked until every field below is complete.

- [ ] **Harness preparation:** I completed S01–S12 (and the hard path if it is my
  chosen artifact), or I already have equivalent harness experience.
- [ ] **Artifact:** I have an inspectable agent/eval artifact.
- [ ] **Baseline:** the artifact has a green, banked baseline that I can reopen.
- **Preparation route:** core / core + hard path / equivalent prior experience
- **Artifact name and location:**
- **Baseline command or receipt path:**
- **Baseline date and result:**
- **Why this baseline is sufficient to begin W1:**

If the preparation checkbox is false, do S01–S12 first. If the artifact or baseline
checkbox is false, bank an inspectable baseline before starting the overlay.

## Route contract

- **Start date:**
- **Learning emphasis:** harness/evals/inference-systems depth OR model-layer fundamentals depth
- **Why this learning emphasis:**
- **Weekly hour ceiling:** use the planned hours below; do not create make-up binges.
- **Protected outcomes:** learner-owned CS336 A1 evidence + shipped harness artifact.
- **Evidence rule:** no completion claim until the named artifact is banked and
  reopenable.

## Six-week ledger

| Week | Planned model | Actual model | Planned harness | Actual harness | Evidence status | Stop/defer decision |
|---|---:|---:|---:|---:|---|---|
| W1 | 2.0 |  | 3.0 |  | not started |  |
| W2 | 3.5 |  | 1.5 |  | not started |  |
| W3 | 5.5 |  | 0.5 |  | not started |  |
| W4 | 6.0 |  | 0.0 |  | not started |  |
| W5 | 5.0 |  | 1.0 |  | not started |  |
| W6 | 1.0 |  | 3.5 |  | not started |  |
| **Total** | **23.0** |  | **9.5** |  |  |  |

## W1 — Artifact baseline + managed post-training pass

### Predict first

- Before running anything, what do I expect the harness gates to prove, and what
  could still be false if they pass?
- What do I expect a managed RLHF pipeline to hide from me compared with a
  learner-owned RM/PPO implementation?

### Record

- Model hours:
- Harness hours:
- Commands/runs:
- Prediction misses:
- Banked evidence path:
- Commit/run identifiers:
- Evidence I can reopen:
- Claim this evidence supports:
- Claim this evidence does **not** support:

### Restate understanding

In my own words, what happened in the managed pipeline, what remained managed, and
why the local harness results count as evidence rather than a general quality claim?

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- If this week slipped, what single protected base item carries forward?

## W2 — Optimize, deploy, benchmark inference

### Predict first

- Which measurement do I expect the optimization to change, and what confounder
  could create the same change?
- What deployment and workload details must be fixed before two benchmark numbers
  are comparable?

### Record

- Model hours:
- Harness hours:
- Optimization configuration:
- Deployment command/configuration:
- Benchmark workload and environment:
- Raw result path:
- Baseline number:
- Result number:
- Banked evidence path:
- Prediction misses:

### Restate understanding

In my own words, separate the optimization, deployment, and benchmark stages. What
does the comparison show, and what does it not show?

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- Did I preserve the receipt instead of starting CS336 early?

## W3 — CS336 A1: concepts + tokenizer

### Predict first

- Which tokenizer invariant do I expect to fail first in my implementation?
- What test would distinguish a real invariant failure from a mistaken expectation?

### Record

- Model hours:
- Harness hours:
- Learner-owned commit SHA:
- Test command/results:
- Failure investigated:
- Banked evidence path:
- Prediction misses:
- Questions I asked an agent:
- How I kept those questions inside the honor-code boundary:

### Restate understanding

In my own words, explain the tokenizer's core invariants and the failure I debugged.
Do not copy course wording.

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- Confirm A2/A3/A5 implementation remained deferred:

## W4 — CS336 A1: Transformer + training loop

### Predict first

- Which interface or tensor-shape assumption is most likely to fail in the first
  smoke run?
- What is the smallest run that would falsify my current implementation claim?

### Record

- Model hours:
- Harness hours:
- Learner-owned commit SHA:
- Architecture/configuration:
- Test command/results:
- First successful smoke-log path:
- Defect investigated and fixed:
- Banked evidence path:
- Prediction misses:

### Restate understanding

In my own words, trace data through the Transformer and training loop. Explain why
the smoke run is necessary but insufficient evidence of a trained model.

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- Confirm no make-up harness work displaced A1:

## W5 — Finish and bank A1

### Predict first

- What loss-curve behavior do I expect, and which pattern would make me distrust
  the run?
- What should sample generations add to the evidence that the curve alone cannot?

### Record

- Model hours:
- Harness hours:
- Learner-owned commit SHA:
- Run configuration:
- Loss-curve path:
- Sample-generation path:
- Test command/results:
- Banked evidence path:
- Prediction misses:
- Limits on what this run proves:

### Restate understanding

In my own words, connect the implementation, tests, loss curve, and samples. Which
claim is now justified, and which larger model-training claim is still unjustified?

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- Confirm every second coding assignment remained deferred:

## W6 — Ship the harness artifact + evidence narrative

### Predict first

- Which release gate is most likely to expose drift since W1?
- Which claims do I expect the harness release receipts to support, which claims
  require the A1 evidence, and which claims will remain unsupported?

### Record

- Model hours:
- Harness hours:
- Release commit SHA:
- Verification commands/results:
- Shipped artifact location:
- Supported claims by evidence source:
- Unsupported-claims list:
- Banked evidence path:
- Prediction misses:
- Optional Anthropic API course taken? If yes, hours and learner-written note path:

### Restate understanding

In my own words, explain what the harness artifact demonstrates, which additional
claims the A1 evidence supports, and what neither evidence set demonstrates.

### Stop/defer decision

- Base complete?
- Stretch attempted?
- What did I stop or defer, and why?
- Confirm the CCA exam remained outside this six-week route:

## Final evidence audit

- [ ] Each week records actual model and harness hours.
- [ ] Each week contains a written prediction made before the work.
- [ ] Each week links one reopenable evidence artifact.
- [ ] Each restatement uses my own words.
- [ ] A1 implementation and debugging remained learner-owned.
- [ ] No external course materials or answer keys were copied here.
- [ ] Deferred work is named rather than silently counted as completed.
- [ ] Each final claim names its supporting evidence and its limits.
- [ ] Any calendar extension was planned; no make-up binge was used.
