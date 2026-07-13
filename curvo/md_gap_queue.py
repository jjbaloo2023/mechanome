"""
curvo.md_gap_queue — the future-oriented seam (MD plugs in here).

Two seams, both well-formed now and runnable later without touching anything
upstream:

  1. MD-Gap Queue — when a required parameter is missing, or the target state
     point falls outside a stored parameter's valid_range, the orchestrator
     emits a WELL-FORMED MD job spec (what to simulate, which observable, which
     estimator). Stubbed this sprint: returns the cached/literature value with
     WIDENED uncertainty and a flag; the job spec is queued for a real MD run.

  2. FreeDTS Tier-1 seam — a config-generator + run-wrapper behind the SAME
     evaluator interface as Tier-0, so swapping in the dynamically-triangulated
     surface solver later changes nothing in the orchestrator. Stubbed: writes a
     valid FreeDTS input deck and returns a "would-run" marker.

The reverse seam is noted too: a found FreeDTS shape backmaps to CG-MD via TS2CG
(push a mesoscale result down to molecular detail).
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field, asdict

from .schemas import ParameterRecord, StatePoint


# --------------------------------------------------------------------------
# 1. MD-Gap Queue
# --------------------------------------------------------------------------
# Which estimator computes which observable — the recipe the MD run must follow.
ESTIMATORS = {
    "c0": "first moment of the lateral pressure profile (kappa*c0 = -integral z*[pL-pN] dz)",
    "kappa": "bilayer bending modulus from the height-fluctuation spectrum <|h_q|^2> ~ kBT/(kappa q^4)",
    "area_per_lipid": "mean projected area / (N_lipids per leaflet), equilibrated block average",
    "insertion_depth": "helix COM z relative to phosphate plane, averaged over the trajectory",
    "lambda_line": "line tension from the ka-band capillary-wave spectrum of the domain boundary",
}


@dataclass
class MDJobSpec:
    """A well-formed MD job the orchestrator would dispatch to fill a gap."""
    param: str
    system: str                       # what to simulate, e.g. "POPC:PIP2 95:5 bilayer"
    observable: str
    estimator: str
    target_state_point: dict          # T, tension, composition needed
    reason: str                       # why the gap exists
    priority: str = "normal"
    ensemble: str = "CG-Martini3"     # suggested model resolution
    job_id: str = ""

    def __post_init__(self):
        if not self.job_id:
            payload = f"{self.param}|{self.system}|{json.dumps(self.target_state_point, sort_keys=True)}"
            self.job_id = "md_" + hashlib.sha256(payload.encode()).hexdigest()[:10]

    def to_dict(self):
        return asdict(self)


class MDGapQueue:
    def __init__(self):
        self.queue: list[MDJobSpec] = []

    def check_and_emit(self, rec: ParameterRecord, target: StatePoint,
                       load_bearing: bool = False):
        """If rec does not apply at target, emit a job spec and return a
        gap-flagged record (widened uncertainty). Otherwise return rec unchanged.

        load_bearing=True + a gap that cannot be safely widened -> refuse
        (returns (None, spec)) so the orchestrator can decline rather than
        silently extrapolate."""
        ok, why = rec.applies_at(target)
        if ok:
            return rec, None
        spec = MDJobSpec(
            param=rec.param,
            system=rec.state_point.composition or rec.provenance.identifier or "unspecified bilayer",
            observable=rec.param,
            estimator=ESTIMATORS.get(rec.param, "TODO: define estimator"),
            target_state_point=target.to_dict(),
            reason=f"state-point mismatch: {why}",
            priority="high" if load_bearing else "normal",
        )
        self.queue.append(spec)
        # stub: widen uncertainty rather than fabricate a new value
        widened = ParameterRecord(
            param=rec.param, value=rec.value, uncertainty=rec.uncertainty * 2.5,
            units=rec.units, state_point=rec.state_point, provenance=rec.provenance,
            valid_range=rec.valid_range,
            flags=list(rec.flags) + ["md_gap", "widened_uncertainty", f"jobspec:{spec.job_id}"],
        )
        if load_bearing and rec.uncertainty * 2.5 > abs(rec.value):
            # gap is load-bearing and uncertainty would swamp the value -> refuse
            return None, spec
        return widened, spec

    def dump(self, path: str):
        json.dump([s.to_dict() for s in self.queue], open(path, "w"), indent=2)
        return path


# --------------------------------------------------------------------------
# 2. FreeDTS Tier-1 seam (config-generator behind the evaluator interface)
# --------------------------------------------------------------------------
def freedts_config(case, proposal_contribs: dict) -> str:
    """Generate a valid FreeDTS input deck from a resolved orchestration.

    FreeDTS = dynamically triangulated surface; vertex inclusions = the proteins;
    constant-tension frame; external forces. This writes the deck the Tier-1
    evaluator WOULD run. Wired behind the same interface as evaluator_tier0 so
    swapping it in changes nothing upstream.
    """
    c_eff = sum(c.get("c0_contribution_inv_nm", 0.0)
                for k, c in proposal_contribs.items() if k != "tension")
    kappa_factor = 1.0
    for c in proposal_contribs.values():
        kappa_factor *= c.get("kappa_factor", 1.0)
    deck = f"""# FreeDTS input deck (auto-generated by curvo) — STUB, not run this sprint
# case: {case.name}
Integrator = MC
Temperature = 1.0                       # reduced units (kBT)
Box = 60 60 60
Kappa = {case.kappa_kBT * kappa_factor:.3f}    # kBT (coat-stiffened)
Tension_Frame = ConstantTension
Sigma = {case.sigma_kBT_nm2:.4f}         # kBT/nm^2
# Vertex inclusions represent the active players:
Inclusion_C0 = {c_eff:.4f}               # effective spontaneous curvature (nm^-1)
Inclusion_Coverage = fromProposal
Nsteps = 500000
Readout = mean_curvature_field, dome_omega_OP, neck_radius
# Reverse seam: TS2CG backmap of the resulting shape to CG-MD is available.
"""
    return deck


class FreeDTSTier1:
    """Stubbed Tier-1 evaluator with the SAME call signature as the Tier-0 path.

    available() reports False this sprint (build not attempted on this host);
    evaluate() writes the deck and returns a 'would_run' marker so the seam is
    demonstrable and the upgrade is drop-in.
    """
    tier = "tier1_freedts"

    def available(self) -> bool:
        return False   # not built this sprint (README § Design and development)

    def evaluate(self, case, proposal_contribs: dict, deck_path: str = "cache/freedts_deck.inp"):
        deck = freedts_config(case, proposal_contribs)
        with open(deck_path, "w") as f:
            f.write(deck)
        return {
            "tier": self.tier,
            "status": "would_run",
            "deck_path": deck_path,
            "note": "FreeDTS not built this sprint; deck is valid and runnable later. "
                    "Tier-0 analytic evaluator carried the demo (README § Design and development).",
        }
