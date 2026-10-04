"""Stage 2B addendum — the P6 case B verdict, under the owner's ruling of 2026-10-01.

Ruling: "A = 0.325 is a declared trajectory marker, not 'half fold activity'.
Compare agent Lambda* (both crossing estimands) with the kinetic Lambda* =
25.42849 +- 0.01344 at delta = 5% and issue the verdict; 25.38 stays unverified;
20.35 is reported as the bridge-fold hazard with no comparison drawn."

Appendix F (now in the project) confirms case B's frozen fold activity A_fold = 0.65,
so the declared marker A = 0.325 is A_fold/2 and 25.38 is Appendix F's own
"Lambda exact at A_fold/2" entry, obtained by simulation at M = 2e4.

Two measurement defects in the Stage 2 case B tabulation are corrected here, both
numerical rather than scientific:
  (1) Lambda was accumulated with np.cumsum(A)*dt -- a right-rectangle rule on a
      dt = 0.1 grid -- which over a falling A(t) from 1.0 to 0.325 biases Lambda
      high by roughly lambda*(dt/2)*(A_0 - A_t*) ~ 0.084.  The trapezoidal rule is
      used here and the difference is reported.
  (2) The sampling grid is refined from dt = 0.1 to dt = 0.02 and the residual
      grid dependence measured.
An N ladder supplies A6's error source 2 (finite-N bias against the mean-field
prediction), which the kinetic reference makes meaningful for the first time.
"""
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(HERE), "stage2")
sys.path.insert(0, HERE)
sys.path.insert(0, S2)

from crowd1 import engine as E                                         # noqa: E402
from crowd1.a6 import (make_verdict, t_interval, decide, Verdict,      # noqa: E402
                       replicates_to_resolve, finite_N_bias_from_ladder)
from crowd1.rng import derive_run_seed                                 # noqa: E402
from crowd1.runner import RunConfig, run_one                           # noqa: E402
import config.stage2_config as CFG                                     # noqa: E402

LEVEL = 0.325                 # declared trajectory marker (ruling 3)
KIN_LAMBDA = 25.42849         # kinetic reference, Stage 2B task 3
KIN_LAMBDA_UNC = 0.01344
KIN_TSTAR = 12.90539
DELTA_FRAC = 0.05             # A6 trajectory marker
OUT = os.path.join(HERE, "outputs", "raw")


def _down_cross(t, A, lev):
    for i in range(1, len(A)):
        if A[i - 1] > lev >= A[i]:
            a0, a1 = A[i - 1], A[i]
            return float(t[i - 1] + (a0 - lev) / (a0 - a1) * (t[i] - t[i - 1]))
    return float("nan")


def _lambda_at(t, A, lam, tc):
    """Trapezoidal lambda*int_0^tc A ds, with the final partial interval handled."""
    if math.isnan(tc):
        return float("nan")
    k = int(np.searchsorted(t, tc))
    val = float(np.trapezoid(A[:k], t[:k])) if k > 1 else 0.0
    if k >= 1 and t[k - 1] < tc:
        a_end = float(np.interp(tc, t, A))
        val += 0.5 * (A[k - 1] + a_end) * (tc - t[k - 1])
    return lam * val


def worker(args):
    N, rep, dt = args
    c = CFG.P6["fixed"]["B"]
    t_end = CFG.P6["declared"]["t_end_B"]
    grid = np.arange(0.0, t_end + 1e-9, dt)
    seed = derive_run_seed(CFG.MASTER_SEED, 6, ord("B"), rep, N)
    cfg = RunConfig(N=N, eps=c["eps"], c_b=c["c_b"], c_h=c["c_h"],
                    alpha=c["alpha"], beta=c["beta"], r=c["r"], lam=c["lam"],
                    rho=c["rho"], kappa=c["kappa"], f=c["f"],
                    pulses=((0.0, 0),), initial_law="I1", t_end=t_end,
                    stop_on_extinction=True, sample_times=tuple(grid))
    o = run_one(cfg, seed)
    A = np.where(o["sampleA"] >= 0, o["sampleA"], 0).astype(float) / N
    tc = _down_cross(grid, A, LEVEL)
    return dict(N=N, rep=rep, dt=dt, seed=int(seed), t_star=tc,
                Lambda_trap=_lambda_at(grid, A, c["lam"], tc),
                Lambda_rect=float(np.cumsum(A)[min(int(np.searchsorted(grid, tc)),
                                                   len(A) - 1)] * dt * c["lam"])
                if not math.isnan(tc) else float("nan"),
                lam_intA_total=float(o["agg"][E.A_INTA] / N) * c["lam"],
                A_trace=A, grid_dt=dt)


def run_cell(N, nrep, dt, pool):
    res = pool.map(worker, [(N, rep, dt) for rep in range(nrep)])
    tr = np.array([r["A_trace"] for r in res])
    grid = np.arange(0.0, CFG.P6["declared"]["t_end_B"] + 1e-9, dt)
    lam = CFG.P6["fixed"]["B"]["lam"]
    Am = tr.mean(axis=0)
    tc_mt = _down_cross(grid, Am, LEVEL)
    ts = np.array([r["t_star"] for r in res])
    Ls = np.array([r["Lambda_trap"] for r in res])
    Lr = np.array([r["Lambda_rect"] for r in res])
    return dict(
        N=N, replicates=nrep, dt=dt,
        t_star_mean_of_crossings=float(ts.mean()), t_star_sd=float(ts.std(ddof=1)),
        Lambda_mean_of_crossings=float(Ls.mean()), Lambda_sd=float(Ls.std(ddof=1)),
        Lambda_rect_mean_of_crossings=float(Lr.mean()),
        t_star_mean_trajectory=tc_mt,
        Lambda_mean_trajectory=_lambda_at(grid, Am, lam, tc_mt),
        lam_intA_total_mean=float(np.mean([r["lam_intA_total"] for r in res])),
        seeds=[r["seed"] for r in res]), Ls, Lr, tr, grid


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    nrep = CFG.P6["fixed"]["replicates"]
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    res = {"level": LEVEL, "kinetic_Lambda": KIN_LAMBDA,
           "kinetic_Lambda_unc": KIN_LAMBDA_UNC, "kinetic_t_star": KIN_TSTAR,
           "delta_frac": DELTA_FRAC, "replicates": nrep}
    try:
        ladder = []
        for N in [25000, 50000, 100000, 200000]:
            cell, _, _, _, _ = run_cell(N, nrep, 0.02, pool)
            ladder.append(cell)
            print(f"  N={N:<7} t*={cell['t_star_mean_of_crossings']:.5f} "
                  f"Lambda*={cell['Lambda_mean_of_crossings']:.5f} "
                  f"(rect {cell['Lambda_rect_mean_of_crossings']:.5f})", flush=True)
        res["N_ladder"] = ladder
        # grid-refinement at the registered N
        grids = []
        for dt in [0.1, 0.05, 0.02, 0.01]:
            cell, _, _, _, _ = run_cell(100000, nrep, dt, pool)
            grids.append(cell)
            print(f"  dt={dt:<6} Lambda*_trap={cell['Lambda_mean_of_crossings']:.5f} "
                  f"Lambda*_rect={cell['Lambda_rect_mean_of_crossings']:.5f}",
                  flush=True)
        res["grid_refinement"] = grids
        main, Ls, Lr, traces, fgrid = run_cell(100000, nrep, 0.01, pool)
    finally:
        pool.close()
        pool.join()

    res["primary"] = main
    # A6 error source 2: finite-N bias from the ladder (top gap + 1/N Richardson)
    bias = finite_N_bias_from_ladder(
        [(c["N"], c["Lambda_mean_of_crossings"]) for c in ladder])
    res["finite_N_bias"] = bias
    bias_scalar = float(bias.get("residual_bias_at_Nmax", bias.get("top_gap", 0.0)))
    # A6 error source 3 on the MEASUREMENT side: residual sampling-grid dependence
    grid_err = abs(grids[-1]["Lambda_mean_of_crossings"]
                   - grids[-2]["Lambda_mean_of_crossings"])
    res["measurement_grid_error"] = grid_err
    res["quadrature_rule_offset_at_dt_0.1"] = (
        grids[0]["Lambda_rect_mean_of_crossings"]
        - grids[0]["Lambda_mean_of_crossings"])

    # ---- A6 verdict, both crossing estimands, delta = 5% of the kinetic reference
    delta = DELTA_FRAC * KIN_LAMBDA
    verdicts = []
    note = ("declared trajectory marker A = 0.325 (ruling 3); reference is the "
            "Stage 2B counter-resolved kinetic solution; Appendix F's 25.38 is not "
            "compared (unverified) and 20.35 is the bridge-fold hazard, a different "
            "object")
    v = make_verdict(
        name=f"P6 case B Lambda* at A = {LEVEL} (mean of replicate crossings)",
        predicted=KIN_LAMBDA, per_replicate_values=Ls, delta=delta,
        delta_basis=f"A6 trajectory marker: 5% of {KIN_LAMBDA}", N=100000,
        numerical_error=KIN_LAMBDA_UNC + grid_err,
        finite_N_bias=bias_scalar, closure_error=None, note=note)
    verdicts.append(v.__dict__ if hasattr(v, "__dict__") else dict(v))
    # The mean-trajectory functional is ONE number per cell, not a replicate mean,
    # so a Student-t interval across replicates does not apply to it.  Its sampling
    # uncertainty is obtained by resampling the 50 traces with replacement,
    # rebuilding the mean trajectory and recomputing the crossing (B = 2000).
    lamB = CFG.P6["fixed"]["B"]["lam"]
    rng = np.random.default_rng(CFG.MASTER_SEED)
    nrep_ = traces.shape[0]
    boot = np.empty(2000)
    for b in range(2000):
        idx = rng.integers(0, nrep_, nrep_)
        Ab = traces[idx].mean(axis=0)
        boot[b] = _lambda_at(fgrid, Ab, lamB, _down_cross(fgrid, Ab, LEVEL))
    blo, bhi = np.percentile(boot, [2.5, 97.5])
    mt = main["Lambda_mean_trajectory"]
    dlo, dhi = blo - KIN_LAMBDA, bhi - KIN_LAMBDA
    st = decide(dlo, dhi, delta)
    hw = 0.5 * (bhi - blo)
    v2 = Verdict(
        name=f"P6 case B Lambda* at A = {LEVEL} (crossing of the mean trajectory)",
        predicted=KIN_LAMBDA, measured=float(mt), diff=float(mt - KIN_LAMBDA),
        ci_lo=float(dlo), ci_hi=float(dhi), delta=float(delta),
        delta_basis=f"A6 trajectory marker: 5% of {KIN_LAMBDA}", status=st,
        n_replicates=nrep_, N=100000,
        replicates_needed=(replicates_to_resolve(mt - KIN_LAMBDA, hw, delta, nrep_)
                           if st == "INCONCLUSIVE" else None),
        mc_error=float(hw), finite_N_bias=bias_scalar,
        numerical_error=float(KIN_LAMBDA_UNC + grid_err), closure_error=None,
        interval_kind="bootstrap percentile over replicate traces, B = 2000",
        note=note)
    verdicts.append(v2.__dict__ if hasattr(v2, "__dict__") else dict(v2))
    res["bootstrap_mean_trajectory"] = dict(lo=float(blo), hi=float(bhi),
                                            B=2000)
    res["verdicts"] = verdicts
    with open(os.path.join(OUT, "p6b_verdict.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("done", flush=True)
