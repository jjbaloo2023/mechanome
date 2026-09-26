"""Force-free small-slope membrane patch; not a nonlinear budding solver.

All lengths use ell=sqrt(kappa/sigma). y=h/(c*ell**2) solves
    y'' + y'/r - y = 1[r < x],  x=R/ell.
The finite-volume solve below is independent of the Bessel closed form.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.linalg import solve_banded
from scipy.special import iv, kv

ROOT = Path(__file__).resolve().parents[1]
CASES = (0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
RESOLUTIONS = (40, 80, 160)
AMPLITUDE = 0.01  # c*ell; synthetic, not an empirical value


def predictions(x: float) -> dict[str, float]:
    """Curvatures normalized by c/2; depths by c*ell**2."""
    apex = x * kv(1, x)
    return {
        "apex_H_over_c_half": float(apex),
        "coat_mean_H_over_c_half": float(2 * iv(1, x) * kv(1, x)),
        "depth_over_c_ell_squared": float(1 - apex),
        "cap_H_over_c_half": float(1 / (1 + x*x/8)),
        "cap_depth_over_c_ell_squared": float(x*x / (4 * (1+x*x/8))),
        "max_membrane_slope": float(AMPLITUDE*x*kv(1, x)*iv(1, x)),
        "cap_edge_slope_small_slope": float(AMPLITUDE*x / (2*(1+x*x/8))),
        "d_apex_normalized_dx": float(-x*kv(0, x)),
        "d_depth_normalized_dx": float(x*kv(0, x)),
    }


def finite_volume(x: float, cells_per_ell: int) -> tuple[float, float]:
    """Cell-centered radial flux balance, regular center, y(x+20)=0.

    The last ghost cell enforces zero at the outer face. The source is
    area-averaged over cells, including any cell cut by the patch boundary.
    """
    outer = x + 20
    count = int(round(outer*cells_per_ell))
    dr = outer/count
    faces = np.arange(count+1)*dr
    centers = (faces[:-1]+faces[1:])/2
    lower = faces[:-1]/(centers*dr*dr)
    upper = faces[1:]/(centers*dr*dr)
    diagonal = -lower-upper-1
    diagonal[-1] -= upper[-1]
    source = (np.minimum(faces[1:], x)**2 - np.minimum(faces[:-1], x)**2)
    source /= faces[1:]**2-faces[:-1]**2
    band = np.zeros((3, count))
    band[0, 1:] = upper[:-1]
    band[1] = diagonal
    band[2, :-1] = lower[1:]
    y = solve_banded((1, 1), band, source)
    # Regular-center extrapolation removes the r^2 term; retain both values.
    center_y = (9*y[0]-y[1])/8
    return float(1+center_y), float(-center_y)


def interface_residuals(x: float) -> dict[str, float]:
    a, b = x*kv(1, x), -x*iv(1, x)
    inside_y, outside_y = a*iv(0, x)-1, b*kv(0, x)
    inside_slope, outside_slope = a*iv(1, x), -b*kv(1, x)
    # m=Delta(y)-source=y on either side; generalized radial shear
    # d(Delta(y)-source)/dr-y'=0. No edge force or couple is applied.
    return {"height": float(inside_y-outside_y),
            "slope": float(inside_slope-outside_slope),
            "bending_moment": float(inside_y-outside_y),
            "generalized_shear": 0.0}


def run() -> dict:
    rows = []
    for x in CASES:
        exact = predictions(x)
        green = 1-quad(lambda t: t*kv(0, t), 0, x,
                       epsabs=1e-12, epsrel=1e-12)[0]
        refinement = []
        for n in RESOLUTIONS:
            apex, depth = finite_volume(x, n)
            refinement.append({"cells_per_ell": n, "apex_normalized": apex,
                "depth_normalized": depth,
                "apex_abs_error": abs(apex-exact["apex_H_over_c_half"])})
        rows.append({"x": x, **exact,
                     "green_integral_apex_abs_error": abs(green-exact["apex_H_over_c_half"]),
                     "interface_residuals": interface_residuals(x),
                     "finite_volume": refinement})
    paths = [Path(__file__), ROOT/"curvo/evaluator_tier0.py"]
    return {"task_id": "cap-full-shape-benchmark-001", "attempt": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": "linear, force-free circular curvature patch in infinite membrane",
        "design": {"x_R_over_ell": CASES, "c_times_ell": AMPLITUDE,
                   "cells_per_ell": RESOLUTIONS, "finite_outer_radius_over_ell": "x+20"},
        "source_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"):
                          hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "limitations": ["Projected patch area equals surface area only to leading order",
            "Uniform tension and rigidity; no force, pressure, line energy or stiffness jump",
            "Local apex and area-averaged curvature are distinct measurement functionals",
            "No neck, overhang, snap-through, biological calibration or nonlinear-paper reproduction",
            "Finite-volume outer-boundary truncation is separate from infinite-domain closed form",
            "Analytic shear residual is an identity, not an independent numerical check"],
        "records": rows}


def plot(data: dict, path: Path) -> None:
    xs = np.geomspace(0.1, 10, 250)
    values = [predictions(x) for x in xs]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    for key, label in [("apex_H_over_c_half", "Membrane: apex curvature"),
                       ("coat_mean_H_over_c_half", "Membrane: mean over coat"),
                       ("cap_H_over_c_half", "Spherical cap: uniform curvature")]:
        axes[0].plot(xs, [p[key] for p in values], label=label)
    for key, label in [("depth_over_c_ell_squared", "Membrane: depth below reservoir"),
                       ("cap_depth_over_c_ell_squared", "Spherical cap: depth below edge")]:
        axes[1].plot(xs, [p[key] for p in values], label=label)
    axes[0].set(ylabel="Curvature / (c/2)", title="Curvature decreases as the patch grows")
    axes[1].set(ylabel="Depth / (c ell^2)", title="Depth increases at the same time")
    for ax in axes:
        ax.set(xscale="log", xlabel="Patch radius / tension length (R/ell)")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
    fig.suptitle("Force-free small-slope benchmark; c ell = 0.01\n"
                 "Cap and surrounding-membrane geometry have different depth references", fontsize=11)
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    output = Path(__file__).with_name("linear_patch_results.json")
    figure = output.with_name("linear_patch_comparison.png")
    if output.exists() or figure.exists():
        raise FileExistsError("Preserve results; choose a new attempt before rerunning.")
    result = run()
    with output.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    plot(result, figure)
    print(json.dumps({"cases": len(result["records"]),
        "max_green_error": max(r["green_integral_apex_abs_error"] for r in result["records"]),
        "max_fine_grid_error": max(r["finite_volume"][-1]["apex_abs_error"] for r in result["records"]),
        "max_slope": max(r["max_membrane_slope"] for r in result["records"])}))
