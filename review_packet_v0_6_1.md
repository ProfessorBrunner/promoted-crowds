# REVIEW PACKET v0.6.1 — Promoted crowds under a projective response rule with novelty-weighted memory: ignition, invasion, burn-out

Contents: Idea memo v0.6 (authoritative); Appendix C — ChatGPT C1–C6 derivation (verbatim); Appendix D — Claude C1–C6 derivation (verbatim). The process specification v0.6 that both derivations were run against is reproduced in the memo. Appendices A and B of packet v0.5 are superseded and not included.

---

## IDEA MEMO v0.6.1 (for blind review, round two)

Erratum from v0.6: R7's closed form was labeled exact for the full process with κ > 0; it is exact only when active parents do not reconsider during their lifetime. The general criterion is Appendix C's multitype operator. The substantive claim (dependence on x only, no preparation product) holds in both. Reviewers are asked to check every other [EXACT] label for the same kind of scope gap between the two appendices.

### SCOPE OF CLAIM
A single mean-field stochastic process, specified below, in which (i) a silent population is absorbing and its invasion by an active seed is governed by a closed-form criterion that depends on the population's stance law and not on any framing-preparation product; (ii) the onset of self-sustained activity has three classes, forward transcritical, backward transcritical with hysteresis, and saddle-node, and habituation carries a crowd through all three; (iii) with finitely many framing classes and habituation, activity is bounded and ends without any scheduled event; (iv) campaign message order changes the invasion threshold through the stance law it leaves behind, with two further order channels that are transient multipliers decaying at rates ρ and ε; (v) a finite promotional cascade and a Lux-type two-state switching law are recovered as restricted limits, the latter under stated conditions and as a coefficient map onto a generic form; (vi) the projective response rule contributes one observable, Lüders repeatability of outcomes, measurable three ways and absent from the Lux regime. No universal ignition threshold, no interior phase diagram in r, and no market result are claimed.

### THREE MEANINGS OF "IGNITION", KEPT SEPARATE
Activation: the campaign itself creates agents with |c| > c_b. Invasion: linear growth of activity from an infinitesimal active seed in a declared background. Persistence: mean-field activity positive as t → ∞.

### PROCESS SPECIFICATION v0.6
AGENTS. N agents. State: orientation φ_i ∈ [0°,180°); conviction c_i ∈ [−1,1]; stance s_i ∈ {+,−}; exposure counters n_{i,j} ∈ ℕ per framing class j; campaign indicator u_i ∈ {0,1}. Parameters: ε > 0; 0 < c_b < 1; 0 ≤ c_h < c_b; α, β ≥ 0; λ, ρ, κ ≥ 0; 0 < r ≤ 1; 0 < δ < 45°. Targets T_+ = 0°, T_− = 90°. Framing class of θ: the basis {θ, θ+90°}, keyed by θ mod 90°.
CLOCKS. Independent Poisson clocks per agent: broadcast at rate λ (active only), reset at rate ρ, reconsideration at rate κ. Clocks, recipient draws and acceptance coins are mutually independent. Campaign messages occur at prescribed pulse times, not Poisson.
PEER DELIVERY. When an active agent's broadcast clock rings, it sends its current orientation to one other agent chosen uniformly at random. Mean-field hazard of receiving a peer message: λA, orientation drawn from the active orientation distribution.
MESSAGE TRANSITION (atomic, in this order): (1) accept with probability cos²(θ−φ) → φ ← θ; else reject → φ ← θ+90°. (2) n_{j(θ)} ← n_{j(θ)} + 1. (3) c ← c + r^{n_{j(θ)}−1} · cos 2θ · (+α if accepted, −β if rejected), post-increment counter. (4) clip to [−1,1]. (5) s ← + if c ≥ c_h; − if c ≤ −c_h; unchanged otherwise; previous stance retained at an exact tie.
RESET (rate ρ): φ ← T_s. RECONSIDERATION (rate κ): φ ← T_s ± δ, each with probability ½. Neither changes c, s or counters. DECAY: ċ = −εc between events. Counters never decrease. ACTIVITY: broadcast iff |c| > c_b; silent agents receive.
CAMPAIGN. Cohort drawn once, u_i = 1 with probability f. A campaign is a finite list (t_k, θ_k), applied once to every cohort member at t_k; coincident pulses compose in index order with no reset or reconsideration between them. Order comparisons hold the multiset, pulse times, m and f fixed.
INITIAL LAWS. I1 fresh-aligned: φ = T_+, c = 0, s = +, n = 0. I2 fresh-isotropic: φ uniform, c = 0, s = + unless declared, n = 0. I3 stationary silent background at (ρ, κ) with stance law p_+: c = 0; given s, φ = T_s w.p. ρ/(ρ+κ), T_s ± δ w.p. κ/(2(ρ+κ)) each; counters declared. Result-2-type statements require finitely many initial orientation classes.
LIMITS. Mean field: N → ∞ at fixed t, then t → ∞ if a long-time statement is made; state the order. Finite N: after any finite campaign the population becomes silent almost surely; all persistence statements are mean-field. Invasion on I3: spectral radius of the next-generation operator; on a prepared background the operator is time-inhomogeneous.
AGGREGATES. A active fraction; x = E[s]; B = E[s·1(|c|>c_b)]; Z ever-active fraction; L = ε⁻¹ ln(1/c_b); L_α = ε⁻¹ ln(min(α,1)/c_b)·1(α > c_b), L_β likewise. Expected unclipped increment: E[Δc | φ, θ, n_j] = (r^{n_j} cos 2θ / 2)[(α − β) + (α + β) cos 2(θ − φ)].
PROVENANCE. The orientation rule is the two-dimensional real projective (Lüders) response of the quantum question-order model (Wang & Busemeyer 2013; Wang, Solloway, Shiffrin & Busemeyer 2014). Conviction, stance, habituation, activity gate and campaign are the additions.

### RESULTS
Labels: EXACT = consequence of the specification, obtained independently in Appendices C and D and agreeing; LIMIT = under an explicit scaling with its order stated; CLOSURE = under a named reduction; OPEN. Where the two appendices differ the difference is stated.

R1. Kinetic equation. [EXACT] Mean-field generator of McKean–Vlasov type with impulsive cohort maps at pulses (C §C1, D §C1). Class-specific novelty clock in a cohort: E[r^{n_j(t)}] = E[r^{n_j(0)}] r^{m_j(t)} exp[−(1−r)λ∫₀ᵗ A_j]. The joint law is the state; (x, A, B), with or without mean budgets, do not close. The single-class optimist crowd at exact targets with κ = 0 closes on a one-dimensional conviction density, and on A alone when α ≥ 1 (D).

R2. Finite-budget extinction. [EXACT, hypotheses: r < 1, finitely many accessible framing classes, counters without recovery, finite campaign] ∫A dt < ∞ and A(t) → 0; no stationary branch exists for any 0 < r < 1, in one camp or two. Order of limits: fixed r < 1 then t → ∞ gives silence; r → 1 first can give persistence. The theorem does not use the projective rule. A continuously oriented initially active population violates the finite-class hypothesis; a continuously oriented initially silent one does not.

R3. Exact activation and the sparse exponent. [EXACT] For prescribed peer intensity, P_t(c > c_b) is an explicit ordered-time quadrature with clipping at every receipt, with a controlled truncation error and a convergent Picard iteration for the self-consistent A(t) (C §C2a). The minimal activating receipt count under habituation is the geometric count m_r = min{k : α rⁿ(1 − r^k)/(1−r) > c_b}, infinite when the remaining budget α rⁿ/(1−r) ≤ c_b; the frozen-dose formula ⌊c_b/(α r^{n−1})⌋+1 is correct only at r = 1 and otherwise understates the exponent (example: α rⁿ = 0.4, r = 0.5, c_b = 0.65 gives 3, not 2).

R4. Onset in three classes (r = 1, single class, κ = 0, stationary self-consistency A = M P_{λA}). [EXACT for classes 1 and 3; class 2 EXACT in the unclipped regime 2α < 1 (C §C2b), sign condition stated generally (D §C2b)]
 Class 1, α ≥ 1: P = 1 − e^{−νL} exactly, concave; forward transcritical at λML = 1, continuous onset.
 Class 2, c_b < α < 1: the point A = 0 is transcritical at λML_α = 1, but the small-ν expansion P_ν = νℓ + ν²(π²/12 − ℓ²/2) + o(ν²), ℓ = ln(α/c_b) (unclipped regime), has a positive quadratic coefficient whenever ℓ < √(π²/6) ≈ 1.28: the onset is backward, with a fold below λ_c = 1/(Mℓ) and hysteresis. Example: α = 0.4, c_b = 0.39, ε = 1, M = 1: λ_c = 39.50, coefficient 0.822 > 0.
 Class 3, α ≤ c_b (m ≥ 2): P = Θ(ν^m), the silent state is linearly stable for every λ, and the least λ with a positive fixed point is a saddle-node (critical mass).
 Habituation shrinks the effective dose α rⁿ and carries a crowd from class 1 through 2 to 3 as exposure accumulates. The previously stated dichotomy "transcritical iff m = 1, saddle-node iff m ≥ 2" is withdrawn.

R5. Burn-out in time. [CLOSURE: fluid regime λM ≫ ε, shot noise self-averaging; D §C2c] Mean conviction c̄(t) = c₀e^{−εt} + λMα r^{m₀}[e^{−gt} − e^{−εt}]/(ε − g), g = (1−r)λM; collapse when c̄ falls to c_b; collapse index k_acc = λM t_acc, with closed forms in the branches g < ε and g > ε, and residual-conviction factor (ε − g)/(λM) relative to the single-shot index k_cross. [EXACT] The stochastic collapse index is random, with no common population value (C §C2c); a sufficient permanent-silence test is c + α rⁿ/(1−r) ≤ c_b. [OPEN] The crossover between the fluid and sparse regimes in closed form.

R6. Standard corners. [LIMIT] r → 0, α = 1: each first-exposed agent broadcasts for exactly L and the cascade closes to Kermack–McKendrick with fixed duration, 1 − Z_∞ = (1 − Z₀)e^{−λLZ_∞}, invasion iff λL > 1. [EXACT, submodel] r = 1, α = β = 1, two fixed camps: A(t) = M[1 − exp(−λ∫_{t−L}^{t}A)], A* = M(1 − e^{−λLA*}), threshold λML = 1 (Cooke–Yorke constant-period SIS with contact reset); x is inert. Neither is claimed as new.

R7. Invasion of a stationary background. [EXACT, general form] On I3 with stance law p_± = (1 ± x)/2, single class, single-shot doses, the invasion criterion is the spectral radius of the multitype next-generation operator of Appendix C (C3.3–C3.4), whose types are (broadcast angle, outcome) with broadcast angles in {0, ±δ, 90°, 90°±δ} once κ > 0, and whose parent occupation measure W_b splits a parent's lifetime between its birth orientation and the relaxed I3 orientation law. On I3 the operator depends on the background through x and (ρ, κ, δ) only; no framing-preparation product survives. [EXACT, reduced form; scope corrected in v0.6.1] When active parents do not reconsider during their lifetime, κ = 0 or ℓ_b(ρ + κ) ≪ 1, the operator reduces to rank 2 and
 R_inv = ½[u + √(u²y² + v²(1 − y²))], u = λL_α, v = λL_β, y = ζx, ζ = (ρ + κ cos 2δ)/(ρ + κ) = 1 − 2g,
 with listener acceptance π₁ = (1 + ζx)/2 agreeing exactly between Appendices C and D. For β ≤ c_b: R_inv = λL_α (1 + ζx)/2. For κ > 0 with parents that reconsider during their lifetime, this closed form is the two-type approximation of the multitype spectral radius, not the exact criterion (Appendix D's four-type reduction keeps broadcasters at exact targets; Appendix C's does not). For v > u the balanced background is easiest to invade, in the reduced form.

R8. Prepared backgrounds and the three order channels. [LIMIT: mean field, linearization, then t → ∞] A prepared background relaxing at rate ρ multiplies a seed by a finite gain G(τ₀) = Π_k R(τ₀ + kL); asymptotic growth is decided by R_inv(I3) alone. A frozen spectral radius at the seed time is a diagnostic, not a threshold. [EXACT, constructions, f = 1, ε = 1]
 (a) Stance channel, permanent under resets. I2, α = 1, β = ¼, r = ½, c_b = ½, c_h = 0.01, κ = 0, ρ > 0, zero-gap campaigns relaxed to I3: (40°,50°,140°) leaves x = 0; (40°,140°,50°) leaves x = 0.970. Nothing activates. R_inv = λ ln 2 · p_+ = 0.347λ versus 0.683λ, a factor 1.97, carried by x alone.
 (b) Orientation channel, permanent only at ρ = κ = 0 and only from non-isotropic starts. I1, α = 1, β = 0, r = ½, c_b = 0.95, gaps ln 100, preparations (10°,20°,30°), (10°,30°,20°), (20°,10°,30°), T seed: q_T = 0.7074, 0.7591, 0.6379; R_inv = 0.0363λ, 0.0389λ, 0.0327λ. From I2 the maximally mixed state is invariant under every projection and all orders give 0.0256λ.
 (c) Outcome–deposit channel, transient at rate ε even when orientation is frozen. I2, α = 0.6, β = 0, c_b = 0.5, ρ = κ = 0, zero gaps, seed immediately: (45°,20°) gives frozen R = 0.317λ/ε, (20°,45°) gives 0.219λ/ε; both orders share the asymptotic threshold R_∞ = (λ/2) ln 1.2 = 0.091λ/ε; the transient difference in expected second-generation count is 0.0977λ² versus 0.0690λ².
 The earlier "isotropic no-go" and the earlier Γ-to-invasion inference are both withdrawn; 7a of v0.5 is replaced by (b), and 8 of v0.5 by the statement that the maximally mixed orientation is invariant while stance and conviction are not.

R9. Two-camp branch. [EXACT] With fixed camps at κ = 0, r = 1, the stationary conviction marginals are explicit (unclipped Laplace transform via Ein; clipped by method of steps), the self-consistent system (A_+, A_−) is cooperative so fixed points are ordered and stable and unstable ones alternate, and local stability is decided by the spectral radius of the static susceptibility matrix. Skeptic activity is a smooth function of forcing: for every β > 0 and λA_+ > 0, 0 < P(|c_−| > c_b) < 1; there is no sharp activation threshold. [CLOSURE, fluid] Fixed points (M_+, 0) iff λαM_+ > εc_b and λβM_+ ≤ εc_b; coexistence iff λ(βM_+ + αM_−) > εc_b and λ(αM_+ + βM_−) > εc_b; skeptic hysteresis band εc_b/λ ∈ (βM_+, βM_+ + αM_−). At α = β = 1 the system reduces to R6 with x inert. [LIMIT] At r < 1 no positive two-camp branch exists. [OPEN] Exact tails with clipping; the coexistence boundary beyond the fluid closure.

R10. Lux limit as a coefficient map. [LIMIT: r = 1, active branch, current-framing broadcasts; α = h a₀, β = h b₀, λ = Λ/h², ρ = p₀/h, κ = k₀/h; h → 0 at fixed K = (H − ε/2)/D, then K → ∞; exponent error O(hK)] With q = (p₀ + k₀ cos² 2δ)/(p₀ + k₀), U = p₀ + k₀ cos 2δ, ā₀ = (a₀ + b₀)/2, d₀ = (a₀ − b₀)/2:
 H = ā₀qU/(1−q), J = d₀U/(1−q), D = (ΛAq/2)[d₀² + ā₀²(1+q)/(1−q)], a = J(1 + c_h)/D.
 Conditions: q < 1 (κ, δ > 0; with endpoint bases only no diffusion limit exists), U > 0, d₀ > 0, and wall-pinned wells, H > ε necessary and H − J > ε sufficient for all |x| ≤ 1. H and J are independent of the active fraction at leading order while D ∝ A, so a ∝ 1/A at finite c_b. The reduced law ẋ = 2ν_K[sinh(ax) − x cosh(ax)] is the form of any bistable variable with linear tilt and Kramers switching (Krause & Bornholdt 2013; Henkel 2016); the contribution is the map and its domain, not the form. [CLOSURE] A bulk O(h) correction to a is delivered under the all-active reduction (C §C6.3; D §C6b, three contributions). [OPEN] The full gated O(h) correction (an all-active stationary population is impossible at finite h), and the skewness coefficient.

R11. What the geometry contributes. [EXACT under a declared surrogate: anchor a, receptivity τ, τ ← τ cos 2(θ − a), a ← θ, acceptance (1 + τ)/2, τ₀ = 1] The surrogate matches every single-message acceptance rate and every mean orientation of the process and differs only in joint laws. Three separating measurements, all one property, Lüders repeatability of an outcome once realized:
 (a) Repeated-framing lock: from I2 with campaign (T, T), the process leaves x = 0 exactly; the surrogate leaves x = ¼; independent draws leave x = ½.
 (b) Outcome–deposit correlation: in R8(c), order (45°,20°), process 0.317 versus surrogate 0.239 λ/ε (32%), identical in the other order.
 (c) Past-45° step: after a 60° framing, a repeated rejection is locked in the process (P = ¾) and not in the surrogate (9/16); with a T seed, R_inv 0.169 versus 0.141 λ/ε (20%).
 All three vanish with seed delay ≫ 1/ε, and none survives in the r = 1 Lux regime, where only q and the increment identity enter. Single-message rates and mean orientations cannot test the rule.

### COMPARATORS
Dodds & Watts 2005 (dose memory with a window; epidemic and critical-mass classes; baseline for R3, R4, R6). Cooke & Yorke 1973 (constant-period SIS with contact reset; R6). Wang, Tang, Zhang & Lai 2015 PRE 92, 012820 (edge-based non-redundant reinforcement with recovery; a different redundancy rule from listener-class habituation; baseline for R2, R5). Lux 1995 §I–II (the r = 1 two-state target of R10; no external source, content or rejection memory). Krause & Bornholdt 2013, Henkel 2016 (the hyperbolic switching form from prescribed rates; R10's form is theirs, its map is not). Carro, Toral & San Miguel 2015 (external signal as direction-dependent herding coefficients; baseline for R8). Hashemi, Gallay & Hongler 2021 (collapse by maturation delay; R2 needs none). Harras & Sornette 2011 (random news with adaptive trust; no promoter). Wang & Busemeyer 2013; Wang, Solloway, Shiffrin & Busemeyer 2014 (the orientation rule, Γ as the sequential-overlap product, the maximally-mixed invariance; cited, not claimed). Miller & Campbell 1959 (primacy/recency under delay; the activation-order examples of v0.5).
Claimed new: the closed-form stationary invasion criterion R7 with its dependence on stance and reconsideration only; the three-class onset R4 and habituation's traversal of it; the finite-budget extinction R2 in this setting; order-dependent invasion through the stance law R8(a) with the two transient channels and their rates; the two-camp structure R9; the coefficient map R10 with its domain; the Lüders-repeatability observables R11. Not new: exponential run-down, branching thresholds, the epidemic/critical-mass split as such, finite-resource extinction as a principle, the hyperbolic switching form, the projection order mechanism.

### WHAT WOULD KILL WHAT
- A memory model without orientation dynamics reproducing R11(a)–(c) kills the geometry claim, not the process.
- A proof that R7 depends on x only through symmetric terms for every β kills the order-through-stance mechanism; the constructions in R8(a) say otherwise at β = ¼.
- A counterexample to the sign condition of R4 class 2 outside the unclipped regime narrows class 2, not the classification.
- Failure of the h → 0 then K → ∞ control in R10 kills the Lux map, not the crowd model.
- Prior art containing a promotional invasion criterion with stance memory as the order channel and burn-out from novelty-weighted memory kills the novelty of the combination.

### OPEN ITEMS, RANKED BY WHETHER CLOSING THEM CHANGES A VERDICT
1. Ignition at finite N or finite seed: the only route by which a prepared background could convert a subcritical I3 into persistence; outside the mean-field specification; a large-deviation or finite-N calculation.
2. R4 class 2 beyond the unclipped regime: the sign of the two-jump coefficient with clipping.
3. R9 exact tails with clipping and the coexistence boundary.
4. R10 skewness coefficient and the gated O(h) correction.
5. R5 crossover in closed form.

### REVIEWER ASSIGNMENT (same packet to four reviewers; none sees another's report)
Reviewer 1, primary: process validity, R1–R6, R9, R10. Reviewer 2, primary: R7, R8, R11, mechanism necessity, prior art. Both address:
1. Is the specification one well-defined process? Name every unstated rule a result needs.
2. Classify R1–R11 as exact, controlled limit, closure-dependent, unsupported or false, with the decisive calculation or counterexample.
3. Do Appendices C and D actually establish what the memo cites them for? Name every discrepancy between them and between them and the memo.
4. Separate activation, invasion and persistence in R8; check the three constructions and the claim that (b) and (c) are transient with rates ρ and ε.
5. Which results survive removal of the orientation dynamics; does R11 identify a prediction a matched memory model cannot reproduce?
6. Nearest existing construction and the precise mathematical difference.
7. For each objection: an example, a limit, the novelty claim, or the process?
8. The minimum unresolved calculations before a market layer is added.

---

## APPENDIX C — ChatGPT derivation, C1–C6 against specification v0.6 (verbatim)

Process specification v0.6: calculations C1–C6

EXACT — overall assessment. Several requested conclusions do not hold under v0.6. In particular, habituation with finitely many framing classes rules out positive long-time activity even in mean field; the proposed C2 bifurcation dichotomy is false; the C4 activation threshold is a deterministic-mean approximation rather than a stochastic threshold; and a prepared background generally does not have a single stationary invasion number. The C6 coefficients can be derived under an explicitly stated all-active reduction, but that reduction does not supply the full gated process's finite-h correction.

EXACT — conventions. Below, EXACT denotes a deduction from v0.6 or an explicitly defined auxiliary process; LIMIT denotes an asymptotic statement with its limiting order stated; CLOSURE denotes an additional reduction; and OPEN denotes either missing specifications or a result not established here. Angles are in degrees. I write s\in\{-1,+1\}, and use
\ell(d)=
\begin{cases}
\displaystyle \frac1\varepsilon
\left[\log\frac{\min(1,d)}{c_b}\right]_+,&d>0,\\[6pt]
0,&d=0.
\end{cases}
Thus \ell(d) is the active lifetime produced by an isolated, positive, magnitude-d deposit into c=0.

EXACT — provenance. The orientation update is the real, two-dimensional projective specialization of the cited quantum question-order framework. That component is attributed to Wang and Busemeyer (2013) and Wang, Solloway, Shiffrin, and Busemeyer (2014); the additional conviction, habituation, activity, and campaign mechanisms are not attributed to those papers.

C1. Kinetic equation and novelty clocks

C1.1 The joint-law equation

EXACT — assumptions: exchangeable initial agents, the declared independent clocks and recipient draws, and the mean-field limit N\to\infty at fixed time. Let
z=(\phi,c,s,\mathbf n,u),\qquad \mu_t=\operatorname{Law}(z_t).
Define the active orientation measure
\nu_{\mu}(d\theta)
=
\int \mathbf 1_{\{|c|>c_b\}}\delta_\phi(d\theta)\,\mu(dz).
Its total mass is A, not one. Let K_\theta denote the complete message kernel: outcome draw, orientation replacement, counter increment, conviction deposit, clipping, and stance update, in the specified order.

EXACT — generator. For a suitable test function F, between campaign pulses,
\begin{aligned}
\mathcal L_\mu F(z)
={}&-\varepsilon c\,\partial_cF(z)
+\rho\bigl[F(Rz)-F(z)\bigr]\\
&+\frac{\kappa}{2}\sum_{\sigma=\pm1}
\bigl[F(Q_\sigma z)-F(z)\bigr]\\
&+\lambda\int
\bigl[K_\theta F(z)-F(z)\bigr]\,\nu_\mu(d\theta),
\end{aligned}
\tag{C1.1}
where R resets \phi to T_s, and Q_\sigma sets \phi=T_s+\sigma\delta. The weak kinetic equation is
\frac{d}{dt}\langle F,\mu_t\rangle
=
\langle\mathcal L_{\mu_t}F,\mu_t\rangle.
\tag{C1.2}

EXACT — delivery normalization. At finite N, agent i's incoming peer hazard is
\lambda\frac{NA-\mathbf 1_{\{|c_i|>c_b\}}}{N-1}.
Consequently, its mean-field hazard is \lambda A. There is no additional factor 1/N, and broadcasts are not delivered to every recipient.

EXACT — campaign impulses. At pulse k, the u=0 subpopulation is unchanged and the u=1 subpopulation is pushed through K_{\theta_k}:
\mu_{t_k^+}
=
\mu_{t_k^-}\big|_{u=0}
+
(K_{\theta_k})_\#
\bigl(\mu_{t_k^-}\big|_{u=1}\bigr).
\tag{C1.3}
For coincident pulses, these maps are composed in index order. No reset or reconsideration occurs between exactly coincident pulses.

C1.2 Class-specific novelty

EXACT — assumptions: a specified framing class j, deterministic mean-field input intensities, and cohort membership conditioned upon. Put
A_j(t)=\nu_{\mu_t}\{\theta:j(\theta)=j\},
and let m_j(t) count campaign pulses of class j up to time t. Conditional on u=b,
\boxed{
E[r^{n_j(t)}\mid u=b]
=
E[r^{n_j(0)}\mid u=b]\,
r^{b\,m_j(t)}
\exp\!\left[-(1-r)\lambda\int_0^t A_j(s)\,ds\right].
}
\tag{C1.4}
The requested expression is the b=1 case.

EXACT — proof. A peer receipt of class j multiplies r^{n_j} by r, regardless of acceptance. Its count is an inhomogeneous Poisson count with cumulative intensity \lambda\int_0^t A_j. The Poisson probability-generating function supplies the exponential factor; campaign receipts supply r^{m_j}.

EXACT — closure boundary. The joint law \mu_t is the state that closes. Equation (C1.4) closes conditional on knowing A_j(t). It does not determine A_j(t). Neither (x,A,B) nor those moments augmented by E[r^{n_j}] generally close, because orientation, residual conviction, stance, and novelty are correlated.

EXACT — what C1 rules out. It rules out replacing one-recipient delivery by broadcast-to-all dynamics, treating campaign pulses as Poisson events, or factoring novelty from the other state variables without an additional closure.

C2. Single-class shot noise, bifurcations, and collapse

C2.0 A finite-input-budget result

EXACT — assumptions: r<1, finitely many reachable framing classes, finite initial conviction, and a finite campaign. For class j, choose a representative \theta_j. The total absolute magnitude of all future unclipped deposits into one agent is bounded by
V_\infty
\le
\sum_j
\frac{\max(\alpha,\beta)\,|\cos2\theta_j|\,
r^{n_j(0)}}{1-r}.
\tag{C2.1}
Clipping cannot increase the absolute size of a deposit's effect. Therefore,
|c(t)|
\le |c(0)|e^{-\varepsilon t}
+\int_0^t e^{-\varepsilon(t-s)}\,dV(s),
\qquad V(\infty)<\infty.
\tag{C2.2}
The right side tends to zero.

LIMIT — order: N\to\infty at fixed time, then t\to\infty; assumptions as above.
\boxed{A(t)\longrightarrow0.}
\tag{C2.3}
Moreover,
\varepsilon\int_0^\infty E|c(t)|\,dt
\le E|c(0)|+EV_\infty,
so
\boxed{
\int_0^\infty A(t)\,dt
\le
\frac{E|c(0)|+EV_\infty}{\varepsilon c_b}.
}
\tag{C2.4}
Thus positive linear invasion and eventual extinction can coexist. Invasion is not persistence.

EXACT — scope of the finite-class assumption. A finite campaign, finitely many initially active orientation classes, and the reset/reconsideration classes generate only finitely many classes. A continuously oriented but initially silent I2 population does not itself violate this condition: a message overwrites orientation before creating activity. A continuously oriented initially active population does violate it.

C2(a). Exact transient solution and small-input asymptotics

EXACT — literal I1 experiment. With I1, one class T=0, \kappa=0, and no campaign or active seed,
A(t)=0,\qquad c(t)=0.
A nontrivial trajectory requires an explicitly supplied campaign, seed, or external arrival intensity.

EXACT — assumptions for the shot-noise calculation: all messages are T, the recipient remains an optimist, and the peer intensity is a prescribed function a(t). Let n_0 be the pre-existing class count. Conditional on ordered receipt times
0<t_1<\cdots<t_k<t,
define
z_0=c_0,\qquad
z_i=\min\!\left\{1,\,
e^{-\varepsilon(t_i-t_{i-1})}z_{i-1}
+\alpha r^{n_0+i-1}\right\},
\tag{C2.5}
and
C_t=e^{-\varepsilon(t-t_k)}z_k.
Writing H(t)=\int_0^t a(s)\,ds, the exact activation probability is
\boxed{
P_t(c>c_b)
=
e^{-H(t)}
\sum_{k=0}^{\infty}
\int_{0<t_1<\cdots<t_k<t}
\left[\prod_{i=1}^k a(t_i)\,dt_i\right]
\mathbf 1_{\{C_t>c_b\}}.
}
\tag{C2.6}
This includes clipping at every receipt, not merely clipping the final sum.

EXACT — controlled quadrature. Truncating (C2.6) after k=K has error at most
\Pr\{\operatorname{Poisson}(H(t))>K\}.
\tag{C2.7}
For mean-field feedback, substitute a(t)=\lambda A(t), average over the specified post-campaign initial law, and iterate the resulting Volterra map. Coupling two prescribed arrival intensities gives
|\mathcal F(A)(t)-\mathcal F(\widetilde A)(t)|
\le \lambda\int_0^t|A(s)-\widetilde A(s)|\,ds.
\tag{C2.8}
Consequently, successive quadratures converge on every finite time interval, with the usual factorial Picard bound. This supplies a controlled computation of A(t), without replacing random counters by their means.

EXACT — small-input expansion at fixed finite t>0, c_0=0, constant input \nu, and first future dose d=\alpha r^{n_0}>0. The minimum number of receipts capable of activating is
\boxed{
m_*=
\min\left\{k\ge1:
d\frac{1-r^k}{1-r}>c_b\right\},
\qquad r<1.
}
\tag{C2.9}
If d/(1-r)\le c_b, activation is impossible. Otherwise,
P_t(c>c_b)
=
C_{m_*}(\varepsilon t,d,r,c_b)
\left(\frac{\nu}{\varepsilon}\right)^{m_*}
+
O\!\left((\nu/\varepsilon)^{m_*+1}\right),
\tag{C2.10}
where C_{m_*}>0 is the ordered-time integral in (C2.6).

EXACT — correction to the proposed exponent. The formula
m=\left\lfloor\frac{c_b}{\alpha r^{n-1}}\right\rfloor+1
is the frozen-dose formula, not the habituating-burst formula. For example,
d=0.4,\qquad r=0.5,\qquad c_b=0.65
gives deposits 0.4,0.2,0.1,\ldots. Two receipts cannot activate, but three sufficiently close receipts can:
m_*=3,\qquad m_{\rm frozen}=2.
At r=1, the geometric sum becomes kd, and the proposed floor formula is correct.

C2(b). Stationary self-consistency and transition class

LIMIT — constant external input \nu>0, r<1, then t\to\infty. The conviction marginal converges to \delta_0. The full process with finite-valued counters has no stationary law at positive input, because counters keep increasing. Therefore a positive stationary equation
A=M P_{\lambda A}(c>c_b)
cannot describe the habituating process's long-time branch.

EXACT — assumptions for a stationary conviction marginal: r=1, constant input \nu, and positive dose d=\alpha. For 0<c<1, its density f_\nu satisfies
0=\varepsilon(cf_\nu)'-
\nu f_\nu(c)+
\nu\mathbf 1_{\{c>d\}}f_\nu(c-d),
\tag{C2.11}
with
\varepsilon f_\nu(1-)
=
\nu\int_{\max(0,1-d)}^1f_\nu(c)\,dc,
\qquad
\int_0^1f_\nu(c)\,dc=1.
\tag{C2.12}
Setting a=\nu/\varepsilon, a method-of-steps representation is
f_\nu(c)
=
c^{a-1}
\left[
C-a\int_d^c u^{-a}f_\nu(u-d)\,du
\right],
\tag{C2.13}
where the integral is absent for c<d. Hence
P_\nu(c>c_b)=\int_{c_b}^1 f_\nu(c)\,dc
\tag{C2.14}
is an exact stationary quadrature.

EXACT — self-consistency. For the full I1 crowd, M=1. More generally, an M<1 equation requires a declared invariant responsive pool and a permanently nonresponsive remainder—for example, a T^\perp remainder with \beta=0,\kappa=0. With that declaration,
A=M P_{\lambda A},\qquad
\lambda(\nu)=\frac{\nu}{M P_\nu}.
\tag{C2.15}

EXACT — m\ge2. At r=1,
P_\nu\sim C_m(\nu/\varepsilon)^m,
\qquad
m=\left\lfloor\frac{c_b}{d}\right\rfloor+1.
When m\ge2, \lambda(\nu)\to\infty both as \nu\downarrow0 and as \nu\to\infty. It therefore has an interior minimum. A nondegenerate minimum is a saddle-node; nondegeneracy and uniqueness of the minimum are additional properties, not consequences of the exponent alone.

EXACT — counterexample to "saddle-node iff m\ge2." Take
r=1,\quad d=0.4,\quad c_b=0.39,\quad
\varepsilon=1,\quad M=1.
Here m=1. Because 2d<1, clipping does not affect the two-receipt coefficient. Writing
\ell=\log(d/c_b),
the stationary small-\nu expansion is
\boxed{
P_\nu
=
\nu\ell+
\nu^2\left(\frac{\pi^2}{12}-\frac{\ell^2}{2}\right)
+o(\nu^2).
}
\tag{C2.16}
The positive two-receipt contribution is
\frac12\int_0^1\frac{du}{u}
\int_{1-u}^1\frac{dv}{v}
=\frac{\pi^2}{12};
the overlap subtraction is \ell^2/2.

EXACT — numerical consequences, rounded.
\ell=0.025317808,\qquad
\frac{\pi^2}{12}-\frac{\ell^2}{2}=0.822146538>0,
and
\lambda_c=\ell^{-1}=39.4978902.
Therefore P_\nu/\nu initially increases, so \lambda(\nu) initially decreases below \lambda_c, before eventually increasing to infinity. There is a critical-mass fold with m=1.

EXACT — conclusion for C2(b). A one-shot activating dose gives nonzero linear susceptibility. It does not guarantee a forward transition or exclude a saddle-node and coexistence. The stated "transcritical iff m=1, saddle-node iff m\ge2" classification is false.

C2(c). A(t), accumulated conviction, and the collapse index

EXACT — mean-field trajectory in quadrature. Equation (C2.6), with the substitution and convergent iteration in (C2.8), gives A(t) for any declared post-campaign initial law. For example, one T pulse applied to an I1 cohort of fraction f gives
A(t)
=
f\,P^{\,\min(1,\alpha),\,1}_{\lambda A}(t)
+(1-f)\,P^{\,0,\,0}_{\lambda A}(t).
\tag{C2.17}
The superscripts specify initial conviction and initial class count.

EXACT — history-dependent residual correction. Before clipping, conditional on receipt times,
c_k
=
c_0e^{-\varepsilon t_k}
+
\alpha r^{n_0+k-1}
\underbrace{
\sum_{j=1}^k
r^{-(k-j)}e^{-\varepsilon(t_k-t_j)}
}_{F_k}.
\tag{C2.18}
The factor F_k\ge1 is the exact accumulated-conviction correction. It is random under Poisson delivery.

EXACT — no deterministic "true k_{\rm acc}." The last active receipt index
K_{\rm last}=\sup\{k:c_k>c_b\}
\tag{C2.19}
is a random variable, not a common population index. Arbitrarily many receipts can occur during the residual active lifetime following an early strong deposit. Thus a dose becoming individually subthreshold does not imply immediate collapse at that count.

EXACT — a sufficient permanent-silence test for the one-camp process. At current state (c,n),
c+\frac{\alpha r^n}{1-r}\le c_b
\tag{C2.20}
rules out any future activation. Its converse does not guarantee activation, because arrival timing and decay still matter.

CLOSURE — equally spaced receipts, used only to exhibit a deterministic correction factor. Let the gap be \Delta, put w=e^{-\varepsilon\Delta}, and suppose clipping is inactive. Then
c_k
=
\alpha\frac{r^k-w^k}{r-w}
=
\alpha r^{k-1}
\frac{1-(w/r)^k}{1-w/r},
\qquad r\ne w,
\tag{C2.21}
while c_k=\alpha k r^{k-1} when r=w. For w<r, the late correction factor is
F_\infty=\frac{1}{1-w/r}.
\tag{C2.22}
When w\ge r, no finite constant correction factor of this form applies.

CLOSURE — numerical comparison within that periodic-receipt model. With
\alpha=0.6,\quad r=0.8,\quad
w=0.5,\quad c_b=0.3,\quad \varepsilon=1,
clipping never occurs. The last individually activating dose is receipt 4, whereas
c_8=0.327732>0.3,\qquad c_9=0.264529<0.3.
Thus the last active receipt is 8, and the first accumulated-conviction failure is 9. The asymptotic residual multiplier is 8/3. These are periodic-clock results, not Poisson-process collapse indices.

C2(d). Boundary checks

LIMIT — order: mean field first, then r\downarrow0 at fixed time; assumptions: T-only optimism, \alpha=1, and an initial campaign activating fraction f. Only the first class exposure deposits conviction. Let S(t) be the never-exposed fraction. The limiting stopwatch process satisfies
S'(t)=-\lambda A(t)S(t),
\boxed{
A(t)
=
f\,\mathbf 1_{\{t<L\}}
+
\int_{\max(0,t-L)}^t
\lambda A(s)S(s)\,ds.
}
\tag{C2.23}
An agent is active for L after its first exposure and cannot be refreshed by later exposures.

EXACT — r=1,\alpha=\beta=1,\kappa=0, in the invariant two-orientation population with conviction sign matching orientation and stance. Every peer receipt resets |c| to one. After initial-condition effects have expired,
\boxed{
A(t)
=
1-\exp\!\left[-\lambda\int_{t-L}^t A(s)\,ds\right].
}
\tag{C2.24}
The stationary equation is A=1-e^{-\lambda LA}. This is the applicable renewal check.

OPEN — identification with "Result 4." The text of Result 4 was not supplied. Equation (C2.24) is derived from v0.6 under the stated invariant-state assumptions; equivalence to an unspecified Result 4 cannot be checked.

EXACT — what C2 rules out. It rules out a positive habituating stationary branch with finitely many classes, the frozen-dose exponent for a genuinely habituating burst, the proposed bifurcation dichotomy, and a universal deterministic collapse count.

C3. Stationary and prepared-background invasion

C3(a). The stationary next-generation operator

EXACT — assumptions: I3, fresh counters in every reachable class, \rho,\kappa>0, stance fraction p=p_+, and linearization about zero activity. Put
v=\rho+\kappa,\qquad
\zeta=\frac{\rho+\kappa\cos2\delta}{v},
\qquad x=2p-1.
A message of angle \theta is accepted by the background with probability
\boxed{
p_{\rm acc}(\theta)
=\frac{1+\zeta x\cos2\theta}{2}.
}
\tag{C3.1}
This follows by averaging \cos^2(\theta-\phi) over I3.

EXACT — important correction to "single class." With \kappa>0 and current-orientation broadcasts, the single class T is not invariant. A T seed generates the finite angle set
\mathcal S=\{0,\delta,-\delta,90,90+\delta,90-\delta\}.
\tag{C3.2}
An operator retaining only T messages would change the declared delivery rule.

EXACT — birth types. Index a child type by b=(\theta,o), with o acceptance or rejection. Its post-message conviction is
c_b^*=
\begin{cases}
\operatorname{clip}(\alpha\cos2\theta),&o=A,\\
\operatorname{clip}(-\beta\cos2\theta),&o=R.
\end{cases}
Keep only types with |c_b^*|>c_b. Their birth orientation is
\phi_b=\theta\quad\text{or}\quad\theta+90,
their stance is \operatorname{sign}(c_b^*), and their lifetime is
\ell_b=\frac1\varepsilon\log\frac{|c_b^*|}{c_b}.

EXACT — parent occupation measure. Define
h_v(\ell)=\frac{1-e^{-v\ell}}{v}.
A parent of type b, receiving no further peer message at linear order, has lifetime orientation occupation measure
W_b(d\eta)
=
h_v(\ell_b)\delta_{\phi_b}(d\eta)
+
\bigl[\ell_b-h_v(\ell_b)\bigr]\pi_{s_b}(d\eta),
\tag{C3.3}
where \pi_s is the I3 orientation law conditional on stance.

EXACT — next-generation matrix and criterion.
\boxed{
K_{b',b}
=
\lambda\,
W_b(\{\theta_{b'}\})\,
p_{o_{b'}}(\theta_{b'}),
\qquad
R_{\rm inv}=\operatorname{spr}(K_{\rm reachable}).
}
\tag{C3.4}
The reachable restriction is taken from the declared T seed. The stationary linearization is supercritical for R_{\rm inv}>1, subcritical for R_{\rm inv}<1, and critical at equality.

EXACT — proof of the linearization. A parent broadcasts at rate \lambda during its active lifetime. Equation (C3.3) gives its expected time at each transmitting angle, and (C3.1) gives the corresponding background outcome probabilities. Peer receipts into already active parents and repeat receipts into previously perturbed background agents contribute only at second order in seed mass.

EXACT — dependence on the background. Under the fresh-counter I3 declaration, the background enters through p, equivalently x, and the specified reset/reconsideration parameters. No preparation product \Gamma remains. The spectral radius need not depend strictly on p for every parameter choice; symmetries can remove that dependence. Nonfresh or stance-correlated counters require additional background information.

EXACT — useful \kappa=0 reduction. With a common pre-counter n_0, let
\ell_\alpha=\ell(\alpha r^{n_0}),\qquad
\ell_\beta=\ell(\beta r^{n_0}).
The nonzero reproduction spectrum is represented by
K_{\rm camp}
=
\lambda
\begin{pmatrix}
p\ell_\alpha&p\ell_\beta\\
(1-p)\ell_\beta&(1-p)\ell_\alpha
\end{pmatrix},
\tag{C3.5}
whose full Perron root is
\frac{\lambda}{2}
\left[
\ell_\alpha+
\sqrt{x^2\ell_\alpha^2+(1-x^2)\ell_\beta^2}
\right].
\tag{C3.6}
When \ell_\beta=0, the matrix is reducible. A positive T seed reaches only the positive block, giving
\boxed{R_{\rm inv}=\lambda p\ell_\alpha,}
\tag{C3.7}
not the larger eigenvalue of an inaccessible block.

C3(b). Prepared, relaxing backgrounds

EXACT — assumptions: the campaign leaves a silent background, and the seed is introduced at time t_0. Let \mu_t^0 be the no-seed background law. For \kappa=0, its conviction decays as c_0e^{-\varepsilon t}, while its orientation law, conditional on the prepared state, is
e^{-\rho t}\delta_{\phi_0}
+
(1-e^{-\rho t})\delta_{T_s}.
\tag{C3.8}
Correlations with c_0,s,\mathbf n must be retained.

EXACT — time-dependent birth kernel. Let \mathcal H_{\mu_t^0}^\theta be the distribution of active children produced by one \theta message into \mu_t^0. Then
\mathcal K(t,a;b,db')
=
\lambda\mathbf 1_{\{a<\ell_b\}}
\int
P_a^{s_b}(\phi_b,d\theta)\,
\mathcal H_{\mu_t^0}^\theta(db').
\tag{C3.9}
The linear birth measure obeys the nonautonomous renewal equation
b(t)=b_{\rm seed}(t)
+\int_0^{t-t_0}\mathcal K(t,a)\,b(t-a)\,da.
\tag{C3.10}

EXACT — seed-arrival dependence. A well-defined first-generation quantity is
R_1(t_0)
=
\lambda\int_0^{\ell_{\rm seed}}
\int P_a^{s_{\rm seed}}(\phi_{\rm seed},d\theta)\,
\Pr_{\mu_{t_0+a}^0}
\{\text{the message creates activity}\}\,da.
\tag{C3.11}
In general, R_1(t_0)>1 is neither a necessary nor a sufficient criterion for asymptotic invasion.

EXACT — explicit relaxing-orientation special case. Suppose residual conviction is zero, \beta is subthreshold, all activating children have lifetime \ell_\alpha, and
q_T(t)=p+(q_T(0)-p)e^{-\rho t}.
For a T seed of lifetime \ell_{\rm seed},
R_1(t_0)=
\lambda\left[
p\ell_{\rm seed}
+
(q_T(0)-p)e^{-\rho t_0}
\frac{1-e^{-\rho\ell_{\rm seed}}}{\rho}
\right].
\tag{C3.12}
The frozen-background diagnostic is instead
R_{\rm fr}(t_0)=\lambda\ell_\alpha q_T(t_0).
\tag{C3.13}
These are different objects.

LIMIT — order: mean field, infinitesimal-seed linearization, then long time. If the background converges to I3 and the seed at t_0 has a nonzero path into the limiting reproductive class, the asymptotic threshold is the limiting stationary spectral-radius threshold. Seed arrival changes transient amplification. A seed that dies before reaching any reproducing class is an accessibility exception; it cannot be rescued by a later supercritical limiting background.

C3(c). Reviewer constructions

EXACT — numerical conventions. The table uses f=1, T=0, and \varepsilon=1. Case (i) uses I1; cases (ii)–(iv) use I2. Seeds are infinitesimal T-oriented, c=1,s=+ seeds. Displayed numbers are rounded. "Frozen" quantities are explicitly not substituted for the nonautonomous criterion.

Construction (i): persistent orientation preparation

EXACT — stated parameters, \rho=\kappa=0. Every campaign history is silent. The T class is fresh, and any accepted T seed message clips conviction to one. Define
\Gamma=
\cos2\theta_1
\prod_{k=2}^3\cos2(\theta_k-\theta_{k-1}),
so that
q_T=\frac{1+\Gamma\cos2\theta_3}{2},
\qquad
R_{\rm inv}=\lambda q_T\log(1/0.95).
\tag{C3.14}

Order	Status	q_T	R_{\rm inv}/\lambda	Channel
10,20,30	EXACT	0.707442366	0.036287050	\Gamma
10,30,20	EXACT	0.759089355	0.038936194	\Gamma
20,10,30	EXACT	0.637858566	0.032717867	\Gamma

EXACT — interpretation. All three have x=1. Residual deposits do not affect the offspring lifetime because the accepted dose is one. This construction isolates the persistent orientation-preparation channel.

Construction (ii): stance after relaxation

EXACT — stated zero-gap parameters, followed by relaxation to I3. The 50^\circ and 140^\circ messages share a framing class, so the second such receipt has half the novelty. Direct outcome enumeration gives
p_+(40,50,140)=\frac12,
p_+(40,140,50)
=\frac{1+\cos^2 10^\circ}{2}
=0.984923155.
\tag{C3.15}
The campaign remains silent. After relaxation, T acceptance is determined by stance, the fresh accepted T dose gives lifetime \log2, and the rejected dose is subthreshold.

Order	Status	x	R_{\rm inv}/\lambda	Channel
40,50,140	EXACT after relaxation	0	0.346573590	Stance imbalance
40,140,50	EXACT after relaxation	0.969846310	0.682696708	Stance imbalance

EXACT — interpretation. The geometric preparation product is not the invasion statistic after relaxation. The order dependence survives through the stance law.

Construction (iii): residual outcome–deposit correlation

EXACT — stated parameters. Put
d=0.6\cos40^\circ=0.459626666,\qquad
q=\cos^225^\circ.
The post-campaign joint laws are
(45,20):
\quad
(\phi,c)=
\begin{cases}
(20,d),&1/2,\\
(110,0),&1/2,
\end{cases}
\tag{C3.16}
and
(20,45):
\quad
\begin{array}{c|c}
(\phi,c)&\text{probability}\\ \hline
(45,d)&q/2\\
(135,d)&(1-q)/2\\
(45,0)&(1-q)/2\\
(135,0)&q/2.
\end{array}
\tag{C3.17}
Both have x=1 and unconditional T-acceptance probability 1/2.

EXACT — calendar-time lifetimes and weights.
\ell_0=\log1.2,
\qquad
\ell_H(t)
=
\log\frac{\min(1,\,0.6+d e^{-t})}{0.5}.
\tag{C3.18}
For 45,20,
w_H=\tfrac12\cos^220^\circ=0.441511111,
\qquad w_L=\tfrac12-w_H.
For 20,45,
w_H=w_L=\tfrac14.
The exact linear activity equation is
A(t)=A_{\rm seed}(t)
+\lambda\int_{t_0}^t A(s)
\left[
w_H\mathbf 1_{\{t-s<\ell_H(s)\}}
+w_L\mathbf 1_{\{t-s<\ell_0\}}
\right]ds.
\tag{C3.19}

Order	Status of asymptotic criterion	R_\infty/\lambda	R_{\rm fr}(0)/\lambda, diagnostic only	Channel
45,20	LIMIT	0.091160778	0.316695967	Outcome–deposit correlation
20,45	LIMIT	0.091160778	0.218867184	Outcome–deposit correlation

LIMIT — order: mean field, linearization, then t\to\infty. Since \ell_H(t)\to\ell_0,
\boxed{
R_\infty=\frac{\lambda}{2}\log1.2
}
\tag{C3.20}
for both orders. The frozen numbers differ, but the asymptotic threshold does not.

EXACT — a genuinely nonautonomous numerical separator. For a seed introduced immediately with lifetime L=\log2, the expected number of second-generation agents is
E Z_2
=
\frac{\lambda^2}{2}
\int_0^L
\left[w_H\ell_H(s)+w_L\ell_0\right]ds.
\tag{C3.21}
The two orders give
E Z_2(45,20)=0.0976502474\,\lambda^2,
E Z_2(20,45)=0.0689974669\,\lambda^2.
\tag{C3.22}
This is a transient branching difference calculated without freezing the background.

Construction (iv): missing parameters and an explicit completion

OPEN — original construction. The stated case omits c_b,c_h,\varepsilon,\kappa, pulse gaps, and the precise seed timing relative to relaxation. It therefore has no unique numerical R_{\rm inv}. In particular, a campaign that already activates a positive population cannot be treated as a silent prepared background.

EXACT — declared completion, denoted (iv^*). Take
c_b=0.95,\quad c_h=0.01,\quad
\varepsilon=1,\quad\kappa=0,
put all three pulses at time zero, and take \rho\to\infty after the coincident pulse composition. Introduce the seed after that vanishing reset layer. The post-campaign deposit distributions are
\begin{array}{c|rrrr}
(T,T,30):c&0.9&0.575&-0.075&-0.4\\
\Pr&0.375&0.125&0.125&0.375
\end{array}
\tag{C3.23}
and
\begin{array}{c|rrrrr}
(T,30,T):c&0.9&0.575&0.25&-0.075&-0.4\\
\Pr&0.28125&0.125&0.1875&0.125&0.28125.
\end{array}
\tag{C3.24}
All agents are silent, and all have n_T=2.

EXACT — resulting kernel. The next accepted T dose is 0.45(0.5)^2=0.1125. Only the c=0.9 group can activate. Its offspring lifetime at calendar time t is
\ell_4(t)=
\left[
\log\frac{\min(1,\,0.9e^{-t}+0.1125)}{0.95}
\right]_+.
\tag{C3.25}
The birth kernel is \lambda w\,\mathbf 1_{\{a<\ell_4(t)\}}, with w=0.375 or 0.28125.

Order in (iv^*)	Status	x	R_\infty/\lambda	R_{\rm fr}(0)/\lambda	Channel
T,T,30	EXACT kernel; LIMIT criterion	0	0	0.019234985	Residual outcome–deposit distribution
T,30,T	EXACT kernel; LIMIT criterion	0.1875	0	0.014426239	Residual outcome–deposit distribution

EXACT — finite end of linear reproduction in (iv^*). No new births occur after
t_*=\log\frac{0.9}{0.95-0.1125}=0.071973500.
All linear activity is gone by t_*+L=0.123266794. The order with larger x has the smaller transient reproductive opportunity here; x alone is insufficient.

EXACT — cohort fractions other than one. For (i), replace q_T by (1-f)+fq_T. For (ii), replace p_+ by (1-f)+fp_+. For (iii), replace w_H by fw_H and w_L by 1/2-fw_H. In (iv^*), multiply the high-deposit weights by f; the noncohort's fresh 0.45 dose remains subthreshold.

EXACT — what C3 rules out. It rules out a universal \Gamma-based invasion statistic, a one-angle operator when reconsideration changes broadcast framing, and using frozen prepared-background numbers as asymptotic invasion thresholds.

C4. The two-camp branch

C4.1 Exact stationary response

EXACT — assumptions: r=1,\kappa=0, and an invariant two-camp initial law. The positive camp has \phi=0,s=+,c\ge0, mass p; the negative camp has \phi=90,s=-,c\le0, mass 1-p. Reset is harmless under this declaration. Put y=|c|.

EXACT — jump rates. Positive agents receive magnitude-\alpha reinforcement at rate \lambda A_+ and magnitude-\beta reinforcement at rate \lambda A_-. Negative agents receive magnitude-\alpha reinforcement at rate \lambda A_- and magnitude-\beta reinforcement at rate \lambda A_+. Thus a rejected T^\perp message does refresh an optimist by +\beta.

EXACT — stationary response function. Let
F(u,v;\alpha,\beta)
=
\Pr_{\rm stat}\{y>c_b\}
for the capped process with jumps \alpha at rate u, jumps \beta at rate v, and decay -\varepsilon y. Its density satisfies
\begin{aligned}
0={}&\varepsilon(yf)'-(u+v)f(y)\\
&+u\mathbf 1_{\{y>\alpha\}}f(y-\alpha)
+v\mathbf 1_{\{y>\beta\}}f(y-\beta),
\end{aligned}
\tag{C4.1}
with clipped-arrival boundary flux
\varepsilon f(1-)
=
u\int_{\max(0,1-\alpha)}^1f(y)\,dy
+
v\int_{\max(0,1-\beta)}^1f(y)\,dy.
\tag{C4.2}
Zero-size jumps are omitted. Normalization and method-of-steps integration determine F.

EXACT — the skeptic conviction is not a deterministic constant. Under fixed positive-camp forcing alone, the unclipped mean is
E y=\frac{\lambda\beta A_+}{\varepsilon}.
\tag{C4.3}
For the clipped process,
\varepsilon E y
=
\lambda A_+\,E[\min(\beta,1-y)].
\tag{C4.4}
Neither equation identifies P(y>c_b) with a threshold on the mean.

EXACT — activation condition. For every
\beta>0,\qquad \lambda A_+>0,
a sufficiently tight finite cluster of rejected T messages produces y>c_b with positive probability. Long gaps also have positive probability. Therefore
\boxed{
0<F(0,\lambda A_+;\alpha,\beta)<1
}
\tag{C4.5}
at every finite positive forcing rate.

CLOSURE — candidate mean threshold.
\lambda\beta A_+>\varepsilon c_b
is the threshold obtained by replacing random conviction by its unclipped stationary mean. It is not an activation threshold of v0.6.

C4.2 Coupled fixed points and their parameter region

EXACT — mean-field stationary marginal equations; N\to\infty precedes the stationary/long-time analysis.
\boxed{
\begin{aligned}
A_+&=p\,F(\lambda A_+,\lambda A_-;\alpha,\beta),\\
A_-&=(1-p)\,F(\lambda A_-,\lambda A_+;\alpha,\beta).
\end{aligned}}
\tag{C4.6}
These are exact fixed-point equations, with F supplied by (C4.1)–(C4.2).

EXACT — region with an active skeptic pool. If 0<p<1 and \beta>0, every positive fixed point has both A_+>0 and A_->0. There is no separate positive forcing threshold at which the skeptic pool first becomes exactly active. If \beta=0, a one-camp branch is possible.

EXACT — quadrature parametrization of all positive branches. Write
\nu=\lambda(A_++A_-),\qquad
z=\frac{A_+}{A_++A_-}.
Define
F_+=F(\nu z,\nu(1-z)),\qquad
F_-=F(\nu(1-z),\nu z),
S=pF_++(1-p)F_-.
Every positive branch is given by
z=\frac{pF_+}{S},
\qquad
\lambda=\frac{\nu}{S},
\qquad
(A_+,A_-)=(pF_+,(1-p)F_-).
\tag{C4.7}
This is a scalar consistency equation in z, together with stationary quadratures, rather than an assumed deterministic-conviction closure.

C4.3 Kinetic stability

EXACT — assumptions: fixed camp masses and an equilibrium whose fixed-input conviction processes are ergodic. Let P_i(t) be the fixed-input semigroup in camp i, let \pi_i be its stationary law, and set g(y)=\mathbf 1_{\{y>c_b\}}. An additional jump of size d_{ij}, where
d_{++}=d_{--}=\alpha,\qquad d_{+-}=d_{-+}=\beta,
has response kernel
k_{ij}(t)
=
\int\pi_i(dy)
\left[
P_i(t)g(\min(1,y+d_{ij}))
-
P_i(t)g(y)
\right].
\tag{C4.8}
Monotone coupling gives k_{ij}(t)\ge0.

EXACT — characteristic equation. The linearized activity equation is a convolution equation, not generally a two-dimensional ordinary differential equation. Its characteristic equation is
\det\!\left[
I-\lambda\,\operatorname{diag}(p,1-p)\,
\widehat k(z)
\right]=0.
\tag{C4.9}
Define the static susceptibility matrix
J=
\lambda\,\operatorname{diag}(p,1-p)
\int_0^\infty k(t)\,dt.
\tag{C4.10}
It equals the derivative of the fixed-point map in (C4.6).

EXACT — local stability criterion.
\boxed{
\operatorname{spr}(J)<1\Rightarrow\text{linear stability},\qquad
\operatorname{spr}(J)>1\Rightarrow\text{linear instability}.
}
\tag{C4.11}
At equality there is a zero-frequency marginal mode, and nonlinear terms must be examined. Positivity of the kernels gives the criterion: for \Re z\ge0, the absolute transform is bounded by its zero-frequency transform; when the zero-frequency Perron root exceeds one, a positive real characteristic root exists.

EXACT — fully explicit check, \alpha=\beta=1. Let A=A_++A_-. Then
A=1-e^{-\lambda LA},\qquad
A_+=pA,\quad A_-=(1-p)A.
\tag{C4.12}
A unique positive branch exists exactly when \lambda L>1. It is stable because
\lambda L(1-A)<1.
The zero branch is stable below threshold and unstable above it.

LIMIT — r<1, finite classes, N\to\infty first and t\to\infty second. Both types of receipt advance the same framing-class counter. The finite-input-budget result applies, and no positive stationary two-camp branch survives.

OPEN — remaining classification. A closed elementary classification of every possible fold and degenerate point for arbitrary \alpha,\beta,c_b,p is not supplied. Equations (C4.1), (C4.7), and (C4.11) do supply exact fixed-point and local-stability tests.

C5. Geometry-separating quantities

C5.0 Completing the surrogate definition

EXACT — additional declaration needed for a unique comparison. The surrogate needs an initial (a,\tau) law and a broadcast rule. I use the pure-state lift
a_0=\phi_0,\qquad \tau_0=1,
and broadcast angle a. On each receipt,
\tau\leftarrow\tau\cos2(\theta-a),\qquad a\leftarrow\theta,
then draw a conviction-deposit outcome with probability (1+\tau)/2. These outcome coins do not condition or reset (a,\tau). All tests below have \rho=\kappa=0.

EXACT — alternative initialization. The homogeneous mixed initialization \tau_0=0 is a different surrogate initialization, even though it gives the same initial ensemble acceptance probability. Where relevant, its result is stated separately.

C5(a). Repeated-framing lock

EXACT — parameters.
I2,\quad f=1,\quad
\alpha=0.6,\quad\beta=0.2,\quad r=0.5,\quad
c_h=0.01,\quad c_b=0.95,\quad\varepsilon=1,
with the zero-gap campaign (T,T).

EXACT — process. The first outcome is equally likely to be acceptance or rejection. The second is perfectly repeatable:
P(AA)=P(RR)=\frac12,\qquad
P(AR)=P(RA)=0.
Final conviction is 0.9 or -0.3, so
\boxed{x_{\rm process}=0.}
\tag{C5.1}

EXACT — pure-state-lift surrogate. Conditional on the initial angle, both conviction coins have probability q=\cos^2\phi_0. Consequently,
P(AA)=P(RR)=E[q^2]=\frac38,
\qquad
P(AR)=P(RA)=\frac18.
The mixed histories finish at c=0.5 and c=0.1, both positive. Thus
\boxed{x_{\rm surrogate}=\frac14.}
\tag{C5.2}
The stated separation is 0.25.

EXACT — independent fair-coin comparison. With homogeneous \tau_0=0, all four histories have probability 1/4, giving x=0.5. Neither surrogate preserves selective repeatability.

C5(b). Outcome–deposit correlation

EXACT — parameters. Use the C3(iii) experiment with
r=0.5,\quad c_h=0.01,\quad f=1.
The process joint laws are (C3.16)–(C3.17). Put
g=\cos50^\circ,\qquad k=\cos40^\circ,\qquad
d=0.6\cos40^\circ.

EXACT — surrogate joint law. After either order, \tau has the scaled arcsine law
\mu_g(d\tau)=
\frac{\mathbf 1_{\{|\tau|<g\}}}{\pi\sqrt{g^2-\tau^2}}\,d\tau.
For 45,20, the final anchor is a=20, and
P(c=d,\tau\in d\tau)=\frac{1+\tau}{2}\mu_g(d\tau).
\tag{C5.3}
For 20,45, the final anchor is a=45, and
P(c=d,\tau\in d\tau)=\frac{1+\tau/g}{2}\mu_g(d\tau).
\tag{C5.4}
The complementary mass has c=0.

EXACT — T-acceptance/deposit weights. Updating the surrogate with the incoming T message gives
w_H^{\rm sur}(45,20)
=
\frac14\left(1+\frac{k g^2}{2}\right)
=0.289563889,
w_H^{\rm sur}(20,45)=\frac14.
\tag{C5.5}
The corresponding process weights are 0.441511111 and 0.25. All four total T-acceptance probabilities are 1/2.

Model and order	Status	R_{\rm fr}(0)/\lambda, diagnostic	E Z_2/\lambda^2, actual nonautonomous quantity
Process, 45,20	EXACT formulas	0.316695967	0.097650247
Surrogate, 45,20	EXACT under declared surrogate	0.239077433	0.074916786
Process, 20,45	EXACT formulas	0.218867184	0.068997467
Surrogate, 20,45	EXACT under declared surrogate	0.218867184	0.068997467

EXACT — numerical separation. For 45,20, the process–surrogate difference is
0.0776185344\,\lambda
in the frozen diagnostic and
\boxed{0.0227334612\,\lambda^2}
\tag{C5.6}
in expected second-generation count. The latter is obtained from the actual time-dependent kernel.

LIMIT — order: mean field, linearization, then long time. All four share
R_\infty=\frac{\lambda}{2}\log1.2.
The separator is transient outcome–deposit correlation, not a different eventual invasion threshold.

EXACT — homogeneous mixed surrogate. With \tau_0=0, both orders have w_H=1/4, so both equal the 20,45 row. The initialization convention therefore matters quantitatively.

C5(c). A sign-reversal step

EXACT — parameters.
I1,\quad f=1,\quad
\alpha=\beta=0.2,\quad r=1,\quad
c_h=0.01,\quad c_b=0.9,\quad\varepsilon=1,
with zero-gap campaign
(0,60,60).
The 60^\circ step has
\cos120^\circ=-\frac12.

EXACT — process. After the first 60^\circ message, orientation is 60^\circ with probability 1/4 and its complement 150^\circ with probability 3/4. The repeated 60^\circ outcome is then locked:
P(R_2,R_3)=\frac34.
\tag{C5.7}

EXACT — surrogate. After that step, \tau=-1/2; repetition leaves it unchanged. Each conviction coin rejects with probability 3/4, but they are not selectively locked:
P(R_2,R_3)=\left(\frac34\right)^2=\frac{9}{16}.
\tag{C5.8}
The difference is
\boxed{\frac{3}{16}=0.1875.}

EXACT — interpretation. The negative cosine factor by itself is not a marginal separator: the surrogate also represents a complement-biased ensemble. The separation arises because the process conditions the subsequent state on the realized outcome, whereas the declared surrogate does not.

EXACT — what C5 establishes. C5 supplies numerical differences in stance, joint outcome probabilities, and actual finite-generation reproduction. It does not establish different asymptotic invasion thresholds for the relaxing-deposit example.

C6. Diffusion and two-state limit

C6.1 Definitions and coefficient map

EXACT — additional definitions. The quantities q,U,\bar a_0,d_0 were not defined in the supplied specification. The natural definitions under which the requested map can be derived are
\bar a_0=\frac{a_0+b_0}{2},\qquad
d_0=\frac{a_0-b_0}{2},
v_0=p_0+k_0,\qquad
U=p_0+k_0\cos2\delta,
q=\frac{p_0+k_0\cos^22\delta}{v_0},
\qquad g=1-q.
\tag{C6.1}

CLOSURE — assumptions for the following map. Suppress the activity gate at leading order by setting A=1; freeze the slow stance/imbalance while averaging the fast orientation process; use its stationary framing-class law; and calculate away from clipping and stance-switching boundary layers. This is an all-active bulk reduction, not yet the full gated limit of v0.6.

CLOSURE — fast orientation calculation. Let Y=\cos2\phi. The peer update multiplies its conditional first moment by q. At leading symmetric order,
E[Y_n^2]=q,\qquad
E[Y_nY_{n+k}]=q^{k+1}.
\tag{C6.2}
Reset/reconsideration supplies the stance-conditioned mean
E[Y\mid s]
=
\frac{hUs}{\Lambda(1-q)+h v_0}.
\tag{C6.3}
The normalized conviction deposit can be written
V_n=d_0\cos2\theta_n+\bar a_0Y_n.
\tag{C6.4}

LIMIT — within that closure; order: N\to\infty, then h\to0 at fixed coefficient ratios and fixed K. Summing the serial covariance in (C6.2) gives
\boxed{
H=\frac{\bar a_0qU}{1-q},\qquad
J=\frac{d_0U}{1-q},
}
\tag{C6.5}
\boxed{
D=
\frac{\Lambda q}{2}
\left[
d_0^2+\bar a_0^2\frac{1+q}{1-q}
\right].
}
\tag{C6.6}
The resulting reflected bulk diffusion is
dc=(Hs-\varepsilon c+Jx)\,dt+\sqrt{2D}\,dW,
\tag{C6.7}
with s retaining the declared hysteresis rule.

CLOSURE — wall-pinning restriction. At c_h=0,x=0, the potential is
V(c)=\frac{\varepsilon c^2}{2}-H|c|.
Its minima are at the walls only when
\boxed{H>\varepsilon.}
\tag{C6.8}
The weaker inequality H>\varepsilon/2 merely makes the expression H-\varepsilon/2 positive; it does not pin the wells to the walls. At nonzero x, both wells remain wall-pinned only if
\boxed{H-|Jx|>\varepsilon.}
\tag{C6.9}

C6.2 Tilt, hysteresis, and the switching form

CLOSURE — leading barrier calculation with wall-pinned wells. At c_h=0, the zero-field barrier is
B_0=H-\varepsilon/2,\qquad K=B_0/D.
For positive stance persisting down to -c_h, the exit barrier is
B_+(x)
=
H(1+c_h)-\frac{\varepsilon}{2}(1-c_h^2)
+Jx(1+c_h).
\tag{C6.10}
The opposite barrier has the opposite sign of the final term. Consequently,
\boxed{
a=\frac JD,\qquad
a_{\rm hyst}=(1+c_h)\frac JD.
}
\tag{C6.11}
Hysteresis changes the zero-field barrier as well as the tilt coefficient.

LIMIT — large-barrier reduction after the diffusion limit, with metastable wells and a finite limiting tilt parameter. At leading exponential order, the two switching rates have the form
w_{+\to-}\simeq\nu_K e^{-a_{\rm hyst}x},
\qquad
w_{-\to+}\simeq\nu_K e^{a_{\rm hyst}x}.
Thus
\boxed{
\dot x
=
2\nu_K
\left[
\sinh(a_{\rm hyst}x)
-x\cosh(a_{\rm hyst}x)
\right].
}
\tag{C6.12}
At fixed physical time, switching vanishes as the barrier tends to infinity. A nontrivial limiting switching dynamics requires the corresponding Kramers-time rescaling.

EXACT — within the two-state equation (C6.12). Its stationary equation is
x=\tanh(a_{\rm hyst}x).
\tag{C6.13}
There are two stable nonzero equilibria and an unstable zero equilibrium when a_{\rm hyst}>1; only the stable zero equilibrium exists when a_{\rm hyst}<1. Equality is the bifurcation point.

EXACT — limitation of the stated conditions. The inequalities H>\varepsilon,q<1,U>0,d_0>0 do not, by themselves, imply a_{\rm hyst}>1, nor do they imply the stronger wall-pinning condition (C6.9) at a nonzero branch.

C6.3 An O(h) bulk correction

CLOSURE — assumptions: the same all-active stationary angular environment, frozen slow variables, and no threshold/wall boundary-layer correction. Set
G_h=g+\frac{h v_0}{\Lambda}.
The bulk coefficients through first order are
H_h=\frac{\bar a_0qU}{G_h},\qquad
J_h=\frac{d_0U}{G_h},
\tag{C6.14}
D_h=
\frac{\Lambda q}{2}(d_0^2+\bar a_0^2)
+
\frac{\Lambda\bar a_0^2q^2}{G_h}
+O(h^2).
\tag{C6.15}
The extra reset/reconsideration rate shortens the orientation correlation time.

CLOSURE — resulting tilt correction. Put
S=g\,d_0^2+(1+q)\bar a_0^2.
Then
\boxed{
a_h^{\rm bulk}
=
a\left[
1-h\,
\frac{v_0(d_0^2+\bar a_0^2)}
{\Lambda S}
\right]
+O(h^2).
}
\tag{C6.16}
The corresponding leading-exponential hysteresis tilt is
a_{{\rm hyst},h}^{\rm bulk}
=(1+c_h)a_h^{\rm bulk}.
\tag{C6.17}

CLOSURE — finite-h branch conditions within this reduction. The reduced bistable branch requires
a_{{\rm hyst},h}^{\rm bulk}>1,\qquad
H_h>\varepsilon,
and, at the selected x_*,
H_h-|J_hx_*|>\varepsilon.
\tag{C6.18}
These conditions concern the reduced switching equation, not a proved full-process stationary branch.

C6.4 Why this is not the full gated O(h) correction

EXACT — finite-h gate obstruction. At any finite peer rate, the probability of no peer receipt during the last L units of time is positive. In a stationary population,
A\le1-e^{-\lambda A L}<1.
\tag{C6.19}
Thus an exactly all-active stationary population is impossible at finite h.

CLOSURE — size of the omitted effect in the wall-pinned diffusion. At zero field, the cost of moving from 1 down to c_b is
\Delta_b
=
H(1-c_b)-\frac{\varepsilon}{2}(1-c_b^2)>0.
\tag{C6.20}
The silent fraction is exponentially small in \Delta_b/D in the large-barrier regime, but at fixed finite K it is not automatically O(h), much less o(h).

EXACT — consequence for the requested order of limits. Taking h\to0 at fixed finite K does not justify discarding a nonzero silent fraction when computing an O(h) correction. Peer intensity is \Lambda A/h^2, and the donor orientation distribution is conditioned on activity. Both must be included in the leading gated homogenization before its first correction can be identified.

EXACT — distinction between finite-amplitude persistence and invasion in this scaling. On a fresh c=0 background, whenever
h\max(a_0,b_0)\le c_b,
\tag{C6.21}
one message cannot activate any recipient. The single-shot next-generation operator is therefore zero, even though \lambda=\Lambda/h^2. Any positive branch at those parameters is necessarily a finite-amplitude branch, not linear invasion from the fresh silent background.

EXACT — finite-barrier rates need more than J/D. Even in the reduced diffusion, a frozen-stance first-passage time from the positive wall to -c_h is
\tau_+(1;x)
=
\frac1D\int_{-c_h}^{1}
e^{V_+(y)/D}
\left[
\int_y^1e^{-V_+(z)/D}\,dz
\right]dy,
\tag{C6.22}
where V_+(c)=\varepsilon c^2/2-(H+Jx)c. Its prefactor is parameter dependent. Thus J/D identifies the leading barrier tilt, not an exact finite-barrier switching-rate parameter.

OPEN — full C6(b). A full gated O(h) correction, including activity conditioning, clipping, switching overshoots, and the relevant boundary layers, is not established here. Nor is a necessary-and-sufficient finite-h existence theorem for the full kinetic bistable branch. Equation (C6.16) is a delivered bulk correction under a declared closure; presenting it as the full v0.6 correction would be incorrect.

C6.5 What is and is not process-specific

EXACT — mathematical form. For symmetric metastable states with linearly tilted barriers and leading Kramers switching, the exponential rates and the resulting hyperbolic-function equation follow independently of the projective orientation mechanism. Asymmetry or unequal prefactors requires modifications.

EXACT — attribution. Exponential two-state transition rules appear explicitly in Henkel's 2016 treatment, and Krause and Bornholdt's 2013 work supplies related microscopic-to-macroscopic coarse-graining precedent. These references do not prove the coefficient map for v0.6.

CLOSURE — contribution of the present calculation. The process-specific object is the map from orientation, reinforcement, and clock parameters to H,J,D, together with its domain of validity. The switching functional form is not a distinguishing contribution.

Gate status and remaining boundaries

Requested gate	Status	Result
C1: generator and novelty clock	EXACT	Joint-law generator, impulsive cohort maps, and conditional novelty formula supplied.
C2(b): transition classification	EXACT — refuted	No positive habituating stationary branch; an m=1, r=1 counterexample has a critical-mass fold.
C2(c): A(t) and collapse	EXACT / CLOSURE	Controlled nonlinear Volterra quadrature supplied. The stochastic collapse index is random; deterministic residual factors require a timing closure.
C3(a): stationary invasion operator	EXACT	Finite multitype operator supplied, including reconsideration-generated broadcast classes and reachability.
C3(c): four constructions	EXACT / LIMIT / OPEN	(i)–(iii) computed. Original (iv) is underspecified; a fully declared (iv^*) is computed. Frozen and asymptotic quantities are separated.
C4: coupled fixed points and stability	EXACT	Stationary-response quadratures, branch parametrization, and kinetic local-stability criterion supplied.
C5: process–surrogate separation	EXACT under declared surrogate	Differences include 0.25 in stance imbalance and 0.1875 in repeated-rejection probability.
C6(a): coefficient map	CLOSURE, then LIMIT	Confirmed for the all-active bulk reduction, with H>\varepsilon and additional branch restrictions.
C6(b): finite-h correction and branch	CLOSURE / OPEN	Bulk O(h) correction delivered; full gated correction and full branch-existence theorem remain unestablished.

EXACT — final boundary. The calculations support three distinct mechanisms of order dependence: persistent orientation preparation, stance changes surviving relaxation, and residual outcome–deposit correlations. They do not support collapsing those mechanisms into one preparation product, identifying transient amplification with persistence, or assigning the full gated process a stationary scalar reduction without retaining the assumptions that make that reduction valid.

---

## APPENDIX D — Claude derivation, C1–C6 against specification v0.6 (verbatim)

**Assumptions inserted where the specification is silent.** (i) initial law I1 (from I2 the result is order-independent, shown below); (iii) c_h inert since β = 0 and s = + throughout, ε enters only through lifetimes (R_inv in units of λ/ε); (iv) c_b, c_h, ε, gaps unstated, result given by regime. Surrogate reset rule taken as a ← T_s, τ ← 1. All numbers are closed-form evaluations of the specification, no simulation.

## C1. Kinetic equation

State of an agent z = (φ, c, s, n, u). Message kernel for framing θ:
(Q_θ g)(z) = cos²(θ−φ) g(z^acc_θ) + sin²(θ−φ) g(z^rej_θ), with z^acc_θ = (θ, C[c + α r^{n_j(θ)} cos2θ], S, n+e_j), z^rej_θ = (θ+90°, C[c − β r^{n_j(θ)} cos2θ], S, n+e_j), C the clip, S the hysteresis stance rule, exponents using the pre-message counter (equals post-increment minus one).

Mean-field generator between pulses, acting on the law ν_t:
L_t g = −εc ∂_c g + λ∫ ν_t(dφ' ; |c'|>c_b) [Q_{φ'} g − g] + ρ[g(T_s,·) − g] + κ[½g(T_s+δ,·) + ½g(T_s−δ,·) − g].
The message intensity at θ is λ times the active mass at θ, so λA_t π_t(dθ) = λ ν_t(dθ ; |c|>c_b). At pulse t_k the u = 1 sub-population is pushed forward by Q_{θ_k}; coincident pulses compose in index order. d⟨ν_t, g⟩/dt = ⟨ν_t, L_t[ν_t] g⟩ is McKean–Vlasov: the joint law is the state. [EXACT, N → ∞ at fixed t; single-recipient delivery gives the tagged-agent hazard λ·(active others)/(N−1) → λA.]

Novelty clock. For a cohort member, n_j(t) − n_j(0) − m_j(t) is the count of class-j peer arrivals, an inhomogeneous Poisson variable with mean λ∫₀ᵗ A_j, and its class is fixed by the sender, not by the receiver's state, so it is independent of the agent's own trajectory. Hence E[r^{n_j(t)}] = E[r^{n_j(0)}] r^{m_j(t)} exp[−(1−r)λ∫₀ᵗ A_j]. [EXACT in mean field; O(1/N) at finite N.]

Closes: the counter law for any cohort; at r = 1 the counters drop out entirely; for the single-class optimist crowd at exact targets with κ = 0 the joint law reduces to a one-dimensional density p_t(c) obeying ∂_t p + ∂_c(−εc p) = λA_t[p(c−α) − p(c)] with A_t = ∫_{c_b}^1 p + (atom at 1): closed, nonlinear, infinite-dimensional; for α ≥ 1 it closes on A_t alone (C2d). Does not close: the (x, A, B) hierarchy in general — ẋ needs the c-density at ±c_h, Ȧ needs it at ±c_b and the crowd's orientation law (acceptance rates), the orientation law needs the (φ,c) joint law, and at r < 1 the counters. [CLOSURE statements are exactly the three listed; OPEN: none at this level.]

## C2. Single-class shot noise

Setting: all agents at T, all messages T, every message accepted, no rejections, no stance change. From I1 the state A = 0 is absorbing; the trajectory requires a campaign pulse or an initial active seed, treated below as an initial condition (c₀, m₀).

(a) Given N(t) = n arrivals at times t₁<…<t_n, c(t) = c₀e^{−εt} + Σ_{k=1}^n α r^{m₀+k−1} e^{−ε(t−t_k)}, clipped. For constant rate ν = λA the arrival times are uniform order statistics on [0,t], so
P_t(c > c_b) = Σ_n e^{−νt}(νt)^n/n! · P_n(t), P_n an n-fold integral. [EXACT; quadrature.]
Stationary case r = 1: E[e^{−sc}] = exp[−(ν/ε) Ein(sα)], Ein(y) = ∫₀^y (1−e^{−u})/u du. [EXACT, unclipped.]
Sparse asymptotics. With counter n and jumps to come αr^n, αr^{n+1}, …, activation needs m consecutive-enough arrivals with αr^n(1−r^m)/(1−r) > c_b; the leading term is (ν/ε)^{m_r} V_{m_r}/m_r!, V_m = Vol{w ∈ (0,1]^m : Σw_i > c_b/(αr^n) with geometric weights} (dw/w measure), and
m_r = ⌈ln(1 − (1−r)c_b/(αr^n)) / ln r⌉, infinite if (1−r)c_b ≥ αr^n (the remaining budget is below threshold).
At r = 1 this is ⌈c_b/α⌉ = ⌊c_b/α⌋+1 for non-integer c_b/α: the stated m confirmed. At r < 1 the stated m = ⌊c_b/(αr^{n−1})⌋+1 counts with the last jump received rather than the geometrically shrinking jumps to come; it understates the exponent whenever more than one jump is needed. [LIMIT: ν/ε → 0 with the tail older than ε⁻¹ln(1/ν) contributing at higher order.] Illustration r = 1, c_b/α = 1.5: V₂ ≈ 0.186/ε², P ≈ 0.093 (ν/ε)².

(b) Transition class, r = 1. P(ν) is continuous, nondecreasing (coupling), P(0)=0, P ≤ 1; F(A) = M P(λA) − A.
m = 1 (α > c_b): P(ν) = νL_α + O(ν²), L_α = ε⁻¹ln(min(α,1)/c_b). F′(0) = λML_α − 1 changes sign at λML_α = 1: transcritical. Forward (continuous onset) when α ≥ 1, since then P = 1 − e^{−νL} exactly and concave. [EXACT.] For c_b < α < 1 the quadratic coefficient is −L_α²/2 + (two-jump accumulation volume)/2; if positive the transcritical point is backward, with a fold below it and hysteresis. [OPEN: sign condition stated, not evaluated.]
m ≥ 2: P = Θ(ν^m), F′(0) = −1, A = 0 linearly stable. F increases pointwise in λ; the least λ at which max_{A>0} F ≥ 0 gives a tangential touch: saddle-node, two branches (lower unstable, upper stable). Confirmed. [EXACT; genericity of the tangency assumed.]
r < 1: no stationary state with A > 0 exists. With A > 0, n → ∞ for every agent, jumps → 0, sup c → 0 < c_b. The self-consistency is meaningful only at r = 1. [LIMIT, mean field; rules out any phase diagram in the interior of the r-axis.]

(c) Trajectory. With the exact mean equation, dE[c]/dt = −εE[c] + λA α E[r^{n}] (unclipped, jump independent of the agent's counter given intensity), and the novelty clock from C1:
c̄(t) = c₀e^{−εt} + λαr^{m₀} ∫₀ᵗ A(u) exp[−(1−r)λ∫₀ᵘA] e^{−ε(t−u)} du. [EXACT for the mean.]
Closure λA ≫ ε (shot noise self-averages): A(t) = M·1(c̄(t) > c_b) while the crowd is active, so A = M and
c̄(t) = c₀e^{−εt} + λMαr^{m₀}[e^{−gt} − e^{−εt}]/(ε − g), g = (1−r)λM. [CLOSURE.]
Collapse time t_acc solves c̄ = c_b on the descending branch; the true collapse index is k_acc = λM t_acc. For g < ε (habituation slower than decay): k_acc = [ln(αr^{m₀}/c_b) + ln(λM/(ε−g))]/(1−r). For g > ε: k_acc = (λM/ε) ln[λMαr^{m₀}/(c_b(g−ε))]. The single-shot index is k_cross = 1 + ln(αr^{m₀}/c_b)/ln(1/r). In the g < ε branch the collapse occurs when the per-message jump reaches c_b(ε−g)/(λM), not c_b: the residual-conviction correction factor is (ε−g)/(λM) = ε/(λM) − (1−r), and k_acc − k_cross ≈ ln(λM/(ε−g))/(1−r) − 1 for r near 1. In the sparse regime (λMα/ε < c_b) the fluid mean never reaches c_b, the closure is inapplicable, and activity is single-shot: k_acc = k_cross. [CLOSURE in its regime; OPEN: the crossover between regimes in closed form; the exact k_acc is the point where the quadrature P_t falls below the self-consistent level.]

(d) Checks. r → 0, α = 1: only the first message counts, sets c = 1, active for exactly L = ε⁻¹ln(1/c_b), then silent forever: Ż = λA(1−Z), A(t) = Z(t) − Z(t−L), final size 1 − Z_∞ = (1−Z₀)e^{−λLZ_∞}, invasion iff λL > 1. Kermack–McKendrick with fixed duration. [EXACT.] r = 1, α = β = 1: every accepted T refreshes c = 1; active iff last arrival within age L: A(t) = M[1 − exp(−λ∫_{t−L}^t A)], fixed point A* = M(1−e^{−λLA*}), transcritical at λML = 1. Result 4's renewal equation recovered. [EXACT.]

Rules out: stationary activity at any r < 1; a saddle-node at m = 1 with α ≥ 1. Assumptions: single class, κ = 0, no rejections. Open: backward-bifurcation condition for c_b < α < 1; closed-form k_acc across the crossover.

## C3. Invasion

(a) I3 at ρ, κ > 0, stance fractions p_± = (1±x)/2, single class, single-shot doses. Define the leak g = κ sin²δ/(ρ+κ): probability that a background agent, at the moment of a peer message, sits at T_s ± δ and collapses to the wrong basis element. A T message is accepted by a + agent w.p. 1−g, by a − agent w.p. g; a T⊥ message the reverse. Acceptance of T: π₁ = p₊(1−g) + p₋g = ½[1 + (1−2g)x]; π₂ = 1 − π₁.
Four types by (broadcast basis, activating jump): T/α, T/β, T⊥/α, T⊥/β with lifetimes L_α = ε⁻¹ln(min(α,1)/c_b)·1(α>c_b), L_β likewise. A T-broadcaster's recipients accept w.p. π₁ (become T/α) and reject w.p. π₂ (become T⊥/β via +(−β)); a T⊥-broadcaster's recipients accept w.p. π₂ (T⊥/α) and reject w.p. π₁ (T/β, since −β·cos180° = +β at φ = T). The next-generation matrix has rank 2; its nonzero spectrum is that of [[uπ₁, vπ₁],[vπ₂, uπ₂]], u = λL_α, v = λL_β, so with y = (1−2g)x:
R_inv = ½[u + √(u²y² + v²(1−y²))]. [EXACT.]
β ≤ c_b: R_inv = λL_α π₁ = (λL_α/2)[1 + (1−2g)x]. The background enters only through x and the reconsideration coefficient g, which is a parameter of the stationary law, not of any preparation. No Γ: at I3 the orientation law given stance is fixed by (ρ, κ, δ); every trace of campaign framing has been erased except what survived into stance. Proved by construction. [EXACT.] Remark: for v > u (β > α) R_inv is maximal at x = 0; a balanced background is easier to invade when rejection activates more strongly than acceptance.

(b) Prepared background. Recipient law at delay τ after the campaign: ν_τ = e^{−ρτ} ν_prep(c decayed by e^{−ετ}) + (1−e^{−ρτ}) ν_relaxed; counters permanent. K(τ) is built from ν_τ as in (a) with orientation-specific acceptance cos²(θ−φ) and deposit-specific lifetimes ε⁻¹ln(|c_pre e^{−ετ} + jump|/c_b). The frozen spectral radius R(τ₀) is an instantaneous reproduction number only if the generation time L ≪ 1/ρ, 1/ε. The exact statement: a seed at τ₀ has expected lineage G(τ₀) = Π_k R(τ₀ + kL) over the relaxation window, a finite gain; growth as t → ∞ is decided by R_inv(I3) alone. In the mean-field order (N → ∞ first) an infinitesimal seed never leaves the linear regime in finite time, so the prepared background cannot convert a subcritical I3 into invasion; it multiplies the seed by G. Exception: ρ = κ = 0, where the orientation law never relaxes and Γ is permanent, while deposits still relax at ε. [LIMIT.] Ignition (nonlinear activation before relaxation) is a finite-seed, finite-N question outside this criterion. [OPEN.]

(c) Table, one framework (frozen operator at the stated seed time, single-recipient delivery, f = 1).

(i) I1, ρ = κ = 0, α = 1, β = 0, r = ½, c_b = 0.95, ε = 1, gaps ln 100. No pulse activates: deposits cos20° = 0.940, cos40°+residual ≤ 0.947, cos60°+residual ≈ 0.51, all < 0.95; stance stays +; residual c ≤ 0.01 at the seed. Only orientation is prepared. Acceptance of T after the sequence is ½[1 + cos2θ₁ Π cos2(θ_{k+1}−θ_k) cos2θ_m] (Bloch contraction), the seed sets c = 1 for every accepter, L = ln(1/0.95) = 0.0513, single type.
(10,20,30): product 0.415, E[cos²φ] = 0.7075, R_inv = 0.0363λ.
(10,30,20): 0.518, 0.759, R_inv = 0.0389λ.
(20,10,30): 0.276, 0.638, R_inv = 0.0327λ.
Channel: Γ, permanent because ρ = κ = 0. Invasion needs λ > 25.7–30.6 (order shifts the threshold by 19%). From I2 instead, the maximally mixed state is invariant under every projection: E[cos²φ] = ½ for all orders, R_inv = 0.0256λ, no order effect. [EXACT.]

(ii) I2, α = 1, β = ¼, r = ½, c_b = ½, c_h = 0.01, ε = 1, κ = 0, ρ > 0, zero gaps, relaxed to I3. Pulse deposits ±0.1736 (accept 40°/50°/140° at n = 1), ∓0.0434 (reject), halved at n = 2 for class 50 (140° ≡ 50°). Within a class the orthogonal element is always rejected and leaves φ fixed.
(40,50,140): branches (½·0.9698, ½·0.0302, ½·0.0302, ½·0.9698) end at c = −0.0217, 0.3039, −0.2388, +0.0868: p₊ = 0.5, x = 0 exactly (mirror symmetry of the branches).
(40,140,50): ends at 0.369, 0.0434, 0.1519, −0.1736 with weights 0.0151, 0.4849, 0.4849, 0.0151: p₊ = 0.9849, x = 0.970.
Nothing activates (max |c| = 0.37 < 0.5). After relaxation φ = T_s, c = 0, g = 0, β < c_b: R_inv = λ ln2 · p₊ = 0.347λ vs 0.683λ. Channel: stance imbalance x, exclusively. [EXACT.]

(iii) I2, α = 0.6, β = 0, c_b = 0.5, ρ = κ = 0, zero gaps, seed immediately. Deposit 0.6cos40° = 0.4596 on accepting 20°; 45° deposits nothing. Lifetimes: clipped c = 1 → ln2 = 0.693; c = 0.6 → ln1.2 = 0.182.
(45,20): final (20°, c = 0.46) w.p. ½, (110°, 0) w.p. ½; T accepted w.p. cos²20° = 0.883 and 0.117: R_inv = [½·0.883·0.693 + ½·0.117·0.182] λ/ε = 0.317λ/ε.
(20,45): final orientation 45°/135°, T accepted w.p. ½ regardless; deposit on half: R_inv = ½[½·0.693 + ½·0.182] λ/ε = 0.219λ/ε.
E[cos²φ_final] = ½ in both orders (isotropic start): the Γ channel is zero; the 45% difference is entirely the outcome–deposit correlation (in (45,20) the deposit sits on exactly the T-favorable agents). With the seed delayed by ≫1/ε both orders give 0.091λ/ε: transient at rate ε even at ρ = κ = 0. [EXACT.]

(iv) I2, α = 0.45, β = 0.2, r = ½, ρ → ∞. Every agent sits at T_s before every pulse, so acceptance depends on stance only; all + throughout. Both orders end at c = 0.9 w.p. 0.75, 0.575 w.p. 0.25 (zero gaps), φ = T at the seed. R_inv identical by order in every c_b regime: c_b < 0.575, whole cohort already active (invasion undefined); 0.575 < c_b < 0.9, 75% active; c_b > 0.9, seed adds 0.45·r² = 0.1125. With finite gaps the orders differ only by decay weights on identical jumps, which any memory model reproduces. Channel: none. [EXACT.]

Rules out: Γ as an invasion channel on any relaxing background; order effects from isotropic starts without conviction memory; the reading that the four constructions test one mechanism. Assumptions: frozen operator at the stated seed time; f = 1. Open: ignition at finite N; the (i) initial law as the reviewer intended it.

## C4. Two-camp branch

Pools M₊ (φ = T, s = +), M₋ (φ = T⊥, s = −), fixed at κ = 0, r = 1 (optimists receive only positive increments: +α per T accepted at rate λA₊, +β per T⊥ rejected at rate λA₋; skeptics only negative: −β per T rejected at rate λA₊, −α per T⊥ accepted at rate λA₋). Stationary marginal: E[e^{−sc}] = exp{−(λ/ε)[A₊Ein(sα) + A₋Ein(sβ)]} for optimists, α ↔ β for skeptics. [EXACT, unclipped.]

Self-consistency A₊ = M₊P₊(A₊,A₋), A₋ = M₋P₋(A₊,A₋) with P_± nondecreasing in both arguments: a cooperative system, so fixed points are ordered, the extremal ones are attracting from extremal initial conditions, and stable and unstable points alternate. [EXACT.]

α = β = 1: both tails equal 1 − exp(−λL(A₊+A₋)); total activity A obeys A = M(1−e^{−λLA}), M = M₊+M₋, A_± = M_±A/M. Skeptics are active whenever optimists are; x = M₊−M₋ is inert; transcritical at λLM = 1. [EXACT; this is Result 4 with a two-camp composition.]

Fluid closure (λA ≫ ε): c̄₊ = λ(αA₊+βA₋)/ε, c̄₋ = −λ(βA₊+αA₋)/ε, A_± = M_± 1(|c̄_±| > c_b). Fixed points: (0,0), absorbing; (M₊,0) iff λαM₊ > εc_b and λβM₊ ≤ εc_b; (M₊,M₋) iff λ(βM₊+αM₋) > εc_b and λ(αM₊+βM₋) > εc_b; (0,M₋) symmetrically. Stability: strict inequalities, marginal at equality. The candidate λβA₊ > εc_b is the condition for the skeptic pool to leave silence on optimist input alone; the coexistence point exists already at λ(βM₊+αM₋) > εc_b because active skeptics reinforce each other with −α. Hysteresis band for the skeptic pool: εc_b/λ ∈ (βM₊, βM₊+αM₋). [CLOSURE; exact fixed points replace the indicator by the shot-noise tails above.]

r < 1: T and T⊥ share the single class counter, so skeptic broadcasts habituate optimists and vice versa; E[r^n] = exp(−(1−r)λ∫(A₊+A₋)); both budgets α/(1−r), β/(1−r) are finite; no stationary active state (C2b); the coupling shortens the transient. [LIMIT.]

Rules out: any two-camp stationary branch at r < 1; a skeptic pool that is silent on the supercritical branch when β ≥ c_b M/(A₊ ln(α/c_b)) in the single-shot regime. Assumptions: κ = 0 (with κ > 0 stances leak at rate g and the pools are not fixed). Open: the exact stationary tails with clipping; the boundary of the coexistence region beyond the fluid closure.

## C5. Geometry-separating quantities

Surrogate: after messages θ₁…θ_m from anchor a₀ with τ₀ = 1, τ = Π cos2(θ_{k+1}−θ_k)·cos2(θ₁−a₀), a = θ_m. Its acceptance probability of the next message equals the process's acceptance probability averaged over collapse outcomes: E[cos2(φ′−θ′)] = cos2(θ−φ)cos2(θ′−θ). The two models agree on every single-message marginal and every mean Bloch vector; they differ only in joint laws. [EXACT.]

(a) Repeated-framing lock, I2, campaign (T,T). Process: accept the first T w.p. ½, then the second surely; two atoms, c = α(1+r) w.p. ½, −β(1+r) w.p. ½. Surrogate: p = cos²a₀, outcomes AA (E p² = 3/8), AR, RA (1/8 each), RR (3/8), four atoms. α = 1, β = ¼, r = ½, c_h ≤ 0.25, zero gap: x_process = 0, x_surrogate = ¼, independent draws at p = ½ give ½. α = β = 0.4, r = ½, c_b = 0.5: x = 0 in both, activation A_process = 1, A_surrogate = 0.75. [EXACT.]

(b) (45,20) vs (20,45), I2, α = 0.6, β = 0. Process joint laws and R_inv as in C3(iii): 0.317 vs 0.219 λ/ε. Surrogate (45,20): τ = 0.6428 sin2a₀ at the 20° pulse, 0.4924 sin2a₀ at the seed; deposit and seed acceptance are correlated only through a₀: P(deposit ∧ accept) = 0.290, P(no deposit ∧ accept) = 0.210, R_inv = 0.239λ/ε. Surrogate (20,45): τ = 0 at the seed, acceptance ½ independent, R_inv = 0.219λ/ε. Process exceeds surrogate by 0.078λ/ε (32%) in the order that carries the correlation; the two agree exactly in the other. [EXACT.]

(c) Sign reversal. I1 (φ = T), one pulse at 60° (Δ = 60° > 45°, cos2Δ = −½), then T seed; α = 0.6, β = 0.15, c_b = 0.5, zero gap. Process: 25% accept, land at 60° with c = −0.3; 75% reject, land at 150° with c = +0.075 — rejection re-aligns the ensemble with 150°, whose mean Bloch vector is +½ u_{150°}, 30° from T. Seed accepted at 0.25 from 60° (c = 0.3, silent) and 0.75 from 150° (c = 0.675, active, L = ln1.35 = 0.300): P(active) = 0.5625, R_inv = 0.169λ/ε. Surrogate: τ = −½ after 60°, +¼ at the seed, acceptance 0.625 (same marginal), independent of the deposit: P(active) = 0.75·0.625 = 0.469, R_inv = 0.141λ/ε. Difference 0.028λ/ε (20%). [EXACT.]

Rules out: any test of the projective rule through single-message acceptance rates or mean orientations. Assumptions: surrogate initial τ = 1. Open: whether any quantity separates the two in the r = 1 Lux regime, where only means and variances enter (C6 says no: q and the increment identity are all that survives).

## C6. Lux limit

(a) Increment identity at r = 1: Y = h[d₀ cos2θ + ā₀ cos2φ′], ā₀ = (a₀+b₀)/2, d₀ = (a₀−b₀)/2, the accept/reject sign carried by the post-message orientation (accept: φ′ = θ; reject: cos2φ′ = −cos2θ). [EXACT.] For a message θ from the sender mixture with E[sin4θ] = 0 (±δ symmetry), E[cos2φ′|φ] = E[cos²2θ] cos2φ = q cos2φ; copying preserves the injected basis mixture, so q = (p₀ + k₀cos²2δ)/(p₀+k₀). Mean orientation of stance-s agents: ṁ_s = −λA(1−q)m_s + ρ(s−m_s) + κ(s cos2δ − m_s), stationary m_s = s(ρ+κcos2δ)/(λA(1−q)+ρ+κ) = s hU/(ΛA(1−q)) + O(h²), U = p₀ + k₀cos2δ. Drift of c: λA·E[Y] = λAh[d₀·x·m + ā₀·q·s·m] (PASTA: post-message mean is q m_s; sender stances average to x on the active branch) = Jx + Hs with
H = ā₀qU/(1−q), J = d₀U/(1−q), both independent of A at h → 0 (message rate and message-driven relaxation cancel).
Diffusion: senders i.i.d. with variance q; the post-message orientation chain has variance q and autocorrelation q^k, long-run variance per message q(1+q)/(1−q); cross terms O(h): D = (ΛAq/2)[d₀² + ā₀²(1+q)/(1−q)]. Confirmed with A = 1. Well of a + agent at c* = (H+Jx)/ε, pinned at the wall iff H + Jx > ε; H > ε is necessary, H − J > ε sufficient for all |x| ≤ 1. Barrier from the wall to the flip point −c_h: ΔV = (H+Jx)(1+c_h) − ε(1−c_h²)/2, so the switching exponent is linear in x with a = J(1+c_h)/D, and K = (H−ε/2)/D is ΔV at x = 0, c_h = 0. Confirmed. [LIMIT: h → 0 at fixed K, then K → ∞; exponent error O(hK) from the third cumulant.]

(b) Finite h, c_b > 0. Three O(h) contributions to a. (1) Orientation relaxation denominator: H, J → H, J·[1 + h(p₀+k₀)/(ΛA(1−q))]⁻¹. (2) Activity: J is A-independent, D ∝ A, so a = [J(1+c_h)/D]·(1/A) with A = 1 − Φ, Φ the band-transit fraction = O(c_b e^{−K}) — the leading finite-c_b effect, exponentially small at large K. (3) Skewness of the summed increments: O(hK) in the exponent and not linear in x, so at finite h "a" is defined as the linear coefficient only. Together:
a(h,c_b) = [J(1+c_h)/(D_{A=1})]·(1/A)·[1 − h(p₀+k₀)/(ΛA(1−q))] + O(h²) + O(hK)·(x-nonlinear terms). [LIMIT for (1),(2); OPEN: the coefficient of (3).]
Existence. The silent state A = 0 is absorbing at c_b > 0 and coexists with the active branch: bistability in A, distinct from Lux's bistability in x. The active branch is locally stable iff its wells stay pinned, H(A) > ε with H(A) = ā₀qU/[(1−q) + h(p₀+k₀)/(ΛA)], i.e. A > h(p₀+k₀)/(Λ[ā₀qU/ε − (1−q)]), which on the branch reduces to H > ε + O(h). The ordered branch x = ±x* exists iff a(h,c_b) > 1. Delivered. [LIMIT.]

(c) The reduced law ẋ-dynamics with rates v e^{∓ax} is the form of any bistable variable with linear tilt and Kramers switching (Krause & Bornholdt 2013; Henkel 2016). The specification contributes the map (a₀, b₀, Λ, p₀, k₀, δ) → (H, J, D); the projective rule enters only through q and the increment identity; sign consolidation is the reset-to-T_s rule; switching is a reconsideration effect (κ, δ > 0 required: with endpoint bases only, m_s = s, the drift is O(1/h) and no diffusion limit exists). [EXACT as a statement of provenance.]

Rules out: Lux's rates from response plus event memory alone; any A-dependence of J at leading order. Assumptions: r = 1, A ≈ 1, current-framing broadcasts, weak tilt for the prefactor only. Open: the O(h) skewness coefficient; whether the map is testable against any quantity the surrogate does not reproduce (C5 says no: the r = 1 regime carries none).

**Gates.** C2(b) settled (proof at r = 1, both classes; r < 1 excluded); C2(c) A(t) in quadrature (exact) and closed form (fluid closure), k_acc in both branches. C3(a) proved; C3(c) table complete with channels named. C4 fixed points and stability delivered (exact at α = β = 1 and via monotonicity; explicit under the fluid closure). C5 three separating quantities with stated amounts (¼ in x, 0.25 in A, 32% and 20% in R_inv). C6(a) confirmed with the H > ε restriction and the sharper H − J > ε; C6(b) delivered with the skewness coefficient left open.

**What the pass settles for the manuscript**

Result 2. Strengthened. No stationary branch exists anywhere on 0 < r < 1, in one camp or two (C2b, C4). The collapse index is k_acc, not k_cross, whenever λM ≫ ε, with the residual-conviction factor (ε−g)/(λM); the sparse-regime exponent is the geometric count m_r, not ⌊c_b/(αr^{n−1})⌋+1. Reviewer 1's reading of item 3 stands: two corners, no interior phase diagram.

Result 4. Exact at α = β = 1 (C2d), and the two-camp system reduces to it with x inert (C4). The onset class is transcritical-forward for α ≥ 1 and possibly backward for c_b < α < 1, which the manuscript does not currently distinguish.

Result 5. The coefficient map is confirmed with two additions the packet lacks: H and J are independent of the active fraction at leading order while D is not, so a scales as 1/A at finite c_b; and the O(h) structure is explicit except for the skewness coefficient. Reviewer 1's provenance verdict holds; the novelty claim should be withdrawn in the form stated and replaced by the map with its necessary conditions (q < 1, U > 0, d₀ > 0, H > ε).

Result 7a. Reviewer 2 is right that Γ never reaches invasion on a relaxing background and wrong that order does not. Order reaches invasion through x alone: construction (ii) moves R_inv by a factor 1.97 with zero contribution from framing geometry after relaxation. Γ is a finite gain G(τ₀), permanent only at ρ = κ = 0 and only from non-isotropic initial laws; the outcome–deposit correlation is a second transient channel, decaying at ε even when orientation is frozen. 7a should be restated as: campaign order → stance law → R_inv, with the two geometric channels as transient multipliers with rates ρ and ε.

Result 8. The prepared-background extension cannot be an invasion criterion under the specification's own mean-field order (C3b). Replace it with the gain statement; the criterion is R_inv(I3) with the closed form of C3a.

Item 5, geometry's observables. Repeatability is not the only one. The joint-law effects in C5(b) and C5(c) separate the process from a surrogate that matches every marginal, by 32% and 20% in R_inv at the stated parameters. They are the same Lüders lock read out through conviction memory rather than through orientation, so the honest claim is one rule, three measurements, all vanishing with seed delay ≫ 1/ε. The r = 1 Lux regime carries none of them.

**Open items, ranked by whether closing them changes the verdict**

1. Ignition at finite N or finite seed (C3b). The only route by which a prepared background could convert subcritical I3 into persistence. Outside the mean-field specification; needs a large-deviation or finite-N calculation. This is the gap a referee will name if Γ is kept anywhere near invasion.
2. Backward bifurcation for c_b < α < 1 (C2b). One quadrature: sign of −L_α²/2 + ½ε⁻²W with W the two-jump volume. If positive, Result 4's onset acquires a hysteresis regime, a new claim.
3. Skeptic-pool exact tails with clipping (C4). Changes numbers, not structure.
4. Skewness coefficient in a(h) (C6b). Changes nothing at the order the paper claims.

**Recommended next pass**

Do item 2 first; it is cheap and it decides whether the onset section needs a third class. Then decide whether item 1 is worth a dedicated calculation or whether the paper drops prepared-background invasion entirely and keeps Γ as a gain and as an observable. The rest of the packet reorganizes around x as the invasion channel, which is where the reviewers already are.

---
*End of packet v0.6.*
