"""Review correction: compare depth from the same coat-edge plane.

Preserve the registered v1 numerical solution; add a derived observable and
versioned figure. Reservoir-to-tip depth remains a separate observable.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.special import iv, kv

from linear_patch_benchmark import predictions


def main():
    root = Path(__file__).resolve().parent
    input_path = root/"linear_patch_results.json"
    data = json.loads(input_path.read_text(encoding="utf-8"))
    for name, digest in data["source_hashes"].items():
        assert hashlib.sha256((root.parent/name).read_bytes()).hexdigest() == digest
    out, figure = root/"linear_patch_depth_v2.json", root/"linear_patch_comparison_v2.png"
    if out.exists() or figure.exists():
        raise FileExistsError("Review artifacts already exist; preserve them.")
    rows = []
    for row in data["records"]:
        x = row["x"]
        edge = float(x*kv(1, x)*(iv(0, x)-1))
        integral = quad(lambda t: x*kv(1, x)*iv(1, t), 0, x,
                        epsabs=1e-12, epsrel=1e-12)[0]
        assert abs(integral-edge) < 2e-14
        rows.append({"x": x, "membrane_edge_depth_normalized": edge,
            "cap_edge_depth_normalized": row["cap_depth_over_c_ell_squared"],
            "membrane_reservoir_depth_normalized": row["depth_over_c_ell_squared"],
            "slope_integral_abs_error": abs(integral-edge)})
    result = {"created_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": "cap-full-shape-benchmark-001", "attempt": 1,
        "review_revision": 2, "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "depth_normalization": "c*ell**2", "formula": "x*K1(x)*(I0(x)-1)",
        "scope": "derived observable, original linear model; no new nonlinear solve",
        "records": rows}
    with out.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    xs = np.geomspace(0.1, 10, 250)
    vals = [predictions(x) for x in xs]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), layout="constrained")
    for key, label in [("apex_H_over_c_half", "Membrane: apex"),
                       ("coat_mean_H_over_c_half", "Membrane: mean over coat"),
                       ("cap_H_over_c_half", "Spherical cap: uniform")]:
        axes[0].plot(xs, [v[key] for v in vals], label=label)
    axes[1].plot(xs, xs*kv(1, xs)*(iv(0, xs)-1), label="Membrane: edge to tip")
    axes[1].plot(xs, [v["cap_depth_over_c_ell_squared"] for v in vals], label="Cap: edge to tip")
    axes[1].plot(xs, [v["depth_over_c_ell_squared"] for v in vals], "--", color="0.4",
                 label="Membrane: reservoir to tip")
    axes[0].set(ylabel="Curvature / (c/2)", title="Local and coat-mean curvature differ")
    axes[1].set(ylabel="Depth / (c ell^2)", title="Depth depends on its reference plane")
    for ax in axes:
        ax.set(xscale="log", xlabel="Patch radius / tension length (R/ell)")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
    fig.suptitle("Force-free small-slope membrane benchmark; c ell = 0.01\n"
                 "Solid depth curves share the coat-edge reference", fontsize=11)
    fig.savefig(figure, dpi=160)
    plt.close(fig)
    print(json.dumps({"cases": len(rows), "max_integral_error": max(r["slope_integral_abs_error"] for r in rows)}))


if __name__ == "__main__":
    main()
