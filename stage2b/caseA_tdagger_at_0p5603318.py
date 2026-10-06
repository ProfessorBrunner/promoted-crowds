"""Crossing-level shift for P6 case A: first downward crossing of
A = 0.5603318 (the Proposition 4 / C7(c) dose-mixture fold activity) against the
archived crossings of the declared marker A = 0.5603.

Kinetic: the existing h ladder (0.0100052, 0.0050026, 0.0024997) with the same
Richardson construction as the archived 70.3277 +- 0.0244.
Agent: the 50 registered replicates at their recorded seeds, crossings by
tests_s2._first_down_crossing on the declared 0.1 sample grid, Student-t 49 df.

Both levels are evaluated from the same run so the shift is a paired difference,
and recomputing at 0.5603 reproduces the archive exactly as a control.

Writes stage2b/outputs/raw/caseA_tdagger_at_0p5603318.json.
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
LEV_OLD = 0.5603                      # declared marker, stage2_config.py:163
LEV_NEW = 0.5603318                   # Prop. 4 fold activity, tex L612
CS_FOLD = 0.5603318621202521          # CS-computed fold activity, caseA_fold_v2
ARCH = dict(kinetic_richardson=70.32768783769728,
            kinetic_unc=0.024354959755214622,
            kinetic_finest=70.30333287794207,
            agent_mean=70.35303633651682,
            agent_ci=[70.32878516161954, 70.37728751141411],
            agent_halfwidth=0.02425117489728846)


def kinetic(level):
    import p6_reference as P6R
    rows = P6R.kinetic_series(f"A@{level}", alpha=2.0, r=0.99, lam=3.0, c_b=0.5,
                              level=level, T=95.0, c_min=0.02,
                              hs=[0.01, 0.005, 0.0025])
    return rows, P6R.richardson(rows, "t_cross")


def agents(levels):
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
    from scipy import stats
    out = {}
    for lv in levels:
        td = np.array([T2._first_down_crossing(grid, a, lv) for a in tr])
        n = len(td)
        mean, sd = float(td.mean()), float(td.std(ddof=1))
        tm = float(stats.t.ppf(0.975, n - 1))
        hw = tm * sd / math.sqrt(n)
        out[repr(lv)] = dict(level=lv, replicates=n, mean=mean, sd=sd,
                             t_multiplier_df=n - 1, t_multiplier=tm,
                             ci95_halfwidth=hw, ci95_lo=mean - hw,
                             ci95_hi=mean + hw, per_replicate=td.tolist(),
                             mean_trajectory=float(
                                 T2._first_down_crossing(grid, tr.mean(axis=0), lv)))
    # paired per-replicate shift
    a, b = out[repr(levels[0])], out[repr(levels[1])]
    d = np.array(b["per_replicate"]) - np.array(a["per_replicate"])
    n = len(d)
    tm = float(stats.t.ppf(0.975, n - 1))
    hw = tm * float(d.std(ddof=1)) / math.sqrt(n)
    out["paired_shift_new_minus_old"] = dict(
        mean=float(d.mean()), sd=float(d.std(ddof=1)),
        ci95_lo=float(d.mean()) - hw, ci95_hi=float(d.mean()) + hw,
        ci95_halfwidth=hw, t_multiplier_df=n - 1)
    return out


if __name__ == "__main__":
    res = dict(level_old=LEV_OLD, level_new=LEV_NEW, cs_fold_activity=CS_FOLD,
               archived=ARCH)

    print(f"kinetic ladder at A = {LEV_NEW}", flush=True)
    rows_new, rich_new = kinetic(LEV_NEW)
    print(f"kinetic ladder at A = {LEV_OLD} (control)", flush=True)
    rows_old, rich_old = kinetic(LEV_OLD)
    res["kinetic"] = dict(new=dict(rows=rows_new, **rich_new),
                          old_control=dict(rows=rows_old, **rich_old))
    res["kinetic"]["control_reproduces_archive"] = dict(
        richardson_diff=rich_old["richardson"] - ARCH["kinetic_richardson"],
        finest_diff=rich_old["value_finest"] - ARCH["kinetic_finest"])
    res["kinetic"]["shift_vs_archive"] = dict(
        richardson=rich_new["richardson"] - ARCH["kinetic_richardson"],
        richardson_value=rich_new["richardson"],
        richardson_unc=rich_new["uncertainty"],
        finest=rich_new["value_finest"] - ARCH["kinetic_finest"],
        finest_value=rich_new["value_finest"])

    print("agent replicates", flush=True)
    ag = agents([LEV_OLD, LEV_NEW])
    res["agent"] = ag
    a_old, a_new = ag[repr(LEV_OLD)], ag[repr(LEV_NEW)]
    res["agent"]["control_reproduces_archive"] = dict(
        mean_diff=a_old["mean"] - ARCH["agent_mean"],
        halfwidth_diff=a_old["ci95_halfwidth"] - ARCH["agent_halfwidth"])
    res["agent"]["shift_vs_archive"] = dict(
        mean=a_new["mean"] - ARCH["agent_mean"], mean_value=a_new["mean"],
        ci95=[a_new["ci95_lo"], a_new["ci95_hi"]],
        ci95_halfwidth=a_new["ci95_halfwidth"],
        mean_trajectory=a_new["mean_trajectory"] - ARCH["agent_mean"])

    # sensitivity dt_dagger/dA from the two levels, and the CS-fold correction
    dA = LEV_NEW - LEV_OLD
    sens = (rich_new["richardson"] - rich_old["richardson"]) / dA
    res["sensitivity"] = dict(
        dA=dA, dt_dagger_dA_kinetic=sens,
        dt_dagger_dA_agent=(a_new["mean"] - a_old["mean"]) / dA,
        cs_fold_minus_printed=CS_FOLD - LEV_NEW,
        implied_t_dagger_shift_from_cs_fold=sens * (CS_FOLD - LEV_NEW))

    json.dump(res, open(os.path.join(OUT, "caseA_tdagger_at_0p5603318.json"), "w"),
              indent=2)
    k, a = res["kinetic"], res["agent"]
    print(json.dumps(dict(kinetic_shift=k["shift_vs_archive"],
                          kinetic_control=k["control_reproduces_archive"],
                          agent_shift=a["shift_vs_archive"],
                          agent_control=a["control_reproduces_archive"],
                          paired=a["paired_shift_new_minus_old"],
                          sensitivity=res["sensitivity"]), indent=2), flush=True)
    print("wrote caseA_tdagger_at_0p5603318.json", flush=True)
