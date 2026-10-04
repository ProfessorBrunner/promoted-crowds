# Stage 3 item P5 — ambiguities encountered

Stage 1 items 1–9 (frozen as design v0.3.1 A4b), Stage 2 items S2-*, and Stage 2B
items S2B-A* are unchanged and still govern. This file lists only what P5 newly
encountered. Nothing here modifies the specification or the design; where a reading
had to be chosen, both readings are stated and the choice is declared.

---

## P5-A1 — registered replicate count versus A4a's frozen precision target

**Where** Design v0.3.1 A4 item P5 ("N = 10⁵, 50 replicates per cell") against A4a
("Where no numerical outbreak probability is predicted, ±0.03 is a precision target
for the estimate, not an agreement tolerance").

**Problem** At 0/50 and 50/50 the Wilson half-width is 0.03567, which does not meet
the 0.03 precision target. The two frozen statements cannot both be satisfied with
50 replicates.

**Reading 1** 50 replicates as A4 literally registers, accepting a half-width above
the target.
**Reading 2** Extend until the target is met, since A4a is a frozen definition that
governs probability estimates generally.

**Adopted** Both, reported side by side (REPORT_P5.md §3.2). The registered 50 are
reported as the registered estimate; 400 further replicates bring the half-width to
0.00423. The extension runs only to t = 20, because survival is A(20) > 0, so it
cannot and does not touch any window statistic. No verdict depends on which reading
is taken — the proportions are 0 and 1 under both.

---

## P5-A2 — A4a's outbreak criterion is degenerate for P5

**Where** Design v0.3.1 A4a ("outbreak = ever-active fraction > 1% of N within the
horizon") against A4 item P5 ("report outbreak probability at f = 0.01 and 0.1").

**Problem** In P5, α = 2 > c_b and the population starts at I1 (φ = T₊), so the
campaign pulse is accepted with probability 1 and **every** cohort member activates.
At f = 0.01 the cohort alone is already ≈ 1 % of N, so one further activation decides
the criterion. The measured outbreak probability is 1.000 in all four cells,
including both λ = 1 cells, where activity provably dies before t = 20 (0/450
survival, and the exact mean field is at 10⁻¹⁰). The criterion is measuring the
campaign, not the epidemic, and it cannot distinguish the supercritical from the
subcritical case — which is the one thing P5's finite-N sentence is about.

**Reading 1** A4a literally: report the degenerate 1.000 and note it.
**Reading 2** The owner's P5 survival criterion A(20) > 0, which separates the cases
cleanly (0/450 at λ = 1, 450/450 at λ = 2).

**Adopted** Both, under their own names, with **no verdict on the A4a quantity**
(A4 registers no number for it). The owner's survival criterion carries the
finite-N content. A4a is not modified.

**For the owner** If an outbreak probability is wanted for P5 as a *population*
endpoint distinct from survival, the criterion needs a threshold above the campaign
reach — for instance ever-active fraction > 1 % of N **in excess of the realized
reach**, or simply a higher threshold. That is a change to a frozen definition and
is not made here.

---

## P5-A3 — c_h is not named for P5

**Where** Design v0.3.1 A4 item P5 lists r, α, β, c_b, κ, ρ, the initial law and the
pulse, but not c_h. Other items (P1, P2 via c_h = 0.01, P7) do name it.

**Adopted** DECLARED c_h = 0.01, matching every other item that names it, and
recorded in `config/p5_config.py` before the runs. **Verified immaterial rather than
assumed**: with β = 0, I1 and a T₊ pulse every deposit is +α cos 0, so no conviction
is ever negative and no stance ever leaves +. Measured across all four cells: minimum
final conviction ≥ 0 and zero agents with stance − in every replicate. No value of
c_h in [0, c_b) could change a registered number.

---

## P5-A4 — "A_max" as a replicate maximum versus a mean-field level

**Where** Not a P5 ambiguity — P5 registers no A_max — but P5 measures one, and the
quantity is a registered endpoint in **P7**, which is not authorised.

**Observation** The measured A_max at λ = 2 is 0.5079, against the mean-field
A* = 0.5. The maximum of a fluctuating finite-N trajectory exceeds its mean level by
construction, so a per-replicate A_max is a biased estimator of any mean-field level,
with a bias that grows with the window length and shrinks with N.

**Status** Flagged, not resolved. The owner's Stage 3 P7 definition already
anticipates this ("A_max and T_act computed per replicate and averaged, with the
mean-trajectory versions reported beside them"); this is evidence that the two will
differ measurably, and the size of the gap at N = 10⁵ is about 1.6 % here.
