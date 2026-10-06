"""Two case-A checks, writing to stage2b/outputs/raw/.  Changes no figure or
manuscript file.

(1) Counter-offset hypothesis: rerun the dose-mixture fold with the dose index
    shifted by one, dose = alpha r^N with N ~ Poisson(H), instead of the
    manuscript's n = U + Poisson(H) (= 1 + Poisson(H) at f = 1).

(2) t-dagger of the CS fold activity A = 0.5647472640328673 from the archived
    case-A setup: kinetic on the existing h ladder with the same Richardson
    construction, and the 50 agent replicates at their recorded seeds.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(HERE), "stage2")
sys.path.insert(0, HERE)
sys.path.insert(0, S2)

OUT = os.path.join(HERE, "outputs", "raw")
os.makedirs(OUT, exist_ok=True)

CS_FOLD_A = 0.5647472640328673          # CS dose-mixture fold activity
CS_T_AD_F = 65.84387955279966           # CS adiabatic fold time
MANUSCRIPT = dict(A_f=0.5603318, H_f=158.354403, t_ad_f=66.30915)


# ------------------------------------------------------------------ (1)
def offset_test():
    import dose_mixture_fold as DMF
    ladder = []
    for M, N, nq in ((24, 128, 32), (32, 256, 48)):
        r = DMF.run(M, N, nq, lo=152.0, hi=168.0, offset=0)
        ladder.append(r)
        print(f"  [offset=0] M={M} N={N}: A_f={r['A_f']:.9f}  H_f={r['H_f']:.6f}  "
              f"t_ad_f={r['t_ad_f']:.6f}", flush=True)
    fin, prev = ladder[-1], ladder[-2]
    err = {k: abs(fin[k] - prev[k]) for k in ("A_f", "H_f", "t_ad_f")}
    dev = {"A_f": fin["A_f"] - MANUSCRIPT["A_f"],
           "H_f": fin["H_f"] - MANUSCRIPT["H_f"],
           "t_ad_f": fin["t_ad_f"] - MANUSCRIPT["t_ad_f"]}
    # does it reproduce the manuscript to its PRINTED digits?
    printed = {"A_f": f"{fin['A_f']:.7f}" == f"{MANUSCRIPT['A_f']:.7f}",
               "H_f": f"{fin['H_f']:.6f}" == f"{MANUSCRIPT['H_f']:.6f}",
               "t_ad_f": f"{fin['t_ad_f']:.5f}" == f"{MANUSCRIPT['t_ad_f']:.5f}"}
    out = dict(
        hypothesis="counter offset by one: dose = alpha r^N with N ~ Poisson(H), "
                   "i.e. mixture_weights(offset=0)",
        convention_used_in_first_run="n = U + Poisson(H), U ~ Bernoulli(f); at "
                                     "f = 1 this is n = 1 + Poisson(H), so the "
                                     "dose is alpha r^(1+N) -- the manuscript "
                                     "convention of Sec. V.C / C.7.1 / C.7.2",
        result=dict(A_f=fin["A_f"], H_f=fin["H_f"], t_ad_f=fin["t_ad_f"]),
        numerical_error=err, manuscript=MANUSCRIPT,
        deviation_from_manuscript=dev,
        reproduces_manuscript_to_printed_digits=printed,
        ladder=ladder)
    json.dump(out, open(os.path.join(OUT, "dose_mixture_fold_caseA_offset0.json"),
                        "w"), indent=2)
    for k in ("A_f", "H_f", "t_ad_f"):
        print(f"  {k}: offset0 {fin[k]!r} +-{err[k]:.1e}  manuscript "
              f"{MANUSCRIPT[k]}  dev {dev[k]:+.6g}  printed-match {printed[k]}",
              flush=True)
    return out


# ------------------------------------------------------------------ (2a)
def kinetic_tdagger(level):
    import p6_reference as P6R
    rows = P6R.kinetic_series("A@CSfold", alpha=2.0, r=0.99, lam=3.0, c_b=0.5,
                              level=level, T=95.0, c_min=0.02,
                              hs=[0.01, 0.005, 0.0025])
    return rows, P6R.richardson(rows, "t_cross")


# ------------------------------------------------------------------ (2b)
def agent_tdagger(level):
    import multiprocessing as mp
    import config.stage2_config as CFG
    from crowd1 import tests_s2 as T2
    cfg_path = os.path.join(S2, "config", "stage2_config.py")
    nrep = CFG.P6["fixed"]["replicates"]
    dc = CFG.P6["declared"]
    grid = np.arange(0.0, dc["t_end_A"] + 1e-9, dc["sample_dt"])
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    try:
        res = pool.map(T2.p6_worker, [(cfg_path, "A", r) for r in range(nrep)])
    finally:
        pool.close(); pool.join()
    tr = np.array([r["A_trace"] for r in res])
    seeds = [int(r["seed"]) for r in res]

    # reproduction check: the recorded level must give back the archived values
    arch = np.load(os.path.join(os.path.dirname(HERE), "figures", "data",
                                "f3_p6A_agent.npz"))
    td_old = np.array([T2._first_down_crossing(grid, a, 0.5603) for a in tr])
    repro = dict(max_abs_diff_vs_archived_t_dagger=float(
                     np.max(np.abs(td_old - arch["t_dagger"]))),
                 seeds_match=seeds == [int(s) for s in arch["seeds"]],
                 max_abs_diff_mean_trace=float(
                     np.max(np.abs(tr.mean(axis=0) - arch["mean"]))))

    td = np.array([T2._first_down_crossing(grid, a, level) for a in tr])
    n = len(td)
    mean = float(td.mean())
    sd = float(td.std(ddof=1))
    from scipy import stats
    tmult = float(stats.t.ppf(0.975, n - 1))
    hw = tmult * sd / math.sqrt(n)
    return dict(level=level, replicates=n, seeds=seeds,
                t_dagger_mean_of_replicates=mean, t_dagger_sd=sd,
                t_multiplier_df=n - 1, t_multiplier=tmult,
                ci95_halfwidth=hw, ci95_lo=mean - hw, ci95_hi=mean + hw,
                t_dagger_of_mean_trajectory=float(
                    T2._first_down_crossing(grid, tr.mean(axis=0), level)),
                reproduction_check=repro)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "offset"):
        print("(1) counter-offset hypothesis", flush=True)
        offset_test()
    if which in ("all", "tdagger"):
        print(f"(2) t_dagger at the CS fold activity A = {CS_FOLD_A!r}", flush=True)
        rows, rich = kinetic_tdagger(CS_FOLD_A)
        ag = agent_tdagger(CS_FOLD_A)
        res = dict(
            level=CS_FOLD_A, t_ad_f=CS_T_AD_F,
            kinetic=dict(rows=rows, **rich),
            agent=ag,
            comparison=dict(
                kinetic_richardson=dict(
                    t_dagger=rich["richardson"], unc=rich["uncertainty"],
                    delay=rich["richardson"] - CS_T_AD_F,
                    relative_adiabatic_error=(rich["richardson"] - CS_T_AD_F)
                    / rich["richardson"]),
                kinetic_finest=dict(
                    t_dagger=rich["value_finest"],
                    delay=rich["value_finest"] - CS_T_AD_F,
                    relative_adiabatic_error=(rich["value_finest"] - CS_T_AD_F)
                    / rich["value_finest"]),
                agent_mean_of_replicates=dict(
                    t_dagger=ag["t_dagger_mean_of_replicates"],
                    delay=ag["t_dagger_mean_of_replicates"] - CS_T_AD_F,
                    relative_adiabatic_error=(ag["t_dagger_mean_of_replicates"]
                                              - CS_T_AD_F)
                    / ag["t_dagger_mean_of_replicates"]),
                agent_mean_trajectory=dict(
                    t_dagger=ag["t_dagger_of_mean_trajectory"],
                    delay=ag["t_dagger_of_mean_trajectory"] - CS_T_AD_F,
                    relative_adiabatic_error=(ag["t_dagger_of_mean_trajectory"]
                                              - CS_T_AD_F)
                    / ag["t_dagger_of_mean_trajectory"])))
        json.dump(res, open(os.path.join(OUT, "caseA_tdagger_at_cs_fold.json"),
                            "w"), indent=2)
        print(json.dumps(res["comparison"], indent=2), flush=True)
        print("reproduction check:", json.dumps(ag["reproduction_check"]), flush=True)
    print("done", flush=True)
