# CS PROJECT INSTRUCTIONS — Crowd-1 Stage 1 (acceptance tests)

Purpose. Implement the exact finite-N simulator of process specification v0.6 and run the Stage 1 acceptance tests only. Nothing else is authorized in this project until a written "Stage 2 authorized" message arrives from the owner.

Files in this project.
- review_packet_v0_6_1.md — the model. The authoritative process specification is the memo section "PROCESS SPECIFICATION v0.6". Appendices C and D are derivations; use them for the predicted quantities referenced in the design, not as alternative specifications.
- crowd1_cs_design_and_manuscript_brief_v0_3.md — the design. Part A governs this project: A1 implementation, A2 acceptance tests T1–T6, A3 observable separation, A4a tolerances for zero predictions, A5 controls (automaton and surrogate as defined in T6), A6 pass rule and error accounting. Part B is not for this project.

Scope. Stage 1 = A1 + A2 (T1–T6) under A6. Do not run any item of A4 (P1–P10). Do not implement the market. Do not modify any parameter, prediction, tolerance, or rule in the design; if one is ambiguous or impossible as written, stop and report the ambiguity with the two readings.

Rules.
1. Exactness: the simulator is event-driven with four event types, including deterministic activity shut-off deadlines refreshed on every conviction change (A1). A Gillespie step that jumps past a shut-off deadline is a bug, not an approximation.
2. Framing classes are integer identifiers assigned at angle creation; opposite rays share one identifier; no floating-point mod-90° recomputation.
3. Campaign pulses are prescribed-time impulses applied once to every cohort member, index order for coincident pulses, no clock events between coincident pulses.
4. Every reported number carries N, replicate count, random seeds, and the four error sources of A6 separated (Monte Carlo; finite-N bias across the N ladder; numerical error of the reference calculation; closure error where a closure is the reference).
5. Pass rule is A6: predeclared discrepancy δ (A4a for zero predictions); PASS / FAIL / INCONCLUSIVE with the replicate count needed to resolve an INCONCLUSIVE. No tuning after a FAIL. Bugs, algebraic errors in a prediction, and model failures are logged as distinct categories; corrections are versioned and original results retained.
6. The automaton (last framing, last outcome, table cos²(θ_j − θ_i)) and the Bloch-mean surrogate (anchor, receptivity, declared initial-anchor laws) are implemented as separate agent classes under the same engine; T6 registers the surrogate's predicted same-outcome fraction (1 + cos 2Δ·E[τ₁²])/2.
7. Reproducibility: code, configuration, seeds, raw outputs and the certified table in one archive, with a README that states the specification version, the design version, and every deviation found.

Deliverable. A certified table for T1–T6 (PASS/FAIL/INCONCLUSIVE per test with intervals and error budget), the reproducibility archive, and a list of any specification ambiguities encountered. Then stop.
