# CROWD-1 Stage 1 — reproducibility archive

**Specification version.** `review_packet_v0_6_1.md`, memo section
**PROCESS SPECIFICATION v0.6** (authoritative). Appendices C and D were used only
for the predicted quantities the design points to (C2(d), C5.0, C5(a), C5(b)), never
as alternative specifications.

**Design version.** `crowd1_cs_design_and_manuscript_brief_v0_3.md`, **Part A**
(v0.3, approved for Stage 1 on 2026-10-01). A1 implementation, A2 tests T1–T6,
A3 observable separation, A4a tolerances for zero predictions, A5 controls, A6 pass
rule and error accounting. Part B was not used.

**Scope run.** Stage 1 only = A1 + A2 (T1–T6) under A6. **No item of design section
A4 (P1–P10) was run.** No market layer. Stage 2 is not authorized and nothing in
this archive anticipates it.

**Archive version.** v3. v1 and v2 are retained in full in `outputs_v1/` and
`outputs_v2/`; `BUGLOG.md` entries B1 (v1 → v2) and B2 (v2 → v3) record the two
corrections, both in this harness. v3 is numerically **bit-identical** to v2 — the
run is deterministic from the master seed, and B2 changed four `note` strings only
(verified: maximum absolute difference 0.0 across all 124 rows and all 12 numeric
columns).

**Master seed.** `20261001`. Every per-run seed and every generator stream is derived
from it (see *Seeds* below), so the whole archive reproduces from that one integer.

---

## 1. Result

| test | registered content (A2) | verdict |
|---|---|---|
| **T1** | stopwatch corner: exact lifetime L, interval bounds [L, L₊], final size vs 1−Z=(1−f)e^{−λLZ} | **PASS** (7 rows) |
| **T2** | renewal corner: A* = 1−e^{−λLA*}, camps fixed | **PASS** (2 rows) |
| **T3** | counter law 1+Poisson(∫intensity); class identifiers vs hand table | **PASS** (3 rows) |
| **T4** | cosine identity P(AA)+P(RR)=cos²Δ, 5 Δ × 2 orders × 3 initial laws | **PASS** (61 rows) |
| **T5** | repeated-framing lock: P(AR)=P(RA)=0 pathwise, x=0 | **PASS** (11 rows) |
| **T6** | surrogate (1+cos2Δ·E[τ₁²])/2, both registered closed forms | **PASS** (40 rows) |

124 registered rows, 0 FAIL, 0 INCONCLUSIVE. Full table: `outputs/certified_table.md`
(and `.csv`). Every row carries N, the replicate count, the predicted value, the
discrepancy with its 95% interval, the predeclared δ with its basis, and the four A6
error sources separated.

Headline numbers, read back from the saved table:

- **T1.1** λ = 0: every one of 100 000 agent lifetimes equals
  `L = 0.6931471805599453` **bit for bit** (max |duration − L| = 0.0).
- **T1.2 / T1.3**: over 4 076 792 activated agents (2 154 164 in cell A, 1 922 628
  in cell B, out of 2 550 000 agents simulated per cell across the N ladder),
  **zero** violations of "first active interval ≥ L" and **zero** violations of "no
  activity after L₊", with L₊ − L = 2.0000040×10⁻⁶ at c_b = 0.5 as A2 states.
- **T1.4** cell A (λ=3, f=0.10): Z = 0.844450 vs predicted 0.8445779571,
  d = −1.28×10⁻⁴, CI [−8.4×10⁻⁴, 5.8×10⁻⁴], δ = 0.042229.
  Cell B (λ=2, f=0.30): Z = 0.753861 vs 0.7538196472, d = +4.1×10⁻⁵.
- **T2.2**: A* = 0.500002 vs 0.5, d = +1.8×10⁻⁶, CI [−2.07×10⁻⁴, 2.11×10⁻⁴],
  δ = 0.025. Camps fixed with zero violations.
- **T3a**: counter mean 7.001755 vs 1 + Λ = 6.999728; variance 6.013486 vs
  Λ = 5.999728; pooled goodness of fit to 1+Poisson(Λ) over 10⁶ agents
  χ² = 22.79 on 20 dof, p = 0.299, total variation 1.5×10⁻³.
- **T3b**: 6 deterministic hand cases, 37 checked quantities, every one exact (float
  agreement to ≤ 1 ulp where a real number is compared).
- **T4**: 60 identity rows — process and automaton over 5 Δ × 2 orders × 3 initial
  laws — largest discrepancy 5.94×10⁻⁴ (Δ = 60°, order 2, I1, process) against
  δ = 3/√N = 9.4868×10⁻³. The 30 surrogate rows over the same grid belong to T6, not
  T4; their largest discrepancy is 9.34×10⁻⁴ (Δ = 45°, order 2, I3), so the largest
  over all 90 grid identity rows (60 T4 + 30 T6) is 9.34×10⁻⁴.
- **T5**: P(AR) = P(RA) = 0 over 2×10⁶ agents for process and automaton; final
  convictions exactly {−0.3, +0.9}, so x = 0.000526 (δ = 0.01). Surrogate contrast
  reproduced: P(AA) = P(RR) = 3/8, P(AR) = P(RA) = 1/8, x = 0.250668 vs ¼, with
  final convictions {−0.3, +0.1, +0.5, +0.9} — exactly the four values of C5.2.
- **T6**: 30 surrogate rows against (1 + cos2Δ·E[τ₁²])/2 over the same grid (largest
  discrepancy 9.34×10⁻⁴, Δ = 45°, order 2, I3), plus 10 rows on the two registered
  closed forms — aligned anchor → cos²Δ and isotropic anchor → ½ + ¼cos2Δ, both
  verified at all five Δ (largest discrepancy 4.36×10⁻⁴). 40 rows in all, against the
  same δ; see the closed-form table in `outputs/certified_table.md`.
- **A5 control**: process and automaton compared **pathwise** on a shared seed over
  30 (Δ, order, initial law) cells and 1.5×10⁷ agents — **0** disagreements in the
  outcome pair, the final conviction, the stance, or the counter vector.

---

## 2. What the simulator is

`crowd1/engine.py` is an exact event-driven simulator of the finite-N process. It is
not a mean-field integrator and contains no approximation of the process.

**Four event types** (A1): Poisson broadcast at rate λ per **active** agent, Poisson
reset at ρ, Poisson reconsideration at κ, and **deterministic activity shut-off**.
All four live in one global binary min-heap.

**Shut-off deadlines are in the queue and are refreshed on every conviction change.**
After any event that sets agent i's conviction with |c_i| > c_b, the deadline
`t + ε⁻¹ ln(|c_i|/c_b)` is pushed with that agent's current shut-off version number;
every subsequent conviction change bumps the version, so the superseded entry is
discarded when popped. Because the deadlines are heap entries, **no step can jump
past a deadline** — the failure mode A1 calls a bug is structurally impossible rather
than merely avoided. When an agent's conviction drops to or below c_b at a message,
its pending broadcast is invalidated as well; when it rises above c_b from silence, a
fresh Exp(λ) broadcast time is drawn. While it stays active the pending broadcast is
left alone, which is exact by memorylessness.

**Campaign pulses** are prescribed-time impulses held in a sorted array with a
pointer, *outside* the heap, and they take priority at an exact time tie. All pulses
sharing a time are applied **atomically in declared index order**, so no reset or
reconsideration can occur between coincident pulses. This is not only asserted: hand
case **H5** runs the (T, T) campaign at κ = 1000 with δ = 30°, where an interposed
reconsideration would produce P(AR | A) = sin²30° = ¼, and measures P(AR) = P(RA) = 0
exactly over 10⁵ agents while ~10⁶ reconsideration events fire after the pulses.

**Decay is analytic.** Each agent stores (c_last, t_last) and c(t) = c_last·e^{−ε(t−t_last)}
is evaluated only when needed. Clipping to [−1, 1] is applied at deposits only.

**Message transition** in the specified order: (1) accept with probability
cos²(θ−φ), else reject and φ ← θ+90°; (2) counter increment; (3) deposit
r^(n−1)·cos 2θ·(+α | −β); (4) clip; (5) stance, with the previous stance retained
strictly inside (−c_h, c_h) and at an exact tie.

**Framing classes** are explicit integer identifiers allocated **at angle creation**
by `crowd1/angles.py` from the declared exact integer-degree angles, before any run
starts. Opposite rays share one identifier by construction, and the engine never
recomputes a class from a stored angle — it carries `phi_cls` alongside `phi` and
propagates the identifier of the incoming message. `ClassRegistry.check_consistency`
asserts at configuration time that the allocation agrees with integer mod-90
arithmetic and that θ, θ+90 and θ+180 share an identifier.

**Three agent classes under one engine** (A5, project rule 6): `process`,
`automaton` (state = last framing, last outcome; table cos²(θ_j − θ_i)), and
`surrogate` (anchor a, receptivity τ; τ ← τ cos 2(θ−a), a ← θ, response coin
(1+τ)/2 drawn after the update with no outcome-dependent update, pure-state lift
a₀ = φ₀, τ₀ = 1). Only the acceptance rule and the memory update differ; the
conviction, counter, activity, campaign and clock machinery is shared.

**Recipient draw.** One *other* agent uniformly at random, so the finite-N receiving
hazard is λ·(active others)/(N−1). That is the finite-N process, not an
approximation; it is the origin of the N-ladder bias reported as A6 error source 2.

---

## 3. Seeds

One master seed, `20261001`. For each run,

```
run_seed = derive_run_seed(MASTER_SEED, test_id, cell_id, ..., replicate_index)
```

(splitmix64 chaining, `crowd1/rng.py`). From the run seed, **six independent
generator streams** are derived by stream id, so that changing the replicate count of
one role never shifts another role's numbers. Specification v0.6 requires clocks,
recipient draws and acceptance coins to be mutually independent; they are separate
streams here, not interleaved draws from one.

| stream | role |
|---|---|
| 0 | clocks (broadcast / reset / reconsideration waiting times, and the reconsideration ± coin) |
| 1 | recipient draws |
| 2 | acceptance coins |
| 3 | cohort draw u_i ~ Bernoulli(f) |
| 4 | initial law (I1 / I2 / I3 / two-camp draws) |
| 5 | prescribed exogenous message process (T3a) |

Generator: xoshiro256++ seeded by splitmix64, implemented in both `njit` and plain
Python so the same bit stream is reproducible either side of the kernel boundary.
Integer draws use Lemire rejection (unbiased). Streams 0–2 run inside the kernel,
3–5 on the Python side. Every run seed is listed in `outputs/seeds.json` and on every
row of every raw CSV.

---

## 4. Reproducing

```bash
cd stage1
python run_stage1.py              # ~3.5 min wall, 16 worker processes
python run_stage1.py --serial     # same numbers, single process
```

Environment: Python 3.12.14, numpy 2.5.3, scipy 1.18.1, numba 0.67.0 (conda env
`qcb-numba`); macOS, Apple Silicon. Captured in
`outputs/stage1_results.json → meta`. The `--serial` and pooled runs give identical
numbers: parallelism is over whole runs, each with its own derived seed, and no run
shares state with another.

### Archive layout

```
stage1/
  README.md                 this file
  AMBIGUITIES.md            the ambiguities encountered, with the two readings each
  BUGLOG.md                 bugs / prediction errors / model failures, kept distinct
  run_stage1.py             driver: runs T1-T6, writes everything under outputs/
  config/stage1_config.py   every FIXED and DECLARED value, and the master seed
  crowd1/rng.py             stream-separated xoshiro256++ / splitmix64
  crowd1/angles.py          integer-degree angles; framing-class registry
  crowd1/engine.py          the event-driven kernel (njit)
  crowd1/runner.py          initial laws, cohort, campaign, driver around the kernel
  crowd1/predictions.py     the reference calculations for every registered quantity
  crowd1/handtable.py       the T3(b) hand-computed cases
  crowd1/a6.py              the A6 pass rule and error accounting
  crowd1/tests.py           T1-T6 as written in A2
  outputs/
    certified_table.md      the certified table (human-readable)
    certified_table.csv     the same rows, machine-readable
    stage1_results.json     predictions, measurements, intervals, budgets, diagnostics
    seeds.json              master seed, derivation, and every per-run seed
    raw/t1.1.csv ... a5.csv per-run sufficient statistics (see deviation D5)
    logs/run_log.txt        the run log
  outputs_v1/               retained v1 results (see BUGLOG.md B1)
  outputs_v2/               retained v2 results (see BUGLOG.md B2)
```

---

## 5. A6 δ assignment, declared before the runs

| registered quantity | δ | basis |
|---|---|---|
| T1.1 lifetime = L; T1.2/T1.3 interval bounds; T2.1 camps fixed; T3b hand table; T5 P(AR)=P(RA)=0; A5 pathwise control | 0 | pathwise or structural identities; any violation is a FAIL |
| T1.4 final size Z | 5% of the predicted value | A6 trajectory marker |
| T2.2 stationary A* | 5% of the predicted value | A6 trajectory marker |
| T3a.1/T3a.2 counter mean and variance | 2% of the predicted value | A6 operator check |
| T5 x = 0 | 0.01 absolute | A4a tolerance for zero predictions |
| T4 identity rows; T5 surrogate contrast; T6 rows | 3/√N = 9.4868×10⁻³ | A2 T4 verbatim; declared by analogy for T5-contrast and T6 |

A6's three δ categories do not cover T1.4, T2.2 or T6 explicitly — see
`AMBIGUITIES.md` item 5, which records the reading adopted and notes that both
readings give the same verdicts here. A6's Holm correction is specified across
**primary endpoints**, all of which (P1, P1-delay, P2, P3, P4, P6) are Stage 2 items;
no multiplicity correction applies to T1–T6 and none is specified for them.

**Pass rule, as applied.** The discrepancy d = simulation − prediction is estimated
with a two-sided 95% Student-t interval across replicates (so it carries both
within- and between-replicate Monte Carlo error). PASS when the interval lies inside
[−δ, δ]; FAIL when it is disjoint from [−δ, δ]; INCONCLUSIVE when it overlaps without
being contained, with the replicate count that would resolve it. Pathwise rows are
exact counts, not intervals, and the row states so.

**The four error sources, as separated.**

1. *Monte Carlo* — the half-width of that interval.
2. *Finite-N bias relative to the mean-field prediction* — from the N ladder
   {10³, 10⁴, 10⁵}: the gap between the top two rungs and a 1/N Richardson
   extrapolation, reported per row (`finite_N_bias`). T1 cell A: ladder
   0.848840 → 0.845644 → 0.844450, extrapolated 0.844803, residual at N_max
   3.53×10⁻⁴. T2: 0.4998645 → 0.5004580 → 0.5000018, extrapolated 0.5002375,
   residual 2.36×10⁻⁴. For T4/T5/T6 it is exactly 0: at λ = 0 the agents are
   independent, so there is no finite-N coupling at all.
3. *Numerical error of the theoretical calculation* — the root-finder residual
   mapped through |g′| for the implicit equations of T1 and T2
   (4.1×10⁻¹⁷, 1.3×10⁻¹⁶ and 1.8×10⁻¹⁶ respectively); exactly 0 for the closed forms
   of T3–T6; and the floating-point representation tolerance (10⁻¹², 10⁻¹⁵) stated
   on the pathwise rows, which is a property of binary arithmetic and not of the
   process.
4. *Closure error* — T1's registered equation is the r → 0 limit, in which each
   first-exposed agent is active for exactly L. At r = 10⁻⁶ each agent's duration
   lies in [L, L₊], so solving the same equation at both endpoints gives a **rigorous
   enclosure** of the small-r approximation error: 1.164×10⁻⁶ (cell A) and
   1.127×10⁻⁶ (cell B), reported as `closure_error` and included in the budget as A2
   requires. **0 for T2** — C2(d) labels A = 1 − e^{−λLA} EXACT for the invariant
   two-orientation submodel, so it is not a closure. 0 for T3a (the prescribed input
   is state-independent), and 0 for T4–T6 (exact pathwise or exact finite laws).

---

## 6. Deviations found

A deviation here means any place where the implementation makes a choice the
specification or design does not literally dictate. Each is listed with its
justification and its effect on the certified numbers. There is no deviation that
changes a registered prediction.

**D1 — I2 "φ uniform" is realized on the 180 integer-degree rays.** Specification
v0.6 writes φ ∈ [0°, 180°) continuous, but A1 and project rule 2 require framing-class
identifiers allocated at angle creation and never recomputed from floating-point
angles, and T5's claim *P(AR) = P(RA) = 0 exactly* is unreachable in binary floating
point (cos²90° evaluates to 3.75×10⁻³³, not 0). All angles are therefore exact
integer degrees — every angle the process of T1–T6 can create is one — and `cosd` is
exact at every multiple of 90°. *Effect: none on any registered quantity.* For any
constant c, `(1/180)Σ_{d=0}^{179} cos(2d°+c) = 0` and
`(1/180)Σ_{d=0}^{179} cos(4d°+c) = 0`, so E[cos²(θ−φ)] = ½ and E[cos²2(θ−a)] = ½
**exactly**, as under the continuous law; both are verified to 0 ulp. See
`AMBIGUITIES.md` item 9.

**D2 — at a shut-off deadline the conviction is set to ±c_b exactly** rather than
recomputed as c_last·e^{−εΔt}, which would differ by ~1 ulp. The analytic value at
the deadline *is* ±c_b by construction. *Effect: removes a ~10⁻¹⁶ drift that would
otherwise accumulate over long chains of refreshes; no registered quantity moves.*

**D3 — exact trigonometry at multiples of 90°.** `cosd` returns 1, 0, −1, 0 at
0°, 90°, 180°, 270° instead of `math.cos`'s 6.1×10⁻¹⁷ at 90°. *Effect: makes T5's
pathwise zeros and T2's "camps remain fixed" exact rather than
exact-to-within-10⁻³³.* Without it both would be PASS at any practical tolerance but
not identities.

**D4 — the recipient is drawn from the N−1 other agents**, per the specification's
"one other agent chosen uniformly at random", so the receiving hazard is
λ·(active others)/(N−1) rather than the mean-field λA. *Effect: this is the finite-N
process; the discrepancy it creates against the mean-field predictions is measured
and reported as A6 error source 2, not absorbed.*

**D5 — raw outputs are per-run sufficient statistics, not per-agent state dumps.**
`outputs/raw/*.csv` holds, per run, the quantities every certified number is computed
from: final sizes, realized reach, interval statistics and violation counts (T1),
time-averaged activity (T2), counter moments and goodness of fit (T3), the full
4-cell outcome counts and x (T4/T5/T6), and the pathwise disagreement counts (A5).
Per-agent arrays for all ~2000 runs are not stored; each is regenerable exactly from
the logged seed. *Effect: none on reproducibility; stated so the archive's meaning is
unambiguous.*

**D6 — the reconsideration ± coin is drawn from the clocks stream.** The
specification names three independent families (clocks, recipient draws, acceptance
coins); the ±δ choice belongs to none of them explicitly, and was assigned to the
clocks stream as part of the reconsideration clock event. *Effect: none on any
distribution; a labelling choice, recorded for exact reproducibility.*

**D7 — the surrogate from I3.** C5.0 declares the surrogate only at ρ = κ = 0 and
gives no reset or reconsideration rule for (a, τ). The I3 orientation law is built by
relaxing the **silent** process (c ≡ 0, so no receipt occurs and the surrogate's rule
never fires), after which the surrogate is initialized by its own declared pure-state
lift a₀ = φ₀, τ₀ = 1; ρ and κ are inert in the main phase because the campaign is
coincident and the run ends at the pulse time. Outside that situation the engine
**refuses** to run the surrogate at ρ > 0 or κ > 0 rather than inventing a rule. See
`AMBIGUITIES.md` item 8.

**D8 — the prescribed exogenous message input of T3(a) is a fifth, prescribed event
stream**, outside the four event types of A1. A2 T3 asks for exactly that ("a
PRESCRIBED Poisson message input of known intensity"). It is used in T3(a) only; the
four agent clocks are unchanged, and every other test runs with the four event types
alone.

**D9 — prescribed events (pulses, T3a input) are held in sorted arrays with pointers
rather than in the heap**, and take priority over heap events at an exact time tie.
*Effect: this is what makes coincident pulses atomic and index-ordered, as rule 3
requires; exact ties with a Poisson clock have probability zero, and the only
deterministic coincidence (clock initialization at t = 0 versus a pulse at t = 0) is
resolved in the pulses' favour, which is the rule's intent.*

### Deviations from the design: none

No parameter, prediction, tolerance or rule of design v0.3 Part A was modified. Where
the design is silent on a quantity a run cannot proceed without, the value was
DECLARED in `config/stage1_config.py`, marked as such, fixed before the runs, and
recorded in `AMBIGUITIES.md` with the two readings considered. Those are items 1–5
and 8 there. Items 6, 7 and 9 are readings of the specification text itself.

---

## 7. T3(b) hand table — the derivations

Every expected value below was derived by hand from the MESSAGE TRANSITION of
specification v0.6 and written into `crowd1/handtable.py` in closed form. None was
copied from a run. All six cases pass, with real-valued comparisons agreeing to
≤ 1 ulp.

**H1 — decay between events, deadline refresh, deactivation and reactivation.**
Declared start φ = 90°, c = 0, s = +; α = 0.6, β = 0.4, r = 0.5, c_b = 0.5,
c_h = 0.01, ε = 1, λ = ρ = κ = 0; messages at t = 0, 1, 2, 3 at 90°, 90°, 0°, 90°.
From φ = 90° a 90° message is accepted with probability cos²0 = 1 and deposits
r⁰·cos 180°·(+α) = −0.6, so c = −0.6, s = −, and the agent is active until
t = ln(0.6/0.5) = 0.18232155679395463. At t = 1 the conviction has decayed to
−0.6e⁻¹; the second 90° message is accepted and deposits r¹·cos 180°·α = −0.3, giving
c = −0.5207276647, active again until 1 + ln(c/0.5) = 1.0406190901660604. At t = 2 a
0° message is **rejected** (cos²(0°−90°) = 0), sending φ to 0°+90° = 90° and
depositing r²·cos 0°·(−β) = −0.1. At t = 3 a 90° message is accepted and deposits
r³·cos 180°·α = −0.075. Expected: outcomes (A, A, R, A), counter vector (4) in the
single target class, φ = 90°, s = −, two active intervals totalling
0.2229406469600150, c(6) = −9.074229422188669×10⁻³.

**H2 — clipping, and the post-rejection ray inside the same class.** I1, α = 0.6,
β = 1.0, r = 0.5, c_b = 0.5; coincident pulses (0°, 90°, 0°). Accept at 0° → +0.6;
reject at 90° (cos²90° = 0) → φ ← 180° ≡ 0° and deposit
r¹·cos 180°·(−β) = +0.5, so c = 1.1 **clipped to 1.0**; accept at 0° →
+0.15, c = 1.15 **clipped to 1.0**. Expected: outcomes (A, R, A), counter (3), φ = 0°,
s = +, one interval ending at ln(1/0.5) = ln 2.

**H3 — class identifiers.** I1, α = β = 0; coincident pulses at
40°, 130°, 40°, 90°, 0°, 70°. The counter advances once per receipt **irrespective of
the outcome**, so the counter vector is a deterministic fingerprint of the class
assignment. 40° and 130° are opposite rays of one basis (130 mod 90 = 40), 90° and 0°
are the target basis, 70° is a third. Expected: 3 classes and counter vector
(2, 3, 1) for (target, {40,130}, {70,160}) — which is what the engine produces, with
`class_of(40) = class_of(130) = 1` and `class_of(0) = class_of(90) = 0`.

**H4 — "previous stance retained at an exact tie."** Declared start φ = 90°, c = 0.5,
s = ±1; c_h = 0, α = 0.5, r = 1; one pulse at 90°, accepted, depositing
cos 180°·0.5 = −0.5, so c = 0 **exactly**. With c_h = 0 both branches of the stance
rule fire at once; the previous stance must be retained. Run for s₀ = +1 and
s₀ = −1; both retained.

**H5 — no reset or reconsideration between coincident pulses.** I2, coincident
(T, T) = (0°, 0°), κ = 1000, δ = 30°, N = 10⁵, c_b = 0.95. An interposed
reconsideration would move φ to T_s ± 30° and give P(AR | A) = sin²30° = ¼. The
specification forbids it, so the pathwise-exact value is P(AR) = P(RA) = 0. Measured:
0 and 0, with 999 247 reconsideration events firing after the pulses — the clock is
demonstrably live.

---

## 8. Reported, but not acceptance conditions

A2 T3 states that the full-system formula `1 + Poisson(λ∫A_j)` *"is a mean-field
statement and is run as a convergence check across the N ladder, not as a finite-N
acceptance condition."* It is therefore reported with **no verdict**:

| N | mean (counter − 1) | λ∫A | mean − λ∫A | var (counter − 1) | var − λ∫A | χ²/dof |
|--:|--:|--:|--:|--:|--:|--:|
| 10³ | 1.736413 | 1.751411 | −0.014998 | 1.755281 | +0.003870 | 0.854 |
| 10⁴ | 1.758169 | 1.752513 | +0.005656 | 1.781194 | +0.028681 | 0.970 |
| 10⁵ | 1.755762 | 1.755791 | **−0.000028** | 1.762311 | +0.006520 | 1.019 |

The A5 independent-seed comparison of the automaton against the process is likewise
reported without a verdict (maximum total-variation distance 1.363×10⁻³ at 2×10⁶
agents per arm, minimum χ² p-value 0.0228 over 30 cells) — a Monte-Carlo-estimated
distance cannot carry a zero-tolerance verdict, which is the substance of `BUGLOG.md`
B1. The verdict-bearing form of that control is the pathwise one.

---

## 9. Stop point

Stage 1 is complete. Per the project instructions, **nothing further is run** in this
project until a written "Stage 2 authorized" message arrives from the owner. Design
v0.3 also conditions Stage 2 on the A4a endpoint definitions being frozen, which is
not a Stage 1 deliverable and has not been done here.
