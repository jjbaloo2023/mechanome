"""
mechanome/schema.py — the MechanoClaim data contract with structural tier enforcement.

The whole design rests on one invariant:

    Every claim is GROUNDED (a forward-model inverse run against data, carrying
    value + uncertainty + identifiability), MEASURED (a cited experimental value
    with provenance), or LINKED (a flagged mechanotransduction hypothesis with an
    explicit causal chain and a proposed test, and NO physical value). The system
    never silently promotes a lower tier to a higher one. Tier is always visible.

This is curvo's ParameterRecord discipline (provenance + validity + uncertainty)
promoted to the organizing principle of the whole system. The GROUNDED<->LINKED
boundary is the credibility firewall: force-to-shape is force balance (a
well-posed inverse); force-to-transcription-factor-activity is multi-step
signaling (correlative). Mixing them is how a knowledge graph launders
correlation into physics — this schema forbids it structurally, in __post_init__,
by raising rather than emitting an invalid claim.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any

class EpistemicTier(str, Enum):
    GROUNDED = "GROUNDED"    # forward+inverse against data: value + uncertainty + identifiability
    MEASURED = "MEASURED"    # a cited experimental value with provenance
    LINKED = "LINKED"        # a flagged hypothesis: causal chain + proposed test, NO physical value


class Identifiability(str, Enum):
    CONSTRAINED = "constrained"
    PRIOR_DOMINATED = "prior_dominated"
    UNIDENTIFIABLE = "unidentifiable"


MECHANICAL_ROLES = ("generator", "sensor", "transmitter", "bearer", "modulator")
RELATIONS = ("generates", "senses", "transmits", "bears", "modulates")
SCALES = ("molecule", "membrane", "cortex", "cell", "tissue", "nucleus")


@dataclass
class Actor:
    """A protein / TF / lipid / cytoskeletal element / ECM node."""
    id: str                               # UniProt id, lipid name, "membrane_tension", ...
    type: str = "protein"                 # protein | TF | lipid | cytoskeleton | ECM | observable
    structure_ref: str = ""               # e.g. AlphaFold:Q9Y6I3
    sequence_ref: str = ""

    def to_dict(self): return asdict(self)


@dataclass
class Context:
    scale: str = "membrane"               # one of SCALES
    location: str = ""
    cell_type: str = ""
    mech_environment: str = ""            # "tension=elevated", "stiffness=high", ...

    def to_dict(self): return asdict(self)


@dataclass
class Value:
    estimate: float
    uncertainty: float
    units: str

    def to_dict(self): return asdict(self)


@dataclass
class MechanoClaim:
    """A single edge of the mechanome, wearing its epistemic tier on its face.

    Tier rules (enforced in __post_init__, raising TierViolation on breach):
      GROUNDED : requires forward_model, value, and identifiability
      MEASURED : requires value AND >=1 citation in evidence
      LINKED   : requires a causal chain (in evidence) AND a proposed experiment
                 (reasoning_trace), and FORBIDS a physical value
    """
    subject: Any                          # Actor or str
    relation: str                         # one of RELATIONS
    object: str                           # Observable name (curvature, tension, ...)
    epistemic_tier: EpistemicTier
    context: Optional[Context] = None
    forward_model: Optional[str] = None   # ForwardModelRef (registry key) | None
    value: Optional[Value] = None
    identifiability: Optional[Identifiability] = None
    evidence: List[str] = field(default_factory=list)   # provenance strings / citations / chains
    reasoning_trace: str = ""
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        # normalize enums passed as strings
        if isinstance(self.epistemic_tier, str):
            self.epistemic_tier = EpistemicTier(self.epistemic_tier)
        if isinstance(self.identifiability, str):
            self.identifiability = Identifiability(self.identifiability)
        if self.relation not in RELATIONS:
            raise TierViolation(f"relation {self.relation!r} not in {RELATIONS}")
        self._enforce_tier()

    # --- the credibility firewall -------------------------------------------
    def _enforce_tier(self):
        t = self.epistemic_tier
        has_citation = any(_looks_like_citation(e) for e in self.evidence)
        has_chain = any(_looks_like_chain(e) for e in self.evidence)

        if t is EpistemicTier.GROUNDED:
            missing = [n for n, v in (("forward_model", self.forward_model),
                                      ("value", self.value),
                                      ("identifiability", self.identifiability)) if v is None]
            if missing:
                raise TierViolation(f"GROUNDED claim missing required field(s): {missing}")

        elif t is EpistemicTier.MEASURED:
            if self.value is None:
                raise TierViolation("MEASURED claim requires a value")
            if not has_citation:
                raise TierViolation("MEASURED claim requires >=1 citation in evidence")

        elif t is EpistemicTier.LINKED:
            if self.value is not None:
                raise TierViolation(
                    "LINKED claim MUST NOT carry a physical value — this is the "
                    "credibility firewall (force-to-TF is correlative, not force balance)")
            if not has_chain:
                raise TierViolation("LINKED claim requires an explicit causal chain in evidence")
            if not self.reasoning_trace.strip():
                raise TierViolation("LINKED claim requires a proposed experiment in reasoning_trace")

    def to_dict(self) -> Dict[str, Any]:
        d = dict(
            subject=self.subject.to_dict() if isinstance(self.subject, Actor) else self.subject,
            relation=self.relation, object=self.object,
            context=self.context.to_dict() if self.context else None,
            forward_model=self.forward_model,
            value=self.value.to_dict() if self.value else None,
            identifiability=self.identifiability.value if self.identifiability else None,
            epistemic_tier=self.epistemic_tier.value,
            evidence=list(self.evidence),
            reasoning_trace=self.reasoning_trace)
        return d


class TierViolation(ValueError):
    """Raised when a MechanoClaim would violate its tier's contract."""


import re as _re
# a citation carries a DOI, a "source@date" provenance stamp, or an
# "Author (YYYY)" / "Author et al." form — not merely a stray digit.
_YEAR = _re.compile(r"(19|20)\d{2}")


def _looks_like_citation(e: str) -> bool:
    el = e.lower()
    if "doi:" in el or "@" in e:
        return True
    if "et al" in el and _YEAR.search(e):
        return True
    # "Surname 2012" / "Surname (2012)" style
    return bool(_re.search(r"[A-Za-z]{3,}\s*\(?(19|20)\d{2}", e))


def _looks_like_chain(e: str) -> bool:
    # a causal chain is written with an arrow and the "chain:" tag
    return e.strip().lower().startswith("chain:") or "->" in e or "\u2192" in e
