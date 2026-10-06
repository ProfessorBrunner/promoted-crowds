# Stage 2B — bug log

Categories, as in Stage 1 and Stage 2, kept distinct:
**B** harness/code bug · **A** algebraic or numerical error in a registered
prediction · **M** model failure · **E** estimand mismatch (new in Stage 2B).

Originals are retained; corrections are versioned. No Stage 1 or Stage 2 verdict is
altered by anything in this file.

---

## S2B-1 — [B] basin classifier rejected a legitimately dying trajectory

**Where** `p4_reference.py::classify`, first version.

**What** The classifier labelled a trajectory `die` only if `A(T) < 10⁻⁶`. At
λ = 1.60, T = 60, a trajectory at the boundary had `A(T) = 1.118 × 10⁻⁶` — on its
way to zero but not yet below the cut — and was labelled `unclassified`, aborting the
bisection. A second abort followed at T = 60 with `A(T) = 0.164`, a trajectory still
climbing through the fold region at a horizon too short to classify at all.

**Why it was wrong** The cut was an arbitrary absolute number, not a statement about
the flow.

**Fix** The classifier now uses the structure of the mean-field flow, which has
exactly two attractors separated by the unstable middle branch: `die` iff
`A(T) < ½ A_fold` **and** `A(T) ≤ A(T − Δt)` (below the fold activity and still
decreasing — there is no attractor in between), `ignite` iff `A(T) > ½ A*(λ)`,
`unclassified` otherwise, which raises. The T = 60 horizon was dropped from the
refinement ladder because 60 time units is genuinely too short for the flow to commit
near the boundary; T = 120 and T = 240 are used instead and give identical answers
to eight digits.

**Effect on results** None that survives. The aborted runs produced no numbers. The
re-run with the corrected classifier reproduced the h = 0.008 and h = 0.004 values
from the first (λ = 1.60: 0.14032707 both times; 0.13648643 → 0.13648692, the
4.9 × 10⁻⁷ difference being the re-bracketing, which is below the 4.2 × 10⁻⁷
bisection half-width plus the bracket-endpoint shift and three orders of magnitude
below the grid uncertainty).

---

## S2B-2 — [E] estimand mismatch, P1-delay (not a bug, logged as a distinct category)

**What** The Stage 2 P1-delay row measured a **frozen-background proxy**
`E Z₁^frozen(τ₀) = λ L q_T(τ₀)` — recipients' orientations *and* convictions held at
their post-campaign values for the whole of the seed's life — and compared it to a
registered sentence ("the order advantage is present at every delay") that is a claim
about the **time-dependent** first-generation count
`E Z₁(τ₀) = λ ∫₀^L q_T(τ₀ + s) ds`.

**Why the proxy cannot see the effect** At τ₀ = 0 the proxy's between-order ratio is
**exactly 1**, because from initial law I2 the maximally mixed orientation law is
invariant under every projection (R8(b)), so `E[cos²φ_post] = ½` for *both* campaign
orders and the frozen orientation channel carries no order information whatsoever.
The whole advantage lives in the stance channel and only resets can express it.

**Classification** Not **B**: the code computes its own definition bit-for-bit
reproducibly. Not **M**: the process behaves as specified. **E**.

**Effect on results** The Stage 2 INCONCLUSIVE verdict stands unchanged in the
record. Task 1 reports both quantities under their own names; the replacement wording
for the registered sentence is proposed, not adopted (the design is authoritative).

---

## S2B-3 — [A] P4 category resolved

Stage 2 left P4's discrepancy category **UNDETERMINED** between **A** and **M** for
want of a reference independent of the agent simulator. Task 2 supplies one. It
agrees with the agent measurement at all three λ and is disjoint from Appendix F at
all three. Category assigned: **A**. See `REPORT_task2_P4_kinetic.md` §4. The Stage 2
FAIL verdicts stand unchanged.

---

## S2B-4 — [B] class-2 fold reference biased by an unladdered conviction floor

**Where** `p4_fold_kinetic.py` / `p4_fold_finer.py`, module constant `C_MIN = 1e-3`,
passed to `kinetic.solve` at every rung of the h-ladder.

**What** The fold was obtained by running a full Brent minimization of ν/P_ν inside
the measure solver at h = 0.008, 0.004, 0.002, 0.001, 0.0005 and
Richardson-extrapolating the minimizer outputs. Reported:
λ_fold = 1.482545582 ± 4.02×10⁻⁴, ν_f = 0.556941032 ± 1.79×10⁻⁴,
A_fold = 0.375665378 ± 1.90×10⁻⁵, with the conclusion that the manuscript's
A_fold = 0.375574 was wrong by 4.82× the numerical error.

**Why it was wrong** The conviction floor c_min was held at 10⁻³ on every rung. A
floor error is **independent of h**, so refining h removed the discretization error
and left the floor error intact: the sequence converged to a biased limit, and the
Richardson increment — which measures only the h-component — reported a small and
shrinking uncertainty for it. The fold identity A_fold = ν_f/λ_fold was satisfied to
1.03×10⁻⁸ because it is an identity of whatever functional is actually being
minimized. Every internal check therefore passed on a wrong answer. The fold is the
minimum of a flat function, which amplifies the fault: at h = 0.001 the floor costs
+9.5×10⁻⁶ in P_ν but displaces ν_f by 1.5×10⁻⁴.

**Fix** The fold is now computed from the **exact** stationary law. At α = 0.5 the
dose is d = 0.5, so C2.13 closes after two steps and P_ν is a quadrature whose
singular factors are removed in closed form; `stage2b/fold_exact.py`. Confirmed
against the independent C2.16 small-ν series (relative −1.6×10⁻¹⁰ at ν = 10⁻⁵) and
against the measure solver itself once the floor is lowered to 10⁻⁵, which
Richardson-extrapolates to the exact value to +3.883×10⁻⁸. The solver is correct;
only its floor setting was not. K = 3 is exonerated — the spread of P_ν over
K = 3, 6, 10 is 9.4×10⁻¹¹. The two solver-side cross-checks and the floor-sensitivity
table are reproducible from `stage2b/fold_solver_crosscheck.py` →
`outputs/raw/fold_solver_crosscheck.json`, log
`outputs/logs/fold_solver_crosscheck.log`; `fold_exact.py` supplies only the exact
quadrature.

**Effect on results** The three reported numbers are corrected to
λ_fold = 1.482508331, ν_f = 0.556791422, A_fold = 0.375573891, numerical error
≈ 2×10⁻⁹. **All three manuscript figures are correct to their printed precision and
the v1 finding against A_fold is withdrawn.** No certified Stage 1/2/2B/3 verdict
depends on the fold: it is used nowhere in a pass rule. The fold enters only
(a) these three reported-without-verdict ledger rows and (b) the λ_fold marker on
Figure 3, both corrected. The superseded values and their ladder are retained in
`outputs/raw/p4_fold_kinetic.json` and in artifact version
`e5c6bb2f-1178-4d55-9071-2b5b68c3f704` of the report.

**How it was caught** Not by me. The referee report of 2026-10-02 (item 2)
independently evaluated the stationary law and obtained the manuscript's values; that
disagreement with two independent sources prompted the exact re-derivation. My own
v1 report had stated the disagreement plainly and had not widened its error bar to
cover it, which is what made the conflict legible — but it attributed the fault to
the manuscript rather than testing its own unladdered parameters.

**Lesson** An h-ladder certifies only the h-component of a solver's error. Any
parameter held fixed across a ladder — floor, cutoff, truncation order, horizon —
needs its own ladder, or the extrapolation reports a confident wrong uncertainty.

**Addendum, 2026-10-02.** `stage2/crowd1/predictions_s2.py::p4_fold()` has returned
the exact values since Stage 2 — lambda_fold = 1.482508331458303,
nu = 0.5567914347613716, A_fold = 0.3755738992803306, from the same C2.11-C2.14
method of steps — and the P4 basin classifier calls it for its 1/2 A_fold threshold,
so the f_c classification never used a wrong fold. One comparison against a function
already in this repository would have caught S2B-4 immediately. Second lesson, then:
before believing a new reference's disagreement with the manuscript, check it against
every independent implementation already in the project.

**Follow-up** All five certified kinetic references were floor-audited at the owner's
request; see `REPORT_floor_audit.md` and `outputs/raw/floor_audit.json`. The P4 f_c^MF
values and P6 case B's t* and Lambda* are corrected; case A's t_dagger is **neither
corrected nor bounded** — the matched 1e-2 -> 1e-4 shift is measured at +1.371e-4 but
the production step 2e-2 -> 1e-2 is not quantified, so **no bound on its floor error
is claimed** — and **no verdict changes**. The audit also found a confound worth recording: changing
c_min changes U = -log c_min and hence the adjusted h = U/round(U/h), so a naive
floor comparison at one requested h compares two different actual h — for case A that
confound is ten times the floor effect and of opposite sign. Floor comparisons must be
done at matched adjusted h (c_min = 1e-2 against 1e-4 gives J and 2J exactly).

---

## Non-defects encountered

- `concurrent.futures.ProcessPoolExecutor` raises `PermissionError` on
  `SC_SEM_NSEMS_MAX` in this sandbox. Switched to
  `multiprocessing.get_context("spawn").Pool`, which is what Stage 1 and Stage 2
  already used. No scientific content affected.
- The first `p6_reference.py` launch was dispatched before that change and aborted in
  part (c) after parts (a) and (b) had printed. The script was made restartable with
  per-part saving and re-run end to end; all reported numbers come from the complete
  re-run.

---

## S2B-CS1 — [B] off-by-one in the method-of-steps recursion below d = 1/2

**Where** `stage2b/dose_mixture_fold.py::P_stat`, the `k >= 2` branch.

**What** For `u` in step k's interval `[kd, (k+1)d]`, the retarded argument
`v = u - d` lies in step **k-1**'s interval `[(k-1)d, kd]`. The code normalised
`v` against `(k-2)d` and interpolated `A_nodes[k-2]`, evaluating the previous
step's solution on the wrong interval.

**Why it survived validation** The branch is reachable only when
`K = ceil(1/d) >= 3`, i.e. `d < 1/2`. Every check run against it lay at
`d >= 1/2`, where `k` never exceeds 1: the `d >= 1` closed form `1 - c_b^a`,
`fold_exact.py::P_nu_exact` at `d = 0.5`, and
`stage2/crowd1/predictions_s2.py::P_nu`, which asserts `d >= 0.5`. The
continuity checks across `d = 1/2` and `d = 1/3` also passed, because just below
`d = 1/2` the third step has width `1 - 2d -> 0` and carries negligible mass;
the error grows smoothly as d falls.

**Detection** Two independent references at `c_b = 0.5`, agreeing with each other
and not with the quadrature: the manuscript D.3 measure solver
(`kinetic.solve`, `r = 1`, `f = 0`, `nu` prescribed) on an h ladder with
`c_min = 1e-5`, and a direct single-agent event-driven Monte Carlo of 10^6
agents. The discrepancy grew from `1.0e-5` at `d = 0.45` to `0.12` at
`d = 0.25`, while the solver's own refinement error stayed at `5.1e-4`.

**Fix** Index `k-1`, normalising against `(k-1)d`.

**Effect on results** After the fix the quadrature agrees with the solver's
Richardson limit to `<= 2.2e-6` over `d` in {0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
0.60} x `nu` in {1.70, 1.90, 2.10, 2.30, 2.45}, inside the solver's own
refinement error, and all three Monte Carlo 95% intervals contain it; the
`d >= 1/2` values are bit-unchanged. The P6 case-A dose-mixture fold moves from

    A_f 0.5647472640328673   H_f 157.41933016681764   t_ad,f 65.84387955279966
to
    A_f 0.5603318621202521   H_f 158.35440293993315   t_ad,f 66.30914996690508

which reproduces Appendix E C7(c)'s `A_f = 0.5603318`, `H_f = 158.354403`,
`t_ad,f = 66.30915` to `6.2e-8`. **The reported disagreement between CS and the
manuscript on the dose-mixture fold is withdrawn: it was this bug.** The
counter-offset hypothesis was also run on the buggy quadrature; re-run clean it
still does not reproduce the manuscript (offset 0 gives `A_f 0.5602859709`,
`H_f 159.3455527`, `t_ad,f 66.7141526`), so that conclusion stands but its stated
magnitudes are superseded.

**Superseded files, all retained**
`outputs/raw/dose_mixture_fold_caseA.json`,
`outputs/raw/dose_mixture_fold_caseA_offset0.json`,
`outputs/raw/caseA_fold_variants.json`, and
`outputs/raw/caseA_tdagger_at_cs_fold.json`, which measured the kinetic and
agent crossing times at the wrong level `A = 0.5647472640328673`. Corrections:
`outputs/raw/caseA_fold_v2.json`, `outputs/raw/caseA_fold_measure_solver.json`,
and `outputs/raw/pnu_independent_check.json` (post-fix; the pre-fix record is
kept as `outputs/raw/pnu_independent_check_prefix_S2B-CS1.json`).

**Not affected** No figure, no manuscript value, no Stage 1 or Stage 2 verdict.
`figures/data/F3_marks.json` was left on the manuscript value throughout, which
the correction now confirms as right.
