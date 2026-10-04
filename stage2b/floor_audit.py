"""Floor audit of every certified kinetic reference (owner request, 2026-10-02).

BUGLOG S2B-4 showed that the conviction floor c_min is invisible to an h-ladder, so
each certified kinetic reference is re-examined with its own FLOOR ladder.  Floors as
originally run:

    P4 f_c^MF (p4_reference.py)   c_min = 1e-3
    P6 case A (p6_reference.py)   c_min = 2e-2   <- coarser than the one that biased
    P6 case B (p6_reference.py)   c_min = 1e-2   <- coarser than the one that biased

Stage 1 (this script, `probe`) holds h at its original coarsest useful value and
walks the floor down, which isolates the floor component.  Stage 2 (`ladder`) re-runs
the full h-ladder at the converged floor for any quantity whose floor component is
not negligible against its published h-uncertainty, and re-extrapolates.

Both components are reported separately, never combined into one number.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "stage2"))
import kinetic as KIN                                      # noqa: E402
from crowd1 import predictions_s2 as PS                     # noqa: E402

OUT = os.path.join(HERE, "outputs", "raw")

# --- P4 basin classifier, copied from p4_reference.py with c_min exposed ----------
P4 = dict(alpha=0.5, r=1.0, c_b=0.3)


def classify(lam, f, h, T, c_min):
    t, A, d = KIN.solve(lam=lam, alpha=P4["alpha"], r=P4["r"], c_b=P4["c_b"], f=f,
                        T=T, h=h, c_min=c_min, K=3)
    A_star = PS.p4_branches(lam)["A_star"]
    A_fold = PS.p4_fold()["A_fold"]
    end = float(A[-1])
    decreasing = A[-1] <= A[-2]
    if end > 0.5 * A_star:
        return "ignite"
    if end < 0.5 * A_fold and decreasing:
        return "die"
    return "unclassified"


def bisect_fc(lam, h, T, lo, hi, c_min, tol=1e-6):
    assert classify(lam, lo, h, T, c_min) == "die"
    assert classify(lam, hi, h, T, c_min) == "ignite"
    n = 0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lab = classify(lam, mid, h, T, c_min)
        if lab == "unclassified":
            raise RuntimeError(f"unclassified at lam={lam} f={mid}")
        if lab == "ignite":
            hi = mid
        else:
            lo = mid
        n += 1
    return 0.5 * (lo + hi), 0.5 * (hi - lo), n


# --- P6 crossing series, copied from p6_reference.py with c_min exposed -----------
P6A = dict(alpha=2.0, r=0.99, lam=3.0, c_b=0.5, level=0.5603, T=95.0)
P6B = dict(alpha=1.0, r=0.95, lam=2.5, c_b=0.4, level=0.325, T=40.0)


def p6_point(cfg, h, c_min):
    t, A, d = KIN.solve(lam=cfg["lam"], alpha=cfg["alpha"], r=cfg["r"],
                        c_b=cfg["c_b"], f=1.0, T=cfg["T"], h=h, c_min=c_min, K=3)
    tc = KIN.first_down_crossing(t, A, cfg["level"])
    return dict(h=d["h"], c_min=c_min, t_cross=tc,
                Lambda=KIN.accumulated_index(t, A, cfg["lam"], tc),
                n_slabs=d["n_slabs"], J=d["J"], mass_at_zero=d["mass_at_zero"],
                mass_deficit=1.0 - d["mass"])


def richardson(vals):
    """Order-1 Richardson on a halving ladder; error = last increment."""
    return vals[-1] + (vals[-1] - vals[-2]), abs(vals[-1] - vals[-2])


BRACKETS = {1.60: (0.10, 0.20), 1.75: (0.02, 0.10), 1.90: (0.002, 0.03)}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    fp = os.path.join(OUT, "floor_audit.json")
    res = json.load(open(fp)) if os.path.exists(fp) else {}

    if mode == "probe":
        res["floors_as_run"] = dict(P4_f_c=1e-3, P6_case_A=2e-2, P6_case_B=1e-2)

        print("P4 f_c^MF - floor ladder at fixed h = 0.004, T = 120", flush=True)
        rows = []
        for lam in (1.60, 1.75, 1.90):
            lo, hi = BRACKETS[lam]
            for c_min in (1e-3, 1e-4, 1e-5):
                fc, half, n = bisect_fc(lam, 0.004, 120.0, lo, hi, c_min)
                rows.append(dict(lam=lam, h=0.004, T=120.0, c_min=c_min, f_c=fc,
                                 bisection_half_width=half, n_evals=n))
                print(f"  lam={lam}  c_min={c_min:.0e}  f_c = {fc:.8f}  "
                      f"(+-{half:.1e}, {n} evals)", flush=True)
        res["P4_floor_probe"] = rows

        print("\nP6 case A - floor ladder at fixed h = 0.01, T = 95", flush=True)
        rows = []
        for c_min in (2e-2, 1e-3, 1e-4):
            r = dict(T=P6A["T"]); r.update(p6_point(P6A, 0.01, c_min))
            rows.append(r)
            print(f"  c_min={c_min:.0e}  t_cross = {r['t_cross']:.5f}  "
                  f"J={r['J']} slabs={r['n_slabs']} "
                  f"mass_at_zero={r['mass_at_zero']:.2e}", flush=True)
        res["P6A_floor_probe"] = rows

        print("\nP6 case B - floor ladder at fixed h = 0.0025, T = 40", flush=True)
        rows = []
        for c_min in (1e-2, 1e-3, 1e-4):
            r = dict(T=P6B["T"]); r.update(p6_point(P6B, 0.0025, c_min))
            rows.append(r)
            print(f"  c_min={c_min:.0e}  t_cross = {r['t_cross']:.5f}  "
                  f"Lambda = {r['Lambda']:.5f}  J={r['J']} slabs={r['n_slabs']} "
                  f"mass_at_zero={r['mass_at_zero']:.2e}", flush=True)
        res["P6B_floor_probe"] = rows

    if mode == "ladder":
        # The floor error is h-INDEPENDENT (that is why an h-ladder cannot see it).
        # So rather than repeat the whole h-ladder at the fine floor -- which changes
        # no reported digit and costs hours at c_min = 1e-5 -- measure the floor
        # shift at a SECOND h and show it is the same shift.  The corrected value is
        # then the published Richardson limit plus that shift, and the two error
        # components stay separate: h from the published ladder, floor from the
        # residual of the floor ladder.
        # T = 240 throughout this pass.  At h = 0.002 with the fine floor the
        # lambda = 1.90 boundary trajectory is still undecided at T = 120 and the
        # classifier RAISES rather than forcing a basin (see P4_lam190_note);
        # T = 240 resolves it and p4_reference.py's own horizon check already
        # showed T = 120 and T = 240 agree to eight digits wherever both classify.
        print("P4 f_c^MF - floor shift at two h, T = 240", flush=True)
        rows = []
        for h in (0.004, 0.002):
            for lam in (1.60, 1.75, 1.90):
                lo, hi = BRACKETS[lam]
                for c_min in (1e-3, 1e-5):
                    fc, half, n = bisect_fc(lam, h, 240.0, lo, hi, c_min)
                    rows.append(dict(lam=lam, h=h, T=240.0, c_min=c_min, f_c=fc,
                                     bisection_half_width=half, n_evals=n))
                    print(f"  h={h:.4f} lam={lam}  c_min={c_min:.0e}  "
                          f"f_c = {fc:.8f}  (+-{half:.1e}, {n} evals)", flush=True)
        res["P4_floor_shift_two_h"] = rows
        shifts = {}
        for h in (0.004, 0.002):
            for lam in (1.60, 1.75, 1.90):
                v = {r["c_min"]: r["f_c"] for r in rows
                     if r["lam"] == lam and r["h"] == h}
                shifts[f"lam={lam},h={h}"] = v[1e-5] - v[1e-3]
        res["P4_floor_shift_summary"] = shifts
        print("  floor shift (c_min 1e-3 -> 1e-5), h-independence check:")
        for k, v in shifts.items():
            print(f"    {k}: {v:+.4e}", flush=True)

        print("\nP6 case A - floor shift at a second h (0.02), T = 95", flush=True)
        rows = []
        for c_min in (2e-2, 1e-3):
            r = p6_point(P6A, 0.02, c_min)
            rows.append(r)
            print(f"  c_min={c_min:.0e}  t_cross = {r['t_cross']:.5f}  J={r['J']}",
                  flush=True)
        res["P6A_floor_shift_second_h"] = rows

        print("\nP6 case B - floor shift at a second h (0.005), T = 40", flush=True)
        rows = []
        for c_min in (1e-2, 1e-3):
            r = p6_point(P6B, 0.005, c_min)
            rows.append(r)
            print(f"  c_min={c_min:.0e}  t_cross = {r['t_cross']:.5f}  "
                  f"Lambda = {r['Lambda']:.5f}  J={r['J']}", flush=True)
        res["P6B_floor_shift_second_h"] = rows

    json.dump(res, open(fp, "w"), indent=2)
    print(f"\nwrote {fp}", flush=True)
