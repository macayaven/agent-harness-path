# Round-2 adversarial review

Verification basis: read the round-1 report and synthesis, inspected every lesson source, all notebooks, generated HTML, README, and AGENTS.md. S01–S07 and S09–S12 execute top-to-bottom; S08’s replayer was exercised in memory because recording would violate read-only mode. All twelve notebooks remain output-free, nbformat 4.5, and stdlib-only. Generated HTML matches the current sources, all checked-in local links resolve, and all referenced Mermaid chunks exist.

## 1. Round-1 validation

### Technical correctness

- **PARTIAL — S09 honesty theorem.** `lessons/src/S09-evidence-reports.md:112–147` now states the validators’ limitations, but the diagram still asks whether “every event” surfaced, line 135 says the report is “checkable iff” both checks pass, and `notebooks/s09_evidence_report_toy.ipynb`, coverage solution still concludes “every logged event surfaces” although it compares only turn numbers.
- **PARTIAL — S08 strict replay.** `notebooks/s08_observability_replay_toy.ipynb`, `Replayer.__call__`, now matches only `entries[_next]`, so reordering is genuinely rejected. The notebook also says parsed content rather than bytes. However, `lessons/src/S08-observability-replay.md:5–6,92–94,111,140–143` and `lessons/src/index.md:39` still promise byte-identical/frozen/verbatim responses, contradicting the JSON decode behavior and the lesson’s own narrower statement at lines 126–130.
- **PARTIAL — S11 hard budget and route mapping.** `notebooks/s11_budgets_routing_toy.ipynb`, `_estimate_usd` and `run_pipeline`, use the same deterministic usage functions as the mocks, so estimate equals actual and the pre-dispatch gate is coherent for this toy; `validate_policy` also uses the passed route map. `lessons/src/S11-budgets-routing.md:24–26,66–69` still teaches only a post-call meter/crossing narrative and never explains why production estimates require reservation, provider caps, or soft-stop wording.
- **PARTIAL — S11 p50.** The notebook honestly calls the result a three-fixture median and prints `median=`, but `lessons/src/S11-budgets-routing.md:138–140,212–216` still calls the three deterministic fixtures p50 measurements, as does the notebook’s transfer summary.
- **NEW ISSUE INTRODUCED — S12 labeling and κ.** The notebook now says label-first is instructed rather than enforced and calls the labels reference judgments. But the zero-denominator guard returns κ=1 for identical constant vectors even though κ is undefined there, while `lessons/src/S12-judge-calibration.md:37–40,75–77` still calls hand labels ground truth. Worse, the notebook concludes “9/10 with κ=0.80 is a judge you can gate on,” directly contradicting the lesson’s “nobody should ship a gate on” this 10-item set at lines 103–114.
- **FIXED — S14 holdout contamination.** `lessons/src/S14-ship-and-pilot.md:37–45,174–187` explicitly consumes failed fixtures as tuning cases and reserves an untouched second holdout for the final gate. Lines 72–78 also limit the n=1 pilot to one observed-run fact.
- **FIXED — S13 eval-suite oracle.** `lessons/src/S13-rebuild-from-memory.md:91–96,143–150` calls the suite a decision instrument, acknowledges missed regressions, and retains independent hunk review.
- **FIXED — S13 unsafe displacement.** `lessons/src/S13-rebuild-from-memory.md:133–155` uses a clean commit plus branch/worktree, keeps the canonical file in HEAD, and restores or drops the audit environment.
- **FIXED — S05 bool and malformed/multiple calls.** `notebooks/s05_consent_gate_toy.ipynb`, `validate_spec`, rejects booleans; `parse_args` fails closed on malformed JSON/types; `run_session` fences each emitted call before dispatch.
- **PARTIAL — S01 API-validation claim.** The notebook correctly narrows `_validate` to the planted orphan-ID failure, but `lessons/src/S01-agent-loop.md:65–66,84–87,144–148` and `AGENTS.md:153–155` still claim real-API-like message-sequence or adjacency validation that the mock does not implement.
- **FIXED — unsafe ground-truth fixtures.** S10 uses an unambiguous gazpacho over-refusal case; S06’s IBAN has a deliberately bad checksum and `112` is explicitly scoped to the EU with a verification-date convention.

### Pedagogy

- **PARTIAL — standalone S13/S14 arc.** `lessons/src/S13-rebuild-from-memory.md:7–10` and `S14-ship-and-pilot.md:9–13` now honestly admit that the path has no cumulative build. That resolves the false history, but not the self-contained-course claim: completion still requires an external project already possessing a banked suite, decision log, traces, failure counts, false-trigger rate, judge agreement, and naive-versus-governed numbers (`S14:99–115,196–209`).
- **FIXED — private-course notebook leakage.** No notebook now names private owned paths, decision IDs, runner exit semantics, or inaccessible course build instructions.
- **FIXED — lesson/notebook exercise mismatch.** The rewritten S01 and S02 lists now correspond to the experiments actually present.
- **NOT FIXED — attempt-before-solution contract.** `AGENTS.md:148–149` still says exercises come in attempt/solution pairs, and `lessons/src/index.md:20–21` presents the pattern without qualification; S01/S02 remain mostly supplied predict-then-run demonstrations. The synthesis’s promised “where implementation is required” qualification is absent.
- **PARTIAL — S02 deterministic-versus-quality dichotomy.** `lessons/src/S02-golden-evals.md:122–128` now correctly blames the weak checker, but the notebook transfer cell still generalizes that “safety stays deterministic while quality gets a judged tier,” omitting deterministic usefulness, selectivity, and completion checks.
- **FIXED — S06 detection boundary.** `lessons/src/S06-layered-detection.md:60–68,187–191` explicitly makes detection fallible and assigns enforcement to capability isolation, least privilege, tool authorization, egress control, and output handling.
- **FIXED — S13 recall versus engineering mastery.** `lessons/src/S13-rebuild-from-memory.md:125–132` scopes the audit to core abstractions and invariants and explicitly allows ordinary reference material for implementation detail.

### State of the art

- **PARTIAL — EU AI Act.** The high-risk dates and “scaled pilot is law” error are corrected against [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744). However, S05/S14’s blanket “Article 50 transparency from 2 August 2026” omits the amendment’s 2 December 2026 transition for certain pre-existing systems subject to Article 50(2).
- **FIXED — OpenAI Responses API.** S01 scopes its mechanism to a client-owned loop and acknowledges Responses as the recommended default for new integrations, consistent with [OpenAI’s guidance](https://openai.com/index/new-tools-for-building-agents/).
- **PARTIAL — MCP 2026-07-28.** S04/S05 now cite the current revision and correctly cover stateless requests, MRTR, Tasks, auth hardening, and deprecations. S05 nevertheless lists “Skills over MCP” as though it shipped in the extensions framework; the release names Tasks and MCP Apps, while Skills was still a working group. See the [official release](https://blog.modelcontextprotocol.io/posts/2026-07-28/).
- **FIXED — OpenTelemetry GenAI.** S08 points to the dedicated GenAI repository, distinguishes Langfuse’s `generation` term, and accurately describes the v1.42 migration documented in the [v1.42.0 release](https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.42.0).
- **FIXED — Apple PCC.** S11 now says content leaves the device and accurately limits the guarantees to constrained, stateless processing, deletion, staff inaccessibility, non-targetability, and transparency, consistent with [Apple’s PCC design](https://security.apple.com/blog/private-cloud-compute/).
- **NEW ISSUE INTRODUCED — Semantic Versioning.** `S14:159–166,210–215` correctly separates SemVer’s public-API contract from the path’s evidence policy, but the SOTA row at line 226 reintroduces the false claim that the tag asserts evidence coverage. The repeated `v1.0` shorthand also conflicts with SemVer’s required `X.Y.Z` form; [SemVer says 1.0.0 defines the public API](https://semver.org/spec/v2.0.0.html).
- **NOT FIXED — Anthropic Citations and ALCE.** S09’s body correctly limits Anthropic’s guarantee to valid source pointers, matching the [official documentation](https://platform.claude.com/docs/en/build-with-claude/citations). Its SOTA row nevertheless says the platform “engineers fabrication away.” The next row still maps ALCE citation recall/precision to this course’s fabrication/event-coverage split, although [ALCE](https://arxiv.org/html/2305.14627v2) measures whether generated statements are supported and whether citations are relevant—not harness-event coverage.
- **FIXED — OWASP Agentic Top 10.** S05/S06 add the ten Agentic Applications 2026 categories and connect tool misuse, privilege abuse, trust exploitation, and cascading failures to the course’s mechanisms; the list matches [OWASP’s 2026 framework](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).
- **FIXED — Anthropic Structured Outputs.** S04 now covers the GA interface, `output_config.format`, strict tools, supported families, and schema/refusal/truncation limitations consistently with the [current documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
- **PARTIAL — judge-calibration table stakes.** S12’s lesson adds multi-annotator adjudication, uncertainty intervals, repeated stochastic runs, position swaps, and prevalence-aware κ, but the notebook’s operational-gate conclusion contradicts that remediation.

### Publication readiness

- **FIXED — footer.** `lessons/template.html:105–108` now identifies The Agent Harness Path without private-companion framing.
- **FIXED — README/index opening.** Both open with “twelve notebook sessions plus two protocol sessions.”
- **FIXED — S13/S14 metadata.** Hands-on and Video lines render as separate, complete metadata entries.
- **NEW ISSUE INTRODUCED — offline Mermaid.** The assets are vendored, but `template.html:110–112` loads Mermaid through an ES-module import. README tells readers to open `lessons/index.html` directly; modern browsers reject module imports from `file://` with CORS errors, so diagrams still do not work under the advertised offline opening path. [MDN explicitly requires a local HTTP server for modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules).
- **FIXED — exact status tags.** Every SOTA table uses only the five required tags.
- **FIXED — license/release ownership.** README clearly separates learner-owned projects from restricted redistribution of course content.
- **PARTIAL — navigation/accessibility.** `build.py:29–77` adds working previous/index/next navigation at both ends of every page. Mermaid diagrams still lack explicit accessible names, captions, or textual alternatives.
- **PARTIAL — safety publication pass.** The IBAN, emergency locale, and food fixture were repaired. S09 still embeds unsourced, actionable advice about mounting a 23 kg loaded shelf and a heavy mirror on damaged old plaster; the synthesis rejected rather than resolved that part of the finding.

## 2. New findings

### Blocker

1. **The advertised offline entry point does not render diagrams.** `README.md:9` directs readers straight to `lessons/index.html`, while `template.html:110–112` uses an imported `.mjs` module. Vendoring removes the network dependency but not the browser’s `file://` module restriction. Either bundle Mermaid as a classic self-contained script or document and supply a one-command local server. This is observable on the first lesson, not an edge case.

### High

2. **S02 presents fabricated latency as measured product evidence.** `notebooks/s02_scripted_user_eval_toy.ipynb`, `drive`, appends three seeded `random.uniform(0.2, 2.0)` values unrelated to either engine; resetting the same seed makes naive and governed latency identical by construction. The delta table labels their median “p50 turn latency” and says the delta is measured, while `lessons/src/S02-golden-evals.md:62–67,118–121` treats it as attributable product evidence. The truth is only that the scope-check delta was measured; latency is an arbitrary shared stub.

3. **S08 cannot detect an omitted cassette suffix.** `Replayer.__call__` enforces order among calls actually received, but there is no `assert_exhausted()`/finalization check. A regression that deletes the last model call—or an entire final phase—finishes replay cleanly with unused entries. That undercuts the claimed behavior-drift alarm in `lessons/src/S08-observability-replay.md:95–98`; strict request matching and complete cassette consumption are separate invariants.

### Medium

4. **S05 fences arguments but not tool identity.** `notebooks/s05_consent_gate_toy.ipynb`, `parse_args` and `run_session`, never verify `call["function"]["name"]`; every valid `{room, power}` object is dispatched to `clean_room` regardless of the proposed function name. The lesson’s approved-action contract therefore checks parameters but not which capability was invoked. In addition, multi-call messages are checked and dispatched sequentially, so an early call can side-effect before a later call aborts; that behavior should be stated or the whole batch should be preflighted.

5. **Contributor documentation contradicts the remediated product.** `AGENTS.md:15–19` still says all fourteen lessons have runnable notebooks, while lines 72 and 120–124 acknowledge S13/S14 do not. `AGENTS.md:75` says “There are no other files,” despite `LICENSE` and `review/`. Lines 153–155 also preserve the overbroad S01 real-API claim. These stale instructions are likely to reintroduce fixed defects during the next content edit.

6. **The August 2026 OWASP LLM baseline is already stale.** S05/S06 continue to call the 2025 LLM list current and say the “2026 revision” merely keeps excessive agency near the top. OWASP now labels its current release [GenAI LLM Top 10 2026](https://owasp.org/www-project-top-10-for-large-language-model-applications/). Adding the separate Agentic Top 10 was correct, but it did not refresh the older LLM row.

### Low

7. **S14 overstates artifact citation as a universal documentation rule.** `lessons/src/S14-ship-and-pilot.md:98–100,200` says every claim or sentence without a citation is invention. Evidence-bearing behavioral and architectural claims should cite artifacts; procedural transitions, scope statements, and explanatory prose do not become inventions merely because they lack a trace or decision-record pointer. The absolute wording teaches cargo-cult citation rather than claim-to-evidence discipline.

## 3. Top 3 remaining changes by impact

1. **Repair S09 end-to-end — M.** Give events stable identities, validate those identities rather than turns, separate pointer validity, claim support, event coverage, and overall honesty, and correct both SOTA rows plus the notebook’s final conclusion.

2. **Make the final arc genuinely standalone—or explicitly optional — L.** Supply a cumulative/reference project with the artifacts S13/S14 consume, or move those sessions into an optional “apply this to an existing project” extension and stop counting them as self-contained course completion.

3. **Run one cross-artifact publication gate — M.** Fix direct-file Mermaid delivery, S02’s fake p50, S08 cassette exhaustion/byte claims, S11’s remaining p50 and hard-budget prose, S12’s undefined κ and gate contradiction, S01’s mock claims, and stale AGENTS instructions; then regenerate and recheck source, notebook, index, self-check, and SOTA wording as one contract.

VERDICT: major rework needed
