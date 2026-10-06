"""Case-A fold under alternative frozen constructions, to test which one (if any)
produces the Appendix E C7(c) values A_f = 0.5603318, H_f = 158.354403,
t_ad,f = 66.30915.  Writes stage2b/outputs/raw/caseA_fold_variants.json.

Constructions, all with the same fold condition F(A_f,H_f)=A_f, d/dA F = 1 and
the same t_ad,f = int_0^{H_f} dH/(lambda A_+(H)):

  mixture_n1    F = sum_n w_n(H) P_{lambda A}(alpha r^n), n = 1 + Poisson(H)
                  -- Appendix C.7.1 + C.7.2 as written (the first CS run)
  mixture_n0    same with n = Poisson(H)              -- counter-offset test
  single_mean_n F = P_{lambda A}(alpha r^{E[n]}),  E[n] = 1 + H
  mean_dose     F = P_{lambda A}(alpha E[r^n]),  E[r^n] = (1-f+fr) e^{-(1-r)H}
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dose_mixture_fold as DMF                                   # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")
os.makedirs(OUT, exist_ok=True)
MAN = dict(A_f=0.5603318, H_f=158.354403, t_ad_f=66.30915)
A, R, LAM, CB, F = DMF.ALPHA, DMF.R, DMF.LAM, DMF.C_B, DMF.F_REACH


def make_F(kind, M, N):
    if kind in ("mixture_n1", "mixture_n0"):
        off = 1 if kind == "mixture_n1" else 0
        return lambda a, H: DMF.F_map(a, H, M=M, N=N, offset=off)
    if kind == "single_mean_n":
        return lambda a, H: DMF.P_stat(LAM * a, A * R ** (1.0 + H), CB, M=M, N=N)
    if kind == "mean_dose":
        B = lambda H: (1 - F + F * R) * math.exp(-(1 - R) * H)        # noqa: E731
        return lambda a, H: DMF.P_stat(LAM * a, A * B(H), CB, M=M, N=N)
    raise ValueError(kind)


def gmax(Ff, H):
    r = minimize_scalar(lambda a: a - Ff(a, H), bounds=(1e-3, 0.999),
                        method="bounded", options=dict(xatol=1e-11))
    return -r.fun, r.x


def fold(Ff, lo, hi):
    Hf = brentq(lambda H: gmax(Ff, H)[0], lo, hi, xtol=1e-9)
    g, Af = gmax(Ff, Hf)
    return Hf, Af


def t_ad(Ff, Hf, nq):
    s, w = DMF._gl(nq)
    V = math.sqrt(Hf)
    v = V * s
    Hs = Hf - v ** 2
    vals = np.empty_like(Hs)
    prev = None
    for i in np.argsort(-Hs):
        H = float(Hs[i])
        lo = prev if prev is not None else gmax(Ff, H)[1]
        if Ff(lo, H) - lo < 0:
            lo = gmax(Ff, H)[1]
        a = brentq(lambda x: Ff(x, H) - x, lo, 0.99999, xtol=1e-12)
        vals[i] = 2.0 * v[i] / (LAM * a)
        prev = a
    return float(V * (w * vals).sum())


def run(kind, lo, hi, rungs=((24, 128, 32), (32, 256, 48))):
    lad = []
    for M, N, nq in rungs:
        Ff = make_F(kind, M, N)
        Hf, Af = fold(Ff, lo, hi)
        lad.append(dict(A_f=Af, H_f=Hf, t_ad_f=t_ad(Ff, Hf, nq),
                        settings=dict(M=M, N=N, nq=nq)))
        print(f"  [{kind}] M={M} N={N}: A_f={Af:.9f} H_f={Hf:.6f} "
              f"t_ad_f={lad[-1]['t_ad_f']:.6f}", flush=True)
    fin, prev = lad[-1], lad[-2]
    err = {k: abs(fin[k] - prev[k]) for k in ("A_f", "H_f", "t_ad_f")}
    dev = {k: fin[k] - MAN[k] for k in MAN}
    printed = {"A_f": f"{fin['A_f']:.7f}" == f"{MAN['A_f']:.7f}",
               "H_f": f"{fin['H_f']:.6f}" == f"{MAN['H_f']:.6f}",
               "t_ad_f": f"{fin['t_ad_f']:.5f}" == f"{MAN['t_ad_f']:.5f}"}
    print(f"  [{kind}] dev vs manuscript: " +
          ", ".join(f"{k} {dev[k]:+.6g}" for k in ("A_f", "H_f", "t_ad_f")) +
          f"   printed-match {printed}", flush=True)
    return dict(construction=kind, result={k: fin[k] for k in MAN},
                numerical_error=err, deviation_from_manuscript=dev,
                reproduces_manuscript_to_printed_digits=printed, ladder=lad)


if __name__ == "__main__":
    res = dict(manuscript=MAN, parameters=dict(alpha=A, r=R, lam=LAM, c_b=CB, f=F),
               variants=[])
    for kind, lo, hi in (("single_mean_n", 120.0, 200.0),
                         ("mean_dose", 120.0, 200.0)):
        print(kind, flush=True)
        res["variants"].append(run(kind, lo, hi))
    # the two mixture runs already exist; fold their summaries in for comparison
    for f, tag in (("dose_mixture_fold_caseA.json", "mixture_n1"),
                   ("dose_mixture_fold_caseA_offset0.json", "mixture_n0")):
        d = json.load(open(os.path.join(OUT, f)))
        res["variants"].append(dict(
            construction=tag, result=d["result"],
            numerical_error=d["numerical_error"],
            deviation_from_manuscript=d["deviation_from_manuscript"],
            reproduces_manuscript_to_printed_digits=d.get(
                "reproduces_manuscript_to_printed_digits"),
            source_file=f))
    json.dump(res, open(os.path.join(OUT, "caseA_fold_variants.json"), "w"), indent=2)
    print("wrote caseA_fold_variants.json", flush=True)
