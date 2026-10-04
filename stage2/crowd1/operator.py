"""Operator checks on a frozen background (design A3).

A3: "Operator checks: offspring counts, offspring types, and generation timing
from a single seed on a frozen background, compared with the kernel or branching
calculation."  A4a: "Frozen diagnostics at finite delay are labeled as such and
reported separately from measured descendant growth."

"Frozen" means the background responds in the state it was SAVED in: a recipient's
conviction is not decayed to the message time.  Each agent that the seed (or one of
its descendants) activates still decays normally for the purpose of its OWN
lifetime, which is what sets its offspring count -- that is the construction
Appendix C C3.19 uses, where l_H(s) is evaluated at the freeze time s while the
newborn's own lifetime runs from its activation.

The message transition here is the same arithmetic as engine._deliver, restricted
to the process agent class (operator checks are not defined for the automaton or
the surrogate, which have no invasion seed in the design).

Two quantities come out of one run of `frozen_trials`:

  Z1   -- offspring of the SEED, which is what P1 and P2 register
          (P1: R_inv = lambda L_alpha (1 + zeta x)/2;  P2: R_inv = lambda q_T log(1/0.95))
  R_fr -- mean offspring of a FIRST-GENERATION agent, which is what P3 registers
          as the frozen diagnostic (C3.19's rank-one next-generation operator,
          R_fr = lambda [w_H l_H + w_L l_0]); for P1 and P2 the operator is
          homogeneous and R_fr coincides with Z1.
"""

import math

import numpy as np
from numba import njit

from .engine import _cosd_i
from .rng import next_double, next_exp, next_below

MAXT = 1 << 16   # per-trial cap on the number of touched background agents


@njit(cache=True)
def frozen_trials(
    n_trials, max_gen, lam, eps, c_b, c_h, alpha, beta, r, seed_c, freeze,
    relax_rho, target_phi_plus, target_phi_minus,
    phi, phi_cls, c_last, s, n_cnt, t_touch,  # state, restored after each trial
    relaxed, relax_t,                         # background relaxation bookkeeping
    p_phi, p_cls, p_c, p_s, p_n,              # pristine copies
    streams,
    out_z1, out_z2, out_gen1_n, out_gen1_off, out_nmsg, out_nacc,
    out_off_c, out_off_phi, out_off_s, out_off_t, out_off_gen, out_nrec,
):
    """Run `n_trials` independent single-seed trials on one frozen background.

    Per-trial outputs: out_z1 (offspring of the seed), out_z2 (generation-2 count),
    out_gen1_n / out_gen1_off (number of generation-1 agents and their total
    offspring, for the ratio estimator of R_fr), out_nmsg / out_nacc (messages sent
    and accepted).  Per-offspring records (conviction at activation, pre-message
    orientation and stance, birth time, generation) are appended to out_off_* up to
    their capacity, with out_nrec[0] the number written.
    """
    N = phi.shape[0]
    J = n_cnt.shape[1]
    touched = np.empty(MAXT, dtype=np.int64)
    # BFS queue over activated agents: index, conviction at activation, generation
    q_idx = np.empty(MAXT, dtype=np.int64)
    q_c = np.empty(MAXT, dtype=np.float64)
    q_g = np.empty(MAXT, dtype=np.int32)
    q_t = np.empty(MAXT, dtype=np.float64)
    cap = out_off_c.shape[0]

    for trial in range(n_trials):
        ntouch = 0
        nmsg = 0
        nacc = 0
        z1 = 0
        z2 = 0
        g1n = 0
        g1off = 0

        seed = next_below(streams, 1, N)
        # the seed occupies an agent slot: save and overwrite it (A1)
        touched[ntouch] = seed
        ntouch += 1
        t_touch[seed] = 0.0
        relaxed[seed] = 1
        relax_t[seed] = 0.0
        phi[seed] = 0
        phi_cls[seed] = 0
        c_last[seed] = seed_c
        s[seed] = 1
        for jj in range(J):
            n_cnt[seed, jj] = 0

        qh = 0
        qt = 0
        q_idx[qt] = seed
        q_c[qt] = seed_c
        q_g[qt] = 0
        q_t[qt] = 0.0
        qt += 1

        while qh < qt:
            a = q_idx[qh]
            ca = q_c[qh]
            ga = q_g[qh]
            ta = q_t[qh]
            qh += 1
            if ga > max_gen:
                continue
            absa = -ca if ca < 0.0 else ca
            if absa <= c_b:
                continue
            ell = math.log(absa / c_b) / eps
            th = phi[a]
            jc = phi_cls[a]
            # broadcast times are a Poisson(lambda) process on the agent's lifetime
            tt = next_exp(streams, 0, lam)
            while tt < ell:
                nmsg += 1
                k = next_below(streams, 1, N - 1)
                if k >= a:
                    k += 1
                # --- message transition (engine._deliver order).  freeze = 1 holds
                # the recipient at the saved state (A3's frozen background);
                # freeze = 0 decays it analytically to the absolute message time,
                # which is exact for a background that has received nothing.
                t_abs = ta + tt
                if freeze == 1:
                    c = c_last[k]
                else:
                    c = c_last[k] * math.exp(-eps * (t_abs - t_touch[k]))
                if relax_rho > 0.0 and relaxed[k] == 0:
                    # RESET (rate rho) sends phi to T_s and nothing else moves it,
                    # and a reset changes neither c nor s.  So at absolute time u the
                    # orientation is T_s with probability 1 - exp(-rho u) and the
                    # saved orientation otherwise, INDEPENDENTLY of everything else;
                    # memorylessness lets that be decided at the moment of receipt
                    # and re-decided from the last decision time on a later hit.
                    du = t_abs - relax_t[k]
                    if next_double(streams, 0) < 1.0 - math.exp(-relax_rho * du):
                        relaxed[k] = 1
                        if s[k] == 1:
                            phi[k] = target_phi_plus
                        else:
                            phi[k] = target_phi_minus
                    relax_t[k] = t_abs
                was_act = 1 if (c > c_b or c < -c_b) else 0
                cc = _cosd_i(th - phi[k])
                p = cc * cc
                uu = next_double(streams, 2)
                acc = 1 if uu < p else 0
                if acc == 1:
                    nacc += 1
                    newphi = th
                else:
                    newphi = (th + 90) % 180
                if ntouch >= MAXT:
                    out_nrec[1] = 1          # overflow flag
                    break
                touched[ntouch] = k
                ntouch += 1
                t_touch[k] = t_abs
                relaxed[k] = 1
                relax_t[k] = t_abs
                phi[k] = newphi
                phi_cls[k] = jc
                n_cnt[k, jc] += 1
                nn = n_cnt[k, jc]
                w = r ** (nn - 1)
                if acc == 1:
                    dep = w * _cosd_i(2 * th) * alpha
                else:
                    dep = -w * _cosd_i(2 * th) * beta
                c = c + dep
                if c > 1.0:
                    c = 1.0
                elif c < -1.0:
                    c = -1.0
                if c >= c_h and c <= -c_h:
                    pass
                elif c >= c_h:
                    s[k] = 1
                elif c <= -c_h:
                    s[k] = -1
                c_last[k] = c
                absc = -c if c < 0.0 else c
                if was_act == 0 and absc > c_b:
                    # a new offspring of generation ga + 1
                    if ga == 0:
                        z1 += 1
                    elif ga == 1:
                        z2 += 1
                    if ga == 0:
                        g1n += 1
                    if ga == 1:
                        g1off += 1
                    nrec = out_nrec[0]
                    if nrec < cap:
                        out_off_c[nrec] = c
                        out_off_phi[nrec] = p_phi[k]
                        out_off_s[nrec] = p_s[k]
                        out_off_t[nrec] = ta + tt
                        out_off_gen[nrec] = ga + 1
                        out_nrec[0] = nrec + 1
                    if qt < MAXT:
                        q_idx[qt] = k
                        q_c[qt] = c
                        q_g[qt] = ga + 1
                        q_t[qt] = ta + tt
                        qt += 1
                tt += next_exp(streams, 0, lam)

        out_z1[trial] = z1
        out_z2[trial] = z2
        out_gen1_n[trial] = g1n
        out_gen1_off[trial] = g1off
        out_nmsg[trial] = nmsg
        out_nacc[trial] = nacc

        # restore every touched agent from the pristine copy
        for ii in range(ntouch):
            k = touched[ii]
            phi[k] = p_phi[k]
            phi_cls[k] = p_cls[k]
            c_last[k] = p_c[k]
            s[k] = p_s[k]
            t_touch[k] = 0.0
            relaxed[k] = 0
            relax_t[k] = 0.0
            for jj in range(J):
                n_cnt[k, jj] = p_n[k, jj]


def run_frozen_operator(state, cfg, master_seed, n_trials, max_gen=1,
                        seed_c=1.0, record_cap=200000, freeze=True,
                        relax_rho=0.0):
    """Python wrapper.  `state` is a saved post-campaign state (runner._snapshot).

    freeze=True  -> A3's frozen-background operator check (the registered frozen
                    diagnostic R_fr).
    freeze=False -> the time-dependent kernel: the background decays analytically
                    from the save instant, which is exact because it has received
                    nothing.  This is what C3.21's E Z_2 is computed "without
                    freezing the background".
    """
    from .rng import seed_streams
    phi = state["phi"].copy()
    phi_cls = state["phi_cls"].copy()
    c_last = state["c_last"].copy()
    s = state["s"].copy()
    n_cnt = state["n_cnt"].copy()
    assert np.all(np.abs(c_last) <= cfg.c_b), (
        "an operator check requires a silent background; "
        f"max |c| = {np.abs(c_last).max()} > c_b = {cfg.c_b}")
    t_touch = np.zeros(phi.shape[0], dtype=np.float64)
    relaxed = np.zeros(phi.shape[0], dtype=np.int8)
    relax_t = np.zeros(phi.shape[0], dtype=np.float64)
    p_phi, p_cls, p_c, p_s, p_n = (phi.copy(), phi_cls.copy(), c_last.copy(),
                                   s.copy(), n_cnt.copy())
    z1 = np.zeros(n_trials, dtype=np.int64)
    z2 = np.zeros(n_trials, dtype=np.int64)
    g1n = np.zeros(n_trials, dtype=np.int64)
    g1off = np.zeros(n_trials, dtype=np.int64)
    nmsg = np.zeros(n_trials, dtype=np.int64)
    nacc = np.zeros(n_trials, dtype=np.int64)
    off_c = np.zeros(record_cap, dtype=np.float64)
    off_phi = np.zeros(record_cap, dtype=np.int32)
    off_s = np.zeros(record_cap, dtype=np.int8)
    off_t = np.zeros(record_cap, dtype=np.float64)
    off_gen = np.zeros(record_cap, dtype=np.int32)
    nrec = np.zeros(2, dtype=np.int64)
    streams = seed_streams(np.uint64(master_seed), 6)
    frozen_trials(
        n_trials, max_gen, cfg.lam, cfg.eps, cfg.c_b, cfg.c_h, cfg.alpha,
        cfg.beta, cfg.r, seed_c, 1 if freeze else 0,
        float(relax_rho), 0, 90,
        phi, phi_cls, c_last, s, n_cnt, t_touch, relaxed, relax_t,
        p_phi, p_cls, p_c, p_s, p_n, streams,
        z1, z2, g1n, g1off, nmsg, nacc,
        off_c, off_phi, off_s, off_t, off_gen, nrec,
    )
    assert nrec[1] == 0, "frozen-trial touch buffer overflowed"
    k = int(nrec[0])
    return {
        "Z1": z1, "Z2": z2, "gen1_n": g1n, "gen1_off": g1off,
        "n_messages": nmsg, "n_accepted": nacc,
        "offspring_c": off_c[:k], "offspring_phi_pre": off_phi[:k],
        "offspring_s_pre": off_s[:k], "offspring_t": off_t[:k],
        "offspring_gen": off_gen[:k],
        "n_trials": n_trials, "max_gen": max_gen, "seed_c": seed_c,
        "freeze": bool(freeze), "relax_rho": float(relax_rho),
    }
