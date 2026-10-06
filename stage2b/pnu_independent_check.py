"""Independent checks of dose_mixture_fold.P_stat below d = 1/2.

(a) against the deterministic measure solver of manuscript D.3 (kinetic.solve at
    r = 1, f = 0, nu prescribed, dose = alpha), on an h ladder with the
    conviction floor lowered to c_min = 1e-5, at c_b = 0.5 and the case-A fold
    range of nu;
(b) against a direct single-agent Monte Carlo with exact event times.

Writes stage2b/outputs/raw/pnu_independent_check.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinetic as KIN                                             # noqa: E402
from dose_mixture_fold import P_stat                              # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")
os.makedirs(OUT, exist_ok=True)

C_B = 0.5
DOSES = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]
# lambda A along the case-A branch: 3 * 0.8172 at H = 0 down to 3 * 0.5647 at the fold
NUS = [1.70, 1.90, 2.10, 2.30, 2.45]
HS = [0.008, 0.004, 0.002, 0.001]
T_STAT = 60.0


def P_measure(nu, d, c_b, h, c_min=1e-5, K=3, T=T_STAT):
    t, A, dg = KIN.solve(lam=0.0, alpha=d, r=1.0, c_b=c_b, f=0.0, T=T, h=h,
                         c_min=c_min, K=K, eps=1.0, nu_prescribed=float(nu))
    return float(A[-1]), dg


def mc_P(nu, d, c_b, n_agents=1_000_000, T=40.0, eps=1.0, seed=0):
    """Exact event-driven single-agent Monte Carlo.  Clipping is nonexpansive, so
    starting every agent at c = 0 leaves a coupling error <= exp(-eps T)."""
    rng = np.random.default_rng(seed)
    c = np.zeros(n_agents)
    t = np.zeros(n_agents)
    idx = np.arange(n_agents)
    while idx.size:
        gap = rng.exponential(1.0 / nu, idx.size)
        tn = t[idx] + gap
        fin = tn > T
        f_i = idx[fin]
        c[f_i] *= np.exp(-eps * (T - t[f_i]))
        a_i = idx[~fin]
        c[a_i] = np.minimum(1.0, c[a_i] * np.exp(-eps * gap[~fin]) + d)
        t[a_i] = tn[~fin]
        idx = a_i
    k = int((c > c_b).sum())
    p = k / n_agents
    z = 1.959963984540054
    se = math.sqrt(p * (1 - p) / n_agents)
    return dict(nu=nu, d=d, n_agents=n_agents, burn_in_T=T, seed=seed,
                successes=k, p_hat=p, se=se, ci95_lo=p - z * se, ci95_hi=p + z * se,
                coupling_bias_bound=math.exp(-eps * T))


if __name__ == "__main__":
    out = dict(c_b=C_B, doses=DOSES, nus=NUS, h_ladder=HS, c_min=1e-5,
               T_stationary=T_STAT, solver="kinetic.solve r=1 f=0 nu_prescribed "
                                            "(manuscript D.3 measure solver)")
    rows = []
    for d in DOSES:
        for nu in NUS:
            q = P_stat(nu, d, C_B, M=32, N=256)
            vals = []
            for h in HS:
                P, dg = P_measure(nu, d, C_B, h)
                vals.append(dict(h=dg["h"], P=P, J=dg["J"]))
            v = [x["P"] for x in vals]
            rich = v[-1] + (v[-1] - v[-2])
            refine_err = abs(v[-1] - v[-2])
            d1, d2 = v[-2] - v[-3], v[-1] - v[-2]
            order = math.log2(abs(d1 / d2)) if d2 != 0 and d1 / d2 > 0 else None
            rows.append(dict(d=d, nu=nu, quadrature=q, solver_rows=vals,
                             solver_richardson=rich, refinement_error=refine_err,
                             observed_order=order,
                             diff_richardson_minus_quadrature=rich - q,
                             diff_finest_minus_quadrature=v[-1] - q))
            print(f"  d={d:.2f} nu={nu:.2f}  quad={q:.9f}  solver_rich={rich:.9f}  "
                  f"diff={rich - q:+.2e}  refine_err={refine_err:.2e}  "
                  f"order={order if order is None else round(order, 3)}", flush=True)
    out["comparison"] = rows
    dd = [abs(r["diff_richardson_minus_quadrature"]) for r in rows]
    out["max_abs_diff_richardson_vs_quadrature"] = max(dd)
    out["max_refinement_error"] = max(r["refinement_error"] for r in rows)
    worst = rows[int(np.argmax(dd))]
    out["worst_point"] = dict(d=worst["d"], nu=worst["nu"],
                              diff=worst["diff_richardson_minus_quadrature"],
                              refinement_error=worst["refinement_error"])
    print(f"max |solver(Richardson) - quadrature| = "
          f"{out['max_abs_diff_richardson_vs_quadrature']:.3e}   "
          f"max solver refinement error = {out['max_refinement_error']:.3e}", flush=True)

    # floor sensitivity at one point
    fl = []
    for cm in (1e-4, 1e-5, 1e-6):
        P, dg = P_measure(2.10, 0.35, C_B, 0.002, c_min=cm)
        fl.append(dict(c_min=cm, P=P, J=dg["J"]))
        print(f"  floor c_min={cm:g}: P={P:.9f}", flush=True)
    out["floor_sensitivity_d0.35_nu2.10_h0.002"] = fl

    print("Monte Carlo, 10^6 agents, exact event times", flush=True)
    mc = []
    for nu, d in ((1.90, 0.40), (2.10, 0.30), (2.30, 0.45)):
        m = mc_P(nu, d, C_B, seed=int(1000 * nu + 100 * d))
        q = P_stat(nu, d, C_B, M=32, N=256)
        m["quadrature"] = q
        m["quadrature_minus_p_hat"] = q - m["p_hat"]
        m["quadrature_inside_ci95"] = m["ci95_lo"] <= q <= m["ci95_hi"]
        mc.append(m)
        print(f"  d={d} nu={nu}: MC {m['p_hat']:.6f} "
              f"[{m['ci95_lo']:.6f}, {m['ci95_hi']:.6f}]  quad {q:.9f}  "
              f"inside={m['quadrature_inside_ci95']}", flush=True)
    out["monte_carlo"] = mc
    json.dump(out, open(os.path.join(OUT, "pnu_independent_check.json"), "w"),
              indent=2)
    print("wrote pnu_independent_check.json", flush=True)
