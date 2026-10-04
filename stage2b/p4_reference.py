"""Stage 2B task 2: the independent kinetic reference for P4's critical fraction.

f_c^MF(lambda) = inf{ f : the mean-field trajectory started from
                        mu_0 = (1-f) delta_0 + f delta_alpha ignites }

"Ignites" is decided by classifying the FULL trajectory, not by a time-t criterion:
the mean-field flow has exactly two attractors, A = 0 and the upper branch A*(lambda)
of lambda(nu) = nu / P_nu, so A(T) for large T is either numerically zero or within
the discretisation error of A*.  Runs whose terminal activity is neither are reported
as unclassified rather than forced into a basin; none occurred.

Refinement: the grid h is halved three times and the horizon T is doubled, and the
reported uncertainty is taken from the spread of the bisected boundary across those
refinements, not assumed.
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
from crowd1 import predictions_s2 as PS                                # noqa: E402

ALPHA, R, C_B = 0.5, 1.0, 0.3        # P4, design A4 / C2(b): inert counters at r = 1
OUT = os.path.join(HERE, "outputs", "raw")


def classify(lam, f, h, T, c_min=1e-3):
    """Which basin the trajectory is in at the horizon.

    The mean-field flow has exactly two attractors, A = 0 and the upper branch
    A*(lambda), separated by the unstable middle branch, whose activity at the
    saddle-node is A_fold.  So a trajectory is in the extinction basin as soon as
    it is BELOW the fold activity and still decreasing -- there is no attractor
    between the two -- and in the ignition basin once it is within half of A*.
    Anything else is reported as unclassified rather than forced into a basin.
    """
    t, A, d = KIN.solve(lam=lam, alpha=ALPHA, r=R, c_b=C_B, f=f, T=T, h=h,
                        c_min=c_min, K=3)
    A_star = PS.p4_branches(lam)["A_star"]
    A_fold = PS.p4_fold()["A_fold"]
    end, peak = float(A[-1]), float(A.max())
    decreasing = A[-1] <= A[-2]
    if end > 0.5 * A_star:
        lab = "ignite"
    elif end < 0.5 * A_fold and decreasing:
        lab = "die"
    else:
        lab = "unclassified"
    return lab, end, peak, d


def bisect_fc(lam, h, T, lo, hi, tol=1e-6, log=None):
    """Bisect the basin boundary; `lo` must die and `hi` must ignite."""
    l_lo, *_ = classify(lam, lo, h, T)
    l_hi, *_ = classify(lam, hi, h, T)
    assert l_lo == "die", f"bracket low end {lo} classified {l_lo}"
    assert l_hi == "ignite", f"bracket high end {hi} classified {l_hi}"
    n = 0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lab, end, peak, d = classify(lam, mid, h, T)
        if lab == "unclassified":
            raise RuntimeError(f"unclassified trajectory at lam={lam} f={mid}: "
                               f"A(T)={end}")
        if lab == "ignite":
            hi = mid
        else:
            lo = mid
        n += 1
        if log is not None:
            log.append(dict(f=mid, label=lab, A_end=end, A_peak=peak))
    return 0.5 * (lo + hi), 0.5 * (hi - lo), n


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    CASES = [(1.60, 0.10, 0.20), (1.75, 0.02, 0.10), (1.90, 0.002, 0.03)]
    res = {}
    for lam, lo0, hi0 in CASES:
        rows = []
        lo, hi = lo0, hi0
        for h in [0.008, 0.004, 0.002, 0.001]:
            fc, half, n = bisect_fc(lam, h, 120.0, lo, hi)
            rows.append(dict(h=h, T=120.0, f_c=fc, bisection_half_width=half,
                             n_evals=n, bracket=[lo, hi]))
            print(f"  lam={lam}  h={h:<6} T=120  f_c^MF={fc:.8f} "
                  f"(+-{half:.1e}, {n} evals)", flush=True)
            # the boundary moves monotonically down with h; re-bracket generously
            lo, hi = max(0.0, fc - 0.02 * max(fc, 1e-3) - 0.004), fc + 1e-4
        hor = []
        for T in [120.0, 240.0]:
            fc, half, n = bisect_fc(lam, 0.004, T, lo0, hi0)
            hor.append(dict(h=0.004, T=T, f_c=fc, bisection_half_width=half))
            print(f"  lam={lam}  h=0.004  T={T:<6} f_c^MF={fc:.8f}", flush=True)
        d1 = rows[-2]["f_c"] - rows[-3]["f_c"]
        d2 = rows[-1]["f_c"] - rows[-2]["f_c"]
        order = float(math.log2(abs(d1 / d2))) if d2 != 0 and d1 / d2 > 0 else None
        rich = rows[-1]["f_c"] + (rows[-1]["f_c"] - rows[-2]["f_c"])
        res[f"{lam}"] = dict(
            lam=lam, h_refinement=rows, horizon_refinement=hor,
            observed_order_in_h=order, f_c_richardson=rich,
            f_c_finest=rows[-1]["f_c"],
            unc_grid=abs(rows[-1]["f_c"] - rows[-2]["f_c"]),
            unc_horizon=max(abs(x["f_c"] - hor[0]["f_c"]) for x in hor),
            A_star=PS.p4_branches(lam)["A_star"])
        print(f"  lam={lam}: order={order}, Richardson f_c^MF={rich:.8f}\n",
              flush=True)
    with open(os.path.join(OUT, "p4_reference.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("done", flush=True)
