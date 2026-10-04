"""Stage 3 P5 — the exact mean-field reference, independent of the agent simulator.

In this sector r = 1 and alpha = 2 > c_b, so every receipt clips conviction to 1 and
refreshes the shut-off deadline: an agent is active at time t if and only if it
received at least one message in (t - L, t], L = eps^-1 log(1/c_b).  Each agent
receives at rate lambda A(t) (N/(N-1) in the finite-N process; exactly lambda A in
the mean field).  Hence C9(b)'s pair

    A(t) = f e^{lambda t} / (1 - f + f e^{lambda t}),              0 <= t < L
    A(t) = 1 - exp[ -lambda \\int_{t-L}^{t} A(s) ds ],              t >= L

the first line being the closed-form solution of A = 1 - (1-f) exp(-lambda \\int_0^t A)
on [0, L).  The persistent branch solves A* = 1 - exp(-lambda L A*); at lambda = 2,
L = log 2 this is 1 - exp(-log 2) = 1/2 IDENTICALLY, so the registered A* = 0.5
carries no numerical error at all.

This file integrates the delay equation directly.  It shares no code with the agent
simulator and has no RNG.  Step halving with the observed order reported.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def solve(lam, f, T, h, c_b=0.5, eps=1.0):
    """Integrate the delay equation on a uniform grid with h dividing L exactly."""
    L = math.log(1.0 / c_b) / eps
    m = int(round(L / h))
    h = L / m                                  # make L an exact multiple of h
    n = int(math.ceil(T / h))
    t = h * np.arange(n + 1)
    A = np.empty(n + 1)
    # closed form on [0, L)
    k0 = min(m, n)
    e = np.exp(lam * t[:k0 + 1])
    A[:k0 + 1] = f * e / (1.0 - f + f * e)
    # cumulative integral by the trapezoidal rule, extended as we go
    C = np.empty(n + 1)                        # C[k] = int_0^{t_k} A
    C[0] = 0.0
    for k in range(1, k0 + 1):
        C[k] = C[k - 1] + 0.5 * h * (A[k - 1] + A[k])
    for k in range(k0 + 1, n + 1):
        # A[k] appears on both sides through C[k]; one fixed-point sweep on the
        # trapezoidal rule converges in a few iterations (contraction factor
        # lambda*h/2 << 1)
        a = A[k - 1]
        for _ in range(60):
            Ck = C[k - 1] + 0.5 * h * (A[k - 1] + a)
            a_new = 1.0 - math.exp(-lam * (Ck - C[k - m]))
            if abs(a_new - a) < 1e-15:
                a = a_new
                break
            a = a_new
        A[k] = a
        C[k] = C[k - 1] + 0.5 * h * (A[k - 1] + a)
    return t, A, C, dict(h=h, L=L, m=m, n=n)


def window_mean(t, A, t0, t1):
    k0 = int(round(t0 / (t[1] - t[0])))
    k1 = int(round(t1 / (t[1] - t[0])))
    return float(np.trapezoid(A[k0:k1 + 1], t[k0:k1 + 1]) / (t[k1] - t[k0]))


def A_star(lam, c_b=0.5, eps=1.0):
    L = math.log(1.0 / c_b) / eps
    if lam * L <= 1.0:
        return 0.0
    a = 0.5
    for _ in range(200):
        a -= (1.0 - math.exp(-lam * L * a) - a) / (lam * L * math.exp(-lam * L * a) - 1.0)
    return a


if __name__ == "__main__":
    out = {"A_star_lambda2": A_star(2.0), "A_star_lambda1": A_star(1.0)}
    rows = []
    for lam in (1.0, 2.0):
        for f in (0.01, 0.10):
            ladder = []
            for h in (2e-3, 1e-3, 5e-4, 2.5e-4):
                t, A, C, d = solve(lam, f, 70.0, h)
                ladder.append(dict(h=d["h"], window_mean_A=window_mean(t, A, 20., 70.),
                                   A_at_20=float(np.interp(20.0, t, A)),
                                   A_at_70=float(A[-1]),
                                   A_max=float(A.max())))
            w = [x["window_mean_A"] for x in ladder]
            d1, d2 = w[-2] - w[-3], w[-1] - w[-2]
            order = float(math.log2(abs(d1 / d2))) if d2 != 0 and d1 / d2 > 0 else None
            rows.append(dict(lam=lam, f=f, ladder=ladder, observed_order=order,
                             window_mean_richardson=(w[-1] + (w[-1] - w[-2]) / 3.0
                                                     if order and order > 1.5
                                                     else w[-1] + (w[-1] - w[-2])),
                             uncertainty=abs(w[-1] - w[-2]),
                             A_at_20=ladder[-1]["A_at_20"],
                             A_at_70=ladder[-1]["A_at_70"],
                             A_max=ladder[-1]["A_max"]))
            print(f"  lam={lam} f={f}: window mean A = {w[-1]:.9f} "
                  f"(order {order}, unc {abs(w[-1]-w[-2]):.2e}), "
                  f"A(20) = {ladder[-1]['A_at_20']:.6e}", flush=True)
    out["rows"] = rows
    with open(os.path.join(HERE, "outputs", "raw", "p5_delay_reference.json"),
              "w") as fh:
        json.dump(out, fh, indent=2)
    print("done")
