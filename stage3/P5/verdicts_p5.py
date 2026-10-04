"""Stage 3 P5 — A6 verdict table."""
import csv, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stage2")
sys.path.insert(0, os.path.join(HERE, "config")); sys.path.insert(0, S2)
from crowd1.a6 import make_verdict, wilson_interval, finite_N_bias_from_ladder
import p5_config as CFG
FX, DC = CFG.P5["fixed"], CFG.P5["declared"]
R   = json.load(open(os.path.join(HERE,"outputs","raw","p5_raw.json")))
DR  = json.load(open(os.path.join(HERE,"outputs","raw","p5_delay_reference.json")))
SX  = json.load(open(os.path.join(HERE,"outputs","raw","p5_survival_extension.json")))
TR  = np.load(os.path.join(HERE,"outputs","raw","p5_traces.npz"))
ref = {(r["lam"], r["f"]): r for r in DR["rows"]}
cells = {(c["lam"], c["f"]): c for c in R["cells"]}
sx = {(c["lam"], c["f"]): c for c in SX["cells"]}
dt = DC["sample_dt"]; w0, w1 = FX["window"]
i0, i1 = int(round(w0/dt)), int(round(w1/dt)); i20 = int(round(FX["burn_in_end"]/dt))
grid = np.arange(0.0, DC["t_end"]+1e-9, dt)

def per_rep_window(lam, f):
    tr = TR[f"lam{lam}_f{f}"]
    return np.trapezoid(tr[:, i0:i1+1], grid[i0:i1+1], axis=1)/(grid[i1]-grid[i0]), tr

V = []
# ---- finite-N bias (A6 source 2) and measurement grid error (A6 source 3)
bias = {str(f): finite_N_bias_from_ladder(
            [(c["N"], c["window_mean_A_conditional"]) for c in R["N_ladder"][str(f)]])
        for f in FX["reaches"]}
g = [c["window_mean_A_conditional"] for c in R["grid_refinement"]]
grid_err = abs(g[-1]-g[-2])

for f in FX["reaches"]:
    # ---------- lambda = 2: persistent branch
    wm, tr = per_rep_window(2.0, f)
    alive = tr[:, i20] > 0
    b = float(bias[str(f)].get("residual_bias_at_Nmax", bias[str(f)]["top_gap"]))
    V.append(make_verdict(
        name=f"P5 active-branch mean A over [20,70] at lambda=2, f={f} "
             f"(conditional on A(20)>0)",
        predicted=0.5, per_replicate_values=wm[alive],
        delta=CFG.DELTA_TRAJECTORY_FRAC*0.5,
        delta_basis="A6/A4b trajectory marker: 5% of A* = 0.5", N=FX["N"],
        numerical_error=max(ref[(2.0,f)]["uncertainty"], grid_err),
        finite_N_bias=b, closure_error=None,
        note=f"A* = 1-exp(-lambda L A*) is EXACTLY 0.5 at lambda=2, L=ln2; the "
             f"exact delay-equation reference gives window mean "
             f"{ref[(2.0,f)]['ladder'][-1]['window_mean_A']:.9f}; survivors "
             f"{int(alive.sum())}/{len(alive)}"))
    # ---------- lambda = 1: activity dies
    wm1, tr1 = per_rep_window(1.0, f)
    V.append(make_verdict(
        name=f"P5 mean A over [20,70] at lambda=1, f={f} (activity dies)",
        predicted=0.0, per_replicate_values=wm1, delta=CFG.DELTA_ZERO_ABS,
        delta_basis="A4a absolute tolerance 1e-3 for zero predictions", N=FX["N"],
        numerical_error=ref[(1.0,f)]["uncertainty"], finite_N_bias=0.0,
        closure_error=None,
        note=f"lambda L = {math.log(2.0):.6f} < 1; "
             f"exact mean-field A(20) = {ref[(1.0,f)]['A_at_20']:.3e}, and every "
             f"finite-N run is exactly extinct by t=20 "
             f"(survivors {int((tr1[:,i20]>0).sum())}/{len(tr1)})"))
    # ---------- pathwise: extinction is absorbing and exact
    viol = int((tr1[:, i20:] > 0).sum())
    V.append(make_verdict(
        name=f"P5 pathwise extinction at lambda=1, f={f}: A(t)=0 for all t>=20",
        predicted=0.0, per_replicate_values=np.zeros(len(tr1))+viol, delta=0.0,
        delta_basis="pathwise structural identity: any violation is a FAIL",
        N=FX["N"], numerical_error=0.0, finite_N_bias=0.0,
        note=f"{viol} grid points with A>0 at or after t=20 across "
             f"{len(tr1)} replicates"))

rep = dict(verdicts=[v.__dict__ for v in V], finite_N_bias=bias,
           measurement_grid_error=grid_err,
           grid_refinement=[(c["dt"], c["window_mean_A_conditional"])
                            for c in R["grid_refinement"]],
           survival=[dict(lam=c["lam"], f=c["f"],
                          registered_50=c["registered_50"], extended=c["extended"])
                     for c in SX["cells"]],
           outbreak_A4a=[dict(lam=c["lam"], f=c["f"],
                              k=c["outbreak_count"], n=c["replicates"],
                              p=wilson_interval(c["outbreak_count"], c["replicates"])[0],
                              ever_active_frac_mean=c["ever_active_frac_mean"])
                         for c in R["cells"]],
           reference=DR)
json.dump(rep, open(os.path.join(HERE,"outputs","p5_results.json"),"w"),
          indent=2, default=float)
with open(os.path.join(HERE,"outputs","certified_table.csv"),"w",newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(V[0].__dict__)); w.writeheader()
    for v in V: w.writerow(v.__dict__)
for v in V:
    print(f"{v.status:13s} {v.name}\n   pred {v.predicted}  meas {v.measured:.8f}  "
          f"diff {v.diff:+.3e}  CI [{v.ci_lo:+.3e},{v.ci_hi:+.3e}]  delta {v.delta:.3e}")
