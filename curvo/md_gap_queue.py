"""Queue MD job specifications when parameters do not cover the target state.

The queue records what should be simulated; it does not run simulations.
Until a measurement is available, records retain widened uncertainty and
explicit gap flags.
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict

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
