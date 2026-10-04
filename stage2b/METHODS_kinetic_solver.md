# Methods — deterministic kinetic reference solver

*Drop-in block for the manuscript's Methods. Every statement is a property of
`stage2b/kinetic.py` as run; settings per reference are in the table at the end.*

## Equation integrated

The solver integrates the mean-field measure equation directly. It shares no code
with the agent simulator: there is no event queue, no random number generator and no
representation of an agent. At r = 1 the framing counters are inert, so with dose
d = α the law is

    d/dt ⟨ψ, μ_t⟩ = ⟨ −εc ψ′(c) + λA(t)[ψ(min{1, c+d}) − ψ(c)], μ_t ⟩,
    A(t) = μ_t((c_b, 1]),    μ_0 = (1−f) δ_0 + f δ_{min(1,α)}.

At r < 1 the counter is resolved: the state is (c, n), the deposit on a receipt from
slab n is d_n = α r^n with n the **pre-receipt** count, and

    d/dt ⟨ψ, μ_t^{(n)}⟩ = ⟨ −εc ψ′, μ_t^{(n)} ⟩ − λA(t)⟨ψ, μ_t^{(n)}⟩
                          + λA(t)⟨ψ(min{1, · + d_{n−1}}), μ_t^{(n−1)}⟩,
    A(t) = Σ_n μ_t^{(n)}((c_b, 1]).

An optional constant drive replaces the self-consistent rate λA(t) by a prescribed
ν; the long-time activity is then the stationary response P_ν of C2(b), which is
what the fold construction needs.

## Conviction grid

Uniform in **u = log c** on [log c_min, 0], because in that variable the decay
ċ = −εc becomes uniform translation u̇ = −ε. Given a requested step h the solver
sets U = −log c_min, J = round(U/h), and then **resets h ← U/J** so the grid fits
the interval exactly; the reported h is this adjusted value, which is why the
ladders read 0.008001, 0.003999, … rather than exact powers of two. The grid has
J+1 edges with the top edge at u = 0, i.e. c = 1. Mass is piecewise constant in u
within a cell, so the activity is

    A = Σ_j W_j · clip( (u_{j+1} − log c_b)/h , 0, 1 ),

the exact u-uniform fraction of each cell lying above c_b — no cell is counted
all-or-nothing.

## Time step, substep ordering and durations

The time step is tied to the grid, **dt = h/ε**, with n_steps = ⌈T/dt⌉.

**There are no half-steps.** Each time step is two *full-dt* passes of the same
Lie–Trotter composition, the first of which is discarded:

| pass | duration of each substep | rate used | fate |
|---|---|---|---|
| 1 — predictor | jump dt, then transport dt | ν = λA(t) | **discarded**; its only output is A_pred |
| 2 — accepted | jump dt, then transport dt | ν̄ = ½(λA(t) + λA_pred) | kept |

Concretely: the state is copied; pass 1 applies the jump semigroup over the full dt
and then transports; A_pred is read off; the state is **restored from the copy**; pass
2 applies the jump over the full dt at the averaged rate and transports again. So
each substep lasts dt, not dt/2, and the transport moves exactly **one cell = h in
u**, which is exactly dt·ε of decay (c ← c e^{−h} = c e^{−ε dt}). Under a prescribed
constant ν no averaging is applied and pass 1 is skipped.

The one-cell shift is therefore **exact for the drift**: a piecewise-constant-in-u
measure decaying for exactly dt lands on the grid with no interpolation and no
numerical diffusion.

**What the exactness does *not* buy, and what an earlier version of this section got
wrong.** The drift substep being exact does not make the drift's contribution to the
scheme's error zero, and the leading error is *not* in the jump map. Composing
"jump over dt" with "transport over dt" in a fixed order is a **first-order
Lie–Trotter splitting**, whose commutator error is O(dt). It is **one of two** O(dt)
contributions and not the only one: the top-cell projection of clipped
mass (boundary item 1 below) advances that mass's decay by up to one time step, which
is first order in dt as well. **The refinement ladders measure the two together and
do not separate them**, so they are reported as one combined first-order
contribution rather than apportioned between the two mechanisms — apportioning them
would need a diagnostic that varies one while holding the other fixed, which was not
run. The error budget, largest first:

| source | order | status |
|---|---|---|
| **operator splitting** (jump ∘ transport, fixed order) **+ top-cell projection of clipped mass** | **O(dt) = O(h/ε), combined** | **dominant**; this combined term is what every ladder measures, and the ladders do not resolve its two parts |
| deposit interpolation (conservative, linear in u) | O(h²) in position, exact in mass | subdominant |
| Heun on the coupling rate | O(dt²) in the rate | subdominant |
| jump-series truncation at K | O((ν dt)^{K+1}) | laddered to 9.4×10⁻¹¹ at K = 3 |
| transport | exact | — |
| conviction floor c_min | O(c_min), **h-independent** | laddered separately (§ refinement) |

Every refinement ladder in §"Settings" shows an observed order p between 1.00 and
1.06, which is the **combined** first-order term — operator splitting together with
the top-cell projection, in a proportion these ladders do not resolve. A second-order
(Strang) composition was not used; note that it would reduce the splitting part only,
leaving the projection's O(dt) contribution in place. The first-order rate is instead
measured and extrapolated away.

## Jump map and counter cutoff K

The jump half-step applies the **exact pure-jump semigroup**

    exp(ν dt (J − I)) = e^{−ν dt} Σ_{k=0}^{K} (ν dt)^k J^k / k!,

truncated at k = K, so the "two receipts in one step" error that a single-jump
scheme carries is removed to order (ν dt)^{K+1}. All production runs use **K = 3**.
K is not a conviction cutoff and not a counter bound: it is the truncation order of
this exponential series. It was laddered — the spread of P_ν over K = 3, 6, 10 is
**9.4×10⁻¹¹** at every floor tested — so K = 3 is converged and contributes
nothing to the error budget.

Within the jump map, deposits are placed by **conservative linear-in-u
interpolation**: mass at position p contributes weight w₀ = 1 − frac to cell i₀ and
w₁ = frac to cell i₀+1, where frac is the fractional part of
(log p − u_centre,0)/h. Mass is conserved exactly by construction.

The counter dimension is separate. At r = 1 one slab represents the whole joint law
exactly. At r < 1 the solver allocates one slab per counter value, by default
n_slabs = ⌊λT + 8√max(λT,1) + 16⌋ — eight standard deviations of head-room over the
crude bound Λ ≤ λT on a Poisson counter. Mass that would advance past the last slab
is accumulated in a reported `slab_leak`; in the production runs it is between
6.8×10⁻⁵⁹ and 1.5×10⁻⁵⁷, i.e. nil.

## Boundary treatment

Three boundaries, each exact or with a bounded and now-laddered error:

1. **Top (c = 1).** The top grid edge is exactly c = 1, and the clip of the
   specification is applied to the deposit *position* first (p ← min(p, 1)), which is
   exact. The clipped mass is then **not** held as an explicit atom at c = 1: it is
   placed entirely in the **top cell** (index J−1, spanning u ∈ [−h, 0], i.e.
   c ∈ [e^{−h}, 1]) with interpolation weights forced to (1, 0). This is the
   asymmetry with the bottom boundary, which *is* an explicit atom (item 2). Its
   projection error: mass that should sit exactly at c = 1 is represented as the
   cell's u-uniform occupant, so its subsequent decay to any level below the cell
   runs **early by up to h in u, i.e. by up to one time step dt**. The qualification
   matters: the projection does not affect A **immediately on deposition** — the
   whole top cell lies above c_b whenever c_b < e^{−h}, which holds in every run
   here, so the deposit lands on the correct side of the threshold either way. It
   *does* affect A later, because the projected mass reaches c_b up to one time step
   early. That is a first-order-in-dt effect, and it is **not separable from the
   operator-splitting error by the ladders run here**; the two are reported as one
   combined O(dt) term in the budget above.
2. **Bottom (the floor c_min).** Mass transported out of the lowest cell is pooled
   into an **atom at c = 0**, which has zero drift velocity and therefore persists.
   This atom is not inert: it receives deposits through its own interpolation
   weights at position d_n, so floor mass is promoted correctly when it receives.
   The pooling introduces a position error bounded by c_min — the only
   h-independent error in the scheme, and the one that required the separate floor
   ladder described below.
3. **Initial law.** μ₀ = (1−f) δ_0 + f δ_{min(1,α)}. The campaign pulse is counted
   as the cohort's **first** receipt, so the cohort starts at min(1, α) with counter
   1 and the remainder at c = 0 with counter 0.

Total mass W.sum() + m₀.sum() is reported for every run as `mass`; the deficits over
the production ladders run from 9.2×10⁻⁵ at the coarsest grid to 1.5×10⁻⁶ at the
finest.

## Coupling

The self-consistent rate is advanced by **Heun's method** (explicit trapezoid):
a predictor half-step at ν = λA(t), then the accepted step at
ν̄ = ½(λA(t) + λA_pred). Under a prescribed constant ν both half-steps use that ν
and no averaging is applied, so the prescribed-rate path is a pure fixed-rate
integration.

## Refinement and error reporting

Three parameters are refined independently, and their contributions are reported
separately, never combined:

- **Grid/step h.** Halving ladder. The observed order is measured from consecutive
  differences, p = log₂|d₁/d₂|; the reported value is the order-1 Richardson
  extrapolation v_∞ = v_last + (v_last − v_prev), and the reported **numerical (h)
  error is the last Richardson increment** |v_last − v_prev|, not an assumed rate.
- **Horizon T.** Checked by doubling (e.g. T = 120 against T = 240 for the P4 basin
  boundary, T = 30/60/120 for the stationary P_ν). Where the quantity is a property
  of the flow rather than of the window, this is zero to all printed digits and is
  reported as zero.
- **Floor c_min.** Laddered separately, because the floor error is
  **h-independent**: refining h drives the discretization error to zero and leaves
  the floor error untouched, so an h-ladder alone converges to a biased limit while
  reporting a small Richardson increment. This was discovered the hard way
  (BUGLOG S2B-4) and every certified kinetic reference has since been
  floor-laddered; see `REPORT_floor_audit.md`. One trap in doing so: changing c_min
  changes U and hence the adjusted h = U/round(U/h), so a floor comparison at one
  *requested* h compares two different *actual* h. Compare at matched adjusted h —
  c_min = 10⁻² against 10⁻⁴ gives U₂/U₁ = 2 exactly, hence J₂ = 2J₁ and identical h.

## f_c basin classifier

The critical reach f_c is the boundary between the extinction and ignition basins,
located by bisection on f. At r = 1 the mean-field flow has exactly two attractors,
A = 0 and the upper branch A*(λ), separated by the unstable middle branch whose
activity at the saddle-node is A_fold. The classifier uses that structure rather
than an absolute cut on A:

    ignite        if A(T) > ½ A*(λ)
    die           if A(T) < ½ A_fold  AND  A(T) ≤ A(T − dt)
    unclassified  otherwise

— below the fold activity **and still decreasing** means the trajectory is in the
extinction basin, because there is no attractor in between. Anything else **raises**
rather than being forced into a basin; no run in the production ladders raised. The
earlier version of this classifier used an absolute cut A(T) < 10⁻⁶ and aborted on a
trajectory at 1.118×10⁻⁶ that was on its way to zero (BUGLOG S2B-1).

Thresholds come from the registered predictions, not from the solver:
A*(1.60) = 0.6366173, A*(1.75) = 0.7471937, A*(1.90) = 0.8133804, and
A_fold = 0.3755739 from the exact C2.11–C2.14 quadrature in
`predictions_s2.p4_fold()`.

**Tolerance.** Bisection stops when the bracket width falls below
tol = 10⁻⁶; the reported f_c is the bracket midpoint and the reported bisection
half-width is (hi − lo)/2, which comes out at 2.6×10⁻⁷ to 4.3×10⁻⁷ across the runs.
The starting bracket matters at that precision: the floor/horizon comparisons are
bisected from the wide bracket ([0.10, 0.20], [0.02, 0.10], [0.002, 0.03]) so that
the two settings being compared are treated identically, whereas the h-ladder
re-brackets each rung around the previous one. The two therefore land on different
points of the same interval — at λ = 1.60, h = 0.004 they give 0.13648643 and
0.13648692 — and that 4.9×10⁻⁷ gap is the bisection tolerance plus the
bracket-endpoint shift, three orders of magnitude below the grid uncertainty.

## Refinement ladders, with successive values and observed orders

Each ladder halves h. `diff` is v(h/2) − v(h); the observed order is
p = log₂|diffₙ/diffₙ₊₁|; the Richardson limit is v_last + (v_last − v_prev) and the
reported numerical (h) error is |v_last − v_prev|. Every p lies between 1.00 and
1.06 — the combined first-order term identified above (operator splitting + top-cell
projection, not resolved into parts), and nothing faster.

### P4 — basin boundary f_c^MF (T = 120, floor 10⁻³ as run; α = 0.5, c_b = 0.3, r = 1)

| λ | h | f_c | diff | p |
|---|---|---|---|---|
| **1.60** | 0.008000 | 0.14032707 | — | — |
|  | 0.004000 | 0.13648692 | -3.840e-03 | — |
|  | 0.002000 | 0.13460228 | -1.885e-03 | 1.027 |
|  | 0.001000 | 0.13366797 | -9.343e-04 | 1.012 |
| | *Richardson* | **0.13273366** | *h error* | **9.34e-04** (reported order 1.0123) |
| **1.75** | 0.008000 | 0.04801910 | — | — |
|  | 0.004000 | 0.04604016 | -1.979e-03 | — |
|  | 0.002000 | 0.04506484 | -9.753e-04 | 1.021 |
|  | 0.001000 | 0.04458089 | -4.840e-04 | 1.011 |
| | *Richardson* | **0.04409694** | *h error* | **4.84e-04** (reported order 1.0110) |
| **1.90** | 0.008000 | 0.00921832 | — | — |
|  | 0.004000 | 0.00814185 | -1.076e-03 | — |
|  | 0.002000 | 0.00761507 | -5.268e-04 | 1.031 |
|  | 0.001000 | 0.00735457 | -2.605e-04 | 1.016 |
| | *Richardson* | **0.00709407** | *h error* | **2.61e-04** (reported order 1.0159) |

The floor-corrected values that supersede these three Richardson limits are in
`REPORT_floor_audit.md` §3: 0.13268101, 0.04406947, 0.00708210. The floor shift is
h-independent, so it leaves every `diff` and every p in this table unchanged.

### P6 case A — t† and Λ at A_f = 0.5603 (T = 95, floor 2×10⁻²; α = 2, r = 0.99, λ = 3, c_b = 0.5, 436 slabs)

| quantity | h | value | diff | p |
|---|---|---|---|---|
| **t†** | 0.0100052 | 70.228247 | — | — |
|  | 0.0050026 | 70.278978 | +5.073e-02 | — |
|  | 0.0024997 | 70.303333 | +2.435e-02 | 1.059 |
| | *Richardson* | **70.327688** | *h error* | **0.024355** (reported order 1.0586) |
| **Λ(t†)** | 0.0100052 | 165.780887 | — | — |
|  | 0.0050026 | 166.627026 | +8.461e-01 | — |
|  | 0.0024997 | 167.038058 | +4.110e-01 | 1.042 |
| | *not extrapolated* | — | — | Λ(t†) is not a registered endpoint |

### P6 case B — t* and Λ* at A = 0.325 (T = 40, floor 10⁻²; α = 1, r = 0.95, λ = 2.5, c_b = 0.4, 196 slabs)

| quantity | h | value | diff | p |
|---|---|---|---|---|
| **t*** | 0.00998952 | 12.856209 | — | — |
|  | 0.00500018 | 12.880884 | +2.468e-02 | — |
|  | 0.00250009 | 12.893164 | +1.228e-02 | 1.007 |
|  | 0.00125005 | 12.899282 | +6.118e-03 | 1.005 |
|  | 0.00062502 | 12.902335 | +3.053e-03 | 1.003 |
| | *Richardson* | **12.905389** | *h error* | **0.003053** (reported order 1.0025) |
| **Λ*** | 0.00998952 | 25.211074 | — | — |
|  | 0.00500018 | 25.320462 | +1.094e-01 | — |
|  | 0.00250009 | 25.374649 | +5.419e-02 | 1.013 |
|  | 0.00125005 | 25.401612 | +2.696e-02 | 1.007 |
|  | 0.00062502 | 25.415049 | +1.344e-02 | 1.005 |
| | *Richardson* | **25.428485** | *h error* | **0.013437** (reported order 1.0048) |

Floor-corrected: t* = 12.905457, Λ* = 25.428608 (`REPORT_floor_audit.md` §5).

## Adaptive replicate rule for outbreak probabilities

Two call sites, both in `stage2/stage2_items.py`. A pilot of **50** replicates is run
first, p̂ is the pilot's outbreak fraction, and the target replicate count is

    need = ceil( (1.96 / target)^2 * max( p_hat*(1 - p_hat), floor_var ) )
    need = min( max(need, pilot), cap )

| call site | used by | target | variance floor | pilot | cap |
|---|---|---|---|---|---|
| `_p1_pop` | P1 (`DELTA_OUTBREAK_ABS`) | 0.03 | 0.01 | 50 | **1200** |
| `_generic_pop` | P2 (`outbreak_precision_target`) | 0.02 | 0.004 | 50 | **1200** |

Three things to note about this rule, stated rather than left implicit:

- The multiplier is the **normal** 1.96, not a Student-t quantile, and p̂(1−p̂) is the
  normal-approximation variance — so `need` is a normal-approximation sample size
  even though the interval finally reported is Wilson.
- The **variance floor** (0.01 for P1, 0.004 for P2) is what stops a zero-count pilot
  from terminating at the pilot: with p̂ = 0 the unfloored formula would give
  need = 0, hence need = max(need, 50) = 50 and no extension. With the floor it gives
  need = ⌈(1.96/0.03)² × 0.01⌉ = 43 for P1 and ⌈(1.96/0.02)² × 0.004⌉ = 39 for P2,
  both below the pilot — so **a 0/50 cell is never extended** and stops at 50
  replicates by construction. Those are exactly the cells that miss the precision
  target (next section).
- The **N = 10⁶ diagnostic cells at λ = 2 are outside this rule entirely.** They
  were run as a **fixed 50-replicate design**, not piloted and not extended, so no
  precision target applies to them and they carry no `meets_*_target` flag. Had the
  adaptive rule been applied to the realised 18/50 it would have asked for
  ⌈(1.96/0.03)² × 0.36 × 0.64⌉ = **984 replicates**; 50 were run. Their Wilson
  interval is correspondingly wide — 18/50 gives [0.2414, 0.4986], half-width
  0.1286 — and that is a property of the fixed design, not a failure of the adaptive
  one. The cell is plotted on F2 as a diagnostic marker with its interval shown.
- The **cap is 1200 replicates** and it never bound: the largest realized count
  anywhere in Stage 2 is 1157 (P2, order (10,30,20)), and the P1 extensions reached
  958, 1006, 1052 and 1157.

`need` is a function of the pilot, and the pilot is **pooled** into the reported
estimate, so the final sample size is data-dependent; fixed-sample Wilson and t
intervals are reported nominally and coverage under this design is **not assessed**
(owner ruling S2B-A7, ledger item "A6 sampling design").

### Why three extended cells still miss the ±0.03 target

`_p1_pop`'s docstring said the rule tops up "to the replicate count that meets the
±0.03 target". It does not, and three cells show it. The flags in the raw JSON and in
`F2_outbreak_probability.csv` are correct as recorded — all three read
`meets_0p03_target: false` — and this note reconciles them with the rule that produced
the counts.

| cell | pilot | → need | realized | Wilson half-width | target | outcome |
|---|---|---|---|---|---|---|
| P1 (40, 140, 50) | 17/50 | 958 | 440/958, p̂ = 0.4593 | **0.031494** | 0.03 | **MISSED** |
| P1 (40, 50, 140) | 19/50 | 1006 | 345/1006, p̂ = 0.3429 | **0.029284** | 0.03 | **MET** |
| P1 (40, 140, 50) | 46/50 | 315 | 275/315, p̂ = 0.8730 | **0.036822** | 0.03 | **MISSED** |
| P1 (140, 40, 50) (held out) | 22/50 | 1052 | 504/1052, p̂ = 0.4791 | **0.030133** | 0.03 | **MISSED** |
| P2 (10, 30, 20) | 7/50 | 1157 | 75/1157, p̂ = 0.0648 | **0.014237** | 0.02 | **MET** |

The mechanism is the one-shot sizing, not a coding error and not the cap: `need` is
computed **once, from the pilot's p̂**, and is never revised as the estimate moves.
A cell misses exactly when the realized p̂(1−p̂) comes out above the pilot's:

| cell | variance assumed (pilot) | variance realized | n needed at the realized p̂ | shortfall |
|---|---|---|---|---|
| (40, 140, 50) | 0.224400 | 0.248343 | 1061 | +103 |
| (40, 50, 140) | 0.235600 | 0.225333 | 962 | -44 |
| (40, 140, 50) | 0.073600 | 0.110859 | 474 | +159 |
| (140, 40, 50) (held out) | 0.246400 | 0.249563 | 1066 | +14 |
| (10, 30, 20) | 0.120400 | 0.060621 | 583 | -574 |

The two cells that met the target are precisely the two whose realized variance came
in *below* the pilot's estimate (0.2253 < 0.2357 and 0.0606 < 0.1205). **No cell
reached the 1200 cap**, so the cap is not implicated in any miss; the largest realized
count is 1157 and the largest shortfall is 159 replicates.

The pilot counts above are recovered by inverting `need`, which fixes
p̂_pilot(1−p̂_pilot) exactly and therefore the pilot count **up to the p ↔ 1−p
reflection**; the branch quoted is the one consistent with the realized p̂ (the
alternatives are 33/50, 31/50, 4/50, 28/50 and 43/50 respectively). This is an
inference from the recorded replicate count, not a separately logged quantity.

A rule that iterated — re-sizing from the running p̂ and continuing until the realized
half-width meets the target — would close these three gaps, at the cost of a stopping
rule whose coverage would need its own analysis. That change is **not** made here: the
replicate counts are part of the certified Stage 2 record and no number is re-run.
What changes is the claim: the rule *targets* ±0.03, it does not *guarantee* it, and
the three cells that miss are flagged in every artifact that reports them.

### The stopped cells

A cell with 0 outbreaks in 50 replicates has Wilson interval **[0, 0.071348]** —
upper endpoint 0.071348, **half-width 0.035674**. The half-width is what the A4a
precision targets bound, and it exceeds both: 0.0357 > 0.03 (P1) and > 0.02 (P2).
These cells are flagged `meets_0p03_target: false` / `meets_0p02_target: false` in the
raw JSON and in `figures/data/F2_outbreak_probability.csv`, and they are exceptions to
the precision target by construction of the rule above, not by chance.

## Settings per certified reference

| reference | α | r | λ | c_b | T | h ladder | floor as run | floor after audit | K | slabs |
|---|---|---|---|---|---|---|---|---|---|---|
| P4 f_c^MF, λ = 1.60/1.75/1.90 | 0.5 | 1 | — | 0.3 | 120 (240 checked) | 0.008 → 0.001 | 10⁻³ | 10⁻⁵ | 3 | 1 (inert) |
| P6 case A, t† at A_f = 0.5603 | 2.0 | 0.99 | 3.0 | 0.5 | 95 | 0.01 → 0.0025 | 2×10⁻² | matched 10⁻² → 10⁻⁴ shift 1.4×10⁻⁴; production step 2×10⁻² → 10⁻² **not quantified**; **no bound claimed** | 3 | 436 |
| P6 case B, t* and Λ* at A = 0.325 | 1.0 | 0.95 | 2.5 | 0.4 | 40 | 0.01 → 6.25×10⁻⁴ | 10⁻² | 10⁻⁴ | 3 | 196 |
| class-2 fold (λ_fold, ν_f, A_fold) | 0.5 | 1 | — | 0.3 | 60 (30/120 checked) | superseded | 10⁻³ | exact quadrature | 3 | 1 (inert) |

The fold row is superseded: it is now computed from the exact C2.11–C2.14 stationary
law (`stage2b/fold_exact.py`), not from this solver, because at α = 0.5 the dose is
d = 0.5 and the method of steps closes after two intervals.
