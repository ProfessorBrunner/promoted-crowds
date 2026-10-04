RETAINED ORIGINAL RESULTS — Stage 2 archive version s2-v1 (A6: "corrections are
versioned and original results retained").

Run of 2026-10-01, master seed 20261002.
Verdict: P1 PASS, P1-delay INCONCLUSIVE, P2 PASS, P2-delay FAIL, P3 PASS,
P4 FAIL, P6 PASS (case A; case B BLOCKED).

The two FAILs are both traceable to one HARNESS defect (bug B3 in ../BUGLOG.md):
six rows were reported as POINT comparisons with ci_lo = ci_hi = diff, i.e. with
no confidence interval, which A6 requires ("The simulation-minus-prediction
difference is estimated with its confidence interval").  Without an interval the
A6 rule can only return PASS or FAIL and can never return INCONCLUSIVE.  The rows
are: P4 f_c at lambda = 1.60 / 1.75 / 1.90, P2-delay rho = 0 persistence,
P2-delay rho = 0.5 decay, P1-delay orientation decay.

P4 additionally had NO N ladder, so A6 error source 2 (finite-N bias relative to
the mean-field prediction) was reported as unavailable on exactly the rows where
the ignition-probability curve shows it is the dominant effect: at lambda = 1.90,
N = 5e4 puts only ~430 agents in the cohort and the measured ignition curve runs
from p = 0.13 at f = 0.005 to p = 1.00 at f = 0.014.

These results are retained unchanged.  No parameter, prediction or tolerance of
design v0.3 was altered in the correction; v2 adds the missing intervals and the
missing N ladder and re-decides the same rows under the same rule.
