# Stage 3 item P7 — ambiguities encountered

Stage 1 items 1–9 (frozen as design v0.3.1 A4b), Stage 2 items S2-*, Stage 2B items
S2B-A*, and Stage 3 P5 items P5-A* are unchanged and still govern. This file lists
only what P7 newly encountered.

---

## P7-A1 — is the coincident-pulse claim registered at one reach or at all four?

**Where** Design v0.3.1 A4 item P7: "two-pulse coincident {T, T⊥}: (T, T⊥)
reproduces the single-pulse values, (T⊥, T) gives zero" — stated without naming a
reach. Appendix E §C9(a) states the same result inside its f = 0.25 case ("order
(T, T⊥) ends at c = 1, n_T = 2, same enclosures").

**Reading 1** The claim is registered only at f = 0.25, where Appendix E states it.
**Reading 2** The claim is registered at every reach in the P7 grid, since A4 does
not restrict it and the underlying arithmetic (final conviction 1 versus 0.400001)
is independent of f.

**Adopted** Reading 2, the stronger test: both orders were run and verdicted at all
four reaches. All twelve (T, T⊥) rows and all twelve (T⊥, T) rows PASS, so no
reading is contradicted and reading 1's four rows are a subset of what is reported.

---

## P7-A2 — T_act is grid-quantized, not grid-convergent

**Where** The measurement of `T_act = Leb{t : A(t) > A_max/2}`, not the design.

**Problem** A crosses A_max/2 at a **jump** discontinuity: every cohort member shuts
off inside the 2 × 10⁻⁶ window [L, L₊], so A falls by the realized reach essentially
instantaneously at t = L. Any sampling grid therefore returns `ceil(L/dt)·dt`
exactly, and a grid-refinement ladder shows **no movement at all** (0.6932 at
dt = 4 × 10⁻⁴, 2 × 10⁻⁴ and 10⁻⁴ alike). A ladder residual of zero would, taken at
face value, claim a numerical error of zero, which is wrong.

**Adopted** The numerical error for T_act is the **quantization**
|ceil(L/dt)·dt − L| = 5.282 × 10⁻⁵, not the ladder residual. This is stated in each
T_act verdict row's note. The same applies to the bootstrap interval, which has
exactly zero width because T_act has no replicate-to-replicate variation at this
resolution; that is reported as a property of the quantity, not a precision claim.

**For the owner** Any future endpoint defined by a level crossing of a trajectory
with a deterministic jump needs the same treatment. An alternative is to define
T_act by the analytic crossing time rather than a grid measure; that would be a
change to the estimand and is not made here.

---

## P7-A3 — the campaign reach is a Bernoulli draw, so "f" has two meanings

**Where** A1 ("Cohort u_i ~ Bernoulli(f) drawn once; realized reach logged alongside
nominal f") against the C9(a) formulas, which take f as an exact population fraction.

**Status** Not a new ambiguity — A1 already resolves it, and Stage 2's P4 reported
f_c against realized reach for the same reason. Recorded here only because P7's
predictions are *point* predictions in f at δ = 2 %, so the distinction could matter
in principle. It does not at N = 10⁵: the realized reaches average 0.100010,
0.249927, 0.500017, 0.750268, within 3.6 × 10⁻⁴ of nominal, while the binomial
standard deviation of the realized reach is at most 1.6 × 10⁻³ — both far inside the
tolerances, and the resulting scatter is already inside the reported Monte-Carlo
error. Predictions are quoted against nominal f, as registered.
