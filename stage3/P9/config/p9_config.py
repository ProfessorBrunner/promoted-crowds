"""Stage 3 item P9 — configuration (two-camp fixed points, R9 / Appendix C C4).

FIXED    = verbatim from design v0.3.1 A4 item P9, A6, or the owner's rulings.
RULED    = supplied by the owner on request where the design is silent.
DECLARED = not fixed by the design; chosen here, logged, fixed before the runs.
"""
MASTER_SEED = 20261005          # DECLARED; distinct from 20261001-20261004

DELTA_TRAJECTORY_FRAC = 0.05    # FIXED by the authorisation: delta = 5%

P9 = dict(
    fixed=dict(
        # design v0.3.1 A4 item P9
        r=1.0, kappa=0.0, alpha=1.0, beta=0.4, M_plus=0.5, eps=1.0,
        lambdas=[1.5, 2.0, 3.0],
        # owner, 2026-10-01
        camp_plus_c=0.6, camp_minus_c=-0.6, stances_aligned=True,
        perturbation=0.05, relax_tol=1e-3, relax_time=10.0,
    ),
    ruled=dict(
        # Design A4 item P9 does not give c_b, and the value is load-bearing: with
        # beta = 0.4, whether ONE rejected message can activate an agent from rest
        # depends on whether c_b is below or above 0.4, and that decides which
        # registered lambda have a positive two-camp branch at all.  At c_b = 0.5
        # the zero branch is stable for lambda < 2/ln2 = 2.885, so lambda = 1.5 and
        # 2 have NO positive fixed point and only lambda = 3 does, at
        # A_+ = A_- = 0.385368902 (exact root of the symmetric branch equation;
        # an earlier chat message to the owner mis-stated this as 0.185 -- the
        # DECIDING fact put to the owner, one live lambda versus three, was and is
        # correct, so the ruling is unaffected).  At c_b = 0.3 all three lambda have
        # a positive stable branch.  Put to the owner with both branch structures
        # computed; ruled 2026-10-02.
        c_b=0.3,
        c_b_ruling="owner 2026-10-02, after both readings were computed and reported",
    ),
    declared=dict(
        # c_h is not named for P9.  Declared 0.01 and verified immaterial: a
        # positive agent's deposits are +alpha (accepted T) and +beta (rejected
        # T_perp), both positive, so conviction never changes sign and no stance
        # ever flips.  Checked at run time (stance flips, sign of c by camp).
        c_h=0.01,
        # rho is not named either.  C4.1: "Reset is harmless under this
        # declaration" -- a reset sends phi to T_s, which it already equals, and
        # the two-camp orientation law is exactly invariant under the message
        # transition (a positive agent rejecting a T_perp message goes to
        # 90 + 90 = 180 = 0).  Declared 0 and the invariance checked at run time.
        rho=0.0,
        N=100000, replicates=50,
        burn_in=50.0,               # to 50/eps, as in P10's declared burn-in
        window=(50.0, 100.0),       # measurement window for (A_+, A_-)
        sample_dt=0.5,
        perturb_sample_dt=0.05,
        N_ladder=[25000, 50000, 100000, 200000],
        ladder_lambda=2.0,
        # Perturbation protocol: to move A_i by +delta, the ceil(delta N) INACTIVE
        # agents of camp i with the largest |c| are set to the median |c| of that
        # camp's active agents; to move it by -delta, ceil(delta N) ACTIVE agents of
        # camp i chosen uniformly at random are set to the median |c| of that camp's
        # inactive agents.  Both produce a genuine O(delta) displacement of A rather
        # than a marginal state that decays instantly.  Feasibility is checked and
        # reported: a +delta move needs at least ceil(delta N) inactive agents in
        # that camp.
        perturb_protocol="median-transfer across the threshold, see config comment",
    ),
)
