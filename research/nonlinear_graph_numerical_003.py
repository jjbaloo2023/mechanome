#!/usr/bin/env python3
"""Mesh-refined implementation for queued numerical attempt 3.

This source is intentionally import-safe.  It is preflight-tested with a stub
solver only; actual BVP execution awaits a separate registration and review.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad, solve_bvp
from scipy.interpolate import PPoly
from scipy.special import i1, k1

HERE = Path(__file__).resolve().parent
DESIGN = HERE / "nonlinear_numerical_design.json"
EXECUTION = HERE / "nonlinear_numerical_execution_003.json"
RESULTS = HERE / "nonlinear_numerical_results_003.json"
PROFILES = HERE / "nonlinear_numerical_profiles_003.npz"
MESH_PLAN = HERE / "nonlinear_numerical_mesh_plan.json"
MAX_SOLVES, SOURCE_POINTS = 26, 4097
CONFIGS = ((8, 1e-6), (8, 1e-8), (12, 1e-8))


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bump(r):
    r = np.asarray(r)
    answer = np.zeros_like(r, dtype=float)
    mask = r < 1.0
    q = r[mask]
    answer[mask] = np.exp(1.0 - 1.0 / (1.0 - q*q))
    return answer


def c_over_r_prime(r, epsilon):
    r = np.asarray(r)
    answer = np.zeros_like(r, dtype=float)
    mask = r < 1.0
    q = r[mask]
    answer[mask] = -2.0 * epsilon * bump(q) / (1.0-q*q)**2
    return answer


def source(r, epsilon):
    return epsilon * bump(r)


def config_label(kind, sigma, epsilon, radius, tol):
    amp = "zero" if epsilon == 0 else f"e{epsilon:g}"
    return f"{kind}_s{sigma}_{amp}_R{radius:g}_tol{tol:.0e}"


def make_rhs(kind, sigma, epsilon):
    """Return only the nonsingular part; S carries -3w/r exactly once."""
    if kind == "linear":
        def linear_rhs(r, y):
            return np.vstack((y[1], c_over_r_prime(r, epsilon) + sigma*y[0]))
        return linear_rhs
    if kind not in ("nonlinear", "zero"):
        raise ValueError(f"unsupported solve kind {kind}")
    def nonlinear_rhs(r, y):
        v, w = y
        c = source(r, epsilon)
        denominator = 1.0 - (r*v)**2
        numerator = sigma*v - 0.5*v*(2*v+r*w-c)*(r*w+c)
        return np.vstack((w, c_over_r_prime(r, epsilon) + numerator/denominator))
    return nonlinear_rhs


def bvp_solution(kind, sigma, epsilon, radius, tol, initial=None):
    """One actual call only when the future registered main is invoked."""
    # Fixed reviewed mesh: 1921 source nodes plus 3840 exterior nodes.
    mesh = np.r_[np.linspace(0.0, 1.0, 1921), np.linspace(1.0, radius, 3841)[1:]]
    if initial is None:
        y = np.empty((2, mesh.size))
        y[0] = epsilon*np.exp(-mesh*mesh)*(1.0-(mesh/radius)**2)
        y[1] = np.gradient(y[0], mesh)
        y[1, 0] = 0.0
    else:
        y = initial(mesh)
        y[1, 0] = 0.0
    def bc(ya, yb):
        return np.array([ya[1], yb[0]])
    return solve_bvp(make_rhs(kind, sigma, epsilon), bc, mesh, y, tol=tol,
                     max_nodes=20000, S=np.array([[0., 0.], [0., -3.]]), verbose=0)


def save_state(state, profiles, results_path=RESULTS, profiles_path=PROFILES):
    state["updated_at_utc"] = utcnow()
    results_path.write_text(json.dumps(state, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    np.savez_compressed(profiles_path, **profiles)


def ppoly_arrays(profiles, label, ppoly):
    """Store lossless SciPy PPoly breakpoints and polynomial coefficients."""
    profiles[f"{label}__x"] = ppoly.x.copy()
    profiles[f"{label}__c"] = ppoly.c.copy()
    profiles[f"{label}__axis"] = np.array([ppoly.axis], dtype=int)


def ppoly_from_arrays(profiles, label):
    return PPoly.construct_fast(profiles[f"{label}__c"], profiles[f"{label}__x"],
                                axis=int(profiles[f"{label}__axis"][0]))


def residual_grid(ppoly, radius):
    """Original grid plus 17 interval points and both sides of every knot."""
    original = np.r_[0., np.geomspace(1e-10, .999999, 6000), np.linspace(1., radius, 6001)]
    knots = ppoly.x
    interiors = [np.linspace(left, right, 19)[1:-1] for left, right in zip(knots[:-1], knots[1:])]
    sides = np.r_[np.nextafter(knots[1:-1], -np.inf), np.nextafter(knots[1:-1], np.inf)]
    return np.unique(np.r_[original, *interiors, sides]), len(original), 17*(len(knots)-1), 2*(len(knots)-2)


def exact_checks(ppoly, sigma, epsilon, radius, nonlinear_q_applicable):
    """Physical flux from actual spline derivatives, never RHS substitution."""
    grid, original_count, interval_count, side_count = residual_grid(ppoly, radius)
    v = ppoly(grid)[0]
    stored_w = ppoly(grid)[1]
    vp, vpp = ppoly(grid, 1)[0], ppoly(grid, 2)[0]
    c, cp_r = source(grid, epsilon), c_over_r_prime(grid, epsilon)
    u, up = grid*v, v+grid*vp
    t, tp = 2*v+grid*vp-c, 3*vp+grid*vpp-grid*cp_r
    q = -(1-u*u)*tp - t*u*up + (.5*t*t+sigma)*u
    # Separate reconstruction through p and J; compare only off the pole to
    # avoid cancellation in the algebraically equivalent singular terms.
    J = 1.0/np.sqrt(1.0-u*u)
    p = u*J
    Jp = u*up*J**3
    q_original = -(tp*J+t*Jp)/J**3 + (.5*t*t+sigma)*p/J
    v0, vp0, w0, vpp0, c0 = float(ppoly(0.)[0]), float(ppoly(0., 1)[0]), float(ppoly(0.)[1]), float(ppoly(0., 2)[0]), epsilon
    # Exact equality is required: even a tiny interpolant pole slope cannot
    # use the finite regular-origin limit.
    pole_regular = vp0 == 0.0 and w0 == 0.0
    if pole_regular:
        t0 = 2*v0-c0
        q0 = -4*vpp0 - 2*epsilon - t0*v0*v0 + (.5*t0*t0+sigma)*v0
        q_over_r = np.r_[q0, q[1:]/grid[1:]]
    else:
        q0 = float("nan")
        q_over_r = np.r_[np.inf, q[1:]/grid[1:]]
    pole = 4*vpp0 - (-2*epsilon + sigma*v0 - .5*v0*(2*v0-c0)*c0)
    steps = np.diff(ppoly.x)
    source_steps, exterior_steps = steps[ppoly.x[:-1] < 1.], steps[ppoly.x[1:] > 1.]
    return {"residual_grid_count": int(grid.size), "original_residual_grid_count": original_count,
            "interval_interior_point_count": interval_count, "knot_side_point_count": side_count,
            "final_interval_count": int(steps.size), "max_source_interval_width": float(np.max(source_steps)),
            "max_exterior_interval_width": float(np.max(exterior_steps)), "nonlinear_Q_acceptance_applicable": nonlinear_q_applicable,
            "Q_metrics_interpretation": "nonlinear equilibrium acceptance" if nonlinear_q_applicable else "diagnostic only; not a linear/zero-control acceptance metric",
            "max_abs_u": float(np.max(abs(u))),
            "boundary_vR": float(ppoly(radius)[0]), "boundary_w0": w0,
            "actual_vprime0": vp0, "stored_w0": w0, "pole_regularity_exact_pass": pole_regular,
            "max_abs_spline_vprime_minus_stored_w": float(np.max(abs(vp-stored_w))),
            "max_abs_Q": float(np.max(abs(q))), "max_abs_Q_over_r": float(np.max(abs(q_over_r))),
            "max_abs_original_flux_minus_normalized_off_pole": float(np.max(abs(q_original[1:]-q[1:]))),
            "max_abs_Q_over_r_div_epsilon": None if epsilon == 0 else float(np.max(abs(q_over_r))/epsilon),
            "pole_Q_over_r_limit": float(q0), "pole_relation_residual": float(pole),
            "origin_v": v0, "origin_v_second": vpp0}


def solve_record(state, profiles, kind, sigma, epsilon, radius, tol, initial=None,
                 solver=bvp_solution, save=save_state):
    """Checkpoint start, solver return, and all post-return failures separately."""
    if len(state["solves"]) >= MAX_SOLVES:
        raise RuntimeError("26-solve ceiling reached")
    label = config_label(kind, sigma, epsilon, radius, tol)
    record = {"index": len(state["solves"])+1, "label": label, "kind": kind, "sigma": sigma,
              "epsilon": epsilon, "R": radius, "tol": tol, "started_at_utc": utcnow(),
              "finished_at_utc": None, "outcome": "started"}
    state["solves"].append(record)
    save(state, profiles)
    try:
        result = solver(kind, sigma, epsilon, radius, tol, initial)
    except Exception:
        record.update({"outcome": "solver_call_exception_stop", "failure_traceback": traceback.format_exc()})
        state["status"] = "failed_solver_call_exception"
        save(state, profiles)
        raise
    record.update({"outcome": "solver_returned", "solver_returned": True,
                   "solver_status": int(result.status), "solver_message": str(result.message),
                   "nodes": int(result.x.size), "niter": int(result.niter), "finished_at_utc": utcnow()})
    save(state, profiles)  # mandatory status checkpoint before PPoly/check work
    if result.status != 0 or result.x.size > 20000:
        record["outcome"] = "solver_status_failure_stop"
        state["status"] = "failed_solver_status"
        save(state, profiles)
        raise RuntimeError(f"solver failure in {label}: {result.message}")
    try:
        ppoly_arrays(profiles, label, result.sol)
        record["checks"] = exact_checks(result.sol, sigma, epsilon, radius, kind == "nonlinear")
        record["outcome"] = "completed"
        save(state, profiles)
    except Exception:
        record.update({"outcome": "postprocessing_failure_stop", "failure_traceback": traceback.format_exc()})
        state["status"] = "failed_postprocessing_after_solver_return"
        save(state, profiles)
        raise
    return label, result.sol


def relative_change(a, b):
    return float(np.max(abs(a-b))/max(float(np.max(abs(b))), 1e-12))


def k_is_allowed(gates):
    """K is available only after every required equilibrium gate passes."""
    return all(gates.values())


def bessel_a(r, sigma):
    lam = np.sqrt(sigma)
    def force(s):
        return 0.0 if s <= 0 or s >= 1 else 2*s*float(bump(np.array([s]))[0])/(1-s*s)**2
    def one(x):
        if x == 0:
            return lam/2*quad(lambda s: k1(lam*s)*force(s)*s, 0, 1, epsabs=2e-12, epsrel=2e-12, limit=300)[0]
        first = quad(lambda s: i1(lam*s)*force(s)*s, 0, min(x, 1), epsabs=2e-12, epsrel=2e-12, limit=300)[0]
        second = 0 if x >= 1 else quad(lambda s: k1(lam*s)*force(s)*s, x, 1, epsabs=2e-12, epsrel=2e-12, limit=300)[0]
        return k1(lam*x)*first+i1(lam*x)*second
    a = np.array([one(float(x)) for x in r])
    answer = np.empty_like(a); answer[0] = one(0.); answer[1:] = a[1:]/r[1:]
    return answer


def compatibility_k(profiles, epsilon, grid):
    """Exact K and finite-R linear K3, reconstructed from stored PPolys only."""
    v1 = ppoly_from_arrays(profiles, config_label("nonlinear", 1, epsilon, 12, 1e-8))(grid)[0]
    v2 = ppoly_from_arrays(profiles, config_label("nonlinear", 2, epsilon, 12, 1e-8))(grid)[0]
    u1, u2 = grid*v1, grid*v2
    g, gp = source(grid, epsilon), grid*c_over_r_prime(grid, epsilon)
    k = (u1-u2)*(-(u1+u2)*(g+grid*gp) + grid*(source(grid, epsilon)*g+.5*g*g))
    # U is the matching finite-R linear u, so this is the declared K3 formula.
    U1 = grid*ppoly_from_arrays(profiles, config_label("linear", 1, 1.0, 12, 1e-8))(grid)[0]
    U2 = grid*ppoly_from_arrays(profiles, config_label("linear", 2, 1.0, 12, 1e-8))(grid)[0]
    phi, phi_prime = bump(grid), grid*c_over_r_prime(grid, 1.0)
    k3 = (U1-U2)*(-(U1+U2)*(phi+grid*phi_prime)+1.5*grid*phi*phi)
    return k, k3


def finalize(state, profiles):
    grid = np.linspace(0., 1., SOURCE_POINTS)
    comparisons, nl, linear, ordering, zero = {"source_grid_count": SOURCE_POINTS}, {}, {}, {}, {}
    for eps in (.025, .05, .1):
        for sigma in (1, 2):
            co = ppoly_from_arrays(profiles, config_label("nonlinear", sigma, eps, 8, 1e-6))(grid)[0]
            f8 = ppoly_from_arrays(profiles, config_label("nonlinear", sigma, eps, 8, 1e-8))(grid)[0]
            f12 = ppoly_from_arrays(profiles, config_label("nonlinear", sigma, eps, 12, 1e-8))(grid)[0]
            nl[f"epsilon_{eps:g}_sigma_{sigma}"] = {"tolerance_relative_change_R8": relative_change(co, f8),
                "reservoir_relative_change_R8_to_R12": relative_change(f8, f12),
                "absolute_profile_uncertainty_E": float(max(np.max(abs(co-f8)), np.max(abs(f8-f12))))}
        v1 = ppoly_from_arrays(profiles, config_label("nonlinear", 1, eps, 12, 1e-8))(grid)[0]
        v2 = ppoly_from_arrays(profiles, config_label("nonlinear", 2, eps, 12, 1e-8))(grid)[0]
        e1, e2 = nl[f"epsilon_{eps:g}_sigma_1"]["absolute_profile_uncertainty_E"], nl[f"epsilon_{eps:g}_sigma_2"]["absolute_profile_uncertainty_E"]
        ordering[f"epsilon_{eps:g}"] = {"min_v2": float(np.min(v2)), "min_v1_minus_v2": float(np.min(v1-v2)),
            "threshold_v2": float(10*e2), "threshold_difference": float(10*(e1+e2))}
    for sigma in (1, 2):
        ref = bessel_a(grid, sigma); profiles[f"bessel_reference_sigma_{sigma}__source_grid"] = ref
        for radius, tol in CONFIGS:
            label = config_label("linear", sigma, 1.0, radius, tol)
            v = ppoly_from_arrays(profiles, label)(grid)[0]
            linear[label] = {"infinite_bessel_relative_max_error": relative_change(v, ref)}
        label = config_label("zero", sigma, 0., 8, 1e-8)
        r = np.linspace(0, 8, 8001); v = ppoly_from_arrays(profiles, label)(r)[0]
        zero[label] = {"max_abs_u": float(np.max(abs(r*v)))}
    comparisons.update({"nonlinear": nl, "linear": linear, "ordering": ordering, "zero_source": zero})
    fine = [x for x in state["solves"] if x["kind"] == "nonlinear" and x["tol"] == 1e-8]
    gates = {"fine_status": all(x["solver_status"] == 0 for x in fine),
        "graph_safety": all(x["checks"]["max_abs_u"] < .9 for x in fine),
        "boundary": all(abs(x["checks"]["boundary_vR"]) < 1e-9 and abs(x["checks"]["boundary_w0"]) < 1e-9 for x in fine),
        "pole_regularity": all(x["checks"]["pole_regularity_exact_pass"] for x in fine),
        "Q_over_r": all(x["checks"]["max_abs_Q_over_r_div_epsilon"] < 1e-5 for x in fine),
        "tolerance_refinement": all(x["tolerance_relative_change_R8"] < 5e-4 for x in nl.values()),
        "reservoir_refinement": all(x["reservoir_relative_change_R8_to_R12"] < 1e-5 for x in nl.values()),
        "linear_reference_fine_R8_and_R12": all(linear[config_label("linear", s, 1., r, 1e-8)]["infinite_bessel_relative_max_error"] < 1e-6 for s in (1, 2) for r in (8, 12)),
        "zero_source": all(x["max_abs_u"] < 1e-10 for x in zero.values()),
        "ordering": all(x["min_v2"] > x["threshold_v2"] and x["min_v1_minus_v2"] > x["threshold_difference"] for x in ordering.values())}
    state["comparisons"], state["gates"] = comparisons, gates
    if k_is_allowed(gates):
        kd = {}
        for eps in (.025, .05, .1):
            k, k3 = compatibility_k(profiles, eps, grid)
            profiles[f"K_e{eps:g}__source_grid"], profiles[f"K3_finite_R12_e{eps:g}__source_grid"] = k, k3
            kd[f"epsilon_{eps:g}"] = {"max_abs_K": float(np.max(abs(k))), "max_abs_K_over_epsilon_cubed": float(np.max(abs(k))/eps**3), "max_abs_finite_R12_K3": float(np.max(abs(k3)))}
        state["optional_K_diagnostic"] = {"run": True, "definition": "g=c; K3 uses matching R12 finite linear controls", "values": kd}
    else:
        state["optional_K_diagnostic"] = {"run": False, "reason": "suppressed because at least one required equilibrium gate failed"}
    state["status"], state["completed_at_utc"] = ("completed_gates_pass" if all(gates.values()) else "completed_gate_failed_optional_K_suppressed"), utcnow()
    save_state(state, profiles)


def main():
    """Reserved for a separately registered future execution; not run in repair stage."""
    if RESULTS.exists() and json.loads(RESULTS.read_text(encoding="utf-8")).get("solves"):
        raise SystemExit("Attempt 3 already started; refusing duplicate BVP calls.")
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    state = {"task_id": design["task_id"], "attempt_number": 3, "status": "running", "started_at_utc": utcnow(), "max_total_solves": MAX_SOLVES,
    "provenance": {"design_sha256": sha256(DESIGN), "mesh_plan_sha256": sha256(MESH_PLAN), "execution_sha256": sha256(EXECUTION), "script_sha256": sha256(Path(__file__)), "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()}, "solves": []}
    profiles, solved = {}, {}
    for eps in (.025, .05, .1):
        for sigma in (1, 2):
            prior = None
            for radius, tol in CONFIGS:
                label, prior = solve_record(state, profiles, "nonlinear", sigma, eps, radius, tol, prior); solved[label] = prior
    for sigma in (1, 2):
        prior = None
        for radius, tol in CONFIGS:
            label, prior = solve_record(state, profiles, "linear", sigma, 1., radius, tol, prior); solved[label] = prior
    for sigma in (1, 2):
        label, solved[config_label("zero", sigma, 0., 8, 1e-8)] = solve_record(state, profiles, "zero", sigma, 0., 8, 1e-8)
    finalize(state, profiles)


if __name__ == "__main__":
    main()
