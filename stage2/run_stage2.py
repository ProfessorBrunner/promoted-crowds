#!/usr/bin/env python
"""CROWD-1 Stage 2 driver: A4 items P1, P1-delay, P2, P2-delay, P3, P4, P6.

Usage:  python run_stage2.py [--serial] [--only P1,P4,...]

Stage 3 is NOT authorized: no item of A4 outside the list above is run, and no
market layer exists anywhere in this archive.
"""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from crowd1 import a6, tests_s2 as T2, predictions_s2 as PS
from crowd1 import __spec_version__, __design_version__, __stage__, __archive_version__
from crowd1.rng import derive_run_seed

CFG_PATH = os.path.join(HERE, "config", "stage2_config.py")
OUT = os.path.join(HERE, "outputs")
RAW = os.path.join(OUT, "raw")
LOGS = os.path.join(OUT, "logs")
RANK = {a6.PASS: 0, a6.INCONCLUSIVE: 1, a6.FAIL: 2}


# ------------------------------------------------------------------ Holm (A6)
def equivalence_p(diff, se, delta, dof):
    """p-value for the composite null |d| <= delta, with a Student-t pivot."""
    if se <= 0:
        return 1.0 if abs(diff) <= delta else 0.0
    hi = stats.t.sf((diff - delta) / se, dof)
    lo = stats.t.cdf((diff + delta) / se, dof)
    return float(min(1.0, 2.0 * min(hi, lo)))


def holm(pvals, alpha=0.05):
    """Holm step-down.  Returns adjusted p-values in the input order."""
    idx = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(idx):
        val = (m - rank) * pvals[i]
        run = max(run, val)
        adj[i] = min(1.0, run)
    return adj


def verdict_p(v):
    dof = max(v.n_replicates - 1, 1)
    se = v.mc_error / stats.t.ppf(0.975, dof) if v.mc_error > 0 else 0.0
    return equivalence_p(v.diff, se, v.delta, dof)


def main(serial=False, only=None):
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    logf = open(os.path.join(LOGS, "run_log.txt"), "w")

    def log(*a):
        m = " ".join(str(x) for x in a)
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()

    cfg = T2.load_cfg(CFG_PATH)
    t0 = time.time()
    log(f"CROWD-1 Stage 2  {datetime.now(timezone.utc).isoformat()}")
    log(f"  specification : {__spec_version__}")
    log(f"  design        : {__design_version__}")
    log(f"  scope         : {__stage__}")
    log(f"  archive       : {__archive_version__}")
    log(f"  master seed   : {cfg.MASTER_SEED}")

    pool = None
    if not serial:
        import multiprocessing as mp
        pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    mapper = (lambda fn, jobs: list(pool.map(fn, jobs))) if pool else \
             (lambda fn, jobs: [fn(j) for j in jobs])

    # ---------------------------------------------------------------- SEALING
    seal = seal_predictions(cfg)
    with open(os.path.join(OUT, "sealed_predictions.json"), "w") as fh:
        json.dump(seal, fh, indent=1, default=str)
    log(f"\nSEALED before any run -> outputs/sealed_predictions.json")
    for k, v in seal["P1_held_out"].items():
        log(f"  held-out {k}: x = {v['x']:.9f}, R/lambda = {v['R_over_lambda']:.9f}")

    import stage2_items as SI
    SI.LOG = log
    SI.CFG_PATH = CFG_PATH
    SI.MAPPER = mapper

    todo = only or ["P1", "P1-delay", "P2", "P2-delay", "P3", "P4", "P6"]
    all_v, all_raw, extras = [], [], {}
    for name in todo:
        log(f"\n=== {name} ===")
        ts = time.time()
        v, r, x = SI.RUNNERS[name](cfg)
        extras[name] = x
        all_v += v
        all_raw += r
        worst = max((RANK[z.status] for z in v), default=0)
        log(f"  {name}: {len(v)} rows, worst {[k for k,q in RANK.items() if q==worst][0]}"
            f", {time.time()-ts:.1f}s")
    if pool:
        pool.close(); pool.join()

    # -------------------------------------------------------- Holm correction
    rows = [v.row() for v in all_v]
    for r, v in zip(rows, all_v):
        r["endpoint"] = v.name.split("|")[0].strip().split()[0]
        r["p_equivalence"] = verdict_p(v)
    prim = cfg.PRIMARY_ENDPOINTS
    ep_p, ep_names = [], []
    for e in prim:
        ps = [r["p_equivalence"] for r in rows
              if r["endpoint"] == e and r["delta"] > 0]
        ep_names.append(e)
        ep_p.append(min(ps) if ps else 1.0)
    adj = holm(np.array(ep_p))
    holm_tbl = [dict(endpoint=e, raw_p=float(p), holm_adjusted_p=float(a),
                     rejects_null_at_0_05=bool(a < 0.05))
                for e, p, a in zip(ep_names, ep_p, adj)]
    for r in rows:
        m = {h["endpoint"]: h for h in holm_tbl}
        r["holm_adjusted_p_endpoint"] = (m[r["endpoint"]]["holm_adjusted_p"]
                                         if r["endpoint"] in m else None)

    # ----------------------------------------------------------------- output
    fields = list(rows[0].keys())
    with open(os.path.join(OUT, "certified_table.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    groups = {}
    for r in all_raw:
        groups.setdefault(r["test"], []).append(r)
    for g, rs in groups.items():
        keys = sorted({k for r in rs for k in r})
        with open(os.path.join(RAW, f"{g.lower().replace('-','_')}.csv"), "w",
                  newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
            for r in rs:
                w.writerow({k: r.get(k, "") for k in keys})

    summary = {}
    for v in all_v:
        e = v.name.split("|")[0].strip().split()[0]
        summary.setdefault(e, []).append(v.status)
    summary = {k: [q for q, z in RANK.items() if z == max(RANK[s] for s in vs)][0]
               for k, vs in summary.items()}

    res = dict(
        meta=dict(spec_version=__spec_version__, design_version=__design_version__,
                  archive_version=__archive_version__, scope=__stage__,
                  master_seed=cfg.MASTER_SEED,
                  finished_utc=datetime.now(timezone.utc).isoformat(),
                  wall_seconds=time.time() - t0, python=sys.version.split()[0],
                  platform=platform.platform(), numpy=np.__version__),
        summary=summary, holm=holm_tbl, sealed=seal,
        certified_table=rows, reported_diagnostics=extras)
    with open(os.path.join(OUT, "stage2_results.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=_jsonable)
    with open(os.path.join(OUT, "seeds.json"), "w") as fh:
        json.dump({"master_seed": cfg.MASTER_SEED,
                   "derivation": "derive_run_seed(MASTER_SEED, item, ...) then six "
                                 "xoshiro256++ streams per run (crowd1/rng.py)",
                   "per_run": sorted({int(r["seed"]) for r in all_raw
                                      if isinstance(r.get("seed"), (int, np.integer))})},
                  fh, indent=1)
    write_markdown(os.path.join(OUT, "certified_table.md"), rows, summary,
                   holm_tbl, extras, seal, cfg)
    log(f"\nSUMMARY: {summary}")
    log("HOLM (primary endpoints): " +
        ", ".join(f"{h['endpoint']}={h['holm_adjusted_p']:.3g}" for h in holm_tbl))
    log(f"total wall {time.time()-t0:.1f}s")
    logf.close()
    return res


def _jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return str(o)


def seal_predictions(cfg):
    """Every reference number, computed and written out BEFORE any run."""
    out = {"note": "computed from the appendix constructions before the runs; "
                   "the P1 held-out stance law is sealed here as A4 requires"}
    rep = {}
    for o in cfg.P1["fixed"]["orders"]:
        e = PS.p_plus_campaign(o)
        rep[str(o)] = dict(x=e["x"], R_over_lambda=PS.p1_R_over_lambda(e["x"]),
                           registered_x=cfg.P1["fixed"]["x_pred"][o],
                           registered_R=cfg.P1["fixed"]["R_over_lambda_pred"][o])
    out["P1_registered_reproduction"] = rep
    ho = {}
    for o in cfg.P1["fixed"]["held_out_orders"]:
        e = PS.p_plus_campaign(o)
        ho[str(o)] = dict(x=e["x"], R_over_lambda=PS.p1_R_over_lambda(e["x"]),
                          final_c_law={str(k): v for k, v in e["final_c_law"].items()})
    out["P1_held_out"] = ho
    out["P2_reproduction"] = {str(o): PS.p2_qT_and_R(o)
                              for o in cfg.P2["fixed"]["orders"]}
    out["P2_I2"] = PS.p2_qT_I2()
    out["P3_reproduction"] = {str(o): PS.p3_reference(o)
                              for o in cfg.P3["fixed"]["orders"]}
    lc = PS.p4_lambda_c(); fold = PS.p4_fold()
    br = {lam: PS.p4_branches(lam) for lam in (1.40, 1.60, 1.75, 1.90)}
    out["P4_reproduction"] = dict(
        lambda_c_computed=lc["lambda_c"], lambda_c_registered=cfg.P4["fixed"]["lambda_c"],
        lambda_fold_computed=fold["lambda_fold"],
        lambda_fold_registered=cfg.P4["fixed"]["lambda_fold"],
        A_fold_computed=fold["A_fold"],
        branches={str(k): dict(A_u=v.get("A_u"), A_star=v.get("A_star"),
                               criterion_1p5_A_u=(None if v.get("A_u") is None
                                                  else 1.5 * v["A_u"]))
                  for k, v in br.items()},
        A_star_registered={str(k): v for k, v in cfg.P4["fixed"]["A_star"].items()})
    out["P6_registered"] = {k: {kk: vv for kk, vv in v.items()}
                            for k, v in cfg.P6["fixed"].items()
                            if k in ("A", "B")}
    return out


def _fmt(x, nd=6):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    if isinstance(x, str):
        return x
    if isinstance(x, (bool, np.bool_)):
        return str(bool(x))
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    ax = abs(x)
    if x == 0:
        return "0"
    if ax < 1e-4 or ax >= 1e6:
        return f"{x:.3e}"
    return f"{x:.{nd}f}"


def write_markdown(path, rows, summary, holm_tbl, extras, seal, cfg):
    with open(path, "w") as fh:
        fh.write("# CROWD-1 Stage 2 — certified table (A4: P1, P1-delay, P2, "
                 "P2-delay, P3, P4, P6)\n\n")
        fh.write(f"Specification: `{__spec_version__}`  \n")
        fh.write(f"Design: `{__design_version__}`  \n")
        fh.write(f"Scope: {__stage__}  \n")
        fh.write(f"Archive version: {__archive_version__}  \n")
        fh.write(f"Master seed: `{cfg.MASTER_SEED}`  \n")
        fh.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        fh.write("## Per-item verdict\n\n| item | primary? | verdict |\n|---|:--:|---|\n")
        for k in sorted(summary):
            p = "yes" if k in cfg.PRIMARY_ENDPOINTS else "no"
            fh.write(f"| {k} | {p} | **{summary[k]}** |\n")
        fh.write("\n## Holm correction across the A6 primary endpoints\n\n")
        fh.write("A6: *\"a Holm correction across primary endpoints\"*. Each endpoint's "
                 "p-value is the smallest, over that endpoint's registered rows, of the "
                 "p-value for the composite null |d| ≤ δ (Student-t pivot). A row-level "
                 "FAIL and a Holm rejection are different statements and both are given."
                 "\n\n| endpoint | raw p | Holm-adjusted p | rejects |d| ≤ δ at 0.05 |\n")
        fh.write("|---|--:|--:|:--:|\n")
        for h in holm_tbl:
            fh.write(f"| {h['endpoint']} | {h['raw_p']:.4g} | "
                     f"{h['holm_adjusted_p']:.4g} | "
                     f"{'**yes**' if h['rejects_null_at_0_05'] else 'no'} |\n")
        fh.write("\n## Registered rows\n\n")
        fh.write("d = simulation − prediction; the interval is the two-sided 95% "
                 "interval for d. PASS when it lies inside [−δ, δ] (A6).\n\n")
        fh.write("| row | predicted | measured | d | 95% CI for d | δ | verdict | N "
                 "| reps | MC err | finite-N bias | num err | closure err |\n")
        fh.write("|---|--:|--:|--:|:--:|--:|:--:|--:|--:|--:|--:|--:|--:|\n")
        for r in rows:
            fh.write(f"| {r['name']} | {_fmt(r['predicted'])} | {_fmt(r['measured'])} "
                     f"| {_fmt(r['diff'])} | [{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}] "
                     f"| {_fmt(r['delta'])} | **{r['status']}** | {r['N']} "
                     f"| {r['n_replicates']} | {_fmt(r['mc_error'])} "
                     f"| {_fmt(r['finite_N_bias'])} | {_fmt(r['numerical_error'])} "
                     f"| {_fmt(r['closure_error'])} |\n")
        fh.write("\n## Reported diagnostics (not acceptance conditions)\n\n")
        for k in ("P1", "P1-delay", "P2", "P2-delay", "P3", "P4", "P6"):
            e = extras.get(k)
            if not e:
                continue
            fh.write(f"### {k}\n\n")
            for kk, vv in e.items():
                if isinstance(vv, str):
                    fh.write(f"- **{kk}**: {vv}\n")
                elif isinstance(vv, list) and vv and isinstance(vv[0], dict):
                    cols = list(vv[0].keys())
                    fh.write("\n| " + " | ".join(cols) + " |\n|" +
                             "---|" * len(cols) + "\n")
                    for row in vv:
                        fh.write("| " + " | ".join(_fmt(row[c]) for c in cols) + " |\n")
                    fh.write("\n")
                else:
                    fh.write(f"- **{kk}**: {_fmt(vv) if not isinstance(vv, dict) else json.dumps(vv, default=_jsonable)}\n")
            fh.write("\n")


if __name__ == "__main__":
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only"):
            only = a.split("=", 1)[1].split(",")
    main(serial="--serial" in sys.argv, only=only)
