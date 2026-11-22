"""Failure controls for scientific reporting; no studies, downloads, or long fits."""

from dataclasses import replace
from types import SimpleNamespace
import json

import numpy as np
import pytest
import requests

from curvo import analyze, inverse, mechanism, perception, players, parameter_store
from curvo.schemas import StatePoint
from mechanome.schema import MechanoClaim, Value, TierViolation


SYNTHETIC = inverse.ObservationContext(
    input_kind="synthetic", calibration_id="synthetic_renderer_v1"
)


def install_pipeline(monkeypatch, *, valid=True, capped=False):
    fields = dict(H_inv_nm=.01, H_sigma_inv_nm=.001, depth_nm=30.,
                  actin_density=.5, actin_sigma=.05, coat_coverage=.5,
                  geometry_valid=valid)
    trace = SimpleNamespace(
        extractor="test", arr=lambda name: np.full(24, fields[name]),
        frames=[SimpleNamespace(quality_reason="test") for _ in range(24)],
    )
    monkeypatch.setattr(perception.PerceptionProvider, "extract", lambda *a, **kw: trace)
    calls = []

    def fit(*args, params=None, **kwargs):
        params = params or inverse.DEFAULT_PARAMS
        calls.append(kwargs)
        rng = np.random.default_rng(12)
        samples = np.column_stack([
            rng.normal((p.lo+p.hi)/2, (p.hi-p.lo)/100, 300) for p in params
        ])
        return dict(samples=samples, params=params, logz=10. if len(params) == 3 else 0.,
                    logz_err=.1, stopped_early=capped)

    monkeypatch.setattr(inverse, "run_nested", fit)
    return calls


@pytest.mark.parametrize("context,options,expected", [
    (SYNTHETIC, {}, "synthetic_model_conditional"),
    (None, {}, "exploratory"),
    (replace(SYNTHETIC, input_kind="experimental"), {}, "exploratory"),
    (replace(SYNTHETIC, actin_force_scale_pN=120.), {}, "exploratory"),
    (replace(SYNTHETIC, coverage=tuple(np.linspace(0, 1, 24))), {}, "exploratory"),
    (SYNTHETIC, {"psf_sigma_nm": 25.}, "exploratory"),
    (SYNTHETIC, {"A_coat_nm2": 20000.}, "exploratory"),
])
def test_context_controls_force_and_mechanism_reports(monkeypatch, context, options, expected):
    # Exercise the future qualified path; production has no current qualification.
    monkeypatch.setattr(analyze, "RECOVERY_CALIBRATED", {"active_force_max"})
    calls = install_pipeline(monkeypatch)
    report = analyze.analyze(np.zeros((24, 3, 128, 128)), context=context, **options)
    assert report["analysis_status"] == expected
    supported = expected == "synthetic_model_conditional"
    assert (report["forces"]["active_force_max"]["point_estimate"] is not None) == supported
    assert report["favored_mechanism"]["decisive"] == supported
    assert len(calls) == 5 and all(c["context"] == (context or inverse.ObservationContext()) for c in calls)


def test_capped_full_and_restricted_fits_remain_provisional(monkeypatch):
    monkeypatch.setattr(analyze, "RECOVERY_CALIBRATED", {"active_force_max"})
    install_pipeline(monkeypatch, capped=True)
    report = analyze.analyze(np.zeros((24, 3, 128, 128)), context=SYNTHETIC)
    assert report["analysis_status"] == "provisional"
    assert report["forces"]["active_force_max"]["point_estimate"] is None
    assert report["favored_mechanism"]["incomplete_fits"]
    assert not report["favored_mechanism"]["decisive"]


def test_historical_calibration_cannot_license_the_changed_pipeline(monkeypatch):
    install_pipeline(monkeypatch)
    report = analyze.analyze(np.zeros((24, 3, 128, 128)), context=SYNTHETIC)
    assert report["analysis_status"] == "exploratory"
    assert report["forces"]["active_force_max"]["point_estimate"] is None
    assert any("awaits recovery qualification" in reason for reason in report["provenance"]["calibration_issues"])


@pytest.mark.parametrize("change", ["timing", "psf", "brightness"])
def test_rendered_mismatches_are_exploratory(monkeypatch, change):
    from curvo import synth_movie
    actual_extractor = perception.PerceptionProvider.extract
    calls = install_pipeline(monkeypatch)
    monkeypatch.setattr(perception.PerceptionProvider, "extract", actual_extractor)
    psf = 25. if change == "psf" else 18.
    photons = 440. if change == "brightness" else 220.
    forces = dict(sigma_kBT_nm2=.02, c_eff_max_inv_nm=.015,
                  active_force_max_pN=40., T=24, active_delay=.2 if change == "timing" else 0.)
    movie, gt = synth_movie.render_movie(forces, psf_sigma_nm=psf,
                                         peak_photons=photons, has_actin=True)
    context = replace(SYNTHETIC, coverage=tuple(np.linspace(0, 1, 24))) if change == "timing" else SYNTHETIC
    report = analyze.analyze(movie, channels=gt.channels, context=context,
                             psf_sigma_nm=psf, peak_photons=photons)
    if report["analysis_status"] == "unsupported":
        assert report["uncertainty"]["n_resolved_frames"] == 0
        assert not calls and not report["forces"]
    else:
        assert report["analysis_status"] == "exploratory"
        assert report["uncertainty"]["n_resolved_frames"] > 0
        assert report["forces"]["active_force_max"]["point_estimate"] is None
    reason = "custom coverage" if change == "timing" else "imaging conditions"
    assert any(reason in issue for issue in report["provenance"]["calibration_issues"])


def test_invalid_geometry_never_reaches_sampling(monkeypatch):
    calls = install_pipeline(monkeypatch, valid=False)
    report = analyze.analyze(np.zeros((24, 3, 128, 128)), context=SYNTHETIC)
    assert report["analysis_status"] == "unsupported"
    assert not report["forces"] and not calls


def test_deep_cap_and_failed_bootstrap_are_invalid(monkeypatch):
    monkeypatch.setattr(perception, "_membrane_edge", lambda *a: (
        np.linspace(-30, 30, 40), np.full(40, 80.), 0))
    meta = dict(nm_per_px=2., channels=["membrane", "coat"], psf_sigma_nm=18.)
    for n_boot in (0, 10):
        trace = perception.extract_geometry_analytic(np.ones((2, 2, 8, 8)), meta, n_boot=n_boot)
        assert all(not f.geometry_valid and f.H_sigma_inv_nm > 0 for f in trace.frames)
        assert trace.provenance.source == "unknown_movie"


@pytest.mark.parametrize("mode", ["negative_sigma", "no_frames", "short_trace"])
def test_invalid_observations_fail_before_sampling(mode):
    H, sigma, mask = np.ones(24), np.ones(24), np.ones(24, bool)
    if mode == "negative_sigma": sigma[3] = -1
    if mode == "no_frames": mask[:] = False
    if mode == "short_trace": H = H[:-1]
    with pytest.raises(ValueError):
        inverse.make_loglike(H, sigma, inverse.DEFAULT_PARAMS, 10000., mask=mask)


def test_supplied_coverage_and_force_scale_change_the_shared_likelihood():
    context = replace(SYNTHETIC, coverage=tuple(np.linspace(0, .8, 24)), actin_force_scale_pN=120.)
    theta, area = [.03, 30., .02], 10000.
    H = inverse.predict_H(theta, inverse.DEFAULT_PARAMS, area, context=context)
    actin = np.array(context.coverage) * 30/120
    def score(ctx):
        return inverse.make_loglike(H, np.full(24, .001), inverse.DEFAULT_PARAMS, area,
                                   actin_obs=actin, actin_sigma=np.full(24, .01), context=ctx)(theta)
    assert score(context) > score(SYNTHETIC)
    # A force-free hypothesis must still score the same measured actin channel.
    restricted = mechanism._params_for(["c_eff_max", "sigma"])
    with_actin = inverse.make_loglike(H, np.ones(24), restricted, area,
                    actin_obs=actin, actin_sigma=np.full(24, .01), context=context)
    no_actin = inverse.make_loglike(H, np.ones(24), restricted, area, context=context)
    assert with_actin([.03, .02]) < no_actin([.03, .02])


def test_context_copies_mutable_coverage_before_fitting():
    values = np.linspace(0, 1, 24)
    context = inverse.ObservationContext(coverage=values)
    values[:] = 0
    assert context.coverage[-1] == 1


def test_large_error_in_any_competitor_prevents_a_decisive_verdict(monkeypatch):
    def fit(name, *a, **kw):
        return dict(name=name, free=mechanism.HYPOTHESES[name],
                    logz={"wedge+actin": 10., "wedge_only": 0., "actin_only": -1.}[name],
                    logz_err=10. if name == "actin_only" else .1,
                    stopped_early=False, n_params=2,
                    identifiability={"active_force_max": {"identified": True}})
    monkeypatch.setattr(mechanism, "fit_hypothesis", fit)
    verdict, _ = mechanism.discriminate([], [], 10000., hypotheses=["wedge+actin", "wedge_only", "actin_only"])
    assert not verdict["decisive"]
    assert verdict["numerical_gap_lower_bound"] < 2.5
    assert all("logz_err" in row for row in verdict["ranking"])


@pytest.mark.parametrize("name,rep,params,context", [
    ("wedge", "made_up", {}, {"amphipathic": True}),
    ("wedge", "c0_plus_kappa_softening", {"tension_half_kBT_nm2": 0}, {"amphipathic": True}),
    ("crowding", "saturating_surface_pressure", {"coverage": -.1}, {}),
    ("crowding", "saturating_surface_pressure", {"phi_half": 0}, {}),
    ("coat", "rigidity_area_constraint", {"intrinsic_c0_inv_nm": float("nan")}, {}),
])
def test_invalid_physics_is_rejected(name, rep, params, context):
    assert not players.PLAYERS[name].validate(rep, params, context)[0]


@pytest.mark.parametrize("correction", [-2., float("nan"), 2.])
def test_invalid_coupling_cannot_reach_the_evaluator(correction):
    with pytest.raises(ValueError):
        players.combine_curvature({}, correction)


def test_applicability_distinguishes_mismatch_unknown_and_supported():
    rec = parameter_store.literature("kappa", "POPC")
    assert not rec.applies_at(StatePoint(temperature_K=303, composition="DOPE"))[0]
    ok, reason = rec.applies_at(StatePoint(composition="POPC"))
    assert not ok and reason.startswith("unknown applicability")
    assert rec.applies_at(StatePoint(temperature_K=303, composition="POPC"))[0]


def test_cache_identity_and_checksum_are_verified(tmp_path, monkeypatch):
    def response(values, status=200):
        reply = requests.Response()
        reply.status_code = status
        reply._content = json.dumps(values).encode()
        return reply
    monkeypatch.setattr(parameter_store.requests, "get", lambda *a, **kw: response([[0, 60], [1, 64]]))
    parameter_store.nmrlipids_area_per_lipid("A", tmp_path)
    cache = next(tmp_path.glob("*.json"))
    original = json.loads(cache.read_text())
    monkeypatch.setattr(parameter_store.requests, "get", lambda *a, **kw: response([], 503))
    with pytest.raises(requests.HTTPError):
        parameter_store.nmrlipids_area_per_lipid("B", tmp_path)
    for key, changed in (("simulation", "B"), ("sha256", "incorrect")):
        cache.write_text(json.dumps({**original, key: changed}))
        with pytest.raises(ValueError, match="mismatch"):
            parameter_store.nmrlipids_area_per_lipid("A", tmp_path)


@pytest.mark.parametrize("changes", [
    {"forward_model": "unknown"}, {"value": Value(float("nan"), 1, "pN")},
    {"value": Value(1, -1, "pN")}, {"evidence": []},
    {"input_kind": "experimental", "validation": "real_force_paired"},
])
def test_claims_cannot_promote_unsupported_evidence(changes):
    kwargs = dict(forward_model="helfrich_v1", value=Value(1, .1, "pN"),
                  identifiability="constrained", evidence=["synthetic round trip"],
                  input_kind="synthetic", validation="analytic_limit")
    kwargs.update(changes)
    with pytest.raises(TierViolation):
        MechanoClaim("x", "bears", "force", "GROUNDED", **kwargs)


def test_mutating_a_valid_claim_cannot_bypass_serialization_checks():
    from mechanome import emit
    claim = emit.emit_tether_force_claim()
    assert claim.to_dict()["input_kind"] == "synthetic"
    claim.value.uncertainty = -1
    with pytest.raises(TierViolation):
        claim.to_dict()
