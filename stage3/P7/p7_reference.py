"""Stage 3 P7 — the C9(a) analytical enclosures, recomputed independently.

Appendix E, C9(a), for alpha = 1, beta = 0.4, r = 1e-6, lambda = 0.5, eps = 1,
c_b = 0.5, c_h = 0.01, rho = kappa = 0, I1, one T pulse at zero:

  every first T receipt sets conviction to one; subsequent deposits total at most
  B = r/(1-r); each first-exposed agent is active throughout its first L = log 2 of
  age and never after L_plus = log(1/(c_b - B)).  With

      Z_D(f)  solving  1 - Z_D = (1-f) exp(-lambda D Z_D)      (final size)
      P_D(f)  =  f e^{lambda D} / (1 - f + f e^{lambda D})      (peak activity)

  the enclosures are   L Z_L <= I <= L+ Z_{L+},
                       P_L   <= A_max <= P_{L+},
                       L     <= T_act <= L+.

This file recomputes all of it from the definitions and checks it against the two
things Appendix E states numerically: the 8-digit enclosures at f = 0.25 and the
5-digit reach table at f = 0.10, 0.25, 0.50, 0.75.  Nothing is taken on trust.
"""
import json, math, os
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA, BETA, R, LAM, EPS, C_B = 1.0, 0.4, 1e-6, 0.5, 1.0, 0.5
B = R / (1.0 - R)
L = math.log(1.0 / C_B) / EPS
L_PLUS = math.log(1.0 / (C_B - B)) / EPS

def Z(D, f):
    """Final size: 1 - Z = (1-f) exp(-lambda D Z), the C9(a) / R6 equation."""
    if f >= 1.0:
        return 1.0
    g = lambda z: 1.0 - z - (1.0 - f) * math.exp(-LAM * D * z)
    return brentq(g, f, 1.0 - 1e-16, xtol=1e-16, rtol=8.9e-16, maxiter=300)

def P(D, f):
    e = math.exp(LAM * D)
    return f * e / (1.0 - f + f * e)

def enclosures(f):
    return dict(f=f,
                A_max=(P(L, f), P(L_PLUS, f)),
                I=(L * Z(L, f), L_PLUS * Z(L_PLUS, f)),
                T_act=(L, L_PLUS))

if __name__ == "__main__":
    out = dict(B=B, L=L, L_plus=L_PLUS, L_plus_minus_L=L_PLUS - L,
               params=dict(alpha=ALPHA, beta=BETA, r=R, lam=LAM, eps=EPS, c_b=C_B))
    print(f"B = r/(1-r) = {B:.12e}")
    print(f"L = {L:.15f}   L+ = {L_PLUS:.15f}   L+ - L = {L_PLUS-L:.6e}\n")
    # --- check 1: the 8-digit enclosures Appendix E states at f = 0.25
    APP = {"A_max": (0.32037724, 0.32037746), "I": (0.22968922, 0.22969009),
           "T_act": (0.69314718, 0.69314919)}
    e25 = enclosures(0.25)
    out["f0.25_enclosures"] = {k: list(v) for k, v in e25.items() if k != "f"}
    print("check 1 - Appendix E 8-digit enclosures at f = 0.25")
    chk1 = {}
    for k, (alo, ahi) in APP.items():
        lo, hi = e25[k]
        chk1[k] = dict(computed=[lo, hi], appendix=[alo, ahi],
                       d_lo=lo - alo, d_hi=hi - ahi)
        print(f"  {k:6s} computed [{lo:.8f}, {hi:.8f}]  appendix [{alo:.8f}, {ahi:.8f}]"
              f"   d = [{lo-alo:+.2e}, {hi-ahi:+.2e}]")
    out["check_f0.25"] = chk1
    # --- check 2: the 5-digit reach table
    TABLE = {0.10: (0.13580, 0.09963, 0.69315), 0.25: (0.32038, 0.22969, 0.69315),
             0.50: (0.58579, 0.41095, 0.69315), 0.75: (0.80926, 0.56233, 0.69315)}
    print("\ncheck 2 - Appendix E reach table (A_max, I, T_act), 5 d.p.")
    rows = []
    for f, (am, ii, ta) in TABLE.items():
        e = enclosures(f)
        mid = {k: 0.5 * (e[k][0] + e[k][1]) for k in ("A_max", "I", "T_act")}
        rows.append(dict(f=f, enclosure={k: list(e[k]) for k in mid},
                         midpoint=mid, registered=dict(A_max=am, I=ii, T_act=ta),
                         d=dict(A_max=mid["A_max"] - am, I=mid["I"] - ii,
                                T_act=mid["T_act"] - ta),
                         width={k: e[k][1] - e[k][0] for k in mid}))
        print(f"  f={f:<5} A_max {mid['A_max']:.8f} vs {am}  (d {mid['A_max']-am:+.2e}, "
              f"width {e['A_max'][1]-e['A_max'][0]:.2e})")
        print(f"        I     {mid['I']:.8f} vs {ii}  (d {mid['I']-ii:+.2e}, "
              f"width {e['I'][1]-e['I'][0]:.2e})")
        print(f"        T_act {mid['T_act']:.8f} vs {ta}  (d {mid['T_act']-ta:+.2e}, "
              f"width {e['T_act'][1]-e['T_act'][0]:.2e})")
    out["reach_table"] = rows
    # --- check 3: the two-pulse coincident arithmetic, from the specification
    #   (T, T_perp): accept T (cos^2 0 = 1), deposit r^0 cos0 (+alpha) = +1 -> c = 1;
    #   then T_perp is in the SAME framing class (90 mod 90 = 0 mod 90), rejected
    #   (cos^2 90 = 0), deposit r^1 cos180 (-beta) = +0.4r -> c = 1 (clipped).
    #   (T_perp, T): reject T_perp, deposit r^0 cos180 (-beta) = +0.4 -> c = 0.4;
    #   then accept T, deposit r^1 cos0 (+alpha) = +r -> c = 0.4 + 1e-6.
    two = dict(T_then_Tperp=min(1.0, 1.0 + R * BETA), Tperp_then_T=BETA + ALPHA * R)
    two["T_then_Tperp_active"] = two["T_then_Tperp"] > C_B
    two["Tperp_then_T_active"] = two["Tperp_then_T"] > C_B
    out["two_pulse"] = two
    print(f"\ncheck 3 - coincident {{T, T_perp}} from the specification's transition")
    print(f"  (T, T_perp) -> c = {two['T_then_Tperp']:.9f}  active {two['T_then_Tperp_active']}"
          f"   (Appendix E: ends at c = 1, n_T = 2, same enclosures)")
    print(f"  (T_perp, T) -> c = {two['Tperp_then_T']:.9f}  active {two['Tperp_then_T_active']}"
          f"   (Appendix E: 0.400001 < c_b, so A_max = I = T_act = 0)")
    json.dump(out, open(os.path.join(HERE, "outputs", "raw", "p7_reference.json"),
                        "w"), indent=2)
