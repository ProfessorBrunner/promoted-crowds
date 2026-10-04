# Stage 2B — ambiguities encountered

Stage 1 items 1–9 and Stage 2 items S2-1 onward are unchanged and still govern. This
file lists only what Stage 2B newly encountered. Nothing here modifies the
specification or the design; where a reading had to be chosen, both readings are
stated and the choice is declared.

---

## S2B-A1 — "invasion advantage": three different estimands fit the words

**Where** Design A4, item P1-delay.

**Reading 1 (frozen-background proxy)** Inject one seed into the saved
post-campaign state and hold every recipient fixed for the seed's life. This is what
Stage 2 implemented. Its between-order ratio is *exactly 1* at τ₀ = 0.

**Reading 2 (time-dependent first-generation count)** The same seed, but the
background relaxes while the seed is alive. This is the owner's Stage 2B estimand;
its ratio at τ₀ = 0 is 1.270.

**Reading 3 (stationary invasion operator)** The spectral radius `R_inv` of R7's
invasion operator on the *relaxed* background. This is the τ₀ → ∞ limit of both.

**Status** Resolved by the owner's Stage 2B instruction, which names reading 2 and
requires the Stage 2 quantity to be named a proxy. Both are reported under their own
names in `REPORT_task1_P1delay_audit.md`. The design text itself still does not
distinguish them and would benefit from naming one.

---

## S2B-A2 — the campaign pulse as "the first receipt" in the P4 initial law

**Where** The owner's Stage 2B statement, `μ₀ = (1 − f)δ₀ + f δ_{0.5}`, against the
specification's message transition.

**Question** Does the cohort member whose conviction is 0.5 at t = 0 carry framing
counter n = 0 or n = 1?

**Why it does not matter here** At r = 1 the counters are inert — the deposit
`α r^{n−1} = α` for every n — so the two readings give identical dynamics. The
solver uses one slab for exactly this reason, and this is what makes the owner's
counter-free equation an exact statement of the finite-N mean field rather than an
approximation. **The question becomes load-bearing at r < 1** and is resolved there
by the specification itself (step 2 increments the counter before step 3 deposits,
and step 3 uses `r^{n−1}` with the post-increment counter), which the P6 solver
follows.

**Status** No choice required for P4; recorded because the same initial law at r < 1
would require one.

---

## S2B-A3 — "half fold activity" for P6 case B is still undefined in this project

**Where** Design A4, item P6, case B: "exact Λ = 25.4 at half fold activity versus
bridge 20.35".

**Problem** Neither *fold activity* for case B nor the *bridge* construction appears
in A4 or anywhere in `review_packet_v0_6_1.md`, whose Appendix C and Appendix D both
stop at C6. The design cites C7, which is not a file in this project.

**Consequence for this work** The owner's Stage 2B instruction supplies the marker
directly (`A = 0.325`), so the reference could be computed without C7. But whether
0.325 *is* half case B's fold activity — i.e. whether case B's fold activity is
0.65 — cannot be checked, so case B remains BLOCKED for the purpose of a verdict even
though its Λ is now computed. The mean-field Λ at the supplied marker is
25.4285 ± 0.0134, consistent with the registered 25.4 at the three significant
figures in which 25.4 is stated.

**Status** Open; requires Appendix C7.

---

## S2B-A4 — "the crossing" is ambiguous between two estimands

**Where** Design A4, item P6; also P7 in the Stage 3 definitions.

**Two readings** The crossing time of the mean trajectory, or the mean over
replicates of the per-replicate crossing time. These are different functionals and
coincide only in the N → ∞ limit.

**Status** Resolved by the owner's Stage 2B instruction, which asks for both. Both
are now reported for case B; they differ by at most 2.5 × 10⁻⁴, i.e. 1.6 % of the
replicate standard deviation, at N = 10⁵. The Stage 2 tabulation was the mean of
replicate crossings. The same ambiguity is already handled explicitly in the owner's
Stage 3 definition of P7, which asks for per-replicate values with the
mean-trajectory versions beside them.

---

## S2B-A5 — Appendix F's 0.75 prefactor cannot be probed from inside this project

**Where** The owner's Stage 2B statement reclassifying Appendix F's `f_c` and its
0.75 prefactor as OPEN.

**Problem** Appendix F is not in this project, so the prefactor's referent is
unknown. This work can only report that no quantity it computed carries it:
`f_c^MF / A_u` = 0.9425, 0.7721, 0.5846 at λ = 1.60, 1.75, 1.90 and is not constant,
so no single prefactor on `A_u` reproduces either the registered or the computed
critical fractions.

**Status** Open; requires Appendix F.

---

## S2B-A6 — A6 mandates Holm across six endpoints but does not define an endpoint p-value

**Where** Design v0.3.1 A6: "Primary endpoints: P1, P1-delay, P2, P3, P4, P6;
secondary: the rest; a Holm correction across primary endpoints." Also the A4b
tolerance note: "Holm correction across the Stage 2 primary endpoints only."

**Problem** Each primary endpoint carries several rows (P1 9, P1-delay 3, P2 8, P3 7,
P4 7, P6 1), each with its own equivalence-test p-value. A6 says to Holm-correct
across the six endpoints but is silent on how the six input p-values are formed.
Stage 2 took each endpoint's p to be the **minimum over its rows**
(`run_stage2.py:132`, `ep_p.append(min(ps) if ps else 1.0)`). The minimum of m
p-values is not itself a valid p-value — under independent uniform nulls
P{min p ≤ u} = 1 − (1−u)^m > u — so the multiplicity inside each endpoint is never
corrected, and Holm's family-level guarantee requires valid inputs. The referee
report of 2026-10-02 (item 3) raises exactly this.

**The two readings, both computed**

| endpoint | rows | reading A: p = min over rows (as run) | Holm A | reading B: p = min(1, m·p_min) | Holm B |
|---|---|---|---|---|---|
| P1 | 9 | 1 | 1 | 1 | 1 |
| P1-delay | 3 | 0.878411 | 1 | 1 | 1 |
| P2 | 8 | 1 | 1 | 1 | 1 |
| P3 | 7 | 1 | 1 | 1 | 1 |
| P4 | 7 | 3.62479e-26 | 2.17487e-25 | 2.53735e-25 | 1.52241e-24 |
| P6 | 1 | 1 | 1 | 1 | 1 |

Reading B is the Bonferroni-adjusted minimum, which is a valid endpoint p-value and
is what the referee suggests as one of two repairs (the other being Holm across all
35 individual tests).

**Effect on the Stage 2 conclusion: none.** P4 is the only endpoint that rejects
under either reading, every other adjusted p is exactly 1 under both, and P4's
adjusted p moves from 2.17×10⁻²⁵ to 1.52×10⁻²⁴ — seven times larger and still
twenty-three orders of magnitude below 0.05. The pass/fail record and the Holm
selection are unchanged. Only the quoted adjusted p-value differs.

**Status** **RULED by the owner, 2026-10-02: reading B** — Bonferroni-adjust the
minimum row p-value within each endpoint, then Holm across the six. The quoted
family-level figure for P4 is therefore **1.52×10⁻²⁴**, superseding 2.17×10⁻²⁵. Both
readings are carried in the ledger (stage "Stage 2", item "A6 multiple testing"),
reading A labelled as superseded. The Holm selection is unchanged — P4 only — and no
number in any certified table changes.

---

## S2B-A7 — A6 is silent on whether pilot replicates are pooled into the final estimate

**Where** Design A6's replicate accounting, and the Stage 2/Stage 3 adaptive
extension of replicate counts (`stage2_items.py:172`, `:360`:
`need = min(max(need, pilot), cap)`).

**Problem** Several items ran a pilot of 50 replicates, used it to decide whether and
how far to extend, and then reported statistics over the **full** set including the
pilot. The replicate count is fixed before each run in the sense that `need` is
computed and then that many replicates are drawn — but `need` itself is a function of
the pilot, so the final sample size is data-dependent. Fixed-sample Wilson and
t-intervals do not automatically retain nominal coverage under such a design. A6
specifies neither the sample-size rule nor whether the pilot is pooled, and it
prescribes fixed-sample intervals without a coverage condition.

**What this work did** Pooled the pilot, used fixed-sample intervals, and reported
every replicate count explicitly beside every number, including the cells where the
precision target was not met (`meets_0p03_target` / `meets_0p02_target` flags in the
raw JSON and in `figures/data/F2_outbreak_probability.csv`).

**Status** **RULED by the owner, 2026-10-02: disclose as run.** The design is
recorded in the ledger (stage "Stage 2", item "A6 sampling design"): pilot of 50
extended by `need = min(max(need, pilot), cap)`, **pilot pooled** into every reported
estimate, fixed-sample Wilson and t intervals throughout, and **coverage under the
realized adaptive design not assessed**. No number changes; nothing is re-estimated
and no interval is widened.

**Scope of the rule.** The **N = 10⁶ diagnostic cells at λ = 2 are outside the
adaptive rule entirely**: they ran a **fixed 50-replicate design**, not piloted and
not extended, so no precision target applies and they carry no `meets_*_target` flag.
Applying the rule to their realised 18/50 would have asked for
⌈(1.96/0.03)² × 0.36 × 0.64⌉ = 984 replicates; 50 were run, and the resulting Wilson
interval is correspondingly wide ([0.2414, 0.4986], half-width 0.1286). That is a
property of the fixed design, not a failure of the adaptive one.
