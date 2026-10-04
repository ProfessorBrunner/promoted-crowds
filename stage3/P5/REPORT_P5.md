# CROWD-1 Stage 3, item P5 — class-1 onset

**Specification** `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A, item P5
(supersedes v0.3; Part A unchanged except the status line and A4b).
**Appendices** `crowd1_appendices_EF_C7_C9.md` (E and F) supply C7–C9; P5 cites C9(b).
**Authorisation** 2026-10-01: *"Stage 3, P5 authorized: survival means A(20) > 0;
burn-in [0, 20], observation window [20, 70]; active-branch statistics conditioned on
A(20) > 0 and reported with the survival fraction. Write to Crowd1/stage3/P5, report,
and stop. P7, P8, P9 and P10 are not authorized."*

**Result: 6 registered rows, 6 PASS, 0 FAIL, 0 INCONCLUSIVE.** Nothing was tuned.
No parameter, prediction, tolerance or rule was modified.

Environment `qcb-numba` (Python 3.12.14, numpy 2.5.3, numba 0.67.0), macOS arm64,
32 cores. **Master seed 20261003** (distinct from Stage 1's 20261001 and Stage 2 /
2B's 20261002). N = 10⁵, 50 replicates per cell as registered, with declared
extensions recorded in §5.

---

## 1. Parameters and why the prediction is exact

FIXED by A4: r = 1, α = 2, β = 0, c_b = 0.5, κ = ρ = 0, ε = 1, I1, one pulse of
reach f at the target T₊ = 0°. λ ∈ {1, 2}, f ∈ {0.01, 0.10}.
DECLARED: c_h = 0.01 (A4 does not name it for P5) — and **verified immaterial**, see
§4.3.

In this sector r = 1 and α = 2 > c_b, so every receipt clips conviction to 1 and
refreshes the shut-off deadline. An agent is therefore active at t **iff** it
received at least one message in (t − L, t], with

```
  L = eps^-1 log(1/c_b) = log 2 = 0.693147180559945
```

Each agent receives at rate λA(t), giving C9(b)'s pair

```
  A(t) = f e^{lambda t} / (1 - f + f e^{lambda t}),        0 <= t < L
  A(t) = 1 - exp[ -lambda * int_{t-L}^{t} A(s) ds ],       t >= L
```

whose persistent branch solves `A* = 1 − e^{−λLA*}`. At λ = 2, L = log 2 this is
`1 − e^{−log 2} = 1/2` **identically**, so the registered `A* = 0.5` is an algebraic
identity and its numerical error is **exactly zero**. At λ = 1, `λL = 0.693147 < 1`
and the only fixed point is A = 0.

---

## 2. The three estimands, kept separate

| name | definition | status |
|---|---|---|
| **Survival fraction** | fraction of replicates with A(20) > 0 — the owner's definition | reported with every conditional statistic |
| **Active-branch mean activity** | per replicate, the time-average of A over the observation window [20, 70]; averaged over surviving replicates only | the verdict row at λ = 2 |
| **A4a outbreak probability** | ever-active fraction > 1 % of N within t = 50 | reported **without a verdict** (A4 registers no number) and **degenerate here** — see §4.2 |

Unconditional long-time activity is not an endpoint and no verdict is issued on it,
as the authorisation directs.

---

## 3. Results

### 3.1 Certified rows (A6)

| # | row | predicted | measured | diff | 95 % CI on diff | δ | status |
|---|---|---|---|---|---|---|---|
| 1 | active-branch mean A over [20,70], λ = 2, f = 0.01, conditional on A(20) > 0 | 0.5 | 0.50011818 | +1.182 × 10⁻⁴ | [−3.448 × 10⁻⁵, +2.708 × 10⁻⁴] | ±0.025 | **PASS** |
| 2 | mean A over [20,70], λ = 1, f = 0.01 (activity dies) | 0 | 0.00000000 | 0 | [0, 0] | ±10⁻³ | **PASS** |
| 3 | pathwise extinction, λ = 1, f = 0.01: A(t) = 0 for all t ≥ 20 | 0 | 0 | 0 | [0, 0] | 0 | **PASS** |
| 4 | active-branch mean A over [20,70], λ = 2, f = 0.10, conditional on A(20) > 0 | 0.5 | 0.49989095 | −1.090 × 10⁻⁴ | [−2.568 × 10⁻⁴, +3.874 × 10⁻⁵] | ±0.025 | **PASS** |
| 5 | mean A over [20,70], λ = 1, f = 0.10 (activity dies) | 0 | 0.00000000 | 0 | [0, 0] | ±10⁻³ | **PASS** |
| 6 | pathwise extinction, λ = 1, f = 0.10: A(t) = 0 for all t ≥ 20 | 0 | 0 | 0 | [0, 0] | 0 | **PASS** |

δ for rows 1 and 4 is A4b's trajectory-marker 5 % of A* = 0.5; for rows 2 and 5 it
is A4a's absolute 10⁻³ for zero predictions; rows 3 and 6 are pathwise structural
identities at δ = 0, where any violation is a FAIL. Rows 3 and 6 scanned every grid
point at or after t = 20 in all 50 replicates and found **0** with A > 0.

The two λ = 2 rows miss A* in opposite directions (+1.18 × 10⁻⁴ and −1.09 × 10⁻⁴),
each about one part in 4 500, and each about two orders of magnitude inside the
tolerance.

### 3.2 Survival fraction

| λ | f | registered 50 replicates | extended (450) |
|---|---|---|---|
| 1 | 0.01 | 0/50, p = 0 [0, 0.07135] | 0/450, p = 0 [0, 0.00846] |
| 1 | 0.10 | 0/50, p = 0 [0, 0.07135] | 0/450, p = 0 [0, 0.00846] |
| 2 | 0.01 | 50/50, p = 1 [0.92865, 1] | 450/450, p = 1 [0.99154, 1] |
| 2 | 0.10 | 50/50, p = 1 [0.92865, 1] | 450/450, p = 1 [0.99154, 1] |

Wilson score intervals. The registered 50 replicates give a half-width of 0.03567,
just above A4a's frozen precision target of 0.03 for probability estimates, so the
extension was run (see §5 and AMBIGUITIES P5-A1); it reaches 0.00423. **Both are
reported; the registered value is the registered value.** The extension runs only to
t = 20, since survival is A(20) > 0, and therefore changes no window statistic.

At the registered N = 10⁵ the finite-N departure that A4 anticipates — *"positive
seeds can die out"* — is not observed at either reach: at λ = 2 every one of 450
replicates survives at f = 0.01, where the cohort is already ≈ 1 000 agents. The
prediction is about the possibility, not a rate, and no number is registered for it.

### 3.3 Exact mean-field reference (independent of the agent simulator)

`delay_reference.py` integrates the C9(b) delay equation directly — no agents, no
RNG, no event queue — with step halving:

| λ | f | window mean A over [20,70] | observed order | numerical uncertainty | A(20) | A_max |
|---|---|---|---|---|---|---|
| 1 | 0.01 | 0.000000000 | — | 4.0 × 10⁻¹⁵ | 5.219 × 10⁻¹¹ | 0.019802 |
| 1 | 0.10 | 0.000000000 | — | 3.2 × 10⁻¹⁴ | 4.353 × 10⁻¹⁰ | 0.181818 |
| 2 | 0.01 | 0.499999999 | 0.992 | 8.4 × 10⁻¹³ | 0.500000 | 0.500000 |
| 2 | 0.10 | 0.500000000 | 1.439 | 4.8 × 10⁻¹³ | 0.500000 | 0.500000 |

So t = 20 is far past the transient at λ = 2 (A(20) = 0.5 to the printed digits), and
at λ = 1 the mean field has fallen to ~10⁻¹⁰ by t = 20 — a population expectation of
10⁻⁵ agents at N = 10⁵, which is why every finite-N run is *exactly* extinct rather
than merely small. The order estimates at λ = 1 are meaningless because the
differences are at the rounding floor; the uncertainty column is the honest number
there.

### 3.4 A6's four error sources, separated

| source | λ = 2, f = 0.01 | λ = 2, f = 0.10 |
|---|---|---|
| 1. Monte Carlo (Student-t, 50 replicates) | 1.527 × 10⁻⁴ | 1.478 × 10⁻⁴ |
| 2. Finite-N bias (ladder N = 2.5 × 10⁴ … 2 × 10⁵, 1/N extrapolation) | 2.80 × 10⁻⁵ | 5.40 × 10⁻⁵ |
| 3. Numerical error of the reference (+ measurement grid) | 8.4 × 10⁻¹³ (+ 3.0 × 10⁻⁷) | 4.8 × 10⁻¹³ (+ 3.0 × 10⁻⁷) |
| 4. Closure error | **not applicable** — the prediction is the exact mean-field fixed point, with no approximation to assess | same |

N ladder, window mean A: f = 0.01 → 0.50019245, 0.49984123, 0.50011818, 0.49983511;
f = 0.10 → 0.49989769, 0.49982123, 0.49989095, 0.49998489. Flat in N — the scatter
is Monte Carlo, not bias; the 1/N extrapolations are 0.49986307 and 0.49993093.
Measurement sampling grid dt = 0.04, 0.02, 0.01 → 0.499888856, 0.499890651,
0.499890955, residual 3.0 × 10⁻⁷.

---

## 4. Observations that are reported, not certified

### 4.1 A_max is not an estimate of A*

Measured A_max: 0.507907 and 0.507855 at λ = 2, against the mean-field 0.500000. The
maximum of a fluctuating trajectory exceeds its mean level by construction, so this
is the expected finite-N behaviour of a maximum, not a 1.6 % error in A*. It is
recorded here because A_max is a registered endpoint in **P7**, which is **not
authorised**, and the distinction should be settled before P7 is released. At λ = 1,
A_max = 0.019976 and 0.181056 against the exact 0.019802 and 0.181818.

### 4.2 A4a's outbreak criterion is degenerate for P5

| λ | f | A4a outbreak | mean ever-active fraction |
|---|---|---|---|
| 1 | 0.01 | 50/50 | 0.032607 |
| 1 | 0.10 | 50/50 | 0.265074 |
| 2 | 0.01 | 50/50 | 1.000000 |
| 2 | 0.10 | 50/50 | 1.000000 |

A4a defines an outbreak as "ever-active fraction > 1 % of N within the horizon". In
P5 the campaign itself activates every cohort member (α = 2 > c_b, acceptance
probability 1 from I1), so at f = 0.01 the cohort alone is already ≈ 1 % of N and one
further activation settles the criterion. The result is an outbreak probability of
1.000 in **every** cell — including both λ = 1 cells, where activity provably and
observably dies before t = 20. The criterion is measuring the campaign, not the
epidemic. Reported without a verdict (A4 registers no number for it) and logged as
AMBIGUITIES P5-A2.

The ever-active fractions at λ = 1 are themselves a clean check of the subcritical
branching structure: with mean offspring number λL = 0.693147, expected total progeny
per seed is 1/(1 − λL) = 3.258891, predicting 0.032866 at realized reach 0.010085 —
against 0.032607 measured, a ratio of 0.9921. At f = 0.10 the ratio falls to 0.8148,
as saturation removes the independence the branching bound assumes.

### 4.3 c_h is immaterial here, as declared

A4 does not name c_h for P5, so it was DECLARED 0.01 before the runs and the
declaration was checked rather than assumed. With β = 0, I1 (φ = T₊) and a T₊ pulse,
every message is accepted and every deposit is +α cos 0 = +2. Measured across all
four cells: minimum final conviction 0.0, 0.0, 2.23 × 10⁻⁷, 2.10 × 10⁻⁹ — never
negative — and **0 agents** with stance − in any replicate of any cell. No value of
c_h in [0, c_b) could change a single stance, so no registered number depends on the
declaration.

---

## 5. Deviations from the registered run plan

1. **Replicate extension on the two proportion endpoints.** A4 registers 50
   replicates per cell; at 0/50 and 50/50 the Wilson half-width is 0.03567, just
   above A4a's frozen precision target of 0.03. 400 further replicates were run
   **to t = 20 only** (survival is A(20) > 0), and both the registered-50 and the
   extended estimates are reported in §3.2. No window statistic is affected. Logged
   as AMBIGUITIES P5-A1.
2. **N ladder and grid ladder added** beyond the registered single N = 10⁵, to supply
   A6 error sources 2 and 3. These are additional cells, not replacements; the
   registered N = 10⁵ cells are the certified ones.
3. **No deviation in parameters, predictions, tolerances or rules.**

---

## 6. Files

```
config/p5_config.py        FIXED / DECLARED parameters, frozen before the runs
run_p5.py                  the four registered cells, the N ladder, the grid ladder
delay_reference.py         exact C9(b) delay-equation reference (no agents, no RNG)
survival_extension.py      the 450-replicate survival pass to t = 20
verdicts_p5.py             the A6 verdict table
outputs/certified_table.csv   the six rows of 3.1
outputs/p5_results.json       verdicts, survival, outbreak, error sources, reference
outputs/raw/p5_raw.json       every cell, every seed
outputs/raw/p5_traces.npz     A(t) on a dt = 0.01 grid for all 200 registered runs
outputs/raw/p5_delay_reference.json, p5_survival_extension.json
outputs/seeds.json            seed derivation
outputs/logs/*.log
```

Reproduction: `python run_p5.py && python delay_reference.py &&
python survival_extension.py && python verdicts_p5.py` (≈ 20 min total).

---

## 7. Scope

Only P5 was run. **P7, P8, P9 and P10 are not authorised** and nothing in this
directory bears on them, beyond the A_max note in §4.1 which flags a definitional
question for P7 rather than answering it.
