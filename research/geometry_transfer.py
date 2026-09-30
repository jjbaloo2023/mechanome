"""Frozen leave-one-cell-line-out geometry-transfer calculation.

This script is deliberately a bounded descriptive calculation.  ``--checks``
uses at most six synthetic NNLS calls; ``--run`` reserves and performs the one
27-call empirical grid.  Both operations are lead-owned by the registered plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import nnls

from compare_geometry import KNOTS, MODELS, POLICIES, design, load_verified, select


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
DESIGN_PATH = RESEARCH / "geometry_transfer_design.json"
LEDGER_PATH = RESEARCH / "geometry_transfer_execution.json"
CHECKS_PATH = RESEARCH / "geometry_transfer_checks_001.json"
RESULTS_PATH = RESEARCH / "geometry_transfer_results_001.json"
EMPIRICAL_CAP = 27
SYNTHETIC_CAP = 6


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    names = (
        "research/geometry_transfer.py", "research/geometry_transfer_design.json",
        "research/compare_geometry.py", "research/FIRST_COMPARISON.md",
        "research/geometry_inputs.lock.json", "research/data_audit.json",
        "research/geometry_results_v2.json",
    )
    return {name: sha256(ROOT / name) for name in names}


def load_design_and_verify() -> dict:
    design_document = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    for name, expected in design_document["input_sha256"].items():
        actual = sha256(ROOT / name)
        if actual != expected:
            raise ValueError(f"Frozen input hash changed for {name}: {actual} != {expected}")
    if tuple(design_document["fixed_analysis"]["policies"]) != POLICIES:
        raise ValueError("Policy set differs from registered design")
    if tuple(design_document["fixed_analysis"]["models"]) != MODELS:
        raise ValueError("Model set differs from registered design")
    if tuple(design_document["fixed_analysis"]["flexible_knots_degrees"]) != tuple(KNOTS):
        raise ValueError("Flexible-reference knots differ from registered design")
    return design_document


def load_ledger() -> dict:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    required = {"task_id", "attempt_number", "empirical_fit_cap", "synthetic_fit_cap", "fits", "invocations"}
    if not required.issubset(ledger):
        raise ValueError("Execution ledger is incomplete")
    if ledger["empirical_fit_cap"] != EMPIRICAL_CAP or ledger["synthetic_fit_cap"] != SYNTHETIC_CAP:
        raise ValueError("Execution ledger cap differs from registered design")
    return ledger


def verify_ledger_identity(ledger: dict, design_document: dict) -> None:
    if ledger["task_id"] != design_document["task_id"] or ledger["attempt_number"] != design_document["attempt_number"]:
        raise ValueError("Execution ledger task identity differs from registered design")


def save_ledger(ledger: dict) -> None:
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def reserve_invocation(ledger: dict, kind: str, output_path: Path) -> dict:
    if any(row["kind"] == kind for row in ledger["invocations"]):
        raise RuntimeError(f"{kind} invocation already reserved or completed; rerun refused")
    if output_path.exists():
        raise FileExistsError(f"Immutable output already exists: {output_path}")
    record = {"id": f"{kind}-001", "kind": kind, "status": "reserved", "reserved_at_utc": utc_now(),
              "output": str(output_path.relative_to(ROOT)), "source_hashes": source_hashes(), "fit_ids": []}
    ledger["invocations"].append(record)
    save_ledger(ledger)
    return record


def reserve_nnls(ledger: dict, invocation: dict, kind: str, context: dict) -> dict:
    cap = EMPIRICAL_CAP if kind == "empirical" else SYNTHETIC_CAP
    used = sum(row["kind"] == kind for row in ledger["fits"])
    if used >= cap:
        raise RuntimeError(f"{kind} NNLS cap {cap} reached before requested call")
    record = {"id": f"{kind}-fit-{used + 1:02d}", "kind": kind, "status": "reserved",
              "reserved_at_utc": utc_now(), "invocation_id": invocation["id"], "context": context}
    ledger["fits"].append(record)
    invocation["fit_ids"].append(record["id"])
    save_ledger(ledger)
    return record


def complete_nnls(ledger: dict, record: dict, coefficients: np.ndarray | None, error: Exception | None = None) -> None:
    record["completed_at_utc"] = utc_now()
    if error is None:
        record["status"] = "completed"
        record["coefficients"] = [float(x) for x in coefficients]
    else:
        record["status"] = "failed"
        record["error"] = f"{type(error).__name__}: {error}"
    save_ledger(ledger)


def weighted_training_rows(training: pd.DataFrame) -> tuple[np.ndarray, list[dict]]:
    """Return sqrt row weights; squared weights equalize lines, then groups."""
    lines = sorted(training.cell_line.unique())
    if not lines:
        raise ValueError("No training cell lines")
    n_lines = len(lines)
    squared = np.empty(len(training), dtype=float)
    rows = []
    for line in lines:
        in_line = training.loc[training.cell_line == line]
        groups = sorted(in_line.group.unique())
        if not groups:
            raise ValueError(f"Training line {line} has no groups")
        for group in groups:
            index = in_line.index[in_line.group == group]
            if not len(index):
                raise ValueError(f"Training group {group} is empty")
            value = 1.0 / (n_lines * len(groups) * len(index))
            squared[training.index.get_indexer(index)] = value
            rows.append({"cell_line": line, "group": group, "n_rows": int(len(index)),
                         "squared_weight_per_row": value, "squared_weight_group_total": 1.0 / (n_lines * len(groups))})
    if not np.isclose(squared.sum(), 1.0):
        raise ValueError("Training squared weights do not sum to one")
    return np.sqrt(squared), rows


def fit_once(training: pd.DataFrame, model: str, ledger: dict, invocation: dict, kind: str, context: dict) -> tuple[np.ndarray, list[dict]]:
    if training.empty or not np.isfinite(training.H).all() or (training.H < 0).any():
        raise ValueError("Training data must have finite nonnegative curvature")
    matrix = design(training.angle.to_numpy(), model)
    if np.linalg.matrix_rank(matrix) < matrix.shape[1]:
        raise ValueError("Training design is rank deficient; comparison unresolved")
    weights, weight_rows = weighted_training_rows(training)
    record = reserve_nnls(ledger, invocation, kind, {**context, "model": model})
    try:
        coefficients, _ = nnls(matrix * weights[:, None], training.H.to_numpy() * weights)
        if model == "constant_area":
            area = (1.0 / coefficients[0]) ** 2 if coefficients[0] > 0 else np.inf
            if not np.isfinite(area) or area <= 0:
                raise ValueError("Constant-area fit has nonfinite or nonpositive area")
    except Exception as error:
        complete_nnls(ledger, record, None, error)
        raise
    complete_nnls(ledger, record, coefficients)
    return coefficients, weight_rows


def angle_support(training: pd.DataFrame, target: pd.DataFrame) -> dict:
    train_min, train_max = float(training.angle.min()), float(training.angle.max())
    target_min, target_max = float(target.angle.min()), float(target.angle.max())
    outside = (target.angle < train_min) | (target.angle > train_max)
    return {"training_angle_min_deg": train_min, "training_angle_max_deg": train_max,
            "target_angle_min_deg": target_min, "target_angle_max_deg": target_max,
            "target_count_outside_training_range": int(outside.sum()), "target_count": int(len(target))}


def verify_fold_partition(training: pd.DataFrame, target: pd.DataFrame, held_out_line: str) -> None:
    if target.empty or training.empty:
        raise ValueError("Missing target or training data")
    if set(training.group) & set(target.group):
        raise ValueError("Held-out group leaked into training")
    if held_out_line in set(training.cell_line):
        raise ValueError("Held-out line leaked into training")
    if len(training.cell_line.unique()) != 2:
        raise ValueError("Each registered line holdout must train on exactly two lines")


def verify_empirical_population(data: pd.DataFrame, selected_by_policy: dict[str, pd.DataFrame], design_document: dict) -> None:
    expected = design_document["cache_verified_before_registration"]
    if len(data) != expected["all_rows"]:
        raise ValueError("Verified input row count differs from registration")
    expected_lines = set(design_document["fixed_analysis"]["held_out_lines"])
    if set(data.cell_line.unique()) != expected_lines:
        raise ValueError("Cell-line set differs from registered holdouts")
    for policy, chosen in selected_by_policy.items():
        if len(chosen) != expected["policy_rows"][policy]:
            raise ValueError(f"Row count differs for policy {policy}")
        counts = chosen.groupby("cell_line").group.nunique().to_dict()
        if counts != expected["groups_by_line_each_policy"]:
            raise ValueError(f"Group count differs for policy {policy}")


def empirical_fold(chosen: pd.DataFrame, policy: str, held_out_line: str, ledger: dict, invocation: dict) -> dict:
    target = chosen.loc[chosen.cell_line == held_out_line].copy()
    training = chosen.loc[chosen.cell_line != held_out_line].copy()
    verify_fold_partition(training, target, held_out_line)
    training_groups, target_groups = sorted(training.group.unique()), sorted(target.group.unique())
    support = angle_support(training, target)
    models = {}
    for model in MODELS:
        coefficients, weight_rows = fit_once(training, model, ledger, invocation, "empirical", {
            "policy": policy, "held_out_line": held_out_line,
            "training_group_ids": training_groups, "target_group_ids": target_groups,
        })
        predicted = design(target.angle.to_numpy(), model) @ coefficients
        residual = np.abs(predicted - target.H.to_numpy())
        residual_by_row = pd.Series(residual, index=target.index)
        group_scores = [{"group": group, "n": int(len(part)),
                         "mae_inverse_nm": float(residual_by_row.loc[part.index].mean())}
                        for group, part in target.groupby("group", sort=True)]
        models[model] = {"coefficients": [float(x) for x in coefficients],
                         "training_weight_squared_by_group": weight_rows,
                         "target_group_mae_inverse_nm": group_scores,
                         "equal_target_group_mean_mae_inverse_nm": float(np.mean([x["mae_inverse_nm"] for x in group_scores])),
                         "angular_support": support}
    return {"policy": policy, "held_out_line": held_out_line, "training_line_ids": sorted(training.cell_line.unique()),
            "training_group_ids": training_groups, "target_group_ids": target_groups,
            "target_rows": int(len(target)), "models": models}


def run_checks() -> None:
    design_document = load_design_and_verify()
    ledger = load_ledger()
    verify_ledger_identity(ledger, design_document)
    invocation = reserve_invocation(ledger, "synthetic_checks", CHECKS_PATH)
    output = {"task_id": design_document["task_id"], "status": "running", "started_at_utc": utc_now(),
              "source_hashes": source_hashes(), "synthetic_checks": []}
    with CHECKS_PATH.open("x", encoding="utf-8") as stream:
        try:
            theta = np.array([0.0, 45.0, 90.0, 135.0, 180.0])
            for model, coefficients in (("constant_curvature", np.array([0.02])),
                                        ("constant_area", np.array([0.01])),
                                        ("flexible_reference", np.array([0.01, 0.02, 0.03, 0.04, 0.05]))):
                frame = pd.DataFrame({"cell_line": ["synthetic"] * len(theta), "group": ["synthetic:g"] * len(theta),
                                      "angle": theta, "H": design(theta, model) @ coefficients})
                recovered, weights = fit_once(frame, model, ledger, invocation, "synthetic", {"check": "exact_recovery"})
                if not np.allclose(recovered, coefficients, rtol=1e-10, atol=1e-12):
                    raise AssertionError(f"Synthetic {model} coefficients were not recovered")
                if (recovered < 0).any():
                    raise AssertionError(f"Synthetic {model} produced a negative coefficient")
                output["synthetic_checks"].append({"model": model, "expected_coefficients": coefficients.tolist(),
                                                   "recovered_coefficients": recovered.tolist(), "nonnegative": bool((recovered >= 0).all()),
                                                   "allclose_rtol": 1e-10, "allclose_atol": 1e-12, "weight_rows": weights})
            zero_area = pd.DataFrame({"cell_line": ["synthetic"] * len(theta), "group": ["synthetic:g"] * len(theta), "angle": theta, "H": np.zeros(len(theta))})
            try:
                fit_once(zero_area, "constant_area", ledger, invocation, "synthetic", {"check": "finite_area_boundary"})
            except ValueError as error:
                output["synthetic_checks"].append({"model": "constant_area", "finite_area_boundary_rejected": True, "error": str(error)})
            else:
                raise AssertionError("Zero constant-area coefficient was accepted")
            weight_probe = pd.DataFrame({"cell_line": ["train_a", "train_a", "train_a", "train_b", "train_b"],
                                         "group": ["a:1", "a:1", "a:2", "b:1", "b:1"],
                                         "angle": [0.0, 45.0, 90.0, 45.0, 90.0], "H": [0.0] * 5})
            probe_weights, weight_rows = weighted_training_rows(weight_probe)
            expected_group_totals = {"a:1": 0.25, "a:2": 0.25, "b:1": 0.5}
            observed_group_totals = {group: float(np.square(probe_weights[weight_probe.group.to_numpy() == group]).sum())
                                     for group in expected_group_totals}
            observed_line_totals = {line: float(np.square(probe_weights[weight_probe.cell_line.to_numpy() == line]).sum())
                                    for line in ("train_a", "train_b")}
            metadata_group_totals = {row["group"]: row["squared_weight_group_total"] for row in weight_rows}
            if (not all(np.isclose(observed_group_totals[group], expected_group_totals[group]) for group in expected_group_totals)
                    or not all(np.isclose(observed_line_totals[line], 0.5) for line in observed_line_totals)
                    or metadata_group_totals != expected_group_totals):
                raise AssertionError("Line/group weight construction differs from registered formula")
            target_probe = pd.DataFrame({"cell_line": ["held"], "group": ["held:1"], "angle": [0.0], "H": [0.0]})
            verify_fold_partition(weight_probe, target_probe, "held")
            try:
                verify_fold_partition(weight_probe, weight_probe.iloc[:1], "held")
            except ValueError:
                leakage_rejected = True
            else:
                leakage_rejected = False
            if not leakage_rejected:
                raise AssertionError("Training/target group overlap was accepted")
            output["partition_and_weight_checks"] = {"squared_weight_group_totals": observed_group_totals,
                                                       "squared_weight_line_totals": observed_line_totals,
                                                       "metadata_group_totals": metadata_group_totals,
                                                       "target_leakage_rejected": leakage_rejected}
            output["status"] = "completed"
        except Exception as error:
            output["status"] = "failed"; output["error"] = f"{type(error).__name__}: {error}"
            invocation["status"] = "failed"; invocation["error"] = output["error"]; save_ledger(ledger)
            raise
        finally:
            output["completed_at_utc"] = utc_now()
            stream.write(json.dumps(output, indent=2, allow_nan=False) + "\n")
    invocation["status"] = "completed"; invocation["completed_at_utc"] = utc_now(); save_ledger(ledger)


def run_empirical() -> None:
    design_document = load_design_and_verify()
    ledger = load_ledger()
    verify_ledger_identity(ledger, design_document)
    if not any(row["kind"] == "synthetic_checks" and row["status"] == "completed" for row in ledger["invocations"]):
        raise RuntimeError("Completed synthetic checks are required before reserving the empirical grid")
    invocation = reserve_invocation(ledger, "empirical_grid", RESULTS_PATH)
    output = {"task_id": design_document["task_id"], "status": "running", "started_at_utc": utc_now(),
              "source_hashes": source_hashes(), "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__}, "policies": {}}
    with RESULTS_PATH.open("x", encoding="utf-8") as stream:
        try:
            data = load_verified()
            selected_by_policy = {policy: select(data, policy) for policy in POLICIES}
            verify_empirical_population(data, selected_by_policy, design_document)
            for policy in POLICIES:
                chosen = selected_by_policy[policy]
                folds = [empirical_fold(chosen, policy, line, ledger, invocation) for line in sorted(chosen.cell_line.unique())]
                summary = {model: float(np.mean([fold["models"][model]["equal_target_group_mean_mae_inverse_nm"] for fold in folds])) for model in MODELS}
                output["policies"][policy] = {"rows": int(len(chosen)), "folds": folds,
                                                "equal_held_out_line_grand_mean_mae_inverse_nm": summary}
            if sum(row["kind"] == "empirical" for row in ledger["fits"]) != EMPIRICAL_CAP:
                raise RuntimeError("Empirical grid did not make exactly 27 reserved NNLS calls")
            output["status"] = "completed"
        except Exception as error:
            output["status"] = "failed"; output["error"] = f"{type(error).__name__}: {error}"
            invocation["status"] = "failed"; invocation["error"] = output["error"]; save_ledger(ledger)
            raise
        finally:
            output["completed_at_utc"] = utc_now()
            stream.write(json.dumps(output, indent=2, allow_nan=False) + "\n")
    invocation["status"] = "completed"; invocation["completed_at_utc"] = utc_now(); save_ledger(ledger)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--checks", action="store_true", help="reserve and run the bounded synthetic checks")
    command.add_argument("--run", action="store_true", help="reserve and run the one empirical 27-fit grid")
    args = parser.parse_args()
    if args.checks:
        run_checks()
    else:
        run_empirical()


if __name__ == "__main__":
    main()
