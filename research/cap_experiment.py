"""Reproducible synthetic checks of the spherical-cap energy.

This is a model-conditional numerical audit, not a biological calibration.
It independently reduces ``curvo.evaluator_tier0._cap_energy`` using
``m = 1 - cos(psi)`` and records grid, analytic, and source-implementation
comparisons in an exclusive-create JSON result.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from curvo import evaluator_tier0 as ev
from curvo import inverse


ROOT = Path(__file__).resolve().parents[1]
# v1 is immutable after its exclusive-create run; this corrected rerun is v2.
RESULT = Path(__file__).with_name("cap_experiment_v2.json")
KBT = ev.kBT_zJ
A = float(np.pi * 60.0**2)  # nm^2; deliberately synthetic
GRID_SIZES = (400, 800, 1600)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduced_energy(m, A, kappa, lam, sigma, c0, force):
    """Independent m=1-cos(psi) form of _cap_energy, in kBT."""
    m = np.asarray(m)
    h = np.sqrt(2.0 * np.pi * m / A)
    perimeter = np.sqrt(2.0 * np.pi * A) * np.sqrt(2.0 - m)
    return (
        (kappa * A / 2.0) * (2.0 * h - c0) ** 2
        + lam * perimeter
        + sigma * A * m / 2.0
        - (force / KBT) * np.sqrt(A * m / (2.0 * np.pi))
    )


def exact_lambda_zero(c0, force, kappa, sigma, A):
    """Convex lambda=0 minimizer in y=sqrt(m), including endpoint clipping."""
    numerator = 2.0 * kappa * np.sqrt(2.0 * np.pi * A) * c0 + force * np.sqrt(A / (2.0 * np.pi)) / KBT
    denominator = 8.0 * np.pi * kappa + sigma * A
    y = float(np.clip(numerator / denominator, 0.0, np.sqrt(2.0)))
    m = y * y
    return {
        "m": m,
        "H_inv_nm": float(np.sqrt(2.0 * np.pi * m / A)),
        "second_derivative_y": float(denominator),
        "interior": bool(0.0 < y < np.sqrt(2.0)),
    }


def grid_minimum(case, n):
    # Deliberately retain the source's open endpoint convention for comparison.
    psi = np.linspace(0.02, np.pi - 0.001, n)
    m = 1.0 - np.cos(psi)
    energy = reduced_energy(m, A=A, **case)
    index = int(np.argmin(energy))
    return {
        "psi_rad": float(psi[index]),
        "m": float(m[index]),
        "H_inv_nm": float(np.sqrt(2.0 * np.pi * m[index] / A)),
        "energy_kBT": float(energy[index]),
        "edge_index": bool(index in (0, n - 1)),
    }


def source_energy_agreement():
    max_abs = 0.0
    for psi in np.linspace(0.02, np.pi - 0.001, 17):
        for case in (
            dict(kappa=20.0, lam=0.0, sigma=0.02, c0=0.03, force=12.0),
            dict(kappa=60.0, lam=1.0, sigma=0.05, c0=0.08, force=60.0),
        ):
            actual, _ = ev._cap_energy(psi, A, case["kappa"], case["lam"], case["sigma"], case["c0"], case["force"])
            m = 1.0 - np.cos(psi)
            max_abs = max(max_abs, abs(actual - reduced_energy(m, A=A, **case)))
    return float(max_abs)


def extrema_lambda_positive(case, n=20001):
    """Classify sampled extrema; this detects a real competing basin, if present."""
    m = np.linspace(0.0, 2.0 - 1e-8, n)
    energy = reduced_energy(m, A=A, **case)
    slopes = np.diff(energy)
    minima = np.where((slopes[:-1] < 0.0) & (slopes[1:] >= 0.0))[0] + 1
    maxima = np.where((slopes[:-1] > 0.0) & (slopes[1:] <= 0.0))[0] + 1
    return {
        "interior_minima_m": [float(m[i]) for i in minima],
        "interior_maxima_m": [float(m[i]) for i in maxima],
        "endpoint_energies_kBT": {"flat_m0": float(energy[0]), "closed_m2": float(energy[-1])},
    }


def coverage(T):
    return inverse._coverage_ramp(T, 0.45, 0.12)


def dynamic_exact(sigma, C, force, kappa=20.0, coat_rig=3.0, T=24, area=A):
    g = coverage(T)
    kappat = kappa * (1.0 + (coat_rig - 1.0) * g)
    H = g * (4.0 * np.pi * kappat * C + force / KBT) / (8.0 * np.pi * kappat + sigma * area)
    return H


def dynamic_grid(sigma, C, force, n, kappa=20.0, coat_rig=3.0, T=24):
    g = coverage(T)
    psi = np.linspace(0.02, np.pi - 0.001, n)
    m = 1.0 - np.cos(psi)
    H = np.sqrt(2.0 * np.pi * m / A)
    out = []
    for gi in g:
        case = dict(kappa=kappa * (1.0 + (coat_rig - 1.0) * gi), lam=0.0,
                    sigma=sigma, c0=C * gi, force=force * gi)
        out.append(float(H[int(np.argmin(reduced_energy(m, A=A, **case)))]))
    return np.asarray(out)


def source_domain_clip(H):
    """Clip a continuum minimum to the source's open angular grid endpoints."""
    m_lo = 1.0 - np.cos(0.02)
    m_hi = 1.0 - np.cos(np.pi - 0.001)
    return np.clip(H, np.sqrt(2.0 * np.pi * m_lo / A), np.sqrt(2.0 * np.pi * m_hi / A))


def fast_source_grid(sigma, C, force):
    return inverse._fast_H_trajectory(sigma, C, force, 20.0, 3.0, A, 24)


def run():
    cases = {
        "lambda0_interior": dict(kappa=20.0, lam=0.0, sigma=0.02, c0=0.03, force=0.0),
        "lambda0_c_only": dict(kappa=20.0, lam=0.0, sigma=0.02, c0=0.04, force=0.0),
        "lambda0_force_equivalent_at_constant_kappa": dict(
            kappa=20.0, lam=0.0, sigma=0.02, c0=0.0, force=float(4.0 * np.pi * 20.0 * KBT * 0.04)
        ),
        "lambda0_flat_endpoint": dict(kappa=20.0, lam=0.0, sigma=0.02, c0=0.0, force=0.0),
        "lambda_positive_competing_endpoints": dict(kappa=20.0, lam=1.0, sigma=0.02, c0=0.0, force=0.0),
        "lambda_positive": dict(kappa=20.0, lam=2.0, sigma=0.02, c0=0.03, force=0.0),
    }
    static = {}
    for name, case in cases.items():
        record = {"case": case, "grids": {str(n): grid_minimum(case, n) for n in GRID_SIZES}}
        if case["lam"] == 0.0:
            record["analytic"] = exact_lambda_zero(case["c0"], case["force"], case["kappa"], case["sigma"], A)
        else:
            record["landscape"] = extrema_lambda_positive(case)
        static[name] = record

    dynamic = {}
    source_ridge_trajectories = []
    grid400_ridge_trajectories = []
    C = 0.03
    for sigma in (0.005, 0.02, 0.04):
        ridge_force = float(KBT * C * sigma * A / 2.0)
        exact = dynamic_exact(sigma, C, ridge_force)
        source = fast_source_grid(sigma, C, ridge_force)
        grids = {str(n): dynamic_grid(sigma, C, ridge_force, n) for n in GRID_SIZES}
        clipped = source_domain_clip(exact)
        off = dynamic_exact(sigma, C, ridge_force * 1.25)
        source_ridge_trajectories.append(source)
        grid400_ridge_trajectories.append(grids["400"])
        dynamic[str(sigma)] = {
            "ridge_force_pN": ridge_force,
            "target_H_inv_nm": (C * coverage(24) / 2.0).tolist(),
            "max_exact_target_error": float(np.max(np.abs(exact - C * coverage(24) / 2.0))),
            "max_source400_exact_error": float(np.max(np.abs(source - exact))),
            "physical_boundary_bias_at_source_grid_floor": float(np.max(np.abs(clipped - exact))),
            "max_grid_errors_vs_clipped_exact": {key: float(np.max(np.abs(value - clipped))) for key, value in grids.items()},
            "max_grid_400_800_difference": float(np.max(np.abs(grids["400"] - grids["800"]))),
            "off_ridge_25pct_force_max_delta": float(np.max(np.abs(off - exact))),
            "all_interior_exact": bool(np.all((exact > 0.0) & (exact < np.sqrt(4.0 * np.pi / A)))),
            "exact_H_inv_nm": exact.tolist(), "source400_H_inv_nm": source.tolist(),
            "grid_H_inv_nm": {key: value.tolist() for key, value in grids.items()},
        }

    constant_tradeoff = {
        "force_equivalent_to_c0_0p04_pN": float(4.0 * np.pi * 20.0 * KBT * 0.04),
        "static_H_difference": abs(static["lambda0_c_only"]["analytic"]["H_inv_nm"] - static["lambda0_force_equivalent_at_constant_kappa"]["analytic"]["H_inv_nm"]),
        "dynamic_ramped_rigidity_H_difference": float(np.max(np.abs(
            dynamic_exact(0.02, 0.04, 0.0) - dynamic_exact(0.02, 0.0, 4.0 * np.pi * 20.0 * KBT * 0.04)
        ))),
    }
    area_falsification = {}
    for sigma in (0.005, 0.02, 0.04):
        ridge_force = KBT * C * sigma * A / 2.0
        area_falsification[str(sigma)] = {}
        for area in (A / 2.0, 2.0 * A):
            actual = dynamic_exact(sigma, C, ridge_force, area=area)
            g = coverage(24)
            kappat = 20.0 * (1.0 + 2.0 * g)
            predicted = g * (C / 2.0 + C * sigma * (A - area) / (2.0 * (8.0 * np.pi * kappat + sigma * area)))
            area_falsification[str(sigma)][str(area)] = {
                "max_formula_error": float(np.max(np.abs(actual - predicted))),
                "max_difference_from_reference_ridge": float(np.max(np.abs(actual - C * g / 2.0))),
            }

    return {
        "task": "cap-numerical-001", "attempt": 1,
        "kind": "synthetic_model_conditional", "created_utc": datetime.now(timezone.utc).isoformat(),
        "assumptions": {
            "A_nm2": A, "flat_radius_nm": 60.0, "declared_synthetic_domain":
                {"kappa_kBT": [20.0, 60.0], "sigma_kBT_per_nm2": [0.001, 0.05], "c0_per_nm": [0.0, 0.08], "force_pN": [0.0, 60.0]},
            "no_empirical_calibration": True, "line_tension_units": "kBT/nm",
        },
        "analytic_reduction": {
            "variable": "m=1-cos(psi), y=sqrt(m)",
            "energy": "kappa*A/2*(2*sqrt(2*pi*m/A)-c0)^2 + lambda*sqrt(2*pi*A)*sqrt(2-m) + sigma*A*m/2 - F/kBT*sqrt(A*m/(2*pi))",
            "lambda0_stationary_H": "H=(4*pi*kappa*c0+F/kBT)/(8*pi*kappa+sigma*A)",
            "dynamic_lambda0_stationary_H": "H(t)=g(t)*(4*pi*kappa(t)*C+Fmax/kBT)/(8*pi*kappa(t)+sigma*A)",
            "dynamic_ridge": "Fmax/kBT=C*sigma*A/2 implies H(t)=C*g(t)/2",
        },
        "checks": {"source_vs_independent_energy_max_abs_kBT": source_energy_agreement(), "static": static,
                   "dynamic_ridge": dynamic, "constant_rigidity_tradeoff": constant_tradeoff,
                   "max_pairwise_source400_ridge_spread": float(max(np.max(np.abs(a - b)) for i, a in enumerate(source_ridge_trajectories) for b in source_ridge_trajectories[i + 1:])),
                   "max_pairwise_grid400_ridge_spread": float(max(np.max(np.abs(a - b)) for i, a in enumerate(grid400_ridge_trajectories) for b in grid400_ridge_trajectories[i + 1:])),
                   "result_version": 2, "supersedes": "cap_experiment.json (immutable v1; corrected endpoint comparison)"},
        "area_falsification": {
            "assumption": "C, Fmax, and sigma are shared while area changes; this is a mathematical prediction, not a biological guarantee.",
            "reference_area_nm2": A,
            "formula": "H/u=C/2+C*sigma*(A0-A)/(2*(8*pi*kappa(t)+sigma*A))",
            "checks": area_falsification,
        },
        "source_hashes_sha256": {"cap_experiment.py": sha256(Path(__file__)), "curvo/evaluator_tier0.py": sha256(ROOT / "curvo/evaluator_tier0.py"), "curvo/inverse.py": sha256(ROOT / "curvo/inverse.py")},
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()},
    }


if __name__ == "__main__":
    result = run()
    # An exclusive create keeps this attempt immutable and prevents overwriting a baseline.
    with RESULT.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"written": str(RESULT), "source_energy_error": result["checks"]["source_vs_independent_energy_max_abs_kBT"]}))
