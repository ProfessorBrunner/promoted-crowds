"""Stage 2B task 1: the P1-delay estimator audit and its time-dependent replacement.

Two distinct quantities, measured on the same saved post-campaign states and
reported under their own names.

(1) FROZEN-BACKGROUND PROXY -- what Stage 2 reported as the "invasion advantage".
    A single target-aligned seed is injected into a saved post-campaign state whose
    recipients are held fixed (both orientation and conviction) for the whole of the
    seed's life; Z1 counts first-generation activations only.  This is a
    frozen-background operator; it coincides with the stationary invasion operator
    only as tau0 -> infinity, and at tau0 = 0 its between-order ratio is exactly 1
    because E[cos^2 phi_post] = 1/2 for BOTH campaign orders (from I2 the maximally
    mixed orientation law is invariant under every projection, R8(b)), so the frozen
    orientation channel carries no order information at all.

(2) TIME-DEPENDENT FIRST-GENERATION COUNT E Z1 -- the owner's estimand.
    The same seed, but the background RELAXES during the seed's life: recipient
    convictions decay at rate eps and recipient orientations reset to T_s at rate
    rho.  Reference at tau0 = 0: E Z1 = (lambda/2)[L + x_j(L - 1/2)], ratio 1.270.

The relaxation is sampled exactly rather than simulated.  With kappa = 0 a reset is
the only event that moves a silent agent's orientation, it sends phi to T_s, and it
changes neither c nor s.  So at absolute time u after the save the orientation is
T_s with probability 1 - exp(-rho u) and the saved orientation otherwise,
independently across agents; memorylessness lets that coin be flipped at the moment
of receipt and re-flipped from the previous decision time on a later hit.  This is
implemented as `relax_rho` in crowd1/operator.py, whose default 0.0 reproduces the
Stage 2 numbers bit for bit (verified against outputs/raw/p1_operator.csv).
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

from dataclasses import replace                                        # noqa: E402

from crowd1.operator import run_frozen_operator                        # noqa: E402
from crowd1.rng import derive_run_seed                                 # noqa: E402
from crowd1.tests_s2 import p1_base_cfg, prepare_states, state_x       # noqa: E402
import config.stage2_config as CFG                                     # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")


# ------------------------------------------------------------------- references
def q_T(tau0, x, rho=1.0, Q0=0.5):
    """Acceptance probability of a target-aligned message at background age tau0."""
    e = math.exp(-rho * tau0)
    return e * Q0 + (1.0 - e) * 0.5 * (1.0 + x)


def EZ1_over_lam(tau0, x, L=math.log(2.0), rho=1.0, eps=1.0):
    """E Z1 / lambda = int_0^L q_T(tau0 + s) ds, the seed's lifetime being L."""
    e = math.exp(-rho * tau0)
    return 0.5 * (L + x * (L - e * (1.0 - math.exp(-rho * L)) / rho))


def frozen_proxy_over_lam(tau0, x, L=math.log(2.0), rho=1.0):
    """The Stage 2 proxy: the background is frozen at age tau0 for the whole life."""
    return L * q_T(tau0, x)


# ------------------------------------------------------------------ measurement
def assay_worker(args):
    """One background realisation, assayed at every delay under both kernels.

    The state preparation is seeded exactly as in Stage 2, so the frozen rows here
    reproduce outputs/raw/p1_operator.csv and the two kernels are compared on the
    very same post-campaign states.
    """
    order, N, rep, relax_rho = args
    fx, dc = CFG.P1["fixed"], CFG.P1["declared"]
    delays = CFG.P1_DELAY["fixed"]["tau0_over_rho"]
    lam = dc["operator_lambda"]
    seed = derive_run_seed(CFG.MASTER_SEED, 1, hash(order) % 10007, N, rep)
    base = p1_base_cfg(CFG, N, 0.0)
    states, _ = prepare_states(base, order, delays, seed)
    cfg_op = replace(base, lam=lam,
                     extra_registry_angles=tuple(int(a) for a in order))
    ntr = dc["operator_trials_per_background"]
    rows = []
    for tau in delays:
        st = states[tau]
        op_seed = derive_run_seed(seed, 31, int(tau * 10))
        fr = run_frozen_operator(st, cfg_op, op_seed, ntr,
                                 max_gen=1, seed_c=1.0,
                                 freeze=(relax_rho == 0.0),
                                 relax_rho=relax_rho)
        z = fr["Z1"]
        rows.append(dict(order=str(order), N=N, rep=rep, tau0=tau, lam=lam,
                         relax_rho=float(relax_rho), x=state_x(st),
                         Z1_mean=float(z.mean()),
                         Z1_sd=float(z.std(ddof=1)), n_trials=int(ntr),
                         seed=int(op_seed), prep_seed=int(seed)))
    return rows


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fx, dc = CFG.P1["fixed"], CFG.P1["declared"]
    taus = list(CFG.P1_DELAY["fixed"]["tau0_over_rho"])
    lam = dc["operator_lambda"]
    res = dict(delays=list(taus), lam=lam, L=math.log(2.0), rho=fx["rho"],
               eps=fx["eps"])

    # exact references, for both quantities and both orders
    ref = {}
    for order in fx["orders"]:
        x = fx["x_pred"][tuple(order)]
        ref[str(tuple(order))] = dict(
            x=x,
            EZ1_over_lam=[EZ1_over_lam(t, x) for t in taus],
            frozen_over_lam=[frozen_proxy_over_lam(t, x) for t in taus])
    x2 = fx["x_pred"][tuple(fx["orders"][1])]
    L = math.log(2.0)
    res["reference"] = ref
    res["reference_ratio_time_dependent"] = [
        EZ1_over_lam(t, x2) / EZ1_over_lam(t, 0.0) for t in taus]
    res["reference_ratio_frozen_proxy"] = [
        frozen_proxy_over_lam(t, x2) / frozen_proxy_over_lam(t, 0.0) for t in taus]
    res["reference_ratio_at_zero_owner_formula"] = (
        0.5 * (L + x2 * (L - 0.5)) / (0.5 * L))

    import multiprocessing as mp
    jobs = [(tuple(o), fx["N"], rep, relax)
            for relax in [0.0, float(fx["rho"])]
            for o in fx["orders"]
            for rep in range(dc["operator_backgrounds"])]
    print(f"  {len(jobs)} background realisations x {len(taus)} delays",
          flush=True)
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    try:
        out = pool.map(assay_worker, jobs)
    finally:
        pool.close(); pool.join()
    rows = [r for chunk in out for r in chunk]
    res["rows"] = rows

    # per-(kernel, order, delay) summary across backgrounds, and the ratio
    import collections
    agg = collections.defaultdict(list)
    for r in rows:
        agg[(r["relax_rho"], r["order"], r["tau0"])].append(r["Z1_mean"])
    summ = []
    for (relax, order, tau), v in sorted(agg.items()):
        v = np.array(v)
        summ.append(dict(relax_rho=relax, order=order, tau0=tau,
                         n_backgrounds=len(v), Z1_over_lam=float(v.mean() / lam),
                         Z1_mean=float(v.mean()),
                         sem=float(v.std(ddof=1) / math.sqrt(len(v)))))
    res["summary"] = summ
    o1, o2 = str(tuple(fx["orders"][0])), str(tuple(fx["orders"][1]))
    ratios = []
    for relax in [0.0, float(fx["rho"])]:
        for tau in taus:
            a = np.array(agg[(relax, o1, tau)])
            b = np.array(agg[(relax, o2, tau)])
            # paired across the common background index (same seeds both orders)
            n = min(len(a), len(b))
            rr = b[:n] / a[:n]
            ratios.append(dict(relax_rho=relax, tau0=tau,
                               ratio=float(b[:n].mean() / a[:n].mean()),
                               ratio_paired_mean=float(rr.mean()),
                               ratio_sem=float(rr.std(ddof=1) / math.sqrt(n)),
                               n_backgrounds=n))
    res["measured_ratio"] = ratios
    with open(os.path.join(OUT, "p1delay_reference.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("done", flush=True)
