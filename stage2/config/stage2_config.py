"""Declared configuration of CROWD-1 Stage 2 (A4 items P1, P1-delay, P2, P2-delay,
P3, P4, P6).

FIXED  = verbatim from design v0.3 Part A, or from the Appendix C construction the
         design points to.  Never altered.
DECLARED = not fixed by the design; chosen here, logged, fixed before the runs.

Frozen for Stage 2 by the owner's authorisation of 2026-10-01: design v0.3 Part A
as written, the A4a endpoint definitions, and AMBIGUITIES.md items 1-9 as adopted,
with items 7 and 9 treated as clarifications of the process specification.
"""

MASTER_SEED = 20261002          # DECLARED; distinct from Stage 1's 20261001

# ---- A6 discrepancy categories (FIXED by A6 / A4a)
DELTA_OPERATOR_FRAC = 0.02      # operator checks
DELTA_TRAJECTORY_FRAC = 0.05    # trajectory markers
DELTA_OUTBREAK_ABS = 0.03       # outbreak probabilities
DELTA_ZERO_ABS = 0.01           # |x| <= 0.01 for x = 0
DELTA_AMIT_ABS = 1e-3           # A_max, I, T_act = 0 predictions

# ---- A4a observation horizons (FIXED)
OUTBREAK_HORIZON = 50.0         # t = 50/eps
OUTBREAK_FRACTION = 0.01        # ever-active fraction > 1% of N

# ---- A6 primary endpoints, for the Holm correction (FIXED)
PRIMARY_ENDPOINTS = ["P1", "P1-delay", "P2", "P3", "P4", "P6"]
SECONDARY_ENDPOINTS = ["P2-delay"]

# =========================================================================== P1
P1 = dict(
    fixed=dict(
        initial_law="I2", f=1.0, alpha=1.0, beta=0.25, r=0.5, c_b=0.5, c_h=0.01,
        kappa=0.0, rho=1.0, eps=1.0,
        orders=[(40, 50, 140), (40, 140, 50)],
        held_out_orders=[(50, 40, 140), (140, 40, 50)],
        zero_gaps=True, relax="10/rho",
        lambdas=[1.0, 2.0, 3.5],
        N=100000, N_big=1000000, replicates_big=50,
        # registered operator-check values (C3.15 / C3 table of C3(c)(ii))
        x_pred={(40, 50, 140): 0.0, (40, 140, 50): 0.969846310},
        R_over_lambda_pred={(40, 50, 140): 0.346573590,
                            (40, 140, 50): 0.682696708},
        ratio_pred=1.97,
        R_at_lambda2={"first": 0.693, "second": 1.365},
    ),
    # SEALED before the run by the same direct enumeration that reproduces
    # C3.15 for the two registered orders to 2e-10 (see outputs/sealed_heldout.json)
    sealed_held_out=dict(
        x={(50, 40, 140): 0.0, (140, 40, 50): 0.969846310},
        R_over_lambda={(50, 40, 140): 0.346573590, (140, 40, 50): 0.682696708},
    ),
    declared=dict(
        operator_backgrounds=24, operator_trials_per_background=10000,
        operator_lambda=2.0,
        outbreak_pilot=50, outbreak_halfwidth_target=0.03,
        outbreak_max_replicates=1200,
        t_end=OUTBREAK_HORIZON,
        operator_N_ladder=[10000, 100000],
    ),
)

# ===================================================================== P1-delay
P1_DELAY = dict(
    fixed=dict(tau0_over_rho=[0.0, 0.5, 1.0, 2.0, 5.0, 10.0],
               ratio_limit=1.97, orientation_decay_rate="rho"),
    declared=dict(operator_backgrounds=24, operator_trials_per_background=10000,
                  operator_lambda=2.0, outbreak_replicates=300),
)

# =========================================================================== P2
P2 = dict(
    fixed=dict(
        initial_law="I1", f=1.0, alpha=1.0, beta=0.0, r=0.5, c_b=0.95, c_h=0.01,
        rho=0.0, kappa=0.0, eps=1.0, gap="ln 100",
        orders=[(10, 20, 30), (10, 30, 20), (20, 10, 30)],
        qT_pred={(10, 20, 30): 0.707442366, (10, 30, 20): 0.759089355,
                 (20, 10, 30): 0.637858566},
        R_over_lambda_pred={(10, 20, 30): 0.036287050, (10, 30, 20): 0.038936194,
                            (20, 10, 30): 0.032717867},
        I2_R_over_lambda_pred=0.025646647,      # 0.0256 in A4; C3.14 at q_T = 1/2
        lambda_pop=26.5,
        R_pop={(10, 20, 30): 0.962, (10, 30, 20): 1.032, (20, 10, 30): 0.867},
        outbreak_precision_target=0.02,
        N=100000,
    ),
    declared=dict(operator_backgrounds=20, operator_trials_per_background=4000,
                  operator_lambda=26.5, outbreak_pilot=50,
                  outbreak_max_replicates=1200, t_end=OUTBREAK_HORIZON,
                  operator_N_ladder=[10000, 100000]),
)

# ===================================================================== P2-delay
P2_DELAY = dict(
    fixed=dict(tau0=[0.0, 1.0, 3.0, 10.0], rho_values=[0.0, 0.5],
               claim_rho0="order dependence persists (orientation never relaxes)",
               claim_rho05="order dependence decays as exp(-rho tau0)",
               a4a="post-campaign preparation recomputed for rho = 0.5; the "
                   "rho = 0 coefficients are not reused"),
    declared=dict(operator_backgrounds=10, operator_trials_per_background=4000,
                  operator_lambda=26.5, N=100000),
)

# =========================================================================== P3
P3 = dict(
    fixed=dict(
        initial_law="I2", f=1.0, alpha=0.6, beta=0.0, r=0.5, c_b=0.5, c_h=0.01,
        rho=0.0, kappa=0.0, eps=1.0, zero_gap=True,
        orders=[(45, 20), (20, 45)],
        R_fr0_over_lambda={(45, 20): 0.316695967, (20, 45): 0.218867184},
        EZ2_over_lambda2={(45, 20): 0.0976502474, (20, 45): 0.0689974669},
        R_inf_over_lambda=0.091160778,
        lambda_pop=4.0, tau0=[0.0, 1.0, 3.0, 10.0],
        N=100000, replicates={0.0: 300, 1.0: 100, 3.0: 100, 10.0: 100},
    ),
    declared=dict(operator_backgrounds=20, operator_trials_per_background=4000,
                  operator_lambda=4.0, EZ2_replicates=20000,
                  t_end=OUTBREAK_HORIZON, operator_N_ladder=[10000, 100000]),
)

# =========================================================================== P4
P4 = dict(
    fixed=dict(
        r=1.0, alpha=0.5, c_b=0.3, kappa=0.0, rho=0.0, beta=0.0, eps=1.0,
        initial_law="I1", pulse_angle_deg=0,
        lambda_c=1.958, lambda_fold=1.49,
        f_c={1.60: 0.127, 1.75: 0.038, 1.90: 0.0086},
        f_c_err={1.60: 0.002, 1.75: 0.001, 1.90: 0.0008},
        A_star={1.60: 0.63, 1.75: 0.75, 1.90: 0.81},
        lambda_no_ignition=1.40,
        horizons=[40.0, 80.0, 160.0],
        criterion="A(t) > 1.5 * A_u(lambda) at the horizon",
        criterion_140="A(t) = 0 by t = 160 for every f tested",
        N=50000, replicates=100,
    ),
    declared=dict(
        f_grid={
            1.40: [0.10, 0.25, 0.50, 0.75, 1.00],
            1.60: [0.100, 0.110, 0.118, 0.123, 0.127, 0.131, 0.136, 0.145, 0.160],
            1.75: [0.028, 0.032, 0.035, 0.037, 0.038, 0.039, 0.041, 0.045, 0.052],
            1.90: [0.0050, 0.0065, 0.0075, 0.0082, 0.0086, 0.0090, 0.0098,
                   0.0115, 0.0140],
        },
        t_end=160.0,
        # A6 error source 2 requires an N ladder; A4 fixes the registered cell at
        # N = 5e4, so the second rung is added alongside it, on a reduced grid.
        N_ladder=[50000, 200000],
        ladder_replicates=60,
        ladder_f_grid={
            1.60: [0.118, 0.127, 0.131, 0.136, 0.145],
            1.75: [0.035, 0.038, 0.041, 0.045, 0.052],
            1.90: [0.0065, 0.0075, 0.0086, 0.0098, 0.0115],
        },
        bootstrap_draws=4000,
    ),
)

# =========================================================================== P6
P6 = dict(
    fixed=dict(
        A=dict(alpha=2.0, beta=0.0, r=0.99, lam=3.0, c_b=0.5, rho=0.0, kappa=0.0,
               f=1.0, eps=1.0, initial_law="I1", c_h=0.01,
               crossing_level=0.5603, t_dagger=70.3, t_dagger_err=0.1,
               adiabatic=66.3, adiabatic_error_claim=0.06),
        B=dict(alpha=1.0, beta=0.0, r=0.95, lam=2.5, c_b=0.4, rho=0.0, kappa=0.0,
               f=1.0, eps=1.0, initial_law="I1", c_h=0.01,
               Lambda_exact=25.4, bridge=20.35, adiabatic_error_claim=0.20,
               BLOCKED="needs Appendix C7 for the definition of Lambda and for "
                       "case B's fold activity; neither is in this project"),
        N=100000, replicates=50,
    ),
    declared=dict(t_end_A=140.0, t_end_B=140.0, sample_dt=0.1),
)
