"""Dose-mixture fold for P6 case A (C7(c)), computed in CS for the first time.

Case A: alpha = 2, beta = 0, r = 0.99, lambda = 3, eps = 1, c_b = 0.5,
rho = kappa = 0, f = 1, one T pulse from I1 (c(0) = 1, n(0) = 1, eta = 0.03).

C7(b)/C7(c) give the frozen-mixture map and the fold:

    w_n(H)   = (1-f) e^{-H} H^n/n! + f 1_{n>=1} e^{-H} H^{n-1}/(n-1)!
    F(A, H)  = sum_n w_n(H) P_{lambda A}(alpha r^n)
    fold     : F(A_f, H_f) = A_f  and  d/dA F(A_f, H_f) = 1
    t_ad,f   = int_0^{H_f} du / (lambda A_+(u))

P_nu(d) is the clipped r = 1 stationary activation probability of C2.11-C2.14.

WHY THIS FILE EXISTS RATHER THAN A CALL INTO THE EXISTING QUADRATURE
--------------------------------------------------------------------
Both stationary quadratures already in the project close the method of steps
after ONE step and are therefore restricted to d >= 1/2:

    stage2b/fold_exact.py       P_nu_exact  -- "Because d = 0.5 there are
                                exactly TWO steps on (0, 1)"
    stage2/crowd1/predictions_s2.py  P_nu   -- asserts d >= 0.5, docstring
                                "P6 case A's frozen doses are handled
                                separately"

At the manuscript's H_f = 158.354403 the mixture is supported on doses
alpha r^n in [0.245, 0.669] (n within 4 sd of 1 + Poisson(H)), so most of the
mass lies below d = 1/2 and neither routine can be called.  P_stat below is the
SAME C2.11-C2.14 recursion carried to K = ceil(1/d) steps instead of two; it is
checked against both of the above wherever they are valid, and against the
closed form P = 1 - c_b^a that holds exactly for d >= 1.

Singular factors are removed by substitution before any numerical rule, as in
fold_exact.py, and every reported number carries a node-ladder error estimate.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = os.path.dirname(os.path.abspath(__file__))

ALPHA, BETA, R, LAM, EPS, C_B, F_REACH = 2.0, 0.0, 0.99, 3.0, 1.0, 0.5, 1.0
MANUSCRIPT = dict(A_f=0.5603318, H_f=158.354403, t_ad_f=66.30915)

_GRADE = 3          # c = b_k + Delta w^_GRADE, smooths the (c-b_k)^a kink
_CHEB_CACHE: dict[int, tuple] = {}
_GL_CACHE: dict[int, tuple] = {}


def _cheb(M):
    """Chebyshev-Lobatto nodes on [0, 1] plus barycentric weights."""
    if M not in _CHEB_CACHE:
        j = np.arange(M + 1)
        w = 0.5 * (1.0 - np.cos(np.pi * j / M))
        bw = (-1.0) ** j
        bw[0] *= 0.5
        bw[-1] *= 0.5
        _CHEB_CACHE[M] = (w, bw)
    return _CHEB_CACHE[M]


def _gl(N):
    if N not in _GL_CACHE:
        x, w = leggauss(N)
        _GL_CACHE[N] = (0.5 * (x + 1.0), 0.5 * w)
    return _GL_CACHE[N]


def _bary(wq, nodes, bw, vals):
    """Barycentric interpolation of vals(nodes) at wq (1-D)."""
    diff = wq[:, None] - nodes[None, :]
    exact = np.isclose(diff, 0.0, atol=0.0)
    diff[exact] = 1.0
    num = (bw / diff) @ vals
    den = (bw / diff).sum(axis=1)
    out = num / den
    if exact.any():
        i, j = np.nonzero(exact)
        out[i] = vals[j]
    return out


def P_stat(a, d, c_b=C_B, M=32, N=256):
    """Clipped r = 1 stationary P(c > c_b) at a = nu/eps and dose d (C2.11-C2.14).

    Exact method of steps carried to K = ceil(1/d) steps.  M Chebyshev-Lobatto
    nodes per step, N Gauss-Legendre nodes per inner integral.
    """
    if d >= 1.0:                                   # every jump clips to 1
        return 1.0 - c_b ** a
    K = int(math.ceil(1.0 / d))
    wn, bw = _cheb(M)
    s, gw = _gl(N)
    p = _GRADE

    A_nodes = []                                   # A_k at this step's nodes
    for k in range(K):
        lo = k * d
        hi = min((k + 1) * d, 1.0)
        dl = hi - lo
        c = lo + dl * wn ** p                      # graded physical nodes
        if k == 0:
            A_nodes.append(np.ones_like(c))
            continue
        A_lo = A_nodes[k - 1][-1]                  # continuity at c = lo
        if k == 1:
            # Int_1(c) = (c-d)^a/a * int_0^1 (d + (c-d) s^{1/a})^{-a} ds   [exact]
            u = d + (c - d)[:, None] * s[None, :] ** (1.0 / a)
            q = (gw[None, :] * u ** (-a)).sum(axis=1)
            A = A_lo - (c - d) ** a * q
        else:
            # u = lo + (c-lo) s^p absorbs the (u-lo)^{a+1} kink of A_{k-1}
            u = lo + (c - lo)[:, None] * s[None, :] ** p
            du = (c - lo)[:, None] * p * s[None, :] ** (p - 1)
            # BUGFIX (S2B-CS1): v = u - d lies in step k-1's interval [(k-1)d, kd],
            # not step k-2's.  The old code normalised against (k-2)d and
            # interpolated A_nodes[k-2].  Only reachable for K >= 3, i.e. d < 1/2.
            v = u - d                              # in [ (k-1)d, kd ]
            wv = np.clip((v - (k - 1) * d) / d, 0.0, 1.0) ** (1.0 / p)
            Av = _bary(wv.ravel(), wn, bw, A_nodes[k - 1]).reshape(v.shape)
            integ = u ** (-a) * (u - d) ** (a - 1.0) * Av * du
            A = A_lo - a * (gw[None, :] * integ).sum(axis=1)
        A_nodes.append(A)

    # mass and tail: int c^{a-1} A_k(c) dc over each step, graded in w
    mass = d ** a / a                              # step 0 exactly
    tail = (d ** a - c_b ** a) / a if c_b < d else 0.0
    for k in range(1, K):
        lo = k * d
        hi = min((k + 1) * d, 1.0)
        for a0, a1 in ((lo, hi),) if c_b <= lo or c_b >= hi else ((lo, c_b), (c_b, hi)):
            dl = a1 - a0
            cg = a0 + dl * s ** p
            jac = dl * p * s ** (p - 1)
            wv = np.clip((cg - lo) / (hi - lo), 0.0, 1.0) ** (1.0 / p)
            Ag = _bary(wv, wn, bw, A_nodes[k])
            val = float((gw * cg ** (a - 1.0) * Ag * jac).sum())
            mass += val
            if a0 >= c_b:
                tail += val
    return tail / mass


# ------------------------------------------------------------------ mixture
def mixture_weights(H, f=F_REACH, tol=1e-15, offset=1):
    """w_n(H) of C7(a) / C.7.1.  offset=1 is the manuscript convention
    n = U + Poisson(H) with U ~ Bernoulli(f), i.e. n = 1 + Poisson(H) at f = 1.
    offset=0 is the counter-offset hypothesis n = Poisson(H)."""
    if H <= 0.0:
        return np.array([offset]), np.array([1.0])
    lo = max(0, int(H - 10.0 * math.sqrt(H) - 10))
    hi = int(H + 10.0 * math.sqrt(H) + 10)
    m = np.arange(lo, hi + 1)                      # m = Poisson count
    logp = -H + m * math.log(H) - np.array([math.lgamma(k + 1.0) for k in m])
    w = np.exp(logp)
    n = m + offset
    if f < 1.0:
        raise NotImplementedError("case A has f = 1")
    keep = w > tol * w.max()
    return n[keep], w[keep] / w[keep].sum()


def F_map(A, H, M=32, N=256, offset=1):
    """F(A, H) = sum_n w_n(H) P_{lambda A}(alpha r^n)."""
    n, w = mixture_weights(H, offset=offset)
    a = LAM * A / EPS
    doses = ALPHA * R ** n
    return float(sum(wi * P_stat(a, di, M=M, N=N) for wi, di in zip(w, doses)))


# ------------------------------------------------------------------ fold
def _gmax(H, M, N, offset=1):
    """max_A [F(A,H) - A] and its argmax.  Zero exactly at the fold."""
    from scipy.optimize import minimize_scalar
    r = minimize_scalar(lambda A: A - F_map(A, H, M=M, N=N, offset=offset),
                        bounds=(1e-3, 0.999), method="bounded",
                        options=dict(xatol=1e-11))
    return -r.fun, r.x


def solve_fold(M=32, N=256, lo=150.0, hi=160.0, xtol=1e-9, offset=1):
    """F(A_f,H_f) = A_f and dF/dA = 1, as the root of max_A[F-A] = 0."""
    from scipy.optimize import brentq
    H_f = brentq(lambda H: _gmax(H, M, N, offset)[0], lo, hi, xtol=xtol)
    gm, A_f = _gmax(H_f, M, N, offset)
    return dict(H_f=H_f, A_f=A_f, residual_max_g=gm)


def A_plus(H, M, N, upper=0.99999, bracket_lo=None, offset=1):
    """Largest fixed point of A = F(A,H)."""
    from scipy.optimize import brentq
    g = lambda A: F_map(A, H, M=M, N=N, offset=offset) - A      # noqa: E731
    lo = bracket_lo if bracket_lo is not None else _gmax(H, M, N, offset)[1]
    if g(lo) < 0:
        lo = _gmax(H, M, N, offset)[1]
    return brentq(g, lo, upper, xtol=1e-12)


def t_ad_f(H_f, M=32, N=256, nq=48, offset=1):
    """t_ad,f = int_0^{H_f} dH/(lambda A_+(H)), with H = H_f - v^2 absorbing the
    square-root approach of A_+ to the fold."""
    s, w = _gl(nq)
    V = math.sqrt(H_f)
    v = V * s
    H = H_f - v ** 2
    order = np.argsort(-H)                            # descending H: warm bracket
    vals = np.empty_like(H)
    prev = None
    for i in order:
        a = A_plus(float(H[i]), M, N, bracket_lo=prev, offset=offset)
        vals[i] = 2.0 * v[i] / (LAM * a)
        prev = a
    return float(V * (w * vals).sum())


def run(M, N, nq, lo=150.0, hi=160.0, offset=1):
    f = solve_fold(M=M, N=N, lo=lo, hi=hi, offset=offset)
    f["t_ad_f"] = t_ad_f(f["H_f"], M=M, N=N, nq=nq, offset=offset)
    f["settings"] = dict(cheb_nodes=M, gauss_nodes=N, t_ad_quad_nodes=nq,
                         counter_offset=offset)
    return f


if __name__ == "__main__":
    import time
    t0 = time.time()
    ladder = []
    for M, N, nq in ((24, 128, 32), (32, 256, 48), (44, 384, 64)):
        r = run(M, N, nq)
        ladder.append(r)
        print(f"  M={M} N={N} nq={nq}:  A_f={r['A_f']:.9f}  H_f={r['H_f']:.6f}  "
              f"t_ad_f={r['t_ad_f']:.6f}   [{time.time() - t0:.0f}s]", flush=True)

    fin, prev = ladder[-1], ladder[-2]
    out = dict(
        case="P6 case A, dose-mixture fold (C7(c))",
        parameters=dict(alpha=ALPHA, beta=BETA, r=R, lam=LAM, eps=EPS, c_b=C_B,
                        rho=0.0, kappa=0.0, f=F_REACH, initial="I1, one T pulse, "
                        "c(0)=1, n(0)=1, eta=0.03"),
        method="C2.11-C2.14 method of steps carried to K=ceil(1/d) steps "
               "(the project's two-step quadratures are restricted to d>=1/2 and "
               "cannot be called here); fold as the root of max_A[F(A,H)-A]=0; "
               "t_ad,f by Gauss-Legendre in v with H = H_f - v^2",
        result=dict(A_f=fin["A_f"], H_f=fin["H_f"], t_ad_f=fin["t_ad_f"]),
        numerical_error=dict(A_f=abs(fin["A_f"] - prev["A_f"]),
                             H_f=abs(fin["H_f"] - prev["H_f"]),
                             t_ad_f=abs(fin["t_ad_f"] - prev["t_ad_f"])),
        residual_max_g=fin["residual_max_g"],
        settings=fin["settings"],
        ladder=ladder,
        manuscript=MANUSCRIPT,
        deviation_from_manuscript={k: fin[{"A_f": "A_f", "H_f": "H_f",
                                           "t_ad_f": "t_ad_f"}[k]] - v
                                   for k, v in MANUSCRIPT.items()},
    )
    for k in ("A_f", "H_f", "t_ad_f"):
        print(f"{k}: computed {fin[k]!r}  +- {out['numerical_error'][k]:.2e}   "
              f"manuscript {MANUSCRIPT[k]}   deviation "
              f"{out['deviation_from_manuscript'][k]:+.6g}", flush=True)
    os.makedirs(os.path.join(HERE, "outputs", "raw"), exist_ok=True)
    p = os.path.join(HERE, "outputs", "raw", "dose_mixture_fold_caseA.json")
    json.dump(out, open(p, "w"), indent=2)
    print("wrote", p, flush=True)
