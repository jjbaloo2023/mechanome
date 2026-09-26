"""Independent discretization checks for the registered small-slope model."""
import numpy as np

from research.linear_patch_benchmark import CASES, finite_volume, interface_residuals, predictions


def test_radial_flux_solver_converges_to_infinite_membrane_solution():
    for x in CASES:
        target = predictions(x)["apex_H_over_c_half"]
        errors = [abs(finite_volume(x, n)[0]-target) for n in (40, 80, 160)]
        assert errors[2] < errors[1] < errors[0]
        assert errors[2] < 3e-5


def test_free_interface_matches_height_slope_and_moment():
    for x in CASES:
        residuals = interface_residuals(x)
        for key in ("height", "slope", "bending_moment"):
            assert abs(residuals[key]) < 2e-14


def test_geometry_observables_have_distinct_area_responses():
    rows = [predictions(x) for x in CASES]
    assert np.all(np.diff([r["apex_H_over_c_half"] for r in rows]) < 0)
    assert np.all(np.diff([r["depth_over_c_ell_squared"] for r in rows]) > 0)
    assert max(r["max_membrane_slope"] for r in rows) < 0.01
    assert predictions(10)["cap_H_over_c_half"] > 100*predictions(10)["apex_H_over_c_half"]
