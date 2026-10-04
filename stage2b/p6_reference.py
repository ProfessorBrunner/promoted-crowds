"""Stage 2B task 3: the P6 case B reference, and the case A validation of the solver.

Three pieces:
  (a) kinetic h-refinement of case A's registered marker t_dagger (validation);
  (b) kinetic reference for case B's t* = inf{t : A(t) <= 0.325} and
      Lambda* = lambda int_0^{t*} A ds, with the same refinement;
  (c) an agent re-run of the 50 case-B replicates that SAVES the A(t) traces, so
      the crossing of the mean trajectory and the mean of the replicate crossings
      can both be reported (the Stage 2 run kept only the latter).
Writes outputs/raw/p6b_*.json.  Nothing here changes any Stage 2 verdict.
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

import kinetic as KIN                                                  # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")
os.makedirs(OUT, exist_ok=True)


def kinetic_series(tag, *, alpha, r, lam, c_b, level, T, c_min, hs):
    rows = []
    for h in hs:
        t, A, d = KIN.solve(lam=lam, alpha=alpha, r=r, c_b=c_b, f=1.0, T=T,
                            h=h, c_min=c_min, K=3)
        tc = KIN.first_down_crossing(t, A, level)
        rows.append(dict(h=d["h"], t_cross=tc,
                         Lambda=KIN.accumulated_index(t, A, lam, tc),
                         lam_intA_total=lam * float(np.trapezoid(A, t)),
                         A0=float(A[0]), n_slabs=d["n_slabs"], J=d["J"],
                         mass_deficit=1.0 - d["mass"], slab_leak=d["slab_leak"]))
        print(f"  [{tag}] h={d['h']:.6f} t_cross={tc:.5f} "
              f"Lambda={rows[-1]['Lambda']:.5f} "
              f"leak={d['slab_leak']:.1e} massdef={1-d['mass']:.1e}", flush=True)
    return rows


def richardson(rows, key):
    """First-order Richardson on the two finest grids, with the order measured."""
    out = dict(value_finest=rows[-1][key])
    if len(rows) >= 3:
        d1 = rows[-2][key] - rows[-3][key]
        d2 = rows[-1][key] - rows[-2][key]
        out["observed_order"] = (float(math.log2(abs(d1 / d2)))
                                 if d2 != 0 and d1 / d2 > 0 else None)
    if len(rows) >= 2:
        out["richardson"] = rows[-1][key] + (rows[-1][key] - rows[-2][key])
        out["uncertainty"] = abs(rows[-1][key] - rows[-2][key])
    return out


def save(res):
    with open(os.path.join(OUT, "p6_reference.json"), "w") as fh:
        json.dump(res, fh, indent=2)


if __name__ == "__main__":
    parts = sys.argv[1] if len(sys.argv) > 1 else "abc"
    res = {}
    fp = os.path.join(OUT, "p6_reference.json")
    if os.path.exists(fp):
        res = json.load(open(fp))

    if "a" in parts:
        print("(a) P6 case A kinetic validation: t_dagger at A_f = 0.5603", flush=True)
        rowsA = kinetic_series("A", alpha=2.0, r=0.99, lam=3.0, c_b=0.5,
                               level=0.5603, T=95.0, c_min=0.02,
                               hs=[0.01, 0.005, 0.0025])
        res["case_A_kinetic"] = dict(
            rows=rowsA, t_dagger=richardson(rowsA, "t_cross"),
            registered=70.3, registered_err=0.1)
        save(res)

    if "b" in parts:
        print("(b) P6 case B kinetic reference: t* at A = 0.325", flush=True)
        rowsB = kinetic_series("B", alpha=1.0, r=0.95, lam=2.5, c_b=0.4,
                               level=0.325, T=40.0, c_min=0.01,
                               hs=[0.01, 0.005, 0.0025, 0.00125, 0.000625])
        res["case_B_kinetic"] = dict(
            rows=rowsB, t_star=richardson(rowsB, "t_cross"),
            Lambda_star=richardson(rowsB, "Lambda"),
            lam_intA_total=richardson(rowsB, "lam_intA_total"), level=0.325)
        save(res)

    print("(c) P6 case B agent re-run with traces saved", flush=True)
    import config.stage2_config as CFG                                 # noqa: E402
    from crowd1 import tests_s2 as T2                                  # noqa: E402
    import multiprocessing as mp
    CFG_PATH = os.path.join(S2, "config", "stage2_config.py")
    jobs = [(CFG_PATH, "B", rep) for rep in range(CFG.P6["fixed"]["replicates"])]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    try:
        resB = pool.map(T2.p6_worker, jobs)
    finally:
        pool.close(); pool.join()
    grid = np.arange(0.0, CFG.P6["declared"]["t_end_B"] + 1e-9,
                     CFG.P6["declared"]["sample_dt"])
    lamB = CFG.P6["fixed"]["B"]["lam"]
    traces = np.array([r["A_trace"] for r in resB])
    cums = np.array([r["cum_trace"] for r in resB])
    Amean = traces.mean(axis=0)
    cmean = cums.mean(axis=0)
    per_level = []
    for lev in [0.4, 0.35, 0.325, 0.3]:
        ts, Ls = [], []
        for k in range(len(resB)):
            tc = T2._first_down_crossing(grid, traces[k], lev)
            if not math.isnan(tc):
                ts.append(tc)
                Ls.append(float(np.interp(tc, grid, cums[k])))
        tc_mt = T2._first_down_crossing(grid, Amean, lev)
        per_level.append(dict(
            level=lev, n_crossed=len(ts),
            t_cross_mean_of_replicates=float(np.mean(ts)) if ts else None,
            t_cross_sd=float(np.std(ts, ddof=1)) if len(ts) > 1 else None,
            Lambda_mean_of_replicates=float(np.mean(Ls)) if Ls else None,
            Lambda_sd=float(np.std(Ls, ddof=1)) if len(Ls) > 1 else None,
            t_cross_of_mean_trajectory=tc_mt,
            Lambda_at_mean_trajectory_crossing=(
                float(np.interp(tc_mt, grid, cmean))
                if not math.isnan(tc_mt) else None)))
        print(f"  [B agents] level={lev}: mean-of-crossings "
              f"{per_level[-1]['t_cross_mean_of_replicates']}, "
              f"mean-trajectory {tc_mt}", flush=True)
    res["case_B_agents"] = dict(
        N=CFG.P6["fixed"]["N"], replicates=len(resB), per_level=per_level,
        lam_intA_total_mean=float(np.mean([lamB * r["intA"] for r in resB])),
        lam_intA_total_sd=float(np.std([lamB * r["intA"] for r in resB], ddof=1)),
        sample_dt=CFG.P6["declared"]["sample_dt"])
    np.save(os.path.join(OUT, "p6b_A_mean_trace.npy"), Amean)
    np.save(os.path.join(OUT, "p6b_cum_mean_trace.npy"), cmean)

    save(res)
    print("done", flush=True)
