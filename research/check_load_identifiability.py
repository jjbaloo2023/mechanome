"""Check one preregistered curvature/load response matrix; no fitting or sweep.

Fourier convention: h(r) = integral k*J0(kr)*h_hat(k) dk / (2*pi).
The matrix uses columns C*a, F*a/kappa and rows a*H(0), [h(a)-h(0)]/a.
F multiplies equal/opposite normalized traction components, not net force.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import time

import numpy as np
from scipy.integrate import quad
from scipy.special import exp1, j0

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "research/load_identifiability_numerical_design.json"


def response_matrix(config, tolerance):
    """Two response columns in a calibrated, dimensionless convention."""
    a, b = config["a"], config["b"]
    kappa, sigma = config["kappa"], config["sigma"]
    q2 = sigma / kappa
    width_difference = (b*b-a*a)/2

    def height_transform(k, source):
        damping = math.exp(-a*a*k*k/2)
        if source == "curvature":
            return -2*math.pi*a*a*damping/(k*k+q2)
        # Stable continuation of (1-exp(-width_difference*k^2))/k^2 at zero.
        reaction = (width_difference if k == 0 else
                    -math.expm1(-width_difference*k*k)/(k*k))
        return damping*reaction/(kappa*(k*k+q2))

    def depth_factor(k):
        z = k*a
        if abs(z) < 1e-3:
            return -z*z/4 + z**4/64 - z**6/2304
        return j0(z)-1

    matrix = np.empty((2, 2))
    error = np.empty((2, 2))
    for column, source in enumerate(("curvature", "load")):
        curvature, curvature_error = quad(
            lambda k: -k**3*height_transform(k, source)/(4*math.pi),
            0, np.inf, epsabs=tolerance, epsrel=tolerance, limit=200)
        depth, depth_error = quad(
            lambda k: k*depth_factor(k)*height_transform(k, source)/(2*math.pi),
            0, np.inf, epsabs=tolerance, epsrel=tolerance, limit=200)
        # Convert physical unit C/F responses to the declared dimensionless axes.
        amplitude_factor = 1 if source == "curvature" else kappa
        matrix[:, column] = (amplitude_factor*curvature,
                             amplitude_factor*depth/(a*a))
        error[:, column] = (amplitude_factor*curvature_error,
                            amplitude_factor*depth_error/(a*a))
    return matrix, error


def determinant_error(matrix, error):
    """First-order absolute bound plus the two product-error terms."""
    a, b, c, d = matrix.ravel()
    ea, eb, ec, ed = error.ravel()
    return abs(d)*ea + abs(a)*ed + abs(c)*eb + abs(b)*ec + ea*ed + eb*ec


def main():
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    output = ROOT / design["output"]
    if output.exists():
        raise FileExistsError("Preserve prior results; register a new attempt.")
    deadline = datetime.fromisoformat(design["deadline_utc"].replace("Z", "+00:00"))
    started = datetime.now(timezone.utc)
    if started >= deadline:
        raise TimeoutError("Registered calculation deadline has elapsed.")
    clock_start = time.perf_counter()
    config = design["configuration"]
    matrix, error = response_matrix(config, design["quadrature"]["baseline_eps"])
    precise, precise_error = response_matrix(config, design["quadrature"]["precision_eps"])
    a, b, kappa, sigma = (config[k] for k in ("a", "b", "kappa", "sigma"))
    t_a, t_b = a*a*sigma/(2*kappa), b*b*sigma/(2*kappa)
    phi_a, phi_b = math.exp(t_a)*exp1(t_a), math.exp(t_b)*exp1(t_b)
    analytic_apex = np.array([0.5*(1-t_a*phi_a), -(phi_a-phi_b)/(8*math.pi)])
    balance, balance_error = quad(
        lambda r: r*(math.exp(-r*r/(2*a*a))/(a*a)
                    -math.exp(-r*r/(2*b*b))/(b*b)),
        0, np.inf, epsabs=1e-12, epsrel=1e-12, limit=200)
    det = float(np.linalg.det(precise))
    det_error = float(determinant_error(precise, precise_error))
    difference = float(np.max(np.abs(precise-matrix)))
    apex_error = float(np.max(np.abs(precise[0]-analytic_apex)))
    gates = {
        "force_balanced": abs(balance) < 1e-10,
        "analytic_apex_agreement": apex_error < 1e-10,
        "precision_agreement": difference < 1e-9,
        "resolved_summary_rank": abs(det) > max(1e-10, 100*det_error),
        "finished_before_deadline": datetime.now(timezone.utc) < deadline,
    }
    result = {
        "task_id": design["task_id"], "attempt_number": design["attempt_number"],
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.perf_counter()-clock_start,
        "configuration": config,
        "column_amplitudes": design["unknown_dimensionless_amplitudes"],
        "row_observables": design["dimensionless_observables"],
        "baseline_matrix": matrix.tolist(), "baseline_quad_errors": error.tolist(),
        "precision_matrix": precise.tolist(), "precision_quad_errors": precise_error.tolist(),
        "max_matrix_precision_difference": difference,
        "determinant": det, "determinant_quad_error_bound": det_error,
        "baseline_determinant": float(np.linalg.det(matrix)),
        "column_angle_sine": abs(det)/float(np.prod(np.linalg.norm(precise, axis=0))),
        "matrix_condition_number_2": float(np.linalg.cond(precise)),
        "conditioning_scope": "Declared dimensionless axes only; no observation-noise model or empirical precision.",
        "analytic_apex": analytic_apex.tolist(), "max_apex_crosscheck_error": apex_error,
        "unit_load_integral": balance, "unit_load_integral_quad_error": balance_error,
        "gates": gates, "all_gates_passed": all(gates.values()),
        "source_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (Path(__file__).resolve(), DESIGN,
                                    ROOT/"research/load_identifiability_design.json")},
        "limitations": design["no_claims"] + [
            "Full-profile rank is a separate analytic result; this checks only the declared two summaries.",
            "Quadrature error estimates are numerical diagnostics, not rigorous interval certificates.",
            "Templates, center, scales, tension and rigidity are prescribed; free fields retain the exact source ambiguity.",
            "Unit basis amplitudes are linear derivatives, not validated finite-slope physical states."],
    }
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({k: result[k] for k in (
        "precision_matrix", "determinant", "determinant_quad_error_bound",
        "column_angle_sine", "matrix_condition_number_2", "all_gates_passed", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
