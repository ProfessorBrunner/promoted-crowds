"""Stage 3 item P5 — class-1 onset.  Runner.

Design v0.3.1 A4, item P5: r = 1, alpha = 2, beta = 0, c_b = 0.5, kappa = rho = 0,
I1, one pulse of reach f.  Predicted (mean field): lambda L > 1 with L = ln 2 means
any positive reach reaches the persistent branch; at lambda = 2, A* = 0.5;
lambda L < 1 (lambda = 1) means activity dies.  Finite-N: positive seeds can die
out; report outbreak probability at f = 0.01 and 0.1.  N = 1e5, 50 replicates.

Owner's Stage 3 estimand definitions (2026-10-01): survival means A(20) > 0;
burn-in [0, 20]; observation window [20, 70]; active-branch statistics conditioned
on A(20) > 0 and reported with the survival fraction; unconditional long-time
activity is NOT an endpoint.

Why A* = 0.5 is exact and carries no numerical error: in this sector r = 1 and
alpha = 2 > c_b, so every receipt clips conviction to 1 and refreshes the shut-off
deadline to t + L; C9(b) then gives A* = 1 - exp(-lambda L A*), and at lambda = 2,
L = ln 2 this is 1 - exp(-ln 2) = 1/2 identically.
"""
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config"))
sys.path.insert(0, S2)

from crowd1 import engine as E                                         # noqa: E402
from crowd1.a6 import (make_verdict, wilson_interval,                  # noqa: E402
                       finite_N_bias_from_ladder)
from crowd1.rng import derive_run_seed                                 # noqa: E402
from crowd1.runner import RunConfig, run_one                           # noqa: E402
import p5_config as CFG                                                # noqa: E402

OUT = os.path.join(HERE, "outputs")
FX, DC = CFG.P5["fixed"], CFG.P5["declared"]
L = math.log(1.0 / FX["c_b"])


def A_star(lam):
    """Unique positive root of A = 1 - exp(-lambda L A), or 0 when lambda L <= 1."""
    if lam * L <= 1.0:
        return 0.0
    a = 0.5
    for _ in range(200):                      # Newton; converges in a few steps
        fa = 1.0 - math.exp(-lam * L * a) - a
        dfa = lam * L * math.exp(-lam * L * a) - 1.0
        a -= fa / dfa
    return a


def worker(args):
    lam, f, N, rep, dt = args
    t_end = DC["t_end"]
    grid = np.arange(0.0, t_end + 1e-9, dt)
    seed = derive_run_seed(CFG.MASTER_SEED, 5, int(lam * 100), int(f * 1000), N, rep)
    cfg = RunConfig(N=N, eps=FX["eps"], c_b=FX["c_b"], c_h=DC["c_h"],
                    alpha=FX["alpha"], beta=FX["beta"], r=FX["r"], lam=lam,
                    rho=FX["rho"], kappa=FX["kappa"], f=f,
                    pulses=((0.0, FX["pulse_angle"]),), initial_law=FX["initial_law"],
                    t_end=t_end, stop_on_extinction=True,
                    sample_times=tuple(grid))
    o = run_one(cfg, seed)
    A = np.where(o["sampleA"] >= 0, o["sampleA"], 0).astype(float) / N
    i20 = int(round(FX["burn_in_end"] / dt))
    w0, w1 = (int(round(x / dt)) for x in FX["window"])
    alive = bool(A[i20] > 0.0)
    return dict(
        lam=lam, f=f, N=N, rep=rep, dt=dt, seed=int(seed),
        realized_reach=float(o.get("realized_reach", f)),
        A_at_20=float(A[i20]), alive_at_20=alive,
        window_mean_A=float(np.trapezoid(A[w0:w1 + 1], grid[w0:w1 + 1])
                            / (grid[w1] - grid[w0])),
        A_at_70=float(A[-1]), A_max=float(A.max()),
        ever_active_frac=float(int(o["ever_active"].sum()) / N),
        min_c=float(o["c_final"].min()) if "c_final" in o else float("nan"),
        n_stance_minus=int((o["s_final"] < 0).sum()),
        t_final=float(o["agg"][E.A_TFINAL]),
        A_trace=A)


def cell(lam, f, N, nrep, dt, pool):
    rows = pool.map(worker, [(lam, f, N, rep, dt) for rep in range(nrep)])
    tr = np.array([r["A_trace"] for r in rows])
    alive = np.array([r["alive_at_20"] for r in rows])
    wm = np.array([r["window_mean_A"] for r in rows])
    return dict(lam=lam, f=f, N=N, dt=dt, replicates=nrep,
                survivors=int(alive.sum()),
                survival_fraction=float(alive.mean()),
                window_mean_A_conditional=(float(wm[alive].mean())
                                           if alive.any() else None),
                window_mean_A_conditional_sd=(float(wm[alive].std(ddof=1))
                                              if alive.sum() > 1 else None),
                window_mean_A_unconditional=float(wm.mean()),
                A_at_20_mean=float(np.mean([r["A_at_20"] for r in rows])),
                A_at_70_mean=float(np.mean([r["A_at_70"] for r in rows])),
                A_max_mean=float(np.mean([r["A_max"] for r in rows])),
                realized_reach_mean=float(np.mean([r["realized_reach"]
                                                   for r in rows])),
                ever_active_frac_mean=float(np.mean([r["ever_active_frac"]
                                                     for r in rows])),
                # A4a outbreak endpoint: ever-active fraction > 1% of N.  Measured
                # over the WHOLE run; see AMBIGUITIES P5-A2 on its degeneracy here.
                outbreak_count=int(sum(r["ever_active_frac"]
                                       > CFG.OUTBREAK_FRACTION for r in rows)),
                min_conviction=float(min(r["min_c"] for r in rows)),
                n_stance_minus=int(sum(r["n_stance_minus"] for r in rows)),
                seeds=[r["seed"] for r in rows]), wm, alive, tr


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
    nrep, N0 = FX["replicates"], FX["N"]
    res = dict(L=L, A_star_lambda2=A_star(2.0), A_star_lambda1=A_star(1.0),
               master_seed=CFG.MASTER_SEED, burn_in_end=FX["burn_in_end"],
               window=list(FX["window"]), survival="A(20) > 0")
    assert abs(res["A_star_lambda2"] - 0.5) < 1e-15, res["A_star_lambda2"]

    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    cells, store = [], {}
    try:
        for lam in FX["lambdas"]:
            for f in FX["reaches"]:
                c, wm, alive, tr = cell(lam, f, N0, nrep, DC["sample_dt"], pool)
                cells.append(c)
                store[(lam, f)] = (wm, alive, tr)
                print(f"  lam={lam} f={f}: survival {c['survivors']}/{nrep}, "
                      f"window mean A (cond) {c['window_mean_A_conditional']}",
                      flush=True)
        # A6 error source 2: N ladder at the persistent cells
        ladders = {}
        for f in FX["reaches"]:
            rung = []
            for N in DC["N_ladder"]:
                c, _, _, _ = cell(2.0, f, N, nrep, DC["sample_dt"], pool)
                rung.append(c)
                print(f"  ladder lam=2 f={f} N={N}: "
                      f"{c['window_mean_A_conditional']}", flush=True)
            ladders[str(f)] = rung
        # A6 error source 3 on the measurement side: sampling-grid refinement
        grids = []
        for dt in DC["sample_dt_ladder"]:
            c, _, _, _ = cell(2.0, 0.10, N0, nrep, dt, pool)
            grids.append(c)
            print(f"  grid dt={dt}: {c['window_mean_A_conditional']}", flush=True)
    finally:
        pool.close()
        pool.join()

    res["cells"] = cells
    res["N_ladder"] = ladders
    res["grid_refinement"] = grids
    with open(os.path.join(OUT, "raw", "p5_raw.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    np.savez_compressed(os.path.join(OUT, "raw", "p5_traces.npz"),
                        **{f"lam{lam}_f{f}": store[(lam, f)][2]
                           for (lam, f) in store})
    print("done", flush=True)
