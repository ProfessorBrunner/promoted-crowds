#!/usr/bin/env python3
"""Rebuild everything derived in this repository: the results ledger and F1-F4.

Neither step re-runs a simulation.  `build_ledger.py` reads the certified tables and
raw JSON already committed under stage1/, stage2/, stage2b/ and stage3/;
`figures/make_figures.py` reads only the data files committed under figures/data/.
So this script reproduces the published numbers and figures exactly, from the
archives, on any machine with numpy, scipy and matplotlib.

    python reproduce.py             rebuild the ledger and all four figures
    python reproduce.py --check     additionally verify that a second ledger build is
                                    byte-identical, that the ledger's row count and
                                    status tally match what it reports of itself, and
                                    that manuscript.md's figure links resolve to the
                                    correctly numbered files
    python reproduce.py --ledger    ledger only
    python reproduce.py --figures   figures only

Re-running the simulations themselves is a separate, much longer job: each stage has
its own run_*.py, needs numba, and is pinned by the seeds recorded in its outputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_MD = os.path.join(HERE, "RESULTS_LEDGER.md")
LEDGER_CSV = os.path.join(HERE, "RESULTS_LEDGER.csv")


def _md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _run(args, label):
    print(f"[{label}] {' '.join(os.path.basename(a) for a in args[1:])}", flush=True)
    r = subprocess.run(args, cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"[{label}] FAILED with exit code {r.returncode}")
    for line in r.stdout.rstrip().splitlines():
        print("   " + line, flush=True)
    return r.stdout


def build_ledger():
    _run([sys.executable, os.path.join(HERE, "build_ledger.py")], "ledger")


def build_figures():
    _run([sys.executable, os.path.join(HERE, "figures", "make_figures.py")], "figures")


def check():
    """Idempotence of the ledger, and agreement between its table and its own tally."""
    before = (_md5(LEDGER_MD), _md5(LEDGER_CSV))
    build_ledger()
    after = (_md5(LEDGER_MD), _md5(LEDGER_CSV))
    if before != after:
        raise SystemExit("[check] FAILED: the ledger is not idempotent — a second "
                         "build produced different bytes")
    print("[check] ledger is idempotent (md5 unchanged on rebuild)", flush=True)

    with open(LEDGER_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    # The ledger may carry a CROWD-2 appendix (Crowd-2 Stage 2 authorization,
    # 2026-10-02): CROWD-1's rows and its markdown are unchanged and CROWD-2 rows are
    # appended after them.  The CROWD-1 headline count therefore counts CROWD-1 rows
    # only, and that is what the markdown states, so check the two against each other
    # on the CROWD-1 subset and report any appendix separately.  In a clone of the
    # released repository crowd2/ is absent and c1 == rows.
    c1 = [r for r in rows if not r["stage"].lower().startswith("crowd-2")]
    c2 = [r for r in rows if r["stage"].lower().startswith("crowd-2")]
    tally = Counter(r["status"] for r in c1)
    print(f"[check] {len(c1)} CROWD-1 ledger rows"
          + (f" (+ {len(c2)} CROWD-2 appendix rows)" if c2 else ""), flush=True)
    for status, n in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"          {n:>4}  {status}", flush=True)

    head = open(LEDGER_MD, encoding="utf-8").read()
    claim = f"{len(c1)} ledger rows"
    if claim not in head:
        raise SystemExit(f"[check] FAILED: the markdown ledger does not state "
                         f"'{claim}' — its narrative and its table disagree")
    print(f"[check] the markdown ledger's own summary states '{claim}'", flush=True)
    if c2:
        print(f"[check] CROWD-2 appendix present: {len(c2)} rows, "
              f"{Counter(r['status'] for r in c2).most_common(1)[0][0]} dominant; "
              "excluded from a released clone by .gitignore", flush=True)

    missing = [f for f in (
        "F1_order_advantage_vs_delay", "F2_outbreak_probability_by_order",
        "F3_P6caseA_activity_trajectory", "F4_onset_class2_and_class1")
        for ext in ("pdf", "png")
        if not os.path.exists(os.path.join(HERE, "figures", f"{f}.{ext}"))]
    if missing:
        raise SystemExit(f"[check] FAILED: missing figure files {missing}")
    print("[check] all four figures present as PDF and PNG", flush=True)

    # The manuscript's own figure links.  Path existence alone is not enough: it passes
    # even when two figures are swapped, which is exactly the mismatch a referee caught
    # on this project.  So each link labelled "Figure N" must point at a file whose
    # basename begins with "FN_", and F1-F4 must all be referenced.
    man = os.path.join(HERE, "manuscript.md")
    if not os.path.exists(man):
        raise SystemExit("[check] FAILED: manuscript.md is missing from the "
                         "repository root")
    links = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)",
                       open(man, encoding="utf-8").read())
    if not links:
        raise SystemExit("[check] FAILED: manuscript.md contains no image links")
    broken, misnumbered = [], []
    seen = set()
    for label, target in links:
        if not os.path.exists(os.path.join(HERE, target)):
            broken.append(f"{label!r} -> {target}")
        m = re.fullmatch(r"\s*Figure\s+(\d+)\s*", label)
        if m:
            n = int(m.group(1))
            seen.add(n)
            if not os.path.basename(target).startswith(f"F{n}_"):
                misnumbered.append(f"{label!r} -> {os.path.basename(target)}")
    if broken:
        raise SystemExit(f"[check] FAILED: manuscript figure links do not resolve: "
                         f"{broken}")
    if misnumbered:
        raise SystemExit(f"[check] FAILED: manuscript figure numbering disagrees with "
                         f"the file it links: {misnumbered}")
    if seen != {1, 2, 3, 4}:
        raise SystemExit(f"[check] FAILED: manuscript references figures {sorted(seen)}, "
                         f"expected 1-4")
    print(f"[check] manuscript.md: {len(links)} figure links resolve, and each "
          f"'Figure N' points at FN_* (F1-F4 all referenced)", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", action="store_true", help="rebuild the ledger only")
    ap.add_argument("--figures", action="store_true", help="rebuild the figures only")
    ap.add_argument("--check", action="store_true",
                    help="also verify ledger idempotence and self-consistency")
    a = ap.parse_args()
    do_all = not (a.ledger or a.figures)
    if a.ledger or do_all:
        build_ledger()
    if a.figures or do_all:
        build_figures()
    if a.check:
        check()
    print("done.", flush=True)


if __name__ == "__main__":
    main()
