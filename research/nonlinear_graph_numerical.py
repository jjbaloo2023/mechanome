#!/usr/bin/env python3
"""Bounded realization of frozen nonlinear-numerical-001, attempt 1.

The program deliberately has no import-time work.  A run writes its state after
every solve and will refuse to start a fresh solve sequence if a results file
already records a started attempt.  Reanalysis from the saved PPoly coefficients
is intentionally left possible without calling ``solve_bvp``.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import i1, k1
from scipy.integrate import solve_bvp

HERE = Path(__file__).resolve().parent
DESIGN = HERE / "nonlinear_numerical_design.json"
EXECUTION = HERE / "nonlinear_numerical_execution_001.json"
RESULTS = HERE / "nonlinear_numerical_results_001.json"
PROFILES = HERE / "nonlinear_numerical_profiles_001.npz"
MAX_SOLVES = 26
SOURCE_POINTS = 4097


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bump(r):
    r = np.asarray(r)
    ans = np.zeros_like(r, dtype=float)
    inside = r < 1.0
    q = r[inside]
    ans[inside] = np.exp(1.0 - 1.0 / (1.0 - q * q))
    return ans


def c_over_r_prime(r, epsilon):
    r = np.asarray(r)
    ans = np.zeros_like(r, dtype=float)
    inside = r < 1.0
    q = r[inside]
    ans[inside] = -2.0 * epsilon * bump(q) / (1.0 - q * q) ** 2
    return ans


def source(r, epsilon):
    return epsilon * bump(r)


def config_label(kind, sigma, epsilon, radius, tol):
    e = "zero" if epsilon == 0 else f"e{epsilon:g}"
    return f"{kind}_s{sigma}_{e}_R{radius:g}_tol{tol:.0e}"


def bvp_solution(sigma, epsilon, radius, tol, initial=None):
    """One solver call.  The -3w/r singularity occurs only in S."""
    mesh = np.r_[np.linspace(0.0, 1.0, 121), np.linspace(1.0, radius, 241)[1:]]
    if initial is None:
        # Smooth zero-branch initial shape that honors v(R)=0 and w(0)=0.
        y = np.empty((2, mesh.size))
        y[0] = epsilon * np.exp(-mesh * mesh) * (1.0 - (mesh / radius) ** 2)
        y[1] = np.gradient(y[0], mesh)
        y[1, 0] = 0.0
    else:
        y = initial.sol(mesh)
        y[1, 0] = 0.0

    def fun(r, y):
        v, w = y
        c = source(r, epsilon)
        denom = 1.0 - (r * v) ** 2
        numerator = sigma * v - 0.5 * v * (2.0 * v + r * w - c) * (r * w + c)
        return np.vstack((w, c_over_r_prime(r, epsilon) + numerator / denom))

    def bc(ya, yb):
        return np.array([ya[1], yb[0]])

    return solve_bvp(fun, bc, mesh, y, tol=tol, max_nodes=20000,
                     S=np.array([[0.0, 0.0], [0.0, -3.0]]), verbose=0)


def bessel_a(r, sigma):
    """Independent infinite-domain a=u/epsilon reference (equation (5))."""
    lam = np.sqrt(sigma)
    # -phi' = 2 r phi/(1-r^2)^2.  Quad uses endpoints only as limiting zeros.
    def forcing(s):
        if s <= 0.0 or s >= 1.0:
            return 0.0
        return 2.0 * s * float(bump(np.array([s]))[0]) / (1.0 - s * s) ** 2
    def one(x):
        if x == 0.0:
            val = quad(lambda s: k1(lam * s) * forcing(s) * s, 0.0, 1.0,
                       epsabs=2e-12, epsrel=2e-12, limit=300)[0]
            return lam * val / 2.0
        lo = min(x, 1.0)
        first = quad(lambda s: i1(lam * s) * forcing(s) * s, 0.0, lo,
                     epsabs=2e-12, epsrel=2e-12, limit=300)[0]
        second = 0.0
        if x < 1.0:
            second = quad(lambda s: k1(lam * s) * forcing(s) * s, x, 1.0,
                          epsabs=2e-12, epsrel=2e-12, limit=300)[0]
        return k1(lam * x) * first + i1(lam * x) * second
    a = np.array([one(float(x)) for x in r])
    z = np.empty_like(a)
    z[0] = one(0.0)
    z[1:] = a[1:] / r[1:]
    return z


def ppoly_arrays(store, label, sol):
    # scipy PPoly evaluates sum(c[j,i]*dx**(3-j)); keeping c/x is lossless.
    store[f"{label}__x"] = sol.x.copy()
    store[f"{label}__c"] = sol.c.copy()


def exact_checks(sol, sigma, epsilon, radius):
    """Off-mesh checks use PPoly derivatives, never the ODE RHS."""
    near = np.geomspace(1e-10, 0.999999, 6000)
    exterior = np.linspace(1.0, radius, 6001)
    grid = np.unique(np.r_[0.0, near, exterior])
    v = sol(grid)[0]
    w_stored = sol(grid)[1]
    # Use derivatives of component 0.  The collocation representation of w is
    # stored too, but is not a substitute for off-mesh differentiation of v.
    w = sol(grid, 1)[0]
    v2 = sol(grid, 2)[0]
    c = source(grid, epsilon)
    cp_r = c_over_r_prime(grid, epsilon)
    u = grid * v
    up = v + grid * w
    t = 2.0 * v + grid * w - c
    tp = 3.0 * w + grid * v2 - grid * cp_r
    q = -(1.0-u*u)*tp - t*u*up + (0.5*t*t + sigma)*u
    # Analytic r->0 Q/r from the displayed formula and pole relation.
    c0 = epsilon
    v0 = float(sol(0.0)[0])
    vpp0 = float(sol(0.0, 2)[0])
    # q/r limit derived by Taylor expansion of the exact flux.
    t0 = 2*v0-c0
    q_over_r0 = (-4*vpp0 + float(c_over_r_prime(np.array([0.0]), epsilon)[0])
                  - t0*v0*v0 + (0.5*t0*t0+sigma)*v0)
    q_over_r = np.empty_like(q)
    q_over_r[0] = q_over_r0
    q_over_r[1:] = q[1:] / grid[1:]
    pole_relation = 4*vpp0 - (-2*epsilon + sigma*v0 - 0.5*v0*(2*v0-c0)*c0)
    return {
        "off_mesh_grid_count": int(grid.size),
        "off_mesh_grid": "0, 6000 geometric [1e-10,0.999999], 6001 uniform [1,R]",
        "max_abs_u": float(np.max(np.abs(u))),
        "boundary_vR": float(sol(radius)[0]),
        "boundary_w0": float(sol(0.0)[1]),
        "max_abs_spline_vprime_minus_stored_w": float(np.max(np.abs(w-w_stored))),
        "max_abs_Q": float(np.max(np.abs(q))),
        "max_abs_Q_over_r": float(np.max(np.abs(q_over_r))),
        "max_abs_Q_over_r_div_epsilon": (float(np.max(np.abs(q_over_r)) / epsilon)
                                          if epsilon else None),
        "pole_Q_over_r_limit": float(q_over_r0),
        "pole_relation_residual": float(pole_relation),
        "origin_v": v0,
        "origin_v_second": float(vpp0),
    }


def solve_record(state, profiles, kind, sigma, epsilon, radius, tol, initial=None):
    if len(state["solves"]) >= MAX_SOLVES:
        raise RuntimeError("26-solve ceiling reached before requested solve")
    label = config_label(kind, sigma, epsilon, radius, tol)
    record = {"index": len(state["solves"])+1, "label": label, "kind": kind,
              "sigma": sigma, "epsilon": epsilon, "R": radius, "tol": tol,
              "started_at_utc": utcnow(), "finished_at_utc": None, "outcome": "started"}
    state["solves"].append(record)
    save_state(state, profiles)
    sol = bvp_solution(sigma, epsilon, radius, tol, initial)
    record.update({"finished_at_utc": utcnow(), "outcome": "finished",
                   "solver_status": int(sol.status), "solver_message": sol.message,
                   "nodes": int(sol.x.size), "niter": int(sol.niter)})
    ppoly_arrays(profiles, label, sol)
    record["checks"] = exact_checks(sol, sigma, epsilon, radius)
    if sol.status != 0 or sol.x.size > 20000:
        record["outcome"] = "failed_stop"
        state["status"] = "failed_stop"
        save_state(state, profiles)
        raise RuntimeError(f"solver failure in {label}: {sol.message}")
    save_state(state, profiles)
    return label, sol


def save_state(state, profiles):
    state["updated_at_utc"] = utcnow()
    RESULTS.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    np.savez_compressed(PROFILES, **profiles)


def relative_change(a, b):
    return float(np.max(np.abs(a-b)) / max(float(np.max(np.abs(b))), 1e-12))


def finalize(state, profiles, solved):
    grid = np.linspace(0.0, 1.0, SOURCE_POINTS)
    state["comparisons"] = {"source_grid_count": SOURCE_POINTS, "source_grid": "uniform [0,1], includes endpoints"}
    nl = {}
    for eps in (0.025, 0.05, 0.1):
        for sigma in (1, 2):
            coarse = solved[config_label("nonlinear", sigma, eps, 8, 1e-6)].sol(grid)[0]
            fine8 = solved[config_label("nonlinear", sigma, eps, 8, 1e-8)].sol(grid)[0]
            fine12 = solved[config_label("nonlinear", sigma, eps, 12, 1e-8)].sol(grid)[0]
            nl[f"epsilon_{eps:g}_sigma_{sigma}"] = {
                "tolerance_relative_change_R8": relative_change(coarse, fine8),
                "reservoir_relative_change_R8_to_R12": relative_change(fine8, fine12),
                "absolute_profile_uncertainty_E": float(max(np.max(np.abs(coarse-fine8)), np.max(np.abs(fine8-fine12)))),
                "max_abs_v_R12": float(np.max(np.abs(fine12))),
            }
    state["comparisons"]["nonlinear"] = nl
    linear = {}
    for sigma in (1, 2):
        reference = bessel_a(grid, sigma)
        profiles[f"bessel_reference_sigma_{sigma}__source_grid"] = reference
        for radius, tol in ((8, 1e-6), (8, 1e-8), (12, 1e-8)):
            label = config_label("linear", sigma, 1.0, radius, tol)
            v = solved[label].sol(grid)[0]
            linear[label] = {"infinite_bessel_relative_max_error": relative_change(v, reference),
                             "infinite_bessel_absolute_max_error": float(np.max(np.abs(v-reference)))}
    state["comparisons"]["linear"] = linear
    ordering = {}
    for eps in (0.025, 0.05, 0.1):
        v1 = solved[config_label("nonlinear", 1, eps, 12, 1e-8)].sol(grid)[0]
        v2 = solved[config_label("nonlinear", 2, eps, 12, 1e-8)].sol(grid)[0]
        e1 = nl[f"epsilon_{eps:g}_sigma_1"]["absolute_profile_uncertainty_E"]
        e2 = nl[f"epsilon_{eps:g}_sigma_2"]["absolute_profile_uncertainty_E"]
        ordering[f"epsilon_{eps:g}"] = {"min_v2": float(np.min(v2)), "min_v1_minus_v2": float(np.min(v1-v2)),
                                           "threshold_v2": float(10*e2), "threshold_difference": float(10*(e1+e2)),
                                           "argmin_v2_r": float(grid[np.argmin(v2)]), "argmin_difference_r": float(grid[np.argmin(v1-v2)])}
    state["comparisons"]["ordering"] = ordering
    zero = {}
    for sigma in (1, 2):
        label = config_label("zero", sigma, 0.0, 8, 1e-8)
        sol = solved[label]
        z = sol.sol(np.linspace(0, 8, 8001))[0]
        zero[label] = {"max_abs_v": float(np.max(np.abs(z))), "max_abs_u": float(np.max(np.abs(np.linspace(0,8,8001)*z)))}
    state["comparisons"]["zero_source"] = zero
    # Gates are applied mechanically; compatibility K is only permissible if all pass.
    gates = {}
    fine_nl = [x for x in state["solves"] if x["kind"] == "nonlinear" and x["tol"] == 1e-8]
    gates["fine_status"] = all(x["solver_status"] == 0 for x in fine_nl)
    gates["graph_safety"] = all(x["checks"]["max_abs_u"] < 0.9 for x in fine_nl)
    gates["boundary"] = all(abs(x["checks"]["boundary_vR"]) < 1e-9 and abs(x["checks"]["boundary_w0"]) < 1e-9 for x in fine_nl)
    gates["Q_over_r"] = all(x["checks"]["max_abs_Q_over_r_div_epsilon"] < 1e-5 for x in fine_nl)
    gates["tolerance_refinement"] = all(x["tolerance_relative_change_R8"] < 5e-4 for x in nl.values())
    gates["reservoir_refinement"] = all(x["reservoir_relative_change_R8_to_R12"] < 1e-5 for x in nl.values())
    gates["linear_reference_R12_fine"] = all(linear[config_label("linear", s, 1.0, 12, 1e-8)]["infinite_bessel_relative_max_error"] < 1e-6 for s in (1,2))
    gates["zero_source"] = all(x["max_abs_u"] < 1e-10 for x in zero.values())
    gates["ordering"] = all(x["min_v2"] > x["threshold_v2"] and x["min_v1_minus_v2"] > x["threshold_difference"] for x in ordering.values())
    state["gates"] = gates
    state["optional_K_diagnostic"] = {"run": False, "reason": "suppressed because one or more required gates failed"} if not all(gates.values()) else {"run": False, "reason": "not implemented: this registered run reserves K only after gates; no extra solve is needed but diagnostic omitted"}
    state["status"] = "completed_gates_pass" if all(gates.values()) else "completed_gate_failed_optional_K_suppressed"
    state["completed_at_utc"] = utcnow()
    save_state(state, profiles)


def main():
    if RESULTS.exists():
        old = json.loads(RESULTS.read_text(encoding="utf-8"))
        if old.get("solves"):
            raise SystemExit("Results already contain a started attempt; refusing to duplicate BVP solves.")
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    state = {"task_id": design["task_id"], "attempt_number": 1, "status": "running",
             "started_at_utc": utcnow(), "max_total_solves": MAX_SOLVES,
             "provenance": {"design_sha256": sha256(DESIGN), "execution_sha256": sha256(EXECUTION),
                            "script_sha256": sha256(Path(__file__)), "python": sys.version,
                            "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()},
             "solves": []}
    profiles, solved = {}, {}
    # Fixed order: 18 nonlinear, then six independent linear controls, then two zero controls.
    for eps in (0.025, 0.05, 0.1):
        for sigma in (1, 2):
            prior = None
            for radius, tol in ((8, 1e-6), (8, 1e-8), (12, 1e-8)):
                label, sol = solve_record(state, profiles, "nonlinear", sigma, eps, radius, tol, prior)
                solved[label] = sol
                prior = sol
    for sigma in (1, 2):
        prior = None
        for radius, tol in ((8, 1e-6), (8, 1e-8), (12, 1e-8)):
            label, sol = solve_record(state, profiles, "linear", sigma, 1.0, radius, tol, prior)
            solved[label] = sol
            prior = sol
    for sigma in (1, 2):
        label, sol = solve_record(state, profiles, "zero", sigma, 0.0, 8, 1e-8)
        solved[label] = sol
    finalize(state, profiles, solved)


if __name__ == "__main__":
    main()
