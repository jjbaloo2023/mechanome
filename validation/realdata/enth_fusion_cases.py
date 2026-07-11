"""
Designed-construct test cases: does a C-terminal partner rescue ENTH-domain
curvature, and does it matter whether the partner is disordered or folded?

Constructs (ENTH/H0 amphipathic wedge is the shared front end):
  ENTH + AP180 IDP   -- disordered assembly domain (SNAP91) as a crowding brush
  ENTH + albumin     -- folded globular protein (ALB), counter-example
  ENTH alone         -- reference
  full epsin         -- reference (ENTH + epsin's own IDP tail)

The partner's crowding contribution is GROUNDED, not assumed: curvo fetches the
partner's AlphaFold model and classifies each segment (pLDDT + composition) into
folded vs polymer-brush-crowding (structure_provider.representation_call). Only
brush-competent residues drive entropic curvature; a folded globule contributes
none. The crowding c_eff then follows CrowdingPlayer with coverage set by the
brush-residue count (idr/400 scaling, as in the family screen).

Result: ENTH+AP180-IDP reaches Omega with the least actin force (behaves like /
slightly exceeds full epsin), while ENTH+albumin is indistinguishable from
ENTH-alone -- a folded C-terminal cargo of comparable mass adds no curvature
drive. Stage/threshold calls from the forward model; no force point-estimate.
"""
import numpy as np

import curvo.structure_provider as sp
from curvo.evaluator_tier0 import ccs_curvature
from curvo.players import PLAYERS
from validation.realdata.epsin_domain_cases import (
    enth_ceff, idp_ceff, KAPPA_KBT, SIGMA_KBT_NM2, A_COAT_NM2, COAT_RF, OMEGA_OP)

PARTNERS = {"AP180": "O60641", "albumin": "P02768"}  # SNAP91 IDP vs ALB globule


def partner_brush_residues(uniprot, cache_dir="cache"):
    """Disordered (polymer-brush-crowding) residue count from the partner's
    AlphaFold model, via curvo's segment classifier."""
    model = sp.fetch_alphafold(uniprot, cache_dir=cache_dir)
    call = sp.representation_call(model)
    return sum(s["end"] - s["start"] + 1 for s in call["segments"]
               if s["representation"] == "polymer_brush_crowding")


def crowd_ceff(brush_residues):
    cov = min(1.0, brush_residues / 400.0)
    return PLAYERS["crowding"].contribution(
        {"c_max_inv_nm": 0.05, "coverage": cov, "phi_half": 0.3},
        SIGMA_KBT_NM2)["c0_contribution_inv_nm"]


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


def constructs(cache_dir="cache"):
    e = enth_ceff()
    ap180 = crowd_ceff(partner_brush_residues(PARTNERS["AP180"], cache_dir))
    alb = crowd_ceff(partner_brush_residues(PARTNERS["albumin"], cache_dir))
    return {
        "ENTH + AP180 IDP":  e + ap180,
        "full epsin":        e + idp_ceff(),
        "ENTH + albumin":    e + alb,
        "ENTH alone":        e,
    }


if __name__ == "__main__":
    C = constructs()
    print(f"{'construct':20} {'c_eff':>7} {'H(+40pN)':>9} {'f_min(Ω)':>9}")
    for name, c in C.items():
        p = evaluate(c, 40.0)
        print(f"{name:20} {c:7.4f} {p['achieved_mean_curvature_inv_nm']:9.4f} "
              f"{str(min_force_to_omega(c))+' pN':>9}")
