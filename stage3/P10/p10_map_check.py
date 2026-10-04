"""Stage 3 item P10 — WITHDRAWN, NOT RUN.  Algebraic check of the coefficient map.

P10 was withdrawn from Stage 3 by the owner on 2026-10-02:

    "P10 withdrawn from Stage 3: the registered lag window is empty at h = 0.1 and
     0.05; the Lux coefficient map stays in the manuscript as a derived closure
     without numerical certification."

The empty window, for the record.  The Stage 3 estimand measures H and J from the
conviction drift, and D from the lagged increment variance, over lags in
[5/(rho+kappa), 0.1/eps].  Under the R10 map rho = p_0/h and kappa = k_0/h, so with
p_0 = k_0 = 1 the lower edge is 5h/2 while the upper edge is fixed at 0.1/eps:

    h = 0.10 -> lag in [0.2500, 0.1000]   EMPTY
    h = 0.05 -> lag in [0.1250, 0.1000]   EMPTY
    h = 0.02 -> lag in [0.0500, 0.1000]   non-empty

The window is non-empty only for h <= 0.04, i.e. for one point of the registered
grid, which leaves nothing to check the O(h) convergence against.  No simulation was
run and no number is certified.

What this file DOES establish is that the registered coefficients are algebraically
correct: it recomputes them from the Appendix C definitions (C6.1) and the limit
formulas (C6.5, C6.6) and compares with design v0.3.1 A4.  That is a check of the
derivation, NOT a numerical certification of the map against the finite-N process.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# design v0.3.1 A4, item P10
a_0, b_0, Lambda, p_0, k_0, delta_deg, eps = 1.2, 0.8, 1.0, 1.0, 1.0, 30.0, 1.0
H_REG, J_REG, D_REG, JD_REG, K_REG = 2.5, 0.8, 1.367, 0.585, 1.46
H_GRID = [0.1, 0.05, 0.02]

# Appendix C C6.1
abar_0 = (a_0 + b_0) / 2.0
d_0 = (a_0 - b_0) / 2.0
v_0 = p_0 + k_0
cos2d = math.cos(math.radians(2.0 * delta_deg))
U = p_0 + k_0 * cos2d
q = (p_0 + k_0 * cos2d ** 2) / v_0
g = 1.0 - q

# Appendix C C6.5, C6.6
H = abar_0 * q * U / (1.0 - q)
J = d_0 * U / (1.0 - q)
D = (Lambda * q / 2.0) * (d_0 ** 2 + abar_0 ** 2 * (1.0 + q) / (1.0 - q))

out = dict(
    status="WITHDRAWN, NOT RUN",
    withdrawn_by="owner, 2026-10-02",
    reason="the registered lag window [5/(rho+kappa), 0.1/eps] is empty at h = 0.1 "
           "and h = 0.05 because rho + kappa = 2/h under the R10 map; it is "
           "non-empty only for h <= 0.04, i.e. at one point of the registered grid",
    manuscript_disposition="the Lux coefficient map stays in the manuscript as a "
                           "derived closure without numerical certification",
    C6_1=dict(abar_0=abar_0, d_0=d_0, v_0=v_0, U=U, q=q, g=g),
    computed=dict(H=H, J=J, D=D, J_over_D=J / D, K=(H - eps / 2.0) / D),
    registered=dict(H=H_REG, J=J_REG, D=D_REG, J_over_D=JD_REG, K=K_REG),
    deviation=dict(H=H - H_REG, J=J - J_REG, D=D - D_REG,
                   J_over_D=J / D - JD_REG, K=(H - eps / 2.0) / D - K_REG),
    wall_pinning=dict(C6_8_H_gt_eps=bool(H > eps),
                      C6_9_H_minus_absJx_gt_eps_at_x_1=bool(H - abs(J) > eps),
                      note="C6.8 pins the wells to the walls at x = 0; C6.9 keeps "
                           "both wells wall-pinned for all |x| <= 1"),
    lag_window=[dict(h=h, rho=p_0 / h, kappa=k_0 / h,
                     lag_lo=5.0 / (p_0 / h + k_0 / h), lag_hi=0.1 / eps,
                     empty=bool(5.0 / (p_0 / h + k_0 / h) >= 0.1 / eps))
                for h in H_GRID],
    lag_window_nonempty_iff="h <= 0.04",
    mapped_parameters=[dict(h=h, alpha=a_0 * h, beta=b_0 * h, lam=Lambda / h ** 2,
                            rho=p_0 / h, kappa=k_0 / h, c_b=0.05 * h)
                       for h in H_GRID],
)
with open(os.path.join(HERE, "outputs", "p10_map_check.json"), "w") as fh:
    json.dump(out, fh, indent=2)

print("Appendix C C6.1:  abar_0 = %.4f  d_0 = %.4f  U = %.6f  q = %.6f" %
      (abar_0, d_0, U, q))
print("C6.5 / C6.6 recomputed vs design v0.3.1 A4 registered:")
for k in ("H", "J", "D", "J_over_D", "K"):
    print(f"  {k:<9} computed {out['computed'][k]:.9f}   registered "
          f"{out['registered'][k]}   deviation {out['deviation'][k]:+.2e}")
print("wall pinning: C6.8 H > eps -> %s ; C6.9 H - |J| > eps -> %s"
      % (out["wall_pinning"]["C6_8_H_gt_eps"],
         out["wall_pinning"]["C6_9_H_minus_absJx_gt_eps_at_x_1"]))
print("lag window:")
for w in out["lag_window"]:
    print(f"  h={w['h']:<5} [{w['lag_lo']:.4f}, {w['lag_hi']:.4f}]  "
          f"{'EMPTY' if w['empty'] else 'non-empty'}")
