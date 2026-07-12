"""
Contract tests for the four analytic-tier mechanome forward models
(tissue, cortex, bond, channel), the registry promotion, and grounded-analytic
claim emission.

Each module carries a self_validate() that must recover its closed-form limit
and reproduce its published anchor's parameters to a tight tolerance. These tests
lock that in, plus the registry's validation-tier invariants and the schema-tier
enforcement on the emitted claims.
"""
import math

from mechanome import (forward_tissue as ti, forward_cortex as co,
                       forward_bond as bo, forward_channel as ch)
from mechanome import registry as reg
from mechanome import emit


# --- per-module analytic self-validation ------------------------------------
def test_tissue_self_validate():
    v = ti.self_validate()
    assert v["passed"]
    assert v["force_balance_residual"] < 1e-9        # 120 deg symmetric limit
    assert v["tension_roundtrip_rel_err"] < 1e-9


def test_cortex_self_validate():
    v = co.self_validate()
    assert v["passed"]
    assert v["roundtrip_max_rel_err"] < 1e-9         # Young-Laplace round-trip
    assert v["micropipette"]["rel_err"] < 1e-9


def test_bond_self_validate():
    v = bo.self_validate()
    assert v["passed"]
    assert v["bell"]["xd_rel_err"] < 1e-9            # Bell x-dagger recovery
    assert v["catch_slip"]["peak_rel_err"] < 1e-3    # catch-slip peak analytic=numeric


def test_channel_self_validate():
    v = ch.self_validate()
    assert v["passed"]
    assert v["mscl"]["dA_rel_err"] < 1e-9            # MscL gating-area recovery
    assert v["slope_check"]["rel_err"] < 1e-6        # dPo/dsigma = dA/4kBT identity
    assert abs(v["curvo_link_Po_at_midpoint"] - 0.5) < 1e-3


def test_channel_anchor_parameters():
    # the verified Sukharev 1999 anchor values must be exactly these
    assert ch.MSCL_SIGMA_HALF_mN_m == 11.8
    assert ch.MSCL_DA_nm2 == 6.5


# --- registry promotion invariants ------------------------------------------
def test_registry_four_modules_analytic():
    status = reg.module_status()
    assert status["membrane"]["status"] == "built_validated"
    for m in ("tissue", "cortex", "bond", "channel"):
        assert status[m]["status"] == "built_analytic"


def test_registry_forward_models_registered():
    fms = reg.registered_forward_models()
    for name in ("helfrich_v1", "vertex_v1", "active_gel_v1",
                 "catch_slip_v1", "ms_gating_v1"):
        assert name in fms
        assert fms[name]["status"] == "executable"


def test_grounded_gate_is_real_only():
    # only the real force-paired module may emit REAL-data grounded claims
    assert reg.can_emit_grounded("membrane")
    for m in ("tissue", "cortex", "bond", "channel"):
        assert not reg.can_emit_grounded(m)


def test_analytic_gate_and_provenance():
    for m in ("membrane", "tissue", "cortex", "bond", "channel"):
        assert reg.can_emit_analytic(m)
    assert reg.validation_provenance("membrane") == "real_force_paired"
    assert reg.validation_provenance("tissue") == "analytic_limit"
    assert reg.validation_provenance("nonexistent") == "unregistered"


# --- grounded-analytic claim emission ---------------------------------------
def test_emit_from_module_carries_provenance():
    for m in ("tissue", "cortex", "bond", "channel"):
        c = emit.emit_from_module(m)
        # GROUNDED tier, has value + identifiability + forward model
        assert c.epistemic_tier.value == "GROUNDED"
        assert c.value is not None and c.identifiability is not None
        assert c.forward_model is not None
        # provenance is on the face of the evidence
        assert any(e == "validation=analytic_limit" for e in c.evidence)


def test_emit_relations_span_verbs():
    rels = {emit.emit_from_module(m).relation
            for m in ("tissue", "cortex", "bond", "channel")}
    assert {"transmits", "generates", "bears", "senses"} <= rels


def test_emit_channel_reads_membrane_tension():
    c = emit.emit_from_module("channel")
    assert c.object == "membrane_tension"
    assert c.value.estimate == 11.8       # MscL midpoint, mN/m


# --- structural screen: integrity of the vendored frozen ranking ------------
def test_structural_screen_frozen_hash_reproduces():
    from mechanome import structural_screen as ss
    v = ss.verify_frozen_ranking()
    # the stored CSV and the computed stage-3 CSV both reproduce the frozen hash
    assert v["passed"], v
    assert v["stored_hash"] == "41d49328960d4083"
    assert v["hash_from_frozen_csv"] == v["stored_hash"]
    assert v["hash_from_stage3_csv"] == v["stored_hash"]


def test_structural_screen_energy_scale_consistent():
    # the screen's standalone energy scale must agree with curvo.constants
    from mechanome import structural_screen as ss
    assert ss.verify_energy_scale_consistency()["consistent"]


def test_structural_screen_prereg_is_nine_go_terms():
    # the pre-registered label set is exactly the nine GO IDs scored
    from mechanome import structural_screen as ss
    assert len(ss.prereg_go_terms()) == 9


def test_structural_screen_bar_radii_reproduce_literature():
    # method validating on home turf: the top scaffolds are the textbook BAR
    # curvature generators, in the expected order (dynamin > endophilin > amphiphysin)
    from mechanome import structural_screen as ss
    top3 = list(ss.frozen_ranking().head(3)["protein"])
    assert top3[0] == "Dynamin-1"
    assert "Endophilin" in top3[1]
    assert "Amphiphysin" in top3[2]


def test_structural_screen_registered_and_emits():
    # registered as a molecule-scale forward model + emits a GROUNDED analytic claim
    assert "structural_screen_v1" in reg.FORWARD_MODELS
    assert reg.FORWARD_MODELS["structural_screen_v1"].scale == "molecule"
    assert reg.validation_provenance("structural_screen") == "analytic_limit"
    c = emit.emit_from_module("structural_screen")
    assert c.epistemic_tier.value == "GROUNDED"
    assert c.forward_model == "structural_screen_v1"
    assert any(e == "validation=analytic_limit" for e in c.evidence)


def test_structural_screen_channel_link():
    # the cross-scale seam: MscL's structure-derived c0 -> gating Po=0.5 at midpoint
    from mechanome import channel_link as cl
    channels = {c["channel"] for c in cl.channels_from_screen()}
    assert {"MscL", "Piezo1", "TRAAK"} <= channels
    link = cl.link_channel_to_gating("MscL", 11.8)   # at the MscL midpoint tension
    assert link["source_model"] == "structural_screen_v1"
    assert link["gating_model"] == "ms_gating_v1"
    assert abs(link["open_probability"] - 0.5) < 1e-9
    # a channel whose display name differs from its screen protein key (e.g.
    # "TRAAK" vs "TRAAK (K2P4.1)") must resolve by EITHER name, and every screened
    # channel must return a valid open probability.
    assert abs(cl.link_channel_to_gating("TRAAK", 11.8)["open_probability"] - 0.5) < 1e-9
    for c in cl.channels_from_screen():
        for key in (c["protein"], c["channel"]):
            assert 0.0 <= cl.link_channel_to_gating(key, 11.8)["open_probability"] <= 1.0
