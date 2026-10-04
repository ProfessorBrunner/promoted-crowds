# CROWD-1 Stage 3, item P9 — two-camp fixed points

**Specification** `review_packet_v0_6_1.md`, "PROCESS SPECIFICATION v0.6"; result R9.
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A, item P9.
**Reference** Appendix C §C4 (C4.1–C4.2 for F, C4.6 for the fixed-point system,
C4.7 for the branch parametrization, C4.10–C4.11 for stability).
**Authorised** 2026-10-01; threshold c_b ruled 2026-10-02 (see §1.1).

**Result: 18 registered rows, 18 PASS, 0 FAIL, 0 INCONCLUSIVE.** Nothing was tuned.
Master seed **20261005**, N = 10⁵, 50 replicates per cell.

---

## 1. Parameters

FIXED by A4: r = 1, κ = 0, α = 1, β = 0.4, M₊ = M₋ = ½, λ ∈ {1.5, 2, 3}, ε = 1.
FIXED by the owner: camps at c = ±0.6 with stances aligned; perturbations ±0.05 in
each A_±; relaxation |ΔA| < 10⁻³ over 10/ε; δ = 5 %.
RULED: **c_b = 0.3**.
DECLARED: c_h = 0.01 and ρ = 0, both verified immaterial (§2.3); burn-in to 50/ε,
measurement window [50, 100], N = 10⁵, 50 replicates.

### 1.1 Why c_b had to be ruled rather than declared

A4 does not give c_b for P9, and the value is load-bearing rather than cosmetic.
With β = 0.4, whether **one** rejected message can activate an agent from rest
depends on whether c_b sits below or above 0.4, and that decides which registered λ
have a positive two-camp branch at all:

- **c_b = 0.5** — β < c_b, so a single rejection lands at 0.4 and does *not*
  activate; F(u, v) ≈ u·ln(1/c_b) at small rates. The zero branch is stable for
  λ < 2/ln 2 = 2.885, so **λ = 1.5 and λ = 2 have no positive fixed point at all**
  and only λ = 3 does, at A₊ = A₋ = 0.385368902.
- **c_b = 0.3** — β > c_b, so one rejection does activate; the onset is forward for
  λ > 1.341 and all three λ carry a positive stable branch.

Both readings were computed and put to the owner, who ruled **c_b = 0.3**, matching
P4, the project's other r = 1 item. The declared initial convictions ±0.6 are active
under either reading.

---

## 2. The reference: C4.7, recomputed independently

### 2.1 Construction

At α = 1 the α-term of C4.1 never fires in the interior (y > 1 is impossible on
[0, 1]), so with g = y f and a = (u+v)/ε the stationary equation is a delay ODE with
delay β, solved by the method of steps:

```
  g(y) = C y^a                                                    0 <= y <= beta
  g(y) = y^a [ C - (v/eps) int_beta^y t^-a g(t-beta)/(t-beta) dt ]      y > beta
```

The integrand carries an algebraic singularity (t−β)^(a−1) at t = β. The
substitution t = β + M w^(1/a) with M = y − β removes it **exactly**, because
s^(a−1) ds = (M^a/a) dw, leaving a smooth integrand on [0, 1] for Gauss–Legendre.

### 2.2 Three checks run before any fixed point was reported

| check | result |
|---|---|
| **v → 0 closed form.** With v = 0 the process is "reset to 1 at rate u, then decay", so F = 1 − c_b^(u/ε) exactly | agrees to **≤ 2.0 × 10⁻¹³** at u = 0.3, 0.8, 1.5, 3.0 |
| **C4.2 clipped-arrival flux.** This is the interior equation integrated over (0,1) plus normalization, so it must hold identically — it is a test of the quadrature, not of the model | relative error **≤ 9.3 × 10⁻⁸** over four (u, v) pairs, and 3.4 × 10⁻¹⁶ at the symmetric point |
| **Node refinement** on F(2.0, 1.2) at 50/100/200/400 nodes | last step **7.0 × 10⁻⁹** |

### 2.3 The camps are fixed — verified, not assumed

C4.1 requires an invariant two-camp law. Two facts make it exact here, and both were
checked on every replicate rather than argued:

- **Conviction never changes sign.** A positive agent's deposits are +α (accepted T)
  and +β (rejected T⊥ — `r⁰·cos 180°·(−β) = +0.4`), both positive. Measured: **0
  stance flips** over 150 replicates × 10⁵ agents.
- **Orientation is invariant.** A positive agent rejecting a T⊥ message moves to
  90° + 90° = 180° ≡ 0°, i.e. back to T₊. Measured: **0 agents off {T₊, T₋}**.

So c_h is immaterial (no stance can flip for any c_h ∈ [0, c_b)) and ρ is immaterial
(a reset sends φ to T_s, which it already equals) — exactly C4.1's "reset is harmless
under this declaration".

### 2.4 Fixed points and stability

| λ | A₊ = A₋ (C4.7) | A_total | C4.6 residual | spr(J) (C4.10/C4.11) | asymmetric branch? |
|---|---|---|---|---|---|
| 1.5 | 0.299028897 | 0.598057794 | 0 | 0.705757 | none |
| 2.0 | 0.423895616 | 0.847791232 | 5.6 × 10⁻¹⁷ | 0.378207 | none |
| 3.0 | 0.483041685 | 0.966083371 | 2.5 × 10⁻¹⁴ | 0.126822 | none |

**Branch selected: the C4.7 symmetric branch z = ½**, which at p = ½ is the unique
positive branch — a C4.7 z-scan over 25 points of (0, ½) found **0 interior sign
changes** of the consistency residual at every λ, so no asymmetric branch exists to
compete. All three are linearly stable by C4.11 (spr(J) < 1). J is symmetric with
equal diagonals, as the ± symmetry requires.

---

## 3. Results

### 3.1 Measured (A₊, A₋) against C4.7, δ = 5 %

| λ | A₊ measured | A₋ measured | C4.7 | diff A₊ | diff A₋ | δ |
|---|---|---|---|---|---|---|
| 1.5 | 0.29897799 | 0.29907519 | 0.299028897 | −5.09 × 10⁻⁵ | +4.63 × 10⁻⁵ | ±0.0150 |
| 2.0 | 0.42358442 | 0.42421501 | 0.423895616 | −3.11 × 10⁻⁴ | +3.19 × 10⁻⁴ | ±0.0212 |
| 3.0 | 0.48288782 | 0.48318623 | 0.483041685 | −1.54 × 10⁻⁴ | +1.45 × 10⁻⁴ | ±0.0242 |

All six PASS. The two camps straddle the prediction in every cell, with the A₊ and A₋
deviations equal and opposite to within Monte-Carlo error — the ± symmetry is
reproduced, not imposed.

### 3.2 Stability of the kinetic dynamics

Ten of the twelve perturbations are feasible; all ten relax. **The criterion is
evaluated on the replicate mean, and that choice is forced**: the stationary
single-replicate standard deviation of A₊ at N = 10⁵ is 1.01 × 10⁻³ to
1.44 × 10⁻³, so |ΔA| < 10⁻³ is *below the single-replicate noise floor* and cannot be
met pathwise even at perfect equilibrium. On the replicate mean the standard error is
≈ 1.8 × 10⁻⁴ and the criterion is resolvable.

| λ | perturbation | achieved shift | mean ΔA at t = 10 | single replicates inside 10⁻³ |
|---|---|---|---|---|
| 1.5 | A₊ + 0.05 | +0.0500 | +2.08 × 10⁻⁴ | 13/50 |
| 1.5 | A₊ − 0.05 | −0.0500 | +2.82 × 10⁻⁴ | 13/50 |
| 1.5 | A₋ + 0.05 | +0.0500 | +1.84 × 10⁻⁴ | 11/50 |
| 1.5 | A₋ − 0.05 | −0.0500 | −3.48 × 10⁻⁴ | 12/50 |
| 2.0 | A₊ ± 0.05 | ±0.0500 | −1.28 × 10⁻⁴, −4.60 × 10⁻⁵ | 28/50, 26/50 |
| 2.0 | A₋ ± 0.05 | ±0.0500 | −1.51 × 10⁻⁴, −6.08 × 10⁻⁵ | 27/50, 28/50 |
| 3.0 | A₊ − 0.05 | −0.0500 | +1.88 × 10⁻⁴ | 47/50 |
| 3.0 | A₋ − 0.05 | −0.0500 | +8.80 × 10⁻⁵ | 50/50 |

All ten PASS. The residual deviation **orders with spr(J)**: largest at λ = 1.5
(spr = 0.706, slowest relaxation, max single-replicate |ΔA| 4.98 × 10⁻³), smallest at
λ = 3 (spr = 0.127, 8.83 × 10⁻⁴). That ordering is an independent corroboration of
the C4.10 susceptibility matrix, since nothing in the simulation knows spr(J).

**Two perturbations are infeasible and no verdict is issued on them.** At λ = 3,
A₊ = 0.483 against a camp mass of 0.5, so only **0.0171** of the population is
inactive in each camp — fewer than the 0.05 needed to move A₊ up across the
threshold. This is a property of the branch, not a run failure: the +0.05
perturbation does not exist at λ = 3. The −0.05 perturbations at λ = 3 are feasible
and both relax, so stability is still tested from one side at every λ.

### 3.3 A6's four error sources, separated

| source | A₊ | A₋ |
|---|---|---|
| 1. Monte Carlo (Student-t, 50 replicates) | 2.86 × 10⁻⁴ to 4.13 × 10⁻⁴ | same range |
| 2. Finite-N bias (ladder N = 2.5 × 10⁴ … 2 × 10⁵, 1/N extrapolation) | 1.12 × 10⁻⁸ | 5.94 × 10⁻⁵ |
| 3. Numerical error of the C4.7 quadrature | 7 × 10⁻⁹ (node refinement) | same |
| 4. Closure error | **not applicable** — C4.6/C4.7 are exact fixed-point equations, not a closure | same |

N ladder at λ = 2: A₊ = 0.4234896, 0.4234597, 0.4235844, 0.4235889; A₋ = 0.4242095,
0.4243310, 0.4242150, 0.4241320. Flat in N; the 1/N extrapolations are 0.4235889 and
0.4241914, straddling the C4.7 value 0.4238956 by ∓3 × 10⁻⁴, which is the residual
finite-N splitting of the two camps and is itself within Monte-Carlo error.

---

## 4. Deviations

1. **c_b was ruled by the owner, not declared by me** (§1.1) — the one point where
   the design was silent and the silence was load-bearing.
2. **The relaxation criterion is evaluated on the replicate mean**, because 10⁻³ is
   below the single-replicate stationary noise floor at N = 10⁵ (§3.2). Both the
   replicate-mean verdict and the per-replicate counts are reported. Logged as
   AMBIGUITIES P9-A2.
3. **Two of twelve perturbations are infeasible** at λ = 3 and carry no verdict
   (§3.2). Logged as AMBIGUITIES P9-A3.
4. **One engine addition**: a per-stance active counter (`ctr[4]` / `sampleAp`), so
   A₊ and A₋ can be sampled separately. The Stage 1 regression was re-run after the
   change: **124/124 rows, 0 mismatches**. A `two_camps_c` parameter was also added
   to the two-camp initial law (default 1.0 reproduces Stage 1 T2 exactly; P9 uses
   0.6); the same regression covers it.
5. N ladder added for A6 error source 2 — extra cells, not replacements.

---

## 5. Files

```
config/p9_config.py   p9_reference.py   solve_p9.py   run_p9.py   verdicts_p9.py
REPORT_P9.md  README.md  AMBIGUITIES.md
outputs/certified_table.csv   outputs/p9_results.json   outputs/seeds.json
outputs/raw/{p9_reference_checks.json, p9_fixed_points.json, p9_raw.json}
outputs/logs/
```

Reproduce: `python p9_reference.py && python solve_p9.py && python run_p9.py &&
python verdicts_p9.py` (≈ 35 min, env `qcb-numba`).
