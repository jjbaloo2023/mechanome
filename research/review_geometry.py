"""Adversarial and measurement-sensitivity checks; not independent peer review.

Run: python -m research.review_geometry. No network or model API is used.
"""

import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from research.compare_geometry import ROOT, compare, load_verified, select


def population_counterexample():
    """Every simulated pit has constant curvature, but sampling correlates size/age.

    Each pit grows through the same angle grid at its own fixed curvature. The
    sampled phase increases with that pit's curvature. This deliberately biased
    sampling is a possibility proof, not an inferred model of the real data.
    """
    angles = np.linspace(5, 175, 35)
    tracks = []
    snapshots = []
    for group in range(3):
        for pit, sampled_angle in enumerate(angles):
            curvature = 0.004 + 0.006 * sampled_angle / 180
            identity = f"cell{group}:pit{pit}"
            for angle in angles:
                tracks.append({"pit": identity, "angle": angle, "H": curvature})
            snapshots.append(
                {
                    "pit": identity,
                    "group": f"cell{group}",
                    "cell_line": "synthetic",
                    "angle": sampled_angle,
                    "H": curvature,
                }
            )
    tracks = pd.DataFrame(tracks)
    result = compare(pd.DataFrame(snapshots))
    return {
        "construction": "H constant per pit; snapshot phase correlated with pit curvature",
        "pit_count": int(tracks.pit.nunique()),
        "maximum_within_pit_curvature_range": float(
            tracks.groupby("pit").H.agg(lambda x: x.max() - x.min()).max()
        ),
        "comparison": result,
    }


def shifted_curvature(curvature, radius_shift_nm):
    """H'=1/(1/H+shift), stable at H=0; a sensitivity, not error calibration."""
    curvature = np.asarray(curvature, dtype=float)
    denominator = 1 + radius_shift_nm * curvature
    if (
        not np.isfinite(curvature).all()
        or (curvature < 0).any()
        or (denominator <= 0).any()
    ):
        raise ValueError("Nonphysical radius shift")
    return curvature / denominator


def main():
    data = select(load_verified(), "corrected")
    scenarios = {}
    for shift in (-10, 0, 10):
        for window in ("all_angles", "20_to_160_degrees"):
            selected = data.copy()
            if window != "all_angles":
                selected = selected.loc[selected.angle.between(20, 160)].copy()
            if set(selected.group) != set(data.group):
                raise ValueError("Sensitivity lost an entire group")
            selected["H"] = shifted_curvature(selected.H, shift)
            scenarios[f"radius_shift_{shift}nm_{window}"] = {
                "sites": len(selected),
                "result": compare(selected),
            }
    result = {
        "status": "self_audit_complete_independent_review_pending",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_interpretation": "Uniform radius shifts and endpoint removal are diagnostic assumptions, not calibrated errors or new independent data",
        "hashes": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in (
                "research/review_geometry.py",
                "research/compare_geometry.py",
                "research/data_audit.json",
                "research/REVIEW_PROTOCOL.md",
            )
        },
        "counterexample": population_counterexample(),
        "scenarios": scenarios,
    }
    (ROOT / "research/geometry_review.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "counterexample": result["counterexample"]["comparison"][
                    "summary_mae_inverse_nm"
                ],
                "sensitivity": {
                    name: s["result"]["summary_mae_inverse_nm"]
                    for name, s in scenarios.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
