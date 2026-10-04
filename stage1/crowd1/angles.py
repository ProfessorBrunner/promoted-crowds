"""Angles and framing-class identifiers.

Specification v0.6: "orientation phi_i in [0 deg, 180 deg)"; "Framing class of
theta: the basis {theta, theta+90 deg}, keyed by theta mod 90 deg."

Design A1 / project rule 2: "Framing classes carried as explicit integer
identifiers assigned at angle creation, never recomputed from floating-point
angles; opposite rays share one identifier."

Implementation
--------------
Every angle in this project is an *exact integer number of degrees*.  This is
true of every angle that any of T1-T6 can create:

  * declared campaign framings      (integer degrees in the design)
  * targets T_+ = 0, T_- = 90
  * post-rejection rays theta + 90  (integer if theta is)
  * reconsideration rays T_s +- delta (integer for integer delta)

Angles are therefore stored as int32 degrees reduced into [0, 180), and the
engine's trigonometry goes through `cosd`, which is *exact* at multiples of
90 deg.  That exactness is what makes the T5 claim "P(AR) = P(RA) = 0 pathwise"
a statement the engine can satisfy identically rather than to within 1e-33.

A `ClassRegistry` is built once, at configuration time, from the declared
integer angles.  It allocates one integer identifier per framing basis.  The
engine receives, with every created angle, the identifier that was allocated
for it; it never performs a mod-90 reduction on a stored angle.  The
`AngleRegistry.check_consistency` method asserts, at configuration time only,
that the allocated identifiers agree with integer mod-90 arithmetic.
"""

from __future__ import annotations

import math

_EXACT_COS = {0: 1.0, 90: 0.0, 180: -1.0, 270: 0.0}


def cosd(deg: int) -> float:
    """cos of an integer number of degrees; exact at multiples of 90 deg."""
    m = int(deg) % 360
    if m in _EXACT_COS:
        return _EXACT_COS[m]
    return math.cos(math.radians(m))


def cos2d(deg: int) -> float:
    """cos(2 * theta) for theta an integer number of degrees."""
    return cosd(2 * int(deg))


def reduce180(deg: int) -> int:
    """Reduce an integer-degree ray into [0, 180)."""
    return int(deg) % 180


class ClassRegistry:
    """Allocates integer framing-class identifiers at angle creation."""

    def __init__(self):
        self._by_key: dict[int, int] = {}
        self._order: list[int] = []  # key (theta mod 90) in allocation order
        self._provenance: dict[int, list[int]] = {}

    def create(self, deg: int) -> int:
        """Allocate (or look up) the identifier for the basis containing `deg`.

        Called only at configuration time, on declared exact integer degrees.
        """
        d = int(deg)
        if d != deg:
            raise ValueError(f"angle {deg!r} is not an exact integer number of degrees")
        key = d % 90
        if key not in self._by_key:
            cid = len(self._order)
            self._by_key[key] = cid
            self._order.append(key)
            self._provenance[cid] = []
        cid = self._by_key[key]
        if reduce180(d) not in self._provenance[cid]:
            self._provenance[cid].append(reduce180(d))
        return cid

    def of(self, deg: int) -> int:
        """Identifier already allocated for `deg` (raises if never created)."""
        key = int(deg) % 90
        if key not in self._by_key:
            raise KeyError(
                f"framing class for {deg} deg was never created; every angle the "
                f"process can produce must be declared at configuration time"
            )
        return self._by_key[key]

    @property
    def n_classes(self) -> int:
        return len(self._order)

    def table(self) -> list[dict]:
        return [
            {"class_id": cid, "key_theta_mod_90": self._order[cid],
             "rays_declared": sorted(self._provenance[cid])}
            for cid in range(self.n_classes)
        ]

    def check_consistency(self) -> None:
        """Configuration-time assertion: ids agree with integer mod-90 arithmetic
        and opposite rays share one identifier."""
        for cid in range(self.n_classes):
            key = self._order[cid]
            for ray in self._provenance[cid]:
                assert ray % 90 == key, (cid, ray, key)
                # opposite ray of the basis
                assert self.of(ray + 90) == cid, (cid, ray)
                assert self.of(ray + 180) == cid, (cid, ray)


def build_registry(campaign_angles, delta_deg=None, extra_angles=(), full_bases=False):
    """Create the registry for a run.

    Allocates, in a fixed declared order:
      1. the target basis {T_+ = 0, T_- = 90}   (always first; id 0)
      2. each declared campaign framing, in campaign index order
      3. the reconsideration bases T_s + delta and T_s - delta, when delta is used
      4. any extra declared angles (e.g. a declared non-standard initial orientation)

    `full_bases=True` additionally declares all 90 integer-degree bases.  It is
    used when an initial law (I2) places agents on arbitrary integer-degree rays,
    so that every orientation an agent can ever broadcast has an identifier
    allocated AT CREATION TIME rather than derived later from its angle.

    Returns (registry, info_dict).
    """
    reg = ClassRegistry()
    cid_target = reg.create(0)
    reg.create(90)  # same basis as 0 by construction; recorded as a declared ray
    assert reg.of(90) == cid_target
    for th in campaign_angles:
        reg.create(int(th))
        reg.create(int(th) + 90)  # the post-rejection ray of the same basis
    cid_dp = cid_dm = -1
    if delta_deg is not None:
        d = int(delta_deg)
        if not (0 < d < 45):
            raise ValueError("specification v0.6 requires 0 < delta < 45 deg")
        # T_s + delta  -> basis keyed by  delta mod 90
        cid_dp = reg.create(d)
        reg.create(d + 90)
        # T_s - delta  -> basis keyed by (90 - delta) mod 90
        cid_dm = reg.create(-d)
        reg.create(-d + 90)
    for th in extra_angles:
        reg.create(int(th))
        reg.create(int(th) + 90)
    if full_bases:
        for k in range(90):
            reg.create(k)
            reg.create(k + 90)
    reg.check_consistency()
    info = {
        "class_table": reg.table(),
        "n_classes": reg.n_classes,
        "class_target": cid_target,
        "class_delta_plus": cid_dp,
        "class_delta_minus": cid_dm,
        "key_to_class": {k: reg.of(k) for k in range(90) if (k in reg._by_key)},
        "full_bases": bool(full_bases),
    }
    return reg, info
