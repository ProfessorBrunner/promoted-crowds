"""Reference calculations for the registered quantities of acceptance tests T1-T6.

Every function here computes the quantity the DESIGN registers, from the design
and the appendices of review_packet_v0_6_1.md.  No value is taken from a
simulation.  Each returns, with the value, the numerical error of the reference
calculation itself (A6 error source 3).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq
from scipy.stats import poisson

from .angles import cosd, cos2d


# ---------------------------------------------------------------------- T1
def lifetime_L(eps: float, c_b: float) -> float:
    """L = eps^-1 ln(1/c_b)   (specification v0.6 AGGREGATES)."""
    return math.log(1.0 / c_b) / eps


def lifetime_Lplus(eps: float, c_b: float, r: float) -> float:
    """L_+ = eps^-1 ln(1/(c_b - r/(1-r)))  (design A2, T1).

    Upper bound on the time of last activity measured from first activation:
    after the activating dose alpha = 1, every further receipt in the single
    class deposits at most r^(n-1) <= r for n >= 2, so the total extra
    conviction a listener can ever hold above the decayed first dose is at most
    sum_{k>=1} r^k = r/(1-r).  Activity therefore requires
    exp(-eps t) > c_b - r/(1-r).
    """
    denom = c_b - r / (1.0 - r)
    if denom <= 0.0:
        return math.inf
    return math.log(1.0 / denom) / eps


def final_size_Z(f: float, lam: float, duration: float):
    """Root of 1 - Z = (1 - f) exp(-lambda * duration * Z)  (design A2, T1; R6)."""
    def g(Z):
        return 1.0 - Z - (1.0 - f) * math.exp(-lam * duration * Z)
    lo, hi = f, 1.0 - 1e-16
    if g(lo) * g(hi) > 0:
        # no interior root above the trivial one: Z = f is the only solution
        return f, 0.0
    Z = brentq(g, lo, hi, xtol=1e-16, rtol=8.9e-16, maxiter=300)
    # numerical error: |g(Z)| / |g'(Z)|
    gp = -1.0 + (1.0 - f) * lam * duration * math.exp(-lam * duration * Z)
    num_err = abs(g(Z)) / abs(gp) if gp != 0.0 else 0.0
    return Z, num_err


def t1_prediction(f, lam, eps, c_b, r):
    """Returns the mean-field final size with its small-r closure bracket.

    The registered equation 1 - Z = (1-f) exp(-lambda L Z) is the r -> 0 limit
    (R6, C2.23), in which every first-exposed agent is active for EXACTLY L.
    At r > 0 each agent's active duration D lies in [L, L_+] (see lifetime_Lplus),
    and the limiting relation holds with lambda D Z in the exponent.  The pair
    (Z(L), Z(L_+)) is therefore a rigorous enclosure of the small-r
    approximation error -- A6 error source 4 for this test.
    """
    L = lifetime_L(eps, c_b)
    Lp = lifetime_Lplus(eps, c_b, r)
    Z_L, e1 = final_size_Z(f, lam, L)
    Z_Lp, e2 = final_size_Z(f, lam, Lp)
    return {
        "L": L,
        "L_plus": Lp,
        "Lplus_minus_L": Lp - L,
        "Z": Z_L,
        "Z_at_Lplus": Z_Lp,
        "closure_error": abs(Z_Lp - Z_L),
        "numerical_error": max(e1, e2),
    }


# ---------------------------------------------------------------------- T2
def t2_prediction(lam, eps, c_b):
    """A* root of A = 1 - exp(-lambda L A)   (design A2, T2; R6; C2.24)."""
    L = lifetime_L(eps, c_b)

    def g(A):
        return 1.0 - math.exp(-lam * L * A) - A

    if lam * L <= 1.0:
        return {"L": L, "lamL": lam * L, "A_star": 0.0, "numerical_error": 0.0}
    A = brentq(g, 1e-12, 1.0 - 1e-16, xtol=1e-16, rtol=8.9e-16, maxiter=300)
    gp = lam * L * math.exp(-lam * L * A) - 1.0
    return {"L": L, "lamL": lam * L, "A_star": A,
            "numerical_error": abs(g(A)) / abs(gp) if gp != 0 else 0.0}


# ---------------------------------------------------------------------- T3
def t3_counter_law(Lambda, kmax):
    """Law of the class counter after one pulse: 1 + Poisson(Lambda)."""
    k = np.arange(0, kmax + 1)
    pmf = poisson.pmf(k, Lambda)
    return k + 1, pmf


# ------------------------------------------------------------------ T4 / T6
def _orientation_law(initial_law, p_plus=None, rho=None, kappa=None, delta=None):
    """Return [(phi_deg, weight), ...] for the declared initial orientation law.

    I2 is the uniform law on the 180 integer-degree rays (see runner.py).
    """
    if initial_law == "I1":
        return [(0, 1.0)]
    if initial_law == "I2":
        return [(d, 1.0 / 180.0) for d in range(180)]
    if initial_law == "I3":
        v = rho + kappa
        w_t = rho / v
        w_d = kappa / (2.0 * v)
        out = []
        for s_sign, p_s in ((+1, p_plus), (-1, 1.0 - p_plus)):
            base = 0 if s_sign == 1 else 90
            out.append(((base) % 180, p_s * w_t))
            out.append(((base + delta) % 180, p_s * w_d))
            out.append(((base - delta) % 180, p_s * w_d))
        return out
    raise ValueError(initial_law)


def q1_expectation(theta1, law):
    """E[cos^2(theta1 - phi0)] under the initial orientation law."""
    return sum(w * cosd(theta1 - phi) ** 2 for phi, w in law)


def tau1_sq_expectation(theta1, law):
    """E[tau_1^2] with tau_1 = cos 2(theta1 - a0) and a0 = phi0 (pure-state lift)."""
    return sum(w * cos2d(theta1 - phi) ** 2 for phi, w in law)


def t4_process_joint(theta1, theta2, law):
    """Exact joint law of the two pulse outcomes for the process (and automaton).

    MESSAGE TRANSITION step (1): after accepting theta1 the orientation is
    theta1, after rejecting it is theta1 + 90 deg.  Hence
        P(A2 | A1) = cos^2(theta2 - theta1),  P(A2 | R1) = sin^2(theta2 - theta1),
    so  P(AA) + P(RR) = q1 cos^2 D + (1 - q1) cos^2 D = cos^2 D,
    independent of the initial law and of the order -- the identity T4 registers.
    """
    q1 = q1_expectation(theta1, law)
    D = theta2 - theta1
    cD2 = cosd(D) ** 2
    sD2 = 1.0 - cD2
    return {
        "q1": q1,
        "P_AA": q1 * cD2,
        "P_AR": q1 * sD2,
        "P_RA": (1.0 - q1) * sD2,
        "P_RR": (1.0 - q1) * cD2,
        "P_same": cD2,
        "cos2Delta": cD2,
    }


def t6_surrogate_joint(theta1, theta2, law):
    """Exact joint law for the Bloch-mean surrogate of C5.0 / design A2 T6.

    tau <- tau cos 2(theta - a); a <- theta; response coin (1 + tau)/2 drawn
    AFTER the update and with no outcome-dependent update.  With tau_0 = 1 and
    a_0 = phi_0 the two coins are conditionally independent given phi_0, with
        p1 = (1 + tau1)/2,  p2 = (1 + tau1 cos 2D)/2,  tau1 = cos 2(theta1 - a0),
    so  P(same) = (1 + cos 2D E[tau1^2]) / 2, which is the registered formula.
    """
    D = theta2 - theta1
    c2D = cos2d(D)
    P = {"P_AA": 0.0, "P_AR": 0.0, "P_RA": 0.0, "P_RR": 0.0}
    for phi, w in law:
        tau1 = cos2d(theta1 - phi)
        p1 = 0.5 * (1.0 + tau1)
        p2 = 0.5 * (1.0 + tau1 * c2D)
        P["P_AA"] += w * p1 * p2
        P["P_AR"] += w * p1 * (1.0 - p2)
        P["P_RA"] += w * (1.0 - p1) * p2
        P["P_RR"] += w * (1.0 - p1) * (1.0 - p2)
    Et2 = tau1_sq_expectation(theta1, law)
    P["E_tau1_sq"] = Et2
    P["P_same"] = P["P_AA"] + P["P_RR"]
    P["P_same_formula"] = 0.5 * (1.0 + c2D * Et2)
    P["cos2Delta"] = cosd(D) ** 2
    return P


# ---------------------------------------------------------------------- T5
def t5_process_prediction():
    """I2, zero-gap campaign (T, T); C5(a) parameters.

    First outcome has probability cos^2(phi_0) of acceptance; the second is
    perfectly repeatable because the post-outcome orientation is exactly
    aligned (0 deg) or exactly orthogonal (90 deg) to T.  Hence
    P(AA) = E[cos^2 phi0] = 1/2, P(RR) = 1/2, P(AR) = P(RA) = 0 pathwise,
    final convictions +0.9 and -0.3, so x = 0.
    """
    return {"P_AA": 0.5, "P_RR": 0.5, "P_AR": 0.0, "P_RA": 0.0,
            "x": 0.0, "c_AA": 0.9, "c_RR": -0.3}


def t5_surrogate_prediction():
    """Same campaign for the pure-state-lift surrogate (C5.2).

    Both coins equal q = cos^2(phi0) and are independent, so
    P(AA) = P(RR) = E[q^2] = 3/8, P(AR) = P(RA) = E[q(1-q)] = 1/8; the mixed
    histories finish at c = +0.5 and +0.1, both positive, so x = 1/4.
    """
    return {"P_AA": 3.0 / 8.0, "P_RR": 3.0 / 8.0, "P_AR": 1.0 / 8.0,
            "P_RA": 1.0 / 8.0, "x": 0.25,
            "c_AA": 0.9, "c_RR": -0.3, "c_AR": 0.5, "c_RA": 0.1}
