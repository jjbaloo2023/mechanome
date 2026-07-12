"""Contract tests for the mechanome schema, emitters, registry, and links.

The firewall tests (a GROUNDED claim without a value, a LINKED claim WITH a value,
a MEASURED claim without a citation) are the heart of the suite: they prove the
schema structurally forbids laundering a lower tier into a higher one.
"""
from contextlib import contextmanager

from mechanome.schema import (MechanoClaim, EpistemicTier, Value, Context,
                              Actor, TierViolation)
from mechanome import emit, links, registry


@contextmanager
def raises(exc):
    """Minimal pytest.raises substitute (no pytest dependency)."""
    try:
        yield
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} but none was raised")


# --- the credibility firewall -----------------------------------------------
def test_grounded_requires_value_and_identifiability():
    with raises(TierViolation):
        MechanoClaim("x", "generates", "curvature", "GROUNDED",
                     forward_model="helfrich_v1")   # no value, no identifiability


def test_linked_forbids_a_physical_value():
    with raises(TierViolation):
        MechanoClaim("membrane_tension", "modulates", "YAP", "LINKED",
                     value=Value(23, 5, "pN"),
                     evidence=["chain: a->b"], reasoning_trace="test")


def test_measured_requires_a_citation():
    with raises(TierViolation):
        MechanoClaim("kappa", "bears", "tension", "MEASURED",
                     value=Value(23, 5, "kBT"), evidence=["no citation"])
    # WITH a citation it is valid
    ok = MechanoClaim("kappa", "bears", "tension", "MEASURED",
                      value=Value(23, 5, "kBT"),
                      evidence=["Roy et al. 2020, doi:10.1021/acs.nanolett.9b05232"])
    assert ok.epistemic_tier is EpistemicTier.MEASURED


def test_linked_requires_chain_and_experiment():
    with raises(TierViolation):
        MechanoClaim("a", "modulates", "b", "LINKED",
                     evidence=["just prose, no chain"], reasoning_trace="test")
    with raises(TierViolation):
        MechanoClaim("a", "modulates", "b", "LINKED",
                     evidence=["chain: a->b"], reasoning_trace="")   # no experiment


# --- emitters produce schema-valid real claims ------------------------------
def test_emit_grounded_from_curvo():
    claims = emit.emit_all()
    assert len(claims) >= 2
    # derive the valid set from the registry so it never goes stale as models
    # are added (membrane + the analytic modules + the structural screen).
    from mechanome import registry as reg
    valid_fms = set(reg.FORWARD_MODELS)
    for c in claims:
        assert c.epistemic_tier is EpistemicTier.GROUNDED
        assert c.value is not None and c.identifiability is not None
        # every GROUNDED claim names a registered forward model
        assert c.forward_model in valid_fms
    # the real force-paired membrane claim (helfrich_v1) is present
    assert any(c.forward_model == "helfrich_v1" for c in claims)


def test_family_claims_do_not_claim_epn1_trajectory():
    # honesty check: the capacity claims must NOT cite an EPN1 curvature trajectory
    for c in emit.emit_family_capacity_claims(top=3):
        joined = " ".join(c.evidence).lower() + c.reasoning_trace.lower()
        assert "trajectory" not in joined or "not on an epn1" in joined
        assert "synthetic_recovery:pass" in c.evidence


# --- the curated LINKED edge -------------------------------------------------
def test_yap_link_is_valueless_with_experiment():
    c = links.emit_tension_yap_link()
    assert c.epistemic_tier is EpistemicTier.LINKED
    assert c.value is None
    assert "hyperosmotic" in c.reasoning_trace.lower()


# --- registry: one real model, the rest honest stubs ------------------------
def test_registry_membrane_grounded_analytic_modules_not():
    # only the membrane module is force-paired (GROUNDED-emittable); the analytic
    # modules validate against an analytic limit + published anchor, not raw data,
    # so they emit at the analytic tier and can_emit_grounded is False for them.
    fms = registry.registered_forward_models()
    assert "helfrich_v1" in fms and fms["helfrich_v1"]["status"] == "executable"
    assert registry.can_emit_grounded("membrane") is True
    for analytic in ("tissue", "cortex", "bond", "channel"):
        assert registry.can_emit_grounded(analytic) is False


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} mechanome tests pass")
