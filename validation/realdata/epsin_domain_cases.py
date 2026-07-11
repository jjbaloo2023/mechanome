"""
Orchestration test cases: full epsin vs ENTH-domain-alone vs IDP-domain-alone.

Epsin decomposes into two curvature players in curvo's `players` module:
  - ENTH/H0 amphipathic wedge  -> WedgePlayer (tension-gated)
  - disordered C-terminal tail -> CrowdingPlayer (entropic brush)
The component c_eff sum matches the validated family-screen epsin H_med (~0.033).

Each construct is run through the validated forward model (ccs_curvature) with
the clathrin coat present, and we report (a) autonomous curvature, (b) curvature
under coat + 40 pN actin, and (c) the minimum actin force to cross Omega. This
is a STAGE/THRESHOLD comparison from the forward model, not an inverse on a
measured trajectory; no force point-estimate is made.

Result: no construct is productive on coat + 40 pN actin alone; the force burden
to reach Omega orders full epsin (least) < IDP-alone < ENTH-alone (most). The
two domains are complementary -- deleting either shifts load onto actin.
"""
import numpy as np

from curvo.evaluator_tier0 import ccs_curvature
from curvo.players import PLAYERS

KAPPA_KBT = 20.0
SIGMA_KBT_NM2 = 0.02
A_COAT_NM2 = np.pi * 60.0 ** 2
OMEGA_OP = 0.66
COAT_RF = 3.0

# Domain component c_eff from the players representation.
ENTH_INTRINSIC_C0 = 0.020


def enth_ceff():
    return PLAYERS["wedge"].contribution(
        {"c0_contribution_inv_nm": ENTH_INTRINSIC_C0, "tension_half_kBT_nm2": 0.02},
        SIGMA_KBT_NM2)["c0_contribution_inv_nm"]


def idp_ceff():
    return PLAYERS["crowding"].contribution(
        {"c_max_inv_nm": 0.04, "coverage": 0.5, "phi_half": 0.3},
        SIGMA_KBT_NM2)["c0_contribution_inv_nm"]


def constructs():
    e, i = enth_ceff(), idp_ceff()
    return {"full epsin (ENTH+IDP)": e + i,
            "ENTH domain alone": e,
            "IDP domain alone": i}


def evaluate(c_eff, active_pN=0.0):
    o = ccs_curvature(c_eff, SIGMA_KBT_NM2, KAPPA_KBT, A_COAT_NM2,
                      coat_rigidity_factor=COAT_RF, active_force_pN=active_pN)
    o["productive"] = o["dome_omega_OP"] >= OMEGA_OP
    return o


def min_force_to_omega(c_eff, fmax=200, step=5):
    for f in np.arange(0, fmax + 1, step):
        if evaluate(c_eff, active_pN=float(f))["productive"]:
            return int(f)
    return None


if __name__ == "__main__":
    C = constructs()
    print(f"{'construct':24} {'c_eff':>7} {'H(coat)':>8} {'H(+40pN)':>9} {'f_min(Ω)':>9}")
    for name, c in C.items():
        a = evaluate(c); p = evaluate(c, 40.0); fm = min_force_to_omega(c)
        print(f"{name:24} {c:7.4f} {a['achieved_mean_curvature_inv_nm']:8.4f} "
              f"{p['achieved_mean_curvature_inv_nm']:9.4f} {str(fm)+' pN':>9}")
