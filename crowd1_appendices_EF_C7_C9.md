# CROWD-1 — APPENDICES E AND F: C7–C9 derivation outputs (verbatim)

For the Crowd1 project folder. These are the two C7–C9 outputs cited by design v0.3/v0.3.1 Part A (P4, P6, P7) and omitted from the project at Stage 2 (Stage 2 AMBIGUITIES S2-1). Appendix E is the complete ChatGPT pass. Appendix F is Claude's closing pass (the frozen-rate bridge, the class-2 f_c bisection, the fast-clock operator); Claude's first C7–C9 pass was lost when that chat failed, and only this closing pass exists. Status labels inside are the derivers' own.

---

## APPENDIX E — ChatGPT, C7–C9 against specification v0.6

**[EXACT — scope]** All results below concern the mean-field process, with N→∞ taken first. "Collapse" in C7 is a declared activity marker, not a claim of finite-time extinction. Numerical estimates and rigorous enclosures are distinguished.

**[OPEN — principal qualification]** C7 does not admit a uniform stationary-tracking bound based only on (1−r)λM/ε. Initial relaxation, variation of the incoming intensity, and loss of stability at the fold must also be controlled. The conditional bound and numerical comparison below make those restrictions explicit.

**[EXACT — C7(a): counter law and slow variable]** In the stated I1, T-only experiment, the responsive population is M=1; the campaign reach f is not an invariant responsive-pool size. Put ν(t)=λA(t), H(t)=∫₀ᵗν(s)ds. After one pulse, n(t)=U+Pois(H(t)), U~Bernoulli(f), and therefore w_n(H)=(1−f)e^{−H}H^n/n! + f·1_{n≥1}e^{−H}H^{n−1}/(n−1)!. The counter marginal is exact; conviction and counter are generally correlated. Useful slow variables are z=(1−r)H, B(t)=E[r^{n(t)}]=(1−f+fr)e^{−(1−r)H(t)}, with ż=(1−r)ν, Ḃ=−(1−r)νB. The remaining nominal dose budget is αB/(1−r).

**[EXACT — C7(a): conditional tracking inequality]** Let π_{ν,d} denote the clipped r=1 stationary conviction law with prescribed intensity ν and dose d. Compare the actual joint law with μ̂_t=Σ_n w_n(H(t)) π_{ν(t),αr^n} ⊗ δ_{r^n}. Use Wasserstein distance with cost |c−c'|+|r^n−r^{n'}|. On a window [t−T,t], suppose ν≤ν_max, |ν(s)−ν(t)|≤K_ν|t−s|. Then a coupling gives
D_T := W₁(μ_t, μ̂_t) ≤ e^{−εT} + 2(1−r)ν_max T(1+αν_max/ε) + min(1,α)K_ν/ε².
Clipping is nonexpansive, which is essential to these estimates.

**[LIMIT — C7(a): small-parameter form]** Define Γ=ν_max/ε, η=(1−r)Γ. Assume Γ,α bounded and K_ν/ε² ≤ C_ν η. Choosing T=ε⁻¹log(1/η), with t≥T, yields D_T ≤ η[1+2(1+αΓ)log(1/η)+min(1,α)C_ν]. Thus slaving holds in this metric at order η log(1/η), under the additional slow-intensity assumption. To translate into activity, with the frozen conviction density bounded by B_b near c_b, |A−F(A,H)| ≤ 2√(2B_b D_T), F(A,H)=Σ_n w_n(H)P_{λA}(αr^n). If the selected frozen branch A₊(H) satisfies 1−∂_A F ≥ γ>0 in a neighborhood containing A(t) and A₊(H(t)), then |A(t)−A₊(H(t))| ≤ 2√(2B_b D_T)/γ.

**[OPEN — C7(a): limitation]** Neither the slow-intensity condition nor the branch neighborhood follows from η≪1 alone. A pulse creates an initial transient, and γ→0 at a fold. The displayed estimate is not a uniform fold-time theorem.

**[EXACT — C7(b): mixture coefficient]** Write a=ν/ε and P_ν(d)=aℓ(d)+a²q₂(d)+O(a³), ℓ(d)=[log(min(1,d)/c_b)]₊. Using the established G, q₂(d)=½[G(d)−log²(d/c_b)] for c_b<d<1; −½log²(1/c_b) for d≥1; and for 0<d≤c_b, q₂(d)=∫₀^∞[log(min{1,d(1+e^{−u})}/c_b)]₊du, zero when 2d≤c_b, positive when c_b/2<d≤c_b. The mixture coefficients are ℓ̄(H)=Σ_n w_n(H)ℓ(αr^n), q̄₂(H)=Σ_n w_n(H)q₂(αr^n). Provided ℓ̄>0, the local onset is backward precisely when q̄₂>0.

**[EXACT — C7(b): no class-2 member is necessary]** c_b=0.6, α=2.5, r=0.4, f=1. Frozen doses 1, 0.4, 0.16, …; the first is forward class 1, every remaining dose is class 3. Nevertheless q₂(0.4)=0.093005830, and q̄₂(H)=e^{−H}[−½log²(1/0.6)+0.093005830 H], so the mixture onset is backward for H>1.402830435; at H=2, q̄₂=0.007516556>0. [CLOSURE — scope] This demonstrates the frozen-mixture mechanism; its r=0.4 is not offered as a slow-habituation example.

**[CLOSURE — C7(c): trajectory and fold]** Once on the selected stable branch, A_ad(t)=A₊(H_ad(t)), Ḣ_ad=λA₊(H_ad), t_ad(H)=∫₀^H du/(λA₊(u)). A fold satisfies F(A_f,H_f)=A_f, ∂_AF(A_f,H_f)=1, and the frozen collapse time is t_ad,f=∫₀^{H_f}du/(λA₊(u)). This construction requires branch selection by the actual preparation.

**[CLOSURE — C7(c): numerical comparison with C2]** α=2, β=0, r=0.99, λ=3, ε=1, c_b=0.5, ρ=κ=0, f=1, one T pulse from I1 (c(0)=1, n(0)=1, η=0.03). Transient collapse marker t†=inf{t: A(t)≤A_f}. Frozen fold activity A_f=0.5603318; frozen fold hazard H_f=158.354403; adiabatic fold time t_ad,f=66.30915; C2 Picard quadrature 70.31256 (run 1), 70.25815 (run 2); independent refined joint-law calculation 70.29963. Both C2 comparisons satisfy |t_ad,f−t†|/t† < 6%. No fitted time offset was applied. [OPEN — numerical scope] Convergence checks, not a certified interval.

**[EXACT — C7(d)]** The full joint-law evolution ∂_tμ_n=ε∂_c(cμ_n)−λAμ_n+λA(J_{n−1})_#μ_{n−1}, J_n(c)=min(1,c+αr^n), A=Σ_nμ_n((c_b,1]), equivalent to C2's ordered-time quadrature and self-consistent Volterra equation. [CLOSURE/OPEN — exclusions] When (1−r)λM≳ε, use the joint law. A uniform fold-time error theorem remains open.

**[EXACT — C8(a): used-counter invasion, κ=0]** μ₀=1−f, μ_c=f, p_{g,±}=(1±x_g)/2, n₀=0, n_c=m_T, ℓ_{αg}=ε⁻¹[log(min(1,αr^{n_g})/c_b)]₊, ℓ_{βg} analogous; a_±=Σ_gμ_g p_{g,±}ℓ_{αg}, b_±=Σ_gμ_g p_{g,±}ℓ_{βg}. For target-aligned parents the nonzero eigenvalues are those of K₂=λ[[a₊,b₊],[b₋,a₋]]; when both camp blocks are reachable R_inv=(λ/2)[a₊+a₋+√((a₊−a₋)²+4b₊b₋)]; if b₋=0 a positive T seed reaches only the positive block and its reproduction number is λa₊. For m_T=0 with x=(1−f)x₀+fx_c this reduces to (λ/2)[ℓ_α+√(x²ℓ_α²+(1−x²)ℓ_β²)], subject to reachability. [EXACT — correction to "unreachable"] αr^{m_T}≤c_b makes accepted cohort offspring inactive; the whole cohort is unreachable only if also βr^{m_T}≤c_b.

**[EXACT — C8(b): original R8(a), retaining its reset clock]** The two campaigns leave x₁=0, x₂=0.969846310 and counters n₄₀=1, n₅₀=n₁₄₀=2, n_T=0. With α=1, β=¼, r=½, c_b=½ the largest accepted single-shot magnitudes through the used bases are r|cos80°|=0.08682409 and r²|cos100°|=0.04341204; direct offspring production through either used basis is zero. However an initially active 40°, positive seed resets to T=0° when ρ>0; that endpoint class is fresh, so R₁=0.346573590λ, R₂=0.682696708λ, R₂/R₁=1.969846310. The factor survives through the reset route. Concrete check ρ=ε=1, seed conviction 1: expected time broadcasting T is log2−½=0.193147181; expected first-generation counts 0.096573590λ and 0.190235130λ, same ratio. [EXACT — exhausted reachable classes] A seed constrained to the used basis has reproduction number zero in both preparations; on an endpoint background with n_T≥1 both endpoint doses are subthreshold and K₂=0.

**[EXACT — C8(c): finite operator for κ>0]** Types b=(g,θ,o), θ∈{0,±δ,90°,90°±δ}, o∈{a,r}; d_b=r^{n_{g,j(θ)}}cos2θ·(α if a, −β if r); ℓ_b=ε⁻¹[log(min(1,|d_b|)/c_b)]₊; birth orientation θ on acceptance, θ+90° on rejection; stance sign(d_b). ζ_κ=(ρ+κcos2δ)/(ρ+κ); p_{a,g}(θ;κ)=(1+ζ_κx_g cos2θ)/2; p_{r,g}=1−p_{a,g}. With W_b=h_{ρ+κ}(ℓ_b)δ_{φ_b}+[ℓ_b−h_{ρ+κ}(ℓ_b)]π_{s_b}, h_v(ℓ)=(1−e^{−vℓ})/v, the finite matrix is K_{(g',θ,o),b}=λμ_{g'}p_{o,g'}(θ;κ)W_b({θ}); spectral radius on seed-reachable types. [LIMIT — first-order parent-motion correction] W^{(0)}=h_ρδ_φ+(ℓ−h_ρ)D_s; W^{(1)}=h'_ρ(δ_φ−D_s)+((ℓ−h_ρ)/ρ)(Q_s−D_s), h'_ρ=((ρℓ+1)e^{−ρℓ}−1)/ρ², ρ→0 limit W^{(1)}=(ℓ²/2)(Q_s−δ_φ); K=λμ_{g'}p_{o,g'}(θ;κ)[W^{(0)}+κW^{(1)}]+O(λκ²L³), remainder bounded in column-sum norm by (2/3)λκ²L³. With ρ>0 and κ/ρ≪1, p^{(1)}_{a,g}(θ)=−x_g cos2θ(1−cos2δ)/(2ρ), and R(κ)=R(0)+κ(vᵀK₁u)/(vᵀu)+O(κ²) for an isolated simple dominant eigenvalue. [OPEN] Continuous reachability and an isolated dominant block required; the seed-reachable radius can jump at κ=0.

**[EXACT — C9(a)]** A_max=sup A(t); I=∫₀^∞A dt; T_act=Leb{t: A(t)>A_max/2}. Case: α=1, β=0.4, r=10⁻⁶, λ=0.5, ε=1, c_b=0.5, c_h=0.01, ρ=κ=0, f=0.25, I1, one T pulse at zero. Every first T receipt sets conviction to one; subsequent deposits total at most B=r/(1−r); each first-exposed agent is active throughout its first L=log2 of age and never after L₊=log(1/(c_b−B)). With Z_D(f) solving 1−Z_D=(1−f)e^{−λDZ_D} and P_D(f)=fe^{λD}/(1−f+fe^{λD}): LZ_L≤I≤L₊Z_{L₊}; P_L≤A_max≤P_{L₊}; L≤T_act≤L₊. Enclosures at f=0.25: A_max∈[0.32037724, 0.32037746]; I∈[0.22968922, 0.22969009]; T_act∈[0.69314718, 0.69314919]. Reach table: f=0.10: 0.13580, 0.09963, 0.69315; 0.25: 0.32038, 0.22969, 0.69315; 0.50: 0.58579, 0.41095, 0.69315; 0.75: 0.80926, 0.56233, 0.69315. Two-pulse coincident {T,T⊥}: order (T,T⊥) ends at c=1, n_T=2, same enclosures; order (T⊥,T) ends at c=β+αr=0.400001<c_b, so A_max=I=T_act=0.

**[EXACT — C9(b): r=1, α≥1, positive T-only sector]** Every receipt refreshes conviction to one. L=ε⁻¹log(1/c_b), R=λL. For a fresh activating pulse of reach f, A(t)=fe^{λt}/(1−f+fe^{λt}) for 0≤t<L, then A(t)=1−exp[−λ∫_{t−L}^tA]. For R>1 persistent activity is the unique positive A*=1−e^{−RA*}; every f>0 converges to it. For R≤1, A(t)→0 for every f≤1. Hence f_c(R)=0 (infimum, not attained) for R>1; no activating reach for R≤1. Basin separator for a general initial law μ within this sector: μ((c_b,1])=0. [EXACT/OPEN] This α≥1 case has no nonzero finite-amplitude ignition threshold; a nontrivial unstable-branch basin boundary must be sought in the backward-onset regime.

**[EXACT — C9(c)]** For a declared constant v per active-agent-time, Y(t)−Y(0)=v∫₀^tA(s)ds; the C9(a) example gives Y(∞)−Y(0)∈v[0.22968922, 0.22969009]; the reversed campaign gives zero; on the C9(b) persistent branch Y(t)−Y(0)=vA*t+o(t). No market mechanism specified.

**[OPEN — remaining gates]** C7 has an explicit conditional small-parameter bound and observed agreement within 6%; a certified numerical interval and a uniform analytical fold-time bound remain open.

---

## APPENDIX F — Claude, C7–C9 closing pass (frozen-rate bridge; class-2 f_c; fast-clock operator)

## C7, closing: the frozen-rate bridge

Definition. F(Λ, ν; r) is the activation probability of an agent started at (c = 1, n = 1) and driven at constant rate ν, read at time Λ/ν. Conditional on Λ the counter law is exactly 1 + Poisson(Λ) whatever the rate history, so F differs from the exact single-agent law only through the rate inside the memory window; it carries the geometric past and the count–recency correlation that the dose-mixture object drops. The bridge is A = F(Λ, λA), Λ̇ = λA, upper fixed point followed from A = 1. Tabulated on ν ∈ [0.4, 2.5] × Λ ∈ [0, Λ_max] by independent-agent runs (M = 2·10⁴), same parameters as before (ε = 1, α = 1, c_b = 0.4, λ = 2.5, f = 1).

| r | η | Λ_c bridge (A_fold) | Λ_c naive | Λ exact at A_fold/2 | bridge error | naive error |
|---|---|---|---|---|---|---|
| 0.95 | 0.125 | 20.35 (0.65) | 18.64 | 25.38 | 20% | 27% |
| 0.90 | 0.25 | 10.39 (0.65) | 8.30 | 13.82 | 25% | 40% |
| 0.80 | 0.50 | 5.42 (0.71) | 3.29 | 7.71 | 30% | 57% |

Bulk, A_exact against A_bridge: r = 0.95 gives 0.8551/0.8544 at 0.5Λ_c, 0.8388/0.8390 at 0.7Λ_c, 0.8117/0.7890 at 0.85Λ_c; r = 0.9 gives 0.9% at 0.5 and 0.7Λ_c; r = 0.8 gives 4.3% and 2.5%. Over the first 70% of the run the bridge error in A is below 0.1η at all three η; the naive object is 5–20% off over the same range. LIMIT, verified: the O(η) bulk bound of C7(a) holds for the frozen-rate law. The residual at the collapse point is not O(η): 0.20, 0.25, 0.30 for η = 0.125, 0.25, 0.5, sub-linear, which is the slow passage through the fold — the exact process reaches the bridge's fold with conviction built at the higher rate of the preceding window and overshoots by about 2.5/ε in time. On this scaling a 10% tolerance on the collapse point needs η ≲ 0.02, r ≥ 0.992 at λ = 2.5. Gate status: met for the branch, not met for the collapse point by a quasi-static method; closing it needs a two-variable scheme (Λ plus an exponentially averaged rate) or the fold-passage asymptotics, both OPEN.

What this settles for the manuscript. The memo's traversal sentence rests on the dose-mixture object, which is wrong at order one near the collapse and has the wrong sign of n-dependence everywhere (activation rising with the counter in the exact process, falling in the mixture). The r = 1 class structure of R4 describes the running habituating crowd only through F, whose fold is a different point from the single-dose or mixture fold. The clipped class-2 coefficient from the previous pass is confirmed independently below.

## C9(b), closing: basin boundary in class 2 backward

Parameters r = 1, α = 0.5, c_b = 0.3, ε = 1: ℓ = ln(5/3) = 0.511 < √G(½) = 1.282, backward. EXACT by quadrature (M = 4·10⁴, T = 24): the stationary response P_ν(c > c_b) gives λ(ν) = ν/P_ν falling from λ_c = 1.958 at ν → 0 to λ_fold = 1.49 at ν ≈ 0.55 (A_fold ≈ 0.37), then rising. The small-ν expansion νℓ + ν²·½(π²/6 − ℓ²) reproduces P to 2% at ν = 0.05 and 0.1 (0.0273 against 0.0268, 0.0580 against 0.0566): independent confirmation of G.

Pulse of reach f on I1, cohort at c₀ = α, N = 5·10⁴, persistence judged at t = 40 (upper branch A* = 0.63, 0.75, 0.81 at the three λ):

| λ | f_c | A_u(λ) unstable branch | f_c/A_u |
|---|---|---|---|
| 1.60 | 0.127 ± 0.002 | 0.15 | 0.85 |
| 1.75 | 0.038 ± 0.001 | 0.050 | 0.76 |
| 1.90 | 0.0086 ± 0.0008 | 0.0118 | 0.73 |

Near λ_c the unstable branch is A_u = (1 − λℓ)/(λ²q₂), q₂ = ½(π²/6 − ℓ²) = 0.692, so f_c(λ) ≈ 0.75·(1 − λℓ)/(λ²q₂) for λ → λ_c⁻, the factor 0.75 being the reproductive value of a stationary active agent relative to a freshly dosed one. f_c → 0 as λ → λ_c, rises to O(0.1) by λ = 1.6, and no reach ignites below λ_fold = 1.49. This is the finite-amplitude content the class-1 case lacks: a reach–intensity trade-off with a hard floor in λ. OPEN: f_c on (λ_fold, 1.6) and the exact prefactor.

## C8(c), closing: the (ρ+κ)ℓ ≫ 1 operator

EXACT in the fast-clock regime. Parents hold the I3 orientation law throughout life, and a child born off-target returns to T_s within 1/(ρ+κ) ≪ ℓ, so types reduce to stance s (with the C8(a) subpopulation split). A parent of stance s broadcasts T_s with weight ρ/v and T_s ± δ with weight κ/v, v = ρ + κ; write κ_θ = 1 or cos 2δ for the two. Population-averaged acceptance of such a message is π_s(κ_θ) = ½(1 + sζxκ_θ), ζ = (ρ + κcos2δ)/v. Per broadcast, expected same-stance child lifetime a_s = (ρ/v)π_s(1)ℓ(αrⁿ) + (κ/v)π_s(cos2δ)ℓ(αcos2δ rⁿ), opposite-stance b_s = (ρ/v)(1 − π_s(1))ℓ(βrⁿ) + (κ/v)(1 − π_s(cos2δ))ℓ(βcos2δ rⁿ), with ℓ(·rⁿ) → fℓ(·r^{m_T}) + (1−f)ℓ(·) and x by subpopulation as in C8(a). Matrix λ[[a₊, b₋],[b₊, a₋]], R_inv = (λ/2)[a₊ + a₋ + √((a₊ − a₋)² + 4b₊b₋)]; for β ≤ c_b and a + seed, R_inv = λa₊. At κ = 0 it is C8(a); against the slow regime the parent-side factor is κ/v instead of κℓ/2, and ζ enters the listener side in both.

## Standing

Closed this pass: the bridge's branch (bound verified), f_c in class 2 backward (numbers and the near-λ_c form), the fast-clock operator, and an independent check of G. Open, ranked: (1) the collapse point beyond quasi-statics; (2) f_c near λ_fold; (3) whether R4's traversal survives in any form once F replaces the dose mixture — my reading is that it does not, and the manuscript should state the running crowd's collapse as the fold of F with the slow-passage delay.

NOTE FOR THE PROJECT. The f_c values in Appendix F were obtained by simulation (N = 5·10⁴, persistence judged at t = 40) with Monte Carlo error bars, not by an exact derivation; the design's registered f_c values were taken from this table. Stage 2 measured 0.1334, 0.0438, 0.0073 by the 50%-point estimator against realized reach. The discrepancy is the subject of Stage 2b item 2.
