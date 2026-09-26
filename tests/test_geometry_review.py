import numpy as np
import pytest

from research.review_geometry import population_counterexample, shifted_curvature


def test_population_ranking_does_not_identify_single_pit_dynamics():
    result = population_counterexample()
    assert result["maximum_within_pit_curvature_range"] == 0
    errors = result["comparison"]["summary_mae_inverse_nm"]["synthetic"]
    assert errors["flexible_reference"] < 1e-14
    assert errors["constant_curvature"] > 0.001


def test_radius_sensitivity_keeps_flat_limit_and_units():
    assert shifted_curvature([0, 0.01], 10) == pytest.approx([0, 1 / 110])
    assert shifted_curvature([0, 0.01], -10) == pytest.approx([0, 1 / 90])
    assert np.isfinite(shifted_curvature([0], -10)).all()
    with pytest.raises(ValueError, match="Nonphysical"):
        shifted_curvature([0.1], -10)
