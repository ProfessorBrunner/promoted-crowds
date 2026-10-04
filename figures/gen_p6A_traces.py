"""F3 inputs: P6 case A agent mean trajectory + band, and the kinetic A(t).

Stage 2 kept only t_dagger and intA for case A, not the A(t) traces, so the 50
registered replicates are re-run here with the traces saved.  Same engine, same
config, same seeds as the Stage 2 run, so t_dagger must reproduce.
"""
import json, math, multiprocessing as mp, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(HERE), "stage2")
S2B = os.path.join(os.path.dirname(HERE), "stage2b")
sys.path.insert(0, S2); sys.path.insert(0, S2B)
from crowd1 import tests_s2 as T2
import config.stage2_config as CFG
import kinetic as KIN

if __name__ == "__main__":
    CFG_PATH = os.path.join(S2, "config", "stage2_config.py")
    nrep = CFG.P6["fixed"]["replicates"]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    try:
        res = pool.map(T2.p6_worker, [(CFG_PATH, "A", r) for r in range(nrep)])
    finally:
        pool.close(); pool.join()
    grid = np.arange(0.0, CFG.P6["declared"]["t_end_A"] + 1e-9,
                     CFG.P6["declared"]["sample_dt"])
    tr = np.array([r["A_trace"] for r in res])
    td = np.array([r["t_dagger"] for r in res])
    np.savez_compressed(os.path.join(HERE, "data", "f3_p6A_agent.npz"),
                        grid=grid, mean=tr.mean(axis=0), sd=tr.std(axis=0, ddof=1),
                        lo=np.percentile(tr, 2.5, axis=0),
                        hi=np.percentile(tr, 97.5, axis=0),
                        t_dagger=td, seeds=np.array([r["seed"] for r in res]))
    print(f"agents: t_dagger = {td.mean():.3f} +- {td.std(ddof=1):.3f} "
          f"(Stage 2 recorded 70.353 +- 0.085)", flush=True)
    cA = CFG.P6["fixed"]["A"]
    t, A, d = KIN.solve(lam=cA["lam"], alpha=cA["alpha"], r=cA["r"], c_b=cA["c_b"],
                        f=cA["f"], T=95.0, h=0.0025, c_min=0.02, K=3)
    np.savez_compressed(os.path.join(HERE, "data", "f3_p6A_kinetic.npz"),
                        t=t, A=A)
    json.dump(dict(kinetic_t_dagger=KIN.first_down_crossing(t, A, cA["crossing_level"]),
                   kinetic_h=d["h"], kinetic_slabs=d["n_slabs"],
                   crossing_level=cA["crossing_level"], adiabatic=cA["adiabatic"],
                   registered_t_dagger=cA["t_dagger"],
                   registered_t_dagger_err=cA["t_dagger_err"],
                   agent_t_dagger_mean=float(td.mean()),
                   agent_t_dagger_sd=float(td.std(ddof=1)), replicates=nrep,
                   N=CFG.P6["fixed"]["N"]),
              open(os.path.join(HERE, "data", "f3_meta.json"), "w"), indent=2)
    print("kinetic t_dagger =", KIN.first_down_crossing(t, A, cA["crossing_level"]),
          flush=True)
    print("done", flush=True)
