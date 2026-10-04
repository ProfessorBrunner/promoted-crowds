# CROWD-1 Stage 3, item P5 — class-1 onset

**Specification** `review_packet_v0_6_1.md`, "PROCESS SPECIFICATION v0.6".
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A, item P5.
**Appendices** `crowd1_appendices_EF_C7_C9.md` (E and F) — P5 cites C9(b).
**Authorised** 2026-10-01, P5 only. **P7, P8, P9 and P10 are not authorised.**

**6 registered rows, 6 PASS, 0 FAIL, 0 INCONCLUSIVE.** Master seed **20261003**,
N = 10⁵, 50 replicates per cell as registered. Nothing was tuned; no parameter,
prediction, tolerance or rule was modified.

Full account: **`REPORT_P5.md`**.

## Headline

At λ = 2 the active-branch mean activity over the observation window [20, 70],
conditional on survival (A(20) > 0), is **0.50011818** at f = 0.01 and **0.49989095**
at f = 0.10, against the registered **A\* = 0.5** — which is an algebraic identity
here, not a computed value: `A* = 1 − e^{−λLA*}` with λ = 2, L = ln 2 gives
`1 − e^{−ln 2} = 1/2` exactly. Both rows PASS at δ = 5 %, missing in opposite
directions by about one part in 4 500.

At λ = 1 (λL = 0.693 < 1) activity dies: the window mean is **0 exactly** in all 50
replicates of both cells, with **0** grid points showing A > 0 anywhere at or after
t = 20 — a pathwise identity at δ = 0.

Survival fraction (the owner's criterion, A(20) > 0): **0/450** at λ = 1 for both
reaches, **450/450** at λ = 2 for both.

An independent reference was computed for every cell by integrating C9(b)'s delay
equation directly — no agents, no RNG, no event queue — giving window means of
0.499999999, 0.500000000, 0.000000000, 0.000000000 with numerical uncertainties
below 10⁻¹².

## Two things reported but not certified

- **A4a's outbreak criterion is degenerate for P5** and gives 1.000 in all four
  cells, *including both λ = 1 cells where activity provably dies*. With α = 2 > c_b
  and I1, the campaign activates every cohort member, so at f = 0.01 the cohort alone
  is already ≈ 1 % of N. Reported without a verdict (A4 registers no number) and
  logged as AMBIGUITIES P5-A2 with a concrete suggestion for the owner.
- **A_max is not an estimate of A\***: measured 0.5079 against 0.5, because the
  maximum of a fluctuating trajectory exceeds its mean level by construction. P5
  registers no A_max; this is flagged because **P7** does (AMBIGUITIES P5-A4).

## A6 error sources, separated (λ = 2 rows)

| source | f = 0.01 | f = 0.10 |
|---|---|---|
| Monte Carlo | 1.527 × 10⁻⁴ | 1.478 × 10⁻⁴ |
| Finite-N bias (N = 2.5 × 10⁴ … 2 × 10⁵) | 2.80 × 10⁻⁵ | 5.40 × 10⁻⁵ |
| Numerical (reference + measurement grid) | 3.03 × 10⁻⁷ | 3.03 × 10⁻⁷ |
| Closure | not applicable — the prediction is the exact mean-field fixed point | same |

## Deviations

1. 400 replicates added on the two proportion endpoints, run **only to t = 20**, to
   meet A4a's frozen ±0.03 precision target that 50 replicates miss (half-width
   0.03567 → 0.00423). Both the registered-50 and extended estimates are reported.
2. An N ladder and a sampling-grid ladder were added to supply A6 error sources 2
   and 3. These are extra cells; the registered N = 10⁵ cells are the certified ones.
3. c_h is not named for P5; DECLARED 0.01 and **verified immaterial** (no conviction
   ever negative, zero stance-minus agents in any replicate).

## Layout

```
config/p5_config.py   run_p5.py   delay_reference.py   survival_extension.py
verdicts_p5.py        REPORT_P5.md   AMBIGUITIES.md
outputs/certified_table.csv  outputs/p5_results.json  outputs/seeds.json
outputs/raw/*.json  outputs/raw/p5_traces.npz  outputs/logs/*.log
```

Reproduce: `python run_p5.py && python delay_reference.py && python
survival_extension.py && python verdicts_p5.py` (≈ 20 min, env `qcb-numba`).
