"""
Orchestration test case: PICALM (ANTH adaptor) recruited to the membrane --
can it support productive pit formation?

Runs PICALM's autonomous curvature capacity (family-screen H_med, an ANTH
amphipathic wedge) through the validated forward model (evaluator_tier0.
ccs_curvature) across an assembly ladder, and reads the dome/Omega stage against
the Omega/scission threshold. This is a STAGE/THRESHOLD call from the forward
model with published/derived c_eff magnitudes -- NOT an inverse on a measured
curvature trajectory, and no force point-estimate is made.

Verdict (see run_ladder): PICALM cannot make a productive pit alone (autonomous
P(cross Omega) ~ 0.005); the pit reaches Omega only in the full assembly --
clathrin coat + actin force + a crowding/curvature partner (epsin C-terminal IDP
brush) -- consistent with the division of labour where PICALM sets vesicle size
and epsin/crowding drives curvature.
"""
import numpy as np

from curvo.evaluator_tier0 import ccs_curvature
from curvo.players import PLAYERS

# Constants (family screen + evaluator conventions)
KAPPA_KBT = 20.0
SIGMA_KBT_NM2 = 0.02
A_COAT_NM2 = np.pi * 60.0 ** 2
OMEGA_H_THRESHOLD = 0.030          # productive-pit (scission) mean-curvature threshold
OMEGA_OP = 0.66                    # dome/Omega order-parameter boundary

# PICALM autonomous curvature capacity from the validated family screen (ANTH).
PICALM_H_MED = 0.0194
PICALM_P_CROSS_OMEGA = 0.005

# Representative crowding co-player (epsin C-terminal IDP brush), Hill-saturating.
def crowding_ceff():
    return PLAYERS["crowding"].contribution(
        {"c_max_inv_nm": 0.04, "coverage": 0.5, "phi_half": 0.3},
        SIGMA_KBT_NM2)["c0_contribution_inv_nm"]


def evaluate_assembly(c_eff, coat_rf=1.0, active_pN=0.0, extra_c=0.0):
    out = ccs_curvature(c_eff + extra_c, SIGMA_KBT_NM2, KAPPA_KBT, A_COAT_NM2,
                        coat_rigidity_factor=coat_rf, active_force_pN=active_pN)
    out["productive"] = out["dome_omega_OP"] >= OMEGA_OP
    return out


def run_ladder():
    """The assembly ladder for PICALM. Returns list of (label, result)."""
    crowd = crowding_ceff()
    ladder = [
        ("PICALM alone",              dict(c_eff=PICALM_H_MED)),
        ("+ clathrin coat",           dict(c_eff=PICALM_H_MED, coat_rf=3.0)),
        ("+ coat + actin 40 pN",      dict(c_eff=PICALM_H_MED, coat_rf=3.0, active_pN=40.0)),
        ("+ coat + actin + crowding", dict(c_eff=PICALM_H_MED, coat_rf=3.0, active_pN=80.0, extra_c=crowd)),
    ]
    return [(lbl, evaluate_assembly(**cfg)) for lbl, cfg in ladder]


if __name__ == "__main__":
    print(f"PICALM autonomous P(cross Omega) = {PICALM_P_CROSS_OMEGA}")
    print(f"{'assembly':30} {'H_ach':>8} {'stage':>6}  productive?")
    for lbl, o in run_ladder():
        print(f"{lbl:30} {o['achieved_mean_curvature_inv_nm']:8.4f} {o['stage']:>6}  "
              f"{'YES' if o['productive'] else 'no'}")
