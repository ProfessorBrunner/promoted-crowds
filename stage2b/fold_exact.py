"""Exact class-2 fold at alpha = 0.5, c_b = 0.3, eps = 1, r = 1.

This supersedes the measure-solver fold of p4_fold_kinetic.py, which carried an
h-independent bias from its conviction floor (see BUGLOG S2B-4).

At r = 1 with constant input nu and positive dose d = alpha, Appendix C C2.11-C2.14
give the stationary conviction density in closed method-of-steps form.  Because
d = 0.5 there are exactly TWO steps on (0, 1):

    0 < c < d :   f(c) = C c^{a-1}                       a = nu / eps
    d < c < 1 :   f(c) = C c^{a-1} [ 1 - a J(c) ],        J(c) = int_d^c u^{-a} (u-d)^{a-1} du

so P_nu = int_{c_b}^1 f is a two-dimensional quadrature with one integrable
endpoint singularity, and both singular factors are removed EXACTLY by
substitution before any numerical rule is applied:

    (u - d)^{a-1} du  ->  (c-d)^a / a * ds        with u = d + (c-d) s^{1/a}
    t^a dt            ->  1/(a+1) dy              with t = y^{1/(a+1)}

What is left is smooth, so Gauss-Legendre converges to machine precision and the
node ladder below is a convergence certificate, not an error estimate.

The fold is   lam_fold = min_nu nu / P_nu ,   nu_f = argmin ,   A_fold = P_{nu_f}.
"""
import json
import math
import os

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA, C_B, EPS, R = 0.5, 0.3, 1.0, 1.0
MANUSCRIPT = dict(lam_fold=1.48251, nu_f=0.556791, A_fold=0.375574)


def P_nu_exact(nu, d=ALPHA, c_b=C_B, eps=EPS, n=400):
    """Stationary P(c > c_b) from C2.11-C2.14.  Exact up to Gauss-Legendre error."""
    a = nu / eps
    x, w = leggauss(n)
    x = 0.5 * (x + 1.0)
    w = 0.5 * w

    def Q(c):                                  # J(c) = (c-d)^a / a * Q(c)
        u = d + (c - d) * x ** (1.0 / a)
        return float(np.sum(w * u ** (-a)))

    t = x ** (1.0 / (a + 1.0))                 # removes the t^a factor exactly
    c = d + (1.0 - d) * t
    vals = c ** (a - 1.0) * np.array([Q(ci) for ci in c])
    I2 = (1.0 - d ** a) / a - (1.0 - d) ** (a + 1.0) / (a + 1.0) * float(np.sum(w * vals))
    I1 = d ** a / a
    head = (d ** a - c_b ** a) / a if c_b < d else 0.0
    return (head + I2) / (I1 + I2)


def fold(n=400):
    r = minimize_scalar(lambda v: v / P_nu_exact(v, n=n),
                        bracket=(0.4, 0.55, 0.75), method="brent",
                        options=dict(xtol=1e-12))
    nu_f = float(r.x)
    return dict(nu_f=nu_f, lam_fold=float(r.fun), A_fold=P_nu_exact(nu_f, n=n), nodes=n)


if __name__ == "__main__":
    out = dict(alpha=ALPHA, c_b=C_B, eps=EPS, r=R, manuscript=MANUSCRIPT)

    # check 1 - the C2.16 small-nu expansion, an independent series for the same law
    ell = math.log(ALPHA / C_B)
    ser = []
    for nu in (1e-5, 1e-4, 1e-3):
        ex = P_nu_exact(nu)
        s = nu * ell + nu ** 2 * (math.pi ** 2 / 12.0 - ell ** 2 / 2.0)
        ser.append(dict(nu=nu, quadrature=ex, series_C2_16=s, rel=(ex - s) / ex))
        print(f"  nu={nu:.0e}  quadrature {ex:.10e}  C2.16 series {s:.10e}  "
              f"rel {(ex - s) / ex:+.1e}", flush=True)
    out["check_small_nu_series"] = ser

    # check 2 - Gauss-Legendre node ladder on the fold itself
    lad = []
    for n in (100, 200, 400, 800, 1600):
        f = fold(n)
        lad.append(f)
        print(f"  nodes={n:<5} nu_f={f['nu_f']:.9f}  lam_fold={f['lam_fold']:.9f}  "
              f"A_fold={f['A_fold']:.9f}", flush=True)
    out["node_ladder"] = lad

    fin = lad[-1]
    prev = lad[-2]
    out["fold"] = dict(
        nu_f=fin["nu_f"], lam_fold=fin["lam_fold"], A_fold=fin["A_fold"],
        numerical_error=dict(
            nu_f=abs(fin["nu_f"] - prev["nu_f"]),
            lam_fold=abs(fin["lam_fold"] - prev["lam_fold"]),
            A_fold=abs(fin["A_fold"] - prev["A_fold"])),
        identity_A_minus_nu_over_lam=fin["A_fold"] - fin["nu_f"] / fin["lam_fold"])
    for k in ("lam_fold", "nu_f", "A_fold"):
        dev = out["fold"][k] - MANUSCRIPT[k]
        out["fold"].setdefault("deviation_from_manuscript", {})[k] = dev
        print(f"{k}: exact {out['fold'][k]:.9f}  manuscript {MANUSCRIPT[k]}  "
              f"deviation {dev:+.2e}", flush=True)
    print("identity A_fold - nu_f/lam_fold = "
          f"{out['fold']['identity_A_minus_nu_over_lam']:+.2e}", flush=True)

    os.makedirs(os.path.join(HERE, "outputs", "raw"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "outputs", "raw", "fold_exact.json"), "w"),
              indent=2)
