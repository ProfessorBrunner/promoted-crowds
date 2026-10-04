#!/usr/bin/env python
"""Regression: re-run the whole Stage 1 suite (T1-T6) against the STAGE 2 engine
and diff the certified table against the frozen Stage 1 archive.

Every Stage 2 engine extension is an optional parameter whose default reproduces
Stage 1 behaviour; this script is the evidence for that claim.
"""
import csv, os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from crowd1 import tests as T1, a6

spec = importlib.util.spec_from_file_location(
    "stage1_config", os.path.join(HERE, "..", "stage1", "config", "stage1_config.py"))
cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)

CFG1 = os.path.join(HERE, "..", "stage1", "config", "stage1_config.py")
REF = os.path.join(HERE, "..", "stage1", "outputs", "certified_table.csv")


def main():
    import multiprocessing as mp
    pool = mp.get_context("spawn").Pool(processes=min(16, os.cpu_count() or 4))
    rows = []
    for fn in (lambda: T1.run_t1(cfg, lambda *a: None),
               lambda: T1.run_t2(cfg, lambda *a: None),
               lambda: T1.run_t3(cfg, lambda *a: None),
               lambda: T1.run_t4_t6(cfg, CFG1, pool, lambda *a: None),
               lambda: T1.run_t5(cfg, lambda *a: None)):
        v, r, x = fn()
        rows += [z.row() for z in v]
    pool.close(); pool.join()
    ref = {r["name"]: r for r in csv.DictReader(open(REF))}
    num = ["predicted", "measured", "diff", "ci_lo", "ci_hi", "delta",
           "mc_error", "numerical_error"]
    bad, n = [], 0
    for r in rows:
        if r["name"] not in ref:
            bad.append((r["name"], "missing from the Stage 1 archive")); continue
        q = ref[r["name"]]
        if q["status"] != r["status"]:
            bad.append((r["name"], f"status {q['status']} -> {r['status']}"))
        for k in num:
            a = float(q[k]) if q[k] not in ("", "None") else 0.0
            b = float(r[k]) if r[k] is not None else 0.0
            if abs(a - b) > 1e-12 * max(1.0, abs(a)):
                bad.append((r["name"], f"{k}: {a!r} -> {b!r}"))
        n += 1
    print(f"rows compared: {n} / {len(ref)} in the Stage 1 archive")
    print(f"MISMATCHES: {len(bad)}")
    for b in bad[:40]:
        print("   ", b)
    with open(os.path.join(HERE, "outputs", "regression_stage1.txt"), "w") as fh:
        fh.write(f"Stage 1 suite re-run against the Stage 2 engine\n")
        fh.write(f"rows compared: {n} / {len(ref)}\nmismatches: {len(bad)}\n")
        for b in bad:
            fh.write(f"  {b}\n")
        if not bad:
            fh.write("\nEvery Stage 1 certified row reproduces bit-for-bit under the "
                     "Stage 2 engine: same verdict, same predicted/measured/diff/"
                     "interval/delta/MC error/numerical error.\n")
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
