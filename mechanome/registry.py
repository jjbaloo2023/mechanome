"""
mechanome/registry.py — the Forward-Model and Module registries.

The registry is what makes the schema *executable* rather than descriptive: each
ForwardModel entry tells the orchestrator how to actually run an edge (governing
law, inverse method, validation anchor, data bindings). Registering a new forward
model is how a mechanome edge is added.

HONESTY RULE: exactly ONE forward model is real and executable here (helfrich_v1,
curvo). Every planned module is listed with status='registered_stub' and MAY NOT
emit GROUNDED claims until it passes validate() (synthetic recovery + an analytic
anchor). The registry makes the built-vs-stub split explicit and machine-readable.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
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
    status: str                          # "built_validated" | "registered_stub"
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

FORWARD_MODELS: Dict[str, ForwardModel] = {HELFRICH_V1.name: HELFRICH_V1}


# --- module registry: one built, the rest honest stubs ----------------------
MODULES: Dict[str, Module] = {m.name: m for m in [
    Module("membrane", "membrane", "helfrich_v1", "built_validated",
           "curvo. Synthetic-recovery + real force-paired (STED tether) validated."),
    Module("tissue", "tissue", "vertex_bayesian_force_inference_v0", "registered_stub",
           "vertex / Bayesian junction-tension inference (ablation-validated method); "
           "not built here."),
    Module("cortex", "cortex", "active_gel_v0", "registered_stub",
           "active-gel / TFM-style cortical stress; not built."),
    Module("bond", "molecule", "catch_slip_v0", "registered_stub",
           "catch/slip bond, talin/integrin unfolding (AFM); not built."),
    Module("channel", "membrane", "piezo_gating_v0", "registered_stub",
           "Piezo/MscL gating tension vs membrane tension; not built."),
]}


def registered_forward_models() -> Dict[str, dict]:
    return {k: v.to_dict() for k, v in FORWARD_MODELS.items()}


def module_status() -> Dict[str, dict]:
    return {k: v.to_dict() for k, v in MODULES.items()}


def can_emit_grounded(module_name: str) -> bool:
    """A module may emit GROUNDED claims only if it is built AND validated."""
    m = MODULES.get(module_name)
    return bool(m and m.status == "built_validated")


if __name__ == "__main__":
    print("Forward models:")
    for n, fm in FORWARD_MODELS.items():
        print(f"  {n} [{fm.status}] — {fm.governing_law}")
    print("\nModules (built vs stub):")
    for n, m in MODULES.items():
        flag = "GROUNDED-capable" if can_emit_grounded(n) else "stub (MEASURED/LINKED only)"
        print(f"  {n:9s} [{m.status:16s}] {flag}")
