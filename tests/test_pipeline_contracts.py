"""Fast branch coverage for the scientific decisions in the public pipelines."""

import copy

import numpy as np
import pytest

from curvo import analyze, inverse, mechanism, orchestrator


@pytest.mark.parametrize(
    "name,identified,expected_point",
    [
        ("active_force_max", True, 30.0),
        ("active_force_max", False, None),
        ("c_eff_max", True, None),
        ("sigma", True, None),
    ],
)
def test_point_estimates_require_both_credibility_gates(
    name, identified, expected_point
):
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
    force = analyze._report_forces(report)[name]
    assert force["point_estimate"] == expected_point
    assert force["ci95"] == [20.0, 40.0]
    assert report == original
    if expected_point is None:
        assert force["status"] == "underdetermined"
        assert force["reason"]


@pytest.mark.parametrize(
    "gap,extra_identified,decisive",
    [
        (4.0, True, True),
        (4.0, False, False),
        (1.0, True, False),
    ],
)
def test_evidence_win_requires_identifiable_extra_actor(
    monkeypatch, gap, extra_identified, decisive
):
    def fit(name, *args, **kwargs):
        return dict(
            name=name,
            free=mechanism.HYPOTHESES[name],
            logz=gap if name == "wedge+actin" else 0.0,
            logz_err=0.1,
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
