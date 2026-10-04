"""Append an h = 0.0005 rung to the class-2 fold ladder and re-extrapolate.

A_fold's Richardson increment at h = 0.001 (3.8e-5) left the manuscript value
2.4 increments away, so the ladder is extended one halving to settle whether that is
a real deviation or just the extrapolation error.  Nothing else changes.
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from p4_fold_kinetic import lam_of_nu, P_nu

FP = os.path.join(HERE, "outputs", "raw", "p4_fold_kinetic.json")
out = json.load(open(FP))
h = 0.0005
res = minimize_scalar(lam_of_nu, bracket=(0.50, 0.557, 0.62), args=(h,),
                      method="brent", options=dict(xtol=1e-9))
nu_f, lam_f = float(res.x), float(res.fun)
p, d = P_nu(nu_f, h)
out["h_ladder"].append(dict(h=d["h"], nu_f=nu_f, lam_fold=lam_f, A_fold=p,
                            n_evals=int(res.nfev), J=d["J"],
                            mass_deficit=1.0 - d["mass"]))
rows = out["h_ladder"]
print(f"  h={h} lambda_fold={lam_f:.9f}  nu_f={nu_f:.9f}  A_fold={p:.9f}  "
      f"({res.nfev} evals)")
for k in ("lam_fold", "nu_f", "A_fold"):
    v = [r[k] for r in rows]
    d1, d2 = v[-2] - v[-3], v[-1] - v[-2]
    order = float(math.log2(abs(d1 / d2))) if d2 != 0 and d1 / d2 > 0 else None
    out[k] = dict(finest=v[-1], richardson=v[-1] + (v[-1] - v[-2]),
                  numerical_error=abs(v[-1] - v[-2]), observed_order_in_h=order)
    m = out["manuscript"][k]
    dev = out[k]["richardson"] - m
    print(f"{k}: Richardson {out[k]['richardson']:.9f} +- "
          f"{out[k]['numerical_error']:.2e} (order {order:.4f})  manuscript {m}  "
          f"deviation {dev:+.2e} = {abs(dev)/out[k]['numerical_error']:.2f} x the "
          f"numerical error")
out["consistency_A_fold_vs_nu_over_lam"] = (
    out["A_fold"]["richardson"]
    - out["nu_f"]["richardson"] / out["lam_fold"]["richardson"])
json.dump(out, open(FP, "w"), indent=2)
print("consistency A_fold - nu_f/lam_fold = %+.2e"
      % out["consistency_A_fold_vs_nu_over_lam"])
