# CROWD-1 Stage 2 — ambiguities encountered

Specification: `review_packet_v0_6_1.md`, memo section **PROCESS SPECIFICATION v0.6**
Design: `crowd1_cs_design_and_manuscript_brief_v0_3.md`, **Part A** (v0.3)
Scope: Stage 2 = A4 items P1, P1-delay, P2, P2-delay, P3, P4, P6 under A6 with a
Holm correction across the primary endpoints. Stage 3 not authorized.

Frozen by the owner's Stage 2 authorisation: design v0.3 Part A as written, the
A4a endpoint definitions, and Stage 1 `AMBIGUITIES.md` items 1–9 as adopted, with
items 7 and 9 treated as clarifications of the process specification. Those nine
are therefore not restated here; only new ones are.

No parameter, prediction, tolerance or rule was modified. Where the design is
silent on something a run cannot proceed without, the choice is DECLARED in
`config/stage2_config.py` and recorded below with the two readings considered.

---

## S2-1. Appendices C7, C8 and C9 are cited by the design but are not in this project

**Where.** A4 cites C7 (P6), C8 (P1), C9(a) (P7) and C9(b) (P4). Both Appendix C
and Appendix D of `review_packet_v0_6_1.md` stop at C6; B7 of the design says the
C7–C9 outputs are separate attachments. They are not files in `Crowd1/`.

**Effect, item by item.**
- **P1, P1-delay, P2, P2-delay, P3** — unaffected. C3(c) is in the packet and
  supplies every registered number; C8 is cited only for the channel narrative.
- **P4** — runnable. λ_c, λ_fold, f_c and A\* are tabulated in A4. The one missing
  input is **A_u(λ)**, needed by the activity criterion *"A(t) > A_u(λ)·1.5 at the
  horizon"*. It is computed from C2(b)'s exact stationary quadrature (C2.13–C2.15),
  which **is** in the packet, validated two ways before use: against C2.16's exact
  two-term small-ν expansion, where the residual is exactly O(ν³)
  (−8.8×10⁻¹³, −8.8×10⁻¹⁰, −8.8×10⁻⁷ at ν = 10⁻⁴, 10⁻³, 10⁻²), and against the
  three registered A\* values, which it reproduces to ≤0.007. The criterion is in
  any case a wide separator: ignited runs land near A\* ≈ 0.64–0.81 and the
  threshold 1.5·A_u is 0.21, 0.086, 0.018.
- **P6 case A** — runnable; A4 gives the crossing level A_f = 0.5603 and
  t† = 70.3 ± 0.1 as numbers, so no construction is needed.
- **P6 case B** — **BLOCKED**, see S2-3.

**Reading adopted.** Run everything the packet determines; block only case B; do
not substitute an invented construction for a missing appendix.

## S2-2. How f_c is to be inferred from a finite-N ignition curve (P4)

**Where.** A4 P4 fixes N = 5·10⁴, 100 replicates per (λ, f) cell "on a grid
bracketing each f_c", the criterion *"A(t) > A_u(λ)·1.5 at the horizon"*, horizons
{40, 80, 160}, and *"the inferred f_c is reported against realized reach"*. It
does not say what estimator turns a finite-N ignition-probability curve into a
single f_c. At finite N that curve is a sigmoid, not a step.

**Two readings.** (i) f_c is the 50 % point of the ignition-probability curve
against realized reach. (ii) f_c is the mean-field threshold, of which the finite-N
curve is a smeared image, to be estimated by extrapolating an N ladder.

**Adopted: (i)**, with (ii) supplied alongside as A6 error source 2 — an N ladder
to N = 2·10⁵ on a reduced reach grid. The two agree: the ladder shift in the
inferred f_c is −0.00056, −0.00015 and −0.00012 at λ = 1.60, 1.75, 1.90 for a
fourfold increase in N, an order of magnitude smaller than the discrepancies
against the registered values and not directed towards them. Horizon sensitivity is small but not identically zero: the inferred f_c is bit-identical across t = 40, 80 and 160 at λ = 1.60 and 1.75, and at λ = 1.90 it shifts by 1.08×10⁻⁴ between t = 40 (0.007419) and t = 80, after which t = 80 and t = 160 agree exactly (0.007310). That largest shift is 8.4% of the discrepancy against the registered f_c at that λ and 1.5% of f_c itself. This is the check A4 asks for *"before any threshold is inferred"*.

## S2-3. P6 case B: neither Λ nor case B's fold activity is defined in this project

**Where.** A4 P6 case B registers *"exact Λ = 25.4 at half fold activity versus
bridge 20.35"*. Neither the definition of Λ nor the **fold activity for case B**
appears in A4 or in the packet. Case A's A_f = 0.5603 is given as a number, not as
a construction that can be transported to case B's parameters.

**Two readings.** (i) Λ is the accumulated collapse index λ∫A dt (R5's
k_acc = λM t_acc) evaluated at the first downward crossing of half the frozen-rate
fold activity, with the fold activity obtained from C7's construction.
(ii) Λ is some other accumulated quantity of C7.

**Neither can be executed**, because both need C7's fold activity. A
reconstruction was attempted and **refuted**: taking the frozen-rate fold to be the
saddle-node of λ(ν) = ν/P_ν for a single frozen dose d, with P_ν the C2(b)
stationary law, gives sup over d ∈ [c_b, 1) of λ_fold = **2.574** at case A's
c_b = 0.5, so that construction cannot place a fold at case A's λ = 3 at all, let
alone reproduce the registered A_f = 0.5603; and for d ≥ 1 every receipt clips to
c = 1, which is R6/C2.24's class-1 forward transcritical case with no fold.

**Adopted:** report case B as BLOCKED with no verdict, and tabulate the measured
Λ = λ∫₀^t A ds at the first downward crossing of each of eleven activity levels
from 0.9 to 0.01, plus the total, so the comparison can be made without re-running
once C7 is supplied. Nothing was tuned towards 25.4.

## S2-4. The Holm correction is specified over endpoints, while A6's rule is interval-based

**Where.** A6: *"PASS if the interval lies inside [−δ, δ] … a Holm correction
across primary endpoints."* The pass rule is a confidence-interval rule and
produces no p-value; Holm needs one. An endpoint also has several registered rows,
while Holm's family is the six endpoints.

**Two readings.** (i) Attach to each row the p-value for the composite null
|d| ≤ δ, take each endpoint's p-value to be the smallest over its rows, and Holm
those six. (ii) Apply Holm by widening each endpoint's confidence level and
re-deciding the rows at the widened level.

**Adopted: (i)**, declared before the runs and reported as a separate table beside
the row-level verdicts, which are left exactly as A6's interval rule gives them.
Using the row minimum is anti-conservative for declaring an endpoint failed and
conservative for declaring it passed; it is recorded here because it matters for
only one endpoint. Under (ii) no verdict changes: widening intervals can only turn
a FAIL into an INCONCLUSIVE, and the five endpoints other than P4 have
Holm-adjusted p = 1.

## S2-5. "Present at every delay" is false at τ₀ = 0 (P1-delay)

Recorded as **A1** in `BUGLOG.md`, because it is a property of a registered
prediction rather than a choice this archive had to make. In summary: the exact
invasion-advantage ratio at τ₀ = 0 is **1**, because from I2 the maximally mixed
orientation is invariant under every projection (R8(b)) so the orientation channel
carries no order information, and the stance channel has had no time to act. The
measured ratio is 1.0006 with a 95 % interval [0.992, 1.009]. The row is reported
INCONCLUSIVE and the prediction is left untouched.

---

## Declared values that the design does not fix

All in `config/stage2_config.py`, marked `declared=`, fixed before the runs:
operator-check background counts and seed-trial counts (the design fixes replicate
counts only for the population checks); the P1 outbreak pilot size and the
replicate cap; the reach grids bracketing each f_c; the P4 N-ladder rung and its
reduced grid; the P6 sampling interval and horizons; and the bootstrap draw count.
None of these is a parameter of the process or of a prediction.
