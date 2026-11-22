"""Fast branch coverage for the scientific decisions in the public pipelines."""

import copy

import numpy as np
import pytest

from curvo import analyze, inverse, mechanism, orchestrator


@pytest.mark.parametrize(
    "name,identified,stopped_early,expected_point",
    [
        ("active_force_max", True, False, 30.0),
        ("active_force_max", True, True, None),
        ("active_force_max", False, False, None),
        ("c_eff_max", True, False, None),
        ("sigma", True, False, None),
    ],
)
def test_point_estimates_require_both_credibility_gates(
    name, identified, stopped_early, expected_point, monkeypatch
):
    monkeypatch.setattr(analyze, "RECOVERY_CALIBRATED", {"active_force_max"})
    report = {
        name: dict(
            identified=identified,
            units="test",
            median=30.0,
            ci68=[25.0, 35.0],
            ci95=[20.0, 40.0],
            marginal_constrained=True,
            degenerate_with=[],
        )
    }
    original = copy.deepcopy(report)
    force = analyze._report_forces(report, stopped_early=stopped_early, calibration_supported=True)[name]
    assert force["point_estimate"] == expected_point
    assert force["ci95"] == [20.0, 40.0]
    assert report == original
    if expected_point is None:
        assert force["status"] == "underdetermined"
        assert force["reason"]


@pytest.mark.parametrize(
    "gap,extra_identified,incomplete_name,decisive",
    [
        (4.0, True, None, True),
        (4.0, True, "wedge_only", False),
        (4.0, True, "wedge+actin", False),
        (4.0, False, None, False),
        (1.0, True, None, False),
    ],
)
def test_evidence_win_requires_identifiable_extra_actor(
    monkeypatch, gap, extra_identified, incomplete_name, decisive
):
    def fit(name, *args, **kwargs):
        return dict(
            name=name,
            free=mechanism.HYPOTHESES[name],
            logz=gap if name == "wedge+actin" else 0.0,
            logz_err=0.1,
            stopped_early=name == incomplete_name,
            n_params=len(mechanism.HYPOTHESES[name]),
            identifiability={"active_force_max": {"identified": extra_identified}},
        )

    monkeypatch.setattr(mechanism, "fit_hypothesis", fit)
    verdict, fits = mechanism.discriminate(
        [], [], 100, hypotheses=["wedge_only", "wedge+actin"]
    )
    assert verdict["decisive"] is decisive
    assert verdict["favored"] == ("wedge+actin" if decisive else "UNDETERMINED")
    assert sum(fit["model_prob"] for fit in fits) == pytest.approx(1.0)
    assert ("suggested_experiment" in verdict) is not decisive
    assert verdict["incomplete_fits"] == ([incomplete_name] if incomplete_name else [])
    assert ("overfit_downgrade" in verdict) is (gap >= 2.5 and not extra_identified)


def test_unresolved_frames_do_not_contribute_to_either_likelihood():
    area = np.pi * 60**2
    theta = [0.03, 30, 0.02]
    curvature = inverse.predict_H(theta, inverse.DEFAULT_PARAMS, area)
    actin = np.linspace(0, 0.5, 24)
    mask = np.arange(24) >= 5

    def score(curvature_values, actin_values):
        return inverse.make_loglike(
            curvature_values,
            np.full(24, 0.003),
            inverse.DEFAULT_PARAMS,
            area,
            mask=mask,
            actin_obs=actin_values,
            actin_sigma=np.full(24, 0.05),
        )(theta)

    expected = score(curvature, actin)
    curvature[~mask] = 1e6
    actin[~mask] = 1e6
    assert score(curvature, actin) == expected


def test_hypothesis_fit_preserves_sampler_status(monkeypatch):
    monkeypatch.setattr(
        inverse,
        "run_nested",
        lambda *a, **kw: dict(samples=[], logz=0.0, logz_err=1.0, stopped_early=True),
    )
    monkeypatch.setattr(inverse, "identifiability", lambda *a: {})
    fit = mechanism.fit_hypothesis("wedge_only", [], [], 100)
    assert fit["stopped_early"] is True


@pytest.mark.parametrize(
    "hypotheses", [[], ["wedge_only"], ["wedge_only"] * 2, ["wedge_only", "invented"]]
)
def test_invalid_comparisons_fail_before_sampling(monkeypatch, hypotheses):
    def unexpected_fit(*args, **kwargs):
        pytest.fail("invalid hypotheses must be rejected before fitting")

    monkeypatch.setattr(mechanism, "fit_hypothesis", unexpected_fit)
    with pytest.raises(ValueError):
        mechanism.discriminate([], [], 100, hypotheses=hypotheses)


@pytest.mark.parametrize(
    "shape,channels",
    [
        ((23, 2, 8, 8), None),
        ((25, 2, 8, 8), None),
        ((24, 8, 8), None),
        ((24, 0, 8, 8), None),
        ((24, 4, 8, 8), None),
        ((24, 2, 8, 8), ["coat", "membrane"]),
        ((24, 2, 8, 8), ["membrane", "membrane"]),
        ((24, 2, 8, 8), ["membrane", "coat", "actin"]),
    ],
)
def test_unsupported_movies_fail_before_perception(monkeypatch, shape, channels):
    def unexpected_extract(*args, **kwargs):
        pytest.fail("unsupported movies must be rejected before extraction")

    monkeypatch.setattr(
        analyze.perception.PerceptionProvider, "extract", unexpected_extract
    )
    with pytest.raises(ValueError):
        analyze.analyze(np.zeros(shape), channels=channels)


@pytest.mark.parametrize(
    "overrides",
    [
        {"H_obs": np.ones(25)},
        {"H_sigma": np.ones(23)},
        {"H_sigma": np.zeros(24)},
        {"H_sigma": np.full(24, np.nan)},
        {"H_obs": np.full(24, np.inf)},
        {"mask": np.zeros(24, bool)},
        {"mask": np.ones(23, bool)},
        {"actin_obs": np.ones(24)},
        {"actin_sigma": np.ones(24)},
        {"actin_obs": np.ones(23), "actin_sigma": np.ones(24)},
        {"actin_obs": np.ones(24), "actin_sigma": np.zeros(24)},
    ],
)
def test_invalid_observations_do_not_build_a_likelihood(overrides):
    inputs = dict(
        H_obs=np.ones(24),
        H_sigma=np.ones(24),
        params=inverse.DEFAULT_PARAMS,
        A_coat_nm2=100,
    )
    with pytest.raises(ValueError):
        inverse.make_loglike(**(inputs | overrides))


def test_failed_llm_falls_back_to_physics_search():
    class UnavailableHost:
        def reasoning_model(self):
            return "test-model"

        def llm(self, **kwargs):
            raise RuntimeError("offline")

    case = orchestrator.Case(
        "test",
        0.015,
        0.02,
        np.pi * 60**2,
        20,
        context={"amphipathic": True, "is_disordered": True},
    )
    records = orchestrator.search(
        case, host=UnavailableHost(), max_iter=1, verbose=False
    )
    assert len(records) == 1
    assert "offline fallback: RuntimeError" in records[0]["reasoning_trace"]
    assert np.isfinite(records[0]["evaluator_result"]["objective_value"])


def test_reasoning_trace_does_not_repeat_text_or_invent_a_coupling_rationale():
    proposal = dict(players=[], reasoning="model assumption", coupling_correction=-0.2)
    trace = orchestrator._compose_trace(proposal, "model assumption")
    assert trace.count("model assumption") == 1
    assert "coupling_correction=-0.2" in trace
    assert "synergy" not in trace


def test_refinement_preserves_original_proposal_and_improves_fit():
    case = orchestrator.Case(
        "test",
        0.015,
        0.02,
        np.pi * 60**2,
        20,
        context={"amphipathic": True, "is_disordered": True},
    )
    proposal = orchestrator._offline_proposer(case, [])
    original = copy.deepcopy(proposal)
    initial, *_ = orchestrator.evaluate_proposal(case, copy.deepcopy(proposal))
    refined, result, *_ = orchestrator.refine_magnitude(case, proposal)
    assert proposal == original
    assert refined is not proposal
    assert result.objective_value <= initial.objective_value


def test_structural_screen_rejects_changed_stage3_scores(tmp_path, monkeypatch):
    from mechanome import structural_screen

    for name in ("stage3_ranking.csv", "stage4_frozen_ranking.json"):
        source = (structural_screen._RESULTS / name).read_text(encoding="utf-8")
        if name == "stage3_ranking.csv":
            source = source.replace("78.31999969482422", "79.31999969482422")
        (tmp_path / name).write_text(source, encoding="utf-8")
    monkeypatch.setattr(structural_screen, "_RESULTS", tmp_path)
    verification = structural_screen.verify_frozen_ranking()
    assert verification["hash_from_frozen_csv"] == verification["stored_hash"]
    assert verification["passed"] is False
