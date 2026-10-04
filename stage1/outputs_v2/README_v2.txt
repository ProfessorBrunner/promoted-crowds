RETAINED RESULTS — archive version v2 (A6: "corrections are versioned and original
results retained").

Verdict: T1 PASS, T2 PASS, T3 PASS, T4 PASS, T5 PASS, T6 PASS — identical to v3.

v2 is superseded by v3 for one REPORTING defect only (bug B2 in ../BUGLOG.md): the
`note` field of rows "T1.2 cell {A,B}: first active interval >= L" labels 2550000 as
the number of activated-agent intervals, when 2550000 is the total number of agents
simulated across the N ladder; the number that ever activated is 2154164 (cell A) and
1922628 (cell B).  The verdict (zero violations), the measured value, the interval and
delta are unaffected, and every other row of v2 is identical to v3 -- the run is
deterministic from master seed 20261001, so v3 reproduces v2 numerically.
