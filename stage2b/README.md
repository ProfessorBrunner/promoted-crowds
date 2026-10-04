# CROWD-1 Stage 2B — discrepancy investigation

**Specification** `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION
v0.6" (authoritative).
**Design** `crowd1_cs_design_and_manuscript_brief_v0_3.md`, Part A (authoritative).
**Authorisation** Stage 2B, 2026-10-01, as a **discrepancy investigation, not a
re-certification**. Stage 3 is not authorised.

**No Stage 1 or Stage 2 verdict is changed by anything in this directory.** The
Stage 2 record stands at 32 PASS, 3 INCONCLUSIVE, 2 FAIL, with Holm rejecting P4
only. Nothing was tuned. No parameter, prediction, tolerance or rule was modified.

Environment: `qcb-numba` (Python 3.12.14, numpy 2.5.3, scipy 1.18.1, numba 0.67.0),
macOS arm64, 32 cores. Master seed **20261002**, inherited from Stage 2 so that
state preparation reproduces the Stage 2 backgrounds exactly.

---

## The three tasks and what they found

### Task 1 — P1-delay estimator audit → `REPORT_task1_P1delay_audit.md`

The quantity Stage 2 reported is a **frozen-background proxy**: recipients'
orientations *and* convictions held at their post-campaign values for the whole of
the seed's life; `max_gen = 1`, so offspring lifetimes never enter; not the
stationary operator (that is its τ₀ → ∞ limit).

Its between-order ratio is **exactly 1 at τ₀ = 0**, and the reason is substantive,
not a bug: from initial law I2 the maximally mixed orientation law is invariant under
every projection (**R8(b)**), so `E[cos²φ_post] = ½` for *both* campaign orders. The
frozen orientation channel carries no order information at all; the whole advantage
lives in the stance channel and only resets can express it.

The owner's estimand — the time-dependent first-generation count with the background
relaxing during the seed's life — was then measured on the same saved states. Its
ratio is **greater than one at every delay**: 1.275, 1.549, 1.715, 1.874, 1.959,
1.963 at τ₀/ρ = 0, 0.5, 1, 2, 5, 10, against exact 1.2702501, 1.5455197, 1.7124792,
1.8751663, 1.9651325, 1.9698145. The owner's reference formula
`E Z₁ = (λ/2)[L + x_j(L − ½)]` was independently re-derived from
`E Z₁(τ₀) = λ∫₀^L q_T(τ₀ + s) ds` and agrees **bit for bit** in IEEE double.

Logged as category **E** (estimand mismatch) — a new category, distinct from B, A
and M. The registered sentence stays failed in the record; a replacement naming the
proxy as a proxy is *proposed*, not adopted.

### Task 2 — P4 independent kinetic reference → `REPORT_task2_P4_kinetic.md`

A deterministic measure solver (`kinetic.py`) sharing no code with the agent
simulator: no event queue, no RNG, no agent. Validated against the C2(b) stationary
quadrature to **1.8 × 10⁻⁶** after Richardson extrapolation, with measured
convergence order 1.016 / 1.006 / 1.002.

| λ | kinetic `f_c^MF` | Stage 2 agent `f₅₀` | Appendix F |
|---|---|---|---|
| 1.60 | 0.132734 ± 0.00093 | 0.133422 [0.132588, 0.134220] | 0.1270 ± 0.0020 |
| 1.75 | 0.044097 ± 0.00048 | 0.043815 [0.043361, 0.044434] | 0.0380 ± 0.0010 |
| 1.90 | 0.007094 ± 0.00026 | 0.007310 [0.006476, 0.007633] | 0.0086 ± 0.0008 |

Overlaps the agent interval at all three λ; **disjoint** from Appendix F at all
three. Horizon sensitivity is exactly zero (T = 120 and T = 240 give identical
boundaries to eight digits). A `t = 40` criterion does not recover Appendix F.
Finite-N offsets are sub-unity multiples of `√(f(1−f)/N)` and alternate in sign.

**Category assigned: A** — error in the registered prediction, not model failure.
Appendix F's `f_c` and its 0.75 prefactor remain OPEN.

### Task 3 — P6 case B reference → `REPORT_task3_P6_caseB.md`

Same solver, counter-resolved (r = 0.95 is not inert), validated on case A:
Richardson `t† = 70.32769 ± 0.02435` against the registered **70.3 ± 0.1**.

Case B at the marker A = 0.325:

- **`t*`^MF = 12.90539 ± 0.00305**, **`Λ*`^MF = 25.42849 ± 0.01344** (order ≈ 1.00
  over four halvings).
- Agents, 50 replicates at N = 10⁵, **both estimands reported** (corrected
  quadrature, dt = 0.01): mean of replicate crossings `t*` = 12.90673,
  `Λ*` = **25.43130**; crossing of the mean trajectory `t*` = 12.90697,
  `Λ*` = **25.43138**. The two estimands differ by 8 × 10⁻⁵.
- Historical recovery from the existing Stage 2 tabulation: `t*` = 12.89821,
  `Λ*` = 25.58064, **interpolation error ≤ 0.0062 and ≤ 0.0240** — and the direct
  measurement, made afterwards, falls inside both bounds.

**The registered 25.4 is recovered** as the mean-field Λ at this marker, to the three
significant figures in which it is stated. **25.38 is not reproduced** (3.6 × the
numerical uncertainty) and stays an unverified numerical reference. **20.35 is the
bridge-fold hazard, a different object**, reported as such and not compared.

**Verdict (added under the owner's ruling of 2026-10-01, which declares A = 0.325 a
trajectory marker): PASS on both crossing estimands**, diff +0.00281 and +0.00289
against δ = ±1.27142. Two numerical defects in the Stage 2 harness were corrected
first — a right-rectangle quadrature for Λ (offset +0.21209 at dt = 0.1) and a coarse
sampling grid. The "+0.167 finite-N offset" reported in the first version of task 3
was that artefact: the true residual finite-N bias is 7.9 × 10⁻⁴, from an N ladder
over 2.5 × 10⁴ … 2 × 10⁵ that extrapolates to 25.4289 against the kinetic 25.42849.
Per the owner's ruling, A = 0.325 is a **declared trajectory marker, not "half fold
activity"**; Appendix F's listing of its `Λ exact` column at `A_fold/2` with
`A_fold = 0.65` is recorded only as the marker's likely provenance, and no verdict
rests on it.

---

## Deviations found

1. **Appendices C7, C8, C9 and F are not in this project.** The review packet's
   Appendix C and Appendix D both stop at C6. Design A4 cites C7 (P6), C8 (P1) and
   C9 (P4, P7); the owner's Stage 2B statement cites Appendix F (P4's `f_c` and its
   0.75 prefactor; P6 case B's 25.38). Design B7 says they are separate attachments.
   Consequences are recorded per item in `AMBIGUITIES.md`.
2. **One optional parameter was added to Stage 2 code.** `crowd1/operator.py` gained
   `relax_rho`, whose default `0.0` reproduces the Stage 2 behaviour **bit for bit**
   — verified by re-running the Stage 2 P1 operator cell against the archived
   `stage2/outputs/raw/p1_operator.csv` (all six delays identical). This is the only
   edit to any Stage 2 file.
3. **`ProcessPoolExecutor` is unavailable in this sandbox** (`PermissionError` on
   `SC_SEM_NSEMS_MAX`); `multiprocessing.get_context("spawn").Pool` is used, as in
   Stages 1 and 2. No scientific content affected.

One harness bug was found and fixed during Stage 2B (`BUGLOG.md`, S2B-1, a basin
classifier that rejected a legitimately dying trajectory). It produced no numbers.

---

## Layout

```
kinetic.py                        independent measure solver (no agent, no RNG)
p1delay_reference.py              task 1: both estimands + exact references
p4_reference.py                   task 2: basin classifier, bisection, refinement
p6_reference.py                   task 3: case A validation, case B reference, agent re-run
REPORT_task1_P1delay_audit.md     task 1 report
REPORT_task2_P4_kinetic.md        task 2 report
REPORT_task3_P6_caseB.md          task 3 report
AMBIGUITIES.md                    S2B-A1 .. S2B-A5
BUGLOG.md                         S2B-1 .. S2B-3
outputs/stage2b_summary.csv       every headline number in one table
outputs/p4_comparison.csv         task 2 comparison
outputs/raw/*.json, *.npy         all raw results, every seed
outputs/logs/*.log                run logs
```

## Reproduction

```
cd stage2b
python p1delay_reference.py      #  ~3 min, 16 spawn workers
python p4_reference.py           # ~35 min, serial
python p6_reference.py abc       # ~30 min, serial kinetic + 16-worker agent re-run
```

Each writes its own JSON under `outputs/raw/`. `p6_reference.py` is restartable by
part (`a`, `b`, `c`, or any combination).

## Scope

Only Stage 2B was run. **Stage 3 is not authorised**; its five tests (P5, P7, P8,
P9, P10) are released test by test on separate written authorisation after the
Stage 3 estimand definitions are confirmed.
