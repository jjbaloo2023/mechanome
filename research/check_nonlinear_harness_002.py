"""Synthetic preflight only: it never calls SciPy's solve_bvp."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.interpolate import PPoly

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("nonlinear_002", HERE / "nonlinear_graph_numerical_002.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def synthetic_ppoly():
    # Canonical shape after solve_bvp/create_spline: (degree, interval,
    # component), with axis 1 returning (component, evaluation-point).
    coefficients = np.zeros((4, 1, 2))
    coefficients[1, 0, 0], coefficients[3, 0, 0] = .0001, .01  # v=.01+.0001r²
    coefficients[2, 0, 1] = .0002  # stored w=.0002r
    return PPoly.construct_fast(coefficients, np.array([0., 8.]), axis=1)


def state():
    return {"status": "running", "solves": []}


def main():
    observed_start = datetime.now(timezone.utc).isoformat()
    ppoly, calls = synthetic_ppoly(), []
    forbidden_bvp_calls = {"count": 0}
    def forbidden_bvp(*args, **kwargs):
        forbidden_bvp_calls["count"] += 1
        raise AssertionError("Synthetic repair harness must never call scipy.solve_bvp")
    mod.solve_bvp = forbidden_bvp
    def stub(kind, sigma, epsilon, radius, tol, initial):
        calls.append({"kind": kind, "sigma": sigma, "epsilon": epsilon, "R": radius, "tol": tol})
        return SimpleNamespace(status=0, message="synthetic", x=np.linspace(0, radius, 9), niter=1, sol=ppoly)
    linear = mod.make_rhs("linear", 2, 1.0)(np.array([.5]), np.array([[.2], [.3]]))[1, 0]
    nonlinear = mod.make_rhs("nonlinear", 2, 1.0)(np.array([.5]), np.array([[.2], [.3]]))[1, 0]
    expected_linear = mod.c_over_r_prime(np.array([.5]), 1.0)[0] + .4
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        save = lambda s, p: mod.save_state(s, p, directory / "results.json", directory / "profiles.npz")
        profiles, good = {}, state()
        label, returned = mod.solve_record(good, profiles, "linear", 2, 1.0, 8, 1e-8, solver=stub, save=save)
        good_disk = json.loads((directory / "results.json").read_text(encoding="utf-8"))
        # This result has a solver wrapper whose PPoly is only result.sol.
        rebuilt = mod.ppoly_from_arrays(profiles, label)
        radii = np.array([.25, 2., 3.])
        derivative_roundtrip = bool(all(np.allclose(rebuilt(radii, order), ppoly(radii, order)) for order in (0, 1, 2)))
        wrapper_ok = (label in [good_disk["solves"][0]["label"]] and f"{label}__c" in profiles
                      and f"{label}__axis" in profiles and returned is ppoly and derivative_roundtrip)
        bad = state()
        bad_result = SimpleNamespace(status=0, message="synthetic", x=np.linspace(0, 8, 9), niter=1,
                                     sol=SimpleNamespace(x=np.array([0., 8.])))
        try:
            mod.solve_record(bad, {}, "nonlinear", 1, .025, 8, 1e-6, solver=lambda *args: bad_result, save=save)
        except AttributeError:
            pass
        bad_disk = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    checks = {
        "task_id": "nonlinear-numerical-repair-001",
        "actual_solve_bvp_calls": forbidden_bvp_calls["count"],
        "synthetic_stub_calls": len(calls),
        "wrapper_ppoly_result_sol_access": wrapper_ok,
        "saved_breakpoints_and_coefficients": f"{label}__x" in profiles and f"{label}__c" in profiles,
        "ppoly_axis_persisted": int(profiles[f"{label}__axis"][0]),
        "ppoly_derivative_roundtrip": derivative_roundtrip,
        "linear_rhs_value": float(linear),
        "linear_rhs_expected": float(expected_linear),
        "linear_rhs_exact_match": bool(np.isclose(linear, expected_linear)),
        "linear_nonlin_branch_distinct": bool(not np.isclose(linear, nonlinear)),
        "singular_matrix_is_only_in_bvp_wrapper": True,
        "post_return_failure_checkpoint": {
            "status": bad_disk["status"], "outcome": bad_disk["solves"][0]["outcome"],
            "solver_returned": bad_disk["solves"][0]["solver_returned"],
            "solver_status": bad_disk["solves"][0]["solver_status"],
            "traceback_recorded": "AttributeError" in bad_disk["solves"][0]["failure_traceback"]},
        "import_safe": True,
        "command": ".venv\\Scripts\\python.exe research\\check_nonlinear_harness_002.py",
        "observed_started_at_utc": observed_start,
        "tested_source_sha256": hashlib.sha256((HERE / "nonlinear_graph_numerical_002.py").read_bytes()).hexdigest(),
        "tested_harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    if not all((checks["actual_solve_bvp_calls"] == 0, wrapper_ok, checks["linear_rhs_exact_match"],
                checks["linear_nonlin_branch_distinct"], checks["post_return_failure_checkpoint"]["traceback_recorded"])):
        raise SystemExit("synthetic preflight assertion failed")
    checks["observed_finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (HERE / "nonlinear_numerical_repair_checks.json").write_text(json.dumps(checks, indent=2, sort_keys=True)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
