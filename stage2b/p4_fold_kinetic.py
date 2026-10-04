"""Class-2 fold from the INDEPENDENT kinetic solver (alpha = 0.5, c_b = 0.3, r = 1).

The fold is the saddle-node of the stationary branch map.  At prescribed constant
rate nu the long-time activity of the kinetic equation IS the stationary response
P_nu, and the self-consistency lambda = nu / P_nu then gives

    lambda_fold = min_nu  nu / P_nu,     nu_f = argmin,     A_fold = P_{nu_f}

so the fold is a one-dimensional minimisation over nu with every P_nu supplied by
the measure solver -- no quadrature of C2(b), no agent simulation.

P_nu converges from BELOW at first order in h, so lambda = nu/P_nu converges from
ABOVE; the h-ladder is Richardson-extrapolated and the reported numerical error is
the last extrapolation increment, measured rather than assumed.
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinetic as KIN

ALPHA, C_B, EPS, R = 0.5, 0.3, 1.0, 1.0
T_STAT, C_MIN, KTRUNC = 60.0, 1e-3, 3


def P_nu(nu, h):
    """Stationary P(c > c_b) at prescribed rate nu, from the measure solver."""
    t, A, d = KIN.solve(lam=0.0, alpha=ALPHA, r=R, c_b=C_B, f=0.0, T=T_STAT, h=h,
                        c_min=C_MIN, K=KTRUNC, eps=EPS, nu_prescribed=nu)
    return float(A[-1]), d


def lam_of_nu(nu, h):
    p, _ = P_nu(nu, h)
    return nu / p if p > 0 else np.inf


if __name__ == "__main__":
    out = dict(alpha=ALPHA, c_b=C_B, eps=EPS, r=R, T_stat=T_STAT, c_min=C_MIN,
               K=KTRUNC, manuscript=dict(lam_fold=1.48251, nu_f=0.556791,
                                         A_fold=0.375574))
    # horizon check: the stationary response must not depend on T
    hz = []
    for T in (30.0, 60.0, 120.0):
        KIN_T = T
        t, A, d = KIN.solve(lam=0.0, alpha=ALPHA, r=R, c_b=C_B, f=0.0, T=T,
                            h=0.002, c_min=C_MIN, K=KTRUNC, eps=EPS,
                            nu_prescribed=0.5568)
        hz.append(dict(T=T, P_nu=float(A[-1])))
        print(f"  horizon T={T:<6} P_nu(0.5568) = {A[-1]:.10f}", flush=True)
    out["horizon_check"] = hz
    rows = []
    for h in (0.008, 0.004, 0.002, 0.001):
        res = minimize_scalar(lam_of_nu, bracket=(0.45, 0.556, 0.70), args=(h,),
                              method="brent", options=dict(xtol=1e-9))
        nu_f = float(res.x)
        lam_f = float(res.fun)
        p, d = P_nu(nu_f, h)
        rows.append(dict(h=d["h"], nu_f=nu_f, lam_fold=lam_f, A_fold=p,
                         n_evals=int(res.nfev), J=d["J"],
                         mass_deficit=1.0 - d["mass"]))
        print(f"  h={h:<6} lambda_fold={lam_f:.9f}  nu_f={nu_f:.9f}  "
              f"A_fold={p:.9f}  ({res.nfev} evals)", flush=True)
    out["h_ladder"] = rows

    def rich(key):
        v = [r[key] for r in rows]
        d1, d2 = v[-2] - v[-3], v[-1] - v[-2]
        order = (float(math.log2(abs(d1 / d2))) if d2 != 0 and d1 / d2 > 0 else None)
        return dict(finest=v[-1], richardson=v[-1] + (v[-1] - v[-2]),
                    numerical_error=abs(v[-1] - v[-2]), observed_order_in_h=order)

    for k in ("lam_fold", "nu_f", "A_fold"):
        out[k] = rich(k)
        m = out["manuscript"][k]
        print(f"\n{k}: Richardson {out[k]['richardson']:.9f} "
              f"+- {out[k]['numerical_error']:.2e}  (order "
              f"{out[k]['observed_order_in_h']})  manuscript {m}  "
              f"deviation {out[k]['richardson'] - m:+.2e}", flush=True)
    # internal consistency: A_fold must equal nu_f / lambda_fold
    out["consistency_A_fold_vs_nu_over_lam"] = (
        out["A_fold"]["richardson"]
        - out["nu_f"]["richardson"] / out["lam_fold"]["richardson"])
    print(f"\nconsistency A_fold - nu_f/lambda_fold = "
          f"{out['consistency_A_fold_vs_nu_over_lam']:+.2e}")
    json.dump(out, open(os.path.join(HERE, "outputs", "raw",
                                     "p4_fold_kinetic.json"), "w"), indent=2)
    print("done", flush=True)
