# CROWD-1 Stage 3, item P10 — WITHDRAWN, NOT RUN

**Withdrawn by the owner, 2026-10-02:**

> "P10 withdrawn from Stage 3: the registered lag window is empty at h = 0.1 and
> 0.05; the Lux coefficient map stays in the manuscript as a derived closure without
> numerical certification."

**No simulation was run and no number is certified.** This directory exists so the
ledger can cite the withdrawal and the algebraic check below from a file rather than
from prose.

## Why the window is empty

The Stage 3 estimand measures H and J from the conviction drift and D from the lagged
increment variance, over lags in [5/(ρ+κ), 0.1/ε]. Under the R10 map ρ = p₀/h and
κ = k₀/h, so with p₀ = k₀ = 1 the lower edge is 5h/2 while the upper edge is fixed:

| h | ρ = κ | lag window | |
|---|---|---|---|
| 0.10 | 10 | [0.2500, 0.1000] | **empty** |
| 0.05 | 20 | [0.1250, 0.1000] | **empty** |
| 0.02 | 50 | [0.0500, 0.1000] | non-empty |

Non-empty iff **h ≤ 0.04**, i.e. at one point of the registered grid — which leaves
nothing to check the O(h) convergence against, and O(h) convergence is what the item
exists for.

## What is established: the derivation is algebraically correct

`p10_map_check.py` recomputes the coefficients from the Appendix C definitions (C6.1)
and limit formulas (C6.5, C6.6) and compares them with design v0.3.1 A4. **This is a
check of the derivation, not a numerical certification of the map against the
finite-N process.**

| quantity | recomputed from C6.1/C6.5/C6.6 | registered in A4 | deviation |
|---|---|---|---|
| H | 2.500000000 | 2.5 | 0 |
| J | 0.800000000 | 0.8 | −2.2 × 10⁻¹⁶ |
| D | 1.366666667 | 1.367 | −3.3 × 10⁻⁴ |
| J/D | 0.585365854 | 0.585 | +3.7 × 10⁻⁴ |
| K = (H − ε/2)/D | 1.463414634 | 1.46 | +3.4 × 10⁻³ |

H and J are exact; the other three deviations are the rounding of the registered
three- and four-significant-figure values, not disagreements. Intermediates:
ā₀ = 1.0, d₀ = 0.2, U = 1.5, q = 0.625.

Both wall-pinning conditions hold: **C6.8** H > ε (2.5 > 1), which pins the wells to
the walls at x = 0, and **C6.9** H − |Jx| > ε for all |x| ≤ 1 (2.5 − 0.8 = 1.7 > 1).
As design A4 already records, K = 1.46 means this is **not** a deep-well regime, so no
switching-exponent comparison was ever in scope.

## Files

```
p10_map_check.py              the algebraic check (deterministic, no RNG, no agents)
outputs/p10_map_check.json    its output, cited by RESULTS_LEDGER.md
README.md                     this file
```
