"""
curvo.players — the player ontology, with physics as GUARDRAILS not deciders.

Each player exposes:
  - candidate_representations : the formats the search may pick from
  - validate(proposal)        : cheap physical guardrails that PRUNE invalid
                                proposals (the README § Design and development 2b move). A
                                validator returns (ok, reason); it never picks.
  - contribution(params)      : the effective spontaneous-curvature (or coat
                                stiffening) this player supplies to the evaluator.
  - data_binding              : which Parameter Store key resolves its params.
  - plausibility_range        : sanity bounds for proposed magnitudes.

The §4 table from the sprint plan lives here, but only as validators. The
orchestrator's search chooses the representation + magnitude; these functions
reject the physically impossible and seed good priors. Capturing synergy vs
antagonism (additive only if dilute/uncoupled) is enforced in combine().
"""
from __future__ import annotations

import numpy as np


# ==========================================================================
# P3 — amphipathic-helix wedge (epsin ENTH/H0). Tension-gated curvature sensor.
# ==========================================================================
class WedgePlayer:
    name = "wedge"
    candidate_representations = [
        "c0_plus_kappa_softening",   # correct: area asymmetry + local bending softening
        "isotropic_c0_only",         # allowed only if softening negligible
        "anisotropic_inclusion",     # WRONG for a shallow amphipathic helix (no nematic order)
        "rigid_scaffold",            # WRONG: double-counts a coat that already carries the helix
    ]
    data_binding = ("insertion_depth", "ENTH_H0")
    plausibility_range = {"c0_contribution_inv_nm": (0.0, 0.08)}

    def validate(self, rep: str, params: dict, context: dict) -> tuple[bool, str]:
        # Guardrail 1: a shallow amphipathic helix has no orientational order ->
        # anisotropic representation is physically wrong.
        if rep == "anisotropic_inclusion":
            return False, "amphipathic wedge is not nematic; anisotropic c0 is wrong (§4 rule)"
        # Guardrail 2: must not double-count a scaffold that already carries the helix.
        if rep == "rigid_scaffold" and context.get("coat_active"):
            return False, "wedge-as-scaffold double-counts the active coat's own helix"
        # Guardrail 3: amphipathy must be confirmed (from structure_provider) to use a wedge.
        if not context.get("amphipathic", False):
            return False, "no confirmed amphipathic moment -> cannot represent as membrane wedge"
        # Guardrail 4: plausibility bound on magnitude.
        c0 = params.get("c0_contribution_inv_nm", 0.0)
        lo, hi = self.plausibility_range["c0_contribution_inv_nm"]
        if not (lo <= c0 <= hi):
            return False, f"c0={c0} outside plausibility {self.plausibility_range}"
        return True, "wedge representation admissible"

    def contribution(self, params: dict, sigma: float) -> dict:
        """Wedge curvature contribution, TENSION-GATED (H0 is a sensor: its
        insertion/curvature drive weakens as tension flattens the membrane).
        c_wedge(sigma) = c0 / (1 + sigma/sigma_half).  Also softens kappa locally."""
        c0 = params.get("c0_contribution_inv_nm", 0.0)
        sigma_half = params.get("tension_half_kBT_nm2", 0.02)
        gate = 1.0 / (1.0 + sigma / sigma_half)
        c_eff = c0 * gate
        kappa_soft = params.get("kappa_softening_factor", 0.9)  # <1 softens
        return {"c0_contribution_inv_nm": c_eff, "kappa_factor": kappa_soft,
                "tension_gate": gate}


# ==========================================================================
# P4 — protein crowding (epsin disordered C-terminal IDP). Saturating, entropic.
# ==========================================================================
class CrowdingPlayer:
    name = "crowding"
    candidate_representations = [
        "saturating_surface_pressure",   # correct: density-dependent, saturates
        "fixed_c0",                      # WRONG: crowding is not a fixed spontaneous curvature
        "polymer_brush_ensemble",        # correct: brush on one face + conformational ensemble
    ]
    data_binding = ("area_per_lipid", "POPC")
    plausibility_range = {"c0_contribution_inv_nm": (0.0, 0.05)}

    def validate(self, rep: str, params: dict, context: dict) -> tuple[bool, str]:
        # Guardrail: crowding is entropic/steric and saturates -> a FIXED c0 is wrong.
        if rep == "fixed_c0":
            return False, "crowding is density-dependent & saturates; fixed c0 is wrong (§4 rule)"
        # Guardrail: an IDP represented as a folded pose is forbidden (pLDDT gate).
        if context.get("is_disordered") and rep not in (
                "saturating_surface_pressure", "polymer_brush_ensemble"):
            return False, "disordered tail must be brush/ensemble, not a folded representation"
        return True, "crowding representation admissible"

    def contribution(self, params: dict, sigma: float) -> dict:
        """Saturating surface-pressure -> effective spontaneous curvature.
        c_crowd(phi) = c_max * phi / (phi + phi_half)   (Hill-1 saturation).
        phi = grafting density (fractional coverage). Independent of tension to
        first order (entropic pressure), unlike the wedge."""
        c_max = params.get("c_max_inv_nm", 0.04)
        phi = params.get("coverage", 0.5)
        phi_half = params.get("phi_half", 0.3)
        c_eff = c_max * phi / (phi + phi_half)
        return {"c0_contribution_inv_nm": c_eff, "kappa_factor": 1.0, "saturated": phi > 2*phi_half}


# ==========================================================================
# Coat coupling (AP2/clathrin). Rigidity/area constraint, NOT a c0 source.
# ==========================================================================
class CoatPlayer:
    name = "coat"
    candidate_representations = [
        "rigidity_area_constraint",   # correct (esp. Kaksonen-type: sets size/regularity)
        "isotropic_c0_source",        # WRONG when the coat sets size, not shape
        "curvature_scaffold",         # only if the coat is intrinsically curved (mature CCV)
    ]
    data_binding = ("scaffold_deformation", "ENTH")
    plausibility_range = {"rigidity_factor": (1.0, 6.0)}

    def validate(self, rep: str, params: dict, context: dict) -> tuple[bool, str]:
        # Guardrail (Kaksonen subtlety): if the coat's role is size/regularity, a
        # c0 source is the wrong representation.
        if rep == "isotropic_c0_source" and context.get("coat_role") == "size_regularity":
            return False, "coat setting size/regularity must be a rigidity constraint, not a c0 source (§4/Kaksonen)"
        rf = params.get("rigidity_factor", 1.0)
        lo, hi = self.plausibility_range["rigidity_factor"]
        if not (lo <= rf <= hi):
            return False, f"rigidity_factor={rf} outside {self.plausibility_range}"
        return True, "coat representation admissible"

    def contribution(self, params: dict, sigma: float) -> dict:
        """Coat stiffens the patch (raises effective kappa) and, if intrinsically
        curved, adds a modest c0. Localizes/stabilizes but does not itself bend a
        flat membrane."""
        rf = params.get("rigidity_factor", 1.0)
        c0_coat = params.get("intrinsic_c0_inv_nm", 0.0)  # 0 unless mature curved lattice
        return {"c0_contribution_inv_nm": c0_coat, "kappa_factor": rf}


# ==========================================================================
# Tension antagonist (sigma). Not a curvature source; opposes budding.
# ==========================================================================
class TensionPlayer:
    name = "tension"
    candidate_representations = ["constant_tension_frame"]
    data_binding = None
    plausibility_range = {"sigma_kBT_nm2": (0.0, 0.1)}

    def validate(self, rep: str, params: dict, context: dict) -> tuple[bool, str]:
        s = params.get("sigma_kBT_nm2", 0.0)
        lo, hi = self.plausibility_range["sigma_kBT_nm2"]
        if not (lo <= s <= hi):
            return False, f"sigma={s} outside {self.plausibility_range}"
        return True, "tension frame admissible"

    def contribution(self, params: dict, sigma: float) -> dict:
        return {"sigma_kBT_nm2": params.get("sigma_kBT_nm2", 0.0)}


# ==========================================================================
# Combining players — synergy/antagonism guardrail (additive only if uncoupled)
# ==========================================================================
COUPLED_PAIRS = {("wedge", "coat"), ("crowding", "coat")}  # known-coupled -> not naive-additive


def combine_curvature(contribs: dict, coupling_correction: float = 0.0) -> dict:
    """Sum player c0 contributions ONLY as scalars for uncoupled/dilute players.

    Known-coupled pairs (wedge+coat, crowding+coat) get a coupling correction
    rather than a naive sum. The wedge is the sensor; the coat localizes and
    concentrates it — the correction captures the >additive synergy the epsin
    system is documented to show (H0 alone insufficient without the coat).
    """
    c_total = sum(c.get("c0_contribution_inv_nm", 0.0) for c in contribs.values())
    active = set(contribs.keys())
    coupled_present = any(p[0] in active and p[1] in active for p in COUPLED_PAIRS)
    if coupled_present and coupling_correction:
        c_total *= (1.0 + coupling_correction)
    kappa_factor = 1.0
    for c in contribs.values():
        kappa_factor *= c.get("kappa_factor", 1.0)
    return {"c_eff_inv_nm": c_total, "kappa_factor": kappa_factor,
            "coupled_present": coupled_present}


PLAYERS = {p.name: p for p in [WedgePlayer(), CrowdingPlayer(), CoatPlayer(), TensionPlayer()]}
