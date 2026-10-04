"""Stage 3 item P7 — finite-amplitude observables (C9(a)).  Runner.

Estimands, under the owner's ruling (2) of 2026-10-01:

  A_max = sup_t A(t)                      registered on the MEAN TRAJECTORY
  T_act = Leb{ t : A(t) > A_max/2 }        registered on the MEAN TRAJECTORY
  I     = int_0^inf A(t) dt                reported once (linear in A, so the
                                           mean trajectory and the per-replicate
                                           average coincide identically)

The per-replicate averages of A_max and T_act are computed too and reported beside
the registered values as finite-N diagnostics, without verdicts.

I is NOT taken from the sampling grid: the engine accumulates the exact int A dt
event by event (agg[A_INTA]), so I carries no grid error whatsoever.  The grid is
needed only for A_max and T_act, and only near t = L -- A(t) rises strictly on
[0, L) because every activated agent gets c = 1 and so cannot shut off before its
own age L, and every cohort member shuts off in [L, L_plus], a window of width
2e-6.  So A_max = A(L-) and the crossing of A_max/2 is a jump at L.  The grid is
fine on [0, 2] and coarse after; the coarse part is scanned to confirm that A never
re-crosses A_max/2 later, rather than assuming it.

Outbreak, under ruling (1): ever-active count among agents OUTSIDE the campaign
cohort exceeds 1% of N within the horizon.  P7 registers no outbreak number, so it
is reported without a verdict.
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
from crowd1.runner import RunConfig, run_one                           # noqa: E402
import p7_config as CFG                                                # noqa: E402

FX, DC = CFG.P7["fixed"], CFG.P7["declared"]
L = math.log(1.0 / FX["c_b"]) / FX["eps"]
OUT = os.path.join(HERE, "outputs")


def build_grid(fine_dt):
    fine = np.arange(0.0, DC["fine_end"] + 1e-12, fine_dt)
    coarse = np.arange(DC["fine_end"] + DC["coarse_dt"], DC["t_end"] + 1e-9,
                       DC["coarse_dt"])
    return np.concatenate([fine, coarse])


def observables(grid, A, fine_dt):
    """A_max, T_act on one activity trace, plus the late-re-crossing check.

    T_act is the Lebesgue measure of {A > A_max/2}, computed as the total length
    of the grid intervals whose left endpoint is above the threshold.  With a jump
    discontinuity at t = L this is the right construction: no interpolation across
    the jump.
    """
    A_max = float(A.max())
    if A_max <= 0.0:
        return 0.0, 0.0, 0.0, 0.0
    thr = 0.5 * A_max
    dtv = np.diff(grid, append=grid[-1] + DC["coarse_dt"])
    above = A > thr
    T_act = float(dtv[above].sum())
    t_argmax = float(grid[int(np.argmax(A))])
    # does A come back above A_max/2 after the first descent?  (checked, not assumed)
    first_below = np.argmax(~above) if (~above).any() else len(A)
    late = float(A[first_below:].max()) if first_below < len(A) else 0.0
    return A_max, T_act, t_argmax, late / A_max if A_max > 0 else 0.0


def worker(args):
    f, N, rep, fine_dt, order = args
    grid = build_grid(fine_dt)
    pulses = {"single": ((0.0, FX["pulse_T"]),),
              "T_Tperp": ((0.0, FX["pulse_T"]), (0.0, FX["pulse_Tperp"])),
              "Tperp_T": ((0.0, FX["pulse_Tperp"]), (0.0, FX["pulse_T"]))}[order]
    seed = derive_run_seed(CFG.MASTER_SEED, 7, int(f * 1000), N, rep,
                           {"single": 0, "T_Tperp": 1, "Tperp_T": 2}[order])
    cfg = RunConfig(N=N, eps=FX["eps"], c_b=FX["c_b"], c_h=FX["c_h"],
                    alpha=FX["alpha"], beta=FX["beta"], r=FX["r"], lam=FX["lam"],
                    rho=FX["rho"], kappa=FX["kappa"], f=f, pulses=pulses,
                    initial_law=FX["initial_law"], t_end=DC["t_end"],
                    stop_on_extinction=True, sample_times=tuple(grid),
                    extra_registry_angles=(FX["pulse_T"], FX["pulse_Tperp"]))
    o = run_one(cfg, seed)
    A = np.where(o["sampleA"] >= 0, o["sampleA"], 0).astype(float) / N
    A_max, T_act, t_arg, late_ratio = observables(grid, A, fine_dt)
    u = o["u"].astype(bool)
    ea = o["ever_active"].astype(bool)
    return dict(
        f=f, N=N, rep=rep, order=order, fine_dt=fine_dt, seed=int(seed),
        realized_reach=float(u.sum() / N),
        I_exact=float(o["agg"][E.A_INTA] / N),       # exact, not from the grid
        A_max=A_max, T_act=T_act, t_argmax=t_arg, late_recross_ratio=late_ratio,
        ever_active_frac=float(ea.sum() / N),
        ever_active_outside_cohort=float((ea & ~u).sum() / N),   # ruling (1)
        t_final=float(o["agg"][E.A_TFINAL]), A_trace=A)


def cell(f, N, nrep, fine_dt, order, pool, boot=2000):
    rows = pool.map(worker, [(f, N, rep, fine_dt, order) for rep in range(nrep)])
    grid = build_grid(fine_dt)
    tr = np.array([r["A_trace"] for r in rows])
    Abar = tr.mean(axis=0)
    mt_Amax, mt_Tact, mt_arg, mt_late = observables(grid, Abar, fine_dt)
    # The mean-trajectory functionals are ONE number per cell, not replicate means,
    # so a Student-t interval across replicates does not apply.  Their sampling
    # uncertainty comes from resampling the replicate traces with replacement and
    # rebuilding the mean trajectory.
    rng = np.random.default_rng(CFG.MASTER_SEED + int(f * 1000) + N)
    bA = np.empty(boot); bT = np.empty(boot)
    for b in range(boot):
        idx = rng.integers(0, nrep, nrep)
        bA[b], bT[b], _, _ = observables(grid, tr[idx].mean(axis=0), fine_dt)
    bA_lo, bA_hi = np.percentile(bA, [2.5, 97.5])
    bT_lo, bT_hi = np.percentile(bT, [2.5, 97.5])
    per = lambda k: np.array([r[k] for r in rows])
    out = dict(
        f=f, N=N, order=order, fine_dt=fine_dt, replicates=nrep,
        # registered endpoint: the mean trajectory (ruling 2)
        A_max_mean_trajectory=mt_Amax, T_act_mean_trajectory=mt_Tact,
        A_max_mt_boot=[float(bA_lo), float(bA_hi)],
        T_act_mt_boot=[float(bT_lo), float(bT_hi)], boot_B=boot,
        t_argmax_mean_trajectory=mt_arg,
        late_recross_ratio_mean_trajectory=mt_late,
        # finite-N diagnostics, no verdict (ruling 2)
        A_max_per_replicate_mean=float(per("A_max").mean()),
        A_max_per_replicate_sd=float(per("A_max").std(ddof=1)),
        T_act_per_replicate_mean=float(per("T_act").mean()),
        T_act_per_replicate_sd=float(per("T_act").std(ddof=1)),
        # I: reported once
        I_mean=float(per("I_exact").mean()), I_sd=float(per("I_exact").std(ddof=1)),
        realized_reach_mean=float(per("realized_reach").mean()),
        ever_active_frac_mean=float(per("ever_active_frac").mean()),
        ever_active_outside_cohort_mean=float(per("ever_active_outside_cohort").mean()),
        outbreak_count_new_rule=int((per("ever_active_outside_cohort")
                                     > CFG.OUTBREAK_FRACTION).sum()),
        max_late_recross_ratio=float(per("late_recross_ratio").max()),
        t_final_max=float(per("t_final").max()),
        t_argmax_per_replicate_sd=float(per("t_argmax").std(ddof=1)),
        seeds=[r["seed"] for r in rows])
    return out, {k: per(k) for k in ("A_max", "T_act", "I_exact", "t_argmax",
                                     "ever_active_outside_cohort")}, (Abar, grid)


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
    nrep, N0, dt0 = FX["replicates"], FX["N"], DC["fine_dt"]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    res = dict(L=L, master_seed=CFG.MASTER_SEED, cells=[], per_replicate={})
    MEANTR = {}
    try:
        for order in ("single", "T_Tperp", "Tperp_T"):
            for f in FX["reaches"]:
                c, per, (Abar, grid) = cell(f, N0, nrep, dt0, order, pool)
                res["cells"].append(c)
                MEANTR[f"{order}_f{f}"] = Abar
                res["per_replicate"][f"{order}_f{f}"] = {k: v.tolist()
                                                         for k, v in per.items()}
                print(f"  {order:9s} f={f:<5} A_max(mt)={c['A_max_mean_trajectory']:.6f} "
                      f"I={c['I_mean']:.6f} T_act(mt)={c['T_act_mean_trajectory']:.6f} "
                      f"outbreak={c['outbreak_count_new_rule']}/{nrep}", flush=True)
        ladder = []
        for N in DC["N_ladder"]:
            c, _, _ = cell(DC["ladder_reach"], N, nrep, dt0, "single", pool)
            ladder.append(c)
            print(f"  ladder N={N:<7} A_max(mt)={c['A_max_mean_trajectory']:.7f} "
                  f"I={c['I_mean']:.7f}", flush=True)
        res["N_ladder"] = ladder
        grids = []
        for dt in DC["fine_dt_ladder"]:
            c, _, _ = cell(DC["ladder_reach"], N0, nrep, dt, "single", pool)
            grids.append(c)
            print(f"  grid dt={dt}: A_max(mt)={c['A_max_mean_trajectory']:.7f} "
                  f"T_act(mt)={c['T_act_mean_trajectory']:.7f}", flush=True)
        res["grid_refinement"] = grids
    finally:
        pool.close()
        pool.join()
    with open(os.path.join(OUT, "raw", "p7_raw.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    np.savez_compressed(os.path.join(OUT, "raw", "p7_mean_traces.npz"),
                        grid=build_grid(dt0), **MEANTR)
    print("done", flush=True)
