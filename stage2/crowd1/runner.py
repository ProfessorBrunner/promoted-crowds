"""Configuration objects and the Python driver around the njit kernel.

Initial laws (specification v0.6 INITIAL LAWS, design A1):
  I1  fresh-aligned     phi = T_+ = 0, c = 0, s = +, n = 0
  I2  fresh-isotropic   phi uniform, c = 0, s = + unless declared, n = 0
  I3  stationary silent background at (rho, kappa) with declared stance law p_+,
      obtained -- as design A1 requires -- by RELAXING the silent process from
      the declared stance law, not by sampling the closed-form stationary law.

I2 note (declared implementation choice, see README "Deviations"): orientations
in this engine are exact integer degrees, so "phi uniform" is realized as the
uniform law on the 180 integer-degree rays of [0, 180).  Every expectation that
T4-T6 register is *exactly* preserved by that discretization, because
  (1/180) sum_{d=0}^{179} cos(2 d deg + c) = 0  and
  (1/180) sum_{d=0}^{179} cos(4 d deg + c) = 0
for any constant c, hence E[cos^2(theta - phi)] = 1/2 and E[cos^2 2(theta - a)]
= 1/2 exactly, as under the continuous law.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np

from . import engine as E
from .angles import build_registry, reduce180, cosd, cos2d
from .rng import (seed_streams, python_generator, STREAM_COHORT, STREAM_INITIAL,
                  STREAM_EXOGENOUS)

AGENT_CLASS_IDS = {"process": 0, "automaton": 1, "surrogate": 2}


@dataclass
class RunConfig:
    # --- population and agent class
    N: int
    agent_class: str = "process"

    # --- parameters of specification v0.6
    eps: float = 1.0
    c_b: float = 0.5
    c_h: float = 0.01
    alpha: float = 1.0
    beta: float = 0.0
    lam: float = 0.0
    rho: float = 0.0
    kappa: float = 0.0
    # rho/kappa used in the MAIN phase; default None = same as rho/kappa.
    # Only ever set to 0 for the surrogate, whose (a, tau) reset/reconsideration
    # rule the specification does not declare (C5.0: "All tests below have
    # rho = kappa = 0").  Setting them to 0 in the main phase is exact wherever
    # the main phase contains only coincident pulses, because no clock event may
    # occur between coincident pulses and the run ends at the pulse time.
    rho_main: float | None = None
    kappa_main: float | None = None
    r: float = 1.0
    delta_deg: int | None = None

    # --- campaign
    f: float = 1.0
    pulses: tuple = ()               # ((time, angle_deg), ...)

    # --- initial law
    initial_law: str = "I1"          # "I1" | "I2" | "I3" | "declared"
    p_plus: float = 0.5              # I3 / declared stance law
    i3_relax_time: float | None = None
    declared_phi: int | None = None  # for initial_law == "declared"
    declared_c: float = 0.0
    declared_s: int = 1
    M_plus: float = 0.5              # for initial_law == "two_camps"
    two_camps_c: float = 1.0         # |c| on every agent of a two-camp start

    # --- horizon and measurement
    t_end: float = 10.0
    t_measure_start: float = 0.0
    stop_on_extinction: bool = True
    sample_times: tuple = ()

    # --- prescribed exogenous message input (T3 only)
    exo_rate_fn: str | None = None   # "const" | "exp_decay"
    exo_rate_nu0: float = 0.0
    exo_rate_gamma: float = 0.0
    exo_t_end: float = 0.0
    exo_angle_deg: int = 0

    # --- Stage 2 additions (defaults reproduce Stage 1 behaviour exactly)
    # Angles that must have a framing-class identifier even when `pulses` is empty,
    # so that a run RESUMED from a saved state keeps the identifier space of the
    # campaign that produced it.
    extra_registry_angles: tuple = ()
    compact_initial_classes: bool = False  # one placeholder id for silent I2/I3 rays
    seed_agent: bool = False               # inject the A1 invasion seed at t = 0
    broadcast_only_seed: bool = False      # only the seed broadcasts (operator check)
    freeze_background: bool = False        # recipients evaluated at the saved state

    # --- engine
    heap_cap_per_agent: int = 12

    def to_json(self):
        d = asdict(self)
        d["pulses"] = [list(p) for p in self.pulses]
        d["sample_times"] = list(self.sample_times)
        return d


def _exo_intensity_integral(cfg: RunConfig) -> float:
    if cfg.exo_rate_fn is None:
        return 0.0
    if cfg.exo_rate_fn == "const":
        return cfg.exo_rate_nu0 * cfg.exo_t_end
    if cfg.exo_rate_fn == "exp_decay":
        g = cfg.exo_rate_gamma
        return cfg.exo_rate_nu0 * (1.0 - np.exp(-g * cfg.exo_t_end)) / g
    raise ValueError(cfg.exo_rate_fn)


def build_registry_for(cfg: RunConfig):
    campaign_angles = [int(a) for (_, a) in cfg.pulses]
    campaign_angles += [int(a) for a in cfg.extra_registry_angles
                        if int(a) not in campaign_angles]
    extra = []
    if cfg.exo_rate_fn is not None:
        extra.append(int(cfg.exo_angle_deg))
    if cfg.declared_phi is not None:
        extra.append(int(cfg.declared_phi))
    continuous_init = cfg.initial_law in ("I2",)
    full = continuous_init and not cfg.compact_initial_classes
    reg, info = build_registry(
        campaign_angles,
        delta_deg=cfg.delta_deg,
        extra_angles=extra,
        full_bases=full,
        initial_only=continuous_init and cfg.compact_initial_classes,
    )
    return reg, info


def run_one(cfg: RunConfig, master_seed: int, registry=None, reg_info=None,
            init_state=None, return_state=False):
    """Run one replicate.  Returns a dict of per-agent arrays and aggregates.

    `init_state` resumes from a previously saved state dict (time origin reset to
    0, with c_last already the conviction at the save instant).  `return_state`
    adds a deep-copied `state` entry to the result, suitable for resuming.
    """
    if cfg.N < 2:
        raise ValueError("N >= 2 required (a broadcast needs one *other* recipient)")
    rho_main = cfg.rho if cfg.rho_main is None else cfg.rho_main
    kappa_main = cfg.kappa if cfg.kappa_main is None else cfg.kappa_main
    if cfg.agent_class == "surrogate" and (rho_main > 0.0 or kappa_main > 0.0):
        raise NotImplementedError(
            "the surrogate of C5.0 is declared only for rho = kappa = 0; no "
            "reset/reconsideration rule for (a, tau) is given by the specification"
        )
    if registry is None:
        registry, reg_info = build_registry_for(cfg)

    N = int(cfg.N)
    J = reg_info["n_classes"]
    ac = AGENT_CLASS_IDS[cfg.agent_class]

    if init_state is not None:
        return _run_from_state(cfg, master_seed, registry, reg_info, init_state,
                               return_state)

    g_cohort = python_generator(master_seed, STREAM_COHORT)
    g_init = python_generator(master_seed, STREAM_INITIAL)
    g_exo = python_generator(master_seed, STREAM_EXOGENOUS)

    # ---- cohort, drawn once
    u = (g_cohort.random(N) < cfg.f).astype(np.int8)
    realized_reach = float(u.mean())

    # ---- initial law
    phi = np.zeros(N, dtype=np.int32)
    c0 = np.zeros(N, dtype=np.float64)
    s0 = np.ones(N, dtype=np.int8)
    if cfg.initial_law == "I1":
        phi[:] = 0
    elif cfg.initial_law == "I2":
        phi[:] = g_init.integers(0, 180, size=N).astype(np.int32)
        if cfg.p_plus != 0.5 or cfg.declared_s != 1:
            s0[:] = np.where(g_init.random(N) < cfg.p_plus, 1, -1).astype(np.int8)
    elif cfg.initial_law == "declared":
        phi[:] = int(cfg.declared_phi)
        c0[:] = cfg.declared_c
        s0[:] = cfg.declared_s
    elif cfg.initial_law == "two_camps":
        # T2 / R6 / C2.24 invariant two-orientation population: conviction sign
        # matches orientation and stance, |c| = cfg.two_camps_c on every agent
        # (default 1.0 reproduces Stage 1 T2 exactly; P9 declares 0.6).
        camp = g_init.random(N) < cfg.M_plus
        phi[:] = np.where(camp, 0, 90).astype(np.int32)
        c0[:] = np.where(camp, cfg.two_camps_c, -cfg.two_camps_c)
        s0[:] = np.where(camp, 1, -1).astype(np.int8)
    elif cfg.initial_law == "I3":
        s0[:] = np.where(g_init.random(N) < cfg.p_plus, 1, -1).astype(np.int8)
        phi[:] = np.where(s0 == 1, 0, 90).astype(np.int32)
    else:
        raise ValueError(cfg.initial_law)

    if cfg.compact_initial_classes and cfg.initial_law == "I2":
        assert np.all(np.abs(c0) <= cfg.c_b), (
            "compact initial classes require every agent silent at t = 0")
        phi_cls = np.full(N, reg_info["class_initial_only"], dtype=np.int32)
    else:
        lut = {int(a): int(registry.of(int(a))) for a in np.unique(phi)}
        phi_cls = np.array([lut[int(a)] for a in phi], dtype=np.int32)

    n_cnt = np.zeros((N, J), dtype=np.int32)
    tau = np.ones(N, dtype=np.float64)
    anchor = phi.copy()
    last_out = np.ones(N, dtype=np.int8)
    last_fr = phi.copy()
    t_last = np.zeros(N, dtype=np.float64)
    c_last = c0.copy()

    streams = seed_streams(np.uint64(master_seed), 6)

    # ---- I3: relax the silent process from the declared stance law
    i3_relax_info = None
    if cfg.initial_law == "I3":
        if cfg.rho <= 0.0 and cfg.kappa <= 0.0:
            raise ValueError("I3 requires rho + kappa > 0 to relax")
        t_rel = cfg.i3_relax_time
        if t_rel is None:
            t_rel = 20.0 / (cfg.rho + cfg.kappa)
        out = _call_kernel(
            cfg, N, J, ac_override=0, lam=0.0, t_end=t_rel, t_measure_start=t_rel,
            phi=phi, phi_cls=phi_cls, c_last=c_last, t_last=t_last, s=s0,
            n_cnt=n_cnt, tau=tau, anchor=anchor, last_out=last_out, last_fr=last_fr,
            u=np.zeros(N, dtype=np.int8),
            pulses=(), exo=None, streams=streams, reg_info=reg_info,
            sample_times=(), stop_on_extinction=False,
        )
        i3_relax_info = {
            "relax_time": t_rel,
            "n_reset": out["agg"][E.A_NRESET],
            "n_recons": out["agg"][E.A_NRECONS],
            "phi_hist": {int(k): int(v) for k, v in
                         zip(*np.unique(phi, return_counts=True))},
            "x_realized": float(s0.mean()),
        }
        # the automaton / surrogate memory must represent the relaxed orientation
        last_fr[:] = phi
        last_out[:] = 1
        anchor[:] = phi
        tau[:] = 1.0
        t_last[:] = 0.0
        c_last[:] = 0.0

    # ---- prescribed exogenous message process (T3)
    exo = None
    if cfg.exo_rate_fn is not None:
        exo = _draw_exogenous(cfg, N, g_exo, registry)

    out = _call_kernel(
        cfg, N, J, ac_override=ac, lam=cfg.lam, t_end=cfg.t_end,
        rho_override=rho_main, kappa_override=kappa_main,
        t_measure_start=cfg.t_measure_start,
        phi=phi, phi_cls=phi_cls, c_last=c_last, t_last=t_last, s=s0,
        n_cnt=n_cnt, tau=tau, anchor=anchor, last_out=last_out, last_fr=last_fr,
        u=u, pulses=cfg.pulses, exo=exo, streams=streams, reg_info=reg_info,
        sample_times=cfg.sample_times,
        stop_on_extinction=cfg.stop_on_extinction,
        kw_gen=None, kw_broadcast_only=-1,
    )
    out["realized_reach"] = realized_reach
    out["i3_relax"] = i3_relax_info
    out["n_classes"] = J
    out["master_seed"] = int(master_seed)
    out["exo_integral"] = _exo_intensity_integral(cfg)
    out["phi_final"] = phi
    out["s_final"] = s0
    out["c_final"] = c_last
    out["n_counters"] = n_cnt
    out["tau_final"] = tau
    out["u"] = u
    if return_state:
        out["state"] = _snapshot(phi, phi_cls, c_last, s0, n_cnt, tau, anchor,
                                 last_out, last_fr, out["gen"], u)
    return out


def _draw_exogenous(cfg, N, gen, registry):
    """Prescribed inhomogeneous-Poisson message input of KNOWN intensity.

    Thinning of a homogeneous rate-nu0 process on [0, exo_t_end], independently
    per agent; the angle is the single declared exogenous framing.
    """
    nu0 = cfg.exo_rate_nu0
    T = cfg.exo_t_end
    if cfg.exo_rate_fn == "const":
        def keep(t):
            return np.ones_like(t, dtype=bool)
    elif cfg.exo_rate_fn == "exp_decay":
        def keep(t):
            return gen.random(t.shape[0]) < np.exp(-cfg.exo_rate_gamma * t)
    else:
        raise ValueError(cfg.exo_rate_fn)
    counts = gen.poisson(nu0 * T, size=N)
    tot = int(counts.sum())
    times = gen.random(tot) * T
    agents = np.repeat(np.arange(N, dtype=np.int32), counts)
    m = keep(times)
    times = times[m]
    agents = agents[m]
    order = np.argsort(times, kind="stable")
    times = times[order]
    agents = agents[order]
    ang = int(reduce180(cfg.exo_angle_deg))
    return {
        "t": np.ascontiguousarray(times),
        "ag": np.ascontiguousarray(agents.astype(np.int32)),
        "ang": np.full(times.shape[0], ang, dtype=np.int32),
        "cls": np.full(times.shape[0], registry.of(ang), dtype=np.int32),
    }


def _call_kernel(cfg, N, J, ac_override, lam, t_end, t_measure_start,
                 phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor, last_out,
                 last_fr, u, pulses, exo, streams, reg_info, sample_times,
                 stop_on_extinction, rho_override=None, kappa_override=None,
                 kw_gen=None, kw_broadcast_only=-1):
    rho_eff = cfg.rho if rho_override is None else rho_override
    kappa_eff = cfg.kappa if kappa_override is None else kappa_override
    reg = reg_info
    pul = sorted([(float(t), int(a)) for (t, a) in pulses], key=lambda z: z[0])
    # NOTE: sorted() is stable, so coincident pulses keep their declared index order
    pulse_t = np.array([p[0] for p in pul], dtype=np.float64)
    pulse_ang = np.array([reduce180(p[1]) for p in pul], dtype=np.int32)
    from .angles import ClassRegistry  # noqa: F401
    pulse_cls = np.array([reg["key_to_class"][int(reduce180(p[1])) % 90] for p in pul],
                         dtype=np.int32)
    if exo is None:
        exo_t = np.empty(0, dtype=np.float64)
        exo_ag = np.empty(0, dtype=np.int32)
        exo_ang = np.empty(0, dtype=np.int32)
        exo_cls = np.empty(0, dtype=np.int32)
    else:
        exo_t, exo_ag, exo_ang, exo_cls = exo["t"], exo["ag"], exo["ang"], exo["cls"]

    n_pul = pulse_t.shape[0]
    ever_active = np.zeros(N, dtype=np.int8)
    t_first_act = np.full(N, np.nan)
    t_first_deact = np.full(N, np.nan)
    t_last_deact = np.full(N, np.nan)
    n_intervals = np.zeros(N, dtype=np.int32)
    act_time = np.zeros(N, dtype=np.float64)
    pulse_out = np.full((N, max(n_pul, 1)), -1, dtype=np.int8)
    st = np.array(sorted(sample_times), dtype=np.float64)
    sampleA = np.full(st.shape[0], -1, dtype=np.int64)
    sampleAp = np.full(st.shape[0], -1, dtype=np.int64)
    agg = np.zeros(E.N_AGG, dtype=np.float64)
    intAj = np.zeros(J, dtype=np.float64)
    intAj_win = np.zeros(J, dtype=np.float64)

    gen = kw_gen if kw_gen is not None else np.full(N, -1, dtype=np.int32)
    n_offspring = np.zeros(N, dtype=np.int32)
    bro = int(kw_broadcast_only)
    frz = 1 if cfg.freeze_background else 0
    cio = int(reg.get("class_initial_only", -1))

    cap = int(cfg.heap_cap_per_agent) * N + 4096
    for _attempt in range(6):
        agg[:] = 0.0
        intAj[:] = 0.0
        intAj_win[:] = 0.0
        E.simulate(
            N, ac_override,
            cfg.eps, cfg.c_b, cfg.c_h, cfg.alpha, cfg.beta, lam, rho_eff, kappa_eff,
            cfg.r,
            int(cfg.delta_deg or 0), reg["class_target"],
            reg["class_delta_plus"], reg["class_delta_minus"],
            phi, phi_cls, c_last, t_last, s, n_cnt, tau, anchor, last_out, last_fr,
            u, pulse_t, pulse_ang, pulse_cls,
            exo_t, exo_ag, exo_ang, exo_cls,
            float(t_end), float(t_measure_start), 1 if stop_on_extinction else 0,
            streams, cap,
            ever_active, t_first_act, t_first_deact, t_last_deact, n_intervals,
            act_time, pulse_out, st, sampleA, sampleAp,
            agg, intAj, intAj_win,
            gen, n_offspring, bro, frz, cio,
        )
        if agg[E.A_OVERFLOW] == 2.0:
            raise RuntimeError(
                "an agent broadcast an orientation whose framing class was never "
                "created (engine.py cls_initial_only guard)")
        if agg[E.A_OVERFLOW] == 0.0:
            break
        cap *= 4
    else:
        raise RuntimeError("event-queue capacity exhausted")

    return {
        "ever_active": ever_active,
        "t_first_act": t_first_act,
        "t_first_deact": t_first_deact,
        "t_last_deact": t_last_deact,
        "n_intervals": n_intervals,
        "act_time": act_time,
        "pulse_out": pulse_out[:, :n_pul] if n_pul else pulse_out[:, :0],
        "sample_t": st,
        "sampleA": sampleA,
        "sampleAp": sampleAp,
        "agg": agg,
        "gen": gen,
        "n_offspring": n_offspring,
        "intAj": intAj,
        "intAj_win": intAj_win,
        "heap_cap_used": cap,
    }


# ---------------------------------------------------------------- state I/O
_STATE_KEYS = ("phi", "phi_cls", "c_last", "s", "n_cnt", "tau", "anchor",
               "last_out", "last_fr", "gen", "u")


def _snapshot(phi, phi_cls, c_last, s, n_cnt, tau, anchor, last_out, last_fr,
              gen, u):
    return {"phi": phi.copy(), "phi_cls": phi_cls.copy(), "c_last": c_last.copy(),
            "s": s.copy(), "n_cnt": n_cnt.copy(), "tau": tau.copy(),
            "anchor": anchor.copy(), "last_out": last_out.copy(),
            "last_fr": last_fr.copy(), "gen": gen.copy(), "u": u.copy()}


def copy_state(st):
    return {k: st[k].copy() for k in _STATE_KEYS}


def inject_seed(st, idx, c_b):
    """Design A1: 'one agent at phi = T_+, c = 1, s = +, fresh counters'."""
    st["phi"][idx] = 0
    st["phi_cls"][idx] = 0          # the target basis is always class id 0
    st["c_last"][idx] = 1.0
    st["s"][idx] = 1
    st["n_cnt"][idx, :] = 0
    st["tau"][idx] = 1.0
    st["anchor"][idx] = 0
    st["last_out"][idx] = 1
    st["last_fr"][idx] = 0
    st["gen"][idx] = 0
    return st


def _run_from_state(cfg, master_seed, registry, reg_info, st, return_state):
    """Resume the process from a saved state, with the time origin reset to 0."""
    N = int(cfg.N)
    J = reg_info["n_classes"]
    ac = AGENT_CLASS_IDS[cfg.agent_class]
    phi = st["phi"].copy(); phi_cls = st["phi_cls"].copy()
    c_last = st["c_last"].copy(); s0 = st["s"].copy()
    n_cnt = st["n_cnt"].copy(); tau = st["tau"].copy()
    anchor = st["anchor"].copy(); last_out = st["last_out"].copy()
    last_fr = st["last_fr"].copy(); gen = st["gen"].copy(); u = st["u"].copy()
    t_last = np.zeros(N, dtype=np.float64)
    assert n_cnt.shape[1] == J, (n_cnt.shape, J)

    seed_idx = -1
    if cfg.seed_agent:
        g = python_generator(master_seed, STREAM_INITIAL)
        seed_idx = int(g.integers(0, N))
        inject_seed({"phi": phi, "phi_cls": phi_cls, "c_last": c_last, "s": s0,
                     "n_cnt": n_cnt, "tau": tau, "anchor": anchor,
                     "last_out": last_out, "last_fr": last_fr, "gen": gen,
                     "u": u}, seed_idx, cfg.c_b)

    rho_main = cfg.rho if cfg.rho_main is None else cfg.rho_main
    kappa_main = cfg.kappa if cfg.kappa_main is None else cfg.kappa_main
    streams = seed_streams(np.uint64(master_seed), 6)
    out = _call_kernel(
        cfg, N, J, ac_override=ac, lam=cfg.lam, t_end=cfg.t_end,
        t_measure_start=cfg.t_measure_start,
        phi=phi, phi_cls=phi_cls, c_last=c_last, t_last=t_last, s=s0,
        n_cnt=n_cnt, tau=tau, anchor=anchor, last_out=last_out, last_fr=last_fr,
        u=u, pulses=cfg.pulses, exo=None, streams=streams, reg_info=reg_info,
        sample_times=cfg.sample_times,
        stop_on_extinction=cfg.stop_on_extinction,
        rho_override=rho_main, kappa_override=kappa_main,
        kw_gen=gen,
        kw_broadcast_only=(seed_idx if cfg.broadcast_only_seed else -1),
    )
    out.update(realized_reach=float(u.mean()), i3_relax=None, n_classes=J,
               master_seed=int(master_seed), exo_integral=0.0,
               phi_final=phi, s_final=s0, c_final=c_last, n_counters=n_cnt,
               tau_final=tau, u=u, seed_index=seed_idx)
    if return_state:
        out["state"] = _snapshot(phi, phi_cls, c_last, s0, n_cnt, tau, anchor,
                                 last_out, last_fr, gen, u)
    return out
