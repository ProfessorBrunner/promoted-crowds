"""Per-item Stage 2 runners.  Each returns (verdict_rows, raw_rows, diagnostics)."""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from crowd1 import a6, predictions_s2 as PS, tests_s2 as T2

LOG = print
CFG_PATH = None
MAPPER = None


def _mk(name, pred, vals, delta, basis, N, **kw):
    return a6.make_verdict(name=name, predicted=pred, per_replicate_values=vals,
                           delta=delta, delta_basis=basis, N=N, **kw)


def _pathwise(name, count, n_rep, N, basis, note=""):
    return a6.Verdict(name=name, predicted=0.0, measured=float(count),
                      diff=float(count), ci_lo=float(count), ci_hi=float(count),
                      delta=0.0, delta_basis=basis,
                      status=a6.PASS if count == 0 else a6.FAIL,
                      n_replicates=n_rep, N=N, replicates_needed=None,
                      mc_error=0.0, finite_N_bias=0.0, numerical_error=0.0,
                      closure_error=0.0,
                      interval_kind="exact pathwise (violation count)", note=note)


def _wilson(k, n):
    p, lo, hi, hw = a6.wilson_interval(k, n)
    return p, lo, hi, hw


# ============================================================================ P1
def _p1_operator(cfg, orders, N, nbg):
    jobs = [(CFG_PATH, o, N, rep) for o in orders for rep in range(nbg)]
    res = MAPPER(T2.p1_operator_worker, jobs)
    rows = [r for sub in res for r in sub]
    return rows


def run_P1(cfg):
    fx, dc = cfg.P1["fixed"], cfg.P1["declared"]
    delays = cfg.P1_DELAY["fixed"]["tau0_over_rho"]
    N = fx["N"]
    orders = fx["orders"] + fx["held_out_orders"]
    LOG(f"  P1 operator: {len(orders)} orders x {dc['operator_backgrounds']} "
        f"backgrounds x {len(delays)} delays x "
        f"{dc['operator_trials_per_background']} seed trials, N={N}")
    rows = _p1_operator(cfg, orders, N, dc["operator_backgrounds"])
    raw = [dict(test="P1-operator", **r) for r in rows]
    LOG(f"  P1 operator ladder rung N={dc['operator_N_ladder'][0]}")
    rows_lo = _p1_operator(cfg, fx["orders"], dc["operator_N_ladder"][0],
                           max(4, dc["operator_backgrounds"] // 4))
    raw += [dict(test="P1-operator", **r) for r in rows_lo]

    V, diag = [], {}
    lam = dc["operator_lambda"]
    tau_ref = max(delays)                      # P1 proper: relax for 10/rho
    sel = lambda rs, o, t: [r for r in rs if r["order"] == str(o) and r["tau0"] == t]

    n_act = sum(r["n_activated_by_campaign"] for r in rows)
    V.append(_pathwise("P1 no activation by the campaign (pathwise)", n_act,
                       len(rows), N,
                       "R8(a): 'Nothing activates'; any activation is a FAIL",
                       note=f"max |c| post-campaign "
                            f"{max(r['max_abs_c'] for r in rows):.9f} < c_b = {fx['c_b']}"))
    for o in fx["orders"] + fx["held_out_orders"]:
        held = o in fx["held_out_orders"]
        tag = "held-out " if held else ""
        xp = (cfg.P1["sealed_held_out"]["x"][o] if held else fx["x_pred"][o])
        Rp = (cfg.P1["sealed_held_out"]["R_over_lambda"][o] if held
              else fx["R_over_lambda_pred"][o])
        rs = sel(rows, o, tau_ref)
        xs = np.array([r["x"] for r in rs])
        zs = np.array([r["Z1_mean"] / lam for r in rs])
        zl = np.array([r["Z1_mean"] / lam for r in sel(rows_lo, o, tau_ref)])
        fnb = (abs(zs.mean() - zl.mean()) if len(zl) else None)
        if abs(xp) < 1e-12:
            V.append(_mk(f"P1 {tag}post-campaign x | {o}", 0.0, xs,
                         cfg.DELTA_ZERO_ABS,
                         f"A4a absolute tolerance for x = 0: {cfg.DELTA_ZERO_ABS}",
                         N, finite_N_bias=0.0, numerical_error=0.0,
                         closure_error=0.0,
                         note="sealed before the run" if held else ""))
        else:
            V.append(_mk(f"P1 {tag}post-campaign x | {o}", xp, xs,
                         cfg.DELTA_OPERATOR_FRAC * abs(xp),
                         f"A6 operator check: 2% of {xp:.9f}", N,
                         finite_N_bias=0.0, numerical_error=0.0, closure_error=0.0,
                         note="sealed before the run" if held else ""))
        V.append(_mk(f"P1 {tag}operator R/lambda | {o}", Rp, zs,
                     cfg.DELTA_OPERATOR_FRAC * Rp,
                     f"A6 operator check: 2% of {Rp:.9f}", N,
                     finite_N_bias=fnb, numerical_error=0.0, closure_error=0.0,
                     note=f"single seed on the relaxed background at tau0={tau_ref}/rho, "
                          f"lambda={lam}; {dc['operator_trials_per_background']} seeds "
                          f"per background"))
    # invasion consequence at lambda = 2 (A3: R is not a growth rate)
    for o, claim, Rreg in ((fx["orders"][0], "does not invade", fx["R_at_lambda2"]["first"]),
                           (fx["orders"][1], "invades", fx["R_at_lambda2"]["second"])):
        rs = sel(rows, o, tau_ref)
        zs = np.array([r["Z1_mean"] for r in rs])
        m, lo, hi, hw = a6.t_interval(zs)
        diag.setdefault("invasion_at_lambda2", []).append(
            dict(order=str(o), claim=claim, R_registered=Rreg, R_measured=m,
                 ci_lo=lo, ci_hi=hi,
                 consistent=bool((hi < 1.0) if claim == "does not invade" else (lo > 1.0))))

    # ---- population check: outbreak probability (A4a: +-0.03 is a PRECISION target)
    pop = []
    for lam_p in fx["lambdas"]:
        for o in fx["orders"]:
            k, n = _p1_pop(cfg, o, N, lam_p, tau_ref, pilot=dc["outbreak_pilot"],
                           cap=dc["outbreak_max_replicates"], raw=raw)
            p, lo, hi, hw = _wilson(k, n)
            pop.append(dict(order=str(o), lam=lam_p, N=N, replicates=n,
                            outbreaks=k, p_outbreak=p, ci_lo=lo, ci_hi=hi,
                            half_width=hw,
                            meets_0p03_target=bool(hw <= cfg.DELTA_OUTBREAK_ABS)))
            LOG(f"    outbreak lam={lam_p} {o}: {k}/{n} = {p:.4f} +- {hw:.4f}")
    # held-out orders at lambda = 2
    for o in fx["held_out_orders"]:
        k, n = _p1_pop(cfg, o, N, 2.0, tau_ref, pilot=dc["outbreak_pilot"],
                       cap=dc["outbreak_max_replicates"], raw=raw)
        p, lo, hi, hw = _wilson(k, n)
        pop.append(dict(order=str(o) + " (held out)", lam=2.0, N=N, replicates=n,
                        outbreaks=k, p_outbreak=p, ci_lo=lo, ci_hi=hi,
                        half_width=hw,
                        meets_0p03_target=bool(hw <= cfg.DELTA_OUTBREAK_ABS)))
    diag["outbreak_probability"] = pop
    diag["outbreak_status"] = ("REPORTED. A4a: where no numerical outbreak "
                               "probability is predicted, +-0.03 is a precision "
                               "target for the estimate, not an agreement tolerance. "
                               "The invasion claim itself is certified on the "
                               "operator rows above (A3 keeps R, growth rate and "
                               "outbreak probability distinct).")
    # ---- N = 10^6 rung
    big = []
    jobs = [(CFG_PATH, o, fx["N_big"], 2.0, tau_ref, rep)
            for o in fx["orders"] for rep in range(fx["replicates_big"])]
    LOG(f"  P1 N=10^6: {len(jobs)} runs")
    res = MAPPER(T2.p1_outbreak_worker, jobs)
    raw += [dict(test="P1-outbreak", **r) for r in res]
    for o in fx["orders"]:
        rs = [r for r in res if r["order"] == str(o)]
        k = sum(r["outbreak"] for r in rs)
        p, lo, hi, hw = _wilson(k, len(rs))
        big.append(dict(order=str(o), N=fx["N_big"], replicates=len(rs),
                        outbreaks=k, p_outbreak=p, half_width=hw))
    diag["outbreak_N1e6_lambda2"] = big
    diag["operator_N_ladder"] = [
        dict(N=dc["operator_N_ladder"][0],
             R_over_lambda=float(np.mean([r["Z1_mean"] / lam for r in
                                          sel(rows_lo, fx["orders"][1], tau_ref)]))),
        dict(N=N, R_over_lambda=float(np.mean([r["Z1_mean"] / lam for r in
                                               sel(rows, fx["orders"][1], tau_ref)])))]
    return V, raw, diag


def _p1_pop(cfg, order, N, lam, tau0, pilot, cap, raw):
    """Pilot, then top up to the replicate count SIZED for the +-0.03 target.

    `need` is computed once from the pilot's p_hat and is never revised, so this
    TARGETS +-0.03 but does not guarantee it: a cell whose realised p_hat(1-p_hat)
    exceeds the pilot's estimate ends up under-sampled.  Three cells do
    (440/958, 275/315, 504/1052); see stage2b/METHODS_kinetic_solver.md.  The
    meets_0p03_target flag records the realised Wilson half-width, not this aim.
    """
    jobs = [(CFG_PATH, order, N, lam, tau0, rep) for rep in range(pilot)]
    res = MAPPER(T2.p1_outbreak_worker, jobs)
    k = sum(r["outbreak"] for r in res)
    p = k / len(res)
    need = int(math.ceil((1.96 / cfg.DELTA_OUTBREAK_ABS) ** 2 *
                         max(p * (1 - p), 0.01)))
    need = min(max(need, pilot), cap)
    if need > pilot:
        jobs2 = [(CFG_PATH, order, N, lam, tau0, rep)
                 for rep in range(pilot, need)]
        res += MAPPER(T2.p1_outbreak_worker, jobs2)
    raw += [dict(test="P1-outbreak", **r) for r in res]
    return sum(r["outbreak"] for r in res), len(res)


# ====================================================================== P1-delay
def run_P1_delay(cfg, _cache={}):
    fx, dc = cfg.P1["fixed"], cfg.P1_DELAY["declared"]
    delays = cfg.P1_DELAY["fixed"]["tau0_over_rho"]
    N, lam = fx["N"], dc["operator_lambda"]
    jobs = [(CFG_PATH, o, N, rep) for o in fx["orders"]
            for rep in range(dc["operator_backgrounds"])]
    LOG(f"  P1-delay operator: {len(jobs)} backgrounds x {len(delays)} delays")
    res = MAPPER(T2.p1_operator_worker, jobs)
    rows = [r for sub in res for r in sub]
    raw = [dict(test="P1-delay-operator", **r) for r in rows]
    V, diag, tbl = [], {}, []
    rho = fx["rho"]
    for t in delays:
        a = np.array([r["Z1_mean"] for r in rows
                      if r["order"] == str(fx["orders"][0]) and r["tau0"] == t])
        b = np.array([r["Z1_mean"] for r in rows
                      if r["order"] == str(fx["orders"][1]) and r["tau0"] == t])
        ratio = b / a
        m, lo, hi, hw = a6.t_interval(ratio)
        unrel = np.array([1.0 - r["frac_phi_target"] for r in rows
                          if r["order"] == str(fx["orders"][1]) and r["tau0"] == t])
        ex1 = PS.p1_qT_at_delay(fx["orders"][0], t, rho=rho)["R_over_lambda"] * lam
        ex2 = PS.p1_qT_at_delay(fx["orders"][1], t, rho=rho)["R_over_lambda"] * lam
        tbl.append(dict(tau0_over_rho=t, R_first=float(a.mean()),
                        R_second=float(b.mean()), ratio=m, ci_lo=lo, ci_hi=hi,
                        R_first_exact=ex1, R_second_exact=ex2,
                        ratio_exact=ex2 / ex1,
                        advantage_present=bool(lo > 1.0),
                        unrelaxed_fraction=float(unrel.mean()),
                        exp_minus_rho_tau=math.exp(-rho * t)))
    diag["invasion_radius_ratio_vs_delay"] = tbl
    diag["label"] = ("A4a: this is the FROZEN operator-check endpoint (offspring "
                     "counts per seed on the saved post-campaign state at each "
                     "delay). Outbreak probabilities are a separate population "
                     "endpoint and are never divided to form an advantage.")
    tmax = max(delays)
    a = np.array([r["Z1_mean"] for r in rows
                  if r["order"] == str(fx["orders"][0]) and r["tau0"] == tmax])
    b = np.array([r["Z1_mean"] for r in rows
                  if r["order"] == str(fx["orders"][1]) and r["tau0"] == tmax])
    V.append(_mk(f"P1-delay invasion-advantage ratio at tau0={tmax}/rho vs 1.97",
                 fx["ratio_pred"], b / a,
                 cfg.DELTA_OPERATOR_FRAC * fx["ratio_pred"],
                 f"A6 operator check: 2% of {fx['ratio_pred']}", N,
                 finite_N_bias=None, numerical_error=0.0, closure_error=0.0,
                 note="ratio of invasion radii (A4a endpoint F1); the exact limit "
                      "from the sealed enumeration is 1.969846310"))
    wrow = min(tbl, key=lambda r: r["ci_lo"])
    if wrow["ci_lo"] > 1.0:
        st = a6.PASS
    elif wrow["ci_hi"] < 1.0:
        st = a6.FAIL
    else:
        st = a6.INCONCLUSIVE
    V.append(a6.Verdict(
        name="P1-delay advantage present at every delay (ratio > 1)",
        predicted=1.0, measured=float(wrow["ratio"]),
        diff=float(wrow["ratio"] - 1.0),
        ci_lo=float(wrow["ci_lo"] - 1.0), ci_hi=float(wrow["ci_hi"] - 1.0),
        delta=0.0,
        delta_basis="sign claim; A6 three-way: PASS iff the 95% lower bound "
                    "exceeds 1 at every delay, FAIL iff an upper bound falls "
                    "below 1, INCONCLUSIVE otherwise",
        status=st, n_replicates=dc["operator_backgrounds"], N=N,
        replicates_needed=None,
        mc_error=float(wrow["ci_hi"] - wrow["ratio"]),
        finite_N_bias=None, numerical_error=0.0, closure_error=0.0,
        interval_kind="student-t across backgrounds, worst delay",
        note=f"worst delay tau0={wrow['tau0_over_rho']}/rho, where the EXACT "
             f"invasion-radius ratio derived from the same enumeration that "
             f"reproduces C3.15 is {wrow['ratio_exact']:.9f}. At tau0 = 0 that "
             f"exact ratio is 1 to machine precision, because from I2 the "
             f"maximally mixed orientation is invariant under every projection "
             f"(R8(b)), so the orientation channel contributes nothing and the "
             f"stance channel has had no time to act. No finite replicate count "
             f"can place a confidence interval strictly above 1 at a point where "
             f"the true value IS 1; see BUGLOG.md A1."))
    un = np.array([r["unrelaxed_fraction"] for r in tbl])
    ex = np.array([r["exp_minus_rho_tau"] for r in tbl])
    _dev = []
    for t in delays:
        u = np.array([1.0 - r["frac_phi_target"] for r in rows if r["tau0"] == t])
        _dev.append(np.abs(u - math.exp(-rho * t)))
    _m, _lo, _hi = a6.bootstrap_mean_ci(np.max(np.vstack(_dev), axis=0), seed=909)
    V.append(a6.verdict_with_ci(
        name="P1-delay orientation preparation decays as exp(-rho tau0)",
        predicted=0.0, measured=_m, ci_lo_abs=_lo, ci_hi_abs=_hi,
        delta=cfg.DELTA_OPERATOR_FRAC,
        delta_basis="A4a: the exponential-decay claim is stated for the underlying "
                    "state law, not the threshold observable; 2% absolute on the "
                    "unrelaxed orientation fraction",
        N=N, n_replicates=dc["operator_backgrounds"],
        numerical_error=0.0, closure_error=0.0, finite_N_bias=None,
        interval_kind="bootstrap over backgrounds of the max absolute deviation "
                      "over the six delays",
        note="unrelaxed fraction measured vs exp(-rho tau0): " +
             ", ".join(f"{t['tau0_over_rho']}:{t['unrelaxed_fraction']:.5f}/"
                       f"{t['exp_minus_rho_tau']:.5f}" for t in tbl)))
    return V, raw, diag



# ============================================================================ P2
def run_P2(cfg):
    fx, dc = cfg.P2["fixed"], cfg.P2["declared"]
    N, lam = fx["N"], dc["operator_lambda"]
    jobs = [(CFG_PATH, o, N, rep, 0.0, [0.0], "I1") for o in fx["orders"]
            for rep in range(dc["operator_backgrounds"])]
    jobs += [(CFG_PATH, o, N, rep, 0.0, [0.0], "I2") for o in fx["orders"]
             for rep in range(dc["operator_backgrounds"])]
    LOG(f"  P2 operator: {len(jobs)} backgrounds x "
        f"{dc['operator_trials_per_background']} seed trials, N={N}")
    rows = [r for sub in MAPPER(T2.p2_operator_worker, jobs) for r in sub]
    jobs_lo = [(CFG_PATH, o, dc["operator_N_ladder"][0], rep, 0.0, [0.0], "I1")
               for o in fx["orders"] for rep in range(max(4, dc["operator_backgrounds"]//4))]
    rows_lo = [r for sub in MAPPER(T2.p2_operator_worker, jobs_lo) for r in sub]
    raw = [dict(test="P2-operator", **r) for r in rows + rows_lo]
    V, diag = [], {}
    nact = sum(r["n_activated_by_campaign"] for r in rows)
    V.append(_pathwise("P2 no activation by the campaign (pathwise)", nact,
                       len(rows), N,
                       "c_b = 0.95 is chosen so the campaign is silent; any "
                       "activation is a FAIL",
                       note=f"max |c| post-campaign {max(r['max_abs_c'] for r in rows):.6f}"))
    for o in fx["orders"]:
        rs = [r for r in rows if r["order"] == str(o) and r["initial_law"] == "I1"]
        rl = [r for r in rows_lo if r["order"] == str(o)]
        q = np.array([r["qT_measured"] for r in rs])
        z = np.array([r["Z1_mean"] / lam for r in rs])
        zl = np.array([r["Z1_mean"] / lam for r in rl])
        qp, Rp = fx["qT_pred"][o], fx["R_over_lambda_pred"][o]
        V.append(_mk(f"P2 first-generation acceptance q_T | {o}", qp, q,
                     cfg.DELTA_OPERATOR_FRAC * qp,
                     f"A6 operator check: 2% of {qp:.9f}", N,
                     finite_N_bias=0.0, numerical_error=0.0, closure_error=0.0))
        V.append(_mk(f"P2 operator R/lambda | {o}", Rp, z,
                     cfg.DELTA_OPERATOR_FRAC * Rp,
                     f"A6 operator check: 2% of {Rp:.9f}", N,
                     finite_N_bias=float(abs(z.mean() - zl.mean())) if len(zl) else None,
                     numerical_error=0.0, closure_error=0.0))
    zi = np.array([r["Z1_mean"] / lam for r in rows if r["initial_law"] == "I2"])
    V.append(_mk("P2 operator R/lambda from I2 (all orders equal)",
                 fx["I2_R_over_lambda_pred"], zi,
                 cfg.DELTA_OPERATOR_FRAC * fx["I2_R_over_lambda_pred"],
                 f"A6 operator check: 2% of {fx['I2_R_over_lambda_pred']:.9f}", N,
                 finite_N_bias=0.0, numerical_error=0.0, closure_error=0.0,
                 note="pooled over the three orders; the maximally mixed "
                      "orientation is invariant under every projection"))
    spread = {}
    for o in fx["orders"]:
        spread[str(o)] = float(np.mean([r["Z1_mean"] / lam for r in rows
                                        if r["order"] == str(o) and
                                        r["initial_law"] == "I2"]))
    diag["I2_by_order"] = spread
    pop = []
    for o in fx["orders"]:
        k, n = _generic_pop(cfg, T2.p2_outbreak_worker,
                            [(CFG_PATH, o, N, fx["lambda_pop"], rep)
                             for rep in range(dc["outbreak_max_replicates"])],
                            dc["outbreak_pilot"], fx["outbreak_precision_target"],
                            dc["outbreak_max_replicates"], raw, "P2-outbreak")
        p, lo, hi, hw = _wilson(k, n)
        pop.append(dict(order=str(o), lam=fx["lambda_pop"], R_registered=fx["R_pop"][o],
                        N=N, replicates=n, outbreaks=k, p_outbreak=p,
                        ci_lo=lo, ci_hi=hi, half_width=hw,
                        meets_0p02_target=bool(hw <= fx["outbreak_precision_target"])))
        LOG(f"    P2 outbreak {o} lam={fx['lambda_pop']}: {k}/{n} = {p:.4f} +- {hw:.4f}")
    diag["outbreak_probability"] = pop
    diag["outbreak_status"] = ("REPORTED with a +-0.02 precision target (A4 P2); "
                               "near-critical, no numerical outbreak probability "
                               "is predicted, so this is not an agreement tolerance.")
    return V, raw, diag


def _generic_pop(cfg, worker, all_jobs, pilot, target, cap, raw, tag):
    res = MAPPER(worker, all_jobs[:pilot])
    p = sum(r["outbreak"] for r in res) / len(res)
    need = int(math.ceil((1.96 / target) ** 2 * max(p * (1 - p), 0.004)))
    need = min(max(need, pilot), cap)
    if need > pilot:
        res += MAPPER(worker, all_jobs[pilot:need])
    raw += [dict(test=tag, **r) for r in res]
    return sum(r["outbreak"] for r in res), len(res)


# ====================================================================== P2-delay
def run_P2_delay(cfg):
    fx, dc = cfg.P2["fixed"], cfg.P2_DELAY["declared"]
    f2 = cfg.P2_DELAY["fixed"]
    N, lam = dc["N"], dc["operator_lambda"]
    rows = []
    for rho in f2["rho_values"]:
        jobs = [(CFG_PATH, o, N, rep, rho, f2["tau0"], "I1") for o in fx["orders"]
                for rep in range(dc["operator_backgrounds"])]
        LOG(f"  P2-delay rho={rho}: {len(jobs)} backgrounds x {len(f2['tau0'])} delays")
        rows += [r for sub in MAPPER(T2.p2_operator_worker, jobs) for r in sub]
    raw = [dict(test="P2-delay-operator", **r) for r in rows]
    V, diag, tbl = [], {}, []
    for rho in f2["rho_values"]:
        for t in f2["tau0"]:
            vals = {}
            for o in fx["orders"]:
                z = np.array([r["Z1_mean"] / lam for r in rows
                              if r["order"] == str(o) and r["rho"] == rho
                              and r["tau0"] == t])
                vals[str(o)] = float(z.mean())
            ph = np.array([r["frac_phi_T"] for r in rows
                           if r["rho"] == rho and r["tau0"] == t])
            spread = max(vals.values()) - min(vals.values())
            tbl.append(dict(rho=rho, tau0=t, spread_R_over_lambda=spread,
                            frac_phi_at_T=float(ph.mean()), **vals))
    diag["order_dependence_vs_delay"] = tbl
    s0 = [r for r in tbl if r["rho"] == 0.0]
    sp0, sp0lo, sp0hi = _boot_spread(rows, fx["orders"], 0.0, 0.0, lam, 801)
    sp1, sp1lo, sp1hi = _boot_spread(rows, fx["orders"], 0.0, max(f2["tau0"]),
                                     lam, 802)
    V.append(a6.verdict_with_ci(
        name="P2-delay rho=0: order dependence persists (orientation never relaxes)",
        predicted=sp0, measured=sp1, ci_lo_abs=sp1lo, ci_hi_abs=sp1hi,
        delta=cfg.DELTA_OPERATOR_FRAC * sp0,
        delta_basis="A6 operator check: 2% of the tau0 = 0 spread; persistence "
                    "means the spread does not decay",
        N=N, n_replicates=dc["operator_backgrounds"],
        interval_kind="bootstrap over backgrounds of the spread of R/lambda "
                      "across the three orders",
        numerical_error=0.0, closure_error=0.0, finite_N_bias=None,
        note=f"spread at tau0=0 {sp0:.6f} [{sp0lo:.6f}, {sp0hi:.6f}], at "
             f"tau0={max(f2['tau0'])} {sp1:.6f} [{sp1lo:.6f}, {sp1hi:.6f}]"))
    s5 = [r for r in tbl if r["rho"] == 0.5]
    un = np.array([1.0 - r["frac_phi_at_T"] for r in s5])
    ex = np.array([math.exp(-0.5 * r["tau0"]) for r in s5])
    rel = un / un[0] if un[0] > 0 else un
    _d5 = []
    for t in f2["tau0"]:
        u = np.array([1.0 - r["frac_phi_T"] for r in rows
                      if r["rho"] == 0.5 and r["tau0"] == t])
        _d5.append(np.abs(u / max(un[0], 1e-12) - math.exp(-0.5 * t)))
    _m5, _lo5, _hi5 = a6.bootstrap_mean_ci(np.max(np.vstack(_d5), axis=0), seed=910)
    V.append(a6.verdict_with_ci(
        name="P2-delay rho=0.5: order dependence decays as exp(-rho tau0)",
        predicted=0.0, measured=_m5, ci_lo_abs=_lo5, ci_hi_abs=_hi5,
        delta=cfg.DELTA_OPERATOR_FRAC,
        delta_basis="A4a: the decay claim is stated for the underlying orientation "
                    "law, not the threshold observable; 2% absolute",
        N=N, n_replicates=dc["operator_backgrounds"],
        numerical_error=0.0, closure_error=0.0, finite_N_bias=None,
        interval_kind="bootstrap over backgrounds of the max absolute deviation "
                      "over the four delays",
        note="A4a: the post-campaign preparation IS recomputed at rho = 0.5 "
             "(the rho = 0 coefficients are not reused); un-relaxed fraction "
             "relative to tau0 = 0: " +
             ", ".join(f"{r['tau0']}:{u:.5f}/{e:.5f}"
                       for r, u, e in zip(s5, rel, ex))))
    return V, raw, diag


# ============================================================================ P3
def run_P3(cfg):
    fx, dc = cfg.P3["fixed"], cfg.P3["declared"]
    N, lam = fx["N"], dc["operator_lambda"]
    jobs = [(CFG_PATH, o, N, rep, fx["tau0"]) for o in fx["orders"]
            for rep in range(dc["operator_backgrounds"])]
    LOG(f"  P3 operator: {len(jobs)} backgrounds x {len(fx['tau0'])} delays")
    res = MAPPER(T2.p3_operator_worker, jobs)
    jobs_lo = [(CFG_PATH, o, dc["operator_N_ladder"][0], rep, fx["tau0"])
               for o in fx["orders"]
               for rep in range(max(4, dc["operator_backgrounds"] // 4))]
    res_lo = MAPPER(T2.p3_operator_worker, jobs_lo)
    raw = [dict(test="P3-operator", **r) for r in res + res_lo]
    V, diag = [], {}
    nact = sum(r["n_activated_by_campaign"] for r in res)
    V.append(_pathwise("P3 no activation by the campaign (pathwise)", nact,
                       len(res), N, "the campaign must leave a silent background",
                       note=f"max |c| {max(r['max_abs_c'] for r in res):.9f} < c_b"))
    for o in fx["orders"]:
        rs = [r for r in res if r["order"] == str(o)]
        rl = [r for r in res_lo if r["order"] == str(o)]
        pr = PS.p3_reference(o)
        frp = fx["R_fr0_over_lambda"][o] * lam
        ez = fx["EZ2_over_lambda2"][o] * lam ** 2
        a = np.array([r["R_fr_mean"] for r in rs])
        b = np.array([r["EZ2_mean"] for r in rs])
        al = np.array([r["R_fr_mean"] for r in rl])
        V.append(_mk(f"P3 frozen diagnostic R_fr(0) | {o}", frp, a,
                     cfg.DELTA_OPERATOR_FRAC * frp,
                     f"A6 operator check: 2% of {frp:.9f}", N,
                     finite_N_bias=float(abs(a.mean() - al.mean())),
                     numerical_error=0.0, closure_error=0.0,
                     note="LABELLED A FROZEN DIAGNOSTIC (A4a); evaluated on the "
                          f"saved post-campaign state at lambda={lam}"))
        V.append(_mk(f"P3 E Z_2 from a seed introduced immediately | {o}", ez, b,
                     cfg.DELTA_OPERATOR_FRAC * ez,
                     f"A6 operator check: 2% of {ez:.9f}", N,
                     finite_N_bias=None,
                     numerical_error=pr["EZ2_quad_error"] * lam ** 2,
                     closure_error=0.0,
                     note="time-dependent kernel, background NOT frozen "
                          "(C3.21); measured descendant growth"))
    pop = []
    for t in fx["tau0"]:
        for o in fx["orders"]:
            n = fx["replicates"][t]
            jobs = [(CFG_PATH, o, N, fx["lambda_pop"], t, rep) for rep in range(n)]
            rr = MAPPER(T2.p3_outbreak_worker, jobs)
            raw += [dict(test="P3-outbreak", **r) for r in rr]
            k = sum(r["outbreak"] for r in rr)
            p, lo, hi, hw = _wilson(k, n)
            pop.append(dict(order=str(o), tau0=t, lam=fx["lambda_pop"], N=N,
                            replicates=n, outbreaks=k, p_outbreak=p,
                            half_width=hw,
                            mean_Z1_live=float(np.mean([r["Z1_live"] for r in rr])),
                            mean_Zfrac=float(np.mean([r["Z_frac"] for r in rr]))))
            LOG(f"    P3 outbreak {o} tau0={t}: {k}/{n}, mean Z1_live="
                f"{pop[-1]['mean_Z1_live']:.4f}")
    diag["outbreak_and_descendants"] = pop
    Rinf = fx["R_inf_over_lambda"] * fx["lambda_pop"]
    tmax = max(fx["tau0"])
    rdelay = []
    for o in fx["orders"]:
        rs = [r for r in res if r["order"] == str(o)]
        rdelay.append(dict(order=str(o),
                           **{f"R_fr_tau{t:g}": float(np.mean(
                               [r[f"R_fr_tau{t:g}"] for r in rs]))
                              for t in fx["tau0"]}, R_inf_registered=Rinf))
        z = np.array([r[f"R_fr_tau{tmax:g}"] for r in rs])
        V.append(_mk(f"P3 convergence to R_inf = 0.0912 lambda at tau0 = {tmax} | {o}",
                     Rinf, z, cfg.DELTA_OPERATOR_FRAC * Rinf,
                     f"A6 operator check: 2% of {Rinf:.9f}", N,
                     finite_N_bias=None, numerical_error=0.0, closure_error=0.0,
                     note="next-generation operator of the RELAXED state (the "
                          "offspring count of a typical offspring, not of the "
                          "seed, whose conviction is 1 by A1)"))
    diag["R_fr_vs_delay"] = rdelay
    return V, raw, diag


# ============================================================================ P4
def run_P4(cfg):
    fx, dc = cfg.P4["fixed"], cfg.P4["declared"]
    N, nrep = fx["N"], fx["replicates"]
    jobs = [(CFG_PATH, lam, f, rep) for lam, fs in dc["f_grid"].items()
            for f in fs for rep in range(nrep)]
    LOG(f"  P4: {len(jobs)} runs (N={N}, horizons {fx['horizons']})")
    res = MAPPER(T2.p4_worker, jobs)
    raw = [dict(test="P4", **{k: v for k, v in r.items()}) for r in res]
    V, diag = [], {}
    branches = {lam: PS.p4_branches(lam) for lam in dc["f_grid"]}
    # lambda = 1.40: extinction for every reach
    r140 = [r for r in res if r["lam"] == fx["lambda_no_ignition"]]
    viol = sum(1 for r in r140 if r["A_160"] > 0.0)
    V.append(_pathwise(f"P4 no reach ignites at lambda = {fx['lambda_no_ignition']} "
                       f"(A(160) = 0)", viol, len(r140), N,
                       "A4a: below the fold the criterion is extinction, A(t) = 0 "
                       "by t = 160 for every f tested",
                       note=f"reaches tested {dc['f_grid'][fx['lambda_no_ignition']]}; "
                            f"{len(r140)} runs"))
    # ---- A6 error source 2: the N ladder for f_c
    lad_jobs = [(CFG_PATH, lam, f, 5000 + rep, dc["N_ladder"][1])
                for lam, fs in dc["ladder_f_grid"].items() for f in fs
                for rep in range(dc["ladder_replicates"])]
    LOG(f"  P4 N ladder: {len(lad_jobs)} runs at N={dc['N_ladder'][1]}")
    lad = MAPPER(T2.p4_worker, lad_jobs)
    raw += [dict(test="P4-ladder", **r) for r in lad]
    ladder_bias, ladder_tbl = {}, []
    for lam, fs in dc["ladder_f_grid"].items():
        thr = 1.5 * branches[lam]["A_u"]
        c_hi = [(float(np.mean([r["realized_reach"] for r in lad
                                if r["lam"] == lam and r["f"] == f])),
                 [1 if r["A_160"] > thr else 0 for r in lad
                  if r["lam"] == lam and r["f"] == f]) for f in fs]
        c_lo = [(float(np.mean([r["realized_reach"] for r in res
                                if r["lam"] == lam and r["f"] == f])),
                 [1 if r["A_160"] > thr else 0 for r in res
                  if r["lam"] == lam and r["f"] == f]) for f in fs]
        a_hi, lo_h, hi_h, _ = a6.bootstrap_threshold(c_hi, B=1000, seed=77)
        a_lo, lo_l, hi_l, _ = a6.bootstrap_threshold(c_lo, B=1000, seed=78)
        ladder_bias[lam] = abs(a_hi - a_lo) if not (math.isnan(a_hi) or
                                                    math.isnan(a_lo)) else None
        ladder_tbl.append(dict(lam=lam, f_c_N50k=a_lo, f_c_N200k=a_hi,
                               shift=(a_hi - a_lo), f_c_registered=fx["f_c"][lam],
                               grid_used=str(fs)))
    diag["N_ladder_f_c"] = ladder_tbl

    ign_tbl, fc_tbl = [], []
    for lam in [l for l in dc["f_grid"] if l != fx["lambda_no_ignition"]]:
        Au = branches[lam]["A_u"]
        thr = 1.5 * Au
        per_f = []
        for f in dc["f_grid"][lam]:
            rs = [r for r in res if r["lam"] == lam and r["f"] == f]
            row = dict(lam=lam, f_nominal=f,
                       realized_reach=float(np.mean([r["realized_reach"] for r in rs])),
                       A_u=Au, threshold=thr)
            for h in fx["horizons"]:
                ig = [1 if r[f"A_{int(h)}"] > thr else 0 for r in rs]
                row[f"p_ignite_t{int(h)}"] = float(np.mean(ig))
            row["A_160_mean_ignited"] = float(np.mean(
                [r["A_160"] for r in rs if r["A_160"] > thr])) if any(
                r["A_160"] > thr for r in rs) else float("nan")
            per_f.append(row)
            ign_tbl.append(row)
        fc = {}
        for h in fx["horizons"]:
            fc[f"f_c_t{int(h)}"] = _interp_half(
                [(r["realized_reach"], r[f"p_ignite_t{int(h)}"]) for r in per_f])
        cells = []
        for f in dc["f_grid"][lam]:
            rs = [r for r in res if r["lam"] == lam and r["f"] == f]
            cells.append((float(np.mean([r["realized_reach"] for r in rs])),
                          [1 if r["A_160"] > thr else 0 for r in rs]))
        fcv, flo, fhi, _ = a6.bootstrap_threshold(cells, B=dc["bootstrap_draws"],
                                                  seed=4000 + int(lam * 100))
        fnb = ladder_bias.get(lam)
        fc_tbl.append(dict(lam=lam, A_u=Au, threshold=thr,
                           f_c_registered=fx["f_c"][lam],
                           f_c_registered_err=fx["f_c_err"][lam],
                           f_c_bootstrap=fcv, ci_lo=flo, ci_hi=fhi, **fc))
        V.append(a6.verdict_with_ci(
            name=f"P4 finite-amplitude threshold f_c at lambda = {lam}",
            predicted=fx["f_c"][lam], measured=fcv, ci_lo_abs=flo, ci_hi_abs=fhi,
            delta=cfg.DELTA_TRAJECTORY_FRAC * fx["f_c"][lam],
            delta_basis=f"A6 trajectory marker: 5% of {fx['f_c'][lam]}",
            N=N, n_replicates=nrep,
            interval_kind=f"bootstrap ({dc['bootstrap_draws']} draws) of the 50% "
                          f"point of the ignition-probability curve against "
                          f"REALIZED reach, horizon t = 160",
            numerical_error=fx["f_c_err"][lam], closure_error=None,
            finite_N_bias=fnb,
            note=f"criterion A(160) > 1.5 A_u = {thr:.6f}; horizon sensitivity "
                 f"{ {k: round(v, 5) for k, v in fc.items()} }"))
        ast = np.array([r["A_160"] for r in res
                        if r["lam"] == lam and r["A_160"] > thr])
        if ast.size:
            V.append(_mk(f"P4 upper branch A* at lambda = {lam}",
                         fx["A_star"][lam], ast,
                         cfg.DELTA_TRAJECTORY_FRAC * fx["A_star"][lam],
                         f"A6 trajectory marker: 5% of {fx['A_star'][lam]}", N,
                         finite_N_bias=None,
                         numerical_error=abs(branches[lam]["A_star"] -
                                             fx["A_star"][lam]),
                         closure_error=None,
                         note=f"A(160) over the {ast.size} ignited runs; the C2(b) "
                              f"quadrature gives {branches[lam]['A_star']:.6f}"))
    diag["ignition_grid"] = ign_tbl
    diag["f_c_and_horizon_sensitivity"] = fc_tbl
    diag["reference_reproduction"] = dict(
        lambda_c_computed=PS.p4_lambda_c()["lambda_c"],
        lambda_c_registered=fx["lambda_c"],
        lambda_fold_computed=PS.p4_fold()["lambda_fold"],
        lambda_fold_registered=fx["lambda_fold"],
        note="A_u(lambda) is not tabulated in A4; it is computed from the C2(b) "
             "exact stationary quadrature, validated against C2.16 to O(nu^3) and "
             "against the three registered A* values")
    return V, raw, diag


def _interp_half(pairs):
    pairs = sorted(pairs)
    xs = [p[0] for p in pairs]; ys = [p[1] for p in pairs]
    for i in range(1, len(xs)):
        if ys[i - 1] < 0.5 <= ys[i]:
            if ys[i] == ys[i - 1]:
                return xs[i]
            return xs[i - 1] + (0.5 - ys[i - 1]) / (ys[i] - ys[i - 1]) * (xs[i] - xs[i - 1])
    return float("nan")


# ============================================================================ P6
def run_P6(cfg):
    fx, dc = cfg.P6["fixed"], cfg.P6["declared"]
    N, nrep = fx["N"], fx["replicates"]
    V, raw, diag = [], [], {}
    jobs = [(CFG_PATH, "A", rep) for rep in range(nrep)]
    LOG(f"  P6 case A: {len(jobs)} runs (N={N})")
    resA = MAPPER(T2.p6_worker, jobs)
    td = np.array([r["t_dagger"] for r in resA])
    raw += [dict(test="P6", case="A", rep=r["rep"], seed=r["seed"], N=N,
                 t_dagger=r["t_dagger"], intA=r["intA"], t_final=r["t_final"])
            for r in resA]
    cA = fx["A"]
    V.append(_mk("P6 case A collapse time t_dagger vs the kinetic solution",
                 cA["t_dagger"], td,
                 cfg.DELTA_TRAJECTORY_FRAC * cA["t_dagger"],
                 f"A6 trajectory marker: 5% of {cA['t_dagger']}", N,
                 finite_N_bias=None, numerical_error=cA["t_dagger_err"],
                 closure_error=abs(cA["t_dagger"] - cA["adiabatic"]),
                 note=f"first downward crossing of A_f = {cA['crossing_level']}; the "
                      f"adiabatic value {cA['adiabatic']} is the approximation being "
                      f"assessed, closure error "
                      f"{abs(cA['t_dagger']-cA['adiabatic'])/cA['t_dagger']*100:.1f}% "
                      f"(A4 claims 6%)"))
    diag["case_A"] = dict(t_dagger_measured=float(td.mean()),
                          t_dagger_sd=float(td.std(ddof=1)),
                          t_dagger_registered=cA["t_dagger"],
                          t_dagger_registered_err=cA["t_dagger_err"],
                          adiabatic=cA["adiabatic"],
                          adiabatic_relative_error=abs(cA["t_dagger"] -
                                                       cA["adiabatic"]) / cA["t_dagger"],
                          adiabatic_error_claimed=cA["adiabatic_error_claim"])
    jobs = [(CFG_PATH, "B", rep) for rep in range(nrep)]
    LOG(f"  P6 case B: {len(jobs)} runs (reported only; see BLOCKED note)")
    resB = MAPPER(T2.p6_worker, jobs)
    raw += [dict(test="P6", case="B", rep=r["rep"], seed=r["seed"], N=N,
                 intA=r["intA"], t_final=r["t_final"],
                 lam_intA_total=cfg.P6["fixed"]["B"]["lam"] * r["intA"])
            for r in resB]
    grid = np.arange(0.0, dc["t_end_B"] + 1e-9, dc["sample_dt"])
    lamB = fx["B"]["lam"]
    lev_tbl = []
    for lev in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01]:
        ts, Ls = [], []
        for r in resB:
            t = T2._first_down_crossing(grid, r["A_trace"], lev)
            if not math.isnan(t):
                ts.append(t)
                Ls.append(float(np.interp(t, grid, r["cum_trace"])))
        if ts:
            lev_tbl.append(dict(activity_level=lev, t_cross_mean=float(np.mean(ts)),
                                Lambda_mean=float(np.mean(Ls)),
                                Lambda_sd=float(np.std(Ls, ddof=1))))
    diag["case_B_Lambda_vs_activity_level"] = lev_tbl
    diag["case_B_total"] = dict(
        lam_intA_total_mean=float(np.mean([lamB * r["intA"] for r in resB])),
        lam_intA_total_sd=float(np.std([lamB * r["intA"] for r in resB], ddof=1)),
        Lambda_registered=fx["B"]["Lambda_exact"], bridge_registered=fx["B"]["bridge"])
    diag["case_B_status"] = (
        "BLOCKED, no verdict. The registered comparison is 'exact Lambda = 25.4 at "
        "half fold activity versus bridge 20.35'. Neither the definition of Lambda "
        "nor case B's FOLD ACTIVITY appears in A4 or anywhere in "
        "review_packet_v0_6_1.md, whose Appendix C and Appendix D both stop at C6; "
        "the design cites C7, which is not a file in this project. A reconstruction "
        "of the frozen-rate fold from the C2(b) stationary quadrature was attempted "
        "and REFUTED on case A: over every frozen dose d in [c_b, 1) the saddle-node "
        "of lambda(nu) = nu/P_nu satisfies lambda_fold <= 2.574, so that construction "
        "cannot place a fold at case A's lambda = 3, let alone reproduce the "
        "registered A_f = 0.5603. Nothing was tuned to close the gap. The measured "
        "Lambda at each activity level is tabulated above so the comparison can be "
        "made without re-running once C7 is supplied.")
    return V, raw, diag


def _boot_spread(rows, orders, rho, tau0, lam, seed, B=4000):
    """Bootstrap the across-order spread of R/lambda over background realisations."""
    per = {str(o): np.array([r["Z1_mean"] / lam for r in rows
                             if r["order"] == str(o) and r["rho"] == rho
                             and r["tau0"] == tau0]) for o in orders}
    rng = np.random.default_rng(seed)
    n = min(len(v) for v in per.values())
    pt = max(v.mean() for v in per.values()) - min(v.mean() for v in per.values())
    d = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        ms = [v[:n][idx].mean() for v in per.values()]
        d[b] = max(ms) - min(ms)
    return float(pt), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


RUNNERS = {"P1": run_P1, "P1-delay": run_P1_delay, "P2": run_P2,
           "P2-delay": run_P2_delay, "P3": run_P3, "P4": run_P4, "P6": run_P6}
