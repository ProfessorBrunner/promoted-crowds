"""Stage 3 P8 — censored supplement: the reported table.

P8 registers no numerical prediction ("Predicted: extinction almost surely with a
median that grows steeply in N; no scaling law is registered"), so there is no A6
verdict row.  What is registered is the REPORTING RULE, and that is what this file
applies: right-censor at T_max and report "median > T_max" wherever fewer than half
the runs extinguish.  No median is ever formed from observed extinctions alone.
"""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "config"))
import p8_config as CFG
FX, DC = CFG.P8["fixed"], CFG.P8["declared"]
RW = json.load(open(os.path.join(HERE, "outputs", "raw", "p8_raw.json")))
rows = []
for c in RW["cells"]:
    rows.append(dict(
        N=c["N"], replicates=c["replicates"], n_extinct=c["n_extinct"],
        n_censored=c["n_censored"], fraction_extinct=c["fraction_extinct"],
        median_extinction_time=c["median_report"],
        km_survival_at_T_max=1.0 - c["fraction_extinct"],
        mean_A_over_run=c["mean_A_over_run"],
        A_star=DC["A_star"],
        depression_below_A_star=DC["A_star"] - c["mean_A_over_run"],
        status="REPORTED (no registered number; no verdict)"))
out = dict(T_max=FX["T_max"], lam=FX["lam"], f=FX["f"],
           replicates=FX["replicates"], A_star=DC["A_star"], rows=rows,
           total_runs=sum(r["replicates"] for r in rows),
           total_extinctions=sum(r["n_extinct"] for r in rows),
           reporting_rule=("owner 2026-10-01: right-censored at T_max = 2000; if "
                           "fewer than half the runs extinguish, report "
                           "'median > T_max'; no median from observed extinctions "
                           "alone"))
json.dump(out, open(os.path.join(HERE, "outputs", "p8_results.json"), "w"),
          indent=2, default=float)
with open(os.path.join(HERE, "outputs", "reported_table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"N={r['N']:<5} extinct {r['n_extinct']}/{r['replicates']}  "
          f"censored {r['n_censored']}  median: {r['median_extinction_time']}  "
          f"mean A {r['mean_A_over_run']:.6f} (A* - A = {r['depression_below_A_star']:.6f})")
print(f"\ntotal: {out['total_extinctions']} extinctions in {out['total_runs']} runs")
