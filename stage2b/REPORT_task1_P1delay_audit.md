# Stage 2B, task 1 — P1-delay estimator audit, and its time-dependent replacement

Specification: `review_packet_v0_6_1.md`, memo section "PROCESS SPECIFICATION v0.6".
Design: `crowd1_cs_design_and_manuscript_brief_v0_3.md`, Part A (A4 item P1-delay,
A4a endpoints, A6 pass rule).
Authorisation: Stage 2B, a discrepancy investigation, **not** a re-certification.
No Stage 2 verdict is changed by anything in this file.

---

## 1. Audit of the estimator Stage 2 actually used

The owner asked four questions. Answers first, derivation after.

| Question | Answer |
|---|---|
| Exact formula or algorithm for the reported "invasion advantage" ratio | `Z1_mean(order 2) / Z1_mean(order 1)`, where `Z1_mean` is the sample mean over 10 000 independent single-seed trials per background of the number of **first-generation** activations produced by one injected target-aligned seed, averaged over 24 independent post-campaign backgrounds, at λ = 2.0, N = 100 000. Code: `stage2/crowd1/operator.py::frozen_trials`, driven by `stage2/crowd1/tests_s2.py::p1_operator_worker`. |
| Were recipient orientations and convictions frozen during the assay? | **Yes — both.** `run_frozen_operator(..., freeze=True)` holds every recipient's orientation *and* conviction at its saved post-campaign value for the whole of the seed's life. Nothing in the background relaxes, decays, or resets while the assay runs. |
| Did offspring lifetimes include residual conviction? | **The question does not arise: offspring lifetimes do not enter the quantity at all.** The assay is run with `max_gen = 1`, so the breadth-first expansion stops at the first generation. A newly activated agent's conviction is recorded (`offspring_c`) but it is never given a broadcast clock and never produces a second-generation birth, so no offspring lifetime — residual-conviction or otherwise — contributes. |
| Is the quantity a stationary operator, a frozen-background proxy, or a time-dependent descendant calculation? | **A frozen-background proxy.** It is not the stationary invasion operator (that is the τ₀ → ∞ limit, which it approaches but does not equal at finite τ₀), and it is not a time-dependent descendant calculation (the background does not evolve). |

### 1.1 What the proxy computes, in closed form

Write `Q₀(order) = E[cos²(0 − φ_post)]` for the post-campaign orientation law and
`p₊ = (1 + x)/2` for the stance law. A target-aligned seed (φ = 0) has lifetime
`L = ε⁻¹ ln(1/c_b) = ln 2` at the Stage 2 parameters (ε = 1, c_b = 0.5, seed c = 1),
broadcasts at rate λ, and each broadcast is accepted with probability cos²(0 − φ)
by the specification's acceptance rule. With the background frozen at age τ₀ for the
whole of the seed's life, every one of the seed's messages sees the *same* orientation
law, so

```
  E Z₁^frozen(τ₀) / λ  =  L · q_T(τ₀),        q_T(u) = e^{−ρu} Q₀ + (1 − e^{−ρu}) p₊
```

(the `q_T` factor is the probability that a *relaxed-at-age-u* recipient accepts: with
κ = 0 a reset is the only event that moves a silent agent's orientation, it sends φ to
`T_s`, and `cos²(0 − T_±) = 1` or `0` according to the stance, so a relaxed recipient
accepts with probability `p₊`).

### 1.2 Why the proxy shows **no** order advantage at τ₀ = 0 — the substantive finding

At τ₀ = 0 the formula collapses to `L · Q₀`, and

> **`Q₀ = E[cos²φ_post] = 1/2` for *both* campaign orders.**

This is not a coincidence of the chosen angles. P1 starts from initial law **I2**
(φ uniform), and the maximally mixed orientation law is invariant under every
projection of the message transition — result **R8(b)**. Each campaign pulse maps
φ to either θ (accept) or θ + 90° (reject) with probabilities cos²(θ − φ) and
sin²(θ − φ); applied to the uniform law this returns the uniform law, pulse after
pulse, for any pulse sequence whatsoever. So **the orientation channel carries no
order information at all** at τ₀ = 0, and the entire order advantage registered in
P1 lives in the *stance* channel (x₁ = 0 vs x₂ = 0.969846310) and becomes visible
only once resets have had time to convert stance into orientation.

That is exactly what Stage 2 measured: ratio 1.0006 with 95 % interval
[0.9922, 1.0090] at τ₀ = 0, rising to 1.97 by τ₀ = 10/ρ. The row was not a bug. It
was a correct measurement of a quantity that is *insensitive by construction* to the
effect the registered sentence asserts.

### 1.3 Classification of the Stage 2 P1-delay failure

Not a code bug (B) and not a model failure (M). The implementation computes the
quantity its own definition names, bit for bit reproducibly, and the process behaves
as the specification says. It is an **estimand mismatch (E)**: the frozen-background
proxy is not the quantity in which the registered claim "the order advantage is
present at every delay" is true. Logged as a new category in `BUGLOG.md`; the
Stage 2 INCONCLUSIVE verdict on that row stands unchanged in the record.

---

## 2. The owner's estimand: the time-dependent first-generation count E Z₁

### 2.1 Definition and reference value

The background **relaxes during the seed's life**: recipient convictions decay at
rate ε and recipient orientations reset to `T_s` at rate ρ. A message emitted at
seed-age `s` therefore meets a background of age `τ₀ + s`, so

```
  E Z₁(τ₀) = λ ∫₀^L q_T(τ₀ + s) ds
           = (λ/2) [ L + x ( L − e^{−ρτ₀}(1 − e^{−ρL})/ρ ) ]
```

and at ρ = ε = 1, L = ln 2 this is `(λ/2)[L + x(L − e^{−τ₀}/2)]`, whose τ₀ = 0 value
is the owner's reference `E Z₁ = (λ/2)[L + x_j(L − ½)]`. The two derivations were
compared before any measurement was made and agree **bit for bit** in IEEE double:
order 1 → `0.6931471805599453`, order 2 → `0.8804702609129119`, ratio
`1.2702500790692697` against the owner's stated 1.270.

### 2.2 Implementation

`crowd1/operator.py` gained one optional parameter, `relax_rho`, whose default `0.0`
reproduces the Stage 2 behaviour **bit for bit** — verified by re-running the Stage 2
P1 operator cell and comparing to the archived `stage2/outputs/raw/p1_operator.csv`
(all six delays identical to the last printed digit, for order (40, 140, 50),
replicate 0, N = 100 000).

The relaxation is **sampled exactly rather than simulated**. With κ = 0 a reset is
the only event that moves a silent agent's orientation; it sends φ to `T_s`; and it
changes neither c nor s. So at absolute time u after the save the orientation is
`T_s` with probability `1 − e^{−ρu}` and the saved orientation otherwise,
independently across agents. Memorylessness lets that coin be flipped at the moment
of receipt and re-flipped from the previous decision time on a later hit, which is
what the `relaxed` / `relax_t` bookkeeping does. Conviction decay is applied
analytically to the absolute message time (exact for a background that has received
nothing). No reset clock is added to the operator kernel and no approximation is
substituted for the process.

### 2.3 Results

λ = 2.0, N = 100 000, 24 independent post-campaign backgrounds per order per
kernel, 10 000 single-seed trials per background (2.88 × 10⁶ trials per cell),
master seed 20261002, state preparation seeded identically to Stage 2 so that both
kernels are assayed on *the very same* post-campaign states.
Uncertainties are the standard error over the 24 backgrounds of the paired ratio.

**(a) Frozen-background proxy — the Stage 2 quantity, named as a proxy**

| τ₀/ρ | E Z₁^frozen/λ, order 1 (x=0) | exact | order 2 (x=0.9698) | exact | measured ratio | exact ratio |
|---|---|---|---|---|---|---|
| 0.0 | 0.347215 | 0.346574 | 0.347367 | 0.346574 | 1.00044 ± 0.00406 | **1.0000000** |
| 0.5 | 0.347110 | 0.346574 | 0.480217 | 0.478828 | 1.38347 ± 0.00424 | 1.3816048 |
| 1.0 | 0.346106 | 0.346574 | 0.559817 | 0.559044 | 1.61747 ± 0.00492 | 1.6130598 |
| 2.0 | 0.347585 | 0.346574 | 0.638008 | 0.637207 | 1.83554 ± 0.00603 | 1.8385919 |
| 5.0 | 0.346994 | 0.346574 | 0.681379 | 0.680432 | 1.96366 ± 0.00501 | 1.9633115 |
| 10.0 | 0.347327 | 0.346574 | 0.682419 | 0.682681 | 1.96477 ± 0.00608 | 1.9698023 |

**(b) Time-dependent first-generation count E Z₁ — the owner's estimand**

| τ₀/ρ | E Z₁/λ, order 1 | exact | order 2 | exact | measured ratio | exact ratio |
|---|---|---|---|---|---|---|
| 0.0 | 0.345987 | 0.346574 | 0.441062 | 0.440235 | **1.27479 ± 0.00531** | **1.2702501** |
| 0.5 | 0.345925 | 0.346574 | 0.535973 | 0.535636 | 1.54939 ± 0.00475 | 1.5455197 |
| 1.0 | 0.347100 | 0.346574 | 0.595296 | 0.593500 | 1.71506 ± 0.00454 | 1.7124792 |
| 2.0 | 0.347738 | 0.346574 | 0.651669 | 0.649883 | 1.87402 ± 0.00539 | 1.8751663 |
| 5.0 | 0.348048 | 0.346574 | 0.681888 | 0.681063 | 1.95918 ± 0.00411 | 1.9651325 |
| 10.0 | 0.346988 | 0.346574 | 0.681075 | 0.682686 | 1.96282 ± 0.00624 | 1.9698145 |

Both kernels reproduce their own exact reference at every delay. Computing
(measured − exact)/sem for all twelve ratio rows, every one is within 1.5 standard
errors: the largest magnitudes are τ₀ = 5 in (b) at **−1.450 σ** and τ₀ = 10 in (b)
at −1.121 σ, then τ₀ = 1 in (a) at +0.897 σ; the remaining nine are below 0.9 σ. The
mean signed z over the twelve rows is −0.030, so there is no systematic offset in
either kernel.

### 2.4 Reading

- For the **time-dependent first-generation count**, the between-order ratio is
  **greater than one at every delay including τ₀ = 0** (1.275, 1.549, 1.715, 1.874,
  1.959, 1.963), and the τ₀ = 0 value matches the owner's reference 1.270 to within
  the Monte-Carlo error. The ratio increases monotonically to the limit
  `1 + x₂ = 1.9698`.
- For the **frozen-background proxy**, the ratio is exactly one at τ₀ = 0 for the
  reason in §1.2, and is strictly below the time-dependent ratio at every finite
  delay, because freezing denies the background the relaxation that occurs while the
  seed is alive.
- The two coincide only as τ₀ → ∞, where both tend to `1 + x₂`; the exact limits are
  `1.9698023` (frozen) and `1.9698145` (time-dependent), differing only by the
  `e^{−τ₀}` term's residue at τ₀ = 10.

### 2.5 Replacement wording for the registered sentence

The registered sentence in design A4 ("P1-delay: the order advantage is present at
every delay") **stays failed in the record** — the Stage 2 verdict on the row is not
revised, and the quantity that failed is the frozen-background proxy.

Proposed replacement, for the owner to accept or reject (not adopted here; the design
is authoritative and is not edited by this investigation):

> **P1-delay.** For the time-dependent first-generation count
> `E Z₁(τ₀) = λ ∫₀^L q_T(τ₀ + s) ds`, the order advantage is present at every delay,
> with between-order ratio `1 + x₂(L − e^{−ρτ₀}(1 − e^{−ρL})/(ρL))` rising
> monotonically from `1.270` at τ₀ = 0 to `1 + x₂ = 1.970` as τ₀ → ∞.
> The *frozen-background proxy* `E Z₁^frozen(τ₀) = λ L q_T(τ₀)`, in which the
> recipients' orientations and convictions are held at their post-campaign values for
> the whole of the seed's life, has between-order ratio **exactly one at τ₀ = 0** and
> is therefore not a test of this claim: from initial law I2 the maximally mixed
> orientation law is invariant under every projection (R8(b)), so the frozen
> orientation channel carries no order information and the whole advantage is carried
> by the stance channel, which only resets can express.

---

## 3. Files

- `p1delay_reference.py` — the assay and both exact references.
- `outputs/raw/p1delay_reference.json` — 1 152 measured rows (2 kernels × 2 orders ×
  24 backgrounds × 6 delays), per-cell summaries, paired ratios, exact references,
  and every seed.
- `../stage2/crowd1/operator.py` — the `relax_rho` extension (default 0.0 is
  bit-identical to Stage 2).
