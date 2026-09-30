"""Audit saved transfer predictions without fitting any model."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np

from compare_geometry import load_verified, select


ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "research"


def main():
    result = json.loads((R / "geometry_transfer_results_001.json").read_text())
    reference = json.loads((R / "geometry_transfer_weight_reference.json").read_text())
    ledger = json.loads((R / "geometry_transfer_execution.json").read_text())
    checks = json.loads((R / "geometry_transfer_checks_001.json").read_text())
    assert result["status"] == checks["status"] == "completed"
    for output in (result, checks):
        for path, expected in output["source_hashes"].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert len(ledger["invocations"]) == 2
    assert all(x["status"] == "completed" for x in ledger["invocations"])
    assert sum(x["kind"] == "empirical" for x in ledger["fits"]) == 27
    assert sum(x["kind"] == "synthetic" for x in ledger["fits"]) == 4
    assert all(x["status"] == "completed" for x in ledger["fits"] if x["kind"] == "empirical")
    data = load_verified()
    audited_groups = 0
    rows = []
    for policy, run in result["policies"].items():
        chosen = select(data, policy)
        assert len(chosen) == run["rows"]
        for fold in run["folds"]:
            line = fold["held_out_line"]
            target = chosen[chosen.cell_line == line]
            ref = next(x for x in reference["folds"] if x["policy"] == policy and x["held_line"] == line)
            assert sorted(fold["training_group_ids"]) == sorted(x["group"] for x in ref["train_groups"])
            assert sorted(fold["target_group_ids"]) == sorted(ref["held_groups"])
            assert fold["target_rows"] == ref["held_rows"] == len(target)
            for model, fitted in fold["models"].items():
                coef = np.array(fitted["coefficients"])
                theta = target.angle.to_numpy()
                # Independent prediction formulas; do not import the fitted basis.
                if model == "constant_curvature":
                    predicted = np.full(len(theta), coef[0])
                elif model == "constant_area":
                    predicted = 2 * np.sqrt(np.pi) * np.sin(theta * np.pi / 360) * coef[0]
                else:
                    predicted = np.interp(theta, [0, 45, 90, 135, 180], coef)
                errors = np.abs(predicted - target.H.to_numpy())
                scores = []
                for group in fitted["target_group_mae_inverse_nm"]:
                    selected = target.group.to_numpy() == group["group"]
                    assert int(selected.sum()) == group["n"]
                    mae = float(errors[selected].mean())
                    assert np.isclose(mae, group["mae_inverse_nm"], rtol=1e-12, atol=1e-15)
                    scores.append(mae)
                    audited_groups += 1
                assert len(scores) == len(ref["held_groups"])
                assert np.isclose(np.mean(scores), fitted["equal_target_group_mean_mae_inverse_nm"], rtol=1e-12, atol=1e-15)
                for weight in fitted["training_weight_squared_by_group"]:
                    exact = next(x for x in ref["train_groups"] if x["group"] == weight["group"])
                    assert weight["n_rows"] == exact["n_rows"]
                    assert weight["cell_line"] == exact["line"]
                    assert np.isclose(weight["squared_weight_per_row"], float(Fraction(exact["row_squared_weight_exact"])), rtol=1e-13, atol=0)
                    assert np.isclose(weight["squared_weight_group_total"], float(Fraction(exact["group_total_squared_weight_exact"])), rtol=1e-13, atol=0)
                support = fitted["angular_support"]
                assert support["target_count_outside_training_range"] == ref["held_outside_training_angle_range_count"]
                assert [support["training_angle_min_deg"], support["training_angle_max_deg"]] == ref["train_angle_range_deg"]
                assert [support["target_angle_min_deg"], support["target_angle_max_deg"]] == ref["held_angle_range_deg"]
                entry = next(x for x in ledger["fits"] if x["kind"] == "empirical" and x["context"]["policy"] == policy and x["context"]["held_out_line"] == line and x["context"]["model"] == model)
                assert fitted["coefficients"] == entry["coefficients"]
            rows.append({"policy": policy, "held_out_line": line, "ranking": sorted(fold["models"], key=lambda m: fold["models"][m]["equal_target_group_mean_mae_inverse_nm"]), "outside_training_angle_range": ref["held_outside_training_angle_range_count"]})
        for model, grand in run["equal_held_out_line_grand_mean_mae_inverse_nm"].items():
            assert np.isclose(grand, np.mean([f["models"][model]["equal_target_group_mean_mae_inverse_nm"] for f in run["folds"]]), rtol=1e-13, atol=0)
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "status": "passed", "additional_fit_calls": 0, "fold_model_predictions": 27, "group_model_scores_recomputed": audited_groups, "source_locks": "passed", "exact_prefit_weight_reference": "passed", "rankings": rows, "empirical_fit_calls_total": 27, "synthetic_fit_calls_total": 4, "expected_boundary_rejection": True}
    with (R / "geometry_transfer_prediction_audit.json").open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
