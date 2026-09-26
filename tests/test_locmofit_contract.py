"""Focused tests for the LocMoFit processed-observation adapter contract."""
import json

import pandas as pd
import pytest

from validation.realdata.ingest_smlm_locmofit import ingest_locmofit


def _row(**changes):
    row = {
        "ID": 7, "cell_line": "SKMEL2", "file_number": 3,
        "theta": 42.0, "curvature": 0.01, "radius": -100.0,
        "surface_area": 1234.0, "projected_area": 456.0,
        "theta_corrected": 0.0001, "curvature_corrected": 0.0,
        "disconnected_sites": False,
    }
    row.update(changes)
    return row


def _write_fixture(tmp_path, *rows):
    path = tmp_path / "locmofit_fixture.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_default_preserves_legacy_raw_nonnegative_unflagged_cohort(tmp_path):
    _write_fixture(
        tmp_path, _row(), _row(ID=8, curvature=-0.001),
        _row(ID=9, disconnected_sites=True))

    gs = ingest_locmofit(str(tmp_path))

    assert [site.site_id for site in gs.sites] == [7]
    site = gs.sites[0]
    assert site.H_inv_nm == 0.01
    assert site.theta_deg == 42.0
    assert site.H_sigma_inv_nm is None
    assert gs.provenance["geometry_selection"] == "raw_nonnegative"
    assert gs.provenance["curvature_uncertainty_calibrated"] is False
    assert "unknown" in gs.provenance["curvature_uncertainty"]


def test_legacy_uncertainty_requires_explicit_exploratory_opt_in(tmp_path):
    _write_fixture(tmp_path, _row())

    gs = ingest_locmofit(str(tmp_path), legacy_curvature_sigma=True)

    assert gs.sites[0].H_sigma_inv_nm is not None
    assert gs.sites[0].H_sigma_inv_nm > 0
    assert gs.provenance["curvature_uncertainty_calibrated"] is False
    assert gs.provenance["curvature_uncertainty"].startswith("exploratory_")


def test_corrected_selection_preserves_deposited_raw_geometry(tmp_path):
    fixture = _write_fixture(
        tmp_path, _row(curvature=-0.01, rim_length=789.0))

    raw = ingest_locmofit(str(tmp_path))
    assert raw.sites == []

    gs = ingest_locmofit(str(tmp_path), geometry="corrected")

    site = gs.sites[0]
    assert site.H_inv_nm == 0.0
    assert site.theta_deg == 0.0001
    assert site.raw_H_inv_nm == -0.01
    assert site.raw_theta_deg == 42.0
    assert site.corrected_H_inv_nm == 0.0
    assert site.corrected_theta_deg == 0.0001
    assert site.corrected_geometry_supplied is True
    assert site.R_nm == 100.0
    assert site.raw_R_nm == -100.0
    assert site.surface_area_nm2 == 1234.0
    assert site.projected_area_nm2 == 456.0
    assert site.rim_length_nm == 789.0
    assert site.source_key == "SKMEL2:3:7"
    assert site.source_path == str(fixture.resolve())


def test_json_serializes_unknown_sigma_as_null_and_by_cell_line_keeps_contract(tmp_path):
    _write_fixture(tmp_path, _row())
    gs = ingest_locmofit(str(tmp_path)).by_cell_line("SKMEL2")
    output = tmp_path / "geometry.json"

    gs.to_json(output)

    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["sites"][0]["H_sigma_inv_nm"] is None
    assert exported["provenance"]["observation_contract_version"]
    assert exported["cell_lines"] == ["SKMEL2"]


def test_corrected_selection_rejects_missing_corrected_fields(tmp_path):
    _write_fixture(tmp_path, _row())
    path = tmp_path / "locmofit_fixture.csv"
    frame = pd.read_csv(path).drop(
        columns=["theta_corrected", "curvature_corrected", "disconnected_sites"])
    frame.to_csv(path, index=False)

    raw = ingest_locmofit(str(tmp_path))
    assert raw.sites[0].corrected_geometry_supplied is False
    assert raw.sites[0].corrected_theta_deg is None
    assert raw.sites[0].corrected_H_inv_nm is None
    assert raw.sites[0].disconnected_sites is None

    with pytest.raises(ValueError, match="requires deposited corrected fields"):
        ingest_locmofit(str(tmp_path), geometry="corrected")


def test_corrected_selection_rejects_nonfinite_corrected_values(tmp_path):
    _write_fixture(tmp_path, _row(curvature_corrected=float("nan")))

    with pytest.raises(ValueError, match="requires finite deposited"):
        ingest_locmofit(str(tmp_path), geometry="corrected")


def test_unknown_geometry_selection_is_rejected(tmp_path):
    _write_fixture(tmp_path, _row())

    with pytest.raises(ValueError, match="geometry must be"):
        ingest_locmofit(str(tmp_path), geometry="invented")


def test_legacy_uncertainty_opt_in_must_be_boolean(tmp_path):
    _write_fixture(tmp_path, _row())

    with pytest.raises(TypeError, match="explicit bool"):
        ingest_locmofit(str(tmp_path), legacy_curvature_sigma="False")
