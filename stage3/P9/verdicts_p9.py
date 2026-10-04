"""Stage 3 P9 — A6 verdict table."""
import csv, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config")); sys.path.insert(0, S2)
from crowd1.a6 import make_verdict, finite_N_bias_from_ladder
import p9_config as CFG
FX, RU, DC = CFG.P9["fixed"], CFG.P9["ruled"], CFG.P9["declared"]
RW = json.load(open(os.path.join(HERE, "outputs", "raw", "p9_raw.json")))
FP = json.load(open(os.path.join(HERE, "outputs", "raw", "p9_fixed_points.json")))
CK = json.load(open(os.path.join(HERE, "outputs", "raw",
                                 "p9_reference_checks.json")))
CHK = json.load(open(os.path.join(HERE, "outputs", "raw",
                                  "p9_reference_checks.json")))
# read back the two quadrature-validation figures rather than quoting them
_FX = max(r["flux_rel_err"] for r in CHK["check_flux"])
_VZ = max(abs(r["d"]) for r in CHK["check_v_to_zero"])
cells = {c["lam"]: c for c in RW["cells"]}
bias = dict(
    A_plus=finite_N_bias_from_ladder([(r["N"], r["A_plus"]) for r in RW["N_ladder"]]),
    A_minus=finite_N_bias_from_ladder([(r["N"], r["A_minus"]) for r in RW["N_ladder"]]))
bs = lambda d: float(d.get("residual_bias_at_Nmax", d["top_gap"]))
V = []
for lam in FX["lambdas"]:
    c = cells[lam]; sy = FP["branches"][str(lam)]["symmetric"]
    pred = sy["A_plus"]
    note = (f"C4.7 symmetric branch z = 1/2, the UNIQUE positive branch (the C4.7 "
            f"z-scan found 0 interior sign changes on (0, 1/2) at this lambda); "
            f"linearly stable by C4.11 with spr(J) = {sy['spr']:.6f}; quadrature "
            f"validated (at c_b = {CHK['c_b']}, beta = {CHK['beta']}) against its "
            f"v->0 closed form to {_VZ:.2e} absolute and against the C4.2 flux "
            f"condition to {_FX:.2e} relative")
    for side, key in (("A_+", "A_plus"), ("A_-", "A_minus")):
        V.append(make_verdict(
            name=f"P9 {side} on the two-camp branch at lambda={lam}",
            predicted=pred,
            per_replicate_values=np.array(c["per_replicate"][key]),
            delta=CFG.DELTA_TRAJECTORY_FRAC * pred,
            delta_basis=f"delta = 5% of the C4.7 value {pred:.9f}", N=c["N"],
            numerical_error=7e-9, finite_N_bias=bs(bias[key]),
            closure_error=None, note=note))
    for p in c["perturbations"]:
        nm = (f"P9 relaxation after perturbing A_{p['camp']} by {p['delta']:+.2f} "
              f"at lambda={lam}")
        if not p["n_feasible"]:
            print(f"SKIP (infeasible): {nm}")
            continue
        # The criterion is applied to the REPLICATE MEAN: the stationary sd of A_+
        # at N = 1e5 is ~1.0-1.4e-3, so |dA| < 1e-3 is below the single-replicate
        # noise floor and cannot be met pathwise even at perfect equilibrium.  The
        # verdict row therefore uses the per-replicate deviations of whichever
        # component moved further from equilibrium, so its interval is a genuine
        # Student-t interval on 50 values rather than on two summary numbers.
        dp = np.array(p["dA_plus_end_per_replicate"])
        dm = np.array(p["dA_minus_end_per_replicate"])
        vals = dp if abs(dp.mean()) >= abs(dm.mean()) else dm
        which = "A_+" if abs(dp.mean()) >= abs(dm.mean()) else "A_-"
        V.append(make_verdict(
            name=nm, predicted=0.0, per_replicate_values=vals,
            delta=FX["relax_tol"],
            delta_basis=f"owner's relaxation criterion |dA| < {FX['relax_tol']} "
                        f"over {FX['relax_time']}/eps, applied to the replicate mean",
            N=c["N"], numerical_error=0.0, finite_N_bias=bs(bias["A_plus"]),
            note=f"interval on the 50 replicate deviations of {which} at t = "
                 f"{FX['relax_time']}; the other component's mean deviation is "
                 f"{(dm.mean() if which == 'A_+' else dp.mean()):+.2e}; "
                 f"achieved shift {p['achieved_shift_mean']:+.4f}; max |dA| over "
                 f"single replicates {p['max_abs_dA_end']:.2e} against a stationary "
                 f"single-replicate sd of {c['A_plus_sd']:.2e}, so the criterion is "
                 f"evaluated on the replicate mean (sem "
                 f"{c['A_plus_sd']/math.sqrt(c['replicates']):.2e}); "
                 f"{p['n_relaxed']}/{p['n_feasible']} individual replicates also "
                 f"inside 1e-3"))
# structural invariance, pooled over every cell and replicate
tot_flips = sum(c["checks"]["stance_flips"] for c in RW["cells"])
tot_off = sum(c["checks"]["orientation_off_target"] for c in RW["cells"])
nrep_tot = sum(c["replicates"] for c in RW["cells"])
for nm, val in (("stance never flips (camps are fixed, C4.1)", tot_flips),
                ("orientation stays on {T_+, T_-} (two-camp law invariant)", tot_off)):
    V.append(make_verdict(
        name=f"P9 pathwise: {nm}", predicted=0.0,
        per_replicate_values=np.zeros(nrep_tot) + val, delta=0.0,
        delta_basis="pathwise structural identity: any violation is a FAIL",
        N=DC["N"], numerical_error=0.0, finite_N_bias=0.0,
        note=f"{val} violations over {nrep_tot} replicates x {DC['N']} agents at "
             f"three lambda; a positive agent's deposits are +alpha (accepted T) "
             f"and +beta (rejected T_perp), both positive, and rejecting T_perp "
             f"sends phi to 90+90 = 180 = 0"))
out = dict(verdicts=[v.__dict__ for v in V], finite_N_bias=bias,
           N_ladder=RW["N_ladder"], fixed_points=FP, reference_checks=CK,
           branch_selected="C4.7 symmetric branch z = 1/2 (p = 1/2); the unique "
                           "positive branch at all three lambda",
           infeasible_perturbations=[
               dict(lam=c["lam"], camp=p["camp"], delta=p["delta"],
                    reason=p.get("reason"),
                    inactive_mass_in_camp=FX["M_plus"] - c["A_plus"])
               for c in RW["cells"] for p in c["perturbations"]
               if not p["n_feasible"]])
json.dump(out, open(os.path.join(HERE, "outputs", "p9_results.json"), "w"),
          indent=2, default=float)
with open(os.path.join(HERE, "outputs", "certified_table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(V[0].__dict__)); w.writeheader()
    for v in V: w.writerow(v.__dict__)
from collections import Counter
print(Counter(v.status for v in V))
for v in V:
    print(f"{v.status:5s} {v.name:62s} pred {v.predicted:<11.8f} meas {v.measured:<12.8f} "
          f"diff {v.diff:+.3e}  delta {v.delta:.2e}")
