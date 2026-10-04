"""Stage 3 item P8 — configuration (censored supplement).

FIXED from design v0.3.1 A4 item P8 and the owner's Stage 3 estimand:
  "Finite-N extinction on the persistent branch, P5 parameters at lambda = 2,
   f = 0.5: extinction-time distribution at N in {100, 200, 400, 800} with a
   predeclared maximum observation time T_max = 2000 and censored survival
   reporting.  Predicted: extinction almost surely with a median that grows
   steeply in N; no scaling law is registered.  100 replicates per N."
  Owner, 2026-10-01: "right-censored at T_max = 2000; if fewer than half the runs
   extinguish, report 'median > T_max'; no median from observed extinctions alone."

P5 parameters (design v0.3.1 A4 item P5): r = 1, alpha = 2, beta = 0, c_b = 0.5,
kappa = rho = 0, eps = 1, I1, one pulse of reach f.  c_h declared 0.01 as in P5 and
immaterial for the same reason (every deposit is +alpha cos 0, so no conviction is
ever negative and no stance ever leaves +).
"""
MASTER_SEED = 20261006          # DECLARED; distinct from 20261001-20261005

P8 = dict(
    fixed=dict(r=1.0, alpha=2.0, beta=0.0, c_b=0.5, kappa=0.0, rho=0.0, eps=1.0,
               initial_law="I1", pulse_angle=0, lam=2.0, f=0.5,
               N_list=[100, 200, 400, 800], replicates=100, T_max=2000.0),
    declared=dict(c_h=0.01,
                  # A* = 1 - exp(-lambda L A*) with lambda = 2, L = ln 2 gives
                  # exactly 0.5; reported for context, not as a P8 endpoint
                  A_star=0.5),
)
