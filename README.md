# CROWD-1 — certified simulations of the promoted-crowd process

This repository holds the simulation code, raw outputs, certification record and
figures behind the CROWD-1 manuscript. Everything here is reproducible from the
committed archives: `python reproduce.py` rebuilds the results ledger and all four
figures without re-running a single simulation.

## What the paper is about

The promoted-crowd process is a finite-*N* interacting-particle model of opinion
dynamics in which each agent carries an **orientation** φ on the half-circle, a
real-valued **conviction** *c*, and a binary **stance**. Agents broadcast only while
their conviction exceeds an activity threshold *c_b*; a received message is accepted
with probability cos²(θ − φ) and otherwise rejected, and either way it moves the
recipient's orientation and deposits a conviction increment whose size decays
geometrically with the number of prior receipts in the same framing class. Conviction
decays exponentially between events.

Three features make the model worth certifying numerically rather than only
analysing. The **order of a campaign's messages** changes the outcome even when the
set of messages does not — a projective, non-commuting effect inherited from the
cosine response rule. **Onset is not always forward**: for small deposit sizes the
active branch appears through a saddle-node, so there is a finite critical campaign
reach *f_c* below which no campaign ignites the population. And **activity shuts off
deterministically**, which puts a hard deadline structure inside an otherwise
event-driven stochastic process.

The specification is `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION
v0.6". The experimental design — which quantities are registered, with what
tolerances, and what counts as a pass — is
`crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A. Appendices E and F
(C7–C9) are `crowd1_appendices_EF_C7_C9.md`. **Those three documents are
authoritative; nothing in this repository modifies a parameter, prediction,
tolerance or rule.**

## How the stages map to the manuscript

Section numbers follow the design's own section plan (Part B, §B3), which is the
authority; this table says which stage supplies the numbers for each.

| manuscript section | supplied by |
|---|---|
| 2. Model | **Stage 1** — A1 implementation and the A2 acceptance tests T1–T6 (124 rows, all PASS) |
| 3. Extinction (R2, finite-*N*) | **Stage 1** T1; **Stage 3 P8** (finite-*N* extinction; reported without a verdict — no number is registered) |
| 4. Invasion and order — F1, F2 | **Stage 2** P1, P1-delay, P2, P2-delay, P3; **Stage 2B task 1** (the estimand audit that replaced the P1-delay row) |
| 5. Onset and burn-out — F3, F4 | **Stage 2** P4, P6; **Stage 2B** tasks 2 and 3, the class-2 fold, and the floor audit; **Stage 3** P5 and P7 |
| 6. What the response rule predicts | **Stage 1** T4–T6 (process, automaton and surrogate contrasts) |
| Appendix: two-camp dynamics (R9) | **Stage 3 P9** (18 rows, all PASS) |
| Appendix: the Lux coefficient map (R10) | **Stage 3 P10** — *withdrawn, not run*; an algebraic derivation check only |

**Figure numbering — read this before cross-referencing.** This repository uses the
**submission numbering**, set by owner directive of 2026-10-02:

| | this repository (submission numbering) |
|---|---|
| **F1** | order advantage vs seed delay |
| **F2** | outbreak probability by campaign order |
| **F3** | P6 case-A activity trajectory |
| **F4** | onset, class 2 and class 1 |

**This supersedes two earlier numberings that agree with each other and disagree with
the above.** The design's §A7 lists *F3 = f_c(λ) in the class-2 backward regime* and
*F4 = A(t) for P6 case A*, and the figure list this work was originally given used
that same assignment. The figures were built under it and renamed afterwards, in both
the file names and the data-file names, when the submission numbering was directed.

So: **F3 and F4 are swapped relative to §A7 and to anything written before
2026-10-02.** The content of each figure is unchanged, and §B3 cites the pair
together in section 5, so no section cross-reference breaks — but any sentence that
names F3 or F4 individually and predates the directive refers to the other one. The
data files follow the current numbering (`F3_P6A_*`, `f3_*` for case A;
`F4a_*`, `F4b_*`, `F4_marks.csv` for onset).

## Layout

    README.md                    this file
    LICENSE                      MIT
    manuscript.md                the manuscript; its figure links resolve to figures/
    reproduce.py                 rebuilds the ledger and all four figures
    build_ledger.py              generates RESULTS_LEDGER.{md,csv} from the archives
    RESULTS_LEDGER.md / .csv     THE SINGLE SOURCE OF TRUTH for every certified number
    review_packet_v0_6_1.md                       specification (authoritative)
    crowd1_cs_design_and_manuscript_brief_v0_3_1.md   design, Part A (authoritative)
    crowd1_appendices_EF_C7_C9.md                 Appendices E and F (C7-C9)
    crowd1_cs_design_and_manuscript_brief_v0_3.md superseded design v0.3, retained
    cs_project_instructions_stage1.md             the original stage-1 brief
    stage1/     A1 simulator + A2 acceptance tests T1-T6
    stage2/     registered predictions P1, P1-delay, P2, P2-delay, P3, P4, P6
    stage2b/    discrepancy investigation, the kinetic solver, the fold, the floor audit
    stage3/     P5, P7, P8, P9, P10
    figures/    F1-F4 as PDF and PNG, their data files, and the generators

**A CROWD-2 appendix now exists.** `build_ledger.py` appends rows from
`crowd2/outputs/` under the Crowd-2 Stage 2 authorization of 2026-10-02, which
specifies that CROWD-1's engine and ledger are unchanged and CROWD-2 rows are
appended after them with a `C2-` prefix. Every byte of the CROWD-1 ledger is a
prefix of the combined file, and the CROWD-1 headline count stays at 262. The
appendix is guarded on `crowd2/` being present, and **`crowd2/` is excluded from
this repository by `.gitignore`** — so a clone of what is released here contains the
CROWD-1 record only, and `build_ledger.py` reproduces exactly the 262 CROWD-1 rows.
If you are working in the owner's full folder instead, expect 262 + 44 = 306 rows in
the CSV and a CROWD-2 section after the CROWD-1 one in the markdown.

Each stage directory carries its own `README.md`, `AMBIGUITIES.md` and (where
defects were found) `BUGLOG.md`, plus `outputs/` with the raw JSON, logs and
certified table. Earlier output directories (`outputs_v1`, `outputs_v2`) are the
**retained originals** of corrected runs and are deliberately kept: the project rule
is that corrections are versioned and originals retained.

## Reproducing

    python reproduce.py              # ledger + all four figures
    python reproduce.py --check      # also verify the ledger is byte-identical on a second run

Requires Python 3.11+, numpy, scipy and matplotlib. Re-running the *simulations*
needs numba as well and is not part of `reproduce.py`; each stage's `run_*.py` does
that, takes hours, and is pinned by the seeds recorded in its outputs.

- `build_ledger.py` reads only the certified tables and raw JSON already in the
  stage directories, so the ledger cannot drift from the record it summarises.
- `figures/make_figures.py` reads only `figures/data/`, so the figures are
  reproducible without any simulation.
- `figures/gen_p6A_traces.py` is the one script that simulates: it re-runs the 50
  P6 case-A replicates with their recorded seeds to produce F3's agent traces. Its
  output is committed, so you only need it if you want to re-derive that series.

## What is certified, and what is not

The ledger classifies every row. Three categories are *not* certifications and are
labelled as such wherever they appear:

- **Reported without a verdict** — a quantity with no registered prediction or
  tolerance, so no pass rule applies (P8; the class-2 fold; the floor audit).
- **Withdrawn** — P10, whose registered lag window is empty at the design's own
  parameter values. The Lux coefficient map stays in the manuscript as a derived
  closure, without numerical certification.
- **Superseded** — earlier values retained beside their corrections, with the
  correction's reason recorded in the relevant `BUGLOG.md`.

Two defects found in this project's own reference computations are recorded in
`stage2b/BUGLOG.md` rather than quietly fixed: **S2B-1** (a basin classifier that
aborted on a legitimately dying trajectory) and **S2B-4** (a conviction floor held
fixed across an *h*-ladder, which produced a confidently wrong fold location —
`stage2b/REPORT_class2_fold.md` and `stage2b/REPORT_floor_audit.md`).

## Known deviations from the design

- **§A7's F1 inset showing P2-delay is not drawn.** P2-delay was INCONCLUSIVE in
  Stage 2 and no inset was produced; F1 carries the P1-delay series only. Stated here
  rather than silently omitted.
- **§A7's supplement** (same-outcome fraction vs Δ for process, automaton and
  surrogate, T4–T6) is not drawn. Its data are in the Stage 1 archive.
- **Figure numbering** differs from §A7 as described above.

Open ambiguities that needed an owner ruling, and the rulings given, are collected in
the per-stage `AMBIGUITIES.md` files — in particular `stage2b/AMBIGUITIES.md`
items S2B-A6 (how an endpoint p-value is formed before Holm) and S2B-A7 (adaptive
replicate counts and interval coverage — note that the N = 10⁶ diagnostic cells at
λ = 2 sit outside the adaptive rule, on a fixed 50-run design with no precision
target).

## Citation and licence

Released under the MIT licence (see `LICENSE`). If you use this code or the certified
record, please cite the CROWD-1 manuscript; until it appears, cite this repository
and the specification version it certifies (`review_packet_v0_6_1.md`, PROCESS
SPECIFICATION v0.6).
