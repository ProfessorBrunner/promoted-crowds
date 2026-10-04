"""Declared configuration of CROWD-1 Stage 1 (acceptance tests T1-T6).

Every entry is marked FIXED (taken verbatim from design v0.3 Part A, or from the
appendix of review_packet_v0_6_1.md that the design points to) or DECLARED
(not fixed by the design; chosen here, logged, and never changed after a run).
No FIXED value is altered anywhere in this archive.

Seeds: one master seed; every per-run seed is
    derive_run_seed(MASTER_SEED, test_id, cell_id, replicate_index)
and every kernel stream is seeded from the run seed by stream id (rng.py).
"""

MASTER_SEED = 20261001          # DECLARED: the staged-approval date 2026-10-01

# A6 discrepancy categories, as predeclared for Stage 1.  See README section
# "A6 delta assignment" and AMBIGUITIES.md item 5.
DELTA_TRAJECTORY_FRAC = 0.05    # FIXED (A6): 5% for trajectory markers
DELTA_OPERATOR_FRAC = 0.02      # FIXED (A6): 2% for operator checks
DELTA_X_ZERO_ABS = 0.01         # FIXED (A4a): |x| <= 0.01 for x = 0


def delta_t4(N):
    """FIXED (A2, T4): 'within 3/sqrt(N)'."""
    return 3.0 / N ** 0.5


# --------------------------------------------------------------------- T1
T1 = dict(
    fixed=dict(alpha=1.0, r=1e-6, eps=1.0, c_b=0.5, initial_law="I1",
               n_pulses=1, pulse_angle_deg=0, single_class=True),
    declared=dict(
        beta=0.0,        # inert: an aligned listener at phi = 0 never rejects theta = 0
        c_h=0.01,        # inert: conviction never becomes negative in this corner
        rho=0.0, kappa=0.0,
        t_end=200.0,
        cells=[dict(name="A", lam=3.0, f=0.10),
               dict(name="B", lam=2.0, f=0.30)],
        ladder=[1000, 10000, 100000],
        replicates={1000: 50, 10000: 50, 100000: 20},
        zero_lambda=dict(N=10000, replicates=10, f=1.0, t_end=5.0),
    ),
)

# --------------------------------------------------------------------- T2
T2 = dict(
    fixed=dict(r=1.0, alpha=1.0, beta=1.0, lam=2.0, eps=1.0, c_b=0.5,
               A_star=0.5, two_camps=True),
    declared=dict(
        c_h=0.01, rho=0.0, kappa=0.0, M_plus=0.5,
        t_measure_start=20.0, t_end=70.0,
        ladder=[1000, 10000, 100000],
        replicates={1000: 50, 10000: 50, 100000: 20},
    ),
)

# --------------------------------------------------------------------- T3
T3 = dict(
    fixed=dict(counter_law="1 + Poisson(integral of prescribed intensity)",
               full_system_law="1 + Poisson(lambda * integral A_j)",
               full_system_is_convergence_check_only=True),
    declared=dict(
        # (a) prescribed Poisson message input of known intensity
        a=dict(N=100000, replicates=10, eps=1.0, c_b=0.95, c_h=0.01,
               alpha=0.6, beta=0.2, r=0.5, lam=0.0, rho=0.0, kappa=0.0, f=1.0,
               pulse_angle_deg=0, exo_angle_deg=0,
               exo_rate_fn="exp_decay", exo_nu0=3.0, exo_gamma=0.5, exo_T=20.0),
        # (c) full-system convergence check, run in the T1 cell-A setting
        c=dict(ladder=[1000, 10000, 100000], replicates=20, cell="A"),
    ),
)

# --------------------------------------------------------------------- T4 / T6
T4 = dict(
    fixed=dict(deltas_deg=[15, 30, 45, 60, 75], both_orders=True,
               initial_laws=["I1", "I2", "I3"], i3_x=0.6,
               identity="P(AA) + P(RR) = cos^2(Delta)",
               tolerance="3/sqrt(N)"),
    declared=dict(
        N=100000, replicates=20,
        theta1_deg=0,       # so that I1's anchor T_+ = 0 is aligned with theta_1
        alpha=0.6, beta=0.2, r=0.5, c_b=0.95, c_h=0.01, eps=1.0, lam=0.0, f=1.0,
        i3_rho=1.0, i3_kappa=0.5, i3_delta_deg=30, i3_relax_factor=20.0,
        agent_classes=["process", "automaton", "surrogate"],
        a5_replicates=5,   # shared-seed pathwise pairs per cell (A5 control)
        t_end=0.0,
    ),
)

# --------------------------------------------------------------------- T5
T5 = dict(
    fixed=dict(initial_law="I2", campaign=[(0.0, 0), (0.0, 0)],
               process_P_AR=0.0, process_P_RA=0.0, process_x=0.0,
               surrogate_x=0.25),
    declared=dict(
        # C5(a) parameter set, which the appendix declares for this test
        N=100000, replicates=20,
        alpha=0.6, beta=0.2, r=0.5, c_b=0.95, c_h=0.01, eps=1.0,
        lam=0.0, rho=0.0, kappa=0.0, f=1.0, t_end=0.0,
        agent_classes=["process", "automaton", "surrogate"],
    ),
)
