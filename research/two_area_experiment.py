"""Registered synthetic two-area identifiability checks for the cap limit.

This uses the analytic zero-line-tension curvature, clipped to the actual open
angular domain used by ``curvo.inverse._fast_H_trajectory``.  It deliberately
does not fit data or use a sampler: ranks are local analytic-Jacobian facts.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from curvo import inverse


ROOT = Path(__file__).resolve().parents[1]
RESULT = Path(__file__).with_name("two_area_results.json")
FIGURE = Path(__file__).with_name("two_area_comparison.png")
A0 = float(np.pi * 60.0**2)
AREAS = (A0, 2.0 * A0)
C0, SIGMA0, KAPPA0, RIG_FACTOR, T = 0.03, 0.02, 20.0, 3.0, 24
P0 = C0 * SIGMA0 * A0 / 2.0  # F/kBT, nm^-1; the single-A0 ridge value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coverage() -> np.ndarray:
    return np.asarray(inverse._coverage_ramp(T, 0.45, 0.12), dtype=float)


def bounds(area: float) -> tuple[float, float]:
    a = np.sqrt(area / np.pi)
    return 2.0 * np.sin(0.02 / 2.0) / a, 2.0 * np.sin((np.pi - 0.001) / 2.0) / a


def trajectory(area: float, C: float, P: float, sigma: float, scale: float = 1.0,
               varying_kappa: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Analytic H and source-domain clipped H; mask says derivative is interior."""
    u = coverage()
    q = 1.0 + (RIG_FACTOR - 1.0) * u if varying_kappa else np.ones_like(u)
    k = scale * KAPPA0 * q
    raw = u * (4.0 * np.pi * k * C + P) / (8.0 * np.pi * k + sigma * area)
    lo, hi = bounds(area)
    interior = (raw > lo) & (raw < hi)
    return np.clip(raw, lo, hi), interior


def _row(area: float, u: float, k: float, C: float, P: float, sigma: float,
         scale: float, names: tuple[str, ...], c_slot: int | None = None) -> np.ndarray:
    D, N = 8.0 * np.pi * k + sigma * area, 4.0 * np.pi * k * C + P
    values = {
        "C": u * 4.0 * np.pi * k / D,
        "P": u / D,
        "sigma": -u * N * area / D**2,
        "rho": u * area / D,
        "scale": u * (4.0 * np.pi * C * D - 8.0 * np.pi * N) * (k / scale) / D**2,
    }
    out = []
    for name in names:
        if name.startswith("C") and name != "C":
            out.append(values["C"] if name == f"C{c_slot}" else 0.0)
        else:
            out.append(values[name])
    return np.asarray(out)


def model_observations(kind: str, theta: np.ndarray, areas: tuple[float, ...], varying: bool):
    """Return clipped observations and analytic Jacobian prior to dimension scaling."""
    if kind == "shared":
        names, C, P, sigma, scale = ("C", "P", "sigma"), *theta, 1.0
    elif kind == "force_density":
        names, C, rho, sigma, scale = ("C", "rho", "sigma"), *theta, 1.0
    elif kind == "area_C":
        names, C1, C2, P, sigma, scale = ("C1", "C2", "P", "sigma"), *theta, 1.0
    elif kind == "unknown_scale":
        names, C, P, sigma, scale = ("C", "P", "sigma", "scale"), *theta
    else:
        raise ValueError(kind)
    u = coverage()
    q = 1.0 + (RIG_FACTOR - 1.0) * u if varying else np.ones_like(u)
    observations, rows, clipped = [], [], []
    for ai, area in enumerate(areas, start=1):
        ci = (C1, C2)[ai - 1] if kind == "area_C" else C
        pi = rho * area if kind == "force_density" else P
        h, interior = trajectory(area, ci, pi, sigma, scale, varying)
        for j, (uj, qj) in enumerate(zip(u, q)):
            observations.append(h[j])
            clipped.append(not bool(interior[j]))
            k = scale * KAPPA0 * qj
            # Clipped observations are locally constant under the analytic clip.
            rows.append(_row(area, uj, k, ci, pi, sigma, scale, names, ai) if interior[j]
                        else np.zeros(len(names)))
    return np.asarray(observations), np.asarray(rows), np.asarray(clipped), names


def scaled_jacobian(kind: str, theta: np.ndarray, areas: tuple[float, ...], varying: bool):
    h, J, clipped, names = model_observations(kind, theta, areas, varying)
    scales = {"C": C0, "P": P0, "sigma": SIGMA0, "rho": P0 / A0,
              "C1": C0, "C2": C0, "scale": 1.0}
    return h, J * np.asarray([scales[n] for n in names]), clipped, names, scales


def fd_check(kind: str, theta: np.ndarray, areas: tuple[float, ...], varying: bool) -> dict:
    h, Jscaled, clipped, names, scales = scaled_jacobian(kind, theta, areas, varying)
    # Finite differences use analytic H on strictly interior observations, never grid argmins.
    interior = ~clipped
    max_error = 0.0
    for col, name in enumerate(names):
        dz = 1e-6
        plus, minus = theta.copy(), theta.copy()
        plus[col] += dz * scales[name]
        minus[col] -= dz * scales[name]
        hp = model_observations(kind, plus, areas, varying)[0]
        hm = model_observations(kind, minus, areas, varying)[0]
        max_error = max(max_error, float(np.max(np.abs((hp[interior] - hm[interior]) / (2 * dz) - Jscaled[interior, col]))))
    return {"interior_rows": int(interior.sum()), "max_abs_scaled_derivative_error": max_error}


def rank_record(kind: str, label: str, theta: np.ndarray, areas: tuple[float, ...], varying: bool) -> dict:
    h, J, clipped, names, _ = scaled_jacobian(kind, theta, areas, varying)
    sv = np.linalg.svd(J, compute_uv=False)
    cutoff = (sv[0] * 1e-10) if sv.size and sv[0] else 1e-12
    return {
        "kind": kind, "label": label, "areas_nm2": list(areas), "varying_kappa": varying,
        "parameters": dict(zip(names, map(float, theta))), "dimensionless_parameter_scales": {
            "C_or_Ci_per_nm": C0, "P_per_nm": P0, "sigma_kBT_per_nm2": SIGMA0,
            "rho_per_nm3": P0 / A0, "rigidity_scale": 1.0},
        "singular_values": sv.tolist(), "svd_cutoff": float(cutoff), "rank": int((sv > cutoff).sum()),
        "n_clipped_rows": int(clipped.sum()), "n_interior_rows": int((~clipped).sum()),
        "fd_check": fd_check(kind, theta, areas, varying),
        "max_H_inv_nm": float(h.max()), "min_H_inv_nm": float(h.min()),
    }


def exact_symmetry_error(kind: str, theta: np.ndarray, transformed: np.ndarray) -> float:
    return float(max(np.max(np.abs(model_observations(kind, theta, AREAS, v)[0] -
                                   model_observations(kind, transformed, AREAS, v)[0]))
                     for v in (False, True)))


def make_figure(records: list[dict]) -> None:
    labels = [r["label"] for r in records if r["varying_kappa"] and len(r["areas_nm2"]) == 2]
    vals = [r["singular_values"] for r in records if r["varying_kappa"] and len(r["areas_nm2"]) == 2]
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    for i, (label, s) in enumerate(zip(labels, vals)):
        ax.semilogy(np.arange(len(s)) + i * 0.12, np.maximum(s, 1e-16), "o-", label=label)
    ax.axhline(1e-10, color="0.5", ls="--", lw=1, label="relative rank threshold scale")
    ax.set_xticks(range(4), ["1", "2", "3", "4"])
    ax.set_xlabel("dimensionless-Jacobian singular-value index")
    ax.set_ylabel("singular value")
    ax.set_title("Two known cap areas: which parameter-sharing assumptions retain a ridge?")
    ax.legend(fontsize=7, ncol=2)
    # Match the immutable JSON record: this attempt may not overwrite a figure.
    with FIGURE.open("xb") as handle:
        fig.savefig(handle, format="png", dpi=180)
    plt.close(fig)


def run() -> dict:
    generic = {
        "shared": np.array([C0, 1.25 * P0, SIGMA0]),
        "force_density": np.array([C0, 1.25 * P0 / A0, SIGMA0]),
        "area_C": np.array([C0, 0.042, 1.25 * P0, SIGMA0]),
        "unknown_scale": np.array([C0, 1.25 * P0, SIGMA0, 1.0]),
    }
    exceptional = {
        "shared": np.array([C0, P0, SIGMA0]),
        "force_density": np.array([C0, P0 / A0, SIGMA0]),
        # Each area lies on its own ridge: C_i A_i = 2P/sigma.
        "area_C": np.array([C0, C0 / 2.0, P0, SIGMA0]),
    }
    records = []
    for kind, theta in generic.items():
        for varying in (False, True):
            records.append(rank_record(kind, f"{kind}_generic", theta, (A0,), varying))
            records.append(rank_record(kind, f"{kind}_generic", theta, AREAS, varying))
    for kind, theta in exceptional.items():
        for varying in (False, True):
            records.append(rank_record(kind, f"{kind}_exceptional", theta, (A0,), varying))
            records.append(rank_record(kind, f"{kind}_exceptional", theta, AREAS, varying))
    symmetry = {
        "shared_single_area_ridge_only": {
            "transform": "at A0, C fixed; sigma->alpha*sigma; P->alpha*P where P=C*sigma*A0/2",
            "two_area_breaks_it": True,
            "max_two_area_difference_after_alpha_1p7": exact_symmetry_error("shared", exceptional["shared"], np.array([C0, 1.7 * P0, 1.7 * SIGMA0]))},
        "force_density_ridge": {
            "transform": "C fixed; sigma->alpha*sigma; rho->alpha*rho where rho=C*sigma/2",
            "max_difference_after_alpha_1p7": exact_symmetry_error("force_density", exceptional["force_density"], np.array([C0, 1.7 * P0 / A0, 1.7 * SIGMA0]))},
        "area_specific_C_ridge": {
            "transform": "Ci fixed; sigma->alpha*sigma; P->alpha*P when Ci*Ai=2P/sigma for both areas",
            "max_difference_after_alpha_1p7": exact_symmetry_error("area_C", exceptional["area_C"], np.array([C0, C0 / 2.0, 1.7 * P0, 1.7 * SIGMA0]))},
        "unknown_rigidity_scale": {
            "transform": "C fixed; (scale,P,sigma)->alpha*(scale,P,sigma)",
            "max_difference_after_alpha_1p7": exact_symmetry_error("unknown_scale", generic["unknown_scale"], np.array([C0, 1.7 * 1.25 * P0, 1.7 * SIGMA0, 1.7]))},
    }
    # Declared design-only noise sensitivities are omitted because every set has a structural null
    # direction in at least one required assumption, so no finite uncertainty is assigned to it.
    return {
        "task": "cap-two-area-numerical-001", "attempt": 1,
        "kind": "registered_synthetic_measurement_design", "registered_before_computation": True,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "design": {"A0_nm2": A0, "areas_nm2": list(AREAS), "C_per_nm": C0,
                   "sigma_kBT_per_nm2": SIGMA0, "P0_per_nm": P0,
                   "F0_pN": P0 * 4.114, "kappa0_kBT": KAPPA0, "rigidity_factor": RIG_FACTOR,
                   "T": T, "line_tension": 0.0, "no_empirical_calibration": True,
                   "clipping_domain": "psi in [0.02, pi-0.001], matching source grid endpoints"},
        "method": {"H": "clip_domain[u*(4*pi*kappa*C_i+P_i)/(8*pi*kappa+sigma*A_i)]",
                   "jacobian": "analytic derivative of H, zeroed only where analytic clip is saturated",
                   "finite_difference": "central differences of analytic clipped H on interior rows only; never grid argmin",
                   "rank_rule": "SVD of J_z, z_j=theta_j/declared_scale_j; s>1e-10*s_max",
                   "noise": "No noise sensitivity reported: structural null directions make pseudoinverse uncertainty invalid."},
        "records": records, "exact_symmetries": symmetry,
        "source_hashes_sha256": {"two_area_experiment.py": sha256(Path(__file__)),
                                  "research/cap_experiment.py": sha256(ROOT / "research/cap_experiment.py"),
                                  "curvo/inverse.py": sha256(ROOT / "curvo/inverse.py")},
        "environment": {"python": sys.version, "numpy": np.__version__, "matplotlib": plt.matplotlib.__version__, "platform": platform.platform()},
    }


if __name__ == "__main__":
    result = run()
    with RESULT.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    make_figure(result["records"])
    print(json.dumps({"written": str(RESULT), "records": len(result["records"])}))
