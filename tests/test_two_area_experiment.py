import numpy as np

from research import two_area_experiment as exp


def record(result, label, areas, varying):
    return next(r for r in result["records"] if r["label"] == label and r["areas_nm2"] == list(areas) and r["varying_kappa"] == varying)


def test_second_area_breaks_shared_single_area_special_ridge_with_known_rigidity():
    result = exp.run()
    one = record(result, "shared_exceptional", (exp.A0,), True)
    two = record(result, "shared_exceptional", exp.AREAS, True)
    assert one["rank"] == 2
    assert two["rank"] == 3
    assert result["exact_symmetries"]["shared_single_area_ridge_only"]["max_two_area_difference_after_alpha_1p7"] > 1e-5


def test_force_density_and_unknown_rigidity_have_exact_remaining_symmetries():
    result = exp.run()
    assert result["exact_symmetries"]["force_density_ridge"]["max_difference_after_alpha_1p7"] < 1e-12
    assert result["exact_symmetries"]["unknown_rigidity_scale"]["max_difference_after_alpha_1p7"] < 1e-12
    assert record(result, "force_density_exceptional", exp.AREAS, True)["rank"] == 2
    assert record(result, "unknown_scale_generic", exp.AREAS, True)["rank"] == 3


def test_analytic_jacobian_agrees_with_interior_finite_difference_and_clips_some_rows():
    result = exp.run()
    rows = [r for r in result["records"] if r["varying_kappa"]]
    assert all(r["fd_check"]["max_abs_scaled_derivative_error"] < 1e-8 for r in rows)
    assert any(r["n_clipped_rows"] > 0 for r in rows)
