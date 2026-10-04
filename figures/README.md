# CROWD-1 — Figures 1–4

**Numbering.** F1 order advantage vs seed delay; F2 outbreak probability by campaign
order; **F3 P6 case-A trajectory; F4 onset (class 2 and class 1)**. The F3/F4
assignment is the submission numbering set by owner directive of 2026-10-02 and is
**swapped relative to the design's §A7 and to the original figure list**, which both
had F3 = onset and F4 = case A. Content unchanged; only the labels moved.

Specification: `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
Design: `crowd1_cs_design_and_manuscript_brief_v0_3_1.md`, Part A.
Ledger: `RESULTS_LEDGER.md` (247 rows) is the source of truth for every number
plotted here; no figure introduces a value that is not in it or in the raw JSON it
names below.

Every figure is written as both PDF (vector, for the manuscript) and PNG (300 dpi).
Every series plotted has a CSV or JSON beside it in `data/`, so each panel can be
redrawn without re-running any simulation.

## Figure index

| file | content | data files | source archive |
|---|---|---|---|
| `F1_order_advantage_vs_delay.{pdf,png}` | Between-order ratio of the time-dependent first-generation count E Z₁ vs seed delay τ₀ ∈ {0, 0.5, 1, 2, 5, 10}/ρ, with the exact curve; the frozen orientation-susceptibility proxy 1 + x₂(1 − e^{−ρτ₀}) on the same axes, labelled as a proxy | `F1_measured.csv`, `F1_exact_curves.csv` | `crowd1_stage2_archive` (P1-delay), `crowd1_stage2b_archive` (task 1) |
| `F2_outbreak_probability_by_order.{pdf,png}` | (a) P1 outbreak probability vs λ ∈ {1, 2, 3.5} for both registered orders and both held-out orders, Wilson intervals; (b) P2 at λ = 26.5 for the three orders with their registered R | `F2_outbreak_probability.csv` | `crowd1_stage2_archive` |
| `F3_P6caseA_activity_trajectory.{pdf,png}` | A(t) for P6 case A: agent mean with 95% band over 50 replicates, kinetic solution, A_f = 0.5603 and the adiabatic time t_ad,f = 66.309 marked; inset resolves the band at the crossing | `F3_P6A_agent.csv`, `F3_P6A_kinetic.csv`, `F3_marks.json`, `f3_p6A_agent.npz`, `f3_p6A_kinetic.npz`, `f3_meta.json` | `crowd1_stage2_archive` (P6 case A), `crowd1_stage2b_archive` (counter-resolved solver) |
| `F4_onset_class2_and_class1.{pdf,png}` | (a) class-2 backward onset at α = 0.5, c_b = 0.3: kinetic f_c^MF with agent f₅₀ overlaid at λ ∈ {1.60, 1.75, 1.90}, λ_fold and λ_c marked; (b) class-1 forward onset (P5): extinction at λ = 1, A* = ½ at λ = 2 | `F4a_class2_onset.csv`, `F4b_P5_traces.csv`, `F4_marks.csv` | `crowd1_stage2_archive` (P4), `crowd1_stage2b_archive` (task 2, fold), `crowd1_stage3_P5_archive` |

## Provenance of each series

**F1.** Measured points are the 24-background × 10 000-trial operator runs of Stage 2B
task 1 (N = 10⁵, **λ = 2, ρ = ε = 1**, L = ln 2, seed 20261002). Error bars are
**t₀.₉₇₅,₂₃ = 2.0687 × sem** over the 24 backgrounds — the Student-t multiplier for
24 groups, not the normal 1.96; the multiplier is written on the figure face and
carried in `F1_measured.csv` as `t_multiplier_df23`. The open squares are the
**Stage 2B frozen-background proxy rows**, labelled as such in the legend and
reported under their own name per ruling 1 — they are not a second estimate of the
paper's quantity. **This figure has no inset**, and none is listed among its sources. The clock ratio is load-bearing — the
time-dependent curve's zero-delay value is 1 + x₂[1 − (1−e^{−ρL})/(ρL)], which is
1.270250 at ρ = ε = 1 and 1.150218 at ρ = 0.5 — so it is stated on the figure face
and on the axis. There is no P2-delay inset in this figure and none is claimed here. The
two exact curves are closed forms, not fits:
E Z₁(τ₀) = (λ/2)[L + x(L − e^{−ρτ₀}(1 − e^{−ρL})/ρ)] for the time-dependent count and
1 + x₂(1 − e^{−ρτ₀}) for the frozen proxy. The proxy formula was verified identical
to the exact frozen-background ratio λL·q_T(τ₀) to 4.44×10⁻¹⁶ before plotting.
Per Stage 2B ruling 1 the time-dependent ratio is the paper's quantity; the frozen
curve is labelled a proxy on the figure itself.

**F2.** Wilson intervals as recorded in `stage2/outputs/stage2_results.json`. Replicate
counts differ by row (50 to 1157) because Stage 2 extended replicates only where the
A4a target was in reach; the counts are printed on panel b and carried in the CSV.
Intervals are **nominal fixed-sample Wilson 95%** intervals and the replicate counts
are adaptive (pilot of 50 extended from p̂, cap 1200, pilot pooled), so **coverage
under the realized design is unassessed** — stated in the figure's footnote per owner
ruling S2B-A7. Zero-outbreak rows are plotted at 0 with their Wilson interval
**[0, 0.071348]**: upper endpoint 0.071348, **half-width 0.035674**. The half-width is
the quantity the A4a targets bound, and it exceeds both 0.03 (P1) and 0.02 (P2);
those cells are flagged on the figure and in the CSV. The open star at λ = 2 is the N = 10⁶ diagnostic (18/50), not an
N = 10⁵ point, and carries its own Wilson interval [0.2414, 0.4986]. **Those N = 10⁶
cells at λ = 2 are outside the adaptive rule**: a fixed 50-run design, not piloted and
not extended, with no precision target and no `meets_*_target` flag — stated in the
figure's footnote. Had the adaptive rule been applied to the realised 18/50 it would
have asked for 984 replicates. The title says
what was observed; 0/50 does not establish impossibility.

**F3 (P6 case A).** Agent traces are a re-run of the Stage 2 P6 case-A replicates **with the same
50 seeds** (`gen_p6A_traces.py`), which reproduces the certified t† = 70.353 ± 0.085
exactly. The kinetic curve is the counter-resolved solver of Stage 2B task 3 at
h = 0.0025 (436 active slabs) — the **finest rung**, whose own crossing is
t† = 70.30333287794207. The certified kinetic **reference** is the Richardson
extrapolation of that three-rung ladder (h = 0.01 / 0.005 / 0.0025),
t† = 70.3277 ± 0.0244; the figure states both, because the plotted curve is a
solution on a grid and the reference is not. A_f = 0.5603 and t_ad,f = 66.309 are
Appendix E §C7 values (0.5603318, 66.30915), quoted not computed here. The agent
mean is **70.3530 with 95% CI [70.3288, 70.3773]**, half-width 0.024251, built with
`a6.t_interval` — Student-t on 49 df, the same construction every mean in the ledger
uses. The replicate standard deviation 0.0853 is reported beside it as a *spread*,
explicitly not the CI. The shaded band is the **pointwise 2.5th–97.5th percentile
across the 50 replicate trajectories**, also a spread and not a confidence interval
for the mean; the inset is labelled accordingly. The agent CI and the kinetic
reference 70.3277 ± 0.0244 overlap. It is narrower than the line width on
the full axes, so an inset resolves it at the crossing.

**F4 (onset).** Panel a: agent f₅₀ at **N = 5×10⁴** (the certified rung; the N = 2×10⁵ rung
serves the finite-N ladder) with bootstrap intervals from Stage 2 P4; kinetic f_c^MF
with its grid uncertainty from Stage 2B task 2. Per Stage 2B ruling 2 the kinetic
value is the reference and Appendix F's f_c values are withdrawn — they are kept in
`F4a_class2_onset.csv` (column `appendixF_withdrawn`) for the record but are **not**
plotted. λ_c = 1.957615 (design registers 1.958); **λ_fold = 1.482508331** from the exact
C2.11–C2.14 quadrature in `stage2b/fold_exact.py` (this supersedes the
measure-solver value 1.482546 — see BUGLOG S2B-4). Panel b: 50 replicate traces per
configuration at dt = 0.01 from Stage 3 P5 (seed 20261003, **α = 2, c_b = 0.5,
r = 1, N = 10⁵**), mean with the 2.5th–97.5th percentile band across replicates; the
shaded strip is the registered measurement window [20, 70]. The title is scoped to
the class-2 bistable window and this one class-1 example; no general classification
is asserted.

## Regeneration

    cd /Users/rb/Desktop/Crowd1
    python stage2b/fold_exact.py          # F4's lambda_fold marker (exact, seconds)
    python figures/gen_p6A_traces.py      # F3 agent + kinetic series (only step that simulates)
    python build_ledger.py                # ledger, if raw outputs changed

F1, F2 and F4 read only existing raw JSON from the stage archives; F3's series are
regenerated by the script above and are byte-stable given the recorded seeds.

## Not included

The A7 supplement (same-outcome fraction vs Δ for process, automaton and surrogate,
T4–T6) is **not** drawn: it is not on the delivered figure list. Its data are in
`crowd1_stage1_archive_v3` should it be wanted later.
