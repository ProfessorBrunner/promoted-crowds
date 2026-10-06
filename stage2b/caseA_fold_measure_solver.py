"""Case-A dose-mixture fold computed with the D.3 measure solver's P_nu in place
of the method-of-steps quadrature.  Writes caseA_fold_measure_solver.json.

The solver costs ~1.2 s per (nu, d) and the fold needs O(10^5) evaluations, so it
is tabulated on a Chebyshev grid and the identical fold machinery is run on the
interpolant.  Panels break at d = 1/k so no kink of P(.,d) sits inside a panel.
For d >= 1 every jump clips to 1 and P = 1 - c_b^a exactly, so no solver call is
needed there; for d < D_MIN the mixture weight is below 1e-7 at every H reached
and the (bug-fixed) quadrature is used.  The solver value at each node is the
Richardson limit of an h ladder, and the whole fold is run at two ladder settings
so the reported error is a refinement error, not an assumed one.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinetic as KIN                                             # noqa: E402
import dose_mixture_fold as DMF                                   # noqa: E402
import caseA_fold_variants as CFV                                 # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")
C_B, LAM = DMF.C_B, DMF.LAM
D_MIN = 0.2
A_LO, A_HI = 1.2, 2.9
T_STAT = 30.0
PANELS = [D_MIN, 0.25, 1.0 / 3.0, 0.5, 1.0]
N_D, N_A = 12, 12


def P_solver(nu, d, hs, c_min=1e-5):
    v = []
    for h in hs:
        _, A, _ = KIN.solve(lam=0.0, alpha=d, r=1.0, c_b=C_B, f=0.0, T=T_STAT,
                            h=h, c_min=c_min, K=3, eps=1.0, nu_prescribed=float(nu))
        v.append(float(A[-1]))
    return v[-1] + (v[-1] - v[-2]), abs(v[-1] - v[-2])


def cheb(n, lo, hi):
    j = np.arange(n + 1)
    x = 0.5 * (1 - np.cos(np.pi * j / n))
    bw = (-1.0) ** j
    bw[0] *= 0.5
    bw[-1] *= 0.5
    return lo + (hi - lo) * x, bw, x


def bary1(xq, nodes01, bw, vals, lo, hi):
    w = (xq - lo) / (hi - lo)
    diff = w - nodes01
    i = np.isclose(diff, 0.0, atol=0.0)
    if i.any():
        return float(vals[np.argmax(i)])
    q = bw / diff
    return float(q @ vals / q.sum())


def build_table(hs):
    an, abw, a01 = cheb(N_A, A_LO, A_HI)
    panels = []
    worst = 0.0
    for p in range(len(PANELS) - 1):
        lo, hi = PANELS[p], PANELS[p + 1]
        dn, dbw, d01 = cheb(N_D, lo, hi)
        V = np.empty((len(an), len(dn)))
        for i, a in enumerate(an):
            for j, d in enumerate(dn):
                V[i, j], e = P_solver(a, d, hs)
                worst = max(worst, e)
        panels.append(dict(lo=lo, hi=hi, dn=dn, d01=d01, dbw=dbw, V=V))
        print(f"    panel d in [{lo:.4f}, {hi:.4f}] done", flush=True)
    return dict(an=an, abw=abw, a01=a01, panels=panels, max_refinement_error=worst)


def make_P(tab):
    quad = DMF.P_stat                      # capture BEFORE substitution

    def P(a, d, c_b=C_B, M=None, N=None):
        if d >= 1.0:
            return 1.0 - c_b ** a
        if d < D_MIN:
            return quad(a, d, c_b, M=32, N=256)
        a = min(max(a, A_LO), A_HI)
        for pn in tab["panels"]:
            if pn["lo"] - 1e-12 <= d <= pn["hi"] + 1e-12:
                col = np.array([bary1(d, pn["d01"], pn["dbw"], pn["V"][i],
                                      pn["lo"], pn["hi"])
                                for i in range(len(tab["an"]))])
                return bary1(a, tab["a01"], tab["abw"], col, A_LO, A_HI)
        raise ValueError(d)
    return P


if __name__ == "__main__":
    res = dict(manuscript=CFV.MAN, solver="kinetic.solve r=1 f=0 nu_prescribed "
               "(manuscript D.3)", T_stationary=T_STAT, d_min_solver=D_MIN,
               a_range=[A_LO, A_HI], panels=PANELS, nodes=dict(d=N_D, a=N_A),
               settings=[])
    for hs in ([0.008, 0.004], [0.004, 0.002]):
        print(f"  tabulating with h ladder {hs}", flush=True)
        tab = build_table(hs)
        P = make_P(tab)
        orig = DMF.P_stat
        DMF.P_stat = P                       # substitute the solver everywhere
        try:
            Ff = lambda a, H: DMF.F_map(a, H, M=32, N=256, offset=1)   # noqa: E731
            Hf, Af = CFV.fold(Ff, 140.0, 180.0)
            tad = CFV.t_ad(Ff, Hf, 48)
        finally:
            DMF.P_stat = orig
        # interpolant check at points off the grid
        chk = []
        for a, d in ((1.7, 0.27), (2.1, 0.38), (2.4, 0.62)):
            ex, _ = P_solver(a, d, hs)
            chk.append(dict(a=a, d=d, interp=P(a, d), direct=ex,
                            diff=P(a, d) - ex))
        res["settings"].append(dict(
            h_ladder=hs, A_f=Af, H_f=Hf, t_ad_f=tad,
            max_node_refinement_error=tab["max_refinement_error"],
            interpolant_check=chk))
        print(f"  [h={hs}] A_f={Af!r} H_f={Hf!r} t_ad_f={tad!r}", flush=True)
        print(f"           max node refinement err {tab['max_refinement_error']:.2e}; "
              f"interp check max |diff| "
              f"{max(abs(c['diff']) for c in chk):.2e}", flush=True)

    s0, s1 = res["settings"]
    res["result"] = {k: s1[k] for k in ("A_f", "H_f", "t_ad_f")}
    res["refinement_error"] = {k: abs(s1[k] - s0[k]) for k in ("A_f", "H_f", "t_ad_f")}
    res["deviation_from_manuscript"] = {k: s1[k] - CFV.MAN[k] for k in CFV.MAN}
    json.dump(res, open(os.path.join(OUT, "caseA_fold_measure_solver.json"), "w"),
              indent=2, default=float)
    for k in ("A_f", "H_f", "t_ad_f"):
        print(f"{k}: solver-fold {s1[k]!r} +-{res['refinement_error'][k]:.2e}  "
              f"manuscript {CFV.MAN[k]}  dev "
              f"{res['deviation_from_manuscript'][k]:+.4g}", flush=True)
    print("wrote caseA_fold_measure_solver.json", flush=True)
