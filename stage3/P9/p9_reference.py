"""Stage 3 P9 — the Appendix C C4.7 quadrature fixed points, computed independently.

C4.1-C4.2 define F(u,v;alpha,beta) = Pr_stat{y > c_b} for the capped process with
jumps alpha at rate u, jumps beta at rate v, and decay -eps*y on [0,1]:

    0 = eps (y f)' - (u+v) f(y) + u 1{y>alpha} f(y-alpha) + v 1{y>beta} f(y-beta)
    eps f(1-) = u int_{max(0,1-alpha)}^1 f + v int_{max(0,1-beta)}^1 f

At alpha = 1 the alpha-term never fires in the interior (y > 1 is impossible), so
with g = y f and a = (u+v)/eps the equation is a delay ODE with delay beta:

    g(y) = C y^a                                              0 <= y <= beta
    g(y) = y^a [ C - (v/eps) int_beta^y t^-a g(t-beta)/(t-beta) dt ]    y > beta

solved by the method of steps.  The integrand carries an algebraic singularity
(t-beta)^(a-1) at t = beta; the substitution t = beta + M w^(1/a) with M = y - beta
removes it EXACTLY, since s^(a-1) ds = (M^a/a) dw, leaving a smooth integrand on
[0,1] for Gauss-Legendre.

Three independent checks are run before any fixed point is reported:
  (1) the clipped-arrival flux condition C4.2, which is the integral of the interior
      equation plus normalization and therefore must hold automatically;
  (2) the v -> 0 limit, where the process is "reset to 1 at rate u then decay", so
      F = 1 - c_b^(u/eps) in closed form;
  (3) mesh refinement of every quadrature.
"""
import json, math, os
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = os.path.dirname(os.path.abspath(__file__))
GL_N = 200
_XW = leggauss(GL_N)

def _gl(fn, lo, hi):
    x, w = _XW
    t = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
    return 0.5 * (hi - lo) * float(np.dot(w, fn(t)))

class CappedStationary:
    """Stationary law of the capped jump-decay process; alpha = 1 assumed."""
    def __init__(self, u, v, beta, eps=1.0, alpha=1.0):
        assert alpha == 1.0, "this construction uses the alpha = 1 simplification"
        assert 0.0 < beta < 1.0
        self.u, self.v, self.beta, self.eps = u, v, beta, eps
        self.a = (u + v) / eps
        self.n_steps = int(math.ceil(1.0 / beta))      # number of method-of-steps blocks

    # g(y) = y f(y), with C = 1; everything is linear in C
    def _I(self, y):
        """int_beta^y t^-a g(t-beta)/(t-beta) dt, by blocks."""
        b, a = self.beta, self.a
        if y <= b:
            return 0.0
        tot = 0.0
        # block 1: t-beta in (0, beta] -> g(s) = s^a exactly; singularity removed
        hi1 = min(y, 2 * b)
        M = hi1 - b
        if M > 0:
            tot += (M ** a / a) * _gl(lambda w: (b + M * w ** (1.0 / a)) ** (-a),
                                      0.0, 1.0)
        # later blocks: g(s) for s > beta is smooth, evaluated recursively
        lo = 2 * b
        while lo < y:
            hi = min(y, lo + b)
            tot += _gl(lambda t: t ** (-a) * self.g(t - b) / (t - b), lo, hi)
            lo = hi
        return tot

    def g(self, y):
        y = np.asarray(y, dtype=float)
        scal = y.ndim == 0
        y = np.atleast_1d(y)
        out = np.empty_like(y)
        for i, yy in enumerate(y):
            if yy <= self.beta:
                out[i] = yy ** self.a
            else:
                out[i] = yy ** self.a * (1.0 - (self.v / self.eps) * self._I(yy))
        return float(out[0]) if scal else out

    def f(self, y):
        y = np.asarray(y, dtype=float)
        return np.where(y > 0, self.g(y) / np.where(y > 0, y, 1.0), 0.0)

    def _mass(self, lo, hi):
        """int_lo^hi f, split at multiples of beta; the y^(a-1) end is exact."""
        b, a = self.beta, self.a
        tot = 0.0
        if lo < min(hi, b):
            top = min(hi, b)
            # int_lo^top y^(a-1) dy = (top^a - lo^a)/a.  Computed with expm1 so the
            # small-a limit (-> log(top/lo)) is free of catastrophic cancellation.
            if lo <= 0.0:
                tot += math.expm1(a * math.log(top)) / a + 1.0 / a
            else:
                tot += (math.expm1(a * math.log(top))
                        - math.expm1(a * math.log(lo))) / a
            lo = top
        while lo < hi:
            top = min(hi, (math.floor(lo / b) + 1) * b)
            if top <= lo:
                top = hi
            tot += _gl(lambda t: self.g(t) / t, lo, top)
            lo = top
        return tot

    def solve(self, c_b):
        tot = self._mass(0.0, 1.0)
        C = 1.0 / tot
        F = self._mass(c_b, 1.0) / tot
        # check (1): the C4.2 clipped-arrival flux condition
        f1 = C * self.g(1.0)
        rhs = self.u * 1.0 + self.v * (self._mass(1.0 - self.beta, 1.0) / tot)
        return dict(F=F, C=C, norm=tot, flux_lhs=self.eps * f1, flux_rhs=rhs,
                    flux_rel_err=abs(self.eps * f1 - rhs) / max(rhs, 1e-300),
                    a=self.a)

def F(u, v, beta=0.4, c_b=0.3, eps=1.0):
    if u + v <= 0.0:
        return 0.0
    return CappedStationary(u, v, beta, eps).solve(c_b)["F"]

if __name__ == "__main__":
    BETA, C_B, EPS, P = 0.4, 0.5, 1.0, 0.5
    out = dict(beta=BETA, c_b=C_B, eps=EPS, p=P, alpha=1.0)
    print("check 2 - the v -> 0 limit against the closed form 1 - c_b^(u/eps)")
    rows = []
    for u in (0.3, 0.8, 1.5, 3.0):
        got = F(u, 1e-12, BETA, C_B, EPS); exact = 1.0 - C_B ** (u / EPS)
        rows.append(dict(u=u, quadrature=got, closed_form=exact, d=got - exact))
        print(f"  u={u:<5} quadrature {got:.12f}  closed form {exact:.12f}  "
              f"d = {got-exact:+.2e}")
    out["check_v_to_zero"] = rows
    print("\ncheck 1 - the C4.2 clipped-arrival flux condition (must hold identically)")
    rows = []
    for (u, v) in ((0.5, 0.5), (1.0, 0.3), (2.0, 1.2), (0.2, 2.5)):
        s = CappedStationary(u, v, BETA, EPS).solve(C_B)
        rows.append(dict(u=u, v=v, **{k: s[k] for k in
                                      ("F", "flux_lhs", "flux_rhs", "flux_rel_err")}))
        print(f"  u={u:<4} v={v:<4} F={s['F']:.10f}  flux {s['flux_lhs']:.10f} vs "
              f"{s['flux_rhs']:.10f}  rel err {s['flux_rel_err']:.2e}")
    out["check_flux"] = rows
    print("\ncheck 3 - Gauss-Legendre node refinement on F(2.0, 1.2)")
    ref = []
    for n in (50, 100, 200, 400):
        globals()["_XW"] = leggauss(n)
        ref.append(dict(nodes=n, F=F(2.0, 1.2, BETA, C_B, EPS)))
        print(f"  nodes={n:<4} F = {ref[-1]['F']:.14f}")
    globals()["_XW"] = leggauss(GL_N)
    out["check_nodes"] = ref
    json.dump(out, open(os.path.join(HERE, "outputs", "raw",
                                     "p9_reference_checks.json"), "w"), indent=2)


# ===================================================================== fixed points
_CACHE = {}

def Fc(u, v, beta=0.4, c_b=0.3, eps=1.0):
    k = (round(u, 12), round(v, 12), beta, c_b, eps)
    if k not in _CACHE:
        _CACHE[k] = F(u, v, beta, c_b, eps)
    return _CACHE[k]


def fixed_point_symmetric(lam, p=0.5, beta=0.4, c_b=0.3, eps=1.0):
    """p = 1/2 symmetric branch: A = p F(lam A, lam A)."""
    from scipy.optimize import brentq
    g = lambda A: p * Fc(lam * A, lam * A, beta, c_b, eps) - A
    lo, hi = 1e-4, p - 1e-9
    if g(lo) <= 0 and g(hi) <= 0:
        return None
    return brentq(g, lo, hi, xtol=1e-13, rtol=8.9e-16, maxiter=200)


def map_C46(A, lam, p=0.5, beta=0.4, c_b=0.3, eps=1.0):
    Ap, Am = A
    return np.array([p * Fc(lam * Ap, lam * Am, beta, c_b, eps),
                     (1.0 - p) * Fc(lam * Am, lam * Ap, beta, c_b, eps)])


def jacobian_C410(A, lam, p=0.5, beta=0.4, c_b=0.3, eps=1.0, hstep=2e-4):
    """J = d(map)/d(A), which C4.10 states IS the static susceptibility matrix."""
    Ap, Am = A
    Fu_p = (Fc(lam * Ap + lam * hstep, lam * Am, beta, c_b, eps)
            - Fc(lam * Ap - lam * hstep, lam * Am, beta, c_b, eps)) / (2 * hstep)
    Fv_p = (Fc(lam * Ap, lam * Am + lam * hstep, beta, c_b, eps)
            - Fc(lam * Ap, lam * Am - lam * hstep, beta, c_b, eps)) / (2 * hstep)
    Fu_m = (Fc(lam * Am + lam * hstep, lam * Ap, beta, c_b, eps)
            - Fc(lam * Am - lam * hstep, lam * Ap, beta, c_b, eps)) / (2 * hstep)
    Fv_m = (Fc(lam * Am, lam * Ap + lam * hstep, beta, c_b, eps)
            - Fc(lam * Am, lam * Ap - lam * hstep, beta, c_b, eps)) / (2 * hstep)
    return np.array([[p * Fu_p, p * Fv_p],
                     [(1 - p) * Fv_m, (1 - p) * Fu_m]])


def c47_scan(lam, p=0.5, beta=0.4, c_b=0.3, eps=1.0, nz=25):
    """Search for ASYMMETRIC branches via the C4.7 scalar consistency equation.

    C4.7: z = p F_+ / S with F_+ = F(nu z, nu(1-z)), S = p F_+ + (1-p) F_-, and
    lambda = nu / S.  At p = 1/2 the residual is antisymmetric about z = 1/2, so
    z = 1/2 is always a root; a sign change of the residual on (0, 1/2) would mean
    an extra asymmetric branch.  nu is chosen at each z so that lambda matches.
    """
    from scipy.optimize import brentq
    out = []
    for z in np.linspace(0.02, 0.5, nz):
        def lam_of_nu(nu):
            Fp = Fc(nu * z, nu * (1 - z), beta, c_b, eps)
            Fm = Fc(nu * (1 - z), nu * z, beta, c_b, eps)
            S = p * Fp + (1 - p) * Fm
            return nu / S - lam
        try:
            nu = brentq(lam_of_nu, 1e-3, 40.0, xtol=1e-12, maxiter=120)
        except ValueError:
            out.append(dict(z=z, nu=None, residual=None))
            continue
        Fp = Fc(nu * z, nu * (1 - z), beta, c_b, eps)
        Fm = Fc(nu * (1 - z), nu * z, beta, c_b, eps)
        S = p * Fp + (1 - p) * Fm
        out.append(dict(z=float(z), nu=float(nu), residual=float(p * Fp / S - z),
                        A_plus=float(p * Fp), A_minus=float((1 - p) * Fm)))
    return out
