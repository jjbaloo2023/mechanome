"""Unit tests for player guardrail validators (design_note.md §2b).
Guardrails PRUNE physically-wrong representations; they never decide."""
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from curvo import players as pl

CASES = [
    ("wedge", "anisotropic_inclusion", {"c0_contribution_inv_nm": 0.03},
     {"amphipathic": True, "coat_active": True}, False),
    ("wedge", "rigid_scaffold", {"c0_contribution_inv_nm": 0.03},
     {"amphipathic": True, "coat_active": True}, False),
    ("wedge", "c0_plus_kappa_softening", {"c0_contribution_inv_nm": 0.03},
     {"amphipathic": True, "coat_active": True}, True),
    ("wedge", "c0_plus_kappa_softening", {"c0_contribution_inv_nm": 0.03},
     {"amphipathic": False}, False),
    ("wedge", "c0_plus_kappa_softening", {"c0_contribution_inv_nm": 0.5},
     {"amphipathic": True, "coat_active": True}, False),
    ("crowding", "fixed_c0", {}, {"is_disordered": True}, False),
    ("crowding", "saturating_surface_pressure", {}, {"is_disordered": True}, True),
    ("crowding", "rigid_inclusion", {}, {"is_disordered": True}, False),
    ("coat", "isotropic_c0_source", {"rigidity_factor": 2.0},
     {"coat_role": "size_regularity"}, False),
    ("coat", "rigidity_area_constraint", {"rigidity_factor": 2.0},
     {"coat_role": "size_regularity"}, True),
    ("tension", "constant_tension_frame", {"sigma_kBT_nm2": 0.02}, {}, True),
    ("tension", "constant_tension_frame", {"sigma_kBT_nm2": 0.5}, {}, False),
]

def test_all_guardrails():
    for player, rep, params, ctx, expected in CASES:
        ok, reason = pl.PLAYERS[player].validate(rep, params, ctx)
        assert ok == expected, f"{player}/{rep}: got {ok}, expected {expected} ({reason})"

if __name__ == "__main__":
    test_all_guardrails()
    print("all guardrail tests pass")
