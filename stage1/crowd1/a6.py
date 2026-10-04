"""Design section A6: the pass rule and the separated error accounting.

A6 verbatim: "For each registered quantity, a discrepancy delta is predeclared
(default 2% of the predicted value for operator checks; +-0.03 absolute for
outbreak probabilities; 5% for trajectory markers).  The simulation-minus-
prediction difference is estimated with its confidence interval; PASS if the
interval lies inside [-delta, delta]; FAIL if it lies outside; INCONCLUSIVE
otherwise, with the replicate count needed to resolve.  Four error sources are
reported separately: Monte Carlo, finite-N bias relative to the mean-field
prediction (from the N ladder), numerical error of the theoretical calculation
(from the quadrature's own convergence), and closure error (adiabatic versus
kinetic)."

Reading used here, stated once so it can be audited:
  * "the interval lies outside [-delta, delta]" is read as *disjoint from*
    [-delta, delta].  PASS = contained, FAIL = disjoint, INCONCLUSIVE = overlaps
    without being contained.  This is the only reading under which the three
    outcomes partition the possibilities.
  * The interval is a two-sided 95% confidence interval for the mean
    discrepancy across replicates (Student t with n-1 degrees of freedom), so
    it carries both within-replicate and between-replicate Monte Carlo error.
    For a quantity measured in a single run the Wilson score interval is used
    and that is stated in the row.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np
from scipy import stats

PASS, FAIL, INCONCLUSIVE = "PASS", "FAIL", "INCONCLUSIVE"


@dataclass
class Verdict:
    name: str
    predicted: float
    measured: float
    diff: float
    ci_lo: float
    ci_hi: float
    delta: float
    delta_basis: str
    status: str
    n_replicates: int
    N: int
    replicates_needed: int | None
    mc_error: float
    finite_N_bias: float | None
    numerical_error: float
    closure_error: float | None
    interval_kind: str
    note: str = ""

    def row(self):
        return asdict(self)


def t_interval(values, conf=0.95):
    """Two-sided Student-t interval for the mean of `values`."""
    v = np.asarray(values, dtype=float)
    n = v.size
    m = float(v.mean())
    if n < 2:
        return m, m, m, 0.0
    sd = float(v.std(ddof=1))
    hw = float(stats.t.ppf(0.5 + conf / 2.0, n - 1) * sd / math.sqrt(n))
    return m, m - hw, m + hw, hw


def wilson_interval(k, n, conf=0.95):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0, 1.0, 0.5
    z = stats.norm.ppf(0.5 + conf / 2.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h, h


def decide(ci_lo, ci_hi, delta):
    if ci_lo >= -delta and ci_hi <= delta:
        return PASS
    if ci_lo > delta or ci_hi < -delta:
        return FAIL
    return INCONCLUSIVE


def replicates_to_resolve(diff, half_width, delta, n):
    """Replicate count that would resolve an INCONCLUSIVE verdict.

    If |diff| < delta the test can resolve to PASS once the half-width is below
    delta - |diff|; if |diff| > delta it can resolve to FAIL once the half-width
    is below |diff| - delta.  Monte Carlo half-width scales as n^(-1/2).
    """
    ad = abs(diff)
    if ad < delta:
        target = delta - ad
    elif ad > delta:
        target = ad - delta
    else:
        return None  # |diff| == delta exactly: no finite replicate count resolves
    if target <= 0 or half_width <= 0:
        return None
    return int(math.ceil(n * (half_width / target) ** 2))


def make_verdict(name, predicted, per_replicate_values, delta, delta_basis, N,
                 numerical_error=0.0, closure_error=None, finite_N_bias=None,
                 note="", interval_kind="student-t across replicates",
                 single_run=None):
    """Build an A6 verdict row.

    `per_replicate_values` are the per-replicate measurements of the quantity.
    `single_run` = (k, n) uses a Wilson interval on a single pooled proportion
    instead (stated in the row).
    """
    if single_run is not None:
        k, n = single_run
        m, lo, hi, hw = wilson_interval(k, n)
        nrep = 1
        interval_kind = "Wilson score, pooled"
    else:
        vals = np.asarray(per_replicate_values, dtype=float)
        nrep = int(vals.size)
        m, lo, hi, hw = t_interval(vals)
    diff = m - predicted
    dlo, dhi = lo - predicted, hi - predicted
    status = decide(dlo, dhi, delta)
    need = None
    if status == INCONCLUSIVE:
        need = replicates_to_resolve(diff, hw, delta, nrep)
    return Verdict(
        name=name, predicted=float(predicted), measured=float(m), diff=float(diff),
        ci_lo=float(dlo), ci_hi=float(dhi), delta=float(delta),
        delta_basis=delta_basis, status=status, n_replicates=nrep, N=int(N),
        replicates_needed=need, mc_error=float(hw),
        finite_N_bias=(None if finite_N_bias is None else float(finite_N_bias)),
        numerical_error=float(numerical_error),
        closure_error=(None if closure_error is None else float(closure_error)),
        interval_kind=interval_kind, note=note,
    )


def finite_N_bias_from_ladder(ladder):
    """A6 error source 2.

    `ladder` is [(N, mean_estimate), ...] with N increasing.  Reports the
    difference between the two largest N (the directly observed residual bias
    scale at the top of the ladder) and, when three or more rungs are present,
    a Richardson extrapolation in 1/N.
    """
    ladder = sorted(ladder)
    out = {"ladder": [(int(n), float(v)) for n, v in ladder]}
    if len(ladder) >= 2:
        out["top_gap"] = abs(ladder[-1][1] - ladder[-2][1])
    if len(ladder) >= 3:
        x = np.array([1.0 / n for n, _ in ladder])
        y = np.array([v for _, v in ladder])
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        out["extrapolated_Ninf"] = float(coef[0])
        out["slope_per_inverse_N"] = float(coef[1])
        out["residual_bias_at_Nmax"] = float(abs(ladder[-1][1] - coef[0]))
    return out
