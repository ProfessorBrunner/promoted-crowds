"""Stage 3 item P8 — finite-N extinction on the persistent branch, right-censored."""
import json, math, multiprocessing as mp, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config")); sys.path.insert(0, S2)
from crowd1 import engine as E
from crowd1.rng import derive_run_seed
from crowd1.runner import RunConfig, run_one
import p8_config as CFG
FX, DC = CFG.P8["fixed"], CFG.P8["declared"]

def worker(args):
    N, rep = args
    seed = derive_run_seed(CFG.MASTER_SEED, 8, N, rep)
    cfg = RunConfig(N=N, eps=FX["eps"], c_b=FX["c_b"], c_h=DC["c_h"],
                    alpha=FX["alpha"], beta=FX["beta"], r=FX["r"], lam=FX["lam"],
                    rho=FX["rho"], kappa=FX["kappa"], f=FX["f"],
                    pulses=((0.0, FX["pulse_angle"]),),
                    initial_law=FX["initial_law"], t_end=FX["T_max"],
                    stop_on_extinction=True, sample_times=(FX["T_max"],))
    o = run_one(cfg, seed)
    tf = float(o["agg"][E.A_TFINAL])
    # stop_on_extinction ends the run when no agent is active; a run that reaches
    # T_max is RIGHT-CENSORED, not extinct.
    extinct = tf < FX["T_max"] - 1e-9
    return dict(N=N, rep=rep, seed=int(seed), t_final=tf,
                extinct=bool(extinct),
                time=tf if extinct else FX["T_max"],
                mean_A=float(o["agg"][E.A_INTA] / N / max(tf, 1e-30)))

def km_median(times, events, T_max):
    """Kaplan-Meier survival; median only if S drops to <= 0.5 within the horizon."""
    order = np.argsort(times)
    t, e = np.asarray(times)[order], np.asarray(events)[order]
    n, S, curve = len(t), 1.0, []
    at_risk = n
    i = 0
    while i < n:
        tt = t[i]
        d = int(((t == tt) & (e == 1)).sum())
        c = int(((t == tt) & (e == 0)).sum())
        if d > 0:
            S *= (1.0 - d / at_risk)
            curve.append((float(tt), float(S)))
        at_risk -= (d + c)
        i += d + c
    med = None
    for tt, s in curve:
        if s <= 0.5:
            med = tt
            break
    return med, curve

if __name__ == "__main__":
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    res = dict(master_seed=CFG.MASTER_SEED, T_max=FX["T_max"],
               lam=FX["lam"], f=FX["f"], A_star=DC["A_star"], cells=[])
    try:
        for N in FX["N_list"]:
            rows = pool.map(worker, [(N, r) for r in range(FX["replicates"])])
            times = np.array([r["time"] for r in rows])
            ev = np.array([1 if r["extinct"] else 0 for r in rows])
            med, curve = km_median(times, ev, FX["T_max"])
            n_ext = int(ev.sum())
            res["cells"].append(dict(
                N=N, replicates=len(rows), n_extinct=n_ext,
                n_censored=len(rows) - n_ext,
                fraction_extinct=float(n_ext / len(rows)),
                median=(float(med) if med is not None else None),
                median_report=(f"{med:.3f}" if med is not None
                               else f"median > T_max = {FX['T_max']:.0f}"),
                extinction_times_observed=[float(r["time"]) for r in rows
                                           if r["extinct"]],
                km_curve=curve,
                mean_A_over_run=float(np.mean([r["mean_A"] for r in rows])),
                seeds=[r["seed"] for r in rows]))
            print(f"  N={N:<5} extinct {n_ext}/{len(rows)}  -> "
                  f"{res['cells'][-1]['median_report']}", flush=True)
    finally:
        pool.close(); pool.join()
    json.dump(res, open(os.path.join(HERE, "outputs", "raw", "p8_raw.json"), "w"),
              indent=2, default=float)
    print("done", flush=True)
