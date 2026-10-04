# CROWD-1 Stage 3, item P8 — finite-N extinction, censored supplement

**Design** `crowd1_cs_design_and_manuscript_brief_v0_3_1.md` Part A, item P8.
**Authorised** 2026-10-01, with the owner's reporting rule: *"right-censored at
T_max = 2000; if fewer than half the runs extinguish, report 'median > T_max'; no
median from observed extinctions alone."*

Master seed **20261006**. P5 parameters (r = 1, α = 2, β = 0, c_b = 0.5, κ = ρ = 0,
ε = 1, I1) at **λ = 2, f = 0.5**, N ∈ {100, 200, 400, 800}, **100 replicates per N**,
400 runs in total.

**P8 registers no numerical prediction** — A4 says "extinction almost surely with a
median that grows steeply in N; no scaling law is registered" — so there is **no A6
verdict row**. What is registered is the reporting rule, and that is what is applied.

---

## Result

| N | extinct | censored | median extinction time | mean A over the run | A* − A |
|---|---|---|---|---|---|
| 100 | 0/100 | 100 | **median > T_max = 2000** | 0.476733 | 0.023267 |
| 200 | 0/100 | 100 | **median > T_max = 2000** | 0.493878 | 0.006122 |
| 400 | 0/100 | 100 | **median > T_max = 2000** | 0.497152 | 0.002848 |
| 800 | 0/100 | 100 | **median > T_max = 2000** | 0.498642 | 0.001358 |

**Zero extinctions in 400 runs.** Every run is right-censored at T_max = 2000, so the
Kaplan–Meier survival function is identically 1 over the whole observation window at
every N and has no event times at all. Under the owner's rule the median is reported
as "> T_max" at every N, and **no median is formed from observed extinctions** —
there are none to form one from.

## What this does and does not establish

- **Consistent with the registered prediction, and not a test of it.** "Extinction
  almost surely with a median that grows steeply in N" is a statement about a
  timescale that is already beyond T_max = 2000 at the *smallest* N tested. The
  observation is consistent with it and cannot discriminate it from any other steeply
  growing median. The censoring rule exists precisely so that this is reported as an
  absence of information rather than as a measurement.
- **No scaling law is registered and none is inferred.** With no event times, there
  is nothing to fit.
- **The persistent branch is confirmed, which is the informative part.** The mean
  activity over each run approaches A* = 0.5 from below as N grows: the depression is
  0.023267, 0.006122, 0.002848, 0.001358 at N = 100, 200, 400, 800. Successive ratios
  are 3.80, 2.15, 2.10 against the 2.00 expected for an O(1/N) finite-N correction,
  so the population sits on the P5 persistent branch at every N and the departure from
  it is the expected finite-N depression. (A* = 0.5 is exact here:
  1 − e^{−λLA*} = 1 − e^{−ln 2} = ½ identically.)

## Why T_max = 2000 is not nearly enough at these N, in one line

At λ = 2 the branch holds A ≈ 0.5, so roughly N/2 agents are active at any moment and
extinction needs every one of them to fall silent together. The mean extinction time
of such a branch grows exponentially in N, so a horizon of 2000 is already far short
at N = 100 — which is what the censored table reports. Extending the horizon or
dropping to much smaller N would be a different experiment and neither is registered.

## Files

```
config/p8_config.py  run_p8.py  verdicts_p8.py  REPORT_P8.md
outputs/reported_table.csv  outputs/p8_results.json  outputs/seeds.json
outputs/raw/p8_raw.json   outputs/logs/run_p8.log
```

Reproduce: `python run_p8.py && python verdicts_p8.py` (≈ 2 min, env `qcb-numba`).
