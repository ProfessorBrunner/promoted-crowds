"""Independent kinetic reference solver for the mean-field conviction law.

This file shares NO code with the agent simulator: there is no event queue, no
random number generator and no notion of an agent.  It integrates the measure
equation directly, which is what makes it an independent check.

Estimand (owner's Stage 2B statement, P4 form -- counters inert at r = 1):

    d/dt <psi, mu_t> = < -c psi'(c) + lambda A(t) [ psi(min{1, c+d}) - psi(c) ], mu_t >
    A(t) = mu_t((c_b, 1]),     mu_0 = (1-f) delta_0 + f delta_{alpha}

and its counter-resolved form, needed when r < 1 (P6): the state is (c, n) with n
the framing-class counter, the deposit on a receipt is d_n = alpha r^n with n the
PRE-receipt count, and

    d/dt <psi, mu_t^{(n)}> = < -c psi'(c), mu_t^{(n)} >
                             - lambda A(t) <psi, mu_t^{(n)}>
                             + lambda A(t) <psi(min{1, . + d_{n-1}}), mu_t^{(n-1)}>,
    A(t) = sum_n mu_t^{(n)}((c_b, 1]).

Discretisation
--------------
Work in u = log c, where the decay c' = -eps c becomes uniform translation
u' = -eps.  On a uniform u-grid of width h, and with the time step tied to the
grid as dt = h/eps, the transport step is an EXACT one-cell shift of a
piecewise-constant-in-u measure -- no numerical diffusion from the drift at all.

That exactness is NOT the same as the scheme being free of drift-related error.
Each time step is two FULL-dt passes of the composition "jump over dt, then
transport over dt" (there are no half-steps): the first pass is discarded and
supplies only A_pred for the Heun average of the rate.  Composing jump with
transport in a fixed order is a first-order Lie-Trotter splitting whose commutator
error is O(dt) -- not the jump map's interpolation.  Splitting is NOT the only O(dt)
term, however: the top-cell projection of clipped mass (boundary note below) is first
order in dt as well, and the h-ladders measure the two TOGETHER without resolving
them.  Every refinement ladder measures an order p between 1.00 and 1.06, which is
that COMBINED first-order term -- splitting plus projection, not splitting alone.

Boundaries are asymmetric.  At the bottom, mass at c = 0 is an explicit atom (zero
drift velocity, so it persists) and mass leaving the bottom cell is pooled into it
with a position error bounded by c_min; the atom still receives deposits.  At the
top there is NO atom at c = 1: the deposit position is clipped to 1 exactly and the
mass is placed in the top cell (u in [-h, 0]), so a unit mass that should sit at
c = 1 decays early by up to h in u = one time step.  That projection is invisible to
the activity functional ONLY AT THE MOMENT OF DEPOSITION -- the whole top cell lies
above c_b whenever c_b < e^-h, which holds in every run here -- but it DOES move A
later, because the projected mass reaches c_b up to one dt early.

The jump half-step applies the exact pure-jump semigroup
    exp(nu dt (Jop - I)) = e^{-nu dt} sum_k (nu dt)^k Jop^k / k!
truncated at k = K, so the "two receipts in one step" error that a single-jump
scheme would carry is removed to order (nu dt)^(K+1).

Everything is refined: h -> h/2 -> h/4 with the order measured, the horizon
extended, and the reported uncertainty taken from the refinement, not assumed.
"""

from __future__ import annotations

import math

import numpy as np
from numba import njit


# --------------------------------------------------------------------- geometry
def build_grid(c_min, h):
    """Uniform grid in u = log c on [log c_min, 0]."""
    U = -math.log(c_min)
    J = int(round(U / h))
    h = U / J                                  # exact fit
    edges_u = -U + h * np.arange(J + 1)        # J+1 edges, top edge = 0 (c = 1)
    cent_u = 0.5 * (edges_u[:-1] + edges_u[1:])
    return dict(h=h, J=J, U=U, edges_u=edges_u, cent_u=cent_u,
                cent_c=np.exp(cent_u), edges_c=np.exp(edges_u))


def frac_above(grid, c_b):
    """Fraction of each cell's (u-uniform) mass lying above c_b."""
    ub = math.log(c_b)
    lo, hi = grid["edges_u"][:-1], grid["edges_u"][1:]
    return np.clip((hi - ub) / grid["h"], 0.0, 1.0)


def deposit_map(grid, positions):
    """Conservative linear-in-u deposition of mass sitting at `positions`.

    Returns (idx0, idx1, w0, w1); mass m at position p contributes m*w0 to cell
    idx0 and m*w1 to idx1.  Positions at or above c = 1 land in the top cell.
    """
    J, h = grid["J"], grid["h"]
    p = np.minimum(np.asarray(positions, dtype=float), 1.0)
    p = np.maximum(p, grid["edges_c"][0])
    x = (np.log(p) - grid["cent_u"][0]) / h      # fractional cell-centre index
    i0 = np.floor(x).astype(np.int64)
    frac = x - i0
    i1 = i0 + 1
    w0 = 1.0 - frac
    w1 = frac
    # clamp at both ends, moving the weight onto the valid cell
    lo = i0 < 0
    w0[lo], w1[lo], i0[lo], i1[lo] = 0.0, 1.0, 0, 0
    hi = i1 > J - 1
    w0[hi], w1[hi], i0[hi], i1[hi] = 1.0, 0.0, J - 1, J - 1
    i0 = np.clip(i0, 0, J - 1)
    i1 = np.clip(i1, 0, J - 1)
    return (i0.astype(np.int32), i1.astype(np.int32), w0, w1)


# ------------------------------------------------------------------ the stepper
@njit(cache=True)
def _jop(A, Am0, B, Bm0, idx0, idx1, w0, w1, ai0, ai1, aw0, aw1, advance, leak,
         n_lo, n_hi):
    """One application of the jump map to (A, Am0), writing into (B, Bm0).

    Only slabs [n_lo, n_hi] are touched; the caller guarantees the rest are empty.
    """
    nS, J = A.shape
    for n in range(n_lo, min(n_hi + advance + 1, nS)):
        for j in range(J):
            B[n, j] = 0.0
        Bm0[n] = 0.0
    for n in range(n_lo, n_hi + 1):
        tgt = n + advance
        if tgt > nS - 1:
            tot = Am0[n]
            for j in range(J):
                tot += A[n, j]
            leak[0] += tot
            tgt = nS - 1
        for j in range(J):
            m = A[n, j]
            if m != 0.0:
                B[tgt, idx0[n, j]] += m * w0[n, j]
                B[tgt, idx1[n, j]] += m * w1[n, j]
        m = Am0[n]
        if m != 0.0:
            B[tgt, ai0[n]] += m * aw0[n]
            B[tgt, ai1[n]] += m * aw1[n]


@njit(cache=True)
def _jump_semigroup(W, m0, nu_dt, K, idx0, idx1, w0, w1, ai0, ai1, aw0, aw1,
                    advance, A1, A1m, A2, A2m, ACC, ACCm, leak, n_lo, n_hi):
    nS, J = W.shape
    e = math.exp(-nu_dt)
    top = min(n_hi + advance * K + 1, nS)
    for n in range(n_lo, top):
        for j in range(J):
            ACC[n, j] = e * W[n, j]
            A1[n, j] = W[n, j]
        ACCm[n] = e * m0[n]
        A1m[n] = m0[n]
    coef = e
    hi = n_hi
    for k in range(1, K + 1):
        coef = coef * nu_dt / k
        _jop(A1, A1m, A2, A2m, idx0, idx1, w0, w1, ai0, ai1, aw0, aw1, advance,
             leak, n_lo, hi)
        hi = min(hi + advance, nS - 1)
        for n in range(n_lo, min(hi + 1, nS)):
            for j in range(J):
                A1[n, j] = A2[n, j]
                ACC[n, j] += coef * A2[n, j]
            A1m[n] = A2m[n]
            ACCm[n] += coef * A2m[n]
    for n in range(n_lo, top):
        for j in range(J):
            W[n, j] = ACC[n, j]
        m0[n] = ACCm[n]


@njit(cache=True)
def _transport(W, m0, n_lo, n_hi):
    """Exact one-cell shift in u (mass moves to lower c); bottom cell pools at 0."""
    nS, J = W.shape
    for n in range(n_lo, min(n_hi + 1, nS)):
        m0[n] += W[n, 0]
        for j in range(J - 1):
            W[n, j] = W[n, j + 1]
        W[n, J - 1] = 0.0


@njit(cache=True)
def _activity(W, fab, n_lo, n_hi):
    nS, J = W.shape
    a = 0.0
    for n in range(n_lo, min(n_hi + 1, nS)):
        for j in range(J):
            a += W[n, j] * fab[j]
    return a


@njit(cache=True)
def run_kinetic(W, m0, fab, idx0, idx1, w0, w1, ai0, ai1, aw0, aw1, advance,
                lam, dt, n_steps, K, A_out, leak, nu_prescribed=-1.0):
    """Integrate to n_steps*dt, recording A on every step.  Heun in the coupling.

    nu_prescribed >= 0 drives the jump process at that CONSTANT rate instead of the
    self-consistent nu(t) = lambda A(t).  The long-time A is then the stationary
    response P_nu of C2(b) / C4.1, which is what the fold construction needs.  The
    default -1.0 keeps the self-consistent coupling, bit for bit.
    """
    nS, J = W.shape
    A1 = np.empty_like(W); A1m = np.empty(nS)
    A2 = np.empty_like(W); A2m = np.empty(nS)
    ACC = np.empty_like(W); ACCm = np.empty(nS)
    Ws = np.empty_like(W); ms = np.empty(nS)
    A1[:, :] = 0.0; A2[:, :] = 0.0; ACC[:, :] = 0.0
    A1m[:] = 0.0; A2m[:] = 0.0; ACCm[:] = 0.0
    n_lo = 0
    n_hi = 0 if advance == 1 else nS - 1
    if advance == 1:
        for n in range(nS):
            tot = m0[n]
            for j in range(J):
                tot += W[n, j]
            if tot > 0.0:
                n_hi = n
    for it in range(n_steps):
        A_now = _activity(W, fab, n_lo, n_hi)
        A_out[it] = A_now
        for n in range(n_lo, min(n_hi + advance * K + 2, nS)):
            for j in range(J):
                Ws[n, j] = W[n, j]
            ms[n] = m0[n]
        nu = nu_prescribed if nu_prescribed >= 0.0 else lam * A_now
        hi_new = min(n_hi + advance * K, nS - 1)
        _jump_semigroup(W, m0, nu * dt, K, idx0, idx1, w0, w1, ai0, ai1, aw0,
                        aw1, advance, A1, A1m, A2, A2m, ACC, ACCm, leak,
                        n_lo, n_hi)
        _transport(W, m0, n_lo, hi_new)
        A_pred = _activity(W, fab, n_lo, hi_new)
        for n in range(n_lo, min(n_hi + advance * K + 2, nS)):
            for j in range(J):
                W[n, j] = Ws[n, j]
            m0[n] = ms[n]
        nu_bar = (nu_prescribed if nu_prescribed >= 0.0
                  else 0.5 * (nu + lam * A_pred))
        _jump_semigroup(W, m0, nu_bar * dt, K, idx0, idx1, w0, w1, ai0, ai1,
                        aw0, aw1, advance, A1, A1m, A2, A2m, ACC, ACCm, leak,
                        n_lo, n_hi)
        _transport(W, m0, n_lo, hi_new)
        n_hi = hi_new
        # prune empty low slabs
        while n_lo < n_hi:
            tot = m0[n_lo]
            for j in range(J):
                tot += W[n_lo, j]
            if tot > 1e-15:
                break
            n_lo += 1
    A_out[n_steps] = _activity(W, fab, n_lo, n_hi)


# ----------------------------------------------------------------- the problems
def solve(lam, alpha, r, c_b, f, T, h, c_min=1e-3, K=2, n_slabs=None, eps=1.0,
          nu_prescribed=-1.0):
    """Integrate the mean-field law and return (t, A(t), diagnostics).

    r == 1 makes the counters inert (the deposit never changes), so a single slab
    represents the whole joint law exactly; r < 1 needs one slab per counter value.
    """
    grid = build_grid(c_min, h)
    J, h = grid["J"], grid["h"]
    dt = h / eps
    n_steps = int(math.ceil(T / dt))
    inert = (r == 1.0)
    if inert:
        nS, advance = 1, 0
        deps = np.array([alpha])
    else:
        if n_slabs is None:
            # the counter is Poisson(Lambda) with Lambda <= lambda * int A dt <=
            # lambda * T; six standard deviations of head-room above the crude
            # bound lambda * T * (a typical A) is ample, and the leak is reported
            lam_T = lam * T
            n_slabs = int(lam_T + 8.0 * math.sqrt(max(lam_T, 1.0)) + 16)
        nS, advance = int(n_slabs), 1
        deps = alpha * r ** np.arange(nS)       # deposit from slab n is alpha r^n
    idx0 = np.empty((nS, J), dtype=np.int32); idx1 = np.empty((nS, J), dtype=np.int32)
    w0 = np.empty((nS, J)); w1 = np.empty((nS, J))
    ai0 = np.empty(nS, dtype=np.int32); ai1 = np.empty(nS, dtype=np.int32)
    aw0 = np.empty(nS); aw1 = np.empty(nS)
    for n in range(nS):
        a, b, c_, d_ = deposit_map(grid, grid["cent_c"] + deps[n])
        idx0[n], idx1[n], w0[n], w1[n] = a, b, c_, d_
        a, b, c_, d_ = deposit_map(grid, np.array([deps[n]]))
        ai0[n], ai1[n], aw0[n], aw1[n] = a[0], b[0], c_[0], d_[0]

    W = np.zeros((nS, J)); m0 = np.zeros(nS)
    # mu_0 = (1-f) delta_0 + f delta_{alpha}; the pulse is the FIRST receipt, so the
    # cohort sits at min(1, alpha) with counter 1 and the rest at 0 with counter 0
    m0[0] = 1.0 - f
    i0, i1, q0, q1 = deposit_map(grid, np.array([min(1.0, alpha)]))
    slab0 = 1 if not inert else 0
    W[min(slab0, nS - 1), i0[0]] += f * q0[0]
    W[min(slab0, nS - 1), i1[0]] += f * q1[0]

    A_out = np.zeros(n_steps + 1)
    leak = np.zeros(1)
    run_kinetic(W, m0, frac_above(grid, c_b), idx0, idx1, w0, w1, ai0, ai1,
                aw0, aw1, advance, lam, dt, n_steps, K, A_out, leak,
                float(nu_prescribed))
    t = dt * np.arange(n_steps + 1)
    diag = dict(h=h, dt=dt, J=J, n_slabs=nS, n_steps=n_steps,
                mass=float(W.sum() + m0.sum()), slab_leak=float(leak[0]),
                nu_prescribed=float(nu_prescribed),
                mass_at_zero=float(m0.sum()), c_min=c_min, K=K, inert=inert)
    return t, A_out, diag


def first_down_crossing(t, A, level):
    above = A > level
    for i in range(1, len(A)):
        if above[i - 1] and not above[i]:
            a0, a1 = A[i - 1], A[i]
            if a0 == a1:
                return float(t[i])
            return float(t[i - 1] + (a0 - level) / (a0 - a1) * (t[i] - t[i - 1]))
    return float("nan")


def accumulated_index(t, A, lam, t_star):
    """Lambda* = lambda int_0^{t*} A(s) ds by the trapezoidal rule."""
    if math.isnan(t_star):
        return float("nan")
    m = t <= t_star
    tt, aa = t[m], A[m]
    val = float(np.trapezoid(aa, tt)) if len(tt) > 1 else 0.0
    if len(tt) and tt[-1] < t_star:                     # final partial interval
        i = len(tt)
        a_end = float(np.interp(t_star, t, A))
        val += 0.5 * (aa[-1] + a_end) * (t_star - tt[-1])
    return lam * val
