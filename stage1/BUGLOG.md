# CROWD-1 Stage 1 — bug / error log

Design A6: *"Implementation bugs, algebraic errors in a prediction, and model
failures are logged as distinct categories, corrected in versioned reruns with the
original results retained."*

Categories used here, kept distinct:

| code | category |
|---|---|
| **S** | simulator bug — the engine does not implement specification v0.6 |
| **H** | harness bug — the test driver, a declared test criterion, or the reporting is wrong; the engine is correct |
| **A** | algebraic error in a prediction of the design or an appendix |
| **M** | model failure — the engine is correct, the prediction is correct, and they disagree |

Nothing in categories **S**, **A** or **M** was found in Stage 1.

---

## B1 — category H (harness) — archive v1 → v2

**Row affected.** `T4 A5 control: automaton reproduces the process joint law`
(certified table row 103 of archive v1). Verdict in v1: **FAIL**, measured
discrepancy 1.3635×10⁻³ against a declared δ = 0.

**Defect.** Two independent faults in the same declared row, both in this harness:

1. The row declared a **zero tolerance on a Monte-Carlo-estimated** quantity (the
   total-variation distance between two 4-cell outcome laws). No finite sample can
   satisfy a zero tolerance on an estimated distance, so the row was unsatisfiable
   by construction regardless of the engine's behaviour.
2. The row's name asserts a **pathwise** comparison, but the two arms it compared
   were the `agent_class="process"` and `agent_class="automaton"` cells of the T4
   grid, which the grid gives **different derived seeds** (e.g. for
   (Δ=30°, order 1, I1): process seed `17722805604446409615`, automaton seed
   `6415845976841894337`). They are therefore two independent samples of the same
   law, not the same path.

**Evidence that this is H and not S, A or M.** The v1 run itself corroborates the A5
prediction: over the 30 (Δ, order, initial law) cells the two arms differ by
total-variation distances of 9.40×10⁻⁵ to 1.36×10⁻³ at 2×10⁶ agents per arm, against
a sampling scale of 5.6×10⁻⁴, and the 30 two-sample chi-square p-values are spread
uniformly over [0.023, 0.962] — the signature of two samples from one law, with no
excess of small p-values. Independently, all 60 T4 identity rows and all 40 T6 rows
of the same run PASS, including the 30 automaton rows, which test the automaton's own
measured P(AA)+P(RR) against cos²Δ at δ = 3/√N.

**Correction (v2).** The A5 row is replaced by the pathwise criterion the control
actually asserts: the process and the automaton are run on **the same seed** over all
30 cells (5 shared-seed pairs per cell) and required to agree **agent by agent** in
the outcome pair of both pulses, the final conviction, the stance and the full
counter vector. That criterion is exact, so δ = 0 is attainable; the justification is
structural — the automaton's state (last framing, last outcome) is a
re-coordinatization of the orientation φ (after accepting θ the orientation is θ,
after rejecting it is θ + 90°), so its acceptance probability is identical message by
message. The independent-seed comparison is retained in full as a reported
diagnostic **with no verdict**, which is the correct status for a
Monte-Carlo-estimated distance.

**What was NOT changed.** No parameter, prediction, tolerance or rule of design v0.3
or specification v0.6 was altered. The design sets no tolerance for the A5 control;
the quantity corrected is a criterion this harness declared for itself. Nothing in
`crowd1/engine.py`, `crowd1/angles.py`, `crowd1/rng.py` or `crowd1/predictions.py`
was touched, and no run of T1, T2, T3, T5 or any T4/T6 identity row was re-declared:
every other row of v2 is the same row, with the same seed, as in v1.

**Retained original.** `outputs_v1/` with `outputs_v1/README_v1.txt`.

---

## B2 — category H (harness, reporting only) — archive v2 → v3

**Rows affected.** The `note` field of **four** rows — the T1.2 and T1.3 rows of both
cells:
`T1.2 cell A: first active interval >= L (pathwise)`,
`T1.3 cell A: no activity after L_+ (pathwise)`,
`T1.2 cell B: first active interval >= L (pathwise)`,
`T1.3 cell B: no activity after L_+ (pathwise)`.

**Defect.** The T1.2 note read *"violations out of 2550000 activated-agent
intervals"*. 2 550 000 is the total number of **agents simulated** across the N ladder
(50×10³ + 50×10⁴ + 20×10⁵), not the number that ever activated. The number that
activated is 2 154 164 in cell A and 1 922 628 in cell B — the ladder's reach-weighted
final sizes. The T1.3 note carried no denominator at all, so the same count was added
there. Found on read-back of the v2 certified table against `outputs/raw/t1.4.csv`.

**Scope.** Reporting text only. The verdict (zero violations), the measured value,
the interval, δ and all four error sources are unaffected on all four rows, and the
remaining **120** of the 124 rows are byte-identical to v2.
No code in `engine.py`, `angles.py`, `rng.py`, `predictions.py` or `a6.py` was
touched, and no seed changed; v3 reproduces v2 numerically, the run being
deterministic from master seed `20261001`.

**Correction (v3).** `crowd1/tests.py` now carries the activated count per cell and
both notes report *"violations out of N_act first-active intervals (agents that ever
activated, out of 2550000 agents simulated)"*; the T1.3 note gained the same
denominator.

**Retained original.** `outputs_v2/` with `outputs_v2/README_v2.txt`.

---

## Non-defects, recorded so they are not re-litigated

- **`scipy.stats.chi2_contingency` raised on a structurally zero column.** At
  Δ with q₁ = 1 (I1, order 1) the first pulse is accepted with probability 1, so the
  RA and RR cells are empty in both arms and the expected-frequency table has a zero
  element. The contingency test is undefined there, not wrong: the comparison is now
  restricted to cells with positive total count, and the degenerate case is reported
  as such. Found during v1→v2 development, before any certified run.
- **The surrogate cannot be run at ρ > 0 or κ > 0.** `runner.run_one` raises
  `NotImplementedError` rather than inventing an (a, τ) reset rule the specification
  does not declare. This is deliberate; see AMBIGUITIES.md item 8.
