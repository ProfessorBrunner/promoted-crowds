# Stage 2B, task 2 — P4: an independent kinetic reference for the critical fraction

Specification: `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
Design: `crowd1_cs_design_and_manuscript_brief_v0_3.md`, Part A (A4 item P4).
Authorisation: Stage 2B, a discrepancy investigation, **not** a re-certification.
The Stage 2 P4 FAIL verdicts stand unchanged in the record. Nothing was tuned.

---

## 1. What was solved, and why it is independent

In the r = 1 aligned positive-target sector the framing counters are inert (the
deposit `α r^{n−1}` never changes), so the joint law collapses to a law on conviction
alone and the owner's equation applies verbatim:

```
  d/dt <psi, mu_t> = < -c psi'(c) + lambda A(t) [ psi(min{1, c+0.5}) - psi(c) ], mu_t >
  A(t) = mu_t((0.3, 1]),      mu_0 = (1-f) delta_0 + f delta_{0.5}
```

`kinetic.py` integrates this directly. It shares **no code** with the agent
simulator: there is no event queue, no random number generator, no agent, and no
`crowd1` import other than `predictions_s2` for the reference branch values it is
compared against. The two implementations have independent discretisations,
independent error mechanisms and independent authors' errors.

### 1.1 Discretisation, and why each piece is controlled

| Piece | Treatment | Error |
|---|---|---|
| Decay `ċ = −εc` | Work in `u = ln c`, where decay is uniform translation at speed ε. Tie the time step to the grid, `Δt = h/ε`. The transport step is then an **exact one-cell index shift** of the piecewise-constant-in-u measure. | **Zero.** No numerical diffusion from the drift at all. |
| Atom at `c = 0` | Tracked outside the grid; it has zero drift velocity, so it persists exactly. Mass leaving the bottom of the grid is pooled into it. | Position error ≤ `c_min = 10⁻³`, far below the threshold `c_b = 0.3`; such mass can only re-enter the active region via a jump, and a jump from anywhere below `c_min` lands within `10⁻³` of a jump from 0. |
| Jump deposition at `min(1, c+d)` | Conservative linear-in-`u` splitting onto the two neighbouring cells, with precomputed index/weight maps. Clipping at `c = 1` folds onto the top cell exactly. | O(h), measured below. |
| Two-or-more receipts in one step | The **exact pure-jump semigroup** `e^{−a} Σ_{k≤K} a^k J^k/k!` with `a = νΔt`, `K = 3`. A single-jump scheme would carry an O((νΔt)²) bias. | Mass deficit `P(>K jumps)`: **1.38 × 10⁻⁸** over the whole λ = 1.75, f = 0.20 validation run at h = 0.001 (and 9.7 × 10⁻¹⁴ on a run at the critical f, where the activity stays low); at K = 2 the same run loses 6.7 × 10⁻⁴, which is why K = 3 is used throughout. |
| Self-consistent coupling `ν(t) = λA(t)` | Heun (predictor–corrector) on the rate, not explicit Euler. | O(h²), subdominant. |
| Threshold cell | `A(t)` uses the exact fraction of the partial cell lying above `c_b`, not a cell-centre test. | O(h²) within the cell. |

### 1.2 Validation before use

The solver was validated against a reference computed by a *different method* — the
C2(b) stationary quadrature for `λ(ν) = ν/P_ν`, which is itself an independent
algebraic object:

| h (λ = 1.75) | A(T = 120) | error vs exact `A* = 0.74719371` |
|---|---|---|
| 0.008 | 0.74255783 | −4.636 × 10⁻³ |
| 0.004 | 0.74490155 | −2.292 × 10⁻³ |
| 0.002 | 0.74605217 | −1.142 × 10⁻³ |
| 0.001 | 0.74662385 | −5.699 × 10⁻⁴ |

Observed order in h: **1.016, 1.006, 1.002** — clean first order. Richardson
extrapolation of the two finest grids gives **0.7471955** against the exact
**0.7471937**, agreeing to **1.8 × 10⁻⁶**. The solver is correct.

---

## 2. The estimand, and how it was bracketed

```
  f_c^MF(lambda) = inf{ f : the mean-field trajectory from mu_0 ignites }
```

Decided by **classifying the full trajectory**, not by a time-t criterion. The
mean-field flow has exactly two attractors — `A = 0` and the upper branch
`A*(λ)` — separated by the unstable middle branch, whose activity at the saddle-node
is `A_fold = 0.375574`. So a trajectory is in the extinction basin once it is below
the fold activity **and still decreasing** (there is no attractor between the two),
and in the ignition basin once it is within half of `A*`. Anything else is reported
as **unclassified** and raises, rather than being forced into a basin; after the
classifier was corrected (see `BUGLOG.md`, S2B-1) no run was unclassified.

Bisection to a half-width of ≈ 4 × 10⁻⁷ in f, which is three orders of magnitude
below the grid uncertainty, so the bisection contributes nothing.

### 2.1 Refinement — the reported uncertainty is measured, not assumed

| λ | h = 0.008 | h = 0.004 | h = 0.002 | h = 0.001 | order in h | Richardson | uncertainty |
|---|---|---|---|---|---|---|---|
| 1.60 | 0.14032707 | 0.13648692 | 0.13460228 | 0.13366797 | 1.012 | **0.1327337** | 9.3 × 10⁻⁴ |
| 1.75 | 0.04801910 | 0.04604016 | 0.04506484 | 0.04458089 | 1.011 | **0.0440969** | 4.8 × 10⁻⁴ |
| 1.90 | 0.00921832 | 0.00814185 | 0.00761507 | 0.00735457 | 1.016 | **0.0070941** | 2.6 × 10⁻⁴ |

**Horizon refinement.** At h = 0.004 the bisected boundary is *identical to all eight
printed digits* at T = 120 and T = 240 (0.13648643 / 0.13648643, 0.04603973 /
0.04603973, 0.00814166 / 0.00814166). The basin boundary is a property of the flow,
not of the horizon, exactly as it should be. Horizon uncertainty: **0**.

These three figures are bisected from the *wide* starting bracket ([0.10, 0.20],
[0.02, 0.10], [0.002, 0.03]) so that T = 120 and T = 240 are compared under
identical conditions. The h-ladder of §2.1 re-brackets each rung around the
previous one and therefore lands on a slightly different point of the same
interval: at λ = 1.60, h = 0.004 it gives 0.13648692 against 0.13648643 here. The
4.9 × 10⁻⁷ gap is the bisection tolerance plus the bracket-endpoint shift — it was
reproduced exactly by re-running the current classifier from the wide bracket — and
is three orders of magnitude below the grid uncertainty. It is not a horizon effect
and not a change of answer.

The reported numerical uncertainty is therefore the grid term, 9.3 × 10⁻⁴,
4.8 × 10⁻⁴, 2.6 × 10⁻⁴ — in every case **smaller than the discrepancy under
investigation** (6.4 × 10⁻³, 5.8 × 10⁻³, 1.3 × 10⁻³), by factors of 6.9, 12.1 and 5.0.

---

## 3. Results

| λ | kinetic `f_c^MF` ± numerical | Stage 2 agent `f₅₀(10⁵, 160)` [bootstrap CI] | Appendix F | kinetic − Appendix F | kinetic − agent |
|---|---|---|---|---|---|
| 1.60 | **0.132734 ± 0.00093** | 0.133422 [0.132588, 0.134220] | 0.1270 ± 0.0020 | **+0.005734** | −0.000688 |
| 1.75 | **0.044097 ± 0.00048** | 0.043815 [0.043361, 0.044434] | 0.0380 ± 0.0010 | **+0.006097** | +0.000282 |
| 1.90 | **0.007094 ± 0.00026** | 0.007310 [0.006476, 0.007633] | 0.0086 ± 0.0008 | **−0.001506** | −0.000216 |

- The kinetic reference **overlaps the agent interval at all three λ**.
- The kinetic reference is **disjoint from Appendix F ± its stated error at all three
  λ**, and the sign of the disagreement is not even consistent (kinetic above
  Appendix F at λ = 1.60 and 1.75, below it at λ = 1.90).

### 3.1 Convergence argument linking `f₅₀(N, T)` to `f_c^MF`

The finite-N process is a mean-field jump process whose empirical measure converges
to the solution of the kinetic equation as N → ∞. For f above the basin boundary the
ignition probability therefore tends to 1 and below it to 0, so the 50 % crossing
point `f₅₀(N, T)` converges to `f_c^MF` once T exceeds the (N-independent) time for
the deterministic flow to commit to a basin — and §2.1 shows T = 120 already does,
since T = 240 gives the identical answer.

The residual at finite N is set by the fluctuation of the realised cohort size about
`fN`, of scale `√(f(1−f)/N)`:

| λ | `√(f(1−f)/N)` at N = 10⁵ | `f₅₀ − f_c^MF` | ratio |
|---|---|---|---|
| 1.60 | 1.07 × 10⁻³ | +6.88 × 10⁻⁴ | 0.64 |
| 1.75 | 6.49 × 10⁻⁴ | −2.82 × 10⁻⁴ | 0.43 |
| 1.90 | 2.65 × 10⁻⁴ | +2.16 × 10⁻⁴ | 0.82 |

Every offset is a sub-unity multiple of that scale, and of alternating sign — i.e.
consistent with finite-N noise about the mean-field boundary rather than with a
systematic bias. Independent corroboration: the Stage 2 N-ladder measured
`f₅₀` shifts of −0.000559, −0.000154, −0.000118 over N = 5 × 10⁴ → 2 × 10⁵, the same
magnitude and likewise an order of magnitude below the Appendix F discrepancies.

### 3.2 Does a `t = 40` criterion recover Appendix F? **No.**

Appendix F's `f_c` is described by the owner as simulation-derived under a `t = 40`
criterion. Applying exactly that criterion inside the mean-field solver — bisecting
on `A(40) > 1.5 A_u(λ)`, the Stage 2 ignition thresholds:

| λ | `A_u` | `1.5 A_u` | `f` at which `A(40)` crosses | `f_c^MF` (T → ∞) | Appendix F |
|---|---|---|---|---|---|
| 1.60 | 0.1408322 | 0.2112483 | 0.1346335 | 0.1327337 | 0.1270 |
| 1.75 | 0.0571127 | 0.0856691 | 0.0450736 | 0.0440969 | 0.0380 |
| 1.90 | 0.0121352 | 0.0182028 | 0.0076786 | 0.0070941 | 0.0086 |

The `t = 40` criterion moves the boundary by only +0.0019, +0.0010, +0.0006 — *away*
from Appendix F at λ = 1.60 and 1.75 and *towards* it at λ = 1.90, and in no case far
enough. A short horizon does not explain the registered values.

---

## 4. Category assignment

The Stage 2 BUGLOG left P4's category **UNDETERMINED** between **A** (algebraic or
numerical error in the registered prediction) and **M** (model failure), because
C9(b) was absent and no reference existed independent of the simulator. That
reference now exists.

> **Category A — error in the registered prediction.**

Grounds: an implementation sharing no code with the agent simulator, validated to
1.8 × 10⁻⁶ against a third and algebraically independent computation, with measured
first-order convergence, zero horizon sensitivity and a numerical uncertainty 5 to 12
times smaller than the discrepancy, reproduces the agent measurement at all three λ
and contradicts Appendix F at all three. Two independent computations of the model
agree with each other; the registered number disagrees with both. The model is not at
fault.

Consistent with the owner's own reclassification: **Appendix F's `f_c` values and the
0.75 prefactor are OPEN.** This investigation adds that the 0.75 prefactor cannot be
recovered from any of the quantities computed here — `f_c^MF / A_u` is 0.943, 0.772,
0.585 at the three λ and is not constant, so no single prefactor on `A_u` reproduces
either the registered or the computed critical fractions. Recovering the prefactor
requires Appendix F itself, which is not in this project.

Category **M** is not excluded *in principle* by this work — it is excluded *for this
endpoint*, because the disagreement is between the prediction and two concordant
computations of the model, not between the model and anything measured.

---

## 5. Files

- `kinetic.py` — the solver (no agent, no RNG, no event queue).
- `p4_reference.py` — estimand, basin classifier, bisection, refinement.
- `outputs/raw/p4_reference.json` — every bisection, both refinement ladders, orders,
  Richardson values and uncertainties.
- `outputs/raw/p4_t40_criterion.json` — the `t = 40` criterion test.
- `outputs/p4_comparison.csv` — the table of §3.
