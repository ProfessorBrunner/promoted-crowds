"""Acceptance tests T1-T6 of design v0.3 section A2, under the A6 pass rule.

Each `run_tN` returns (verdict_rows, raw_rows, extra) where
  verdict_rows : list of a6.Verdict  (the certified table)
  raw_rows     : list of dict, one per simulation run -- the sufficient
                 statistics from which every certified number is recomputed
  extra        : reported diagnostics that A2 does not make acceptance conditions
"""

from __future__ import annotations

import math
import sys

import numpy as np
from scipy import stats

from . import a6, engine as E, predictions as P
from .angles import cosd, cos2d
from .handtable import HAND_CASES
from .runner import RunConfig, run_one, build_registry_for
from .rng import derive_run_seed

FP_TOL = 1e-12   # floating-point representation tolerance for pathwise identities


def _counts4(pulse_out):
    """4-cell outcome counts (AA, AR, RA, RR) over agents that got both pulses."""
    o1, o2 = pulse_out[:, 0], pulse_out[:, 1]
    m = (o1 >= 0) & (o2 >= 0)
    o1, o2 = o1[m], o2[m]
    return (int(((o1 == 1) & (o2 == 1)).sum()),
            int(((o1 == 1) & (o2 == 0)).sum()),
            int(((o1 == 0) & (o2 == 1)).sum()),
            int(((o1 == 0) & (o2 == 0)).sum()))


# =========================================================================  T1
def run_t1(cfgmod, log=print):
    C = cfgmod.T1
    fx, dc = C["fixed"], C["declared"]
    eps, c_b, r, alpha = fx["eps"], fx["c_b"], fx["r"], fx["alpha"]
    L = P.lifetime_L(eps, c_b)
    verdicts, raw, extra = [], [], {}

    # ---- T1.1  lambda = 0: the lifetime is EXACTLY L
    z = dc["zero_lambda"]
    dur_err_max = 0.0
    n_agents = 0
    for i in range(z["replicates"]):
        seed = derive_run_seed(cfgmod.MASTER_SEED, 1, 1, i)
        cfg = RunConfig(N=z["N"], eps=eps, c_b=c_b, c_h=dc["c_h"], alpha=alpha,
                        beta=dc["beta"], r=r, lam=0.0, rho=0.0, kappa=0.0,
                        f=z["f"], pulses=((0.0, fx["pulse_angle_deg"]),),
                        initial_law="I1", t_end=z["t_end"],
                        stop_on_extinction=False)
        o = run_one(cfg, seed)
        act = o["ever_active"] == 1
        d = o["t_first_deact"][act] - o["t_first_act"][act]
        dur_err_max = max(dur_err_max, float(np.abs(d - L).max()))
        n_agents += int(act.sum())
        assert int(act.sum()) == int((o["u"] == 1).sum()), "every cohort member must activate"
        assert set(np.unique(o["n_intervals"][act]).tolist()) == {1}
        raw.append(dict(test="T1.1", rep=i, seed=seed, N=z["N"], lam=0.0,
                        f=z["f"], n_active=int(act.sum()),
                        max_abs_dur_minus_L=float(np.abs(d - L).max())))
    verdicts.append(a6.Verdict(
        name="T1.1 lambda=0 lifetime equals L exactly (pathwise)",
        predicted=L, measured=L + dur_err_max, diff=dur_err_max,
        ci_lo=dur_err_max, ci_hi=dur_err_max, delta=0.0,
        delta_basis="pathwise identity; 0 tolerance (double-precision equality)",
        status=a6.PASS if dur_err_max == 0.0 else a6.FAIL,
        n_replicates=z["replicates"], N=z["N"], replicates_needed=None,
        mc_error=0.0, finite_N_bias=0.0, numerical_error=0.0, closure_error=0.0,
        interval_kind="exact pathwise (max over all agents)",
        note=f"{n_agents} agent lifetimes, every one bit-identical to L={L!r}"))

    # ---- T1.2-T1.4  full cascade on the N ladder, both cells
    for cell in dc["cells"]:
        pred = P.t1_prediction(f=cell["f"], lam=cell["lam"], eps=eps, c_b=c_b, r=r)
        Lp = pred["L_plus"]
        ladder = []
        per_N = {}
        for N in dc["ladder"]:
            nrep = dc["replicates"][N]
            Zs, vL, vLp, reach = [], 0, 0, []
            for i in range(nrep):
                seed = derive_run_seed(cfgmod.MASTER_SEED, 1, 10 + ord(cell["name"]), N, i)
                cfg = RunConfig(N=N, eps=eps, c_b=c_b, c_h=dc["c_h"], alpha=alpha,
                                beta=dc["beta"], r=r, lam=cell["lam"], rho=0.0,
                                kappa=0.0, f=cell["f"],
                                pulses=((0.0, fx["pulse_angle_deg"]),),
                                initial_law="I1", t_end=dc["t_end"],
                                stop_on_extinction=True)
                o = run_one(cfg, seed)
                act = o["ever_active"] == 1
                Z = float(act.mean())
                d1 = o["t_first_deact"][act] - o["t_first_act"][act]
                dl = o["t_last_deact"][act] - o["t_first_act"][act]
                n1 = int((d1 < L - FP_TOL).sum())
                n2 = int((dl > Lp + FP_TOL).sum())
                Zs.append(Z); vL += n1; vLp += n2
                reach.append(o["realized_reach"])
                raw.append(dict(test="T1.4", cell=cell["name"], rep=i, seed=seed,
                                N=N, lam=cell["lam"], f=cell["f"], Z=Z,
                                realized_reach=o["realized_reach"],
                                intA_over_N=float(o["agg"][E.A_INTA] / N),
                                n_receipts=float(o["agg"][E.A_NRECEIPT]),
                                viol_first_interval_lt_L=n1,
                                viol_activity_after_Lplus=n2,
                                min_first_interval=float(d1.min()),
                                max_last_minus_first=float(dl.max())))
                log(f"  T1 cell {cell['name']} N={N} rep={i} Z={Z:.6f} "
                    f"viol=({n1},{n2})")
            per_N[N] = dict(Z=np.array(Zs), vL=vL, vLp=vLp,
                            reach=float(np.mean(reach)), nrep=nrep,
                            n_activated=int(round(float(np.sum(Zs)) * N)))
            ladder.append((N, float(np.mean(Zs))))
        bias = a6.finite_N_bias_from_ladder(ladder)
        Nmax = dc["ladder"][-1]
        tot_vL = sum(per_N[N]["vL"] for N in dc["ladder"])
        tot_vLp = sum(per_N[N]["vLp"] for N in dc["ladder"])
        tot_ag = sum(per_N[N]["nrep"] * N for N in dc["ladder"])
        tot_act = sum(per_N[N]["n_activated"] for N in dc["ladder"])
        verdicts.append(a6.Verdict(
            name=f"T1.2 cell {cell['name']}: first active interval >= L (pathwise)",
            predicted=0.0, measured=float(tot_vL), diff=float(tot_vL),
            ci_lo=float(tot_vL), ci_hi=float(tot_vL), delta=0.0,
            delta_basis="pathwise identity; any violation is a FAIL",
            status=a6.PASS if tot_vL == 0 else a6.FAIL,
            n_replicates=sum(per_N[N]["nrep"] for N in dc["ladder"]), N=Nmax,
            replicates_needed=None, mc_error=0.0, finite_N_bias=0.0,
            numerical_error=FP_TOL, closure_error=0.0,
            interval_kind="exact pathwise (violation count over all agents)",
            note=f"violations out of {tot_act} first-active intervals "
                 f"(agents that ever activated, out of {tot_ag} agents simulated); "
                 f"L={L:.15g}, tolerance {FP_TOL:g} is floating-point only"))
        verdicts.append(a6.Verdict(
            name=f"T1.3 cell {cell['name']}: no activity after L_+ (pathwise)",
            predicted=0.0, measured=float(tot_vLp), diff=float(tot_vLp),
            ci_lo=float(tot_vLp), ci_hi=float(tot_vLp), delta=0.0,
            delta_basis="pathwise identity; any violation is a FAIL",
            status=a6.PASS if tot_vLp == 0 else a6.FAIL,
            n_replicates=sum(per_N[N]["nrep"] for N in dc["ladder"]), N=Nmax,
            replicates_needed=None, mc_error=0.0, finite_N_bias=0.0,
            numerical_error=FP_TOL, closure_error=0.0,
            interval_kind="exact pathwise (violation count over all agents)",
            note=f"violations out of {tot_act} activated agents (out of "
                 f"{tot_ag} simulated); L_+ = {Lp:.15g}, "
                 f"L_+ - L = {Lp - L:.7g}"))
        verdicts.append(a6.make_verdict(
            name=f"T1.4 cell {cell['name']} (lam={cell['lam']}, f={cell['f']}): "
                 f"final size Z vs 1-Z=(1-f)exp(-lam L Z)",
            predicted=pred["Z"], per_replicate_values=per_N[Nmax]["Z"],
            delta=cfgmod.DELTA_TRAJECTORY_FRAC * pred["Z"],
            delta_basis=f"A6 trajectory marker: 5% of {pred['Z']:.6f}",
            N=Nmax, numerical_error=pred["numerical_error"],
            closure_error=pred["closure_error"],
            finite_N_bias=bias.get("residual_bias_at_Nmax", bias.get("top_gap")),
            note=f"realized reach {per_N[Nmax]['reach']:.6f} (nominal {cell['f']}); "
                 f"small-r closure bracket Z in [{pred['Z']:.8f}, "
                 f"{pred['Z_at_Lplus']:.8f}]"))
        extra[f"T1_cell_{cell['name']}"] = dict(prediction=pred, ladder=bias)
    extra["L"] = L
    return verdicts, raw, extra


# =========================================================================  T2
def run_t2(cfgmod, log=print):
    C = cfgmod.T2
    fx, dc = C["fixed"], C["declared"]
    pred = P.t2_prediction(lam=fx["lam"], eps=fx["eps"], c_b=fx["c_b"])
    verdicts, raw = [], []
    ladder, per_N = [], {}
    camp_viol = 0
    for N in dc["ladder"]:
        nrep = dc["replicates"][N]
        vals = []
        for i in range(nrep):
            seed = derive_run_seed(cfgmod.MASTER_SEED, 2, N, i)
            cfg = RunConfig(N=N, eps=fx["eps"], c_b=fx["c_b"], c_h=dc["c_h"],
                            alpha=fx["alpha"], beta=fx["beta"], r=fx["r"],
                            lam=fx["lam"], rho=dc["rho"], kappa=dc["kappa"], f=0.0,
                            initial_law="two_camps", M_plus=dc["M_plus"],
                            t_end=dc["t_end"],
                            t_measure_start=dc["t_measure_start"],
                            stop_on_extinction=False)
            o = run_one(cfg, seed)
            Abar = float(o["agg"][E.A_INTA_WIN] / (N * o["agg"][E.A_WINLEN]))
            # camps must be fixed: phi in {0, 90} and stance matching orientation
            ph, st = o["phi_final"], o["s_final"]
            bad = int((~np.isin(ph, [0, 90])).sum()
                      + ((ph == 0) & (st != 1)).sum() + ((ph == 90) & (st != -1)).sum())
            camp_viol += bad
            vals.append(Abar)
            raw.append(dict(test="T2", rep=i, seed=seed, N=N, A_bar=Abar,
                            camp_violations=bad,
                            n_broadcast=float(o["agg"][E.A_NBROADCAST]),
                            window=float(o["agg"][E.A_WINLEN])))
            log(f"  T2 N={N} rep={i} A_bar={Abar:.6f}")
        per_N[N] = np.array(vals)
        ladder.append((N, float(np.mean(vals))))
    bias = a6.finite_N_bias_from_ladder(ladder)
    Nmax = dc["ladder"][-1]
    verdicts.append(a6.Verdict(
        name="T2.1 two camps remain fixed (pathwise)",
        predicted=0.0, measured=float(camp_viol), diff=float(camp_viol),
        ci_lo=float(camp_viol), ci_hi=float(camp_viol), delta=0.0,
        delta_basis="structural identity; any violation is a FAIL",
        status=a6.PASS if camp_viol == 0 else a6.FAIL,
        n_replicates=sum(dc["replicates"].values()), N=Nmax,
        replicates_needed=None, mc_error=0.0, finite_N_bias=0.0,
        numerical_error=0.0, closure_error=0.0,
        interval_kind="exact pathwise (violation count over all agents)",
        note="phi in {0,90} and stance matching orientation at the horizon"))
    verdicts.append(a6.make_verdict(
        name="T2.2 renewal corner A* vs A=1-exp(-lam L A)",
        predicted=pred["A_star"], per_replicate_values=per_N[Nmax],
        delta=cfgmod.DELTA_TRAJECTORY_FRAC * pred["A_star"],
        delta_basis=f"A6 trajectory marker: 5% of {pred['A_star']:.6f}",
        N=Nmax, numerical_error=pred["numerical_error"], closure_error=0.0,
        finite_N_bias=bias.get("residual_bias_at_Nmax", bias.get("top_gap")),
        note=f"lam*L = {pred['lamL']:.9f}; A(t) time-averaged over "
             f"[{dc['t_measure_start']}, {dc['t_end']}]; closure error 0 "
             f"(C2.24 is EXACT for this submodel, not a closure)"))
    return verdicts, raw, dict(prediction=pred, ladder=bias)


# =========================================================================  T3
def run_t3(cfgmod, log=print):
    C = cfgmod.T3
    dc = C["declared"]
    a = dc["a"]
    verdicts, raw, extra = [], [], {}

    # ---- T3(a)  prescribed Poisson input of known intensity
    Lam = a["exo_nu0"] * (1.0 - math.exp(-a["exo_gamma"] * a["exo_T"])) / a["exo_gamma"]
    means, varis = [], []
    hist_tot = np.zeros(80, dtype=np.int64)
    for i in range(a["replicates"]):
        seed = derive_run_seed(cfgmod.MASTER_SEED, 3, 1, i)
        cfg = RunConfig(N=a["N"], eps=a["eps"], c_b=a["c_b"], c_h=a["c_h"],
                        alpha=a["alpha"], beta=a["beta"], r=a["r"], lam=a["lam"],
                        rho=a["rho"], kappa=a["kappa"], f=a["f"],
                        pulses=((0.0, a["pulse_angle_deg"]),), initial_law="I1",
                        t_end=a["exo_T"], stop_on_extinction=False,
                        exo_rate_fn=a["exo_rate_fn"], exo_rate_nu0=a["exo_nu0"],
                        exo_rate_gamma=a["exo_gamma"], exo_t_end=a["exo_T"],
                        exo_angle_deg=a["exo_angle_deg"])
        o = run_one(cfg, seed)
        n = o["n_counters"][:, 0].astype(np.int64)
        k = n - 1
        assert k.min() >= 0
        means.append(float(k.mean())); varis.append(float(k.var(ddof=1)))
        bc = np.bincount(k, minlength=80)[:80]
        hist_tot += bc
        raw.append(dict(test="T3a", rep=i, seed=seed, N=a["N"], Lambda=Lam,
                        mean_k=float(k.mean()), var_k=float(k.var(ddof=1)),
                        n_exo=float(o["agg"][E.A_NEXO])))
        log(f"  T3a rep={i} mean={k.mean():.5f} var={k.var(ddof=1):.5f}")
    verdicts.append(a6.make_verdict(
        name="T3a.1 counter mean after one pulse vs 1 + Lambda",
        predicted=1.0 + Lam,
        per_replicate_values=np.array(means) + 1.0,
        delta=cfgmod.DELTA_OPERATOR_FRAC * (1.0 + Lam),
        delta_basis=f"A6 operator check: 2% of {1.0 + Lam:.6f}",
        N=a["N"], numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0,
        note="prescribed intensity, so no mean-field closure and no finite-N "
             "coupling: the law is exactly 1 + Poisson(Lambda)"))
    verdicts.append(a6.make_verdict(
        name="T3a.2 counter variance vs Lambda",
        predicted=Lam, per_replicate_values=np.array(varis),
        delta=cfgmod.DELTA_OPERATOR_FRAC * Lam,
        delta_basis=f"A6 operator check: 2% of {Lam:.6f}",
        N=a["N"], numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0))
    # goodness of fit on the pooled law
    ntot = int(hist_tot.sum())
    pk = stats.poisson.pmf(np.arange(80), Lam)
    expct = pk * ntot
    keep = expct >= 5.0
    obs = np.concatenate([hist_tot[keep], [ntot - hist_tot[keep].sum()]])
    exp = np.concatenate([expct[keep], [ntot - expct[keep].sum()]])
    chi2 = float(((obs - exp) ** 2 / exp).sum())
    dof = int(keep.sum())  # cells - 1, no fitted parameter (Lambda is predicted)
    gof_p = float(stats.chi2.sf(chi2, dof))
    tv = 0.5 * float(np.abs(hist_tot / ntot - pk).sum())
    extra["T3a_gof"] = dict(Lambda=Lam, chi2=chi2, dof=dof, p_value=gof_p,
                            total_variation=tv, n_pooled=ntot)

    # ---- T3(b)  hand-computed table of coincident-pulse outcomes
    nb_fail, nb_tot, details = 0, 0, []
    for ci, case in enumerate(HAND_CASES):
        cfg, exp_ = case["cfg"], case["expect"]
        seed = derive_run_seed(cfgmod.MASTER_SEED, 3, 2, ci)
        o = run_one(cfg, seed)
        reg, info = build_registry_for(cfg)
        ok_all, items = True, {}
        po = o["pulse_out"]
        if "pulse_out" in exp_:
            ok = po[0].tolist() == exp_["pulse_out"] and bool((po == po[0]).all())
            items["pulse_out"] = ok; ok_all &= ok
        if "counters" in exp_:
            nc = o["n_counters"]
            ok = all(bool((nc[:, k] == v).all()) for k, v in exp_["counters"].items()) \
                 and bool((nc.sum(1) == sum(exp_["counters"].values())).all())
            items["counters"] = ok; ok_all &= ok
        if "n_classes" in exp_:
            ok = info["n_classes"] == exp_["n_classes"]
            items["n_classes"] = ok; ok_all &= ok
        if "class_of" in exp_:
            ok = all(reg.of(k) == v for k, v in exp_["class_of"].items())
            items["class_of"] = ok; ok_all &= ok
        for key, arr in [("phi", "phi_final"), ("s", "s_final"),
                         ("n_intervals", "n_intervals")]:
            if key in exp_:
                ok = bool((o[arr] == exp_[key]).all()); items[key] = ok; ok_all &= ok
        for key, arr in [("t_first_act", "t_first_act"),
                         ("t_first_deact", "t_first_deact"),
                         ("t_last_deact", "t_last_deact"),
                         ("act_time", "act_time"), ("c_at_t_end", "c_final")]:
            if key in exp_:
                err = float(np.nanmax(np.abs(o[arr] - exp_[key])))
                ok = err <= 1e-15 * max(1.0, abs(exp_[key])); items[key] = ok
                ok_all &= ok
        if "P_AR" in exp_:
            nAA, nAR, nRA, nRR = _counts4(po)
            items["P_AR"] = nAR == 0; items["P_RA"] = nRA == 0
            items["recons_live"] = o["agg"][E.A_NRECONS] > 0
            ok_all &= (nAR == 0 and nRA == 0 and o["agg"][E.A_NRECONS] > 0)
        nb_tot += len(items); nb_fail += sum(1 for v in items.values() if not v)
        details.append(dict(case=case["name"], seed=seed, passed=bool(ok_all),
                            items=items))
        raw.append(dict(test="T3b", case=case["name"], seed=seed,
                        passed=bool(ok_all)))
        log(f"  T3b {case['name']}: {'PASS' if ok_all else 'FAIL'}")
    verdicts.append(a6.Verdict(
        name="T3b class identifiers and transition bookkeeping vs hand table",
        predicted=0.0, measured=float(nb_fail), diff=float(nb_fail),
        ci_lo=float(nb_fail), ci_hi=float(nb_fail), delta=0.0,
        delta_basis="exact hand-computed values; any mismatch is a FAIL",
        status=a6.PASS if nb_fail == 0 else a6.FAIL,
        n_replicates=len(HAND_CASES), N=0, replicates_needed=None,
        mc_error=0.0, finite_N_bias=0.0, numerical_error=1e-15, closure_error=0.0,
        interval_kind="exact (count of mismatched hand-table entries)",
        note=f"{nb_tot} checked quantities over {len(HAND_CASES)} deterministic cases"))
    extra["T3b_details"] = details

    # ---- T3(c)  full-system formula as a CONVERGENCE CHECK across the N ladder
    c = dc["c"]
    T1 = cfgmod.T1
    cell = [x for x in T1["declared"]["cells"] if x["name"] == c["cell"]][0]
    conv = []
    for N in c["ladder"]:
        mk, vk, lamIA, gof = [], [], [], []
        for i in range(c["replicates"]):
            seed = derive_run_seed(cfgmod.MASTER_SEED, 3, 3, N, i)
            cfg = RunConfig(N=N, eps=T1["fixed"]["eps"], c_b=T1["fixed"]["c_b"],
                            c_h=T1["declared"]["c_h"], alpha=T1["fixed"]["alpha"],
                            beta=T1["declared"]["beta"], r=T1["fixed"]["r"],
                            lam=cell["lam"], f=cell["f"],
                            pulses=((0.0, T1["fixed"]["pulse_angle_deg"]),),
                            initial_law="I1", t_end=T1["declared"]["t_end"],
                            stop_on_extinction=True)
            o = run_one(cfg, seed)
            coh = o["u"] == 1
            k = (o["n_counters"][coh, 0] - 1).astype(np.int64)
            Lam_i = cell["lam"] * float(o["agg"][E.A_INTA] / N)
            mk.append(float(k.mean())); vk.append(float(k.var(ddof=1)))
            lamIA.append(Lam_i)
            nn = k.size
            pk = stats.poisson.pmf(np.arange(60), Lam_i)
            ex = pk * nn
            kp = ex >= 5.0
            bc = np.bincount(k, minlength=60)[:60]
            ob = np.concatenate([bc[kp], [nn - bc[kp].sum()]])
            ee = np.concatenate([ex[kp], [nn - ex[kp].sum()]])
            gof.append(float(((ob - ee) ** 2 / ee).sum()) / max(int(kp.sum()), 1))
            raw.append(dict(test="T3c", rep=i, seed=seed, N=N,
                            mean_k=float(k.mean()), var_k=float(k.var(ddof=1)),
                            lam_intA=Lam_i, chi2_per_dof=gof[-1]))
        conv.append(dict(N=N, mean_k=float(np.mean(mk)),
                         mean_lam_intA=float(np.mean(lamIA)),
                         mean_minus_pred=float(np.mean(mk) - np.mean(lamIA)),
                         var_k=float(np.mean(vk)),
                         var_minus_pred=float(np.mean(vk) - np.mean(lamIA)),
                         chi2_per_dof=float(np.mean(gof))))
        log(f"  T3c N={N} mean-pred={conv[-1]['mean_minus_pred']:+.5f} "
            f"var-pred={conv[-1]['var_minus_pred']:+.5f}")
    extra["T3c_convergence"] = conv
    extra["T3c_status"] = ("REPORTED (design A2 T3: the full-system formula is a "
                           "mean-field statement and is NOT a finite-N acceptance "
                           "condition)")
    return verdicts, raw, extra


# ====================================================================  T4 / T6
def _t4_specs(cfgmod):
    C = cfgmod.T4
    fx, dc = C["fixed"], C["declared"]
    th1 = dc["theta1_deg"]
    specs = []
    for D in fx["deltas_deg"]:
        for order in (1, 2):
            a1, a2 = (th1, th1 + D) if order == 1 else (th1 + D, th1)
            for law in fx["initial_laws"]:
                for ac in dc["agent_classes"]:
                    specs.append(dict(D=D, order=order, theta_first=a1,
                                      theta_second=a2, law=law, agent_class=ac))
    return specs


def _t4_cfg(cfgmod, sp, N):
    dc = cfgmod.T4["declared"]
    kw = dict(N=N, agent_class=sp["agent_class"], eps=dc["eps"], c_b=dc["c_b"],
              c_h=dc["c_h"], alpha=dc["alpha"], beta=dc["beta"], r=dc["r"],
              lam=dc["lam"], f=dc["f"],
              pulses=((0.0, sp["theta_first"]), (0.0, sp["theta_second"])),
              t_end=dc["t_end"], stop_on_extinction=False)
    if sp["law"] == "I3":
        kw.update(initial_law="I3", rho=dc["i3_rho"], kappa=dc["i3_kappa"],
                  delta_deg=dc["i3_delta_deg"],
                  p_plus=0.5 * (1.0 + cfgmod.T4["fixed"]["i3_x"]),
                  i3_relax_time=dc["i3_relax_factor"] / (dc["i3_rho"] + dc["i3_kappa"]))
        if sp["agent_class"] == "surrogate":
            # C5.0 declares the surrogate only at rho = kappa = 0.  The I3
            # ORIENTATION law is still built by relaxing the silent process (c = 0
            # throughout, so the surrogate's receipt rule never fires during the
            # relaxation); the surrogate is then initialised by its declared
            # pure-state lift a0 = phi0, tau0 = 1 on that law.  rho and kappa are
            # inert in the main phase here: the campaign is coincident, so no
            # clock event may occur between the two pulses, and t_end = 0.
            kw.update(rho_main=0.0, kappa_main=0.0)
    else:
        kw.update(initial_law=sp["law"])
    return RunConfig(**kw)


def _t4_law(cfgmod, law):
    dc = cfgmod.T4["declared"]
    if law == "I3":
        return P._orientation_law("I3",
                                  p_plus=0.5 * (1.0 + cfgmod.T4["fixed"]["i3_x"]),
                                  rho=dc["i3_rho"], kappa=dc["i3_kappa"],
                                  delta=dc["i3_delta_deg"])
    return P._orientation_law(law)


def _t4_worker(args):
    cfgmod_path, sp, N, seed = args
    cfgmod = _load_cfg(cfgmod_path)
    cfg = _t4_cfg(cfgmod, sp, N)
    o = run_one(cfg, seed)
    nAA, nAR, nRA, nRR = _counts4(o["pulse_out"])
    return dict(nAA=nAA, nAR=nAR, nRA=nRA, nRR=nRR,
                x=float(o["s_final"].mean()),
                realized_reach=o["realized_reach"],
                i3_x=(None if o["i3_relax"] is None else o["i3_relax"]["x_realized"]))


def _a5_worker(args):
    """Run the process and the automaton on the SAME seed and compare pathwise.

    Design A5 predicts the outcome-memory automaton "reproduces every joint law".
    The automaton's state (last framing, last outcome) is a re-coordinatization of
    the orientation phi -- after accepting theta the orientation is theta, after
    rejecting it is theta + 90 deg -- and its acceptance probability is therefore
    identical message by message.  Under a shared seed the two agent classes must
    agree AGENT BY AGENT, which is strictly stronger than agreeing in law and is
    checkable at zero tolerance.
    """
    cfg_path, sp, N, seed = args
    cfgmod = _load_cfg(cfg_path)
    op = run_one(_t4_cfg(cfgmod, {**sp, "agent_class": "process"}, N), seed)
    oa = run_one(_t4_cfg(cfgmod, {**sp, "agent_class": "automaton"}, N), seed)
    return dict(
        diff_outcomes=int((op["pulse_out"] != oa["pulse_out"]).sum()),
        diff_c=int((op["c_final"] != oa["c_final"]).sum()),
        diff_s=int((op["s_final"] != oa["s_final"]).sum()),
        diff_n=int((op["n_counters"] != oa["n_counters"]).sum()),
    )


_CFGMOD = {}


def _load_cfg(path):
    if path not in _CFGMOD:
        import importlib.util
        spec = importlib.util.spec_from_file_location("stage1_config", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _CFGMOD[path] = m
    return _CFGMOD[path]


def run_t4_t6(cfgmod, cfg_path, pool=None, log=print):
    C = cfgmod.T4
    fx, dc = C["fixed"], C["declared"]
    N, nrep = dc["N"], dc["replicates"]
    delta = cfgmod.delta_t4(N)
    specs = _t4_specs(cfgmod)
    jobs = []
    for si, sp in enumerate(specs):
        for i in range(nrep):
            seed = derive_run_seed(cfgmod.MASTER_SEED, 4, si, i)
            jobs.append((cfg_path, sp, N, seed))
    log(f"  T4/T6: {len(specs)} cells x {nrep} replicates = {len(jobs)} runs")
    results = list(pool.map(_t4_worker, jobs)) if pool else [ _t4_worker(j) for j in jobs ]

    verdicts, raw, extra = [], [], {}
    by = {}
    for (jj, res) in zip(jobs, results):
        sp = jj[1]
        key = (sp["D"], sp["order"], sp["law"], sp["agent_class"])
        by.setdefault(key, []).append(res)
        raw.append(dict(test="T4T6", D=sp["D"], order=sp["order"], law=sp["law"],
                        agent_class=sp["agent_class"], seed=jj[3], N=N, **res))

    joint_tbl = []
    for D in fx["deltas_deg"]:
        for order in (1, 2):
            th1 = dc["theta1_deg"] if order == 1 else dc["theta1_deg"] + D
            th2 = dc["theta1_deg"] + D if order == 1 else dc["theta1_deg"]
            for law in fx["initial_laws"]:
                olaw = _t4_law(cfgmod, law)
                pp = P.t4_process_joint(th1, th2, olaw)
                ps = P.t6_surrogate_joint(th1, th2, olaw)
                for ac in dc["agent_classes"]:
                    rs = by[(D, order, law, ac)]
                    tot = np.array([[r["nAA"], r["nAR"], r["nRA"], r["nRR"]]
                                    for r in rs], dtype=float)
                    nper = tot.sum(1)
                    same = (tot[:, 0] + tot[:, 3]) / nper
                    ref = pp if ac in ("process", "automaton") else ps
                    label = ("T4" if ac in ("process", "automaton") else "T6")
                    verdicts.append(a6.make_verdict(
                        name=f"{label} P(AA)+P(RR) | Delta={D} order={order} "
                             f"{law} {ac}",
                        predicted=ref["P_same"] if ac == "surrogate" else pp["cos2Delta"],
                        per_replicate_values=same, delta=delta,
                        delta_basis=f"A2 T4: 3/sqrt(N) = {delta:.7f}",
                        N=N, numerical_error=0.0, closure_error=0.0,
                        finite_N_bias=0.0,
                        note=("agents are independent at lambda=0, so there is no "
                              "finite-N coupling; "
                              + (f"E[tau1^2]={ps['E_tau1_sq']:.9f}" if ac == "surrogate"
                                 else f"q1={pp['q1']:.9f}"))))
                    cells = tot.sum(0) / tot.sum()
                    joint_tbl.append(dict(
                        Delta=D, order=order, law=law, agent_class=ac,
                        P_AA=cells[0], P_AR=cells[1], P_RA=cells[2], P_RR=cells[3],
                        pred_P_AA=ref["P_AA"], pred_P_AR=ref["P_AR"],
                        pred_P_RA=ref["P_RA"], pred_P_RR=ref["P_RR"],
                        max_cell_dev=float(np.max(np.abs(
                            cells - np.array([ref["P_AA"], ref["P_AR"],
                                              ref["P_RA"], ref["P_RR"]])))),
                        P_same=float(cells[0] + cells[3]),
                        pred_P_same=ref["P_same"] if ac == "surrogate" else pp["cos2Delta"]))
    extra["joint_law_table"] = joint_tbl

    # ---- A5 positive equivalence control: automaton reproduces the joint law
    tv_max, tv_rows = 0.0, []
    for D in fx["deltas_deg"]:
        for order in (1, 2):
            for law in fx["initial_laws"]:
                pr = np.sum([[r["nAA"], r["nAR"], r["nRA"], r["nRR"]]
                             for r in by[(D, order, law, "process")]], 0).astype(float)
                au = np.sum([[r["nAA"], r["nAR"], r["nRA"], r["nRR"]]
                             for r in by[(D, order, law, "automaton")]], 0).astype(float)
                p, q = pr / pr.sum(), au / au.sum()
                tv = 0.5 * float(np.abs(p - q).sum())
                ndiff = int(np.abs(pr - au).sum())
                if ndiff == 0:
                    # the automaton state (last framing, last outcome) is a
                    # re-coordinatization of phi with an identical acceptance
                    # probability message by message, so under a shared seed the
                    # two agent classes agree PATHWISE, not merely in law.  The
                    # contingency test is degenerate; it is reported as such.
                    chi2, pv = 0.0, 1.0
                else:
                    keep = (pr + au) > 0
                    chi2, pv = stats.chi2_contingency(
                        np.vstack([pr[keep], au[keep]]))[:2]
                tv_max = max(tv_max, tv)
                tv_rows.append(dict(Delta=D, order=order, law=law,
                                    total_variation=tv, chi2=float(chi2),
                                    p_value=float(pv), count_difference=ndiff,
                                    pathwise_identical=bool(ndiff == 0)))
    extra["automaton_equivalence_independent_seeds"] = dict(
        rows=tv_rows, max_total_variation=tv_max,
        min_p_value=min(r["p_value"] for r in tv_rows),
        note="two INDEPENDENT samples of the same law (the grid gives each agent "
             "class its own derived seed); reported as a diagnostic, with no "
             "verdict, because the distance is Monte-Carlo estimated.  The "
             "verdict row for A5 is the pathwise shared-seed control below.")

    # ---- A5 positive equivalence control, in its pathwise form
    a5_jobs = []
    a5_cells = []
    for D in fx["deltas_deg"]:
        for order in (1, 2):
            th1 = dc["theta1_deg"] if order == 1 else dc["theta1_deg"] + D
            th2 = dc["theta1_deg"] + D if order == 1 else dc["theta1_deg"]
            for law in fx["initial_laws"]:
                ci = len(a5_cells)
                a5_cells.append((D, order, law))
                for i in range(dc["a5_replicates"]):
                    a5_jobs.append((cfg_path,
                                    dict(D=D, order=order, theta_first=th1,
                                         theta_second=th2, law=law,
                                         agent_class="process"),
                                    N, derive_run_seed(cfgmod.MASTER_SEED, 45, ci, i)))
    log(f"  A5 pathwise control: {len(a5_cells)} cells x "
        f"{dc['a5_replicates']} shared-seed pairs")
    a5_res = list(pool.map(_a5_worker, a5_jobs)) if pool else [_a5_worker(j) for j in a5_jobs]
    tot_diff = {k: int(sum(r[k] for r in a5_res))
                for k in ("diff_outcomes", "diff_c", "diff_s", "diff_n")}
    n_pairs = len(a5_res)
    for (jj, rr) in zip(a5_jobs, a5_res):
        raw.append(dict(test="A5", D=jj[1]["D"], order=jj[1]["order"],
                        law=jj[1]["law"], seed=jj[3], N=N, **rr))
    worst = max(tot_diff.values())
    extra["automaton_equivalence_pathwise"] = dict(
        cells=len(a5_cells), pairs=n_pairs, agents_compared=n_pairs * N,
        differences=tot_diff)
    verdicts.append(a6.Verdict(
        name="T4 A5 control: automaton reproduces the process pathwise",
        predicted=0.0, measured=float(worst), diff=float(worst),
        ci_lo=float(worst), ci_hi=float(worst), delta=0.0,
        delta_basis="A5 positive control; pathwise identity under a shared seed, "
                    "so 0 tolerance is attainable (see BUGLOG B1)",
        status=a6.PASS if worst == 0 else a6.FAIL,
        n_replicates=dc["a5_replicates"], N=N, replicates_needed=None,
        mc_error=0.0, finite_N_bias=0.0, numerical_error=0.0, closure_error=0.0,
        interval_kind="exact (count of disagreeing agents)",
        note=f"{n_pairs * N} agents over {len(a5_cells)} (Delta, order, initial "
             f"law) cells; disagreements: outcome pairs {tot_diff['diff_outcomes']}, "
             f"conviction {tot_diff['diff_c']}, stance {tot_diff['diff_s']}, "
             f"counters {tot_diff['diff_n']}"))

    # ---- T6 closed forms: aligned anchor gives cos^2 D, isotropic gives 1/2+cos2D/4
    cf = []
    for D in fx["deltas_deg"]:
        al = P.t6_surrogate_joint(dc["theta1_deg"], dc["theta1_deg"] + D,
                                  P._orientation_law("I1"))
        iso = P.t6_surrogate_joint(dc["theta1_deg"], dc["theta1_deg"] + D,
                                   P._orientation_law("I2"))
        rs = by[(D, 1, "I1", "surrogate")]
        tot = np.array([[r["nAA"], r["nAR"], r["nRA"], r["nRR"]] for r in rs], float)
        same_al = (tot[:, 0] + tot[:, 3]) / tot.sum(1)
        rs = by[(D, 1, "I2", "surrogate")]
        tot = np.array([[r["nAA"], r["nAR"], r["nRA"], r["nRR"]] for r in rs], float)
        same_iso = (tot[:, 0] + tot[:, 3]) / tot.sum(1)
        cf.append(dict(Delta=D,
                       aligned_closed_form=cosd(D) ** 2,
                       aligned_formula=al["P_same_formula"],
                       aligned_measured=float(same_al.mean()),
                       isotropic_closed_form=0.5 + 0.25 * cos2d(D),
                       isotropic_formula=iso["P_same_formula"],
                       isotropic_measured=float(same_iso.mean())))
        verdicts.append(a6.make_verdict(
            name=f"T6 aligned anchor closed form cos^2(Delta) | Delta={D}",
            predicted=cosd(D) ** 2, per_replicate_values=same_al, delta=delta,
            delta_basis=f"3/sqrt(N) = {delta:.7f} (declared, see AMBIGUITIES 5)",
            N=N, numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0,
            note="anchor a0 = phi0 = T_+ = theta_1, so E[tau1^2] = 1"))
        verdicts.append(a6.make_verdict(
            name=f"T6 isotropic anchor closed form 1/2 + cos(2Delta)/4 | Delta={D}",
            predicted=0.5 + 0.25 * cos2d(D), per_replicate_values=same_iso,
            delta=delta,
            delta_basis=f"3/sqrt(N) = {delta:.7f} (declared, see AMBIGUITIES 5)",
            N=N, numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0,
            note="anchor isotropic, so E[tau1^2] = 1/2 exactly"))
    extra["T6_closed_forms"] = cf
    return verdicts, raw, extra


# =========================================================================  T5
def run_t5(cfgmod, log=print):
    C = cfgmod.T5
    fx, dc = C["fixed"], C["declared"]
    N, nrep = dc["N"], dc["replicates"]
    delta = cfgmod.delta_t4(N)
    verdicts, raw, extra = [], [], {}
    pp, ps = P.t5_process_prediction(), P.t5_surrogate_prediction()
    store = {}
    for ac in dc["agent_classes"]:
        xs, ar, ra, cells = [], 0, 0, []
        cvals = set()
        for i in range(nrep):
            seed = derive_run_seed(cfgmod.MASTER_SEED, 5, dc["agent_classes"].index(ac), i)
            cfg = RunConfig(N=N, agent_class=ac, eps=dc["eps"], c_b=dc["c_b"],
                            c_h=dc["c_h"], alpha=dc["alpha"], beta=dc["beta"],
                            r=dc["r"], lam=dc["lam"], rho=dc["rho"],
                            kappa=dc["kappa"], f=dc["f"],
                            pulses=tuple(tuple(p) for p in fx["campaign"]),
                            initial_law=fx["initial_law"], t_end=dc["t_end"],
                            stop_on_extinction=False)
            o = run_one(cfg, seed)
            nAA, nAR, nRA, nRR = _counts4(o["pulse_out"])
            xs.append(float(o["s_final"].mean())); ar += nAR; ra += nRA
            cells.append([nAA, nAR, nRA, nRR])
            cvals |= set(np.unique(np.round(o["c_final"], 12)).tolist())
            raw.append(dict(test="T5", agent_class=ac, rep=i, seed=seed, N=N,
                            nAA=nAA, nAR=nAR, nRA=nRA, nRR=nRR, x=xs[-1]))
            log(f"  T5 {ac} rep={i} x={xs[-1]:+.6f} nAR={nAR} nRA={nRA}")
        cells = np.array(cells, float)
        store[ac] = dict(xs=np.array(xs), cells=cells, nAR=ar, nRA=ra,
                         c_values=sorted(cvals))
    for ac in ("process", "automaton"):
        st = store[ac]
        for nm, cnt in (("P(AR)", st["nAR"]), ("P(RA)", st["nRA"])):
            verdicts.append(a6.Verdict(
                name=f"T5 {nm} = 0 pathwise | {ac}",
                predicted=0.0, measured=float(cnt), diff=float(cnt),
                ci_lo=float(cnt), ci_hi=float(cnt), delta=0.0,
                delta_basis="A4a: P(AR)=P(RA)=0 pathwise; any violation is a FAIL",
                status=a6.PASS if cnt == 0 else a6.FAIL, n_replicates=nrep, N=N,
                replicates_needed=None, mc_error=0.0, finite_N_bias=0.0,
                numerical_error=0.0, closure_error=0.0,
                interval_kind="exact pathwise (violation count over all agents)",
                note=f"{nrep * N} agents"))
        verdicts.append(a6.make_verdict(
            name=f"T5 x = 0 | {ac}", predicted=0.0,
            per_replicate_values=st["xs"], delta=cfgmod.DELTA_X_ZERO_ABS,
            delta_basis=f"A4a absolute tolerance for x = 0: "
                        f"{cfgmod.DELTA_X_ZERO_ABS}",
            N=N, numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0,
            note=f"final convictions observed: {st['c_values']}"))
    st = store["surrogate"]
    tot = st["cells"].sum(0); tot = tot / tot.sum()
    for nm, idx, pred in (("P(AA)", 0, ps["P_AA"]), ("P(AR)", 1, ps["P_AR"]),
                          ("P(RA)", 2, ps["P_RA"]), ("P(RR)", 3, ps["P_RR"])):
        verdicts.append(a6.make_verdict(
            name=f"T5 surrogate registered contrast {nm}", predicted=pred,
            per_replicate_values=st["cells"][:, idx] / st["cells"].sum(1),
            delta=delta, delta_basis=f"3/sqrt(N) = {delta:.7f} (declared)",
            N=N, numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0))
    verdicts.append(a6.make_verdict(
        name="T5 surrogate registered contrast x = 1/4", predicted=ps["x"],
        per_replicate_values=st["xs"], delta=delta,
        delta_basis=f"3/sqrt(N) = {delta:.7f} (declared)",
        N=N, numerical_error=0.0, closure_error=0.0, finite_N_bias=0.0,
        note=f"final convictions observed: {st['c_values']}"))
    extra["process_prediction"] = pp
    extra["surrogate_prediction"] = ps
    extra["c_values"] = {k: v["c_values"] for k, v in store.items()}
    return verdicts, raw, extra
