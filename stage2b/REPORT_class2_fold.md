# Stage 2B addendum — the class-2 fold at α = 0.5, c_b = 0.3, ε = 1, r = 1

**Version 2, 2026-10-02.** Version 1 of this report is retained unaltered as artifact
version `e5c6bb2f-1178-4d55-9071-2b5b68c3f704`.

> **CORRECTION.** Version 1 concluded that the manuscript's A_fold = 0.375574 was
> wrong by 4.8× my numerical error. **That conclusion was mine and it was wrong.**
> All three manuscript figures are correct to their printed precision. The fault was
> an h-independent bias in my own measure-solver reference, from a conviction floor
> left at c_min = 10⁻³; the h-ladder cannot see a floor error, which is why the
> extrapolation looked converged and self-consistent. Logged as **BUGLOG S2B-4,
> category B** — implementation defect in a reference computation, not an error in
> the prediction and not a model failure. The referee report of 2026-10-02 prompted
> the re-derivation; its independently computed values are reproduced here exactly.

Specification: `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
Design: `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A.
Code: `stage2b/fold_exact.py` (this result); `stage2b/fold_solver_crosscheck.py`
(the §2 and §5 cross-checks); `stage2b/kinetic.py`,
`stage2b/p4_fold_kinetic.py`, `stage2b/p4_fold_finer.py` (the superseded solver route).
Raw: `stage2b/outputs/raw/fold_exact.json`,
`stage2b/outputs/raw/fold_solver_crosscheck.json`; superseded
`.../p4_fold_kinetic.json`.
Logs: `stage2b/outputs/logs/fold_exact.log`,
`.../fold_solver_crosscheck.log`, `.../p4_fold_kinetic.log`, `.../p4_fold_finer.log`.

**This is not a certification.** Design A4/A4a registers no prediction and no
tolerance for the fold location, so no verdict is issued.

## 1. Result

At r = 1 the stationary conviction marginal of Appendix C §C2 gives the activity
functional P_ν (C2.11–C2.14), and self-consistency is λ(ν) = ν/(M P_ν) with M = 1.
The fold of the class-2 (backward) branch is

    λ_fold = min_{ν>0} ν/P_ν ,    ν_f = argmin ,    A_fold = P_{ν_f} .

At α = 0.5 the dose is d = 0.5, so the method-of-steps representation C2.13 closes
after exactly **two steps** on (0,1):

    0 < c < d :   f_ν(c) = C c^{a-1}                                a = ν/ε
    d < c < 1 :   f_ν(c) = C c^{a-1} [1 − a J(c)],   J(c) = ∫_d^c u^{−a}(u−d)^{a−1} du

P_ν is therefore a two-dimensional quadrature with one integrable endpoint
singularity, and both singular factors are removed **exactly** by substitution
before any numerical rule is applied — (u−d)^{a−1}du under u = d + (c−d)s^{1/a},
and the residual t^a under t = y^{1/(a+1)}. What remains is smooth, so
Gauss-Legendre reaches machine precision.

| quantity | exact | numerical error | manuscript | deviation |
|---|---|---|---|---|
| λ_fold | **1.482508331** | 1.0e-11 | 1.48251 | -1.67e-06 |
| ν_f | **0.556791422** | 1.7e-09 | 0.556791 | +4.22e-07 |
| A_fold | **0.375573891** | 1.1e-09 | 0.375574 | -1.09e-07 |

Every deviation is the rounding of the manuscript's printed value. **Nothing
disagrees.** Fold identity: A_fold − ν_f/λ_fold = -5.55e-17.

Node ladder (convergence certificate, not an error estimate), ν_f at 100 / 200 /
400 / 800 / 1600 nodes: 0.556791435 / 0.556791433 / 0.556791421 / 0.556791424 /
0.556791422.

## 2. Two independent confirmations

Neither shares code with the quadrature of §1.

**The C2.16 small-ν series.** P_ν = νℓ + ν²(π²/12 − ℓ²/2) + o(ν²), ℓ = log(d/c_b).
Relative difference against the quadrature: −1.6×10⁻¹⁰ at ν = 10⁻⁵, −1.7×10⁻⁸ at
10⁻⁴, −1.7×10⁻⁶ at 10⁻³ — the o(ν²) remainder, scaling as ν³ exactly as it should.

**The measure solver, run with an adequate floor**
(`fold_solver_crosscheck.py`, check A). At fixed ν = ν_f with c_min = 10⁻⁵, the
solver's P_ν over h = 0.008 → 0.0005 has errors −1.634×10⁻³, −8.152×10⁻⁴,
−4.072×10⁻⁴, −2.035×10⁻⁴, −1.017×10⁻⁴ against the quadrature: clean first order,
difference ratios 2.008, 2.003, 2.002, Richardson limit 0.375573929, which agrees
with the exact 0.375573891 to **+3.883×10⁻⁸**. The solver is therefore correct; only
its floor setting was not.

## 3. Error accounting (design A6, four sources separated)

| source | λ_fold | ν_f | A_fold |
|---|---|---|---|
| Monte Carlo | not applicable — deterministic quadrature | — | — |
| finite-N | not applicable — mean-field limit | — | — |
| numerical | 1.0e-11 | 1.7e-09 | 1.1e-09 |
| closure | not applicable — C2.11–C2.14 are exact at r = 1 | — | — |

No seed enters; the computation is deterministic and reproduces bit for bit.

## 4. What v1 got wrong, and why the ladder did not reveal it

v1 obtained the fold by running a full Brent minimization of ν/P_ν inside the
measure solver at each of five grids h = 0.008 … 0.0005 and Richardson-extrapolating
the three minimizer outputs. The h-ladder was clean — difference ratios 1.90, 1.97,
1.99 for A_fold, observed order 1.0013 — and the three extrapolated numbers
satisfied the fold identity to 1.03×10⁻⁸. Every internal check passed.

They all passed because **every rung shared the same conviction floor**,
c_min = 10⁻³, and a floor error is independent of h. Refining h drives the
discretization error to zero and leaves the floor error untouched, so the sequence
converges — to the wrong limit — and the Richardson increment, which measures only
the h-component, reports a small and shrinking uncertainty. The fold identity is
likewise satisfied by the biased triple, because it is an identity of whatever
functional the solver is actually minimizing.

The amplification matters: the fold is the minimum of a flat function, so a small
level error in P_ν displaces the argmin by much more than itself. At h = 0.001 and
ν = ν_f the floor costs only +9.5×10⁻⁶ in P_ν, but it moves ν_f by 1.5×10⁻⁴.

## 5. Quantitative confirmation of the diagnosis

Re-running the minimization at a single grid h = 0.002 with the floor lowered
(`fold_solver_crosscheck.py`, check B):

| | ν_f | λ_fold | A_fold |
|---|---|---|---|
| c_min = 10⁻³ (as in v1) | 0.557657171 | 1.484154365 | 0.375740681 |
| c_min = 10⁻⁵ | 0.557509173 | 1.484117109 | 0.375650392 |
| shift from lowering the floor | −1.480×10⁻⁴ | −3.726×10⁻⁵ | −9.029×10⁻⁵ |
| v1 extrapolated **minus** exact | +1.496×10⁻⁴ | +3.725×10⁻⁵ | +9.149×10⁻⁵ |

The floor shift accounts for v1's residual in all three quantities — to three
significant figures in λ_fold, two in ν_f and A_fold. The truncation parameter
K = 3 is exonerated (check C): the spread of P_ν over K = 3, 6, 10 is
**9.4×10⁻¹¹** at both floors tested, eight orders of magnitude below the residual.

## 6. Lesson recorded

An h-ladder certifies only the h-component of a solver's error. Any parameter held
fixed across the ladder — a floor, a cutoff, a truncation order, a horizon — must get
its own ladder, or the extrapolation will report a confident and wrong uncertainty.
For this solver: K was laddered (and is harmless), the horizon was laddered (zero
sensitivity), c_min was **not**. It is now.
