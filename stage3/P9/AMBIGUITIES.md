# Stage 3 item P9 — ambiguities encountered

Earlier items' ambiguities (Stage 1 items 1–9, frozen as design v0.3.1 A4b; Stage 2
S2-*; Stage 2B S2B-A*; Stage 3 P5-A*, P7-A*) are unchanged and still govern.

---

## P9-A1 — c_b is not given, and the value is load-bearing  [RESOLVED BY OWNER]

**Where** Design v0.3.1 A4 item P9 lists r, κ, α, β, M₊, M₋ and λ, but not c_b.

**Why it is not a free declaration** With β = 0.4, whether a single *rejected*
message can activate an agent from rest depends on whether c_b < β or c_b > β, and
that decides which registered λ have a positive two-camp branch at all. At
c_b = 0.5 the zero branch is stable for λ < 2/ln 2 = 2.885, so λ = 1.5 and λ = 2
have no positive fixed point (only λ = 3, at A₊ = A₋ = 0.385368902); at c_b = 0.3
all three λ have one.

**Resolution** Both readings were computed from the C4.7 quadrature and put to the
owner before any run. Ruled **c_b = 0.3** on 2026-10-02, matching P4, the project's
other r = 1 item. Recorded in `config/p9_config.py` under `ruled`.

---

## P9-A2 — the relaxation criterion is below the finite-N noise floor

**Where** The owner's Stage 3 P9 estimand: "relaxation criterion |ΔA| < 10⁻³ over
10/ε".

**Problem** At the registered N = 10⁵ the *stationary* single-replicate standard
deviation of A₊ is 1.01 × 10⁻³ to 1.44 × 10⁻³, depending on λ. So |ΔA| < 10⁻³ cannot
be met by a single replicate even when the system is exactly at equilibrium and
nothing has been perturbed: the criterion is finer than the equilibrium fluctuation
it is measuring against.

**Two readings** (a) pathwise, per replicate — unachievable in principle at this N,
and would read as a stability failure when none has occurred; (b) on the replicate
mean, whose standard error is ≈ 1.8 × 10⁻⁴ and for which 10⁻³ is resolvable.

**Adopted** Reading (b), stated in every relaxation verdict row. The per-replicate
counts are reported beside it (11–50 of 50 depending on λ) so the raw pathwise
picture is visible. This is the same distinction the owner's P7 ruling (2) draws
between a mean-trajectory endpoint and a per-replicate diagnostic.

**For the owner** If the criterion is meant pathwise, it needs N ≳ 10⁶ at this λ
range, since the stationary sd of A scales like N^(−1/2) — about 100× the run cost.

---

## P9-A3 — two of the twelve perturbations do not exist

**Where** The owner's "perturbations ±0.05 in each A_±", at λ = 3.

**Problem** On the λ = 3 branch A₊ = A₋ = 0.483 against a camp mass of ½, so only
**0.0171** of the population is inactive in each camp — fewer than the 0.05 needed
to move that camp's activity *up* across the threshold. The +0.05 perturbation is
not a run that failed; it is a state that does not exist.

**Adopted** The two infeasible cells are reported with their reason and the available
inactive mass, and carry **no verdict**. The −0.05 perturbations at λ = 3 are
feasible and both relax, so stability is tested from at least one side at every λ.
A symmetric alternative would be to scale the perturbation to a fraction of the
available headroom, but that changes the registered ±0.05 and was not done.

---

## P9-A4 — N and the replicate count are not given for P9

**Where** A4 item P9 gives no N and no replicate count (unlike P5, P7 and P8).

**Adopted** DECLARED N = 10⁵ and 50 replicates, matching P5 and P7. Burn-in to 50/ε
and a measurement window [50, 100] were also declared, the burn-in matching the one
the owner declared for P10. Recorded in `config/p9_config.py` before the runs.
