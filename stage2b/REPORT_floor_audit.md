# Floor audit of every certified kinetic reference

*Owner request, 2026-10-02, following BUGLOG S2B-4.* Code `stage2b/floor_audit.py`
(modes `probe`, `ladder`) and `stage2b/matched_floor.py`; raw
`stage2b/outputs/raw/floor_audit.json`; logs `stage2b/outputs/logs/floor_audit_*.log`,
`.../matched_floor.log`.

## 1. Floors as run

| reference | floor as run | floor is the default 10⁻³? |
|---|---|---|
| P4 f_c^MF, λ = 1.60 / 1.75 / 1.90 | **10⁻³** | yes — the value implicated in S2B-4 |
| P6 case A, t† at A_f = 0.5603 | **2×10⁻²** | no — **20× coarser** |
| P6 case B, t* and Λ* at A = 0.325 | **10⁻²** | no — **10× coarser** |

Two of the three ran at a floor coarser than the one that biased the fold, so all
three were laddered rather than only the 10⁻³ case.

## 2. A confound that had to be removed first

Changing c_min changes U = −log c_min, hence J = round(U/h) and the **adjusted**
h = U/J. A naive floor comparison at one *requested* h therefore compares two
slightly different *actual* h. For case A, where dt†/dh ≈ −10.2, that confound is
the same size as the floor effect and has the opposite sign: the raw comparison at
requested h = 0.01 gave +1.307×10⁻³ while the matched-h comparison gives
+1.371×10⁻⁴, a factor of ten smaller.

The audit removes it by choosing c_min = 10⁻² and 10⁻⁴, for which U₂/U₁ = 2 exactly,
so J₂ = 2J₁ and the adjusted h is **identical** (asserted in the script, not assumed:
h = 0.009989523 for both case-A runs, 0.002500092 for both case-B runs). The P4 pair
needs no such treatment — at h = 0.004 the two floors give adjusted h differing by
4×10⁻⁷ relative, and with df_c/dh ≈ 0.94 that contributes under 10⁻⁶.

## 3. P4 f_c^MF — corrected

The floor shift is **h-independent to machine precision**, which is the direct
demonstration of why an h-ladder cannot see it: measured at h = 0.004 and h = 0.002,
T = 240, the two agree to **5.6×10⁻¹⁷**.

| λ | published (floor 10⁻³) | h error | floor shift 10⁻³→10⁻⁵ | **corrected f_c^MF** | floor error |
|---|---|---|---|---|---|
| 1.60 | 0.13273366 | ±9.34×10⁻⁴ | −5.2643×10⁻⁵ | **0.13268101** | ±1.53×10⁻⁶ |
| 1.75 | 0.04409694 | ±4.84×10⁻⁴ | −2.7466×10⁻⁵ | **0.04406947** | ±1.22×10⁻⁶ |
| 1.90 | 0.00709407 | ±2.61×10⁻⁴ | −1.1963×10⁻⁵ | **0.00708210** | ±8.54×10⁻⁷ |

The h error is unchanged by the correction, because the floor shift is independent of
h and so cancels out of every Richardson increment. The floor error is the residual
floor increment |f_c(10⁻⁴) − f_c(10⁻⁵)|; the floor is converged at 10⁻⁵.

Each shift is 5.6 %, 5.7 % and 4.6 % of its own h error, so no reported digit of the
published values moves outside its band.

**Verdict effect: none.** These three rows are REPORTED (reference) and carry no
verdict. Both Stage 2B conclusions survive the correction, checked explicitly:
the corrected interval still **overlaps the agent f₅₀ interval** at all three λ, and
is still **disjoint from the withdrawn Appendix F value** at all three.

One cell needed care rather than a rule change: at h = 0.002, T = 120, c_min = 10⁻⁵
the λ = 1.90 boundary trajectory was still undecided and the classifier **raised
`unclassified`** at f = 0.007603759765625 instead of forcing a basin. It is resolved
at T = 240, which `p4_reference.py`'s own horizon check had already validated as
agreeing with T = 120 to eight digits wherever both classify — and does so here:
at h = 0.004 the T = 240 values reproduce the T = 120 values exactly —
0.00814166 at c_min = 10⁻³ and 0.00812970 at 10⁻⁵ — the T = 120 minus T = 240
difference is **exactly 0.0** at both floors. The T = 120 side is the λ = 1.90 block of the floor probe
(`P4_floor_probe`, re-recorded with its horizon as `P4_lam190_T120_h004_floor`); the
T = 240 side is `P4_floor_shift_two_h`. The classifier rule and its 10⁻⁶ tolerance
are untouched.

## 4. P6 case A — t† at A_f

| quantity | value | h error | matched-h floor effect 10⁻²→10⁻⁴ |
|---|---|---|---|
| t† | 70.327688 | ±0.024355 | +1.371e-04 |

The floor effect is **0.56 % of the h error** and
0.14 % of the registered tolerance ±0.1.

**No corrected value is issued for case A, and — correcting version 2 of this
report — no bound on its floor error is claimed either.** What is measured is the
matched-h shift over c_min 10⁻² → 10⁻⁴, +1.371×10⁻⁴. Case A was run at 2×10⁻², and
the 2×10⁻² → 10⁻² step is **not quantified**: 2×10⁻² is not commensurate with the
matched pair (U₂/U₁ = 2 holds for 10⁻² against 10⁻⁴, not for 2×10⁻²), and an
unmatched comparison is confounded by the adjusted h, as §2 shows. A measured shift
over part of the range is not a bound over the whole of it. t† is reported unchanged at 70.327688 ± 0.024355 (h) with the floor contribution
**unquantified**. The two-dimensional ladder that would quantify it is deliberately
not run; the reason it would be needed is stated rather than papered over: the published ladder ran at 2×10⁻², and the matched-h construction
above pins the effect only between 10⁻² and 10⁻⁴ (U₂/U₁ = 2 exactly). The remaining
2×10⁻² → 10⁻² step is not commensurate, so a clean correction would need a floor
ladder at **every rung** of the h-ladder, which at 436 counter slabs and c_min = 10⁻⁴
is the expensive case. The measured part of the effect is under 0.6 % of the h error and under 0.2 % of the
registered tolerance, and the unmeasured 2×10⁻² → 10⁻² step is of the same kind, so
there is no indication that t† = 70.33 ± 0.02 or the validation against the
registered 70.3 ± 0.1 is affected — but that is an expectation, not a bound.

**Verdict effect: none.**

## 5. P6 case B — t* and Λ* at A = 0.325

| quantity | published (floor 10⁻²) | h error | matched-h floor effect | **corrected** | floor error |
|---|---|---|---|---|---|
| t* | 12.905389 | ±0.003053 | +6.886e-05 | **12.905457** | <5×10⁻⁸ |
| Λ* | 25.428485 | ±0.013437 | +1.225e-04 | **25.428608** | <8×10⁻⁸ |

Case B carried no h-confound — the matched-h effect (+6.886×10⁻⁵, +1.225×10⁻⁴) is
identical to the unmatched comparison (+6.881×10⁻⁵, +1.224×10⁻⁴) — and the floor is
converged: the 10⁻³ → 10⁻⁴ residual is +4.9×10⁻⁸ on t* and +7.1×10⁻⁸ on Λ*. The
floor effect is 2.3 % of t*'s h error and 0.9 % of Λ*'s.

**Verdict effect: none, and this is the one case with a live verdict.** Against the
corrected Λ* = 25.428608 at δ = ±1.27142 (5 %):

| agent estimand | measured | diff vs corrected | verdict |
|---|---|---|---|
| mean of replicate crossings | 25.43130 | +0.00269 | **PASS** (was PASS) |
| mean trajectory | 25.43138 | +0.00277 | **PASS** (was PASS) |

## 6. Summary

**Six** certified kinetic quantities were floor-audited, across three references.
Five are corrected — P4's three f_c^MF, and case B's t* and Λ* — and one is neither
corrected nor bounded: case A's t†, for which the matched 10⁻² → 10⁻⁴ shift is
1.4×10⁻⁴, the production-floor step 2×10⁻² → 10⁻² is not quantified, and **no bound
is claimed** — with the reason and the cost stated. **No verdict anywhere changes**,
and every shift is between 0.6 % and 5.7 % of the h error already published beside
it. The fold remains the only quantity the floor actually broke — because it was the
only one obtained as the argmin of a flat function, where a level error in P_ν is
amplified into the location of the minimum.

## 7. What the project already contained

Worth recording against S2B-4: `stage2/crowd1/predictions_s2.py::p4_fold()` returns
λ_fold = 1.482508331458303, ν = 0.5567914347613716, A_fold = 0.3755738992803306 —
the **exact** values, from the same C2.11–C2.14 method of steps, and it has done so
since Stage 2. The P4 basin classifier calls it for its ½A_fold threshold, so the
f_c classification never used a wrong fold. A single comparison against a function
already in the repository would have caught S2B-4 immediately. That comparison is now
part of `fold_exact.py`'s role, and the lesson is the same one in a different form:
cross-check a new reference against any existing independent implementation before
believing a disagreement with the manuscript.
