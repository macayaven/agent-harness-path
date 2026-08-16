## 1. **Critical technical errors**

- **BLOCKER — S09’s honesty theorem is false, and its validators do not establish what the prose claims.** [“Reports lie in exactly two ways”](lessons/src/S09-evidence-reports.md:76) excludes unsupported interpretations, misleading emphasis, wrong event notes, stale costs, and privacy leakage. The [coverage validator](notebooks/s09_evidence_report_toy.ipynb:497) compares only turn numbers, so two events on one turn can mask an omission. The citation validator proves substring presence, not that the quotation entails the report’s claim. Anthropic guarantees that citations point into supplied documents, not that the cited passage is relevant or supports the claim; “the platform now engineers fabrication away” therefore overstates the [actual guarantee](https://platform.claude.com/docs/en/build-with-claude/citations). Replace “honest iff” with the exact properties checked; validate event IDs/types and semantic support separately.

- **BLOCKER — S08’s “strict” replayer does not enforce sequence.** [Replayer.__call__](notebooks/s08_observability_replay_toy.ipynb:385) searches every unused entry and accepts any matching request. A program that reorders two distinct calls can therefore replay successfully, defeating the claimed behavior-drift tripwire. Match only the next cassette entry or explicitly record and enforce sequence/phase identifiers. Also, JSON-decoding and returning a Python object is not returning “frozen bytes verbatim”; claim content equality or preserve/canonicalize the original response bytes.

- **BLOCKER — S11’s budget is not a hard runtime invariant.** [run_pipeline](notebooks/s11_budgets_routing_toy.ipynb:255) checks the budget only after a call has incurred its entire cost, so a run can exceed the limit by one arbitrarily expensive call. The lesson repeatedly describes a budget that “holds.” Teach this as a postpaid soft stop unless the harness reserves worst-case call cost, sets per-call output limits, or uses a provider/gateway cap. The same function accepts a custom `routes` mapping but `validate_policy` consults global `ROUTES`, allowing validation and execution against different policy data.

- **S11’s latency result is mislabeled as a percentile measurement.** [Experiment 5](notebooks/s11_budgets_routing_toy.ipynb:601) takes the median of three deterministic synthetic months and calls it `p50`. That is not a latency distribution and provides no evidence about queueing, network variance, streaming, cold starts, or p95. Call it a three-fixture median or run repeated sampled trials.

- **S12 does not enforce label-before-judge despite claiming it does.** [The attempt/solution boundary](notebooks/s12_judge_calibration_toy.ipynb:359) relies entirely on reader discipline: the solution runs the judge when labels remain `None`; it merely skips scoring the learner. Either gate execution until labels are complete or change “enforces” to “instructs.” In addition, [`cohens_kappa`](notebooks/s12_judge_calibration_toy.ipynb:420) divides by zero when both label vectors contain one class. The lesson’s single-author labels are reference judgments, not ground truth.

- **S14 contaminates its own acceptance holdout.** The protocol says to use an unseen scenario, then after failure amend the system and [rerun the same fixture](lessons/src/S14-ship-and-pilot.md:164). After diagnosis and modification, that fixture is a tuning case, not unseen acceptance evidence. Consume a fresh reserved holdout for the final gate. Likewise, an n=1 pilot may reveal a showstopper but cannot certify even the weaker claim that “the house is not currently on fire.”

- **S13 treats the eval suite as an oracle.** [The asserted tolerance](lessons/src/S13-rebuild-from-memory.md:67) cannot guarantee that “a real behavioral gap cannot hide,” particularly when the text admits that the course uses one task. An incomplete or noisy suite can miss regressions. Call it the audit’s decision instrument and preserve a separate invariant/diff review.

- **S13’s audit procedure risks data loss.** [`mv core.py /tmp/core.py.original`](lessons/src/S13-rebuild-from-memory.md:120) can overwrite an existing temporary file and leaves the canonical source displaced until the final restore. A crash or mistaken command can lose work. Require a clean commit/worktree and rebuild on a branch or copy to a unique verified backup.

- **S05’s boundary validator accepts booleans as integers.** [`validate_spec`](notebooks/s05_consent_gate_toy.ipynb:40) accepts `True` for `max_power_level` and `max_turns` because `bool` subclasses `int`. This contradicts S04’s explicit bool exclusion. The execution path also assumes valid argument objects and processes only the first tool call; malformed arguments or parallel calls bypass the pedagogical promise of checking every proposed action.

- **S01’s mock does not validate message sequences “the way a real API does.”** [`_validate`](notebooks/s01_agent_loop_toy.ipynb:47) accepts a tool result if its ID appeared anywhere previously. It does not enforce adjacency, completeness of parallel tool results, duplicates, or ordering. It reproduces the planted orphan failure, but the stronger compatibility claim should be removed.

- **Two “ground truth” fixtures are unsafe or incorrect.** S10 declares [“carbonara is not a raw-egg hazard”](notebooks/s10_error_analysis_toy.ipynb:218), although traditional preparation may leave egg undercooked; that cannot anchor an unambiguous over-refusal label. S06 embeds a checksum-valid Spanish [IBAN](notebooks/s06_layered_detection_toy.ipynb:216) and hard-codes `112` without a locale. Use unmistakably invalid placeholders and location-aware emergency-policy fixtures.

## 2. **Pedagogical structure**

- **The standalone arc breaks at S13.** S01–S12 are independent toys in unrelated domains; the learner never builds one cumulative system, banked suite, decision log, or core file. S13 nevertheless says “[you spent twelve sessions building a system](lessons/src/S13-rebuild-from-memory.md:19),” and S14 requires “your own system.” A reader following only this repository has nothing satisfying those prerequisites. Add a cumulative capstone spine, supply an auditable reference project, or move S13/S14 out of the standalone path.

- **The notebooks leak the private companion course into the standalone route.** Examples include [S01’s `harness/loop.py` and D-01 bridge](notebooks/s01_agent_loop_toy.ipynb:244), [S02’s `runner.sh`, `run.py`, and p-task directions](notebooks/s02_scripted_user_eval_toy.ipynb:210), and similar “real build in the course repo” endings in S03, S06–S10. Because the standalone index links directly to these notebooks, this violates the repository’s own core invariant and leaves public learners with inaccessible instructions.

- **Several lesson exercise lists do not match their notebooks.** S01 asks learners to add a tool and compare unsafe exception propagation with error-as-message, but the notebook contains neither an add-a-tool attempt/solution pair nor an unsafe dispatch variant. S02 asks learners to weaken the signpost checker and add a third engine, but those are prose prompts rather than matching attempt/solution exercises. Audit every lesson list against notebook cells 1:1.

- **Attempt-before-solution is not consistent.** S01 and S02 mostly provide predict-then-run demonstrations rather than attempt/solution pairs; later notebooks have isolated experiments where the implementation is already supplied. Either narrow the public promise to “predict-first, with attempt cells where implementation is required” or bring every notebook into the stated contract.

- **S02 creates an unnecessary deterministic-versus-quality false dichotomy.** A deterministic checker can test task-specific usefulness, expected facts, refusal selectivity, and completion—not merely structure. The “refuses everything” engine passes because this particular checker is weak, not because deterministic checks inherently cannot catch uselessness. This matters because S12 builds on the same premise.

- **S06 teaches a dangerous security intuition.** The lesson correctly says prompt injection is not solved by instructions, but then describes a substring screen as “enforcement” before admitting base64, translation, and novel paraphrases escape it. Detection is not the security boundary. Capability isolation, least privilege, tool authorization, egress controls, and output handling must carry the enforcement claim; classifiers and patterns are fallible signals.

- **S13 over-identifies engineering mastery with closed-book recall.** Reconstructing invariants is useful retrieval practice; memorizing implementation details without documentation is not normally a production competency. The protocol should distinguish “restate and rebuild the core abstraction” from “work without legitimate reference material,” otherwise it rewards recall beyond what the stated engineering goal requires.

## 3. **State-of-the-art alignment**

- **The EU AI Act rows are publication-blocking.** S05 says high-risk human-oversight obligations are “now law” in the sense of currently applicable requirements, while S14 says “a scaled pilot is law.” The latter is unsupported, and the current amendment postpones Chapter III high-risk obligations to 2 December 2027 for Annex III systems and 2 August 2028 for Annex I systems. Update both rows from the current [EUR-Lex Regulation 2026/1744](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744), not an unofficial explainer.

- **S01 presents a legacy API model as the generic present.** Manual message-history reconstruction remains correct for Chat Completions, but current OpenAI guidance recommends the stateful Responses API; Conversations persist messages, tool calls, and outputs, and `previous_response_id` chains turns. Scope the lesson explicitly to a client-owned-loop implementation and acknowledge the [current stateful alternatives](https://developers.openai.com/api/docs/guides/conversation-state).

- **The MCP citations are one major revision behind.** S04 and S05 cite the 2025-06-18 specification. The current 2026-07-28 release adds a stateless core, Tasks, extensions, richer JSON Schema support, and revised interaction/authentication machinery. Refresh against the official [2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/); these changes materially affect the consent, long-running-task, schema, and observability lessons.

- **S08 links a moved/deprecated OpenTelemetry page.** GenAI conventions have moved into the dedicated [OpenTelemetry GenAI semantic-conventions repository](https://github.com/open-telemetry/semantic-conventions-genai). Also distinguish the vendor-specific Langfuse “generation” observation from OpenTelemetry’s model and agent spans rather than calling `generation` an industry-wide primitive.

- **S11 misstates Apple Private Cloud Compute.** “Content never leaves” is false: Apple explicitly says the device sends the prompt and necessary user data to attested PCC nodes. The architecture guarantees constrained processing, deletion, and inaccessibility to Apple—not local-only execution. Correct the row using Apple’s [PCC security description](https://security.apple.com/blog/private-cloud-compute/).

- **S14 misuses Semantic Versioning.** SemVer says v1.0.0 defines the public API; it says nothing about whether evidence covers claims. The course may define an additional release policy, but it cannot attribute that meaning to [SemVer](https://semver.org/spec/v1.0.0.html).

- **S09 overstates Anthropic Citations and mis-maps ALCE.** Valid source pointers do not guarantee entailment, and ALCE citation recall concerns whether claims are cited—not whether every harness event surfaced. Keep citation validity, claim support, and run-event coverage as three separate properties.

- **S05/S06 omit the current agent-security baseline.** The dated tables cite OWASP’s 2025 LLM list but omit the [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): goal hijacking, tool misuse, identity/privilege abuse, agentic supply-chain risk, memory/context poisoning, cascading failures, and rogue agents. These belong in a 2026 course about governing agents.

- **S04’s Anthropic Structured Outputs row reads as historical news, not August 2026 guidance.** Refresh the supported models, GA status, current `output_config.format` interface, and limitations from the [current documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

- **Judge calibration is missing 2026 table stakes.** S12 should include multi-annotator adjudication for subjective labels, confidence intervals or bootstrap uncertainty, repeated stochastic judge runs, position swaps, and explicit handling of prevalence-sensitive κ. A 10-item, single-author, binary set can teach mechanics but should not be presented as sufficient to earn an operational gate.

## 4. **Publication readiness**

- **The generated footer contradicts the product.** Every lesson says it is a “study companion,” “theory depth only,” and that the build, baselines, and audit live in the private course repo. See [template.html](lessons/template.html:94). That directly contradicts the README’s self-contained-course claim and S13/S14.

- **The public opening contains an immediate contradiction.** [README.md](README.md:3) and [index.md](lessons/src/index.md:3) say all fourteen sessions pair lessons with notebooks; both later acknowledge that S13/S14 do not. State “twelve notebook sessions plus two protocols” at first mention.

- **S13 and S14 have malformed metadata blocks.** The Video line interrupts the Hands-on sentence in both [S13](lessons/src/S13-rebuild-from-memory.md:9) and [S14](lessons/src/S14-ship-and-pilot.md:11). This renders as visibly broken prose at the top of the two capstone lessons.

- **Offline reading is incomplete.** The checked-in HTML imports Mermaid from jsDelivr at runtime in [template.html](lessons/template.html:101). Without network access, diagrams do not render. Vendor Mermaid locally or state that prose is offline but diagrams require a network.

- **The required SOTA status vocabulary is not followed.** Rows use `ignore for now`, `adopt when…`, `adopt at S12`, and `ignore as…`, although AGENTS.md says the five tags are exact. Put timing/qualification in the Take column and restore exact tags.

- **The release story conflicts with the license and final assignment.** README says the standalone path is meant to share or teach, S14 requires a public artifact, but the license reserves redistribution and derivative teaching. Clarify whether public learners may publish their work and what “public artifact” means under the license.

- **Public navigation is weak.** Lessons have no previous/next/index navigation, and Mermaid diagrams have no explicit textual alternative. The prose often explains the diagram, but a public course should provide predictable navigation and accessible labels/captions.

- **The safety examples need a publication pass by domain.** Fixed emergency numbers, realistic financial identifiers, high-mounted shelves, old-plaster anchors, and food-safety “ground truth” create avoidable real-world stakes in material advertised as harmless toys. Use lower-stakes domains or source and qualify the advice.

## 5. **Top 5 changes by impact**

1. **Create a real standalone spine for S13/S14, or remove them from this path — L.** The learner needs one cumulative artifact, suite, decision log, trace set, and release target. This is the largest design change and the prerequisite for honestly calling the course self-contained.

2. **Fix the false guarantees in S08, S09, S11, S12, and S14 — M.** Enforce replay order, narrow evidence-validator claims, distinguish soft from hard budgets, make calibration robust, and preserve an unseen acceptance holdout.

3. **Rebuild the security/governance claims around actual enforcement boundaries — L.** Treat detection as fallible; add least privilege, tool authorization, isolation, egress/output controls, incident response, rollback, and data-handling requirements to the path and ship gate.

4. **Re-audit every August 2026 table against primary sources — M.** Prioritize the EU AI Act, Responses API state, MCP 2026-07-28, OpenTelemetry GenAI migration, PCC, Anthropic Structured Outputs, OWASP Agentic Top 10, Citations, and SemVer.

5. **Perform one consistency/publication sweep — M.** Remove private-course bridges from standalone notebooks, align exercises with cells, repair S13/S14 headers, correct the footer and opening promise, normalize status tags, vendor Mermaid or qualify offline support, and reconcile licensing.

VERDICT: major rework needed
