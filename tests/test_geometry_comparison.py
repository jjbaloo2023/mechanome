import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from research import compare_geometry as geometry
from research.compare_geometry import compare, design, fit


def synthetic(model, coefficient):
    angle = np.tile(np.linspace(0, 180, 25), 3)
    return pd.DataFrame(
        {
            "angle": angle,
            "H": design(angle, model) @ np.array([coefficient]),
            "group": np.repeat(["a", "b", "c"], 25),
            "cell_line": "synthetic",
        }
    )


@pytest.mark.parametrize(
    "model,coefficient",
    [("constant_curvature", 0.01), ("constant_area", 1 / np.sqrt(30000))],
)
def test_synthetic_recovery(model, coefficient):
    data = synthetic(model, coefficient)
    assert fit(data, model)[0] == pytest.approx(coefficient)
    result = compare(data)
    assert result["summary_mae_inverse_nm"]["synthetic"][model] < 1e-14


def test_held_out_values_do_not_affect_training():
    data = synthetic("constant_curvature", 0.01)
    first = compare(data)["folds"][0]
    data.loc[data.group == first["held_out"], "H"] = 0.03
    second = compare(data)["folds"][0]
    assert first["held_out"] not in first["training_groups"]
    for model in first["models"]:
        assert (
            first["models"][model]["coefficients"]
            == second["models"][model]["coefficients"]
        )
    assert second["models"]["constant_curvature"]["mae"] > 0.01


def test_equal_group_weight_survives_duplicate_rows_within_group():
    data = synthetic("constant_curvature", 0.01)
    data.loc[data.group == "a", "H"] = 0.02
    expanded = pd.concat([data, data.loc[data.group == "a"]])
    assert fit(data, "constant_curvature") == pytest.approx(
        fit(expanded, "constant_curvature")
    )


def test_units_boundaries_and_nonnegative_basis():
    assert design([0, 180], "constant_area")[:, 0] == pytest.approx(
        [0, np.sqrt(4 * np.pi)]
    )
    basis = design(np.linspace(0, 180, 101), "flexible_reference")
    assert (basis >= 0).all()
    assert basis.sum(axis=1) == pytest.approx(np.ones(101))
    with pytest.raises(ValueError):
        design([-1], "constant_area")


def test_constant_area_rejects_infinite_area_boundary():
    with pytest.raises(ValueError, match="finite positive area"):
        fit(synthetic("constant_curvature", 0), "constant_area")


def frozen_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(geometry, "ROOT", tmp_path)
    research = tmp_path / "research"
    research.mkdir()
    cache = tmp_path / "cache/smlm_locmofit/audit"
    cache.mkdir(parents=True)
    content = b"original table bytes"
    (cache / "cell.csv").write_bytes(content)
    audit = {
        "tables": [
            {
                "path": "cell.csv",
                "sha256": hashlib.sha256(content).hexdigest(),
                "published_md5": hashlib.md5(content).hexdigest(),
            }
        ]
    }
    (research / "data_audit.json").write_text(json.dumps(audit))
    (research / "FIRST_COMPARISON.md").write_text("frozen protocol")
    (research / "compare_geometry.py").write_text("frozen implementation")
    lock = {
        "sha256": {
            f"research/{name}": hashlib.sha256(
                (research / name).read_bytes()
            ).hexdigest()
            for name in (
                "data_audit.json",
                "FIRST_COMPARISON.md",
                "compare_geometry.py",
            )
        }
    }
    (research / "geometry_inputs.lock.json").write_text(json.dumps(lock))
    return research, cache, audit, lock


def test_jointly_changed_table_and_audit_cannot_bypass_frozen_lock(
    tmp_path, monkeypatch
):
    research, cache, audit, _ = frozen_fixture(tmp_path, monkeypatch)
    altered = b"altered table bytes"
    (cache / "cell.csv").write_bytes(altered)
    audit["tables"][0]["sha256"] = hashlib.sha256(altered).hexdigest()
    (research / "data_audit.json").write_text(json.dumps(audit))
    with pytest.raises(ValueError, match="Frozen input changed"):
        geometry.load_verified()


def test_published_md5_still_checked_after_explicit_audit_relock(tmp_path, monkeypatch):
    research, cache, audit, lock = frozen_fixture(tmp_path, monkeypatch)
    altered = b"altered table bytes"
    (cache / "cell.csv").write_bytes(altered)
    audit["tables"][0]["sha256"] = hashlib.sha256(altered).hexdigest()
    (research / "data_audit.json").write_text(json.dumps(audit))
    lock["sha256"]["research/data_audit.json"] = hashlib.sha256(
        (research / "data_audit.json").read_bytes()
    ).hexdigest()
    (research / "geometry_inputs.lock.json").write_text(json.dumps(lock))
    with pytest.raises(ValueError, match="Published MD5 mismatch"):
        geometry.load_verified()


def test_changed_protocol_stops_before_reading_tables(tmp_path, monkeypatch):
    research, _, _, _ = frozen_fixture(tmp_path, monkeypatch)
    (research / "FIRST_COMPARISON.md").write_text("changed protocol")
    with pytest.raises(ValueError, match="Frozen input changed"):
        geometry.load_verified()
