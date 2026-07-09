"""
curvo.schemas — core data contracts for the curvature-orchestration pipeline.

Every object here is a frozen-ish dataclass with a to_dict() so that any record
can be serialized into an OrchestrationRecord and, ultimately, into the SVG
schematic and provenance log. The design rule from the sprint plan is enforced
structurally: *every stored parameter carries provenance + validity range +
uncertainty*. You cannot construct a ParameterRecord without them.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# --------------------------------------------------------------------------
# Provenance & state points
# --------------------------------------------------------------------------
@dataclass
class StatePoint:
    """The thermodynamic/compositional conditions a parameter is valid at."""
    temperature_K: Optional[float] = None
    tension_mN_per_m: Optional[float] = None
    composition: Optional[str] = None          # free text, e.g. "POPC:PIP2 95:5"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Provenance:
    """Where a value came from. Non-negotiable for a scalable autonomous loop."""
    source: str                                 # "AlphaFoldDB", "NMRlipids", "literature:Rand-Fuller-1989", ...
    access: str = "cached"                       # "live_api" | "cached" | "stub" | "computed"
    identifier: str = ""                         # UniProt ID, DOI, DB accession, ...
    model_version: str = ""                      # e.g. AlphaFold model version, DB snapshot
    retrieved_at: float = field(default_factory=time.time)
    citation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ParameterRecord:
    """Uniform record for every physical parameter in the store.

    Construction requires value, uncertainty, state_point, provenance and a
    validity range — this is what lets the orchestrator decide whether existing
    data actually applies or whether it must flag an MD gap.
    """
    param: str                                  # canonical name, e.g. "c0", "kappa", "lambda_line"
    value: float
    uncertainty: float                          # 1-sigma, same units as value
    units: str
    state_point: StatePoint
    provenance: Provenance
    valid_range: dict = field(default_factory=dict)   # e.g. {"tension_mN_per_m": [0, 0.5]}
    flags: list = field(default_factory=list)         # e.g. ["extrapolated", "md_gap", "widened_uncertainty"]

    def applies_at(self, target: StatePoint, tol: dict | None = None) -> tuple[bool, str]:
        """Does this record apply at the target state point (within valid_range)?

        Returns (ok, reason). The orchestrator uses this to decide use-data vs
        flag-MD. Kept deliberately simple: numeric fields must fall inside
        valid_range (if that field's range is stored).
        """
        tol = tol or {}
        for fld, rng in self.valid_range.items():
            tv = getattr(target, fld, None)
            if tv is None:
                continue
            lo, hi = rng
            pad = tol.get(fld, 0.0)
            if tv < lo - pad or tv > hi + pad:
                return False, f"{fld}={tv} outside valid_range {rng} (+/-{pad})"
        return True, "within valid_range"

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# --------------------------------------------------------------------------
# Structure / ML-model provider
# --------------------------------------------------------------------------
@dataclass
class StructureModel:
    """Uniform return from any structure provider (AlphaFold DB, ESMFold, ...).

    coords are kept out of the serialized dict by default (large); a summary is
    stored instead. per_residue_pLDDT and the disorder cross-check drive the
    representation decision.
    """
    uniprot_id: str
    sequence: str
    per_residue_pLDDT: list                      # one float per residue
    provenance: Provenance
    coords_path: str = ""                        # path to PDB/CIF on disk
    pae_available: bool = False
    n_residues: int = 0

    def __post_init__(self):
        if not self.n_residues:
            self.n_residues = len(self.per_residue_pLDDT)

    def to_dict(self, include_plddt: bool = True) -> dict:
        d = {
            "uniprot_id": self.uniprot_id,
            "n_residues": self.n_residues,
            "sequence_len": len(self.sequence),
            "provenance": self.provenance.to_dict(),
            "coords_path": self.coords_path,
            "pae_available": self.pae_available,
            "mean_pLDDT": (sum(self.per_residue_pLDDT) / len(self.per_residue_pLDDT))
                          if self.per_residue_pLDDT else None,
        }
        if include_plddt:
            d["per_residue_pLDDT"] = self.per_residue_pLDDT
        return d


# --------------------------------------------------------------------------
# Players, proposals, decisions
# --------------------------------------------------------------------------
@dataclass
class RepresentationDecision:
    """One player's representation choice, with the rule/justification behind it.

    Under the bitter-lesson reframing this is the OUTPUT of search+guardrail,
    not a lookup in a fixed table. `chosen_by` records which: 'search',
    'guardrail_prune', or 'prior'.
    """
    player: str                                  # "wedge", "crowding", "coat", "tension"
    representation: str                          # the candidate that was chosen
    candidates_considered: list
    rule: str                                    # the physical guardrail that gated it
    justification: str                           # natural-language reasoning
    chosen_by: str = "search"
    signals: dict = field(default_factory=dict)  # e.g. {"mean_pLDDT": 91.2, "disorder_frac": 0.02}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PlayerProposal:
    """A proposed configuration for one player: representation + resolved params."""
    player: str
    decision: RepresentationDecision
    parameters: dict                             # {param_name: ParameterRecord.to_dict()}

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "decision": self.decision.to_dict(),
            "parameters": self.parameters,
        }


# --------------------------------------------------------------------------
# Evaluator results
# --------------------------------------------------------------------------
@dataclass
class EvaluatorResult:
    """Ground-truth output from the evaluator. The LLM never invents these."""
    tier: str                                    # "tier0_analytic" | "tier1_freedts"
    observables: dict                            # e.g. {"tube_radius_nm": 42.0, "mean_curvature_inv_nm": 0.021}
    objective_value: float                       # scalar the loop optimizes (e.g. |achieved - target|)
    target_met: bool
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# The master record: one orchestration iteration
# --------------------------------------------------------------------------
@dataclass
class OrchestrationRecord:
    """Everything about one loop iteration: config + provenance + reasoning +
    evaluator result + version hashes. The SVG schematic and provenance log are
    both generated from this object, so they are faithful views of the result.
    """
    case: str                                    # "epsin_ccs", "budding_anchor", "iav_spherical", ...
    iteration: int
    target: dict                                 # {observable, value, tolerance}
    proposals: list                              # [PlayerProposal.to_dict(), ...]
    evaluator_result: dict                       # EvaluatorResult.to_dict()
    reasoning_trace: str = ""                     # the orchestrator's post-mortem
    md_gaps: list = field(default_factory=list)   # emitted job specs, if any
    version_hashes: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def content_hash(self) -> str:
        payload = json.dumps(
            {"case": self.case, "iteration": self.iteration,
             "target": self.target, "proposals": self.proposals,
             "evaluator_result": self.evaluator_result},
            sort_keys=True, default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["content_hash"] = self.content_hash()
        return d


def version_hashes_of(*modules) -> dict:
    """Hash the source of given modules for provenance/version tracking."""
    import inspect
    out = {}
    for m in modules:
        try:
            src = inspect.getsource(m)
            out[m.__name__] = hashlib.sha256(src.encode()).hexdigest()[:12]
        except (OSError, TypeError):
            out[getattr(m, "__name__", str(m))] = "unknown"
    return out
