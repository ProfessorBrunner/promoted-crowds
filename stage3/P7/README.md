# CROWD-1 Stage 3, item P7 — finite-amplitude observables

**Specification** `review_packet_v0_6_1.md`, "PROCESS SPECIFICATION v0.6".
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A, item P7.
**Appendix** `crowd1_appendices_EF_C7_C9.md`, Appendix E §C9(a).
**Authorised** 2026-10-01, P7 only. **P8, P9 and P10 are not authorised.**

**36 registered rows, 36 PASS, 0 FAIL, 0 INCONCLUSIVE.** Master seed **20261004**,
N = 10⁵, 50 replicates per cell as registered (12 cells, 600 registered runs).
Nothing was tuned; no parameter, prediction, tolerance or rule was modified.

Full account: **`REPORT_P7.md`**.

## Headline

Measured against the Appendix E C9(a) reach table at δ = 2 %, on the **mean
trajectory** for A_max and T_act (ruling 2) and once for I:

| f | A_max | pred | I | pred | T_act | pred |
|---|---|---|---|---|---|---|
| 0.10 | 0.135949 | 0.13580 | 0.099760 | 0.09963 | 0.693200 | 0.69315 |
| 0.25 | 0.320176 | 0.32038 | 0.229582 | 0.22969 | 0.693200 | 0.69315 |
| 0.50 | 0.585634 | 0.58579 | 0.410795 | 0.41095 | 0.693200 | 0.69315 |
| 0.75 | 0.809615 | 0.80926 | 0.562582 | 0.56233 | 0.693200 | 0.69315 |

Coincident **(T, T⊥)** reproduces these at every reach (largest |diff| 2.12 × 10⁻⁴);
coincident **(T⊥, T)** gives **A_max = I = T_act = 0 exactly** at every reach — not
a near-zero measurement, since no cohort member's conviction ever reaches c_b. No
discrepancy anywhere exceeds **6.5 % of its own tolerance**.

The C9(a) enclosures were recomputed independently before any run and reproduce
Appendix E's 8-digit f = 0.25 enclosures to **9.4 × 10⁻⁹** and its 5-digit reach
table to **3.95 × 10⁻⁶**. **I is exact, not gridded**: the engine accumulates
`∫A dt` event by event.

## The two rulings

**Ruling (2) — mean trajectory vs per-replicate average.** In P7 the two coincide
**to machine precision** (gap ≤ 2.2 × 10⁻¹⁶ for A_max, identical for T_act), because
A(t) is non-decreasing on [0, L) in every replicate, so the maximum sits at the same
grid index everywhere and `max ∘ mean = mean ∘ max`. This is the opposite of P5,
where A fluctuates about A* over a 50-unit window and the per-replicate maximum
overshoots by 1.6 %. The ruling is the right general rule; it simply costs nothing
here, and the contrast identifies exactly when it bites — an observable with an
interior maximum over a window in which A fluctuates.

**Ruling (1) — outbreak outside the cohort.** 50/50 for every single-pulse and
(T, T⊥) cell, **0/50 for every (T⊥, T) cell**. The new criterion separates the cases
that produce transmission from the one that produces none; the degeneracy logged as
P5-A2 is removed. Non-cohort ever-active fractions are 0.043912, 0.081290, 0.092636,
0.061365 — non-monotone in f, peaking at f = 0.50, because raising f adds seeds but
removes susceptibles. Reported without verdicts (P7 registers no outbreak number).

## A6 error sources, separated

| source | A_max | I | T_act |
|---|---|---|---|
| Monte Carlo | 2.78 × 10⁻⁴ – 5.42 × 10⁻⁴ | 1.97 × 10⁻⁴ – 4.02 × 10⁻⁴ | 0 (see below) |
| Finite-N bias (N = 2.5 × 10⁴ … 2 × 10⁵) | 8.45 × 10⁻⁵ | 1.22 × 10⁻⁴ | 2.2 × 10⁻¹⁶ |
| Numerical (enclosure + grid) | 1.14 × 10⁻⁵ | ≤ 1.7 × 10⁻⁶ | 5.28 × 10⁻⁵ |
| Closure | not applicable — C9(a) gives rigorous enclosures, not an approximation | | |

**T_act's zero-width interval is a property, not a precision claim.** Every cohort
member shuts off inside a 2 × 10⁻⁶ window, so T_act has no replicate-to-replicate
variation; and because A crosses A_max/2 at a *jump*, every grid returns
`ceil(L/dt)·dt` = 0.6932 and the h-ladder cannot move. The reported numerical error
is the quantization |0.6932 − ln 2| = 5.282 × 10⁻⁵ (AMBIGUITIES P7-A2).

**Cross-check.** Total ever-active against the C9(a) final size Z_L = I/L: 0.143923
vs 0.143735, 0.331216 vs 0.331372, 0.592652 vs 0.592869, 0.811634 vs 0.811274 —
peak, integral and final size mutually consistent to 3.6 × 10⁻⁴.

## Deviations

1. The coincident-pulse claim was verdicted at **all four reaches**, not only at
   Appendix E's f = 0.25 (AMBIGUITIES P7-A1). All twelve rows PASS either way.
2. N ladder and grid ladder added for A6 error sources 2 and 3 — extra cells, not
   replacements.
3. No extra replicates were needed; 50 resolve every row by two to three orders of
   magnitude.

## Layout

```
config/p7_config.py  p7_reference.py  run_p7.py  verdicts_p7.py
REPORT_P7.md  AMBIGUITIES.md
outputs/certified_table.csv  outputs/p7_results.json  outputs/seeds.json
outputs/raw/{p7_raw.json, p7_reference.json, p7_mean_traces.npz}  outputs/logs/
```

Reproduce: `python p7_reference.py && python run_p7.py && python verdicts_p7.py`
(≈ 7 min, env `qcb-numba`).
