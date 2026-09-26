import numpy as np

from research.cap_experiment import A, KBT, dynamic_exact, exact_lambda_zero, reduced_energy
from curvo.inverse import _coverage_ramp


def test_reduced_energy_matches_direct_formula_for_known_flat_limit():
    # At m=0, a flat patch has H=0, perimeter=2*sqrt(pi*A), no tension or work.
    energy = reduced_energy(0.0, A, kappa=20.0, lam=0.5, sigma=0.02, c0=0.03, force=10.0)
    expected = 20.0 * A * 0.03**2 / 2.0 + 0.5 * 2.0 * np.sqrt(np.pi * A)
    assert np.isclose(energy, expected)


def test_lambda_zero_stationary_solution_is_force_curvature_equivalent_at_fixed_rigidity():
    c0 = 0.04
    force = 4.0 * np.pi * 20.0 * KBT * c0
    c_only = exact_lambda_zero(c0, 0.0, 20.0, 0.02, A)
    f_only = exact_lambda_zero(0.0, force, 20.0, 0.02, A)
    assert np.isclose(c_only["H_inv_nm"], f_only["H_inv_nm"])


def test_dynamic_ridge_is_independent_of_rigidity_ramp():
    C, sigma = 0.03, 0.02
    force = KBT * C * sigma * A / 2.0
    h = dynamic_exact(sigma, C, force)
    assert np.allclose(h, C * _coverage_ramp(24, 0.45, 0.12) / 2.0)
