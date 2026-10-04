"""Stage 3 item P5 — configuration.

FIXED    = verbatim from design v0.3.1 Part A (A4 item P5, A4a, A4b, A6), or from
           the owner's Stage 3 P5 estimand definitions of 2026-10-01.  Never altered.
DECLARED = not fixed by the design; chosen here, logged, fixed before the runs.

Governing design: crowd1_cs_design_and_manuscript_brief_v0_3_1.md (supersedes v0.3).
Specification: review_packet_v0_6_1.md, memo section "PROCESS SPECIFICATION v0.6".
Appendices E and F (crowd1_appendices_EF_C7_C9.md) supply C7-C9.

Authorisation (2026-10-01): "Stage 3, P5 authorized: survival means A(20) > 0;
burn-in [0, 20], observation window [20, 70]; active-branch statistics conditioned
on A(20) > 0 and reported with the survival fraction.  Write to Crowd1/stage3/P5,
report, and stop.  P7, P8, P9 and P10 are not authorized."
"""

MASTER_SEED = 20261003          # DECLARED; distinct from Stage 1 (20261001) and
                                # Stage 2 / 2B (20261002)

# ---- A6 discrepancy categories (FIXED by A6 / A4a / A4b)
DELTA_TRAJECTORY_FRAC = 0.05    # stationary active fractions are trajectory markers
DELTA_ZERO_ABS = 1e-3           # A4a: A_max, I, T_act = 0 predictions
DELTA_OUTBREAK_ABS = 0.03       # A4a: precision target for outbreak probabilities
                                # where no number is predicted -- NOT a tolerance

# ---- A4a observation horizon for the outbreak endpoint (FIXED)
OUTBREAK_HORIZON = 50.0
OUTBREAK_FRACTION = 0.01        # ever-active fraction > 1% of N

P5 = dict(
    fixed=dict(
        # design v0.3.1 A4, item P5
        r=1.0, alpha=2.0, beta=0.0, c_b=0.5, kappa=0.0, rho=0.0, eps=1.0,
        initial_law="I1", pulse_angle=0,      # one pulse at the target T_+ = 0 deg
        lambdas=[1.0, 2.0],
        reaches=[0.01, 0.10],
        N=100000, replicates=50,
        # registered predictions
        A_star_at_lambda2=0.5,                # exact: A* = 1 - exp(-lambda L A*)
        L=None,                               # computed = ln(1/c_b) = ln 2
        dies_at_lambda1=True,                 # lambda L = ln 2 < 1
        # owner's Stage 3 P5 estimand definitions, 2026-10-01
        burn_in_end=20.0,
        window=(20.0, 70.0),
        survival_definition="A(20) > 0",
    ),
    declared=dict(
        # c_h is not named for P5 in A4.  Declared 0.01, matching every other item
        # that does name it.  IMMATERIAL here and verified so at run time: with
        # beta = 0, I1 (phi = T_+) and a T_+ pulse, every message is accepted and
        # every deposit is +alpha cos 0 = +2, so no conviction is ever negative and
        # no stance ever leaves +.
        c_h=0.01,
        t_end=70.0,              # the observation window closes at 70
        sample_dt=0.01,          # activity sampling grid; refined below
        sample_dt_ladder=[0.04, 0.02, 0.01],
        N_ladder=[25000, 50000, 100000, 200000],   # A6 error source 2
        # A4a's outbreak definition is degenerate for P5 (see AMBIGUITIES P5-A2):
        # at f = 0.01 the cohort is already 1% of N and every cohort member
        # activates, so "ever-active > 1% of N" is decided by the campaign itself.
        # Both it and the owner's survival criterion are reported, under their
        # own names, with no verdict on the former (A4a: no number is predicted).
        outbreak_extra_replicates=400,
    ),
)
