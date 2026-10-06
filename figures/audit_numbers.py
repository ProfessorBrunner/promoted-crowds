#!/usr/bin/env python3
"""Audit every number drawn or printed on F1-F4.

Plotted values are READ from the files make_figures.py reads; nothing is typed
from memory.  The manuscript column quotes promoted_crowds.tex by line number.
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")

rows = []


def add(fig, element, plotted, source, kind, tex):
    rows.append(dict(figure=fig, element=element, plotted=plotted,
                     source=source, kind=kind, manuscript=tex))


def rd(name):
    with open(os.path.join(DATA, name), newline="") as fh:
        return list(csv.DictReader(fh))


def rng(vals):
    return f"{vals[0]!r} … {vals[-1]!r}  (n={len(vals)})"


# ---------------------------------------------------------------- F1
f1m, f1c = rd("F1_measured.csv"), rd("F1_exact_curves.csv")
tm = float(f1m[0]["t_multiplier_df23"])
x2line = float(f1m[-1]["frozen_formula_1_plus_x2_1_minus_exp"])
g = lambda k, rs=f1m: [float(r[k]) for r in rs]            # noqa: E731

add("F1", "exact time-dependent ratio curve", rng(g("ratio_time_dependent_exact", f1c)),
    "F1_exact_curves.csv:ratio_time_dependent_exact", "computed",
    "L462 table, tau0=10 row: 1.9698145")
add("F1", "exact frozen-proxy curve", rng(g("ratio_frozen_proxy_exact", f1c)),
    "F1_exact_curves.csv:ratio_frozen_proxy_exact", "computed",
    "L477 'increases with 1-e^{-rho tau0} and approaches 1.969846'")
add("F1", "time-dependent markers (6)", rng(g("ratio_timedep_measured")),
    "F1_measured.csv:ratio_timedep_measured", "computed",
    "L462 tau0=10 row: 1.96282 +- 0.00624")
add("F1", "frozen-proxy markers (6)", rng(g("ratio_frozen_measured")),
    "F1_measured.csv:ratio_frozen_measured", "computed", "not tabulated in tex")
add("F1", "error bars = t x sem (time-dep)", rng([tm * s for s in g("ratio_timedep_sem")]),
    "F1_measured.csv:ratio_timedep_sem x t_multiplier_df23", "computed",
    "L504 caption 'error bars are t_{0.975,23}=2.069 times the standard error'")
add("F1", "error bars = t x sem (frozen)", rng([tm * s for s in g("ratio_frozen_sem")]),
    "F1_measured.csv:ratio_frozen_sem x t_multiplier_df23", "computed", "L504 as above")
add("F1", "'$t_{0.975,23}=2.069$' in parameter block", repr(tm),
    "F1_measured.csv:t_multiplier_df23", "computed", "L504 caption: 2.069")
add("F1", "dotted reference line labelled '$1+x_2=1.9698$'",
    repr(float(f1m[0]["stationary_ratio_1_plus_x2"])),
    "F1_measured.csv:stationary_ratio_1_plus_x2 <- "
    "stage2/outputs_v1/sealed_predictions.json P1_registered_reproduction "
    "(40,140,50).x (= ratio of the two R_over_lambda to 2.2e-16)", "computed",
    "L504 caption 'stationary ratio 1+x_2=1.9698'; L468/L477 stationary 1.969846")
add("F1", "dotted reference line at unity", "1.0", "literal in make_figures.py",
    "transcribed", "L477 'the proxy is exactly 1' at tau0=0")
add("F1", "annotation 'proxy ratio exactly 1'", "1 (exact, at tau0=0)",
    "F1_exact_curves.csv:ratio_frozen_proxy_exact[0]=" +
    repr(float(f1c[0]["ratio_frozen_proxy_exact"])), "computed",
    "L477 'the proxy is exactly 1'")
add("F1", "parameter block 'rho=eps=1, lambda=2, N=10^5, L=ln 2'",
    "rho=1, eps=1, lambda=2, N=100000, L=ln2", "design parameters (Sec. IV-C-1)",
    "transcribed", "L504 'at lambda=2 and N=10^5'")
add("F1", "parameter block '24 backgrounds x 10^4 seed trials'", "24, 10000",
    "design: stage2 P1-delay replicate structure", "transcribed",
    "L504 '24 backgrounds of 10^4 seed trials each'")

# ---------------------------------------------------------------- F2
f2 = rd("F2_outbreak_probability.csv")
p1 = [r for r in f2 if r["prediction"] == "P1"]
big = [r for r in f2 if r["prediction"] == "P1 (N=1e6)"]
p2 = [r for r in f2 if r["prediction"] == "P2"]
z = [r for r in p1 if int(r["outbreaks"]) == 0][0]
star = [r for r in big if r["order"] == "(40, 140, 50)"][0]

for r in p1:
    add("F2", f"(a) point {r['order']} at lambda={r['lam']}", repr(float(r["p_outbreak"])),
        f"F2_outbreak_probability.csv p_outbreak ({r['outbreaks']}/{r['replicates']})",
        "computed", "L1477 extended cells 440/958, 504/1052, 275/315; 0/50 cells listed")
    add("F2", f"(a) Wilson interval {r['order']} at lambda={r['lam']}",
        f"[{float(r['ci_lo'])!r}, {float(r['ci_hi'])!r}]",
        "F2_outbreak_probability.csv ci_lo/ci_hi", "computed",
        "L517 'A 0/50 observation has interval [0,0.0713]'")
add("F2", "(a) star marker, N=10^6, lambda=2", repr(float(star["p_outbreak"])) +
    f" (= {star['outbreaks']}/{star['replicates']})",
    "F2_outbreak_probability.csv prediction='P1 (N=1e6)'", "computed",
    "L517 'the star marks 18/50 at N=10^6, lambda=2'")
add("F2", "(a) star Wilson interval",
    f"[{float(star['ci_lo'])!r}, {float(star['ci_hi'])!r}]",
    "F2_outbreak_probability.csv ci_lo/ci_hi", "computed", "not quoted in tex")
add("F2", "(a) annotation '0/50 at both orders at lambda=1'", "0/50, 0/50",
    "F2_outbreak_probability.csv outbreaks/replicates at lam=1.0", "computed",
    "L1477 'Such cells occur at lambda=1 for both stance orders'")
add("F2", "(a) Wilson note '[0, 0.0713]'", repr(float(z["ci_hi"])),
    "F2_outbreak_probability.csv:ci_hi (0/50 cell)", "computed",
    "L517 and L1477: [0,0.0713]")
add("F2", "(a) Wilson note 'half-width 0.0357'", repr(float(z["half_width"])),
    "F2_outbreak_probability.csv:half_width", "computed", "L1477 half-width 0.0357")
add("F2", "(a) Wilson note 'precision targets 0.03 and 0.02'", "0.03, 0.02",
    "design A4a; literals in make_figures.py", "transcribed",
    "L1475 'stance experiments use target 0.03 ... orientation experiments use target 0.02'")
add("F2", "(a) lambda values plotted", "1.0, 2.0, 3.5",
    "F2_outbreak_probability.csv:lam", "computed",
    "L517 'lambda in {1,2,3.5}'")
add("F2", "(a) panel label 'N=10^5 unless marked'", "100000",
    "F2_outbreak_probability.csv:N", "computed", "L517 '(a) ... at N=10^5'")
for r in p2:
    add("F2", f"(b) point {r['order']}", repr(float(r["p_outbreak"])),
        f"F2_outbreak_probability.csv p_outbreak ({r['outbreaks']}/{r['replicates']})",
        "computed", "L512/L517 '0/50, 75/1157=0.065, and 0/50'")
    Rv = float(r["lam"]) * float(r["q_T"]) * math.log(1.0 / 0.95)
    add("F2", f"(b) printed 'R={Rv:.3f}'", repr(Rv),
        "lam x F2_outbreak_probability.csv:q_T x ln(1/0.95); q_T <- "
        "stage2/outputs_v1/stage2_results.json sealed.P2_reproduction[order].q_T",
        "computed (replaced transcribed R_registered in this pass)",
        "L512/L517 'R=0.962, 1.032, and 0.867'")
    add("F2", f"(b) printed count {r['order']}",
        f"{r['outbreaks']}/{r['replicates']}",
        "F2_outbreak_probability.csv:outbreaks/replicates", "computed",
        "L512 '0/50, 75/1157=0.065, and 0/50'")
    add("F2", f"(b) Wilson interval {r['order']}",
        f"[{float(r['ci_lo'])!r}, {float(r['ci_hi'])!r}]",
        "F2_outbreak_probability.csv ci_lo/ci_hi", "computed",
        "L517 'nominal 95% Wilson intervals'")
add("F2", "(b) panel label 'lambda=26.5, N=10^5'",
    f"{float(p2[0]['lam'])!r}, {int(p2[0]['N'])}",
    "F2_outbreak_probability.csv lam/N", "computed",
    "L517 '(b) Orientation-memory campaigns at lambda=26.5 ... panel (b) has N=10^5'")
add("F2", "footnote 'pilot of 50 ... cap 1200'", "50, 1200",
    "design A4a adaptive rule; literals in make_figures.py", "transcribed",
    "L1475 'begin with 50 pilot replicates ... min[max(need,50),1200]'")
add("F2", "footnote 'fixed 50-run design' for the N=10^6 cells",
    f"{star['replicates']}", "F2_outbreak_probability.csv:replicates", "computed",
    "L517 'the star marks 18/50 at N=10^6'")

# ---------------------------------------------------------------- F3
m = json.load(open(os.path.join(DATA, "F3_marks.json")))
ag, kn = rd("F3_P6A_agent.csv"), rd("F3_P6A_kinetic.csv")
add("F3", "agent mean curve", rng([float(r["mean_A"]) for r in ag]),
    "F3_P6A_agent.csv:mean_A", "computed", "L623 'agent mean is shown'")
add("F3", "agent band (2.5th/97.5th pct)",
    f"lo {rng([float(r['pct2p5_A']) for r in ag])}",
    "F3_P6A_agent.csv:pct2p5_A/pct97p5_A", "computed",
    "L623 'pointwise 2.5th-97.5th percentiles across replicate trajectories'")
add("F3", "kinetic curve", rng([float(r["A_kinetic"]) for r in kn]),
    "F3_P6A_kinetic.csv:A_kinetic", "computed",
    "L623 'kinetic curve is evaluated at the finest step h=0.0025'")
add("F3", "reference line / label '$A_f=0.5603$'", repr(m["crossing_level"]),
    "F3_marks.json:crossing_level <- stage2/config/stage2_config.py:163", "transcribed "
    "(declared crossing marker; no computed counterpart in archives)",
    "L623 'fold activity A_f=0.5603'; L1447 'The marker is A_f=0.5603'; "
    "L612 Prop. 4 fold activity A_f=0.5603318, which CS reproduces as "
    "0.5603318621202521 +-4.5e-09 (caseA_fold_v2.json) and the D.3 measure "
    "solver as 0.5603420775436564 +-4.22e-05 "
    "(caseA_fold_measure_solver.json) -- AGREES; the figure marks the declared "
    "level, a distinct quantity")
add("F3", "vertical line / label 'adiabatic $t_{ad,f}=66.309$'", repr(m["adiabatic"]),
    "F3_marks.json:adiabatic <- stage2b/outputs/raw/caseA_fold_v2.json "
    "construction 'mixture_n1' (C.7.2 dose mixture, n = 1+Poisson(H)); "
    "t_ad,f = int_0^{H_f} du/(lambda A_+(u))", "computed "
    "(+-7.2e-09 on the ladder; confirmed by the D.3 measure solver at "
    "66.30902252788111 +-7.29e-04 in caseA_fold_measure_solver.json; reproduces "
    "the manuscript to 3.3e-08. Was a transcribed constant until BUGLOG S2B-CS1 "
    "was fixed)",
    "L623 't_{ad,f}=66.309'; L612/L618/L1532 '66.30915' -- AGREES")
add("F3", "marked crossing point (t, A)",
    f"({m['agent_t_dagger_mean']!r}, {m['crossing_level']!r})",
    "F3_marks.json:agent_t_dagger_mean, crossing_level", "computed",
    "L623 'mean replicate crossing time is 70.3530'")
add("F3", "annotation 'agent mean 70.3530'", repr(m["agent_t_dagger_mean"]),
    "F3_marks.json:agent_t_dagger_mean", "computed", "L623/L1528: 70.3530")
add("F3", "annotation '95% CI [70.3288, 70.3773]'",
    f"[{m['agent_t_dagger_mean_CI_lo']!r}, {m['agent_t_dagger_mean_CI_hi']!r}]",
    "F3_marks.json:agent_t_dagger_mean_CI_lo/hi", "computed",
    "L623/L1528: [70.3288,70.3773]")
add("F3", "annotation 'half-width 0.0243'",
    repr(m["agent_t_dagger_mean_95_halfwidth"]),
    "F3_marks.json:agent_t_dagger_mean_95_halfwidth", "computed",
    "L618/L1530 'Monte Carlo 95% half-width 0.024'")
add("F3", "annotation 'kinetic reference 70.3277 +- 0.0244'",
    f"{m['kinetic_t_dagger_reference']!r} +- {m['kinetic_t_dagger_reference_unc']!r}",
    "F3_marks.json:kinetic_t_dagger_reference(_unc) <- "
    "stage2b/outputs/raw/p6_reference.json case_A_kinetic.t_dagger.richardson/uncertainty",
    "computed", "L623 '70.3277+-0.0244'; L1447 'Extrapolation gives 70.327688, "
    "with error estimate 0.024355'")
add("F3", "annotation 'Richardson, h=0.0100052/0.0050026/0.0024997'",
    repr(m["kinetic_h_ladder"]),
    "F3_marks.json:kinetic_h_ladder <- "
    "stage2b/outputs/raw/p6_reference.json case_A_kinetic.rows[*].h", "computed "
    "(replaced transcribed 0.01/0.005/0.0025 in this pass)",
    "L1447 'At h=(0.0100052,0.0050026,0.0024997)'")
add("F3", "annotation 'p=1.059'", repr(m["kinetic_observed_order_in_h"]),
    "F3_marks.json:kinetic_observed_order_in_h <- p6_reference.json observed_order",
    "computed", "L1447 'with order 1.059'")
add("F3", "annotation 'kinetic finest grid 70.3033'",
    repr(m["kinetic_t_dagger_finest_grid"]),
    "F3_marks.json:kinetic_t_dagger_finest_grid <- p6_reference.json value_finest",
    "computed", "L1447 'The finest-step value is 70.3033'")
add("F3", "legend 'kinetic, finest grid h=0.0025'", repr(m["kinetic_h"]),
    "F3_marks.json:kinetic_h <- p6_reference.json rows[2].h", "computed",
    "L623 'finest step h=0.0025'; L1447 'the plotted curve uses h=0.0025'")
add("F3", "legend 'N=10^5, 50 replicates'", f"{m['N']!r}, {m['replicates']!r}",
    "F3_marks.json:N, replicates", "computed",
    "L623 'Case A activity A(t) at N=10^5 ... 50 replicate trajectories'")
add("F3", "annotation '49 df'", f"49 (= replicates-1 = {m['replicates'] - 1})",
    "literal in make_figures.py; equals F3_marks.json replicates-1", "transcribed "
    "(identical to computed value)", "L623/L1528 '49 degrees of freedom'")

# ---------------------------------------------------------------- F4
on = rd("F4a_class2_onset.csv")
mk = {r["quantity"]: r for r in rd("F4_marks.csv")}
tr = rd("F4b_P5_traces.csv")
for r in on:
    add("F4", f"(a) kinetic f_c^MF at lambda={r['lam']}",
        f"{float(r['f_c_MF'])!r} +- {float(r['f_c_MF_unc'])!r}",
        "F4a_class2_onset.csv:f_c_MF/f_c_MF_unc", "computed",
        "tab:threshold L708-710 kinetic threshold f_c")
    add("F4", f"(a) agent f_50 at lambda={r['lam']}",
        f"{float(r['f50_agent'])!r} [{float(r['f50_lo'])!r}, {float(r['f50_hi'])!r}]",
        "F4a_class2_onset.csv:f50_agent/f50_lo/f50_hi", "computed",
        "tab:threshold L708-710 finite-population 50% point and 95% interval")
add("F4", "(a) vertical line / label 'lambda_fold=1.482508'",
    repr(float(mk["lambda_fold"]["value"])),
    "F4_marks.csv:lambda_fold <- stage2b/fold_exact.py (stage2b/outputs/raw/fold_exact.json)",
    "computed", "L722/L1457/L1584: 1.482508")
add("F4", "(a) vertical line / label 'lambda_c=1.95762'",
    repr(float(mk["lambda_c"]["value"])),
    "F4_marks.csv:lambda_c <- stage2/outputs_v1/stage2_results.json lambda_c_computed",
    "computed (replaced transcribed 1.957615 in this pass)",
    "L722/L669/L1457: 1.9576 (= 1/ln(5/3))")
add("F4", "(a) shaded 'bistable window' span",
    f"[{float(mk['lambda_fold']['value'])!r}, {float(mk['lambda_c']['value'])!r}]",
    "F4_marks.csv:lambda_fold, lambda_c", "computed",
    "L722 'with lambda_fold=1.482508 and lambda_c=1.9576 marked'")
add("F4", "(a) panel label 'alpha=0.5, c_b=0.3, eps=1, r=1'", "0.5, 0.3, 1, 1",
    "design parameters (Theorem 3 example)", "transcribed",
    "L722 'alpha=0.5, c_b=0.3, r=1'")
add("F4", "(a) legend 'agent f_50 (N=5x10^4)'", "50000",
    "design parameter", "transcribed",
    "L722 'the finite-population points use N=5x10^4'")
for k in ("lam1.0_f0.01", "lam1.0_f0.1", "lam2.0_f0.01", "lam2.0_f0.1"):
    add("F4", f"(b) trace {k} mean and band",
        f"mean {rng([float(r[k + '_mean']) for r in tr])}",
        f"F4b_P5_traces.csv:{k}_mean/_lo/_hi", "computed",
        "L722 '(b) active fraction A(t) at lambda=1,2 for f=0.01,0.10'")
add("F4", "(b) reference line / label '$A^*=1/2$'", "0.5",
    "theory: class-1 stationary activity", "transcribed",
    "L722 'settles at A^*=1/2 at lambda=2'")
add("F4", "(b) shaded 'measurement window [20,70]'", "20, 70",
    "design measurement window", "transcribed", "L722 'measured over [20,70]'")
add("F4", "(b) band note 'across 50 replicates'", "50",
    "design replicate count", "transcribed",
    "L722 'Panel (b) uses N=10^5 and 50 replicate trajectories'")
add("F4", "(b) panel label 'alpha=2, c_b=0.5, r=1, N=10^5'", "2, 0.5, 1, 100000",
    "design parameters (Sec. V-E)", "transcribed",
    "L722 '(b) Class-1 example at alpha=2' and 'Panel (b) uses N=10^5'")
add("F4", "(b) legend 'lambda=1/2, f=0.01/0.10'", "1, 2, 0.01, 0.10",
    "design parameters; F4b_P5_traces.csv column names", "transcribed",
    "L722 'at lambda=1,2 for f=0.01,0.10'")

out = os.path.join(HERE, "F1-F4_number_audit.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["figure", "element", "plotted", "source",
                                       "kind", "manuscript"])
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} audited elements -> {os.path.basename(out)}")
