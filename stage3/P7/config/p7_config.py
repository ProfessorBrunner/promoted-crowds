"""Stage 3 item P7 — configuration.

FIXED    = verbatim from design v0.3.1 Part A (A4 item P7, A4a, A4b, A6), from
           Appendix E section C9(a), or from the owner's rulings of 2026-10-01.
DECLARED = not fixed by the design; chosen here, logged, fixed before the runs.

Governing design: crowd1_cs_design_and_manuscript_brief_v0_3_1.md.
Specification:    review_packet_v0_6_1.md, "PROCESS SPECIFICATION v0.6".
Appendices:       crowd1_appendices_EF_C7_C9.md, Appendix E section C9(a).

Owner's rulings of 2026-10-01 that govern this item:
  (1) Outbreak criterion, from now on: the ever-active fraction among agents
      OUTSIDE the campaign cohort exceeds 1% of N within the horizon.
  (2) A_max and T_act: the registered endpoint is the MEAN-TRAJECTORY value
      (the Appendix E enclosures are mean-field); the per-replicate average is
      reported beside it as a finite-N diagnostic WITHOUT a verdict.  I is
      reported once (linear in A).
  Point predictions at delta = 2%.
"""

MASTER_SEED = 20261004          # DECLARED; distinct from Stage 1 (20261001),
                                # Stage 2 / 2B (20261002), Stage 3 P5 (20261003)

DELTA_POINT_FRAC = 0.02         # FIXED by the authorisation: point predictions
DELTA_ZERO_ABS = 1e-3           # A4a: A_max, I, T_act = 0 predictions
OUTBREAK_FRACTION = 0.01        # ruling (1): > 1% of N, counted OUTSIDE the cohort
OUTBREAK_HORIZON = 50.0         # A4a

P7 = dict(
    fixed=dict(
        alpha=1.0, beta=0.4, r=1e-6, lam=0.5, eps=1.0, c_b=0.5, c_h=0.01,
        rho=0.0, kappa=0.0, initial_law="I1",
        reaches=[0.10, 0.25, 0.50, 0.75],
        N=100000, replicates=50,
        # Appendix E C9(a) reach table, registered in design v0.3.1 A4 as the
        # point predictions.  (A_max, I, T_act)
        reach_table={0.10: (0.13580, 0.09963, 0.69315),
                     0.25: (0.32038, 0.22969, 0.69315),
                     0.50: (0.58579, 0.41095, 0.69315),
                     0.75: (0.80926, 0.56233, 0.69315)},
        # two coincident pulses {T, T_perp}; design A4: (T, T_perp) reproduces the
        # single-pulse values, (T_perp, T) gives zero
        pulse_T=0, pulse_Tperp=90,
    ),
    declared=dict(
        # Sampling grid.  A(t) rises strictly on [0, L) and every cohort member
        # shuts off in [L, L_plus] (a window of width 2e-6), so A_max = A(L-) and
        # the crossing of A_max/2 is a jump at L.  A fine grid is needed only
        # around that; the tail matters for I, which is NOT taken from the grid --
        # the engine accumulates the exact int A dt event by event.
        fine_dt=1e-4, fine_end=2.0,
        coarse_dt=0.01, t_end=50.0,
        fine_dt_ladder=[4e-4, 2e-4, 1e-4],
        N_ladder=[25000, 50000, 100000, 200000],
        ladder_reach=0.25,
    ),
)
