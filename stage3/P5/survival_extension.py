"""Stage 3 P5 — extra replicates for the two proportion endpoints.

Design A4 registers 50 replicates per cell for P5.  At 0/50 and 50/50 the Wilson
half-width is 0.0355, just above A4a's frozen precision target of 0.03 for
probability estimates.  The registered 50 are reported as registered; this pass adds
replicates to meet the precision target and both are reported.  Survival is
A(20) > 0, so these runs stop at t = 20 -- they are not a re-run of the window
statistics and change no window number.
"""
import json, math, multiprocessing as mp, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config")); sys.path.insert(0, S2)
from crowd1.a6 import wilson_interval
from crowd1.rng import derive_run_seed
from crowd1.runner import RunConfig, run_one
import p5_config as CFG
FX, DC = CFG.P5["fixed"], CFG.P5["declared"]

def worker(args):
    lam, f, rep = args
    N = FX["N"]; t20 = FX["burn_in_end"]
    seed = derive_run_seed(CFG.MASTER_SEED, 5, int(lam*100), int(f*1000), N, rep)
    cfg = RunConfig(N=N, eps=FX["eps"], c_b=FX["c_b"], c_h=DC["c_h"],
                    alpha=FX["alpha"], beta=FX["beta"], r=FX["r"], lam=lam,
                    rho=FX["rho"], kappa=FX["kappa"], f=f,
                    pulses=((0.0, FX["pulse_angle"]),), initial_law=FX["initial_law"],
                    t_end=t20, stop_on_extinction=True, sample_times=(t20,))
    o = run_one(cfg, seed)
    a = max(float(o["sampleA"][0]), 0.0) / N
    return dict(lam=lam, f=f, rep=rep, seed=int(seed), A_at_20=a,
                alive=bool(a > 0.0),
                ever_active_frac=float(int(o["ever_active"].sum()) / N))

if __name__ == "__main__":
    ntot = FX["replicates"] + DC["outbreak_extra_replicates"]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    res = {"replicates_registered": FX["replicates"], "replicates_total": ntot,
           "horizon": FX["burn_in_end"], "cells": []}
    try:
        for lam in FX["lambdas"]:
            for f in FX["reaches"]:
                rows = pool.map(worker, [(lam, f, r) for r in range(ntot)])
                al = np.array([r["alive"] for r in rows])
                m50, lo50, hi50, hw50 = wilson_interval(int(al[:50].sum()), 50)
                m, lo, hi, hw = wilson_interval(int(al.sum()), ntot)
                res["cells"].append(dict(
                    lam=lam, f=f, N=FX["N"],
                    registered_50=dict(k=int(al[:50].sum()), n=50, p=m50,
                                       lo=lo50, hi=hi50, half_width=hw50),
                    extended=dict(k=int(al.sum()), n=ntot, p=m, lo=lo, hi=hi,
                                  half_width=hw),
                    ever_active_frac_mean=float(np.mean(
                        [r["ever_active_frac"] for r in rows])),
                    seeds=[r["seed"] for r in rows]))
                print(f"  lam={lam} f={f}: survival {int(al.sum())}/{ntot} "
                      f"p={m:.5f} [{lo:.5f},{hi:.5f}] hw={hw:.5f} "
                      f"(registered 50: {int(al[:50].sum())}/50, hw={hw50:.5f})",
                      flush=True)
    finally:
        pool.close(); pool.join()
    json.dump(res, open(os.path.join(HERE,"outputs","raw","p5_survival_extension.json"),"w"),
              indent=2, default=float)
    print("done", flush=True)
