"""Stage 3 P7 — A6 verdict table under the owner's rulings of 2026-10-01."""
import csv, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config")); sys.path.insert(0, S2)
from crowd1.a6 import (make_verdict, Verdict, decide, replicates_to_resolve,
                       finite_N_bias_from_ladder, wilson_interval)
import p7_config as CFG
FX, DC = CFG.P7["fixed"], CFG.P7["declared"]
R = json.load(open(os.path.join(HERE, "outputs", "raw", "p7_raw.json")))
REF = json.load(open(os.path.join(HERE, "outputs", "raw", "p7_reference.json")))
cells = {(c["order"], c["f"]): c for c in R["cells"]}
per = R["per_replicate"]
TBL = {float(k): v for k, v in FX["reach_table"].items()}

# ---- A6 source 2 (finite-N) and source 3 (measurement grid), from the ladders
biasA = finite_N_bias_from_ladder([(c["N"], c["A_max_mean_trajectory"])
                                   for c in R["N_ladder"]])
biasI = finite_N_bias_from_ladder([(c["N"], c["I_mean"]) for c in R["N_ladder"]])
biasT = finite_N_bias_from_ladder([(c["N"], c["T_act_mean_trajectory"])
                                   for c in R["N_ladder"]])
gA = [c["A_max_mean_trajectory"] for c in R["grid_refinement"]]
gT = [c["T_act_mean_trajectory"] for c in R["grid_refinement"]]
gridA = abs(gA[-1] - gA[-2])
# T_act is grid-QUANTIZED, not grid-converged: A crosses A_max/2 at a jump
# discontinuity at t = L, so the measured T_act is ceil(L/dt)*dt for any dt and the
# h-ladder shows no movement at all.  The honest numerical error is therefore the
# quantization |ceil(L/dt)*dt - L|, not the (identically zero) ladder residual.
L_EXACT = math.log(1.0 / FX["c_b"]) / FX["eps"]
gridT = abs(math.ceil(L_EXACT / DC["fine_dt"]) * DC["fine_dt"] - L_EXACT)
# A6 source 3 on the PREDICTION side: the width of the C9(a) enclosure
encl = {float(r["f"]): r["width"] for r in REF["reach_table"]}
bs = lambda d: float(d.get("residual_bias_at_Nmax", d["top_gap"]))

def boot_row(name, pred, meas, lo, hi, delta, basis, nrep, N, num, bias, note):
    dlo, dhi = lo - pred, hi - pred
    st = decide(dlo, dhi, delta); hw = 0.5 * (hi - lo)
    return Verdict(name=name, predicted=float(pred), measured=float(meas),
                   diff=float(meas - pred), ci_lo=float(dlo), ci_hi=float(dhi),
                   delta=float(delta), delta_basis=basis, status=st,
                   n_replicates=nrep, N=int(N),
                   replicates_needed=(replicates_to_resolve(meas - pred, hw, delta,
                                                            nrep)
                                      if st == "INCONCLUSIVE" else None),
                   mc_error=float(hw), finite_N_bias=float(bias),
                   numerical_error=float(num), closure_error=None,
                   interval_kind="bootstrap percentile over replicate traces, B=2000",
                   note=note)

V = []
for order, lbl in (("single", "single T pulse"),
                   ("T_Tperp", "coincident (T, T_perp)")):
    for f in FX["reaches"]:
        c = cells[(order, f)]; am, ii, ta = TBL[f]
        n = c["replicates"]
        extra = ("" if order == "single" else
                 "; design A4: (T, T_perp) reproduces the single-pulse values "
                 "(specification: T accepted -> c = 1, then T_perp is in the SAME "
                 "framing class, rejected, depositing +0.4r, clipped back to 1)")
        V.append(boot_row(
            f"P7 A_max, {lbl}, f={f} (mean trajectory)", am,
            c["A_max_mean_trajectory"], *c["A_max_mt_boot"],
            CFG.DELTA_POINT_FRAC * am, f"2% of the registered {am}", n, c["N"],
            max(gridA, encl[f]["A_max"]), bs(biasA),
            f"registered endpoint is the mean-trajectory value (ruling 2); "
            f"C9(a) enclosure width {encl[f]['A_max']:.2e}{extra}"))
        V.append(boot_row(
            f"P7 T_act, {lbl}, f={f} (mean trajectory)", ta,
            c["T_act_mean_trajectory"], *c["T_act_mt_boot"],
            CFG.DELTA_POINT_FRAC * ta, f"2% of the registered {ta}", n, c["N"],
            max(gridT, encl[f]["T_act"]), bs(biasT),
            f"registered endpoint is the mean-trajectory value (ruling 2); C9(a) "
            f"enclosure width {encl[f]['T_act']:.2e}; the bootstrap interval has "
            f"ZERO width because every cohort member shuts off in the 2e-6 window "
            f"[L, L+] in every replicate, so T_act has no replicate-to-replicate "
            f"variation -- the whole discrepancy is grid quantization "
            f"{gridT:.2e}{extra}"))
        V.append(make_verdict(
            name=f"P7 I, {lbl}, f={f}",
            predicted=ii,
            per_replicate_values=np.array(per[f"{order}_f{f}"]["I_exact"]),
            delta=CFG.DELTA_POINT_FRAC * ii,
            delta_basis=f"2% of the registered {ii}", N=c["N"],
            numerical_error=encl[f]["I"], finite_N_bias=bs(biasI),
            note=f"reported once (ruling 2: I is linear in A, so the "
                 f"mean-trajectory and per-replicate-average values coincide "
                 f"identically); int A dt is accumulated exactly by the engine, "
                 f"not from the sampling grid{extra}"))
# ---- (T_perp, T): zero predictions
for f in FX["reaches"]:
    c = cells[("Tperp_T", f)]
    for q, key in (("A_max", "A_max_mean_trajectory"),
                   ("T_act", "T_act_mean_trajectory")):
        V.append(make_verdict(
            name=f"P7 {q}, coincident (T_perp, T), f={f}",
            predicted=0.0,
            per_replicate_values=np.array(per[f"Tperp_T_f{f}"][
                "A_max" if q == "A_max" else "T_act"]),
            delta=CFG.DELTA_ZERO_ABS,
            delta_basis="A4a absolute tolerance 1e-3 for zero predictions",
            N=c["N"], numerical_error=0.0, finite_N_bias=0.0,
            note="specification: T_perp rejected first (deposit +beta = +0.4), then "
                 "T accepted in the same framing class (deposit +alpha r = +1e-6), "
                 "so c = 0.400001 < c_b = 0.5 and no cohort member ever activates"))
    V.append(make_verdict(
        name=f"P7 I, coincident (T_perp, T), f={f}", predicted=0.0,
        per_replicate_values=np.array(per[f"Tperp_T_f{f}"]["I_exact"]),
        delta=CFG.DELTA_ZERO_ABS,
        delta_basis="A4a absolute tolerance 1e-3 for zero predictions",
        N=c["N"], numerical_error=0.0, finite_N_bias=0.0,
        note="exact int A dt from the engine"))

out = dict(
    verdicts=[v.__dict__ for v in V],
    finite_N_bias=dict(A_max=biasA, I=biasI, T_act=biasT),
    grid_refinement=dict(A_max=list(zip([c["fine_dt"] for c in R["grid_refinement"]],
                                        gA)),
                         T_act=list(zip([c["fine_dt"] for c in R["grid_refinement"]],
                                        gT)),
                         residual_A_max=gridA, residual_T_act=gridT),
    # reported beside the registered rows, without verdicts (ruling 2)
    finite_N_diagnostics=[dict(
        order=c["order"], f=c["f"],
        A_max_mean_trajectory=c["A_max_mean_trajectory"],
        A_max_per_replicate_mean=c["A_max_per_replicate_mean"],
        A_max_per_replicate_sd=c["A_max_per_replicate_sd"],
        A_max_gap=c["A_max_per_replicate_mean"] - c["A_max_mean_trajectory"],
        T_act_mean_trajectory=c["T_act_mean_trajectory"],
        T_act_per_replicate_mean=c["T_act_per_replicate_mean"],
        T_act_per_replicate_sd=c["T_act_per_replicate_sd"],
        t_argmax_mean_trajectory=c["t_argmax_mean_trajectory"],
        t_argmax_per_replicate_sd=c["t_argmax_per_replicate_sd"])
        for c in R["cells"]],
    # reported without a verdict: P7 registers no outbreak number
    outbreak_new_rule=[dict(
        order=c["order"], f=c["f"], k=c["outbreak_count_new_rule"],
        n=c["replicates"],
        p=wilson_interval(c["outbreak_count_new_rule"], c["replicates"])[0],
        ever_active_outside_cohort_mean=c["ever_active_outside_cohort_mean"])
        for c in R["cells"]],
    late_recross_check=dict(
        max_ratio_over_all_cells=max(c["max_late_recross_ratio"]
                                     for c in R["cells"]),
        threshold=0.5,
        meaning="max over every replicate of max(A after the first descent below "
                "A_max/2) / A_max; must stay below 0.5 for T_act to be the single "
                "interval [0, L)"),
    reference=REF)
json.dump(out, open(os.path.join(HERE, "outputs", "p7_results.json"), "w"),
          indent=2, default=float)
with open(os.path.join(HERE, "outputs", "certified_table.csv"), "w",
          newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(V[0].__dict__)); w.writeheader()
    for v in V: w.writerow(v.__dict__)
from collections import Counter
print(Counter(v.status for v in V))
for v in V:
    print(f"{v.status:5s} {v.name:58s} pred {v.predicted:<9.5f} meas {v.measured:<10.6f} "
          f"diff {v.diff:+.3e}  CI [{v.ci_lo:+.2e},{v.ci_hi:+.2e}]  delta {v.delta:.2e}")
