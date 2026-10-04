"""A4 items P1, P1-delay, P2, P2-delay, P3, P4, P6 under the A6 pass rule.

A3 is respected throughout: operator checks (offspring counts on a frozen
background) and population checks (outbreak probability, trajectories in the full
finite-N process) are separate quantities, reported separately; a growth rate is
never used as an estimate of R.
"""

from __future__ import annotations

import importlib.util
import math
from dataclasses import replace

import numpy as np
from scipy import stats

from . import a6, engine as E
from . import predictions_s2 as PS
from .operator import run_frozen_operator
from .rng import derive_run_seed
from .runner import RunConfig, run_one, copy_state

_CFG = {}


def load_cfg(path):
    if path not in _CFG:
        spec = importlib.util.spec_from_file_location("stage2_config", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _CFG[path] = m
    return _CFG[path]


# ---------------------------------------------------------------- shared tools
def prepare_states(base_cfg, pulses, save_times, seed, lam_prep=0.0):
    """Run the campaign, then relax, saving the state at each requested time.

    Returns ({t: state}, info).  `lam_prep` is the broadcast rate during the
    preparation; it is 0 only where the campaign provably activates nobody, and
    the returned info records the activation count so that can be checked.
    """
    base_cfg = replace(base_cfg, extra_registry_angles=tuple(int(a) for a in pulses))
    cfg0 = replace(base_cfg, pulses=tuple((0.0, int(a)) for a in pulses),
                   lam=lam_prep, t_end=0.0, stop_on_extinction=False,
                   seed_agent=False)
    o = run_one(cfg0, seed, return_state=True)
    n_act_campaign = int(o["ever_active"].sum())
    st = o["state"]
    states, prev, k = {}, 0.0, 0
    for t in sorted(save_times):
        if t > prev:
            cfgr = replace(base_cfg, pulses=(), lam=lam_prep, t_end=t - prev,
                           stop_on_extinction=False, seed_agent=False)
            o = run_one(cfgr, derive_run_seed(seed, 777, k), init_state=st,
                        return_state=True)
            st = o["state"]
            prev = t
            k += 1
        states[t] = copy_state(st)
    info = dict(n_activated_by_campaign=n_act_campaign,
                max_abs_c_post_campaign=float(np.abs(states[min(save_times)]["c_last"]).max()))
    return states, info


def state_x(st):
    return float(st["s"].mean())


def outbreak_from(out, N, frac):
    return int(out["ever_active"].sum()) > frac * N


# =========================================================================== P1
def p1_base_cfg(cfgmod, N, lam):
    fx = cfgmod.P1["fixed"]
    return RunConfig(N=N, eps=fx["eps"], c_b=fx["c_b"], c_h=fx["c_h"],
                     alpha=fx["alpha"], beta=fx["beta"], r=fx["r"], lam=lam,
                     rho=fx["rho"], kappa=fx["kappa"], f=fx["f"],
                     initial_law="I2", compact_initial_classes=True,
                     t_end=0.0, stop_on_extinction=True)


def p1_operator_worker(args):
    """One background realisation: states at every delay, then frozen operator
    trials and the post-campaign stance law on each."""
    cfg_path, order, N, rep = args
    cfgmod = load_cfg(cfg_path)
    fx, dc = cfgmod.P1["fixed"], cfgmod.P1["declared"]
    delays = cfgmod.P1_DELAY["fixed"]["tau0_over_rho"]
    lam = dc["operator_lambda"]
    seed = derive_run_seed(cfgmod.MASTER_SEED, 1, hash(order) % 10007, N, rep)
    base = p1_base_cfg(cfgmod, N, 0.0)
    states, info = prepare_states(base, order, delays, seed)
    cfg_op = replace(base, lam=lam,
                     extra_registry_angles=tuple(int(a) for a in order))
    rows = []
    ntr = dc["operator_trials_per_background"]
    for tau in delays:
        st = states[tau]
        fr = run_frozen_operator(st, cfg_op, derive_run_seed(seed, 31, int(tau * 10)),
                                 ntr, max_gen=1, seed_c=1.0)
        g1n = fr["gen1_n"].sum()
        rows.append(dict(
            order=str(order), N=N, rep=rep, tau0=tau, lam=lam,
            x=state_x(st), Z1_mean=float(fr["Z1"].mean()),
            Z1_var=float(fr["Z1"].var(ddof=1)), n_trials=ntr,
            R_fr_mean=(float(fr["gen1_off"].sum() / g1n) if g1n else float("nan")),
            n_gen1=int(g1n),
            frac_phi_target=float(np.mean(np.isin(st["phi"], [0, 90]))),
            n_activated_by_campaign=info["n_activated_by_campaign"],
            max_abs_c=info["max_abs_c_post_campaign"], seed=seed))
    return rows


def p1_outbreak_worker(args):
    """One live invasion run: resume the prepared background, inject the A1 seed."""
    cfg_path, order, N, lam, tau0, rep = args
    cfgmod = load_cfg(cfg_path)
    fx = cfgmod.P1["fixed"]
    seed = derive_run_seed(cfgmod.MASTER_SEED, 11, hash(order) % 10007, N,
                           int(lam * 10), int(tau0 * 10), rep)
    base = p1_base_cfg(cfgmod, N, 0.0)
    states, info = prepare_states(base, order, [tau0], seed)
    cfg_live = replace(base, lam=lam, t_end=cfgmod.OUTBREAK_HORIZON,
                       seed_agent=True, stop_on_extinction=True,
                       extra_registry_angles=tuple(int(a) for a in order))
    o = run_one(cfg_live, derive_run_seed(seed, 99), init_state=states[tau0])
    si = o["seed_index"]
    Z = int(o["ever_active"].sum())
    return dict(order=str(order), N=N, lam=lam, tau0=tau0, rep=rep, seed=seed,
                Z=Z, Z_frac=Z / N,
                outbreak=int(Z > cfgmod.OUTBREAK_FRACTION * N),
                Z1_live=int(o["n_offspring"][si]),
                n_gen1=int((o["gen"] == 1).sum()),
                n_gen2=int((o["gen"] == 2).sum()),
                x_pre=state_x(states[tau0]),
                n_activated_by_campaign=info["n_activated_by_campaign"],
                t_final=float(o["agg"][E.A_TFINAL]))


# =========================================================================== P2
def p2_base_cfg(cfgmod, N, lam, rho=0.0):
    fx = cfgmod.P2["fixed"]
    return RunConfig(N=N, eps=fx["eps"], c_b=fx["c_b"], c_h=fx["c_h"],
                     alpha=fx["alpha"], beta=fx["beta"], r=fx["r"], lam=lam,
                     rho=rho, kappa=fx["kappa"], f=fx["f"],
                     initial_law="I1", t_end=0.0, stop_on_extinction=True)


def _p2_pulses(order):
    g = math.log(100.0)
    return tuple((k * g, int(a)) for k, a in enumerate(order))


def p2_operator_worker(args):
    cfg_path, order, N, rep, rho, delays, initial_law = args
    cfgmod = load_cfg(cfg_path)
    dc = cfgmod.P2["declared"]
    lam = dc["operator_lambda"]
    seed = derive_run_seed(cfgmod.MASTER_SEED, 2, hash(order) % 10007, N,
                           int(rho * 10), rep)
    base = p2_base_cfg(cfgmod, N, 0.0, rho=rho)
    if initial_law == "I2":
        base = replace(base, initial_law="I2", compact_initial_classes=True)
    pulses = _p2_pulses(order)
    base = replace(base, extra_registry_angles=tuple(int(a) for a in order))
    cfg0 = replace(base, pulses=pulses, t_end=pulses[-1][0], stop_on_extinction=False)
    o = run_one(cfg0, seed, return_state=True)
    n_act = int(o["ever_active"].sum())
    st = o["state"]
    states, prev, k = {}, 0.0, 0
    for t in sorted(delays):
        if t > prev:
            cfgr = replace(base, pulses=(), t_end=t - prev, stop_on_extinction=False)
            o = run_one(cfgr, derive_run_seed(seed, 555, k), init_state=st,
                        return_state=True)
            st = o["state"]; prev = t; k += 1
        states[t] = copy_state(st)
    cfg_op = replace(base, lam=lam)
    rows = []
    ntr = dc["operator_trials_per_background"]
    for tau in sorted(delays):
        stt = states[tau]
        fr = run_frozen_operator(stt, cfg_op, derive_run_seed(seed, 41, int(tau * 10)),
                                 ntr, max_gen=1, seed_c=1.0)
        rows.append(dict(order=str(order), N=N, rep=rep, rho=rho, tau0=tau,
                         lam=lam, initial_law=initial_law,
                         Z1_mean=float(fr["Z1"].mean()),
                         Z1_var=float(fr["Z1"].var(ddof=1)),
                         qT_measured=float(fr["n_accepted"].sum() /
                                           max(fr["n_messages"].sum(), 1)),
                         n_trials=ntr, n_activated_by_campaign=n_act,
                         max_abs_c=float(np.abs(stt["c_last"]).max()),
                         frac_phi_T=float(np.mean(stt["phi"] == 0)), seed=seed))
    return rows


def p2_outbreak_worker(args):
    cfg_path, order, N, lam, rep = args
    cfgmod = load_cfg(cfg_path)
    seed = derive_run_seed(cfgmod.MASTER_SEED, 21, hash(order) % 10007, N, rep)
    base = p2_base_cfg(cfgmod, N, 0.0)
    pulses = _p2_pulses(order)
    base = replace(base, extra_registry_angles=tuple(int(a) for a in order))
    cfg0 = replace(base, pulses=pulses, t_end=pulses[-1][0], stop_on_extinction=False)
    o = run_one(cfg0, seed, return_state=True)
    cfg_live = replace(base, lam=lam, t_end=cfgmod.OUTBREAK_HORIZON,
                       seed_agent=True, stop_on_extinction=True)
    o2 = run_one(cfg_live, derive_run_seed(seed, 98), init_state=o["state"])
    Z = int(o2["ever_active"].sum())
    return dict(order=str(order), N=N, lam=lam, rep=rep, seed=seed, Z=Z,
                Z_frac=Z / N, outbreak=int(Z > cfgmod.OUTBREAK_FRACTION * N),
                Z1_live=int(o2["n_offspring"][o2["seed_index"]]),
                n_activated_by_campaign=int(o["ever_active"].sum()))


# =========================================================================== P3
def p3_base_cfg(cfgmod, N, lam):
    fx = cfgmod.P3["fixed"]
    return RunConfig(N=N, eps=fx["eps"], c_b=fx["c_b"], c_h=fx["c_h"],
                     alpha=fx["alpha"], beta=fx["beta"], r=fx["r"], lam=lam,
                     rho=fx["rho"], kappa=fx["kappa"], f=fx["f"],
                     initial_law="I2", compact_initial_classes=True,
                     t_end=0.0, stop_on_extinction=True)


def p3_operator_worker(args):
    """Frozen diagnostic R_fr(tau0) and the time-dependent E Z_2, on one background."""
    cfg_path, order, N, rep = args[:4]
    delays = args[4] if len(args) > 4 else [0.0]
    cfgmod = load_cfg(cfg_path)
    fx, dc = cfgmod.P3["fixed"], cfgmod.P3["declared"]
    lam = dc["operator_lambda"]
    seed = derive_run_seed(cfgmod.MASTER_SEED, 3, hash(order) % 10007, N, rep)
    base = p3_base_cfg(cfgmod, N, 0.0)
    states, info = prepare_states(base, order, sorted(set([0.0] + list(delays))),
                                  seed)
    st = states[0.0]
    cfg_op = replace(base, lam=lam,
                     extra_registry_angles=tuple(int(a) for a in order))
    ntr = dc["operator_trials_per_background"]
    fr = run_frozen_operator(st, cfg_op, derive_run_seed(seed, 61), ntr,
                             max_gen=1, seed_c=1.0, freeze=True)
    # R_fr at each delay: the next-generation operator of the RELAXED state, which
    # is what "convergence of both orders to R = 0.0912 lambda at large delay"
    # registers (the offspring count of a typical offspring, not of the seed)
    R_fr_delay = {}
    for t in delays:
        f2 = run_frozen_operator(states[t], cfg_op,
                                 derive_run_seed(seed, 63, int(t * 10)), ntr,
                                 max_gen=1, seed_c=1.0, freeze=True)
        g = f2["gen1_n"].sum()
        R_fr_delay[t] = float(f2["gen1_off"].sum() / g) if g else float("nan")
    lv = run_frozen_operator(st, cfg_op, derive_run_seed(seed, 62),
                             dc["EZ2_replicates"], max_gen=1, seed_c=1.0,
                             freeze=False)
    g1 = fr["gen1_n"].sum()
    # measured post-campaign weights, for the C3.18 cross-check
    phi, c = st["phi"], st["c_last"]
    acc = np.cos(np.radians(0 - phi)) ** 2
    wH = float(np.mean(acc * (np.abs(c) > 1e-12)))
    wL = float(np.mean(acc * (np.abs(c) <= 1e-12)))
    return dict(order=str(order), N=N, rep=rep, lam=lam, seed=seed,
                R_fr_mean=float(fr["gen1_off"].sum() / g1) if g1 else float("nan"),
                n_gen1_frozen=int(g1), n_trials_frozen=ntr,
                Z1_frozen_mean=float(fr["Z1"].mean()),
                EZ2_mean=float(lv["Z2"].mean()), EZ2_var=float(lv["Z2"].var(ddof=1)),
                EZ1_live_mean=float(lv["Z1"].mean()),
                n_trials_live=dc["EZ2_replicates"],
                w_H_measured=wH, w_L_measured=wL,
                **{f"R_fr_tau{t:g}": v for t, v in R_fr_delay.items()},
                n_activated_by_campaign=info["n_activated_by_campaign"],
                max_abs_c=info["max_abs_c_post_campaign"])


def p3_outbreak_worker(args):
    cfg_path, order, N, lam, tau0, rep = args
    cfgmod = load_cfg(cfg_path)
    seed = derive_run_seed(cfgmod.MASTER_SEED, 31, hash(order) % 10007,
                           int(tau0 * 10), rep)
    base = p3_base_cfg(cfgmod, N, 0.0)
    states, info = prepare_states(base, order, [tau0], seed)
    cfg_live = replace(base, lam=lam, t_end=cfgmod.OUTBREAK_HORIZON,
                       seed_agent=True, stop_on_extinction=True,
                       extra_registry_angles=tuple(int(a) for a in order))
    o = run_one(cfg_live, derive_run_seed(seed, 97), init_state=states[tau0])
    Z = int(o["ever_active"].sum())
    return dict(order=str(order), N=N, lam=lam, tau0=tau0, rep=rep, seed=seed,
                Z=Z, Z_frac=Z / N,
                outbreak=int(Z > cfgmod.OUTBREAK_FRACTION * N),
                Z1_live=int(o["n_offspring"][o["seed_index"]]),
                n_gen2=int((o["gen"] == 2).sum()),
                n_activated_by_campaign=info["n_activated_by_campaign"])


# =========================================================================== P4
def p4_worker(args):
    cfg_path, lam, f, rep = args[:4]
    N_override = args[4] if len(args) > 4 else None
    cfgmod = load_cfg(cfg_path)
    fx, dc = cfgmod.P4["fixed"], cfgmod.P4["declared"]
    N = N_override if N_override else fx["N"]
    seed = derive_run_seed(cfgmod.MASTER_SEED, 4, int(lam * 100),
                           int(round(f * 1e6)), rep, N)
    cfg = RunConfig(N=N, eps=fx["eps"], c_b=fx["c_b"], c_h=0.01,
                    alpha=fx["alpha"], beta=fx["beta"], r=fx["r"], lam=lam,
                    rho=fx["rho"], kappa=fx["kappa"], f=f,
                    pulses=((0.0, fx["pulse_angle_deg"]),), initial_law="I1",
                    t_end=dc["t_end"], stop_on_extinction=True,
                    sample_times=tuple(fx["horizons"]))
    o = run_one(cfg, seed)
    A = {h: (float(a) / N if a >= 0 else 0.0)
         for h, a in zip(fx["horizons"], o["sampleA"])}
    return dict(lam=lam, f=f, rep=rep, seed=seed, N=N,
                realized_reach=o["realized_reach"],
                **{f"A_{int(h)}": A[h] for h in fx["horizons"]},
                t_final=float(o["agg"][E.A_TFINAL]),
                intA=float(o["agg"][E.A_INTA] / N))


# =========================================================================== P6
def p6_worker(args):
    cfg_path, case, rep = args
    cfgmod = load_cfg(cfg_path)
    fx, dc = cfgmod.P6["fixed"], cfgmod.P6["declared"]
    c = fx[case]
    N = fx["N"]
    t_end = dc["t_end_A"] if case == "A" else dc["t_end_B"]
    grid = np.arange(0.0, t_end + 1e-9, dc["sample_dt"])
    seed = derive_run_seed(cfgmod.MASTER_SEED, 6, ord(case), rep)
    cfg = RunConfig(N=N, eps=c["eps"], c_b=c["c_b"], c_h=c["c_h"],
                    alpha=c["alpha"], beta=c["beta"], r=c["r"], lam=c["lam"],
                    rho=c["rho"], kappa=c["kappa"], f=c["f"],
                    pulses=((0.0, 0),), initial_law="I1", t_end=t_end,
                    stop_on_extinction=True, sample_times=tuple(grid))
    o = run_one(cfg, seed)
    A = np.where(o["sampleA"] >= 0, o["sampleA"], 0).astype(float) / N
    out = dict(case=case, rep=rep, seed=seed, N=N, lam=c["lam"],
               t_final=float(o["agg"][E.A_TFINAL]),
               intA=float(o["agg"][E.A_INTA] / N))
    if case == "A":
        lev = c["crossing_level"]
        out["t_dagger"] = _first_down_crossing(grid, A, lev)
    # accumulated collapse index lambda * int A dt, reported on an activity grid
    dt = dc["sample_dt"]
    cum = np.cumsum(A) * dt * c["lam"]
    out["A_trace"] = A
    out["cum_trace"] = cum
    return out


def _first_down_crossing(t, A, level):
    """First time A(t) crosses `level` downward, by linear interpolation."""
    above = A > level
    for i in range(1, len(A)):
        if above[i - 1] and not above[i]:
            a0, a1 = A[i - 1], A[i]
            if a0 == a1:
                return float(t[i])
            return float(t[i - 1] + (a0 - level) / (a0 - a1) * (t[i] - t[i - 1]))
    return float("nan")
