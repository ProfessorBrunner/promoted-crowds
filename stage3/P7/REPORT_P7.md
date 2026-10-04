# CROWD-1 Stage 3, item P7 — finite-amplitude observables

**Specification** `review_packet_v0_6_1.md`, "PROCESS SPECIFICATION v0.6".
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A, item P7.
**Appendix** `crowd1_appendices_EF_C7_C9.md`, Appendix E §C9(a).
**Authorisation** 2026-10-01, P7 only, under two rulings:

> **(1)** Outbreak criterion, from now on: the ever-active fraction among agents
> **outside the campaign cohort** exceeds 1 % of N within the horizon.
> **(2)** A_max and T_act: the registered endpoint is the **mean-trajectory** value
> (the Appendix E enclosures are mean-field); the per-replicate average is reported
> beside it as a finite-N diagnostic **without verdict**. **I** is reported once
> (linear in A). Point predictions at **δ = 2 %**.

**Result: 36 registered rows, 36 PASS, 0 FAIL, 0 INCONCLUSIVE.** Nothing was tuned.
No parameter, prediction, tolerance or rule was modified.

Environment `qcb-numba`, macOS arm64, 32 cores. **Master seed 20261004** (distinct
from 20261001 / 20261002 / 20261003). N = 10⁵, 50 replicates per cell as registered;
12 cells, 600 registered runs, plus ladders.

---

## 1. Parameters, and the structure that makes the measurement sharp

FIXED by A4 and C9(a): α = 1, β = 0.4, r = 10⁻⁶, λ = 0.5, ε = 1, c_b = 0.5,
c_h = 0.01, ρ = κ = 0, I1, one pulse at T₊ = 0°, f ∈ {0.10, 0.25, 0.50, 0.75}.

Because every first T receipt sets conviction to 1 and subsequent deposits total at
most `B = r/(1−r) = 1.000001 × 10⁻⁶`:

```
  L      = log(1/c_b)       = 0.693147180559945
  L_plus = log(1/(c_b - B)) = 0.693149180563945      L+ - L = 2.000004e-06
```

Two consequences the measurement design rests on, both structural rather than
assumed:

- **A(t) is non-decreasing on [0, L) pathwise.** Nobody can shut off before their own
  age L, and every activated agent starts at c = 1. So `A_max = A(L⁻)` exactly, and
  the grid index of the maximum is deterministic.
- **The crossing of A_max/2 is a jump, not a smooth crossing.** Every cohort member
  shuts off inside the 2 × 10⁻⁶ window [L, L₊], so A drops by the realized reach
  essentially instantaneously at t = L. Checked at every f that A(L⁺) < A_max/2, so
  `T_act = L` on the single interval [0, L).

**I is not taken from the grid at all.** The engine accumulates the exact `∫A dt`
event by event, so I carries no grid error whatsoever. The sampling grid
(dt = 10⁻⁴ on [0, 2], 10⁻² to t = 50) exists only for A_max and T_act.

### 1.1 The reference, recomputed independently

`p7_reference.py` recomputes every C9(a) quantity from its definition —
`Z_D(f)` from `1 − Z = (1−f)e^{−λDZ}` by Brent to 10⁻¹⁶, `P_D(f) = fe^{λD}/(1−f+fe^{λD})`
— and checks it against the two things Appendix E states numerically:

| check | result |
|---|---|
| Appendix E's 8-digit enclosures at f = 0.25 | A_max [0.32037724, 0.32037746], I [0.22968922, 0.22969009], T_act [0.69314718, 0.69314918] — agreeing to ≤ **9.4 × 10⁻⁹**, i.e. to the last printed digit |
| Appendix E's 5-digit reach table at all four f | agreeing to ≤ **3.95 × 10⁻⁶** (largest: I at f = 0.50), i.e. to the rounding of 5 decimal places |
| the coincident-pulse arithmetic, from the specification's transition | (T, T⊥) → c = 1.000000000, active; (T⊥, T) → c = 0.400001000 < c_b, inactive — exactly Appendix E's statement |

The (T⊥, T) arithmetic is worth spelling out because it is the whole content of the
zero prediction: T⊥ is **rejected** (cos²90° = 0) and deposits
`r⁰·cos180°·(−β) = +0.4`; then T is accepted, but 90° and 0° lie in the **same
framing class** (both key to 0 mod 90), so the counter is already 1 and T deposits
only `r¹·cos0°·(+α) = +10⁻⁶`. Final conviction 0.400001 < c_b = 0.5, so no cohort
member ever activates.

---

## 2. Results

### 2.1 Single T pulse — registered rows (mean trajectory, δ = 2 %)

| f | A_max meas | pred | diff | I meas | pred | diff | T_act meas | pred | diff |
|---|---|---|---|---|---|---|---|---|---|
| 0.10 | 0.135949 | 0.13580 | +1.49 × 10⁻⁴ | 0.099760 | 0.09963 | +1.30 × 10⁻⁴ | 0.693200 | 0.69315 | +5.0 × 10⁻⁵ |
| 0.25 | 0.320176 | 0.32038 | −2.04 × 10⁻⁴ | 0.229582 | 0.22969 | −1.08 × 10⁻⁴ | 0.693200 | 0.69315 | +5.0 × 10⁻⁵ |
| 0.50 | 0.585634 | 0.58579 | −1.56 × 10⁻⁴ | 0.410795 | 0.41095 | −1.55 × 10⁻⁴ | 0.693200 | 0.69315 | +5.0 × 10⁻⁵ |
| 0.75 | 0.809615 | 0.80926 | +3.55 × 10⁻⁴ | 0.562582 | 0.56233 | +2.52 × 10⁻⁴ | 0.693200 | 0.69315 | +5.0 × 10⁻⁵ |

All twelve PASS. The largest discrepancy in absolute terms is 3.55 × 10⁻⁴ (A_max at
f = 0.75), and the largest **relative to its own tolerance** is I at f = 0.10 at
**6.50 %** of δ — the small-f rows are the tightest because δ scales with the
predicted value. Across all 36 rows no discrepancy exceeds 6.5 % of its tolerance,
and the signs alternate across f, as Monte-Carlo scatter should.

### 2.2 Coincident (T, T⊥) — reproduces the single-pulse values

| f | A_max | pred | I | pred | T_act | pred |
|---|---|---|---|---|---|---|
| 0.10 | 0.135946 | 0.13580 | 0.099747 | 0.09963 | 0.693200 | 0.69315 |
| 0.25 | 0.320592 | 0.32038 | 0.229827 | 0.22969 | 0.693200 | 0.69315 |
| 0.50 | 0.585687 | 0.58579 | 0.410831 | 0.41095 | 0.693200 | 0.69315 |
| 0.75 | 0.809119 | 0.80926 | 0.562254 | 0.56233 | 0.693200 | 0.69315 |

All twelve PASS; largest |diff| 2.12 × 10⁻⁴, largest fraction of tolerance 5.88 %
(I at f = 0.10).

### 2.3 Coincident (T⊥, T) — zero

A_max = I = T_act = **0 exactly**, in all 50 replicates at all four reaches, against
the A4a absolute tolerance 10⁻³. All twelve PASS. This is not a near-zero
measurement: no cohort member's conviction ever reaches c_b, so the activity process
never starts and `∫A dt` is identically zero.

### 2.4 A6's four error sources, separated

| source | A_max | I | T_act |
|---|---|---|---|
| 1. Monte Carlo | 2.78 × 10⁻⁴ to 5.42 × 10⁻⁴ (bootstrap half-width over replicate traces, B = 2000) | 1.97 × 10⁻⁴ to 4.02 × 10⁻⁴ (Student-t, 50 replicates) | **0** — see below |
| 2. Finite-N bias (ladder N = 2.5 × 10⁴ … 2 × 10⁵, 1/N extrapolation) | 8.45 × 10⁻⁵ | 1.22 × 10⁻⁴ | 2.2 × 10⁻¹⁶ |
| 3. Numerical: C9(a) enclosure width + measurement grid | ≤ 2.4 × 10⁻⁷ + 1.14 × 10⁻⁵ | ≤ 1.7 × 10⁻⁶ | 2.0 × 10⁻⁶ + **5.28 × 10⁻⁵** quantization |
| 4. Closure error | **not applicable** — C9(a) gives rigorous enclosures, not an approximation to be assessed | same | same |

The Monte-Carlo ranges span all eight non-zero cells (both pulse orders, four
reaches each); the extremes are A_max at single-pulse f = 0.75 (2.781 × 10⁻⁴) and at
(T, T⊥) f = 0.25 (5.419 × 10⁻⁴), and I at the same two cells (1.966 × 10⁻⁴ and
4.024 × 10⁻⁴). The twelve (T⊥, T) rows are identically zero and are excluded.

N ladder at f = 0.25: A_max 0.3199576, 0.3201816, 0.3201760, 0.3201331;
I 0.2292976, 0.2296075, 0.2295818, 0.2295054; T_act 0.6932 at every rung. Flat — the
scatter is Monte Carlo, not bias.

**The T_act rows have a bootstrap interval of exactly zero width, and that is
correct rather than a defect.** Every cohort member shuts off inside a 2 × 10⁻⁶
window in every replicate, so T_act has no replicate-to-replicate variation at all
at a grid of 10⁻⁴. The entire discrepancy is **grid quantization**: A crosses
A_max/2 at a jump, so any grid returns `ceil(L/dt)·dt`, which is 0.6932 for
dt = 4 × 10⁻⁴, 2 × 10⁻⁴ *and* 10⁻⁴ alike — the h-ladder shows no movement because
there is nothing to converge, only to quantize. The honest numerical error is
|0.6932 − log 2| = **5.282 × 10⁻⁵** (7.6 × 10⁻⁵ relative), which is what the verdict
rows carry, and it is 0.38 % of the tolerance.

---

## 3. Ruling (2): the two estimands coincide **exactly** here

| order | f | A_max mean trajectory | A_max per-replicate average | gap |
|---|---|---|---|---|
| single | 0.10 | 0.135949 | 0.135949 | +2.8 × 10⁻¹⁷ |
| single | 0.25 | 0.320176 | 0.320176 | +1.7 × 10⁻¹⁶ |
| single | 0.50 | 0.585634 | 0.585634 | 0 |
| single | 0.75 | 0.809615 | 0.809615 | −1.1 × 10⁻¹⁶ |
| (T,T⊥) | 0.10–0.75 | — | — | ≤ 2.2 × 10⁻¹⁶ |

T_act likewise: 0.693200 under both definitions at every cell.

The gap is zero **to machine precision**, and for a structural reason: A(t) is
non-decreasing on [0, L) in every replicate, so the maximum is attained at the same
grid index in every replicate and `max ∘ mean = mean ∘ max`. The per-replicate
maximum cannot pick up an upward noise excursion because there is no interior
maximum to find.

This is the opposite of what P5 found, and the contrast is the useful part. In P5
the population sits on a persistent branch and A fluctuates about A* = 0.5 over a
50-unit window, so the per-replicate maximum samples the upper envelope of the noise
and overshoots by 1.6 %. Here the trajectory is monotone up to a deterministic time
and then jumps down, so there is no envelope to sample.

**So ruling (2) is the right general rule and it costs nothing in P7.** The
distinction bites exactly when the observable has an interior maximum over a window
in which A fluctuates — P5's regime, not P7's. (The per-replicate standard deviation
of the *argmax* is 5.8 × 10⁻⁵ to 1.5 × 10⁻⁴, non-zero only because ties on the
plateau move which grid index `argmax` reports; the maximum *value* is unaffected.)

---

## 4. Ruling (1): the new outbreak criterion, reported without verdict

Ever-active fraction among agents **outside** the campaign cohort, against 1 % of N:

| order | f | outbreak | mean non-cohort ever-active |
|---|---|---|---|
| single | 0.10 / 0.25 / 0.50 / 0.75 | 50/50 each | 0.043912 / 0.081290 / 0.092636 / 0.061365 |
| (T, T⊥) | 0.10 / 0.25 / 0.50 / 0.75 | 50/50 each | 0.043943 / 0.081362 / 0.092786 / 0.061396 |
| (T⊥, T) | 0.10 / 0.25 / 0.50 / 0.75 | **0/50 each** | 0.000000 |

P7 registers no outbreak number, so these carry no verdict. Two remarks:

- **The new criterion works.** It cleanly separates the cases that produce
  transmission from the one that produces none, which the old criterion could not do
  (under the old rule the (T⊥, T) cells would still have counted as outbreaks at
  f ≥ 0.01, since the cohort is counted). The degeneracy logged as P5-A2 is removed.
- The non-cohort ever-active fraction is **non-monotone in f**, peaking at f = 0.50.
  That is not an anomaly: raising f adds seeds but removes susceptibles, and at
  f = 0.75 only a quarter of the population is outside the cohort to begin with.

**Independent cross-check of the whole activity accounting.** Total ever-active
(cohort + outside) against the C9(a) final size `Z_L = I/L`: 0.143923 vs 0.143735,
0.331216 vs 0.331372, 0.592652 vs 0.592869, 0.811634 vs 0.811274 — agreeing to
≤ 3.6 × 10⁻⁴ at every reach. The peak, the integral and the final size are mutually
consistent.

---

## 5. Deviations from the registered run plan

1. **The two-pulse claim was verdicted at all four reaches, not only at f = 0.25.**
   Appendix E states the coincident-pulse result for its f = 0.25 case; design A4
   states it without restricting f. Running all four is the stronger reading and all
   twelve rows PASS, so no reading is contradicted. Logged as AMBIGUITIES P7-A1.
2. **N ladder and grid ladder added** beyond the registered single N = 10⁵, to supply
   A6 error sources 2 and 3. Extra cells, not replacements.
3. **No deviation in parameters, predictions, tolerances or rules.** No extra
   replicates were needed: every registered row is a point prediction at δ = 2 %, and
   50 replicates resolve all of them by two to three orders of magnitude.

---

## 6. Files

```
config/p7_config.py     FIXED / DECLARED parameters, frozen before the runs
p7_reference.py         independent recomputation of the C9(a) enclosures
run_p7.py               12 registered cells, N ladder, grid ladder, bootstrap
verdicts_p7.py          the A6 verdict table
REPORT_P7.md  README.md  AMBIGUITIES.md
outputs/certified_table.csv    the 36 rows
outputs/p7_results.json        verdicts, diagnostics, outbreak, error sources
outputs/raw/p7_raw.json        every cell, every seed, per-replicate values
outputs/raw/p7_reference.json  the enclosures and both Appendix E checks
outputs/raw/p7_mean_traces.npz the 12 mean trajectories on the dt = 1e-4 grid
outputs/seeds.json  outputs/logs/*.log
```

Reproduce: `python p7_reference.py && python run_p7.py && python verdicts_p7.py`
(≈ 7 min, env `qcb-numba`).

---

## 7. Scope

Only P7 was run. **P8, P9 and P10 are not authorised.**
