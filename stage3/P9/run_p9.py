"""Stage 3 item P9 — two-camp fixed points and their stability.  Runner.

Measures (A_+, A_-) on the two-camp branch and tests stability by perturbing the
activity of each camp by +-0.05 and integrating the FINITE-N KINETIC DYNAMICS
forward (not iterating a fixed-point map), checking |Delta A| < 1e-3 at 10/eps.

The camps are fixed by construction and that is verified rather than assumed: a
positive agent's deposits are +alpha (accepted T) and +beta (rejected T_perp), both
positive, so conviction never changes sign; and the two-camp orientation law is
exactly invariant, since a positive agent rejecting a T_perp message moves to
90 + 90 = 180 = 0 degrees.  Both are checked every run.
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
from crowd1.rng import derive_run_seed                                 # noqa: E402
from crowd1.runner import RunConfig, run_one, copy_state               # noqa: E402
import p9_config as CFG                                                # noqa: E402

FX, RU, DC = CFG.P9["fixed"], CFG.P9["ruled"], CFG.P9["declared"]
OUT = os.path.join(HERE, "outputs")


def base_cfg(lam, N, t_end, grid):
    return RunConfig(N=N, eps=FX["eps"], c_b=RU["c_b"], c_h=DC["c_h"],
                     alpha=FX["alpha"], beta=FX["beta"], r=FX["r"], lam=lam,
                     rho=DC["rho"], kappa=FX["kappa"], f=1.0, pulses=(),
                     initial_law="two_camps", M_plus=FX["M_plus"],
                     two_camps_c=FX["camp_plus_c"], t_end=t_end,
                     stop_on_extinction=False, sample_times=tuple(grid))


def _AB(o, N):
    A = np.where(o["sampleA"] >= 0, o["sampleA"], 0).astype(float) / N
    Ap = np.where(o["sampleAp"] >= 0, o["sampleAp"], 0).astype(float) / N
    return A, Ap, A - Ap


def perturb(st, camp_plus, delta, c_b, rng):
    """Declared protocol; returns (new_state, achieved_shift, feasible)."""
    st = copy_state(st)
    c = st["c_last"]
    s = st["s"]
    N = c.shape[0]
    in_camp = (s == 1) if camp_plus else (s == -1)
    absc = np.abs(c)
    act = in_camp & (absc > c_b)
    ina = in_camp & (absc <= c_b)
    k = int(math.ceil(abs(delta) * N))
    if delta > 0:
        pool = np.flatnonzero(ina)
        if pool.size < k:
            return None, 0.0, False
        pick = pool[np.argsort(-absc[pool])[:k]]
        if not act.any():
            return None, 0.0, False
        target = float(np.median(absc[act]))
    else:
        pool = np.flatnonzero(act)
        if pool.size < k:
            return None, 0.0, False
        pick = rng.choice(pool, size=k, replace=False)
        if not ina.any():
            return None, 0.0, False
        target = float(np.median(absc[ina]))
    sign = 1.0 if camp_plus else -1.0
    before = float((in_camp & (np.abs(c) > c_b)).sum()) / N
    c[pick] = sign * target
    after = float((in_camp & (np.abs(c) > c_b)).sum()) / N
    return st, after - before, True


def worker(args):
    lam, N, rep = args
    seed = derive_run_seed(CFG.MASTER_SEED, 9, int(lam * 100), N, rep)
    t0, t1 = DC["burn_in"], DC["window"][1]
    grid = np.arange(0.0, t1 + 1e-9, DC["sample_dt"])
    cfg = base_cfg(lam, N, t1, grid)
    o = run_one(cfg, seed, return_state=True)
    A, Ap, Am = _AB(o, N)
    i0 = int(round(t0 / DC["sample_dt"]))
    eq = dict(A_plus=float(Ap[i0:].mean()), A_minus=float(Am[i0:].mean()),
              A_total=float(A[i0:].mean()))
    # invariance checks (not assumed)
    sf = o["s_final"]
    cf = o["c_final"]
    phif = o["phi_final"]
    checks = dict(
        stance_flips=int((sf != np.where(phif == 0, 1, -1)).sum()),
        orientation_off_target=int(((phif != 0) & (phif != 90)).sum()),
        positives_min_c=float(cf[sf == 1].min()),
        negatives_max_c=float(cf[sf == -1].max()))

    # ---- stability: perturb +-0.05 in each A_+- and integrate forward
    rng = np.random.default_rng(seed ^ 0x9E3779B9)
    pgrid = np.arange(0.0, FX["relax_time"] + 1e-9, DC["perturb_sample_dt"])
    perts = []
    st_eq = o["state"]
    for camp_plus in (True, False):
        for sgn in (+1.0, -1.0):
            d = sgn * FX["perturbation"]
            st2, achieved, ok = perturb(st_eq, camp_plus, d, RU["c_b"], rng)
            if not ok:
                perts.append(dict(camp="+" if camp_plus else "-", delta=d,
                                  feasible=False, reason="not enough agents on the "
                                  "source side of the threshold in that camp"))
                continue
            cfg2 = base_cfg(lam, N, FX["relax_time"], pgrid)
            o2 = run_one(cfg2, derive_run_seed(seed, 99, int(sgn), int(camp_plus)),
                         init_state=st2)
            A2, Ap2, Am2 = _AB(o2, N)
            perts.append(dict(
                camp="+" if camp_plus else "-", delta=d, feasible=True,
                achieved_shift=achieved,
                A_plus_0=float(Ap2[0]), A_minus_0=float(Am2[0]),
                A_plus_end=float(Ap2[-1]), A_minus_end=float(Am2[-1]),
                dA_plus_end=float(Ap2[-1] - eq["A_plus"]),
                dA_minus_end=float(Am2[-1] - eq["A_minus"]),
                trace_A_plus=[float(x) for x in Ap2],
                trace_A_minus=[float(x) for x in Am2]))
    return dict(lam=lam, N=N, rep=rep, seed=int(seed), eq=eq, checks=checks,
                perturbations=perts)


def cell(lam, N, nrep, pool):
    rows = pool.map(worker, [(lam, N, rep) for rep in range(nrep)])
    g = lambda k: np.array([r["eq"][k] for r in rows])
    out = dict(lam=lam, N=N, replicates=nrep,
               A_plus=float(g("A_plus").mean()), A_plus_sd=float(g("A_plus").std(ddof=1)),
               A_minus=float(g("A_minus").mean()), A_minus_sd=float(g("A_minus").std(ddof=1)),
               A_total=float(g("A_total").mean()),
               per_replicate=dict(A_plus=g("A_plus").tolist(),
                                  A_minus=g("A_minus").tolist()),
               checks=dict(stance_flips=int(sum(r["checks"]["stance_flips"] for r in rows)),
                           orientation_off_target=int(sum(r["checks"]["orientation_off_target"]
                                                          for r in rows)),
                           positives_min_c=float(min(r["checks"]["positives_min_c"] for r in rows)),
                           negatives_max_c=float(max(r["checks"]["negatives_max_c"] for r in rows))),
               seeds=[r["seed"] for r in rows])
    # stability summary over replicates, per perturbation
    npert = len(rows[0]["perturbations"])
    pert = []
    for i in range(npert):
        ps = [r["perturbations"][i] for r in rows]
        feas = [p for p in ps if p["feasible"]]
        rec = dict(camp=ps[0]["camp"], delta=ps[0]["delta"],
                   n_feasible=len(feas), n_replicates=len(ps))
        if feas:
            dp = np.array([p["dA_plus_end"] for p in feas])
            dm = np.array([p["dA_minus_end"] for p in feas])
            rec.update(
                achieved_shift_mean=float(np.mean([p["achieved_shift"] for p in feas])),
                A_plus_0_mean=float(np.mean([p["A_plus_0"] for p in feas])),
                dA_plus_end_mean=float(dp.mean()), dA_minus_end_mean=float(dm.mean()),
                max_abs_dA_end=float(max(np.abs(dp).max(), np.abs(dm).max())),
                n_relaxed=int(((np.abs(dp) < FX["relax_tol"]) &
                               (np.abs(dm) < FX["relax_tol"])).sum()),
                dA_plus_end_per_replicate=dp.tolist(),
                dA_minus_end_per_replicate=dm.tolist(),
                dA_plus_end_sem=float(dp.std(ddof=1) / math.sqrt(len(dp))),
                dA_minus_end_sem=float(dm.std(ddof=1) / math.sqrt(len(dm))),
                mean_trace_A_plus=np.mean([p["trace_A_plus"] for p in feas],
                                          axis=0).tolist(),
                mean_trace_A_minus=np.mean([p["trace_A_minus"] for p in feas],
                                           axis=0).tolist())
        else:
            rec["reason"] = ps[0].get("reason")
        pert.append(rec)
    out["perturbations"] = pert
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
    nrep, N0 = DC["replicates"], DC["N"]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    res = dict(master_seed=CFG.MASTER_SEED, c_b=RU["c_b"], cells=[])
    try:
        for lam in FX["lambdas"]:
            c = cell(lam, N0, nrep, pool)
            res["cells"].append(c)
            print(f"  lam={lam}: A_+={c['A_plus']:.6f} A_-={c['A_minus']:.6f} "
                  f"(sd {c['A_plus_sd']:.2e}/{c['A_minus_sd']:.2e}); "
                  f"flips {c['checks']['stance_flips']}, off-target "
                  f"{c['checks']['orientation_off_target']}", flush=True)
            for p in c["perturbations"]:
                if p["n_feasible"]:
                    print(f"     pert camp {p['camp']} {p['delta']:+.2f}: achieved "
                          f"{p['achieved_shift_mean']:+.4f}, |dA| at t=10 "
                          f"{p['max_abs_dA_end']:.2e}, relaxed "
                          f"{p['n_relaxed']}/{p['n_feasible']}", flush=True)
                else:
                    print(f"     pert camp {p['camp']} {p['delta']:+.2f}: INFEASIBLE "
                          f"- {p['reason']}", flush=True)
        ladder = []
        for N in DC["N_ladder"]:
            c = cell(DC["ladder_lambda"], N, nrep, pool)
            ladder.append({k: c[k] for k in ("lam", "N", "A_plus", "A_minus",
                                             "A_total")})
            print(f"  ladder N={N}: A_+={c['A_plus']:.7f} A_-={c['A_minus']:.7f}",
                  flush=True)
        res["N_ladder"] = ladder
    finally:
        pool.close()
        pool.join()
    with open(os.path.join(OUT, "raw", "p9_raw.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("done", flush=True)
