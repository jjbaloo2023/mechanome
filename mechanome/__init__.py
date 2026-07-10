"""mechanome — curvo's ParameterRecord discipline promoted to a federated,
tier-enforced data contract for the mechanical layer of the cell.

curvo is the reference implementation of a single GROUNDED module; this package
is the schema every module (built or stubbed) speaks.
"""
from .schema import (MechanoClaim, EpistemicTier, Identifiability, Actor,
                     Context, Value, TierViolation, MECHANICAL_ROLES,
                     RELATIONS, SCALES)

__version__ = "0.1.0"
__all__ = ["MechanoClaim", "EpistemicTier", "Identifiability", "Actor",
           "Context", "Value", "TierViolation", "MECHANICAL_ROLES",
           "RELATIONS", "SCALES"]
