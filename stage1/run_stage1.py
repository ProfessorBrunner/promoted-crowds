#!/usr/bin/env python
"""CROWD-1 Stage 1 driver: acceptance tests T1-T6 of design v0.3 section A2.

Usage:  python run_stage1.py [--serial]

Writes, under outputs/ :
    raw/t*.csv                per-run sufficient statistics (the raw outputs)
    certified_table.csv|.md   the certified table (A6 verdict per registered row)
    stage1_results.json       every prediction, measurement, interval and budget
    seeds.json                master seed and every derived per-run seed
    logs/run_log.txt          the run log

Stage 2 is NOT authorized: nothing in design section A4 (P1-P10) is run here.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from crowd1 import (tests as T, a6, __spec_version__, __design_version__,
                    __stage__, __archive_version__)
from crowd1.tests import _load_cfg

CFG_PATH = os.path.join(HERE, "config", "stage1_config.py")
OUT = os.path.join(HERE, "outputs")
RAW = os.path.join(OUT, "raw")
LOGS = os.path.join(OUT, "logs")

RANK = {a6.PASS: 0, a6.INCONCLUSIVE: 1, a6.FAIL: 2}


def main(serial=False):
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    logf = open(os.path.join(LOGS, "run_log.txt"), "w")

    def log(*a):
        msg = " ".join(str(x) for x in a)
        print(msg)
        logf.write(msg + "\n")
        logf.flush()

    cfg = _load_cfg(CFG_PATH)
    t0 = time.time()
    log(f"CROWD-1 Stage 1  started {datetime.now(timezone.utc).isoformat()}")
    log(f"  specification : {__spec_version__}")
    log(f"  design        : {__design_version__}")
    log(f"  scope         : {__stage__}")
    log(f"  master seed   : {cfg.MASTER_SEED}")

    pool = None
    if not serial:
        import multiprocessing as mp
        pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))

    all_v, all_raw, extras = [], [], {}
    for name, fn in (("T1", lambda: T.run_t1(cfg, log)),
                     ("T2", lambda: T.run_t2(cfg, log)),
                     ("T3", lambda: T.run_t3(cfg, log)),
                     ("T4_T6", lambda: T.run_t4_t6(cfg, CFG_PATH, pool, log)),
                     ("T5", lambda: T.run_t5(cfg, log))):
        log(f"\n=== {name} ===")
        ts = time.time()
        v, r, x = fn()
        extras[name] = x
        all_v += v
        all_raw += r
        worst = max((RANK[z.status] for z in v), default=0)
        log(f"  {name}: {len(v)} registered rows, worst verdict "
            f"{[k for k, q in RANK.items() if q == worst][0]}, "
            f"{time.time() - ts:.1f}s")
    if pool:
        pool.close(); pool.join()

    # ---------------------------------------------------------------- outputs
    import csv
    rows = [v.row() for v in all_v]
    fields = list(rows[0].keys())
    with open(os.path.join(OUT, "certified_table.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # raw outputs, one csv per test group
    groups = {}
    for r in all_raw:
        groups.setdefault(r["test"], []).append(r)
    for g, rs in groups.items():
        keys = sorted({k for r in rs for k in r})
        with open(os.path.join(RAW, f"{g.lower()}.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            for r in rs:
                w.writerow({k: r.get(k, "") for k in keys})

    seeds = {"master_seed": cfg.MASTER_SEED,
             "derivation": "derive_run_seed(MASTER_SEED, test_id, cell_id, ...) "
                           "then six xoshiro256++ streams per run (see crowd1/rng.py)",
             "stream_ids": {"0": "clocks", "1": "recipient", "2": "coin",
                            "3": "cohort", "4": "initial_law", "5": "exogenous"},
             "per_run": sorted({int(r["seed"]) for r in all_raw if "seed" in r})}
    with open(os.path.join(OUT, "seeds.json"), "w") as fh:
        json.dump(seeds, fh, indent=1)

    import re
    summary = {}
    for v in all_v:
        key = re.match(r"T\d", v.name).group(0)
        summary.setdefault(key, []).append(v.status)
    summary = {k: [q for q, z in RANK.items() if z == max(RANK[s] for s in vs)][0]
               for k, vs in summary.items()}

    res = dict(
        meta=dict(spec_version=__spec_version__, design_version=__design_version__,
                  archive_version=__archive_version__,
                  scope=__stage__, master_seed=cfg.MASTER_SEED,
                  started_utc=datetime.now(timezone.utc).isoformat(),
                  wall_seconds=time.time() - t0,
                  python=sys.version.split()[0], platform=platform.platform(),
                  numpy=np.__version__),
        config={k: getattr(cfg, k) for k in ("MASTER_SEED", "T1", "T2", "T3",
                                             "T4", "T5", "DELTA_TRAJECTORY_FRAC",
                                             "DELTA_OPERATOR_FRAC",
                                             "DELTA_X_ZERO_ABS")},
        summary=summary,
        certified_table=rows,
        reported_diagnostics=extras,
    )
    with open(os.path.join(OUT, "stage1_results.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)

    write_markdown_table(os.path.join(OUT, "certified_table.md"), rows, summary,
                         extras, cfg)
    log(f"\nSUMMARY: {summary}")
    log(f"total wall {time.time() - t0:.1f}s")
    logf.close()
    return res


def _fmt(x, nd=6):
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    ax = abs(x)
    if x == 0:
        return "0"
    if ax < 1e-4 or ax >= 1e6:
        return f"{x:.3e}"
    return f"{x:.{nd}f}"


def write_markdown_table(path, rows, summary, extras, cfg):
    with open(path, "w") as fh:
        fh.write("# CROWD-1 Stage 1 — certified table (acceptance tests T1–T6)\n\n")
        fh.write(f"Specification: `{__spec_version__}`  \n")
        fh.write(f"Design: `{__design_version__}`  \n")
        fh.write(f"Scope: {__stage__}  \n")
        fh.write(f"Archive version: {__archive_version__}  \n")
        fh.write(f"Master seed: `{cfg.MASTER_SEED}`  \n")
        fh.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        fh.write("## Per-test verdict\n\n")
        fh.write("| test | verdict |\n|---|---|\n")
        for k in sorted(summary):
            fh.write(f"| {k} | **{summary[k]}** |\n")
        fh.write("\n## Registered rows\n\n")
        fh.write("Discrepancy d = simulation − prediction; the interval is the "
                 "two-sided 95% interval for d. PASS when the interval lies "
                 "inside [−δ, δ] (A6).\n\n")
        fh.write("| row | predicted | measured | d | 95% CI for d | δ | verdict "
                 "| N | reps | MC err | finite-N bias | num err | closure err |\n")
        fh.write("|---|--:|--:|--:|:--:|--:|:--:|--:|--:|--:|--:|--:|--:|\n")
        for r in rows:
            fh.write(
                f"| {r['name']} | {_fmt(r['predicted'])} | {_fmt(r['measured'])} "
                f"| {_fmt(r['diff'])} | [{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}] "
                f"| {_fmt(r['delta'])} | **{r['status']}** | {r['N']} "
                f"| {r['n_replicates']} | {_fmt(r['mc_error'])} "
                f"| {_fmt(r['finite_N_bias'])} | {_fmt(r['numerical_error'])} "
                f"| {_fmt(r['closure_error'])} |\n")
        fh.write("\n## Reported diagnostics (not acceptance conditions)\n\n")
        g = extras.get("T3", {})
        if "T3a_gof" in g:
            d = g["T3a_gof"]
            fh.write(f"**T3(a) goodness of fit of the counter law** to "
                     f"1 + Poisson({d['Lambda']:.9f}): chi-square "
                     f"{d['chi2']:.3f} on {d['dof']} dof, p = {d['p_value']:.4f}, "
                     f"total variation {d['total_variation']:.3e} over "
                     f"{d['n_pooled']} agents.\n\n")
        if "T3c_convergence" in g:
            fh.write("**T3(c) full-system formula 1 + Poisson(λ∫A_j) — "
                     "convergence check across the N ladder.** "
                     f"{g['T3c_status']}\n\n")
            fh.write("| N | mean counter−1 | λ∫A | mean − λ∫A | var counter−1 "
                     "| var − λ∫A | χ²/dof |\n|--:|--:|--:|--:|--:|--:|--:|\n")
            for c in g["T3c_convergence"]:
                fh.write(f"| {c['N']} | {c['mean_k']:.5f} | "
                         f"{c['mean_lam_intA']:.5f} | {c['mean_minus_pred']:+.5f} "
                         f"| {c['var_k']:.5f} | {c['var_minus_pred']:+.5f} "
                         f"| {c['chi2_per_dof']:.3f} |\n")
            fh.write("\n")
        g4 = extras.get("T4_T6", {})
        if "automaton_equivalence_pathwise" in g4:
            d = g4["automaton_equivalence_pathwise"]
            fh.write("**A5 positive equivalence control (pathwise).** Process and "
                     "automaton run on a shared seed over "
                     f"{d['cells']} (Δ, order, initial law) cells, "
                     f"{d['agents_compared']} agents compared; disagreements "
                     f"{d['differences']}.\n\n")
        if "automaton_equivalence_independent_seeds" in g4:
            d = g4["automaton_equivalence_independent_seeds"]
            fh.write("**A5 control, independent-seed diagnostic (no verdict).** "
                     "Maximum total-variation distance between the two arms "
                     f"{d['max_total_variation']:.3e} at 2e6 agents per arm; "
                     f"minimum chi-square p-value {d['min_p_value']:.4f} over 30 "
                     "cells.\n\n")
        if "T6_closed_forms" in g4:
            fh.write("**T6 closed forms.** Aligned anchor → cos²Δ; isotropic "
                     "anchor → ½ + ¼cos2Δ.\n\n")
            fh.write("| Δ | cos²Δ | aligned measured | ½+¼cos2Δ "
                     "| isotropic measured |\n|--:|--:|--:|--:|--:|\n")
            for c in g4["T6_closed_forms"]:
                fh.write(f"| {c['Delta']}° | {c['aligned_closed_form']:.9f} "
                         f"| {c['aligned_measured']:.9f} "
                         f"| {c['isotropic_closed_form']:.9f} "
                         f"| {c['isotropic_measured']:.9f} |\n")
            fh.write("\n")
        for tk in ("T1", "T2"):
            e = extras.get(tk, {})
            lad = e.get("ladder") or e.get("T1_cell_A", {}).get("ladder")
            if lad and "ladder" in lad:
                fh.write(f"**{tk} N ladder** (A6 error source 2): "
                         + ", ".join(f"N={n}: {v:.6f}" for n, v in lad["ladder"])
                         + (f"; 1/N extrapolation {lad['extrapolated_Ninf']:.6f}"
                            if "extrapolated_Ninf" in lad else "") + "\n\n")


if __name__ == "__main__":
    main(serial="--serial" in sys.argv)
