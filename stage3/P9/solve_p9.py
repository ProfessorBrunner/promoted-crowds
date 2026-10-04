"""Stage 3 P9 — solve the C4.7 fixed points and their stability at each lambda."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from p9_reference import (fixed_point_symmetric, map_C46, jacobian_C410, c47_scan,
                          Fc)
BETA, C_B, EPS, P = 0.4, 0.3, 1.0, 0.5
out = dict(beta=BETA, c_b=C_B, eps=EPS, p=P, alpha=1.0, branches={})
for lam in (1.5, 2.0, 3.0):
    A = fixed_point_symmetric(lam, P, BETA, C_B, EPS)
    rec = dict(lam=lam, symmetric=None, zero_branch_stable=None, c47_scan=None)
    if A is not None:
        Av = np.array([A, A])
        resid = map_C46(Av, lam, P, BETA, C_B, EPS) - Av
        J = jacobian_C410(Av, lam, P, BETA, C_B, EPS)
        ev = np.linalg.eigvals(J)
        rec["symmetric"] = dict(
            A_plus=float(A), A_minus=float(A), A_total=float(2 * A),
            residual=[float(x) for x in resid],
            J=[[float(x) for x in row] for row in J],
            eigenvalues=[float(np.real(e)) for e in ev],
            spr=float(max(abs(ev))),
            stable=bool(max(abs(ev)) < 1.0))
        print(f"lam={lam}: symmetric A_+=A_-={A:.9f}  residual "
              f"{np.max(np.abs(resid)):.2e}  spr(J)={max(abs(ev)):.6f}  "
              f"stable={max(abs(ev))<1.0}", flush=True)
    sc = c47_scan(lam, P, BETA, C_B, EPS)
    rec["c47_scan"] = sc
    r = [s["residual"] for s in sc if s["residual"] is not None]
    sign_changes = sum(1 for i in range(len(r) - 1) if r[i] * r[i + 1] < 0)
    rec["asymmetric_sign_changes_on_z_in_(0,0.5)"] = sign_changes
    print(f"       C4.7 z-scan on (0,0.5): {len(r)} points, "
          f"{sign_changes} interior sign changes "
          f"(residual range {min(r):+.4f} .. {max(r):+.4f})", flush=True)
    out["branches"][str(lam)] = rec
json.dump(out, open(os.path.join(HERE, "outputs", "raw", "p9_fixed_points.json"),
                    "w"), indent=2)
print("done", flush=True)
