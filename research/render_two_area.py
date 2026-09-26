"""Render the corrected relative-SVD figure from immutable two-area results."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "two_area_results.json"
OUTPUT = HERE / "two_area_comparison_v2.png"
DISPLAY_FLOOR = 1e-16


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    keep = [r for r in data["records"] if r["varying_kappa"] and len(r["areas_nm2"]) == 2]
    labels = {
        "shared_generic": "Shared C, P, sigma (generic)",
        "shared_exceptional": "Shared C, P, sigma (single-area ridge)",
        "force_density_generic": "Force proportional to area (generic)",
        "force_density_exceptional": "Force proportional to area (ridge)",
        "area_C_generic": "Area-specific C (generic)",
        "area_C_exceptional": "Area-specific C (simultaneous ridge)",
        "unknown_scale_generic": "Unknown rigidity scale",
    }
    fig, ax = plt.subplots(figsize=(9.4, 5.2), constrained_layout=True)
    for i, record in enumerate(keep):
        sv = np.asarray(record["singular_values"], dtype=float)
        relative = sv / sv[0]
        ax.semilogy(np.arange(1, len(sv) + 1) + i * 0.07,
                    np.maximum(relative, DISPLAY_FLOOR), "o-", label=labels[record["label"]])
    ax.axhline(1e-10, color="0.4", ls="--", lw=1, label="rank cutoff: relative sensitivity = 1e-10")
    ax.set_xticks([1, 2, 3, 4], ["1", "2", "3", "4"])
    ax.set_xlabel("dimensionless-Jacobian singular-value index")
    ax.set_ylabel("relative sensitivity: singular value / largest singular value")
    ax.set_title("Two known cap areas: remaining structural ridges by sharing assumption")
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.text(0.99, 0.02, "Values below 1e-16 are shown at a display floor.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
    with OUTPUT.open("xb") as handle:
        fig.savefig(handle, format="png", dpi=180)
    plt.close(fig)
    print(json.dumps({"output": str(OUTPUT), "created_utc": datetime.now(timezone.utc).isoformat(),
                      "input_sha256": sha256(INPUT), "renderer_sha256": sha256(Path(__file__))}))


if __name__ == "__main__":
    main()
