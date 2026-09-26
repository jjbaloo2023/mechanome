"""Exploratory grouped prediction; no molecular-mechanism inference or network."""

import hashlib
import io
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import nnls

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("constant_curvature", "constant_area", "flexible_reference")
POLICIES = ("corrected", "raw_nonnegative", "include_flagged")
KNOTS = np.array([0, 45, 90, 135, 180])


def design(theta, model):
    theta = np.asarray(theta, dtype=float)
    if not np.isfinite(theta).all() or np.any((theta < 0) | (theta > 180)):
        raise ValueError("Angles must be finite and within 0-180 degrees")
    if model == "constant_curvature":
        return np.ones((len(theta), 1))
    if model == "constant_area":
        # Equivalent to sqrt(2*pi*(1-cos(theta))), stable near flat sites.
        return (2 * np.sqrt(np.pi) * np.sin(np.deg2rad(theta) / 2))[:, None]
    if model == "flexible_reference":
        return np.maximum(1 - np.abs(theta[:, None] - KNOTS) / 45, 0)
    raise ValueError(f"Unknown model: {model}")


def fit(training, model):
    if training.empty or not np.isfinite(training.H).all() or (training.H < 0).any():
        raise ValueError("Training data must contain finite nonnegative curvature")
    counts = training.groupby("group").H.transform("size").to_numpy()
    weights = 1 / np.sqrt(counts)  # Equal total squared-error weight per group.
    matrix = design(training.angle, model)
    if np.linalg.matrix_rank(matrix) < matrix.shape[1]:
        raise ValueError("Training design is rank deficient; comparison unresolved")
    coefficients, _ = nnls(matrix * weights[:, None], training.H.to_numpy() * weights)
    return coefficients


def load_verified():
    audit = json.loads((ROOT / "research/data_audit.json").read_text())
    frames = []
    cache = (ROOT / "cache/smlm_locmofit/audit").resolve()
    for entry in audit["tables"]:
        path = (cache / entry["path"]).resolve()
        if not path.is_relative_to(cache):
            raise ValueError("Manifest path escapes cache")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Changed input: {entry['path']}")
        frame = pd.read_csv(io.BytesIO(content))
        frame["group"] = frame.cell_line + ":" + frame.file_number.astype(str)
        frame["source"] = entry["path"]
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    if data.duplicated(["group", "ID"]).any():
        raise ValueError("Duplicate site keys")
    negative = data.curvature < 0
    if not (
        (data.loc[negative, "curvature_corrected"] == 0).all()
        and (data.loc[negative, "theta_corrected"] == 0.0001).all()
        and (
            data.loc[~negative, "curvature"]
            == data.loc[~negative, "curvature_corrected"]
        ).all()
        and (
            data.loc[~negative, "theta"] == data.loc[~negative, "theta_corrected"]
        ).all()
    ):
        raise ValueError("Corrections differ from audited convention")
    flags = data.disconnected_sites.astype(str).str.lower()
    if not flags.isin(["true", "false"]).all():
        raise ValueError("Unknown exclusion flag")
    data["flagged"] = flags.eq("true")
    return data


def select(data, policy):
    if policy not in POLICIES:
        raise ValueError("Unknown filter policy")
    chosen = data.copy()
    if policy == "raw_nonnegative":
        chosen = chosen.loc[chosen.curvature >= 0].copy()
        chosen["angle"], chosen["H"] = chosen.theta, chosen.curvature
    else:
        chosen["angle"], chosen["H"] = (
            chosen.theta_corrected,
            chosen.curvature_corrected,
        )
    if policy != "include_flagged":
        chosen = chosen.loc[~chosen.flagged].copy()
    if set(chosen.group) != set(data.group):
        raise ValueError("Filtering removed a whole group")
    return chosen


def compare(data):
    folds = []
    for line, population in data.groupby("cell_line", sort=True):
        groups = sorted(population.group.unique())
        if len(groups) < 3:
            raise ValueError("At least three groups required")
        for held_out in groups:
            training = population.loc[population.group != held_out]
            test = population.loc[population.group == held_out]
            fold = {
                "cell_line": line,
                "held_out": held_out,
                "training_groups": sorted(training.group.unique()),
                "test_sites": len(test),
                "models": {},
            }
            for model in MODELS:
                coefficients = fit(training, model)
                residuals = np.abs(
                    design(test.angle, model) @ coefficients - test.H.to_numpy()
                )
                ranges = {}
                for lower, upper in ((0, 45), (45, 90), (90, 135), (135, 180)):
                    mask = (test.angle >= lower) & (
                        (test.angle < upper) if upper < 180 else (test.angle <= upper)
                    )
                    ranges[f"{lower}-{upper}"] = {
                        "n": int(mask.sum()),
                        "mae": float(residuals[mask].mean()) if mask.any() else None,
                    }
                fold["models"][model] = {
                    "coefficients": coefficients.tolist(),
                    "mae": float(residuals.mean()),
                    "angle_ranges": ranges,
                }
            fold["paired_mae_differences"] = {
                f"{model}_minus_flexible": fold["models"][model]["mae"]
                - fold["models"]["flexible_reference"]["mae"]
                for model in MODELS[:2]
            }
            folds.append(fold)
    summary = {}
    for line in sorted(data.cell_line.unique()):
        selected = [fold for fold in folds if fold["cell_line"] == line]
        summary[line] = {
            model: float(np.mean([f["models"][model]["mae"] for f in selected]))
            for model in MODELS
        }
    return {"summary_mae_inverse_nm": summary, "folds": folds}


def main():
    data = load_verified()
    output = {
        "status": "exploratory_unreviewed",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
        },
        "hashes": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in (
                "research/compare_geometry.py",
                "research/FIRST_COMPARISON.md",
                "research/data_audit.json",
            )
        },
        "runs": {},
    }
    for policy in POLICIES:
        chosen = select(data, policy)
        result = compare(chosen)
        result["counts_by_group"] = [
            {
                "group": group,
                "input": len(raw),
                "kept": int((chosen.group == group).sum()),
            }
            for group, raw in data.groupby("group")
        ]
        output["runs"][policy] = result
    (ROOT / "research/geometry_results.json").write_text(
        json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                policy: result["summary_mae_inverse_nm"]
                for policy, result in output["runs"].items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
