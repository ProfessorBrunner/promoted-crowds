"""Reference calculations for the registered quantities of A4 items P1-P6.

Nothing here is tuned and nothing is taken from a simulation.  Where design v0.3
states a number, that number is the registered prediction and is used as given;
the functions below reproduce it from the appendix construction so that the
reproduction can be checked, and supply the quantities the design needs but does
not tabulate (the P1 held-out orders' stance law, and P4's unstable branch A_u).
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy import integrate, optimize

from .angles import cosd, cos2d

LOG2 = math.log(2.0)


# =========================================================== P1 / R8(a) / C3(c)(ii)
def p_plus_campaign(order, alpha=1.0, beta=0.25, r=0.5, c_h=0.01, s0=+1):
    """Direct outcome enumeration of the post-campaign stance law (C3.15).

    I2, zero gaps, so no decay between pulses and the initial orientation enters
    only through the first acceptance coin, whose average over the uniform law is
    exactly 1/2; every later acceptance probability is determined by the earlier
    outcomes because the transition sets phi to theta or theta + 90.
    """
    counts = {}
    paths = [(1.0, None, 0.0, {})]          # weight, phi (None = uniform), c, counters
    for k, th in enumerate(order):
        nxt = []
        for w, phi, c, n in paths:
            pa = 0.5 if phi is None else cosd(th - phi) ** 2
            for acc, pw in ((True, pa), (False, 1.0 - pa)):
                if pw == 0.0:
                    continue
                cls = int(th) % 90
                n2 = dict(n)
                n2[cls] = n2.get(cls, 0) + 1
                dep = (r ** (n2[cls] - 1)) * cos2d(th) * (alpha if acc else -beta)
                c2 = min(1.0, max(-1.0, c + dep))
                nxt.append((w * pw, int(th) % 180 if acc else (int(th) + 90) % 180,
                            c2, n2))
        paths = nxt
    p_plus = 0.0
    for w, phi, c, n in paths:
        if c >= c_h and c <= -c_h:
            s = s0
        elif c >= c_h:
            s = +1
        elif c <= -c_h:
            s = -1
        else:
            s = s0
        counts[round(c, 12)] = counts.get(round(c, 12), 0.0) + w
        if s == +1:
            p_plus += w
    return {"p_plus": p_plus, "x": 2.0 * p_plus - 1.0,
            "final_c_law": dict(sorted(counts.items()))}


def p1_qT_at_delay(order, tau0, rho=1.0, alpha=1.0, beta=0.25, r=0.5, c_h=0.01,
                   c_b=0.5):
    """Exact T-acceptance probability of the prepared background at delay tau0.

    Derived from the same enumeration that reproduces C3.15, plus the reset law:
    with probability exp(-rho tau0) no reset has occurred and the orientation is
    still the post-campaign one; otherwise it is T_s, and the stance cannot have
    changed because the background receives nothing.  Hence

        q_T(tau0) = e^{-rho tau0} E[cos^2 phi_post] + (1 - e^{-rho tau0}) p_+ .

    Every accepted T message clips the listener to c = 1 (the T class is fresh and
    alpha = 1), so the offspring lifetime is log(1/c_b) at every delay; a rejected
    T message deposits -beta and leaves |c| below c_b for every history of this
    campaign, so it never activates.  Therefore R(tau0)/lambda = log(1/c_b) q_T.
    This is a DERIVED reference curve, not a number registered in A4; A4 registers
    only the tau0 -> infinity limit and the ratio 1.97.
    """
    paths = [(1.0, None, 0.0, {})]
    for th in order:
        nxt = []
        for w, phi, c, n in paths:
            pa = 0.5 if phi is None else cosd(th - phi) ** 2
            for acc, pw in ((True, pa), (False, 1.0 - pa)):
                if pw == 0.0:
                    continue
                cls = int(th) % 90
                n2 = dict(n); n2[cls] = n2.get(cls, 0) + 1
                dep = (r ** (n2[cls] - 1)) * cos2d(th) * (alpha if acc else -beta)
                nxt.append((w * pw, int(th) % 180 if acc else (int(th) + 90) % 180,
                            min(1.0, max(-1.0, c + dep)), n2))
        paths = nxt
    Q0 = sum(w * cosd(0 - phi) ** 2 for w, phi, c, n in paths)
    p_plus = sum(w for w, phi, c, n in paths if not (c <= -c_h))
    worst_reject = min(c - beta for w, phi, c, n in paths)
    e = math.exp(-rho * tau0)
    qT = e * Q0 + (1.0 - e) * p_plus
    return {"Q0": Q0, "p_plus": p_plus, "q_T": qT,
            "R_over_lambda": math.log(1.0 / c_b) * qT,
            "rejection_can_activate": bool(abs(worst_reject) > c_b)}


def p1_R_over_lambda(x, c_b=0.5, alpha=1.0, eps=1.0, zeta=1.0):
    """R7 reduced form with beta <= c_b: R_inv = lambda L_alpha (1 + zeta x)/2."""
    L_alpha = math.log(min(alpha, 1.0) / c_b) / eps
    return L_alpha * (1.0 + zeta * x) / 2.0


# ============================================================ P2 / R8(b) / C3(c)(i)
def p2_qT_and_R(order, c_b=0.95):
    """C3.14: Gamma = cos 2 theta_1 prod cos 2(theta_k - theta_{k-1});
    q_T = (1 + Gamma cos 2 theta_3)/2; R_inv = lambda q_T log(1/c_b)."""
    g = cos2d(order[0])
    for k in range(1, len(order)):
        g *= cos2d(order[k] - order[k - 1])
    qT = 0.5 * (1.0 + g * cos2d(order[-1]))
    return {"Gamma": g, "q_T": qT, "R_over_lambda": qT * math.log(1.0 / c_b)}


def p2_qT_I2(c_b=0.95):
    """From I2 the maximally mixed orientation is invariant: q_T = 1/2."""
    return {"q_T": 0.5, "R_over_lambda": 0.5 * math.log(1.0 / c_b)}


# =========================================================== P3 / R8(c) / C3(c)(iii)
_D3 = 0.6 * cosd(40)          # 0.459626666...
_Q3 = cosd(25) ** 2


def p3_post_campaign_law(order):
    """C3.16 / C3.17: the exact post-campaign (phi, c) law."""
    if tuple(order) == (45, 20):
        return [(20, _D3, 0.5), (110, 0.0, 0.5)]
    if tuple(order) == (20, 45):
        return [(45, _D3, _Q3 / 2), (135, _D3, (1 - _Q3) / 2),
                (45, 0.0, (1 - _Q3) / 2), (135, 0.0, _Q3 / 2)]
    raise ValueError(order)


def p3_weights(order):
    """w_H, w_L of C3.18: T-acceptance probability split by deposit group."""
    wH = wL = 0.0
    for phi, c, w in p3_post_campaign_law(order):
        acc = cosd(0 - phi) ** 2
        if c > 0:
            wH += w * acc
        else:
            wL += w * acc
    return wH, wL


def _ell_H(s, c_b=0.5, deposit=0.6, d=_D3):
    return math.log(min(1.0, deposit + d * math.exp(-s)) / c_b)


def p3_reference(order, c_b=0.5):
    """R_fr(0)/lambda, R_inf/lambda and E Z_2/lambda^2 (C3.19-C3.22)."""
    wH, wL = p3_weights(order)
    ell0 = math.log(1.2)
    R_fr0 = wH * _ell_H(0.0) + wL * ell0
    R_inf = 0.5 * math.log(1.2)
    L = math.log(1.0 / c_b)
    val, err = integrate.quad(lambda s: wH * _ell_H(s) + wL * ell0, 0.0, L,
                              epsabs=1e-14, epsrel=1e-13, limit=200)
    return {"w_H": wH, "w_L": wL, "ell_0": ell0, "ell_H0": _ell_H(0.0),
            "R_fr0_over_lambda": R_fr0, "R_inf_over_lambda": R_inf,
            "EZ2_over_lambda2": 0.5 * val, "EZ2_quad_error": 0.5 * err,
            "seed_lifetime": L, "Z1_over_lambda": L * (wH + wL)}


# ====================================================== P4 / R4 class 2 / C2(b)
def _I_step(c, d, a):
    """int_0^{c-d} (d+v)^(-a) v^(a-1) dv, the method-of-steps integral of C2.13.

    The v^(a-1) endpoint singularity (severe for the small a that the unstable
    branch needs) is handled exactly by the algebraic-weight rule rather than by
    adaptive subdivision: substituting v = (c-d) w gives
        (c-d)^a int_0^1 (d + (c-d) w)^(-a) w^(a-1) dw.
    """
    if c <= d:
        return 0.0
    h = c - d
    val = integrate.quad(lambda w: (d + h * w) ** (-a), 0.0, 1.0,
                         weight="alg", wvar=(a - 1.0, 0.0),
                         epsabs=1e-14, epsrel=1e-13, limit=400)[0]
    return h ** a * val


@lru_cache(maxsize=4096)
def P_nu(nu, d, c_b, eps=1.0):
    """Exact stationary activation probability at r = 1 (C2.11-C2.14).

    f_nu(c) = c^(a-1) [C - a int_d^c u^(-a) f_nu(u-d) du],  a = nu/eps,
    normalised on [0, 1]; P_nu = int_{c_b}^1 f_nu.  Valid for d >= 1/2, where the
    method of steps closes after one step -- which covers P4 (d = alpha = 0.5) and
    P6 case A's frozen doses are handled separately.
    """
    a = nu / eps
    assert d >= 0.5, "this implementation closes the steps only for d >= 1/2"
    if a < 1e-9:
        # C2.16 two-term expansion; below this the algebraic-weight rule loses
        # its endpoint exponent to rounding (a - 1 underflows to exactly -1)
        ell = math.log(d / c_b)
        return a * ell + a * a * (math.pi ** 2 / 12.0 - 0.5 * ell * ell)
    # unnormalised f = c^(a-1) * (1 - a I(c))   with C = 1
    mass_low = d ** a / a                                   # int_0^d c^(a-1) dc
    hi = integrate.quad(lambda c: c ** (a - 1.0) * (1.0 - a * _I_step(c, d, a)),
                        d, 1.0, epsabs=1e-13, epsrel=1e-12, limit=400)[0]
    C = 1.0 / (mass_low + hi)
    if c_b >= d:
        tail = integrate.quad(
            lambda c: c ** (a - 1.0) * (1.0 - a * _I_step(c, d, a)),
            c_b, 1.0, epsabs=1e-13, epsrel=1e-12, limit=400)[0]
    else:
        tail = (d ** a - c_b ** a) / a + hi
    return C * tail


def p4_lambda_of_nu(nu, d=0.5, c_b=0.3, eps=1.0, M=1.0):
    """C2.15: lambda(nu) = nu / (M P_nu)."""
    return nu / (M * P_nu(nu, d, c_b, eps))


def p4_fold(d=0.5, c_b=0.3, eps=1.0, M=1.0):
    """The saddle-node of lambda(nu): lambda_fold and the activity there."""
    res = optimize.minimize_scalar(
        lambda ln_nu: p4_lambda_of_nu(math.exp(ln_nu), d, c_b, eps, M),
        bounds=(math.log(1e-6), math.log(50.0)), method="bounded",
        options={"xatol": 1e-11})
    nu_f = math.exp(res.x)
    return {"lambda_fold": float(res.fun), "nu_fold": nu_f,
            "A_fold": P_nu(nu_f, d, c_b, eps) * M}


def p4_branches(lam, d=0.5, c_b=0.3, eps=1.0, M=1.0):
    """Unstable (A_u) and stable (A*) roots of A = M P_{lambda A}."""
    fold = p4_fold(d, c_b, eps, M)
    if lam < fold["lambda_fold"]:
        return {"A_u": None, "A_star": None, "fold": fold}

    def g(nu):
        return p4_lambda_of_nu(nu, d, c_b, eps, M) - lam

    nu_f = fold["nu_fold"]
    out = {"fold": fold}
    lo = 1e-5
    while g(lo) <= 0.0 and lo > 1e-12:
        lo /= 10.0
    try:
        nu_u = optimize.brentq(g, lo, nu_f, xtol=1e-14, rtol=8.9e-16)
        out["A_u"] = nu_u / lam
        out["nu_u"] = nu_u
    except ValueError:
        out["A_u"] = None
    hi = nu_f
    while g(hi) < 0 and hi < 1e4:
        hi *= 2.0
    try:
        nu_s = optimize.brentq(g, nu_f, hi, xtol=1e-14, rtol=8.9e-16)
        out["A_star"] = nu_s / lam
        out["nu_star"] = nu_s
    except ValueError:
        out["A_star"] = None
    return out


def p4_lambda_c(d=0.5, c_b=0.3, eps=1.0, M=1.0):
    """R4 class 2: transcritical point at lambda M ell = 1, ell = ln(alpha/c_b)."""
    ell = math.log(d / c_b) / eps
    return {"ell": ell, "lambda_c": 1.0 / (M * ell)}


# ======================================================================== P6 / C7
P6 = {
    "A": dict(alpha=2.0, beta=0.0, r=0.99, lam=3.0, c_b=0.5, rho=0.0, kappa=0.0,
              f=1.0, eps=1.0, initial_law="I1",
              crossing_level=0.5603,          # A4: "first downward crossing of A_f"
              t_dagger=70.3, t_dagger_err=0.1,
              adiabatic=66.3, adiabatic_error_claim=0.06),
    "B": dict(alpha=1.0, beta=0.0, r=0.95, lam=2.5, c_b=0.4, rho=0.0, kappa=0.0,
              f=1.0, eps=1.0, initial_law="I1",
              Lambda_exact=25.4, bridge=20.35, adiabatic_error_claim=0.20),
}
