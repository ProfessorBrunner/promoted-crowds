"""Matched-h floor test for the P6 references.

Changing c_min changes U = -log c_min and hence J = round(U/h) and the adjusted
h = U/J, so a naive floor comparison at one REQUESTED h compares two slightly
different ACTUAL h.  For case A that confound is the same size as the floor effect
itself.  Choosing c_min = 1e-2 and 1e-4 makes U2/U1 exactly 2, so J2 = 2*J1 and the
adjusted h is IDENTICAL -- the remaining difference is purely the floor.
"""
import json, os, sys
sys.argv = ["x"]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "floor_audit.py")).read().split('if __name__')[0])

if __name__ == "__main__":
    out = {}
    for tag, cfg, hreq in (("P6A", P6A, 0.01), ("P6B", P6B, 0.0025)):
        rows = []
        for c_min in (1e-2, 1e-4):
            # request the FIRST run's adjusted h for the second floor, so that
            # J2 = round(U2/h1) = 2*J1 exactly and the adjusted h is identical
            hq = hreq if not rows else rows[0]["h"]
            r = p6_point(cfg, hq, c_min)
            rows.append(r)
            print(f"  [{tag}] c_min={c_min:.0e}  h_actual={r['h']:.9f}  J={r['J']}  "
                  f"t_cross={r['t_cross']:.6f}  Lambda={r['Lambda']:.6f}", flush=True)
        assert abs(rows[0]["h"] - rows[1]["h"]) < 1e-15, "h not matched"
        d = {k: rows[1][k] - rows[0][k] for k in ("t_cross", "Lambda")}
        print(f"  [{tag}] MATCHED-h floor effect 1e-2 -> 1e-4: "
              f"t_cross {d['t_cross']:+.3e}  Lambda {d['Lambda']:+.3e}", flush=True)
        out[tag] = dict(h_requested=hreq, h_actual=rows[0]["h"], rows=rows,
                        matched_floor_effect=d)
    fp = os.path.join(OUT, "floor_audit.json")
    res = json.load(open(fp)); res["matched_h_floor_test"] = out
    json.dump(res, open(fp, "w"), indent=2)
    print("wrote", fp, flush=True)
