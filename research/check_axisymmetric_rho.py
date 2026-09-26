"""Independent lead checks of attempt 2, without rerunning accepted BVP cases."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from research import axisymmetric_passive as previous
from research import axisymmetric_rho as current


ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / "research" / name).read_text(encoding="utf-8"))


def check():
    rng = np.random.default_rng(20260924)
    rho = np.geomspace(np.sqrt(2e-6), 14, 1000)
    # Arbitrary regular states, independent of the computed solutions.
    state = rng.normal(0, 0.02, (6, rho.size))
    state[0] = rho * rng.uniform(0.8, 1.2, rho.size)
    state[2] *= rho / 14
    state[5] += 0.5
    alpha = rho**2 / 2
    prior_rhs, _ = previous.make_system(0.01, 0.5, 0.01, 1e-6)
    old_derivative = prior_rhs(alpha, state, np.zeros(3))
    new_derivative = current.alpha_rhs(alpha, state, 0.01, 0.5, 0.01)
    rhs_error = float(np.max(np.abs(old_derivative - new_derivative)))
    assert rhs_error < 1e-12

    pole_errors = []
    for cutoff in (1e-6, 2.5e-7):
        for _ in range(20):
            parameters = np.array([rng.uniform(-0.03, 0.03), -0.01, 0.5])
            # Include a coat with nonzero derivative at the pole.
            old_pole = previous.pole_terms(cutoff, 0.01, 0.005, 0.01, parameters)
            new_pole = current.pole(np.sqrt(2 * cutoff), 0.01, 0.005, 0.01, parameters)
            pole_errors.append(float(np.max(np.abs(old_pole - new_pole))))
    assert max(pole_errors) < 1e-12

    prior_manifest = read_json("axisymmetric_rho_prior_manifest.json")
    unchanged = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
        for name, digest in prior_manifest["hashes"].items()
    }
    assert all(unchanged.values())

    result = read_json("axisymmetric_rho_results_002.json")
    hashes_match = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
        for name, digest in result["source_hashes"].items()
    }
    assert all(hashes_match.values())
    records = result["records"]
    prior_records = read_json("axisymmetric_amplitude_refinement.json")["records"]
    agreement = []
    for old, new in zip(prior_records[:2], records[:2]):
        errors = {name: abs(value - old["observables"][name])
                  for name, value in new["observables"].items()}
        assert max(errors.values()) <= 2e-6
        agreement.append(errors)
    sensitivity = {name: abs(value - records[2]["observables"][name])
                   for name, value in records[3]["observables"].items()}
    assert max(sensitivity.values()) <= 2e-6
    for record in records:
        assert record["success"] and record["status"] == 0
        assert record["max_rms_rho_ode_residual"] <= record["case"]["tol"] * 1.01
        assert max(record["outer_bc_errors"].values()) <= 1e-9
        assert record["pole_bc_max_abs_error"] <= 1e-9
        assert record["force_balance_Q_relative"] <= 1e-6
    return {
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent formula, preservation and stored-result checks; no BVP rerun.",
        "random_seed": 20260924,
        "alpha_rhs_max_absolute_error": rhs_error,
        "pole_series_max_absolute_error": max(pole_errors),
        "prior_artifacts_unchanged": unchanged,
        "result_hashes_match": hashes_match,
        "accepted_prior_observable_absolute_errors": agreement,
        "combined_mesh_cutoff_observable_absolute_errors": sensitivity,
        "preserved_prior_failure_status": prior_records[2]["status"],
        "all_registered_numerical_gates_passed": True,
    }


if __name__ == "__main__":
    output = check()
    destination = ROOT / "research" / "axisymmetric_rho_lead_checks.json"
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print(json.dumps(output, indent=2))
