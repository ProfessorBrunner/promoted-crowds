# CROWD-1 Stage 1 — ambiguities encountered

Specification: `review_packet_v0_6_1.md`, memo section **PROCESS SPECIFICATION v0.6**
Design: `crowd1_cs_design_and_manuscript_brief_v0_3.md`, **Part A** (v0.3)
Scope: Stage 1 = A1 + A2 (T1–T6) under A6. Stage 2 not authorized.

Project rule: *"Do not modify any parameter, prediction, tolerance, or rule in the
design; if one is ambiguous or impossible as written, stop and report the ambiguity
with the two readings."*

No parameter, prediction, tolerance or rule was modified. Where the design is silent
on a quantity a run cannot proceed without, the choice is recorded below as DECLARED,
together with the two readings considered and the reading adopted. Every DECLARED
value is in `config/stage1_config.py`, marked `declared=`, and was fixed before the
runs.

Items 1–5 and 8 required a declared choice. Items 6, 7 and 9 are readings of the
specification text itself; each changes simulator behaviour, so both readings are
stated and the adopted one is justified from the text.

---

## 1. T1: the broadcast rate λ and the reach f are not declared

**Where.** A2, T1: *"α = 1, r = 10⁻⁶, single class, one pulse, aligned reinforcing
listeners."* The registered final-size comparison is against
`1 − Z = (1−f) e^{−λLZ}`, which depends on both λ and f. Neither is given. ε = 1 is
fixed by the A4 header; c_b = 0.5 is fixed by T1's own parenthetical
*"(L₊ − L ≈ 2×10⁻⁶ at c_b = 0.5)"*. β, c_h, the horizon, N and the replicate count
are also not given.

**Two readings.**
(i) T1 is a template to be instantiated at declared (λ, f) with λL > 1, so that the
registered equation has a root above the trivial one.
(ii) T1 inherits the parameters of some A4 item.

**Adopted: (i).** Reading (ii) has no candidate: no item of A4 uses α = 1 with
r = 10⁻⁶ and a single class. Two cells were declared — cell A (λ = 3.0, f = 0.10)
and cell B (λ = 2.0, f = 0.30) — plus a λ = 0 sub-case for the exact-lifetime claim.
DECLARED further: β = 0 and c_h = 0.01 (both inert — an aligned listener at φ = 0
never rejects θ = 0, so no negative deposit can occur), t_end = 200, N ladder
{10³, 10⁴, 10⁵} with 50/50/20 replicates.

## 2. T2: the two-camp initial state is not written out

**Where.** A2, T2: *"Renewal corner: r = 1, α = β = 1, two fixed camps; A* = 1 −
e^{−λLA*} on the persistent branch. Check: λ = 2, L = ln 2 gives A* = 0.5."* The
state the equation holds for, the camp fractions, the burn-in and the measurement
window are not given.

**Two readings.**
(i) Initialize at the invariant population Appendix C C2(d) names, which is the state
C2(d) labels EXACT for (C2.24): *"the invariant two-orientation population with
conviction sign matching orientation and stance … every peer receipt resets |c| to
one"*, i.e. camp + at φ = T_+ with c = +1, s = +, and camp − at φ = T_− with c = −1,
s = −, with the equation applying *"after initial-condition effects have expired"*.
(ii) Initialize at I1 or I2 and let the camps form dynamically.

**Adopted: (i).** Under (ii) the camps are not "fixed" as A2 requires, and C2(d)
does not license (C2.24) for a non-invariant population. DECLARED: M₊ = ½,
c_h = 0.01, ρ = κ = 0, burn-in to t = 20, measurement window [20, 70], N ladder
{10³, 10⁴, 10⁵} with 50/50/20 replicates. That the camps stay fixed is itself
checked as a pathwise row (T2.1).

## 3. T3: the prescribed Poisson input is not parameterized

**Where.** A2, T3: *"with a PRESCRIBED Poisson message input of known intensity, the
counter law equals 1 + Poisson(∫intensity) after one pulse."* The intensity function,
the framing, the population and the agent parameters are not given.

**Two readings.** (i) Any declared intensity will do, because the registered law
`1 + Poisson(∫intensity)` holds for every state-independent prescribed input.
(ii) A specific homogeneous intensity is intended.

**Adopted: (i),** with a deliberately *inhomogeneous* intensity so that the check
exercises `∫ intensity dt` rather than a rate–time product. DECLARED: a single
framing at 0°, ν(t) = 3 e^{−t/2} on [0, 20] (∫ = 6(1 − e^{−10}) = 5.99972…),
N = 10⁵, 10 replicates, α = 0.6, β = 0.2, r = 0.5, c_b = 0.95, c_h = 0.01, λ = 0,
f = 1, one pulse at 0° at t = 0. The non-zero α, β, r exercise the conviction and
activity machinery while leaving the prescribed input state-independent.

## 4. T4: the angle pair, and "anchor aligned with θ₁" under order reversal

**Where.** A2, T4: *"two coincident pulses at framings θ₁, θ₂ with Δ ∈ {15°, 30°,
45°, 60°, 75°}, both orders, from I1 (anchor aligned with θ₁), I2, and I3 (x = 0.6)."*
Specification v0.6 fixes I1 as φ = T_+ = 0°, so "anchor aligned with θ₁" can only be
realized by taking θ₁ = 0°; and then under order reversal the *first framing applied*
is θ₂, so the anchor is no longer aligned with the first framing.

**Two readings.**
(i) θ₁, θ₂ are fixed labels of the angle pair — here (0°, Δ) — and "both orders"
means the campaigns (0°, Δ) and (Δ, 0°). The I1 anchor is aligned with the
first-applied framing in order 1 only.
(ii) θ₁ denotes whichever framing is applied first, which would require the I1 anchor
to be re-aligned to Δ for the reversed order — something I1 as specified forbids.

**Adopted: (i).** It is also the reading T6 presupposes: T6 states the surrogate
*"fails T4's identity only from non-aligned initial laws"*, and under (i) the reversed
order from I1 is exactly such a non-aligned case, which the measured surrogate rows
confirm. DECLARED: θ₁ = 0°, θ₂ = Δ; α = 0.6, β = 0.2, r = 0.5, c_b = 0.95,
c_h = 0.01, λ = 0, f = 1; N = 10⁵, 20 replicates.

**Also undeclared: (ρ, κ, δ) for the I3 construction at x = 0.6, and the relaxation
time.** DECLARED: ρ = 1, κ = 0.5, δ = 30°, relaxation for 20/(ρ+κ). T4's registered
identity is independent of the initial law — it holds pointwise in φ₀ — so it is
insensitive to this choice. The individual joint-law cells are not, and are reported
against the exact stationary law of the declared (ρ, κ, δ); the realized relaxed
orientation histogram is logged beside it.

## 5. A6 gives three δ categories; three registered quantities fall in none of them

**Where.** A6: *"default 2% of the predicted value for operator checks; ±0.03
absolute for outbreak probabilities; 5% for trajectory markers."* A3 defines operator
checks as *"offspring counts, offspring types, and generation timing from a single
seed on a frozen background"*. The T1 final size Z and the T2 stationary active
fraction A* are none of those three. T6 has no stated tolerance at all.

**Two readings.** (i) Z and A* are trajectory markers → δ = 5% of the predicted
value. (ii) They are operator checks → δ = 2%.

**Adopted: (i)**, declared before the runs. The certified table reports the
discrepancy, its interval and δ explicitly, so a reader applying (ii) can re-decide
each row without re-running: both rows pass under (ii) as well. T3(a)'s counter mean
and variance were assigned the 2% operator-check tolerance, the counter law being
bookkeeping on one agent's receipts. For T6, δ = 3/√N was DECLARED by analogy with
the T4 identity that T6 is the registered contrast to.

**Not applicable in Stage 1:** A6's Holm correction is specified *"across primary
endpoints"*, and A6's primary endpoints are P1, P1-delay, P2, P3, P4, P6 — all of
them Stage 2 items. No multiplicity correction is applied to T1–T6, and none is
specified for them.

## 6. "Previous stance retained at an exact tie" bites only at c_h = 0

**Where.** MESSAGE TRANSITION step (5): *"s ← + if c ≥ c_h; − if c ≤ −c_h; unchanged
otherwise; previous stance retained at an exact tie."* Since c_h ≥ 0, the two
assignment clauses can fire simultaneously only when c_h = 0 and c = 0.

**Two readings.** (i) The tie clause refers to that simultaneity: at c_h = 0, c = 0,
retain the previous stance. (ii) The tie clause refers to c = ±c_h with c_h > 0 — in
which case it contradicts the two preceding clauses, which already assign + at
c = +c_h and − at c = −c_h.

**Adopted: (i)**, the only reading under which the sentence is consistent. Both signs
are covered by hand cases H4 in `crowd1/handtable.py`.

## 7. The exponent of the novelty weight: "r^(n_j(θ)−1) … post-increment counter"

**Where.** MESSAGE TRANSITION: *"(2) n_{j(θ)} ← n_{j(θ)} + 1. (3) c ← c +
r^{n_{j(θ)}−1} · cos 2θ · (+α if accepted, −β if rejected), post-increment counter."*
Step (2) has already incremented the counter, so "r^{n−1}" with the incremented n and
the trailing "post-increment counter" are two descriptions of the same thing.

**Two readings.** (i) The weight exponent is the number of *prior* exposures in that
class, so the first receipt in a class carries weight r⁰ = 1. (ii) The weight
exponent is the incremented counter, so the first receipt carries r.

**Adopted: (i).** It is forced by the appendices: C5(a) computes the (T, T) campaign
at α = 0.6, β = 0.2, r = 0.5 and obtains final convictions 0.9 and −0.3, i.e. first
deposits of exactly ±α, ±β and second deposits scaled by r. Reading (ii) would give
0.45 and −0.15. AGGREGATES also writes
`E[Δc | φ, θ, n_j] = (r^{n_j} cos 2θ/2)[…]` with the *pre-receipt* counter n_j, which
is the same convention.

## 8. The surrogate has no declared reset or reconsideration rule

**Where.** C5.0 declares the surrogate's update only on receipts — *"τ ← τ cos 2(θ−a),
a ← θ, then draw … with probability (1+τ)/2"* — and states *"All tests below have
ρ = κ = 0."* The specification's RESET (φ ← T_s) and RECONSIDERATION (φ ← T_s ± δ)
have no counterpart for τ. But A2 T4 asks for all three initial laws, and I3 is
defined only at ρ + κ > 0.

**Two readings.** (i) I3 is an *initial orientation law*; it is constructed by
relaxing the **silent** process (c ≡ 0 throughout, so no receipt occurs and the
surrogate's update rule never fires), and the surrogate is then initialized by its own
declared pure-state lift a₀ = φ₀, τ₀ = 1 on that law, with ρ = κ = 0 thereafter.
(ii) A reset/reconsideration rule for (a, τ) must be supplied before the surrogate can
be run from I3 at all.

**Adopted: (i).** It needs no rule the specification does not give: the relaxation
touches only φ, and in the main phase ρ and κ are inert because the campaign is
coincident (no clock event may occur between coincident pulses) and the run ends at
the pulse time. The engine *refuses* to run the surrogate with ρ > 0 or κ > 0 in a
main phase rather than inventing a rule (`runner.run_one` raises
`NotImplementedError`), so reading (ii) is enforced wherever (i) does not apply.

## 9. I2 "φ uniform" against exact-integer-degree angles

**Where.** INITIAL LAWS: *"I2 fresh-isotropic: φ uniform."* Design A1 and project
rule 2 require framing classes to be *"explicit integer identifiers assigned at angle
creation, never recomputed from floating-point angles"*. A continuous uniform φ
creates orientations whose framing class cannot have been allocated at declaration
time, and makes the pathwise claims of T5 (*P(AR) = P(RA) = 0 exactly*) unreachable,
because cos²(90°) evaluates to 3.75×10⁻³³ rather than 0 in binary floating point.

**Two readings.** (i) Represent all angles as exact integer degrees — every angle the
process of T1–T6 can create is one — and realize "φ uniform" as the uniform law on the
180 integer-degree rays of [0°, 180°). (ii) Keep φ continuous and accept that both the
class-identifier rule and the pathwise-zero claims hold only approximately.

**Adopted: (i).** It is the only reading compatible with A1 and project rule 2, and it
is *exact* for every quantity T4–T6 register, because for any constant c
`(1/180) Σ_{d=0}^{179} cos(2d° + c) = 0` and `(1/180) Σ_{d=0}^{179} cos(4d° + c) = 0`,
so E[cos²(θ−φ)] = ½ and E[cos² 2(θ−a)] = ½ exactly, as under the continuous law.
Both moments are verified numerically to 0 ulp in `crowd1/predictions.py`'s
self-check. This is recorded again as deviation D1 in README.md.

---

## Not ambiguities, but noted

- **A2 T3** explicitly removes the full-system formula `1 + Poisson(λ∫A_j)` from the
  acceptance conditions (*"a mean-field statement … run as a convergence check across
  the N ladder, not as a finite-N acceptance condition"*). It is reported as a
  convergence table with no PASS/FAIL verdict, as instructed.
- **A2 T6** describes the automaton as a *"positive equivalence control"* expected to
  reproduce every joint law. Implemented as a separate agent class, it turns out to
  agree with the process **pathwise**, not merely in law, under a shared seed — the
  automaton's state (last framing, last outcome) is a re-coordinatization of φ and
  the acceptance probability is identical message by message. The control is therefore
  exact by construction; this is reported rather than tested statistically, and the
  joint-law comparison is given alongside.
- **Erratum in the memo header** (R7's `[EXACT]` scope) concerns a Stage 2 quantity
  (R_inv) and does not bear on T1–T6.
