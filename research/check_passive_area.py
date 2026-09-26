"""Audit saved passive membrane states without running a boundary-value solver."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicHermiteSpline

from research import axisymmetric_rho_frozen_002 as equations

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
RESULT = RESEARCH / "passive_area_results_001.json"
OUTPUT = RESEARCH / "passive_area_lead_checks.json"
NORMALIZED = (
    "apex_H_over_C_source", "coat_mean_H_over_C_source",
    "reservoir_depth_over_c_repo_ell", "edge_depth_over_c_repo_ell",
)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quadrature_nodes(mesh, endpoint, order=8):
    """Gauss nodes in every retained interval, clipping the last at the coat edge."""
    edges = np.r_[mesh[mesh < endpoint], endpoint]
    midpoints = (edges[:-1] + edges[1:]) / 2
    halfwidths = np.diff(edges) / 2
    abscissae, weights = np.polynomial.legendre.leggauss(order)
    points = midpoints[:, None] + halfwidths[:, None] * abscissae
    return points.ravel(), (halfwidths[:, None] * weights).ravel()


def audit_state(record):
    case = record["case"]
    path = ROOT / record["state_path"]
    assert file_hash(path) == record["state_sha256"]
    with np.load(path, allow_pickle=False) as saved:
        mesh, state, parameters = saved["rho"], saved["y"], saved["p"]
    assert np.all(np.diff(mesh) > 0)
    assert np.isfinite(state).all() and np.isfinite(parameters).all()
    amplitude = case["c_repo_ell"]
    curvature = amplitude / 2
    coat_edge = case["x"]
    coat_area = coat_edge**2 / 2
    cutoff = case["alpha_cutoff"]
    rhs, _ = equations.system(curvature, coat_area, case["width_alpha"], mesh[0])
    derivatives = rhs(mesh, state, parameters)
    shape = CubicHermiteSpline(mesh, state, derivatives, axis=1)
    points, weights = quadrature_nodes(mesh, coat_edge)
    sampled = shape(points)
    mean = (parameters[0] * cutoff + np.dot(weights, points * sampled[3])) / coat_area
    projected_integral = state[0, 0]**2 / 2 + np.dot(weights, points * np.cos(sampled[2]))
    edge = shape(coat_edge)
    projected_boundary = edge[0]**2 / 2
    pole_error = float(np.max(np.abs(state[:, 0] - equations.pole(
        mesh[0], curvature, coat_area, case["width_alpha"], parameters))))
    observables = {
        NORMALIZED[0]: float(parameters[0] / curvature),
        NORMALIZED[1]: float(mean / curvature),
        NORMALIZED[2]: float(-parameters[1] / amplitude),
        NORMALIZED[3]: float((edge[1] - parameters[1]) / amplitude),
    }
    differences = {name: abs(value - record["observables"][name])
                   for name, value in observables.items()}
    area_error = float(abs(projected_integral - projected_boundary) / coat_area)
    # This quadrature audit checks the same spline, not another physical solution.
    assert differences[NORMALIZED[1]] <= 2e-4
    assert max(differences[name] for name in (NORMALIZED[0], NORMALIZED[2], NORMALIZED[3])) < 1e-10
    assert area_error <= 1e-6
    assert pole_error <= 1e-9
    assert abs(projected_boundary - record["observables"]["projected_coat_area_over_2pi_ell2"]) < 1e-10
    probes = mesh[:-1] + .37 * np.diff(mesh)
    probe_state = shape(probes)
    defect = probe_state[0] / probes * (shape(probes, 1) - rhs(probes, probe_state, parameters))
    return {
        "label": case["label"], "state_sha256": record["state_sha256"],
        "reconstructed_observables": observables,
        "absolute_differences_from_stored_observables": differences,
        "pole_boundary_max_absolute_error": pole_error,
        "projected_area_identity_relative_error": area_error,
        "projected_area_from_quadrature": float(projected_integral),
        "projected_area_from_boundary": float(projected_boundary),
        "all_interval_arc_defect_component_max": np.max(np.abs(defect), axis=1).tolist(),
    }


def run():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    records = result["records"]
    all_records = records + [result["sensitivity"]]
    audited = [audit_state(record) for record in all_records]
    strongest = max(records, key=lambda record: record["observables"]["max_abs_psi_radians"])
    sensitivity = result["sensitivity"]
    sensitivity_error = abs(strongest["observables"][NORMALIZED[0]] - sensitivity["observables"][NORMALIZED[0]])
    margin = max(1e-5, 2 * sensitivity_error)
    sign = []
    for amplitude in (.02, .1, .3, .6):
        ordered = sorted((record for record in records if record["case"]["c_repo_ell"] == amplitude),
                         key=lambda record: record["case"]["x"])
        values = [record["observables"][NORMALIZED[0]] for record in ordered]
        differences = -np.diff(values)
        status = "preserved" if np.all(differences > margin) else ("reversed" if np.any(differences < -margin) else "unresolved")
        sign.append({"c_repo_ell": amplitude, "x": [record["case"]["x"] for record in ordered],
                     "apex_H_over_C_source": values, "adjacent_decreases": differences.tolist(),
                     "classification": status})
    report = {
        "task_id": "passive-area-sign-001", "attempt": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Hermite reconstruction and 8-point Gauss integration on every saved mesh interval; no BVP solves.",
        "source_sha256": file_hash(Path(__file__)), "result_sha256": file_hash(RESULT),
        "equations_sha256": file_hash(Path(equations.__file__)),
        "lead_design_sha256": file_hash(RESEARCH / "passive_area_lead_design.json"),
        "checks": audited, "sign_margin": margin, "sign_margin_is_not_a_confidence_interval": True,
        "sampled_ordering": sign,
        "limitations": ["Shared numerical solution, not independent physical evidence.",
                        "No proof of continuous branch tracking or global monotonicity.",
                        "Single combined mesh/cutoff check is not a global error bound."],
    }
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"states_checked": len(audited),
                      "max_mean_difference": max(row["absolute_differences_from_stored_observables"][NORMALIZED[1]] for row in audited),
                      "max_area_identity_error": max(row["projected_area_identity_relative_error"] for row in audited),
                      "max_pole_error": max(row["pole_boundary_max_absolute_error"] for row in audited),
                      "classifications": [row["classification"] for row in sign]}))


if __name__ == "__main__":
    run()
