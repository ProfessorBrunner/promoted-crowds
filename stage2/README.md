# CROWD-1 Stage 2 — reproducibility archive

**Specification.** `review_packet_v0_6_1.md`, memo section **PROCESS SPECIFICATION
v0.6** (authoritative). Appendices C and D were used only for the predicted
quantities the design points to — C2(b), C2(d), C3(c)(i)–(iii) — never as
alternative specifications.

**Design.** `crowd1_cs_design_and_manuscript_brief_v0_3.md`, **Part A** (v0.3).

**Scope run.** Stage 2 = A4 items **P1, P1-delay, P2, P2-delay, P3, P4, P6**,
under the A6 pass rule with a Holm correction across the primary endpoints.
**Stage 3 is not authorized**: P5, P7, P8, P9 and P10 were not run, and no market
layer exists anywhere in this archive.

**Frozen for Stage 2** by the owner's authorisation: design v0.3 Part A as
written, the A4a endpoint definitions, and Stage 1 `AMBIGUITIES.md` items 1–9 as
adopted, with items 7 and 9 treated as clarifications of the process
specification (novelty weight r^(prior exposures in class); orientations as exact
integer degrees, I2 uniform on the 180 integer-degree rays).

**Archive version.** s2-v2; s2-v1 retained in full in `outputs_v1/`. One
correction, `BUGLOG.md` B3.

**Master seed.** `20261002`.

---

## 1. Result

| item | primary? | verdict | content |
|---|:--:|---|---|
| **P1** | yes | **PASS** (9 rows) | order through stance: x, R/λ, the two sealed held-out orders, no activation |
| **P1-delay** | yes | **INCONCLUSIVE** (3 rows) | ratio → 1.97 PASSES; the "every delay" clause is exactly on its boundary at τ₀ = 0 |
| **P2** | yes | **PASS** (8 rows) | orientation channel: q_T and R/λ for three orders, and from I2 |
| **P2-delay** | no | **INCONCLUSIVE** (2 rows) | ρ = 0.5 decay PASSES; ρ = 0 persistence is INCONCLUSIVE at δ = 2 % |
| **P3** | yes | **PASS** (7 rows) | outcome–deposit channel: frozen R_fr(0), E Z₂, convergence to R_∞ |
| **P4** | yes | **FAIL** (7 rows) | λ = 1.40 extinction and all three A\* PASS; f_c FAILS at λ = 1.75 and 1.90 |
| **P6** | yes | **PASS** (1 row) | case A certified; **case B BLOCKED** (needs C7) |

37 registered rows (P1 9, P1-delay 3, P2 8, P2-delay 2, P3 7, P4 7, P6 1):
32 PASS, 3 INCONCLUSIVE, 2 FAIL — both FAILs the same quantity, P4's f_c — and
one item (P6 case B) blocked with no row.

**Holm correction across the six A6 primary endpoints** (family level 0.05;
each endpoint's p-value is the smallest, over its registered rows, of the p-value
for the composite null |d| ≤ δ):

| endpoint | raw p | Holm-adjusted p | rejects |d| ≤ δ |
|---|--:|--:|:--:|
| P1 | 1 | 1 | no |
| P1-delay | 1 | 1 | no |
| P2 | 1 | 1 | no |
| P3 | 1 | 1 | no |
| **P4** | 3.6×10⁻²⁶ | **2.2×10⁻²⁵** | **yes** |
| P6 | 1 | 1 | no |

P4's rejection survives the correction with a wide margin — the Holm-adjusted
p is 2.17 × 10⁻²⁵ against α = 0.05, a factor of 2.3 × 10²³ (23 orders of
magnitude; the raw p of 3.62 × 10⁻²⁶ is 24 orders, and an earlier version of this
sentence quoted that figure while naming the corrected one); no
other endpoint comes close to rejection.

### What each item measured

**P1 — order through stance.** The campaign activates nobody (0 activations over
all runs; max |c| post-campaign 0.369 against c_b = 0.5). The two registered
orders leave x = 0.000597 and 0.970109 against 0 and 0.969846310, and operator
R/λ = 0.347327 and 0.682419 against 0.346573590 and 0.682696708. **The two
held-out orders were sealed before the run** — the same enumeration that
reproduces C3.15 to 2×10⁻¹⁰ predicts x = 0 for (50°,40°,140°) and x = 0.969846310
for (140°,40°,50°), written to `outputs/sealed_predictions.json` before any
simulation — and both are confirmed: x = −0.001032 and 0.969685, R/λ = 0.347335
and 0.680675.

**P1-delay (the paper's main figure).** The frozen invasion-radius ratio against
seed delay, at λ = 2:

| τ₀/ρ | R first | R second | ratio (95 %) | exact | unrelaxed fraction | e^(−ρτ₀) |
|--:|--:|--:|--:|--:|--:|--:|
| 0 | 0.6944 | 0.6947 | 1.0006 [0.9922, 1.0090] | 1.000000 | 1.000000 | 1.000000 |
| 0.5 | 0.6942 | 0.9604 | 1.3836 [1.3748, 1.3924] | 1.381605 | 0.606686 | 0.606531 |
| 1 | 0.6922 | 1.1196 | 1.6177 [1.6075, 1.6279] | 1.613060 | 0.367975 | 0.367879 |
| 2 | 0.6952 | 1.2760 | 1.8359 [1.8234, 1.8484] | 1.838592 | 0.135510 | 0.135335 |
| 5 | 0.6940 | 1.3628 | 1.9639 [1.9535, 1.9743] | 1.963312 | 0.006703 | 0.006738 |
| 10 | 0.6947 | 1.3648 | 1.9651 [1.9525, 1.9777] | 1.969802 | 0.000046 | 0.000045 |

The ratio converges to the registered 1.97 (PASS at δ = 2 %), and the
orientation-preparation contribution decays as e^(−ρτ₀) to within 0.0017
absolute. **At τ₀ = 0 the exact ratio is 1** — see `BUGLOG.md` A1.

**P2 — orientation channel.** q_T = 0.705763, 0.759274, 0.638396 against the
registered 0.707442366, 0.759089355, 0.637858566; R/λ = 0.036206, 0.039010,
0.032654 against 0.036287050, 0.038936194, 0.032717867. From I2 all orders give
R/λ = 0.025635 against 0.025646647 — the maximally mixed orientation is invariant
under every projection, so the order dependence vanishes, as R8(b) says.
Population check at λ = 26.5, reported with the ±0.02 precision target A4 asks
for: outbreak probability 0/50, 75/1157 = 0.065, 0/50 for the three orders —
near-critical, and ordered as the registered R = 0.962, 1.032, 0.867.

**P3 — outcome–deposit channel.** Frozen diagnostic R_fr(0) = 1.260159 and
0.878210 against 0.316695967λ = 1.266784 and 0.218867184λ = 0.875469 at λ = 4,
labelled a frozen diagnostic as A4a requires. E Z₂ from a seed introduced
immediately, measured in the time-dependent kernel with the background **not**
frozen: 1.561430 and 1.110392 against 0.0976502474λ² = 1.562404 and 1.103959.
Both orders converge to R_∞ = 0.0912λ = 0.364643 by τ₀ = 10 (0.363536, 0.362526).

**P4 — class-2 backward onset.** No reach ignites at λ = 1.40: zero runs with
A(160) > 0 over 500 runs at f ∈ {0.10, 0.25, 0.50, 0.75, 1.00}, which is A4a's
criterion exactly. The upper branch A\* = 0.6364, 0.7472, 0.8132 against the
registered 0.63, 0.75, 0.81 — all PASS. **f_c FAILS**: see `BUGLOG.md` D1.

**P6 — burn-out.** Case A: the first downward crossing of A_f = 0.5603 is
t† = 70.353 ± 0.085 against the registered 70.3 ± 0.1 (PASS, δ = 5 %). The
adiabatic value 66.3 is 5.69 % below the kinetic one, against the 6 % the design
claims. Case B is **BLOCKED**; the measured Λ = λ∫A dt is tabulated at eleven
activity levels so the comparison can be made once C7 arrives, and the total is
25.973 ± 0.025.

---

## 2. What the simulator is

The Stage 1 engine (`stage1/README.md` §2) extended with the capabilities Stage 2
needs. **Every extension is an optional parameter whose default reproduces Stage 1
behaviour**, and that claim is checked rather than asserted:
`python regression_stage1.py` re-runs the whole Stage 1 suite against this engine
and diffs the certified table against the frozen Stage 1 archive. Result in
`outputs/regression_stage1.txt`: **124 of 124 rows, 0 mismatches** — same verdict
and the same predicted / measured / diff / interval / δ / MC error / numerical
error on every row.

The extensions:

- **State save and resume** (`runner._snapshot`, `_run_from_state`): a campaign is
  run once and the state saved at each seed delay, so "the saved post-campaign
  state" that A4 refers to is a literal object. Resuming resets the time origin,
  which is exact because the clocks are memoryless and the decay is multiplicative.
- **Invasion seed** (`runner.inject_seed`), exactly A1: one agent at φ = T_+,
  c = 1, s = +, fresh counters, at the declared time.
- **Generation tracking** (`gen`, `n_offspring`): the seed is generation 0 and an
  agent activated by a broadcaster of generation g becomes g + 1, so Z₁ and Z₂ are
  measured rather than inferred, and A3's separation of R from a growth rate is
  structural.
- **Frozen-background operator checks** (`crowd1/operator.py`): A3's operator check
  is a separate code path in which the recipient responds in the state it was saved
  in, while each activated agent's own conviction still decays and so still sets
  its own lifetime — the construction C3.19 uses. Each trial restores the agents it
  touched from a pristine copy, so thousands of independent single-seed trials run
  against one background. The same function with `freeze=False` decays the
  background analytically to the absolute message time, which is exact for a
  background that has received nothing, and that is how C3.21's E Z₂ "without
  freezing the background" is measured.
- **Compact initial-class identifiers**: I2 places agents on arbitrary
  integer-degree rays. Rather than allocate 90 counter columns at N = 10⁶, one
  identifier is reserved for "initial orientation of a silent agent". That is sound
  because specification v0.6 gives such an agent c = 0, so it cannot broadcast
  before it receives a message and the message overwrites both its orientation and
  its identifier — Appendix C's own argument (C2.0: *"a message overwrites
  orientation before creating activity"*). The engine raises an error flag if a
  broadcast ever carries that identifier; it never did.

---

## 3. Seeds and reproduction

Master seed `20261002` (Stage 1 used `20261001`; the two are disjoint). Every
per-run seed is `derive_run_seed(MASTER_SEED, item, …)` and each run derives six
independent xoshiro256++ streams by role — clocks, recipient draws, acceptance
coins, cohort, initial law, exogenous — so that changing one role's replicate
count never shifts another's numbers. All logged in `outputs/seeds.json` and on
every row of every raw CSV.

```bash
cd stage2
python run_stage2.py                 # ~55 min wall, 16 worker processes
python run_stage2.py --only=P3,P6    # one or more items
python regression_stage1.py          # Stage 1 regression against this engine
```

Environment: Python 3.12.14, numpy 2.5.3, scipy 1.18.1, numba 0.67.0 (conda env
`qcb-numba`); macOS, Apple Silicon.

### Archive layout

```
stage2/
  README.md                    this file
  AMBIGUITIES.md               the five new ambiguities, with the two readings each
  BUGLOG.md                    B3 (harness), A1 (prediction scope), D1 (P4 f_c)
  run_stage2.py                driver: items, Holm, certified table, outputs
  stage2_items.py              the per-item runners that build the verdict rows
  regression_stage1.py         Stage 1 suite re-run against the Stage 2 engine
  config/stage2_config.py      every FIXED and DECLARED value, and the master seed
  crowd1/engine.py             the event-driven kernel (Stage 1 + the extensions)
  crowd1/operator.py           frozen / time-dependent operator checks
  crowd1/predictions_s2.py     the reference calculations
  crowd1/tests_s2.py           the per-run workers
  outputs/
    certified_table.md|.csv    the certified table
    stage2_results.json        predictions, measurements, intervals, budgets, Holm
    sealed_predictions.json    written BEFORE any run; holds the P1 held-out seal
    seeds.json                 master seed, derivation, every per-run seed
    regression_stage1.txt      the Stage 1 regression result
    raw/*.csv                  per-run sufficient statistics
    logs/run_log.txt
  outputs_v1/                  retained s2-v1 results (see BUGLOG.md B3)
```

---

## 4. A6 accounting

**δ assignment.** Operator checks 2 % of the predicted value; trajectory markers
5 %; outbreak probabilities ±0.03 absolute; x = 0 at 0.01 absolute (A4a). Which
rows are which is on every row of the certified table in the `delta_basis` column.
Outbreak probabilities carry **no verdict** wherever A4 predicts no number for
them — A4a: *"±0.03 is a precision target for the estimate, not an agreement
tolerance"* — and the invasion claim is certified on the operator rows instead,
keeping A3's separation of R, growth rate and outbreak probability intact.

**The four error sources, separated on every row.**

1. *Monte Carlo* — the half-width of the reported interval: Student-t across
   background realisations for the operator rows, Wilson for pooled proportions,
   and a 4000-draw bootstrap for the two threshold-style rows (P4's f_c and the
   P2-delay spreads), where the estimator is a curve crossing rather than a mean.
2. *Finite-N bias* — from an N ladder: N ∈ {10⁴, 10⁵} for the P1, P2 and P3
   operator checks, N ∈ {10⁵, 10⁶} for P1's population check, and N ∈ {5·10⁴,
   2·10⁵} for P4's f_c. Reported in the `finite_N_bias` column, never absorbed
   into the verdict.
3. *Numerical error of the reference calculation* — zero for the closed forms of
   C3(c); the quadrature error for P3's E Z₂ (≈10⁻¹⁵); the registered ± for P4's
   f_c and P6's t†.
4. *Closure error* — P6 case A's adiabatic-versus-kinetic gap, 4.0 time units or
   5.69 %, reported as the approximation being assessed rather than as a
   correction. Zero elsewhere: P1, P2 and P3's operator quantities are exact
   consequences of the specification, not closures.

**Holm.** A6 specifies the correction across the primary endpoints; the reading
used, and the alternative, are in `AMBIGUITIES.md` S2-4. No verdict changes under
either reading.

---

## 5. Deviations and corrections

One harness defect, corrected and versioned (`BUGLOG.md` B3: six rows were emitted
without the confidence interval A6 requires, which made INCONCLUSIVE unreachable
and cost P4 its N ladder; s2-v1 is retained unchanged). One error of scope in a
registered prediction, reported and **not** corrected (`BUGLOG.md` A1). One
discrepancy whose category cannot be assigned from the files in this project
(`BUGLOG.md` D1). No simulator bug was found, and no parameter, prediction,
tolerance or rule of design v0.3 or specification v0.6 was modified anywhere.

---

## 6. Stop point

Stage 2 is complete. Per the authorisation, **nothing further is run**: Stage 3
(P5, P7, P8, P9, P10) is not authorized. Two items need owner input before they
can be closed — P6 case B needs Appendix C7, and P4's f_c discrepancy needs either
C9(b) or an authorised independent mean-field solve.
