"""Focused regression checks for the bounded passive axisymmetric benchmark."""
from __future__ import annotations

import json
from pathlib import Path

from research.axisymmetric_passive import bessel_reference, solve_case


ROOT = Path(__file__).resolve().parents[1]


def _case(x: float, amplitude: float = 0.01) -> dict:
    return {"label": "pytest", "x": x, "c_repo_ell": amplitude,
            "width_alpha": 0.01, "alpha_cutoff": 1e-6,
            "outer_radius": 14.0, "nodes": 401, "tol": 1e-5}


def test_shallow_material_bvp_matches_smooth_apex_and_force_balance() -> None:
    record = solve_case(_case(1.0))
    assert record["success"]
    assert record["max_rms_ode_residual"] < 1.1e-5
    assert record["relative_apex_error_vs_smooth_linear"] < 1e-4
    assert record["force_balance_Q_relative"] < 2e-5
    assert record["outer_bc_errors"]["lambda"] == 0.0


def test_apex_flattens_as_the_nominal_material_coat_grows() -> None:
    records = [solve_case(_case(x)) for x in (0.5, 1.0, 2.0)]
    values = [r["observables"]["apex_H_over_C_source"] for r in records]
    assert all(r["success"] for r in records)
    assert values[0] > values[1] > values[2]
    for x, record in zip((0.5, 1.0, 2.0), records):
        assert abs(record["observables"]["apex_H_over_C_source"]
                   - bessel_reference(x)["apex_H_over_C_source"]) < 2e-4


def test_refined_amplitude_record_shows_quadratic_normalized_limit() -> None:
    with (ROOT / "research/axisymmetric_amplitude_refinement.json").open(encoding="utf-8") as handle:
        records = json.load(handle)["records"]
    low, middle, high = records
    assert low["success"] and middle["success"]
    assert not high["success"]  # A preserved numerical failure, not a deleted case.
    ratio = middle["relative_apex_error_vs_smooth_linear"] / low["relative_apex_error_vs_smooth_linear"]
    assert 3.0 < ratio < 5.0
