"""Case-A dose-mixture fold, recomputed after BUGLOG S2B-CS1.

S2B-CS1: dose_mixture_fold.P_stat carried an off-by-one in the method-of-steps
recursion for k >= 2 -- for u in [kd, (k+1)d] the argument v = u - d lies in step
k-1's interval, but the code normalised against (k-2)d and interpolated
A_nodes[k-2].  The branch is reachable only when K = ceil(1/d) >= 3, i.e. d < 1/2,
which no validation case covered (fold_exact.py and predictions_s2.P_nu are both
restricted to d >= 1/2).  Every case-A fold number is affected because the fold
region needs doses in [0.24, 0.67].

Supersedes dose_mixture_fold_caseA.json, dose_mixture_fold_caseA_offset0.json and
caseA_fold_variants.json, all retained.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dose_mixture_fold as DMF                                   # noqa: E402
import caseA_fold_variants as CFV                                 # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")
MAN = CFV.MAN
RUNGS = ((24, 128, 32), (32, 256, 48), (40, 320, 56))


def summarise(lad, tag):
    fin, prev = lad[-1], lad[-2]
    err = {k: abs(fin[k] - prev[k]) for k in MAN}
    dev = {k: fin[k] - MAN[k] for k in MAN}
    printed = {"A_f": f"{fin['A_f']:.7f}" == f"{MAN['A_f']:.7f}",
               "H_f": f"{fin['H_f']:.6f}" == f"{MAN['H_f']:.6f}",
               "t_ad_f": f"{fin['t_ad_f']:.5f}" == f"{MAN['t_ad_f']:.5f}"}
    print(f"  [{tag}] A_f={fin['A_f']!r} H_f={fin['H_f']!r} "
          f"t_ad_f={fin['t_ad_f']!r}", flush=True)
    print(f"  [{tag}] dev " + ", ".join(f"{k} {dev[k]:+.6g}" for k in
          ("A_f", "H_f", "t_ad_f")) + f"  printed-match {printed}", flush=True)
    return dict(construction=tag, result={k: fin[k] for k in MAN},
                numerical_error=err, deviation_from_manuscript=dev,
                reproduces_manuscript_to_printed_digits=printed, ladder=lad)


if __name__ == "__main__":
    res = dict(buglog="S2B-CS1", manuscript=MAN, variants=[])

    for tag, off, lo, hi in (("mixture_n1", 1, 120.0, 200.0),
                             ("mixture_n0", 0, 120.0, 200.0)):
        print(tag, flush=True)
        lad = []
        for M, N, nq in RUNGS:
            r = DMF.run(M, N, nq, lo=lo, hi=hi, offset=off)
            lad.append({k: r[k] for k in MAN} | {"settings": r["settings"]})
            print(f"    M={M} N={N}: A_f={r['A_f']:.9f} H_f={r['H_f']:.6f} "
                  f"t_ad_f={r['t_ad_f']:.6f}", flush=True)
        res["variants"].append(summarise(lad, tag))

    for tag, lo, hi in (("single_mean_n", 120.0, 220.0),
                        ("mean_dose", 120.0, 220.0)):
        print(tag, flush=True)
        lad = []
        for M, N, nq in RUNGS:
            Ff = CFV.make_F(tag, M, N)
            Hf, Af = CFV.fold(Ff, lo, hi)
            lad.append(dict(A_f=Af, H_f=Hf, t_ad_f=CFV.t_ad(Ff, Hf, nq),
                            settings=dict(M=M, N=N, nq=nq)))
            print(f"    M={M} N={N}: A_f={Af:.9f} H_f={Hf:.6f} "
                  f"t_ad_f={lad[-1]['t_ad_f']:.6f}", flush=True)
        res["variants"].append(summarise(lad, tag))

    json.dump(res, open(os.path.join(OUT, "caseA_fold_v2.json"), "w"), indent=2)
    print("wrote caseA_fold_v2.json", flush=True)
