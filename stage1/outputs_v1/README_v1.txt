RETAINED ORIGINAL RESULTS — archive version v1 (A6: "corrections are versioned and
original results retained").

Run of 2026-10-01, master seed 20261001.  Verdict: T1 PASS, T2 PASS, T3 PASS,
T4 FAIL, T5 PASS, T6 PASS.

The single FAIL is row
    "T4 A5 control: automaton reproduces the process joint law"
and it is a HARNESS BUG (bug B1 in ../BUGLOG.md), not a simulator bug, not an
algebraic error in a design prediction, and not a model failure:

  * the row declared a ZERO tolerance on a Monte-Carlo-ESTIMATED total-variation
    distance, which no finite sample can satisfy; and
  * the two arms compared (agent_class = "process" and agent_class = "automaton")
    were run with DIFFERENT derived seeds, so they are two independent samples of
    the same law rather than the pathwise comparison the row's name claims.

The A5 prediction itself is corroborated by this very run: over the 30
(Delta, order, initial law) cells the two arms give total-variation distances of
9.40e-05 to 1.36e-03 at 2e6 agents per arm (sampling scale 5.6e-04) and 30
chi-square p-values uniformly spread over [0.023, 0.962].

Every other row of this run is unchanged in v2.  No parameter, prediction or
tolerance of the design was altered; the correction replaces a mis-declared test
criterion of this harness with the pathwise criterion the control actually asserts.
