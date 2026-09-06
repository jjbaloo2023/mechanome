"""
mechanome/registry.py — the Forward-Model and Module registries.

The registry is what makes the schema *executable* rather than descriptive: each
ForwardModel entry tells the orchestrator how to actually run an edge (governing
law, inverse method, validation anchor, data bindings). Registering a new forward
model is how a mechanome edge is added.

HONESTY RULE (two validation tiers, machine-readable):
  * ONE module is real-data force-paired: membrane / curvo (helfrich_v1),
    status 'built_validated'. Only it may emit GROUNDED claims backed by REAL
    measured force (can_emit_grounded).
  * FOUR modules are analytic-limit validated: tissue (vertex_v1), cortex
    (active_gel_v1), bond (catch_slip_v1), channel (ms_gating_v1), status
    'built_analytic'. Each reproduces a known closed-form limit and a canonical
    published anchor's parameters, but is NOT paired against a raw dataset
    acquired here. They may emit analytic-tier GROUNDED claims (can_emit_analytic)
    whose evidence carries validation=analytic_limit on its face.
  * Any further planned module is a 'registered_stub' and may emit only
    MEASURED / LINKED claims until it passes validation.
The registry makes this validation tier explicit and machine-readable via
validation_provenance() -> 'real_force_paired' | 'analytic_limit' | 'none'.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class ForwardModel:
    name: str
    scale: str
    governing_law: str
    inputs: List[str]
    outputs: List[str]
    inverse_method: str
    validation_anchor: str
    data_bindings: List[str]
    status: str = "executable"          # "executable" | "registered_stub"

    def to_dict(self): return asdict(self)


@dataclass
class Module:
    name: str
    scale: str
    forward_model: str
    status: str                          # "built_validated" | "built_analytic" | "registered_stub"
    note: str = ""

    def to_dict(self): return asdict(self)


# --- the one real, executable forward model ---------------------------------
HELFRICH_V1 = ForwardModel(
    name="helfrich_v1",
    scale="membrane",
    governing_law="Helfrich bending energy + tension + active cortical stress",
    inputs=["c_eff_inv_nm", "sigma_kBT_nm2", "kappa_kBT", "active_force_pN"],
    outputs=["mean_curvature_inv_nm", "tether_force_pN", "tube_radius_nm"],
    inverse_method="nested sampling (dynesty) + MCMC (emcee) cross-check",
    validation_anchor="a* = 4*kappa/lambda (budding) ; R=sqrt(kappa/2sigma), "
                      "f=2*pi*sqrt(2 sigma kappa) (tube) ; synthetic recovery gate",
    data_bindings=["AlphaFold DB (structure)", "NMRlipids / MDDB (elastic params)",
                   "STED tether (Roy et al. 2020, real force-paired validation)"],
    status="executable")

# --- four analytic-validated forward models (built this session) ------------
VERTEX_V1 = ForwardModel(
    name="vertex_v1", scale="tissue",
    governing_law="tri-junction force balance sum_i T_i t_hat_i = 0 (law of sines)",
    inputs=["junction_opening_angles_deg"], outputs=["relative_edge_tensions"],
    inverse_method="Bayesian / least-squares junction-tension inference on force-balance residual",
    validation_anchor="120 deg symmetric junction -> equal tensions; "
                      "Ishihara & Sugimura 2012 J Theor Biol 313:201 (Bayesian force inference)",
    data_bindings=["cell-array segmentation geometry (method-validated vs ablation recoil)"],
    status="executable")

ACTIVE_GEL_V1 = ForwardModel(
    name="active_gel_v1", scale="cortex",
    governing_law="Young-Laplace dP = 2 gamma / R (cortical tension from curvature+pressure)",
    inputs=["radius_um", "pressure_Pa"], outputs=["cortical_tension_mN_m"],
    inverse_method="closed-form Laplace inverse (active-gel PDE is the next tier)",
    validation_anchor="dP=2gamma/R round-trip + micropipette recovery; "
                      "Tinevez et al. 2009 PNAS 106:18581 (cortical tension 0.03-1 mN/m)",
    data_bindings=["micropipette aspiration critical pressure + radii"],
    status="executable")

CATCH_SLIP_V1 = ForwardModel(
    name="catch_slip_v1", scale="molecule",
    governing_law="Bell k_off=k0 exp(F x/kBT); two-pathway catch-slip (Pereverzev 2005)",
    inputs=["force_pN"], outputs=["off_rate_per_s", "bond_lifetime_s"],
    inverse_method="MLE/Bayesian fit of Bell or two-pathway parameters to force-lifetime data",
    validation_anchor="ln(1/tau) vs F slope = x_dagger/kBT; catch-slip peak dkoff/dF=0; "
                      "Marshall et al. 2003 Nature 423:190 (P-selectin/PSGL-1 catch-slip)",
    data_bindings=["AFM / BFP / optical-tweezers force-lifetime curves"],
    status="executable")

MS_GATING_V1 = ForwardModel(
    name="ms_gating_v1", scale="membrane",
    governing_law="two-state Boltzmann Po(sigma)=1/(1+exp(-(sigma dA - dG)/kBT))",
    inputs=["membrane_tension_mN_m"], outputs=["open_probability"],
    inverse_method="Boltzmann fit of (dA, dG) to patch-clamp Po-tension curve",
    validation_anchor="recover dA, sigma_half from Po sigmoid; slope at midpoint = dA/4kBT; "
                      "Sukharev et al. 1999 J Gen Physiol 113:525 (MscL sigma_half=11.8 mN/m, dA=6.5 nm^2)",
    data_bindings=["patch-clamp Po-tension", "reads curvo membrane tension (cross-scale link)"],
    status="executable")

STRUCTURAL_SCREEN_V1 = ForwardModel(
    name="structural_screen_v1", scale="molecule",
    governing_law="per-protein curvature capacity E_curv = 1/2 kappa (2 c0)^2 A_footprint "
                  "+ gamma |dA|, signed by generated-curvature direction",
    inputs=["experimental_structure_pair", "membrane_frame_alignment"],
    outputs=["curvature_capacity_kBT", "signed_capacity_kBT", "spontaneous_curvature_c0_inv_nm"],
    inverse_method="forward structural screen (PDB coordinates -> A(z) geometry -> capacity); "
                   "no free parameters beyond the fixed energy scale",
    validation_anchor="BAR-domain arc-fit radii reproduce literature independently "
                      "(amphiphysin ~9.8 nm vs ~11 nm; endophilin ~8.0 nm vs 6-11 nm); "
                      "pre-registered GO-enrichment test SUPPORTED (AUROC 0.750, one-sided p 0.085); "
                      "frozen ranking SHA-256 41d49328960d4083",
    data_bindings=["RCSB PDB / OPM experimental structures",
                   "supplies structure-derived c0 to ms_gating_v1 (channel cross-scale link)"],
    status="executable")

FORWARD_MODELS: Dict[str, ForwardModel] = {fm.name: fm for fm in [
    HELFRICH_V1, VERTEX_V1, ACTIVE_GEL_V1, CATCH_SLIP_V1, MS_GATING_V1,
    STRUCTURAL_SCREEN_V1]}


# --- module registry: one built, the rest honest stubs ----------------------
MODULES: Dict[str, Module] = {m.name: m for m in [
    Module("membrane", "membrane", "helfrich_v1", "built_validated",
           "curvo. Synthetic-recovery + real force-paired (STED tether) validated."),
    Module("tissue", "tissue", "vertex_v1", "built_analytic",
           "vertex junction-tension inference. Analytic-limit validated (120 deg force "
           "balance); anchor Ishihara 2012. NOT real-data force-paired."),
    Module("cortex", "cortex", "active_gel_v1", "built_analytic",
           "active-gel cortical tension (Young-Laplace). Analytic-limit validated "
           "(dP=2gamma/R round-trip); anchor Tinevez 2009. NOT real-data force-paired."),
    Module("bond", "molecule", "catch_slip_v1", "built_analytic",
           "Bell / two-pathway catch-slip bond. Analytic-limit validated (Bell fit + "
           "catch-slip peak); anchor Marshall 2003. NOT real-data force-paired."),
    Module("channel", "membrane", "ms_gating_v1", "built_analytic",
           "MscL/Piezo two-state gating; reads curvo membrane tension. Analytic-limit "
           "validated (MscL sigmoid recovery); anchor Sukharev 1999. NOT real-data force-paired."),
    Module("structural_screen", "molecule", "structural_screen_v1", "built_analytic",
           "structure-based curvature-capacity screen (vendored mechanistic-entry-model). "
           "Validated on home turf (BAR radii reproduce literature) + pre-registered "
           "enrichment SUPPORTED (frozen hash 41d49328960d4083). Supplies structure-derived "
           "c0 to the channel module. NOT real-data force-paired."),
]}


def registered_forward_models() -> Dict[str, dict]:
    return {k: v.to_dict() for k, v in FORWARD_MODELS.items()}


def module_status() -> Dict[str, dict]:
    return {k: v.to_dict() for k, v in MODULES.items()}


def can_emit_grounded(module_name: str) -> bool:
    """A module may emit GROUNDED claims backed by REAL force-paired data only if
    it is built AND validated against real measurements (built_validated)."""
    m = MODULES.get(module_name)
    return bool(m and m.status == "built_validated")


def can_emit_analytic(module_name: str) -> bool:
    """A module may emit analytic-tier GROUNDED claims (validation=analytic_limit)
    if it is either real-data validated OR analytic-limit validated."""
    m = MODULES.get(module_name)
    return bool(m and m.status in ("built_validated", "built_analytic"))


def validation_provenance(module_name: str) -> str:
    """The provenance string a claim from this module must carry on its face."""
    m = MODULES.get(module_name)
    if not m:
        return "unregistered"
    return {"built_validated": "real_force_paired",
            "built_analytic": "analytic_limit",
            "registered_stub": "none"}.get(m.status, "none")


if __name__ == "__main__":
    print("Forward models:")
    for n, fm in FORWARD_MODELS.items():
        print(f"  {n:16s} [{fm.status}] — {fm.governing_law}")
    print("\nModules (validation tier):")
    for n, m in MODULES.items():
        if can_emit_grounded(n):
            flag = "GROUNDED (real force-paired)"
        elif can_emit_analytic(n):
            flag = "GROUNDED (analytic_limit)"
        else:
            flag = "stub (MEASURED/LINKED only)"
        print(f"  {n:9s} [{m.status:16s}] {flag}")
