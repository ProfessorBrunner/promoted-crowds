"""Exact event-driven simulator of the finite-N process of specification v0.6.

Design A1 is implemented literally:

  * four event types -- Poisson broadcast (rate lambda, active agents only),
    Poisson reset (rho), Poisson reconsideration (kappa), and DETERMINISTIC
    activity shut-off;
  * every shut-off deadline lives in the event queue and is REFRESHED whenever
    that agent's conviction changes (lazy invalidation by a per-agent version
    counter).  Because the queue is a single global min-heap containing the
    deadlines, no step can jump past a deadline;
  * campaign pulses at prescribed times, applied once to every cohort member,
    coincident pulses composed in index order with no clock event between them
    (they are processed atomically, outside the heap, with priority at an exact
    time tie);
  * one uniformly random *other* recipient per broadcast;
  * the message transition applied in the specified order (1) accept/reject and
    orientation, (2) counter increment, (3) deposit r^(n-1) cos 2theta (+alpha |
    -beta), (4) clip to [-1, 1], (5) stance with the previous stance retained at
    an exact tie;
  * decay applied analytically between events: c(t) = c_last exp(-eps (t-t_last));
  * framing classes carried as explicit integer identifiers (see angles.py);
  * three agent classes under one engine: 0 = process, 1 = outcome-memory
    automaton, 2 = Bloch-mean surrogate.

Nothing in this file is an approximation of the process.
"""

import math

import numpy as np
from numba import njit

from .rng import next_double, next_exp, next_below

# ---------------------------------------------------------------- event kinds
K_SHUTOFF = 0
K_BROADCAST = 1
K_RESET = 2
K_RECONS = 3

# ------------------------------------------------------------- agent classes
AC_PROCESS = 0
AC_AUTOMATON = 1
AC_SURROGATE = 2

# ------------------------------------------------------------- agg[] indices
A_INTA = 0          # integral of (active count) dt over [0, t_final]
A_INTA_WIN = 1      # same over [t_measure_start, t_final]
A_NBROADCAST = 2
A_NRECEIPT = 3
A_NSHUTOFF = 4
A_NRESET = 5
A_NRECONS = 6
A_NPULSEDEL = 7
A_NEXO = 8
A_OVERFLOW = 9
A_TFINAL = 10
A_MAXHEAP = 11
A_NACCEPT = 12
A_NREJECT = 13
A_WINLEN = 14
N_AGG = 15

_DEG2RAD = 0.017453292519943295


@njit(cache=True, inline="always")
def _cosd_i(deg):
    """cos of an integer number of degrees; exact at every multiple of 90."""
    m = deg % 360
    if m == 0:
        return 1.0
    elif m == 90:
        return 0.0
    elif m == 180:
        return -1.0
    elif m == 270:
        return 0.0
    return math.cos(m * _DEG2RAD)


# ------------------------------------------------------------------- min-heap
@njit(cache=True, inline="always")
def _hpush(h_t, h_kind, h_ag, h_ver, ctr, t, kind, ag, ver):
    i = ctr[1]
    if i >= h_t.shape[0]:
        ctr[3] = 1
        return
    h_t[i] = t
    h_kind[i] = kind
    h_ag[i] = ag
    h_ver[i] = ver
    i2 = i + 1
    ctr[1] = i2
    if i2 > ctr[2]:
        ctr[2] = i2
    while i > 0:
        p = (i - 1) >> 1
        if h_t[i] < h_t[p]:
            h_t[i], h_t[p] = h_t[p], h_t[i]
            h_kind[i], h_kind[p] = h_kind[p], h_kind[i]
            h_ag[i], h_ag[p] = h_ag[p], h_ag[i]
            h_ver[i], h_ver[p] = h_ver[p], h_ver[i]
            i = p
        else:
            break


@njit(cache=True, inline="always")
def _hpop(h_t, h_kind, h_ag, h_ver, ctr):
    t = h_t[0]
    kind = h_kind[0]
    ag = h_ag[0]
    ver = h_ver[0]
    nsz = ctr[1] - 1
    ctr[1] = nsz
    if nsz > 0:
        h_t[0] = h_t[nsz]
        h_kind[0] = h_kind[nsz]
        h_ag[0] = h_ag[nsz]
        h_ver[0] = h_ver[nsz]
        i = 0
        while True:
            l = 2 * i + 1
            r2 = l + 1
            m = i
            if l < nsz and h_t[l] < h_t[m]:
                m = l
            if r2 < nsz and h_t[r2] < h_t[m]:
                m = r2
            if m == i:
                break
            h_t[i], h_t[m] = h_t[m], h_t[i]
            h_kind[i], h_kind[m] = h_kind[m], h_kind[i]
            h_ag[i], h_ag[m] = h_ag[m], h_ag[i]
            h_ver[i], h_ver[m] = h_ver[m], h_ver[i]
            i = m
    return t, kind, ag, ver


# --------------------------------------------------------- message transition
@njit(cache=True)
def _deliver(
    j, th, jc, t,
    agent_class, eps, c_b, c_h, alpha, beta, lam, r,
    phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor, last_out, last_fr,
    active, ver_b, ver_s, cls_active, ctr,
    h_t, h_kind, h_ag, h_ver, streams, agg,
    ever_active, t_first_act, t_first_deact, t_last_deact, n_intervals,
    act_time, act_since,
):
    """Deliver one message of integer angle `th` (class id `jc`) to agent `j`."""
    # analytic decay to the event time
    c = c_last[j] * math.exp(-eps * (t - t_last[j]))
    was_active = active[j]
    old_cls = phi_cls[j]

    # (1) accept with probability cos^2(theta - phi); else reject
    if agent_class == AC_PROCESS:
        cc = _cosd_i(th - phi[j])
        p = cc * cc
    elif agent_class == AC_AUTOMATON:
        # state = (last framing, last outcome); table cos^2(theta_j - theta_i)
        if last_out[j] == 1:
            cc = _cosd_i(th - last_fr[j])
        else:
            cc = _cosd_i(th - last_fr[j] - 90)
        p = cc * cc
    else:
        # Bloch-mean surrogate: tau <- tau cos 2(theta - a); a <- theta;
        # then the response coin is (1 + tau)/2, with no outcome-dependent update
        tau[j] = tau[j] * _cosd_i(2 * (th - anchor[j]))
        anchor[j] = th
        p = 0.5 * (1.0 + tau[j])

    uu = next_double(streams, 2)
    acc = 1 if uu < p else 0
    if acc == 1:
        agg[A_NACCEPT] += 1.0
    else:
        agg[A_NREJECT] += 1.0

    # orientation / memory update
    if agent_class == AC_PROCESS:
        if acc == 1:
            phi[j] = th
        else:
            phi[j] = (th + 90) % 180
    elif agent_class == AC_AUTOMATON:
        last_fr[j] = th
        last_out[j] = acc
        if acc == 1:
            phi[j] = th
        else:
            phi[j] = (th + 90) % 180
    else:
        phi[j] = th  # the surrogate's declared broadcast angle is its anchor a
    phi_cls[j] = jc

    # (2) counter increment
    n_cnt[j, jc] += 1
    nn = n_cnt[j, jc]

    # (3) deposit with the novelty weight r^(n-1)
    w = r ** (nn - 1)
    if acc == 1:
        dep = w * _cosd_i(2 * th) * alpha
    else:
        dep = -w * _cosd_i(2 * th) * beta
    c = c + dep

    # (4) clip
    if c > 1.0:
        c = 1.0
    elif c < -1.0:
        c = -1.0

    # (5) stance; previous stance retained strictly between -c_h and +c_h,
    # and "previous stance retained at an exact tie", i.e. when both branches
    # of the rule fire at once.  Since c_h >= 0, that happens only at
    # c_h = 0 and c = 0, and the first test below catches exactly that case.
    if c >= c_h and c <= -c_h:
        pass
    elif c >= c_h:
        s[j] = 1
    elif c <= -c_h:
        s[j] = -1

    c_last[j] = c
    t_last[j] = t
    agg[A_NRECEIPT] += 1.0

    # activity gate and shut-off deadline refresh
    absc = -c if c < 0.0 else c
    now_active = absc > c_b
    if was_active == 1:
        if now_active:
            if old_cls != jc:
                cls_active[old_cls] -= 1
                cls_active[jc] += 1
            ver_s[j] += 1
            _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                   t + math.log(absc / c_b) / eps, K_SHUTOFF, j, ver_s[j])
        else:
            cls_active[old_cls] -= 1
            ctr[0] -= 1
            active[j] = 0
            ver_b[j] += 1
            ver_s[j] += 1
            act_time[j] += t - act_since[j]
            if n_intervals[j] == 1:
                t_first_deact[j] = t
            t_last_deact[j] = t
    else:
        if now_active:
            cls_active[jc] += 1
            ctr[0] += 1
            active[j] = 1
            ver_s[j] += 1
            _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                   t + math.log(absc / c_b) / eps, K_SHUTOFF, j, ver_s[j])
            if lam > 0.0:
                _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                       t + next_exp(streams, 0, lam), K_BROADCAST, j, ver_b[j])
            n_intervals[j] += 1
            act_since[j] = t
            if ever_active[j] == 0:
                ever_active[j] = 1
                t_first_act[j] = t
    return acc


# ------------------------------------------------------------------ main loop
@njit(cache=True)
def simulate(
    N, agent_class,
    eps, c_b, c_h, alpha, beta, lam, rho, kappa, r,
    delta_deg, cls_target, cls_dp, cls_dm,
    phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor, last_out, last_fr,
    u,
    pulse_t, pulse_ang, pulse_cls,
    exo_t, exo_ag, exo_ang, exo_cls,
    t_end, t_measure_start, stop_on_extinction,
    streams, heap_cap,
    ever_active, t_first_act, t_first_deact, t_last_deact, n_intervals, act_time,
    pulse_out, sampleA_t, sampleA,
    agg, intAj, intAj_win,
):
    J = n_cnt.shape[1]
    h_t = np.empty(heap_cap, dtype=np.float64)
    h_kind = np.empty(heap_cap, dtype=np.int8)
    h_ag = np.empty(heap_cap, dtype=np.int32)
    h_ver = np.empty(heap_cap, dtype=np.int32)
    ctr = np.zeros(4, dtype=np.int64)        # n_active, heap_size, max_heap, overflow
    cls_active = np.zeros(J, dtype=np.int64)
    active = np.zeros(N, dtype=np.int8)
    ver_b = np.zeros(N, dtype=np.int32)
    ver_s = np.zeros(N, dtype=np.int32)
    act_since = np.zeros(N, dtype=np.float64)

    n_pul = pulse_t.shape[0]
    n_exo = exo_t.shape[0]

    # ---- initial conditions: activity gate, deadlines, clocks
    for j in range(N):
        absc = -c_last[j] if c_last[j] < 0.0 else c_last[j]
        if absc > c_b:
            active[j] = 1
            ctr[0] += 1
            cls_active[phi_cls[j]] += 1
            ever_active[j] = 1
            t_first_act[j] = 0.0
            n_intervals[j] = 1
            act_since[j] = 0.0
            ver_s[j] += 1
            _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                   math.log(absc / c_b) / eps, K_SHUTOFF, j, ver_s[j])
            if lam > 0.0:
                _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                       next_exp(streams, 0, lam), K_BROADCAST, j, ver_b[j])
        if rho > 0.0:
            _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                   next_exp(streams, 0, rho), K_RESET, j, 0)
        if kappa > 0.0:
            _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                   next_exp(streams, 0, kappa), K_RECONS, j, 0)

    t_prev = 0.0
    pi = 0
    xi = 0
    sg = 0
    n_s = sampleA_t.shape[0]
    INF = 1.0e300

    while True:
        th_next = INF
        if ctr[1] > 0:
            th_next = h_t[0]
        tp_next = INF
        if pi < n_pul:
            tp_next = pulse_t[pi]
        tx_next = INF
        if xi < n_exo:
            tx_next = exo_t[xi]
        t_next = th_next
        if tp_next < t_next:
            t_next = tp_next
        if tx_next < t_next:
            t_next = tx_next
        if t_next > t_end or t_next >= INF:
            break

        # ---- advance the clock, accumulating activity integrals and samples
        while sg < n_s and sampleA_t[sg] < t_next:
            sampleA[sg] = ctr[0]
            sg += 1
        dt = t_next - t_prev
        if dt > 0.0:
            agg[A_INTA] += ctr[0] * dt
            for k in range(J):
                intAj[k] += cls_active[k] * dt
            a0 = t_prev if t_prev > t_measure_start else t_measure_start
            if t_next > a0:
                dw = t_next - a0
                agg[A_INTA_WIN] += ctr[0] * dw
                for k in range(J):
                    intAj_win[k] += cls_active[k] * dw
        t_prev = t_next

        # ---- prescribed events have priority at an exact time tie
        if tp_next == t_next:
            tp = pulse_t[pi]
            while pi < n_pul and pulse_t[pi] == tp:
                th = pulse_ang[pi]
                jc = pulse_cls[pi]
                for j in range(N):
                    if u[j] == 1:
                        a = _deliver(
                            j, th, jc, tp,
                            agent_class, eps, c_b, c_h, alpha, beta, lam, r,
                            phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor,
                            last_out, last_fr,
                            active, ver_b, ver_s, cls_active, ctr,
                            h_t, h_kind, h_ag, h_ver, streams, agg,
                            ever_active, t_first_act, t_first_deact, t_last_deact,
                            n_intervals, act_time, act_since,
                        )
                        pulse_out[j, pi] = a
                        agg[A_NPULSEDEL] += 1.0
                pi += 1
        elif tx_next == t_next:
            j = exo_ag[xi]
            _deliver(
                j, exo_ang[xi], exo_cls[xi], t_next,
                agent_class, eps, c_b, c_h, alpha, beta, lam, r,
                phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor,
                last_out, last_fr,
                active, ver_b, ver_s, cls_active, ctr,
                h_t, h_kind, h_ag, h_ver, streams, agg,
                ever_active, t_first_act, t_first_deact, t_last_deact,
                n_intervals, act_time, act_since,
            )
            agg[A_NEXO] += 1.0
            xi += 1
        else:
            t_ev, kind, j, ver = _hpop(h_t, h_kind, h_ag, h_ver, ctr)
            if kind == K_SHUTOFF:
                if ver == ver_s[j] and active[j] == 1:
                    # at the deadline |c| equals c_b exactly, by construction
                    c_last[j] = c_b if c_last[j] >= 0.0 else -c_b
                    t_last[j] = t_ev
                    cls_active[phi_cls[j]] -= 1
                    ctr[0] -= 1
                    active[j] = 0
                    ver_b[j] += 1
                    act_time[j] += t_ev - act_since[j]
                    if n_intervals[j] == 1:
                        t_first_deact[j] = t_ev
                    t_last_deact[j] = t_ev
                    agg[A_NSHUTOFF] += 1.0
            elif kind == K_BROADCAST:
                if ver == ver_b[j] and active[j] == 1:
                    th = phi[j]
                    jc = phi_cls[j]
                    k = next_below(streams, 1, N - 1)
                    if k >= j:
                        k += 1
                    _deliver(
                        k, th, jc, t_ev,
                        agent_class, eps, c_b, c_h, alpha, beta, lam, r,
                        phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor,
                        last_out, last_fr,
                        active, ver_b, ver_s, cls_active, ctr,
                        h_t, h_kind, h_ag, h_ver, streams, agg,
                        ever_active, t_first_act, t_first_deact, t_last_deact,
                        n_intervals, act_time, act_since,
                    )
                    agg[A_NBROADCAST] += 1.0
                    _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                           t_ev + next_exp(streams, 0, lam), K_BROADCAST, j, ver_b[j])
            elif kind == K_RESET:
                old_cls = phi_cls[j]
                newphi = 0 if s[j] == 1 else 90
                phi[j] = newphi
                phi_cls[j] = cls_target
                if agent_class == AC_AUTOMATON:
                    last_fr[j] = newphi
                    last_out[j] = 1
                elif agent_class == AC_SURROGATE:
                    anchor[j] = newphi
                if active[j] == 1 and old_cls != cls_target:
                    cls_active[old_cls] -= 1
                    cls_active[cls_target] += 1
                agg[A_NRESET] += 1.0
                _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                       t_ev + next_exp(streams, 0, rho), K_RESET, j, 0)
            else:  # K_RECONS
                old_cls = phi_cls[j]
                base = 0 if s[j] == 1 else 90
                if next_double(streams, 0) < 0.5:
                    newphi = (base + delta_deg) % 180
                    newcls = cls_dp
                else:
                    newphi = (base - delta_deg) % 180
                    newcls = cls_dm
                phi[j] = newphi
                phi_cls[j] = newcls
                if agent_class == AC_AUTOMATON:
                    last_fr[j] = newphi
                    last_out[j] = 1
                elif agent_class == AC_SURROGATE:
                    anchor[j] = newphi
                if active[j] == 1 and old_cls != newcls:
                    cls_active[old_cls] -= 1
                    cls_active[newcls] += 1
                agg[A_NRECONS] += 1.0
                _hpush(h_t, h_kind, h_ag, h_ver, ctr,
                       t_ev + next_exp(streams, 0, kappa), K_RECONS, j, 0)

        if ctr[3] == 1:
            break
        if (stop_on_extinction == 1 and ctr[0] == 0 and pi >= n_pul and xi >= n_exo
                and rho == 0.0 and kappa == 0.0):
            break

    # ---- close out at t_end (or at the frozen time)
    t_fin = t_end
    if t_prev > t_fin:
        t_fin = t_prev
    dt = t_fin - t_prev
    if dt > 0.0:
        agg[A_INTA] += ctr[0] * dt
        for k in range(J):
            intAj[k] += cls_active[k] * dt
        a0 = t_prev if t_prev > t_measure_start else t_measure_start
        if t_fin > a0:
            dw = t_fin - a0
            agg[A_INTA_WIN] += ctr[0] * dw
            for k in range(J):
                intAj_win[k] += cls_active[k] * dw
    while sg < n_s:
        if sampleA_t[sg] <= t_fin:
            sampleA[sg] = ctr[0]
        else:
            sampleA[sg] = -1
        sg += 1
    for j in range(N):
        if active[j] == 1:
            act_time[j] += t_fin - act_since[j]
        c_last[j] = c_last[j] * math.exp(-eps * (t_fin - t_last[j]))
        t_last[j] = t_fin
    agg[A_TFINAL] = t_fin
    agg[A_MAXHEAP] = ctr[2]
    agg[A_OVERFLOW] = ctr[3]
    w0 = t_fin - t_measure_start
    agg[A_WINLEN] = w0 if w0 > 0.0 else 0.0
