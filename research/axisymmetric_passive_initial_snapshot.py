"""Bounded passive axisymmetric BVP benchmark in material-area coordinates.

This research-only calculation implements the homogeneous, force-free,
pressure-free supplement S40 system in dimensionless variables.  It is a
small-amplitude validation target, not a reproduction of a published nonlinear
continuation study.  The source convention is k_source=2*kappa_repo,
C_source=c_repo/2 and lambda=lambda_physical*ell**2/k_source.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.integrate import quad, solve_bvp
from scipy.special import iv, kv

ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = Path(__file__).with_name("axisymmetric_design.json")
RESULT_PATH = Path(__file__).with_name("axisymmetric_results_001.json")


def bessel_reference(x: float) -> dict[str, float]:
    apex = x * kv(1, x)
    return {
        "apex_H_over_C_source": float(apex),
        "coat_mean_H_over_C_source": float(2 * iv(1, x) * kv(1, x)),
        "reservoir_depth_over_c_repo_ell": float(1 - apex),
        "edge_depth_over_c_repo_ell": float(apex * (iv(0, x) - 1)),
    }


def smooth_linear_apex_reference(c_source: float, alpha_coat: float, width: float) -> float:
    """Linear smooth-coat apex H/C_source from the radial Green function."""
    def g(radius: float) -> float:
        return float(coat_profile(np.array([radius*radius/2]), 1.0, alpha_coat, width)[0][0])
    # The upper limit is safely beyond both the Bessel decay and the finite coat.
    g0 = g(0.0)
    integral = quad(lambda r: r*kv(0, r)*g(r), 0, 40, epsabs=2e-10, epsrel=2e-10)[0]
    return float(g0-integral)


def coat_profile(alpha: np.ndarray, c_source: float, alpha_coat: float,
                 width: float) -> tuple[np.ndarray, np.ndarray]:
    u = (alpha - alpha_coat) / width
    # Stable enough for this deliberately narrow finite range.
    th = np.tanh(u)
    C = 0.5 * c_source * (1 - th)
    Cdot = -0.5 * c_source * (1 - th * th) / width
    return C, Cdot


def pole_terms(alpha0: float, c_source: float, alpha_coat: float, width: float,
               parameters: np.ndarray) -> np.ndarray:
    """Regular S40 pole expansion from AXISYMMETRIC_THEORY.md."""
    h0, z0, lambda_p = parameters
    C0, Cdot0 = coat_profile(np.array([0.0]), c_source, alpha_coat, width)
    C0, Cdot0 = float(C0[0]), float(Cdot0[0])
    d0 = h0 - C0
    q0 = lambda_p - C0 * d0
    h2 = 0.5 * (Cdot0 + h0 * q0)
    rho = np.sqrt(2 * alpha0)
    r = rho - h0*h0*rho**3/8
    psi = h0*rho + (h2/2 + h0**3/24)*rho**3
    z = z0 + h0*rho**2/2 + h2*rho**4/8
    H = h0 + h2*rho**2
    L = 2*h0*q0*alpha0
    lam = lambda_p + 2*d0*Cdot0*alpha0
    return np.array([r, z, psi, H, L, lam])


def make_system(c_source: float, alpha_coat: float, width: float, alpha0: float):
    def fun(alpha: np.ndarray, y: np.ndarray, _p: np.ndarray) -> np.ndarray:
        r, _z, psi, H, L, lam = y
        C, Cdot = coat_profile(alpha, c_source, alpha_coat, width)
        sin_over_r = np.sin(psi) / r
        return np.vstack((
            np.cos(psi) / r,
            np.sin(psi) / r,
            (2*r*H - np.sin(psi)) / (r*r),
            (L + r*r*Cdot) / (r*r),
            2*H*((H-C)**2 + lam)
            - 2*(H-C)*(H*H + (H-sin_over_r)**2),
            2*(H-C)*Cdot,
        ))

    def bc(ya: np.ndarray, yb: np.ndarray, p: np.ndarray) -> np.ndarray:
        start = pole_terms(alpha0, c_source, alpha_coat, width, p)
        return np.r_[ya-start, yb[1], yb[2], yb[5]-0.5]
    return fun, bc


def initial_guess(alpha: np.ndarray, c_repo_ell: float, x: float) -> tuple[np.ndarray, np.ndarray]:
    """Shallow Bessel-shaped seed; it only initializes the nonlinear solve."""
    r = np.sqrt(2*alpha)
    csrc = c_repo_ell / 2
    inside = r <= x
    h = np.where(inside, csrc*x*kv(1, x)*iv(0, r),
                 -csrc*x*iv(1, x)*kv(0, r))
    z = np.where(inside, c_repo_ell*(x*kv(1, x)*iv(0, r)-1),
                 -c_repo_ell*x*iv(1, x)*kv(0, r))
    psi = np.where(inside, c_repo_ell*x*kv(1, x)*iv(1, r),
                   c_repo_ell*x*iv(1, x)*kv(1, r))
    y = np.vstack((r, z, psi, h, np.zeros_like(r), np.full_like(r, .5)))
    return y, np.array([h[0], z[0], .5])


def diagnostic_profile(sol, c_source: float, alpha_coat: float, width: float) -> dict:
    a = sol.x
    y = sol.y
    r, z, psi, H, L, lam = y
    C, _ = coat_profile(a, c_source, alpha_coat, width)
    algebraic = r*((H-C)*(H+C-np.sin(psi)/r)-lam)*np.sin(psi)
    invariant = algebraic + L*np.cos(psi)
    scale = max(float(np.max(np.abs(L))), float(np.max(np.abs(algebraic))), 1e-12)
    indexes = np.unique(np.linspace(0, len(a)-1, 9, dtype=int))
    return {
        "max_abs_force_balance_Q": float(np.max(np.abs(invariant))),
        "force_balance_scale": scale,
        "force_balance_Q_relative": float(np.max(np.abs(invariant))/scale),
        "sparse_profile": [{"alpha": float(a[i]), "r": float(r[i]), "z": float(z[i]),
                            "psi": float(psi[i]), "H": float(H[i]),
                            "L": float(L[i]), "lambda": float(lam[i]),
                            "C": float(C[i])} for i in indexes],
    }


def solve_case(case: dict) -> dict:
    x = float(case["x"])
    c_repo_ell = float(case["c_repo_ell"])
    width = float(case["width_alpha"])
    alpha0 = float(case["alpha_cutoff"])
    alpha_coat = x*x/2
    r_outer = float(case["outer_radius"])
    alpha_outer = r_outer*r_outer/2
    nodes = int(case["nodes"])
    alpha = np.linspace(alpha0, alpha_outer, nodes)
    guess, parameters = initial_guess(alpha, c_repo_ell, x)
    fun, bc = make_system(c_repo_ell/2, alpha_coat, width, alpha0)
    began = time.perf_counter()
    sol = solve_bvp(fun, bc, alpha, guess, p=parameters, tol=float(case["tol"]),
                    max_nodes=12000, verbose=0)
    elapsed = time.perf_counter() - began
    csrc = c_repo_ell/2
    profile = diagnostic_profile(sol, csrc, alpha_coat, width)
    sample_alpha = np.linspace(alpha0, alpha_coat, 1001)
    sample = sol.sol(sample_alpha)
    coat_integral = sol.p[0]*alpha0 + np.trapezoid(sample[3], sample_alpha)
    coat_mean = float(coat_integral / alpha_coat)
    edge_z = float(sol.sol(alpha_coat)[1])
    apex_z = float(sol.p[1])
    outer_y = sol.y[:, -1]
    initial_y = sol.y[:, 0]
    pole_expected = pole_terms(alpha0, csrc, alpha_coat, width, sol.p)
    reference = bessel_reference(x)
    smooth_apex = smooth_linear_apex_reference(csrc, alpha_coat, width)
    observables = {
        "apex_H_over_C_source": float(sol.p[0]/csrc),
        "coat_mean_H_over_C_source": coat_mean/csrc,
        "reservoir_depth_over_c_repo_ell": -apex_z/c_repo_ell,
        "edge_depth_over_c_repo_ell": (edge_z-apex_z)/c_repo_ell,
    }
    return {
        "case": case,
        "status": int(sol.status), "message": str(sol.message), "success": bool(sol.success),
        "runtime_seconds": elapsed, "iterations": int(sol.niter), "nodes_final": int(sol.x.size),
        "max_rms_ode_residual": float(np.max(sol.rms_residuals)),
        "outer_bc_errors": {"z": float(abs(outer_y[1])), "psi": float(abs(outer_y[2])),
                            "lambda": float(abs(outer_y[5]-.5))},
        "pole_expansion_max_abs_error": float(np.max(np.abs(initial_y-pole_expected))),
        "observables": observables, "bessel_reference": reference,
        "smooth_linear_reference": {"apex_H_over_C_source": smooth_apex},
        "relative_errors_vs_bessel": {k: float(abs(observables[k]-reference[k])/max(abs(reference[k]), 1e-12))
                                       for k in reference},
        "relative_apex_error_vs_smooth_linear": float(abs(observables["apex_H_over_C_source"]-smooth_apex)
                                                     / max(abs(smooth_apex), 1e-12)),
        "max_abs_force_balance_Q": profile["max_abs_force_balance_Q"],
        "force_balance_scale": profile["force_balance_scale"],
        "force_balance_Q_relative": profile["force_balance_Q_relative"],
        "sparse_profile": profile["sparse_profile"],
    }


def cases() -> list[dict]:
    base = {"c_repo_ell": .01, "width_alpha": .01, "alpha_cutoff": 1e-6,
            "outer_radius": 14., "nodes": 401, "tol": 1e-5}
    records = [{"label": f"baseline_x{x:g}", "x": x, **base} for x in (.5, 1., 2.)]
    records += [
        {"label": "amplitude_low_x1", "x": 1., **{**base, "c_repo_ell": .005}},
        {"label": "amplitude_high_x1", "x": 1., **{**base, "c_repo_ell": .02}},
        {"label": "mesh_tol_refined_x1", "x": 1., **{**base, "nodes": 801, "tol": 3e-6}},
        {"label": "smooth_wide_x1", "x": 1., **{**base, "width_alpha": .02}},
        {"label": "smooth_narrow_x1", "x": 1., **{**base, "width_alpha": .005}},
        {"label": "axis_cutoff_small_x1", "x": 1., **{**base, "alpha_cutoff": 2.5e-7}},
        {"label": "domain_extended_x1", "x": 1., **{**base, "outer_radius": 20.}},
    ]
    return records


def source_hashes() -> dict[str, str]:
    paths = [Path(__file__), DESIGN_PATH, ROOT/"research/linear_patch_benchmark.py",
             ROOT/"research/AXISYMMETRIC_THEORY.md"]
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.exists()}


def run() -> dict:
    records = []
    for case in cases():
        try:
            records.append(solve_case(case))
        except Exception as exc:  # Failed cases are data, not silently discarded.
            records.append({"case": case, "success": False, "status": "exception",
                            "message": repr(exc)})
    return {
        "task_id": "axisymmetric-passive-numerical-001", "attempt": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_scope": "Passive homogeneous nonlinear material-area BVP; p=f=0.",
        "equation_convention": "Supplement S40 plus tension-gradient sign; main Eq. 3 conflict remains documented.",
        "source_hashes": source_hashes(), "python": sys.version,
        "records": records,
    }


if __name__ == "__main__":
    if RESULT_PATH.exists():
        raise FileExistsError(f"Preserve prior result: {RESULT_PATH}")
    result = run()
    with RESULT_PATH.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"cases": len(result["records"]),
                      "successful": sum(bool(r.get("success")) for r in result["records"])}))
