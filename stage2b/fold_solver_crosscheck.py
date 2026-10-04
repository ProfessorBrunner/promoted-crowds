"""Cross-checks behind BUGLOG S2B-4 and REPORT_class2_fold.md sections 2 and 5.

fold_exact.py computes the fold from the exact C2.11-C2.14 law and supersedes the
measure-solver route.  This script supplies the two SEPARATE claims that the report
makes about the superseded route, so that both are reproducible from the archive
rather than only from the session transcript:

  check A (report section 2, second bullet) -- the measure solver is CORRECT; only its
    floor setting was not.  At fixed nu = nu_f, with the conviction floor lowered to
    c_min = 1e-5, the solver's P_nu over an h-ladder converges first order to the
    exact value.

  check B (report section 5) -- the floor is what biased the fold.  Re-running the
    minimization at a single grid h = 0.002 with c_min = 1e-3 (as in the superseded
    run) and then c_min = 1e-5 moves nu_f and lam_fold by the size of the residual
    that the superseded extrapolation carried.

  check C -- the truncation order K is exonerated: P_nu is unchanged across K at
    every floor tested, so K = 3 is adequate and is not implicated.

Runtime is a few minutes; this is a diagnostic, not a certified reference.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinetic as KIN                                    # noqa: E402
from fold_exact import ALPHA, C_B, EPS, P_nu_exact, fold  # noqa: E402

T_STAT = 60.0


def P_nu_solver(nu, h, c_min, K=3):
    t, A, d = KIN.solve(lam=0.0, alpha=ALPHA, r=1.0, c_b=C_B, f=0.0, T=T_STAT, h=h,
                        c_min=c_min, K=K, eps=EPS, nu_prescribed=float(nu))
    return float(A[-1]), d


def fold_solver(h, c_min, K=3):
    r = minimize_scalar(lambda v: float(v) / P_nu_solver(v, h, c_min, K)[0],
                        bracket=(0.45, 0.56, 0.70), method="brent",
                        options=dict(xtol=1e-9))
    return float(r.x), float(r.fun)


if __name__ == "__main__":
    exact = fold()
    nu_star, A_star = exact["nu_f"], exact["A_fold"]
    out = dict(exact=exact, T_stat=T_STAT)
    print(f"exact nu_f = {nu_star:.9f}   exact A_fold = P_nu(nu_f) = {A_star:.12f}\n",
          flush=True)

    print("check A - solver P_nu at fixed nu = nu_f, floor lowered to c_min = 1e-5")
    rows = []
    for h in (0.008, 0.004, 0.002, 0.001, 0.0005):
        P, d = P_nu_solver(nu_star, h, 1e-5)
        rows.append(dict(h=d["h"], P_nu=P, error_vs_exact=P - A_star, J=d["J"],
                         mass_at_zero=d["mass_at_zero"]))
        print(f"  h={d['h']:.6f}  P_nu = {P:.9f}   error vs exact = {P - A_star:+.3e}",
              flush=True)
    v = [r["P_nu"] for r in rows]
    diffs = [v[i + 1] - v[i] for i in range(len(v) - 1)]
    ratios = [diffs[i] / diffs[i + 1] for i in range(len(diffs) - 1)]
    rich = v[-1] + (v[-1] - v[-2])
    print("  first differences: " + ", ".join(f"{d:+.3e}" for d in diffs))
    print("  ratios: " + ", ".join(f"{r:.3f}" for r in ratios))
    print(f"  Richardson (order 1) = {rich:.9f}   error vs exact = {rich - A_star:+.3e}",
          flush=True)
    out["check_A_floor_lowered_h_ladder"] = dict(
        c_min=1e-5, nu=nu_star, rows=rows, first_differences=diffs, ratios=ratios,
        richardson=rich, richardson_error_vs_exact=rich - A_star)

    print("\ncheck B - fold at a single grid h = 0.002, floor 1e-3 vs 1e-5")
    rows = []
    for c_min in (1e-3, 1e-5):
        nu_h, lam_h = fold_solver(0.002, c_min)
        rows.append(dict(c_min=c_min, h=0.002, nu_f=nu_h, lam_fold=lam_h,
                         A_fold=nu_h / lam_h))
        print(f"  c_min={c_min:.0e}  nu_f = {nu_h:.9f}  lam_fold = {lam_h:.9f}  "
              f"A_fold = {nu_h / lam_h:.9f}", flush=True)
    shift = {k: rows[1][k] - rows[0][k] for k in ("nu_f", "lam_fold", "A_fold")}
    print("  shift from lowering the floor: " +
          ", ".join(f"{k} {s:+.3e}" for k, s in shift.items()))
    sup = json.load(open(os.path.join(HERE, "outputs", "raw",
                                      "p4_fold_kinetic.json")))
    resid = {k: sup[k]["richardson"] - exact[k] for k in ("nu_f", "lam_fold", "A_fold")}
    print("  superseded extrapolation minus exact: " +
          ", ".join(f"{k} {r:+.3e}" for k, r in resid.items()), flush=True)
    out["check_B_floor_sensitivity"] = dict(
        rows=rows, shift_from_lowering_floor=shift,
        superseded_extrapolation_minus_exact=resid)

    print("\ncheck C - truncation order K at fixed nu, h = 0.001")
    rows = []
    for c_min in (1e-3, 1e-5):
        for K in (3, 6, 10):
            P, d = P_nu_solver(nu_star, 0.001, c_min, K)
            rows.append(dict(c_min=c_min, K=K, P_nu=P))
            print(f"  c_min={c_min:.0e} K={K:<3} P_nu = {P:.9f}", flush=True)
    spread = {f"{c:.0e}": max(r["P_nu"] for r in rows if r["c_min"] == c)
                          - min(r["P_nu"] for r in rows if r["c_min"] == c)
              for c in (1e-3, 1e-5)}
    print("  spread over K at fixed floor: " +
          ", ".join(f"c_min={k} -> {s:.1e}" for k, s in spread.items()), flush=True)
    out["check_C_truncation_order"] = dict(rows=rows, spread_over_K=spread)

    os.makedirs(os.path.join(HERE, "outputs", "raw"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "outputs", "raw",
                                     "fold_solver_crosscheck.json"), "w"), indent=2)
    print("\nwrote outputs/raw/fold_solver_crosscheck.json")
