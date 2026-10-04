"""T3 part (b): hand-computed table of coincident-pulse outcomes.

Every expected value in this file was derived by hand from the MESSAGE
TRANSITION of specification v0.6 and is written here in closed form (no value
was copied from a simulator run).  Each case is deterministic: either the
acceptance probability of every message is exactly 0 or exactly 1, or the
quantity checked (the counter vector, the class identifiers) does not depend
on the outcomes at all.

The derivations are reproduced in README.md, section "T3(b) hand table".
"""

from __future__ import annotations

import math

from .runner import RunConfig

LN = math.log

HAND_CASES = []


def _case(name, cfg, expect, derivation):
    HAND_CASES.append({"name": name, "cfg": cfg, "expect": expect,
                       "derivation": derivation})


# ---------------------------------------------------------------------------
# H1  decay between events, deadline refresh, deactivation and reactivation
# ---------------------------------------------------------------------------
_c1 = -0.6
_c2 = _c1 * math.exp(-1.0) - 0.3           # receipt at t = 1
_c3 = _c2 * math.exp(-1.0) - 0.1           # receipt at t = 2
_c4 = _c3 * math.exp(-1.0) - 0.075         # receipt at t = 3
_case(
    "H1_decay_deadline_refresh",
    RunConfig(N=4, agent_class="process", eps=1.0, c_b=0.5, c_h=0.01,
              alpha=0.6, beta=0.4, r=0.5, lam=0.0, f=1.0,
              pulses=((0.0, 90), (1.0, 90), (2.0, 0), (3.0, 90)),
              initial_law="declared", declared_phi=90, declared_c=0.0,
              declared_s=1, t_end=6.0, stop_on_extinction=False),
    {
        "pulse_out": [1, 1, 0, 1],
        "counters": {0: 4},
        "phi": 90,
        "s": -1,
        "n_intervals": 2,
        "t_first_act": 0.0,
        "t_first_deact": LN(0.6 / 0.5),
        "t_last_deact": 1.0 + LN(abs(_c2) / 0.5),
        "act_time": LN(0.6 / 0.5) + LN(abs(_c2) / 0.5),
        "c_at_t_end": _c4 * math.exp(-3.0),
    },
    "phi=90 start. theta=90 accepted (cos^2 0 = 1), deposit r^0 cos180 (+alpha) "
    "= -0.6; theta=0 rejected (cos^2 90 = 0) sends phi to 0+90 = 90, deposit "
    "r^2 cos0 (-beta) = -0.1.  Full arithmetic in README.",
)

# ---------------------------------------------------------------------------
# H2  clipping to [-1, 1]; post-rejection ray theta+90 inside the same class
# ---------------------------------------------------------------------------
_case(
    "H2_clipping_and_rejection_ray",
    RunConfig(N=4, agent_class="process", eps=1.0, c_b=0.5, c_h=0.01,
              alpha=0.6, beta=1.0, r=0.5, lam=0.0, f=1.0,
              pulses=((0.0, 0), (0.0, 90), (0.0, 0)),
              initial_law="I1", t_end=2.0, stop_on_extinction=False),
    {
        "pulse_out": [1, 0, 1],
        "counters": {0: 3},
        "phi": 0,
        "s": 1,
        "n_intervals": 1,
        "t_first_act": 0.0,
        "t_first_deact": LN(1.0 / 0.5),
        "act_time": LN(1.0 / 0.5),
        "c_at_t_end": 1.0 * math.exp(-2.0),
    },
    "0.6 then +0.5 (clip 1.1 -> 1.0) then +0.15 (clip 1.15 -> 1.0).",
)

# ---------------------------------------------------------------------------
# H3  class identifiers: opposite rays share one identifier, keyed by mod 90
# ---------------------------------------------------------------------------
_case(
    "H3_class_identifiers",
    RunConfig(N=8, agent_class="process", eps=1.0, c_b=0.5, c_h=0.01,
              alpha=0.0, beta=0.0, r=0.5, lam=0.0, f=1.0,
              pulses=((0.0, 40), (0.0, 130), (0.0, 40), (0.0, 90),
                      (0.0, 0), (0.0, 70)),
              initial_law="I1", t_end=1.0, stop_on_extinction=False),
    {
        # class 0 = basis {0, 90} (target); class 1 = basis {40, 130};
        # class 2 = basis {70, 160}
        "counters": {0: 2, 1: 3, 2: 1},
        "n_classes": 3,
        "class_of": {40: 1, 130: 1, 90: 0, 0: 0, 70: 2},
        "c_at_t_end": 0.0,
        "n_intervals": 0,
    },
    "Counters advance once per receipt irrespective of the outcome, so the "
    "counter vector is a deterministic fingerprint of the class assignment.",
)

# ---------------------------------------------------------------------------
# H4  "previous stance retained at an exact tie" (c_h = 0, c = 0)
# ---------------------------------------------------------------------------
for _s0, _tag in ((1, "plus"), (-1, "minus")):
    _case(
        f"H4_stance_exact_tie_{_tag}",
        RunConfig(N=4, agent_class="process", eps=1.0, c_b=0.5, c_h=0.0,
                  alpha=0.5, beta=0.5, r=1.0, lam=0.0, f=1.0,
                  pulses=((0.0, 90),),
                  initial_law="declared", declared_phi=90, declared_c=0.5,
                  declared_s=_s0, t_end=1.0, stop_on_extinction=False),
        {
            "pulse_out": [1],
            "counters": {0: 1},
            "s": _s0,
            "c_at_t_end": 0.0,
            "n_intervals": 0,
        },
        "c = 0.5 + cos(180 deg) * 0.5 = 0 exactly; with c_h = 0 both branches "
        "of the stance rule fire, so the previous stance is retained.",
    )

# ---------------------------------------------------------------------------
# H5  "no reset or reconsideration between coincident pulses"
# ---------------------------------------------------------------------------
_case(
    "H5_no_clock_event_between_coincident_pulses",
    RunConfig(N=100000, agent_class="process", eps=1.0, c_b=0.95, c_h=0.01,
              alpha=0.6, beta=0.2, r=0.5, lam=0.0, rho=0.0, kappa=1000.0,
              delta_deg=30, f=1.0,
              pulses=((0.0, 0), (0.0, 0)),
              initial_law="I2", t_end=0.01, stop_on_extinction=False),
    {
        "P_AR": 0.0,
        "P_RA": 0.0,
        "n_recons_positive": True,
    },
    "With kappa = 1000 and delta = 30 deg, a reconsideration interposed between "
    "the two coincident pulses would give P(AR | A) = sin^2(30 deg) = 1/4. The "
    "specification forbids it, so the pathwise-exact value is 0.",
)
