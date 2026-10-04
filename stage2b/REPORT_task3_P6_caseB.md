# Stage 2B, task 3 — P6 case B: the reference that was blocked in Stage 2

Specification: `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
Design: `crowd1_cs_design_and_manuscript_brief_v0_3.md`, Part A (A4 item P6).
Authorisation: Stage 2B, a discrepancy investigation, **not** a re-certification.
Stage 2 reported case B as **BLOCKED, no verdict**; that status is not revised here,
and no verdict is issued. Nothing was tuned.

Case B parameters (design, FIXED): α = 1, β = 0, r = 0.95, λ = 2.5, c_b = 0.4,
ρ = κ = 0, f = 1, ε = 1, initial law I1, c_h = 0.01.

---

## 1. Estimand, stated exactly

```
  t*      = inf{ t : A(t) <= 0.325 }     (first DOWNWARD crossing)
  Lambda* = lambda * int_0^{t*} A(s) ds
```

`r = 0.95 ≠ 1`, so the framing counters are **not** inert: the deposit on the n-th
receipt in a class is `α r^{n−1}`, and the conviction law must be resolved jointly in
`(c, n)`. The counter-resolved kinetic equation integrated here is

```
  d/dt <psi, mu_t^{(n)}> = < -c psi'(c), mu_t^{(n)} >
                           - lambda A(t) <psi, mu_t^{(n)}>
                           + lambda A(t) <psi(min{1, . + alpha r^{n-1}}), mu_t^{(n-1)}>
  A(t) = sum_n mu_t^{(n)}((c_b, 1])
```

one slab per counter value, with the slab count set from a Poisson tail bound and the
leak out of the top slab reported (it is ≤ 10⁻⁹² throughout — the slab space is not
a source of error).

### 1.1 Mean trajectory, or mean of replicate crossings?

The owner asked which, and for both. **The Stage 2 tabulation is the mean of
replicate crossings** — `_first_down_crossing` applied per replicate and averaged.
The crossing of the mean trajectory was not computed in Stage 2 because the A(t)
traces were not retained. The 50 case-B replicates were therefore re-run here with
the traces saved (same engine, same config, same seeds):

| level | mean of replicate crossings | sd | crossing of the mean trajectory | difference |
|---|---|---|---|---|
| 0.400 | 12.581264 | 0.015485 | 12.581129 | −1.34 × 10⁻⁴ |
| 0.350 | 12.801038 | 0.015755 | 12.801099 | +6.12 × 10⁻⁵ |
| **0.325** | **12.904191** | **0.015305** | **12.904441** | **+2.50 × 10⁻⁴** |
| 0.300 | 13.003855 | 0.014524 | 13.003926 | +7.02 × 10⁻⁵ |

At N = 10⁵ the two definitions differ by at most 2.5 × 10⁻⁴, i.e. **1.6 % of the
replicate standard deviation**. The distinction is immaterial at this N, but it is
now measured rather than assumed, and both are reported.

---

## 2. (i) The historical comparison, recovered from the existing Stage 2 tabulation

The Stage 2 `case_B_Lambda_vs_activity_level` table has nodes at A = 0.3 and A = 0.4
bracketing 0.325. Interpolating (mean of replicate crossings, 50 replicates,
N = 10⁵):

| quantity | linear | cubic, 6 nodes | cubic, 4 nodes | **interpolation error** |
|---|---|---|---|---|
| `t*` | 12.89821 | 12.90440 | 12.90362 | **≤ 0.0062** |
| `Λ*` | 25.58064 | 25.60462 | 25.59571 | **≤ 0.0240** |

The interpolation error is comparable to the replicate standard deviation of Λ at the
bracketing nodes (0.0257 at A = 0.3, 0.0271 at A = 0.4), so interpolation is not the
limiting error.

**Check against the direct measurement** of §1.1, which did not exist when the
interpolation was made: direct `t*` = 12.904191, `Λ*` = 25.59557. The linear
interpolant is off by −0.0060 in `t*` and −0.0149 in `Λ*` — both **inside** the
error bounds stated above (0.0062 and 0.0240). The stated interpolation error was
honest.

---

## 3. (ii) The full counter-resolved kinetic reference

### 3.1 Solver validation on case A, where a registered number exists

Case A (α = 2, r = 0.99, λ = 3, c_b = 0.5) uses the **same counter-resolved solver**
and has a registered marker: `t† = 70.3 ± 0.1`, the first downward crossing of
A_f = 0.5603.

| h | `t†` | Λ at the crossing |
|---|---|---|
| 0.010005 | 70.22825 | 165.78089 |
| 0.005003 | 70.27898 | 166.62703 |
| 0.002500 | 70.30333 | 167.03806 |

Observed order **1.059**; Richardson **70.32769 ± 0.02435**, against the registered
**70.3 ± 0.1** — agreeing to **0.028**, well inside the registered uncertainty and
inside the numerical uncertainty of the extrapolation at about one unit. Slab leak
≤ 1.5 × 10⁻⁵⁷; mass deficit ≤ 1.5 × 10⁻⁶. The counter-resolved solver reproduces the
one case-A number the design registers, so it is trusted for case B.

(Stage 2's agent measurement of the same marker was `t† = 70.353 ± 0.085` over 50
replicates. Agent, kinetic and registered all agree.)

### 3.2 Case B

| h | `t*` at A = 0.325 | `Λ*` | slab leak | mass deficit |
|---|---|---|---|---|
| 0.009990 | 12.85621 | 25.21107 | 1.0 × 10⁻⁹³ | 9.0 × 10⁻⁶ |
| 0.005000 | 12.88088 | 25.32046 | 4.2 × 10⁻⁹³ | 1.2 × 10⁻⁶ |
| 0.002500 | 12.89316 | 25.37465 | 1.2 × 10⁻⁹² | 1.5 × 10⁻⁷ |
| 0.001250 | 12.89928 | 25.40161 | 2.8 × 10⁻⁹² | 1.8 × 10⁻⁸ |
| 0.000625 | 12.90234 | 25.41505 | 6.1 × 10⁻⁹² | 2.3 × 10⁻⁹ |

Observed order **1.003** (`t*`) and **1.005** (`Λ*`) — clean first order over four
halvings.

> **`t*`^MF = 12.90539 ± 0.00305**
> **`Λ*`^MF = 25.42849 ± 0.01344**

---

## 4. The three numbers, separated

| object | value | what it is |
|---|---|---|
| **`Λ*`^MF = 25.4285 ± 0.0134** | this work | mean-field counter-resolved `λ∫A` to the first downward crossing of A = 0.325 |
| **`Λ*` agent = 25.4313 ± 0.0104** | this work, 50 reps, N = 10⁵ — **corrected**, see §6 | the same estimand in the finite-N process |
| **25.4** | Appendix F, registered in design A4 | now **recovered**: see §4.1 |
| **25.38** | Appendix F, flagged by the owner as unverified | see §4.2 |
| **20.35** | Appendix F | the **bridge-fold hazard** — a different object, see §4.3 |
| 25.9726 ± 0.0246 | Stage 2 | `λ∫A` over the **whole run**, not to any crossing |

### 4.1 The registered 25.4 is recovered

The mean-field `Λ*` at the A = 0.325 marker is **25.4285**, differing from the
registered **25.4** by **+0.0285**. Since 25.4 is quoted to three significant
figures, every value in [25.35, 25.45] rounds to it, and 25.4285 does. The
registered number is therefore consistent with being the mean-field `Λ` at this
marker, computed to the precision at which it is stated.

This is the first independent corroboration of a case-B number in this project.

> **Status note.** The paragraph that follows was written on 2026-10-01 *before*
> Appendices E and F entered the project and before the owner's ruling. It is
> retained as the record of what was known then. It is **superseded**: see §5 for
> the current status of each blocked item and §6 for the verdict. In particular,
> case B is no longer BLOCKED, and the owner's ruling declares A = 0.325 a trajectory
> marker and explicitly *not* "half fold activity".

It
does **not** promote case B out of BLOCKED: the design's registered comparison is
"exact Λ = 25.4 **at half fold activity** versus bridge 20.35", and *half fold
activity* is defined in Appendix C7, which is not in this project. What is now
established is that **if** the marker is A = 0.325, the mean-field Λ is 25.43.
Whether A = 0.325 *is* half case B's fold activity (i.e. whether case B's fold
activity is 0.65) cannot be checked without C7.

### 4.2 On 25.38

25.38 differs from the mean-field value by 0.0485, which is 3.6 × the numerical
uncertainty, so it is **not** reproduced. It does, however, fall squarely on this
solver's own h-ladder, between the h = 0.0025 value (25.37465) and the h = 0.00125
value (25.40161) — i.e. it is where a first-order scheme with h ≈ 0.0024 and no
Richardson extrapolation would land. That is an observation about where the number
sits, **not** a claim about Appendix F's algorithm, which remains unrecovered.
**25.38 stays classified as an unverified numerical reference.**

### 4.3 On 20.35

**20.35 is the bridge-fold hazard and is a different object from `Λ*`.** It is not
an approximation to 25.4 and the difference between them is not an "approximation
error". It is reported here as a distinct quantity and no comparison is drawn,
because the construction that defines it lives in Appendix C7. Stage 2 attempted to
reconstruct the frozen-rate fold from the C2(b) stationary quadrature and **refuted**
that reconstruction on case A (over every frozen dose `d ∈ [c_b, 1)` the saddle-node
of `λ(ν) = ν/P_ν` satisfies `λ_fold ≤ 2.574`, so it cannot place a fold at case A's
λ = 3); that refutation stands and nothing further was attempted.

### 4.4 Finite-N offset — **superseded, see §6**

This section originally reported `Λ*` agent − `Λ*` mean-field = +0.167 (+0.66 %) and
attributed it to finite N. **That was wrong.** The offset was almost entirely an
artefact of the quadrature rule used to accumulate Λ in the Stage 2 harness. With a
trapezoidal rule on a refined grid the offset is **+0.0028**, and an N ladder over
N = 2.5 × 10⁴ … 2 × 10⁵ extrapolates to 25.4289 against the kinetic 25.42849 — a
residual finite-N bias of **7.9 × 10⁻⁴**. Details and the corrected verdict are in
§6.

---

## 5. What remained blocked, and its status after the appendices arrived

§§1–4 were written while Appendices E and F were not in the project. They are now
(`crowd1_appendices_EF_C7_C9.md`), and the owner has ruled on the marker. Current
status:

| item | status at §1–4 | status now |
|---|---|---|
| Case B's **fold activity** | BLOCKED, needed C7 | Appendix F gives `A_fold = 0.65` for case B |
| Whether A = 0.325 is "half fold activity" | BLOCKED | **Moot** — the ruling declares A = 0.325 a trajectory marker and explicitly *not* "half fold activity" |
| The definition of **Λ** in "exact Λ = 25.4" | partially recovered | Confirmed as `λ∫A` to the crossing; the kinetic value 25.42849 recovers 25.4 at its three significant figures |
| The algorithm behind **25.38** | unrecovered | Appendix F identifies it as its own `Λ exact` column, obtained **by simulation at M = 2 × 10⁴** — so its provenance is known but it is still **not** an independently verified reference, and the ruling keeps it unverified |
| The **bridge-fold hazard 20.35** | unrecovered | Appendix F gives it as `Λ_c bridge` with a stated 20 % bridge error; reported as a distinct object, not compared |

Appendix F's own closing note records the same discrepancy this investigation
examined: *"The f_c values in Appendix F were obtained by simulation (N = 5·10⁴,
persistence judged at t = 40) with Monte Carlo error bars, not by an exact
derivation; the design's registered f_c values were taken from this table."*

---

## 6. Correction and verdict (added after the owner's ruling of 2026-10-01)

Two measurement defects were found in the Stage 2 case-B tabulation when the verdict
was computed. Both are numerical, not scientific, and neither touches the kinetic
reference of §3.2.

1. **Quadrature rule.** Λ was accumulated as `np.cumsum(A)*dt*λ` — a right-rectangle
   rule. Over an A(t) falling from 1.0 to 0.325 this biases Λ high by about
   `λ·(dt/2)·(A₀ − A_{t*})`. Measured offset at dt = 0.1: **+0.21209**. The
   trapezoidal rule is used from here on.
2. **Sampling grid.** Refining dt from 0.1 to 0.01 moves the trapezoidal Λ* by only
   0.0084 in total and 0.0013 between the two finest grids, so the grid itself was
   never the problem — the rule was.

| dt | Λ* trapezoid | Λ* right-rectangle (Stage 2's rule) |
|---|---|---|
| 0.1 | 25.43970 | 25.65179 |
| 0.05 | 25.43373 | 25.53795 |
| 0.02 | 25.42997 | 25.47060 |
| 0.01 | 25.43130 | 25.45147 |

**Corrected agent values** (N = 10⁵, 50 replicates, dt = 0.01, trapezoid):
`Λ*` = **25.43130** (mean of replicate crossings) and **25.43138** (crossing of the
mean trajectory); `t*` = 12.90673 and 12.90697 against the kinetic 12.90539.

**N ladder** (dt = 0.02): 25.42212, 25.41926, 25.42997, 25.42812 at
N = 2.5 × 10⁴, 5 × 10⁴, 10⁵, 2 × 10⁵ — flat, with a 1/N extrapolation to **25.4289**
against the kinetic **25.42849**. Residual finite-N bias at N = 10⁵: **7.9 × 10⁻⁴**.

**Verdict** (owner's ruling: A = 0.325 is a declared trajectory marker; compare at
δ = 5 % of the kinetic reference, i.e. ±1.27142):

| estimand | measured | diff | 95 % CI on the diff | δ | status |
|---|---|---|---|---|---|
| mean of replicate crossings | 25.43130 | +0.00281 | [−0.00760, +0.01322] | ±1.27142 | **PASS** |
| crossing of the mean trajectory | 25.43138 | +0.00289 | [−0.00782, +0.01286] | ±1.27142 | **PASS** |

A6 error sources, separated: Monte Carlo 0.0104 (Student-t across 50 replicates) and
0.0103 (bootstrap over traces, B = 2000); finite-N bias 7.9 × 10⁻⁴; numerical
0.01476 (kinetic 0.01344 + residual measurement grid 0.00132); closure error not
applicable — no approximation enters the reference.

25.38 is **not** compared (unverified). 20.35 is reported as the bridge-fold hazard,
a different object; Appendix F's own table gives it as `Λ_c bridge` with
`A_fold = 0.65`, against its `Λ exact at A_fold/2` of 25.38 and a stated 20 % bridge
error.

**On the status of A = 0.325.** The owner's ruling is explicit: *"A = 0.325 is a
declared trajectory marker, not 'half fold activity'."* That is the governing
characterization and it is the one used throughout this file. Separately, and as a
matter of arithmetic only, Appendix F's table happens to list its `Λ exact` column at
`A_fold/2` with `A_fold = 0.65`, whose numeric half is 0.325 — which is presumably
where the value came from. That coincidence is recorded here so the provenance of the
marker is traceable; it does **not** re-import the "half fold activity" reading, and
no verdict in this file rests on it.

---

## 7. Files

- `kinetic.py` — the counter-resolved solver.
- `p6_reference.py` — case A validation, case B reference, agent re-run with traces.
- `outputs/raw/p6_reference.json` — both h-ladders, orders, Richardson values,
  uncertainties, leaks, and both agent estimands at four activity levels.
- `outputs/raw/p6b_historical_interpolation.json` — §2.
- `outputs/raw/p6b_A_mean_trace.npy`, `p6b_cum_mean_trace.npy` — the mean traces.
- `p6b_verdict.py`, `outputs/raw/p6b_verdict.json` — §6: N ladder, grid refinement,
  both quadrature rules, bootstrap, and the two verdict rows.
