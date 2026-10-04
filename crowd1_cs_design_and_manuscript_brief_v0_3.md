# CROWD-1 — CS SIMULATION DESIGN v0.3 AND MANUSCRIPT BRIEF

Status: approved for Stage 1 (staged approval of 2026-10-01). Stage 2 runs only after the endpoint definitions in A4a are frozen; Stage 3 requires separate approval. Model: process specification v0.6 (review_packet_v0_6_1.md). v0.2 incorporates the design review of v0.1: P5 corrected (A* = 0.5); P9 surrogate prediction corrected and initial-anchor laws declared; simulator acceptance tests added; operator checks separated from population checks; pass rule replaced by a predeclared discrepancy rule; P8 moved to a censored supplement; null control removed; delay experiment added as the primary collective test; three-stage ordering.

---

## PART A — SIMULATION DESIGN

### A1. Implementation (exact simulator of the finite-N process)
- Event-driven simulation with four event types: Poisson broadcast (rate λ per active agent), Poisson reset (ρ), Poisson reconsideration (κ), and DETERMINISTIC activity shut-off. After any event that sets agent i's conviction to c_i with |c_i| > c_b, its unrefreshed shut-off time is t + ε⁻¹ ln(|c_i|/c_b); the engine keeps these deadlines in the event queue and refreshes them whenever c_i changes. A Gillespie step that jumps past a deadline is a bug.
- Campaign pulses at prescribed times, applied once to every cohort member, index order for coincident pulses, no clock events between coincident pulses.
- One uniformly random recipient per broadcast; message transition in the specified order; decay applied analytically between events.
- Framing classes carried as explicit integer identifiers assigned at angle creation, never recomputed from floating-point angles; opposite rays share one identifier.
- Cohort u_i ~ Bernoulli(f) drawn once; realized reach logged alongside nominal f.
- Initial laws I1, I2, I3 as specified; I3 by relaxing the silent process from a declared stance law.
- Seed for invasion tests: one agent at φ = T_+, c = 1, s = +, fresh counters, at the declared time.
- All random seeds logged.

### A2. Acceptance tests (Stage 1; must pass before Stage 2 runs)
T1. Stopwatch corner: α = 1, r = 10⁻⁶, single class, one pulse, aligned reinforcing listeners. Without subsequent messages the lifetime is exactly L = ε⁻¹ ln(1/c_b). With subsequent messages, activity begins with an uninterrupted interval of at least L and none occurs after L₊ = ε⁻¹ ln(1/(c_b − r/(1−r))), both measured from first activation (L₊ − L ≈ 2×10⁻⁶ at c_b = 0.5). Final size compared with the limiting equation 1 − Z = (1−f)e^{−λLZ} under the discrepancy rule, with the small-r approximation error included in the error budget.
T2. Renewal corner: r = 1, α = β = 1, two fixed camps; A* = 1 − e^{−λLA*} on the persistent branch. Check: λ = 2, L = ln 2 gives A* = 0.5.
T3. Counter bookkeeping: with a PRESCRIBED Poisson message input of known intensity, the counter law equals 1 + Poisson(∫intensity) after one pulse; class identifiers verified against a hand-computed table of coincident-pulse outcomes. The full-system formula 1 + Poisson(λ∫A_j) is a mean-field statement and is run as a convergence check across the N ladder, not as a finite-N acceptance condition.
T4. Cosine identity (implementation check of the response rule, not a validation of it): two coincident pulses at framings θ₁, θ₂ with Δ ∈ {15°, 30°, 45°, 60°, 75°}, both orders, from I1 (anchor aligned with θ₁), I2, and I3 (x = 0.6); same-outcome fraction P(AA) + P(RR) = cos²Δ for every initial law and both orders, within 3/√N.
T5. Repeated-framing lock: I2, (T, T): pathwise P(AR) = P(RA) = 0 exactly; x = 0 within sampling imbalance.
T6. Surrogate implementation (anchor a, receptivity τ; τ ← τ cos 2(θ − a), a ← θ; response sampled with probability (1+τ)/2 after the update, no outcome-dependent update). Predicted same-outcome fraction (1 + cos 2Δ·E[τ₁²])/2 where τ₁ = cos 2(θ₁ − a₀): equals cos²Δ from an anchor aligned with θ₁, and ½ + ¼ cos 2Δ from an isotropic anchor. Both verified. The surrogate therefore fails T4's identity only from non-aligned initial laws; that is the registered contrast, and the automaton storing (last framing, last outcome) with table cos²(θ_j − θ_i) is kept as a positive equivalence control that reproduces every joint law.

### A3. Observables and their separation
Operator checks: offspring counts, offspring types, and generation timing from a single seed on a frozen background, compared with the kernel or branching calculation. Population checks: outbreak probability (ever-active fraction exceeding 1% of N within a declared horizon) and subsequent trajectories in the full finite-N process. Reproduction numbers, growth rates and outbreak probabilities are reported as three distinct quantities; a growth rate is never used as an estimate of R.

### A4a. Endpoint definitions (frozen before Stage 2)
- Invasion advantage (F1): the ratio of invasion radii of the two orders, estimated from operator checks (offspring counts per seed on the saved post-campaign state at each delay); its limit 1.97 is a ratio of radii. Outbreak probabilities are reported alongside as a separate population endpoint and are never divided to form an "advantage." Frozen diagnostics at finite delay are labeled as such and reported separately from measured descendant growth.
- Observation horizons: outbreak tests run to t = 50/ε or until extinction; outbreak = ever-active fraction > 1% of N within the horizon. Where no numerical outbreak probability is predicted, ±0.03 is a precision target for the estimate, not an agreement tolerance.
- Tolerances for zero predictions: absolute, not relative: |x| ≤ 0.01 for x = 0; P(AR) = P(RA) = 0 pathwise (any violation is a FAIL); A_max, I, T_act = 0 predictions use absolute tolerance 10⁻³.
- P4 at λ = 1.40 (below the fold, no unstable branch): criterion is extinction, A(t) = 0 by t = 160 for every f tested.
- P2-delay with ρ = 0.5: resets act during the campaign's ln 100 gaps, so the post-campaign preparation is recomputed for ρ = 0.5 before the run; the ρ = 0 coefficients are not reused.
- Exponential decay claims: stated for the underlying state differences (orientation and conviction laws), not for the threshold observable, whose dependence is nonlinear and is reported as measured.

### A4. Registered predictions (ε = 1 throughout unless noted)

STAGE 2 — core collective tests

P1. Order through stance (R8(a), C3(c)(ii)). I2, f = 1, α = 1, β = ¼, r = ½, c_b = ½, c_h = 0.01, κ = 0, ρ = 1. Campaigns (40°,50°,140°) and (40°,140°,50°), zero gaps; relax for 10/ρ; then seed.
  Operator check: post-campaign x = 0 versus 0.9698; no activation; offspring counts of a single seed on the relaxed background consistent with R = 0.3466λ versus 0.6827λ. Population check: outbreak probability at λ ∈ {1.0, 2.0, 3.5}; predicted second order invades at λ = 2 (R = 1.365) and first does not (R = 0.693); neither at λ = 1; both at λ = 3.5. Held-out orders (50°,40°,140°), (140°,40°,50°) with x sealed from the enumeration before the run.
  N = 10⁵, replicates set so the outbreak-probability interval half-width is ≤ 0.03 at λ = 2 (pilot of 50 runs fixes the count); N = 10⁶, 50 replicates at λ = 2.

P1-delay (primary). Same campaigns; seed introduced at delays τ₀ ∈ {0, 0.5, 1, 2, 5, 10}/ρ after the campaign. Predicted: the invasion advantage of the second order is present at every delay, converging to the ratio 1.97 as τ₀ → ∞ (stance channel); any orientation-preparation contribution decays with e^{−ρτ₀}. This is the paper's main figure.

P2. Orientation channel at ρ = κ = 0 (C3(c)(i)). I1, f = 1, α = 1, β = 0, r = ½, c_b = 0.95, gaps ln 100; orders (10°,20°,30°), (10°,30°,20°), (20°,10°,30°); T seed.
  Operator check: first-generation acceptance q_T = 0.7074, 0.7591, 0.6379 and R/λ = 0.03629, 0.03894, 0.03272. Population check at λ = 26.5 (R = 0.962, 1.032, 0.867): near-critical, so the registered quantity is the outbreak probability with a precision target of ±0.02, replicate count fixed by pilot; and from I2 all three orders equal (R/λ = 0.0256).
  N = 10⁵.

P2-delay. Same, with the seed delayed by τ₀ ∈ {0, 1, 3, 10}/ε at ρ = κ = 0: predicted order dependence persists (orientation never relaxes) while residual conviction decays; and with ρ = 0.5 added: predicted order dependence decays as e^{−ρτ₀}.

P3. Outcome–deposit channel (C3(c)(iii), C5(b)). I2, f = 1, α = 0.6, β = 0, r = ½, c_b = 0.5, ρ = κ = 0; (45°,20°) versus (20°,45°), zero gap.
  Operator check on the saved post-campaign state: the frozen diagnostic 0.317λ versus 0.219λ evaluated directly on that state; E Z₂ = 0.0977λ² versus 0.0690λ² from a seed introduced immediately (time-dependent kernel). Population check: outbreak probability at λ = 4 for seed delays τ₀ ∈ {0, 1, 3, 10}/ε; predicted convergence of both orders to R = 0.0912λ = 0.365 (both subcritical) at large delay.
  N = 10⁵, 300 replicates at τ₀ = 0, 100 otherwise.

P4. Class-2 backward onset and finite-amplitude threshold (R4, C9(b)). r = 1, α = 0.5, c_b = 0.3, κ = ρ = 0, β = 0; one pulse of reach f sets the cohort at c₀ = α.
  Predicted: λ_c = 1.958, λ_fold = 1.49; f_c = 0.127 ± 0.002 at λ = 1.60, 0.038 ± 0.001 at 1.75, 0.0086 ± 0.0008 at 1.90; A* = 0.63, 0.75, 0.81; no reach ignites at λ = 1.40.
  Activity criterion: A(t) > A_u(λ)·1.5 at the horizon, with A_u the unstable branch; horizons t ∈ {40, 80, 160} to test horizon sensitivity before any threshold is inferred. Realized reach logged; the inferred f_c is reported against realized reach.
  N = 5·10⁴, 100 replicates per (λ, f) cell on a grid bracketing each f_c.

P6. Burn-out and the frozen-rate fold (C7). Case A: α = 2, β = 0, r = 0.99, λ = 3, c_b = 0.5, ρ = κ = 0, f = 1, I1, one pulse. The comparison quantity is the counter-resolved kinetic solution (Appendix C C2(a) Picard iteration of the full joint law, not a frozen-rate or averaged-counter approximation): t† = 70.3 ± 0.1 (first downward crossing of A_f = 0.5603). The adiabatic value 66.3 is reported as the approximation being assessed. Case B: α = 1, c_b = 0.4, λ = 2.5, r = 0.95, f = 1: exact Λ = 25.4 at half fold activity versus bridge 20.35.
  Predicted: simulation agrees with the kinetic solution within the discrepancy rule; the adiabatic error is 6% (A) and 20% (B). Two cases check two cases; no delay law is claimed from them.
  N = 10⁵, 50 replicates per case.

STAGE 3 — extensions and supplements

P5. Class-1 onset (C9(b)). r = 1, α = 2, β = 0, c_b = 0.5, κ = ρ = 0, I1, one pulse of reach f. Predicted (mean field): λL > 1 with L = ln 2 means any positive reach reaches the persistent branch; at λ = 2, A* = 0.5; λL < 1 (λ = 1) means activity dies. Finite-N: positive seeds can die out; report outbreak probability at f = 0.01 and 0.1.
  N = 10⁵, 50 replicates per cell.

P7. Finite-amplitude observables (C9(a)). α = 1, β = 0.4, r = 10⁻⁶, λ = 0.5, c_b = 0.5, c_h = 0.01, ρ = κ = 0, I1, one pulse, f ∈ {0.10, 0.25, 0.50, 0.75}. Point predictions from the analytical enclosures: at f = 0.25, A_max = 0.32038, I = 0.22969, T_act = 0.69315; reach table as in C9(a); two-pulse coincident {T, T⊥}: (T, T⊥) reproduces the single-pulse values, (T⊥, T) gives zero.
  N = 10⁵, 50 replicates per cell.

P8 (supplement, censored). Finite-N extinction on the persistent branch, P5 parameters at λ = 2, f = 0.5: extinction-time distribution at N ∈ {100, 200, 400, 800} with a predeclared maximum observation time T_max = 2000 and censored survival reporting. Predicted: extinction almost surely with a median that grows steeply in N; no scaling law is registered.
  100 replicates per N.

P9 (supplement). Two-camp fixed points (R9): r = 1, κ = 0, α = 1, β = 0.4, M₊ = M₋ = ½, λ ∈ {1.5, 2, 3}: measured (A₊, A₋) against the quadrature fixed points of Appendix C C4.7; stability by perturbation.

P10 (supplement, coefficient map only). Lux coefficient map (R10): r = 1, h ∈ {0.1, 0.05, 0.02}, a₀ = 1.2, b₀ = 0.8, Λ = 1, p₀ = 1, k₀ = 1, δ = 30°, c_b small, c_h = 0: measured H, J, D from conviction drift and diffusion on the active branch against C6.5–C6.6 at O(h). At these parameters H = 2.5, J = 0.8, D = 1.367, J/D = 0.585 and (H − ε/2)/D = 1.46, so this is NOT a deep-well regime and no switching-exponent comparison is made here. A rare-switching test is a separate limit experiment requiring (H − ε/2)/D ≫ 1 and its own approval.

### A5. Controls and comparators
- Classical outcome-memory automaton (last framing, last outcome, table cos²(θ_j − θ_i)) on T4–T6, P1, P3: positive equivalence control, predicted to reproduce every joint law.
- Bloch-mean surrogate on T4–T6 and P3 (declared initial anchor laws): registered contrast.
- Target-only broadcast variant only in cells where it is not a null control, i.e., with κ > 0 (P1 rerun at κ = 0.5): predicted to change the operator through the parent-side ±δ broadcasts (C8(c)).
- Dodds–Watts dose-window model at matched (λ, threshold, window L) on P4 and P5: shared three-class structure, different boundary.
- Held-out orders on P1 and P2, sealed.

### A6. Pass rule and error accounting
For each registered quantity, a discrepancy δ is predeclared (default 2% of the predicted value for operator checks; ±0.03 absolute for outbreak probabilities; 5% for trajectory markers). The simulation-minus-prediction difference is estimated with its confidence interval; PASS if the interval lies inside [−δ, δ]; FAIL if it lies outside; INCONCLUSIVE otherwise, with the replicate count needed to resolve. Four error sources are reported separately: Monte Carlo, finite-N bias relative to the mean-field prediction (from the N ladder), numerical error of the theoretical calculation (from the quadrature's own convergence), and closure error (adiabatic versus kinetic). Primary endpoints: P1, P1-delay, P2, P3, P4, P6; secondary: the rest; a Holm correction across primary endpoints. No parameter is tuned after a FAIL. Implementation bugs, algebraic errors in a prediction, and model failures are logged as distinct categories, corrected in versioned reruns with the original results retained.

### A7. Figures
F1 (main). Invasion advantage of the second order versus seed delay (P1-delay), with the stance-channel limit 1.97 and the e^{−ρτ₀} decay of the orientation contribution; inset P2-delay.
F2. Outbreak probability versus λ by order (P1, P2).
F3. f_c(λ) in the class-2 backward regime with λ_c and λ_fold (P4); class-1 panel with no threshold (P5).
F4. A(t) for P6 case A with the kinetic solution and the adiabatic fold time marked.
Supplement: same-outcome fraction versus Δ for process, automaton and surrogate (T4–T6).

---

## PART B — MANUSCRIPT BRIEF (for the drafting chat)

Working title: Campaign order, stance memory and burn-out in promoted crowds.

Venue constraint: physics first; no empirical mapping, no market.

### B1. The narrative, narrowed
A promotional campaign leaves a persistent change in a silent population's stance distribution, and that change sets the population's susceptibility to later invasion after the immediate conviction and orientation effects of the campaign have relaxed. The invasion criterion is a derived next-generation operator on the joint stance–counter law; the crowd's own talking is endogenous and gated by conviction; habituation gives a finite budget, so every boom ends. Order matters through what the campaign leaves behind, not through what it does while it runs.

Distinction from Niu, Shu & Zhao 2026, stated precisely: both encode history in the post-campaign state; the difference is the derived invasion operator with endogenous broadcasting, the conviction gate, and the habituation budget, and the explicit separation of the persistent stance channel from the transient orientation and outcome–deposit channels with their decay rates.

### B2. Claims in four sentences
1. Finite budget: with finitely many framings and habituation, total activity is bounded and the crowd goes silent without any scheduled event (theorem R2).
2. Order through stance: campaign order changes the post-campaign stance law and hence the invasion threshold, by a factor 1.97 in a worked case; the other two order channels decay at ρ + κ and ε (R7, R8, C8; certified by P1, P1-delay, P2, P3).
3. Onset and burn-out: at r = 1 the onset has three classes with a closed-form clipped boundary; for a running habituating crowd a conditional frozen-rate approximation locates the collapse at its fold, and two kinetic comparisons show the approximation's error (6% and 20% at the two η tested), with no general delay law claimed; a finite-amplitude ignition threshold exists only in the backward regime (R4, C7, C9; certified by P4, P6).
4. The response rule's prediction: P(AA) + P(RR) = cos²Δ for any two framings in either order from any initial law; a classical outcome-memory automaton reproduces every joint law, so the test is of the cosine law, not of a quantum implementation (R11; T4–T6).

### B3. Section plan
1. Introduction. 2. Model (specification v0.6 verbatim; three meanings of ignition). 3. Extinction (R2; finite-N). 4. Invasion and order (R7 multitype and reduced forms with scope; C8; the three channels; F1, F2). 5. Onset and burn-out (R4 with Dodds–Watts; C7 frozen-rate fold; C9(b) threshold; C9(a) observables; F3, F4). 6. What the response rule predicts (cosine invariance; automaton). 7. Discussion and open problems (uniform fold-time theorem; f_c near λ_fold; finite-N ignition; gated O(h)).
Appendices: two-camp dynamics (R9); the Lux coefficient map (R10); C1–C9 derivations with labels intact.

### B4. Theorem statements to lift verbatim, with hypotheses
R2 (Appendix C §C2.0); R7 (Appendix C §C3(a), C8(a); reduced forms with scope; used-counter form); R4 (both round-two reviews derive G(α)); R6 corners; R9 (quadratures, extremal fixed points, spr(J) < 1; no ordering claim); R10 (closure, conditions, Appendix C C6.16); cosine invariance (Claude round-two review §5); C7 bridge bound (conditional) and the fold comparison; C9(b) f_c(λ) in class 2 backward; C9(a) enclosures.

### B5. Pending certification
All numbers in P1–P7 and T4–T6 carry a "pending" mark; when the certified table arrives, the prose is revised to what was measured, not merely unmarked.

### B6. Comparators by section
§1 Harras & Sornette 2011; §2 Wang & Busemeyer 2013, Wang et al. 2014; §3 Wang, Tang, Zhang & Lai 2015, Hashemi et al. 2021; §4 Carro et al. 2015, Niu et al. 2026, Miller & Campbell 1959; §5 Dodds & Watts 2004/2005, Cooke & Yorke 1973 (pending equation-level match); §6 Chu 2026, Özmen Garibay & Mutlu 2021; appendices Lux 1995, Krause & Bornholdt 2013, Henkel 2016.

### B7. Routing
Draft in a fresh Opus chat with this file, review_packet_v0_6_1.md, and the two C7–C9 outputs attached. Blind read of the draft on Fable, fresh chat. CS runs Stage 1 now. Stage 2 after Stage 1 passes AND the A4a definitions are frozen. Stage 3 on separate approval.
