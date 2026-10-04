# CROWD-1 Stage 3, item P9 — two-camp fixed points

**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md` Part A, item P9.
**Reference** Appendix C §C4 (C4.1–C4.2, C4.6, C4.7, C4.10–C4.11); result R9.
**Authorised** 2026-10-01; threshold **c_b = 0.3 ruled by the owner 2026-10-02**.

**18 registered rows, 18 PASS, 0 FAIL, 0 INCONCLUSIVE.** Master seed **20261005**,
N = 10⁵, 50 replicates per cell. Nothing was tuned.

Full account: **`REPORT_P9.md`**.

## Headline

**Branch selected: the C4.7 symmetric branch z = ½** — at p = ½ it is the *unique*
positive branch, confirmed by a C4.7 z-scan over (0, ½) that found no interior sign
change of the consistency residual at any λ. All three are linearly stable by C4.11.

| λ | A₊ measured | A₋ measured | C4.7 quadrature | spr(J) |
|---|---|---|---|---|
| 1.5 | 0.29897799 | 0.29907519 | 0.299028897 | 0.705757 |
| 2.0 | 0.42358442 | 0.42421501 | 0.423895616 | 0.378207 |
| 3.0 | 0.48288782 | 0.48318623 | 0.483041685 | 0.126822 |

The camps straddle the prediction in every cell with equal and opposite deviations,
so the ± symmetry is reproduced rather than imposed; all six rows PASS at δ = 5 %.

**Stability.** Ten of twelve perturbations are feasible and all ten relax. The
residual deviation at t = 10 **orders with spr(J)** — largest at λ = 1.5 (spr 0.706),
smallest at λ = 3 (spr 0.127) — which independently corroborates the C4.10
susceptibility matrix, since nothing in the simulation knows spr(J).

## Three things that needed care

- **c_b had to be ruled, not declared.** A4 omits it, and with β = 0.4 the value
  decides whether one rejected message can activate from rest. At c_b = 0.5, λ = 1.5
  and λ = 2 have *no* positive fixed point (only λ = 3, at 0.385368902); at c_b = 0.3
  all three do. Both readings were computed and put to the owner (P9-A1).
- **The relaxation criterion is below the noise floor.** The stationary
  single-replicate sd of A₊ at N = 10⁵ is 1.0–1.4 × 10⁻³, so |ΔA| < 10⁻³ cannot be
  met pathwise even at equilibrium. Evaluated on the replicate mean (sem
  ≈ 1.8 × 10⁻⁴), with per-replicate counts reported beside it (P9-A2).
- **Two perturbations do not exist.** At λ = 3 only 0.0171 of the population is
  inactive in each camp, less than the 0.05 needed to move A up. Reported with the
  reason and no verdict; the −0.05 side is feasible and relaxes (P9-A3).

## The reference was validated three ways before use

| check | result |
|---|---|
| v → 0 closed form F = 1 − c_b^(u/ε) | ≤ 2.0 × 10⁻¹³ |
| C4.2 clipped-arrival flux (must hold identically) | ≤ 9.3 × 10⁻⁸ relative |
| Gauss–Legendre node refinement | last step 7.0 × 10⁻⁹ |

**The camps are fixed by verification, not assumption**: 0 stance flips and 0 agents
off {T₊, T₋} over 150 replicates × 10⁵ agents, which is why c_h and ρ are immaterial
here — exactly C4.1's "reset is harmless under this declaration".

## A6 error sources

Monte Carlo 2.86 × 10⁻⁴ – 4.13 × 10⁻⁴; finite-N bias 1.12 × 10⁻⁸ (A₊) and
5.94 × 10⁻⁵ (A₋) from an N ladder over 2.5 × 10⁴ … 2 × 10⁵; numerical 7 × 10⁻⁹;
closure **not applicable** — C4.6/C4.7 are exact fixed-point equations, not a closure.

## Engine additions (Stage 1 regression re-run: 124/124, 0 mismatches)

A per-stance active counter (`ctr[4]` / `sampleAp`) so A₊ and A₋ can be sampled
separately, and a `two_camps_c` parameter whose default 1.0 reproduces Stage 1 T2
exactly (P9 uses 0.6).

Reproduce: `python p9_reference.py && python solve_p9.py && python run_p9.py &&
python verdicts_p9.py` (≈ 35 min, env `qcb-numba`).
