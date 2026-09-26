from __future__ import annotations

from datetime import timedelta

import numpy as np
import pytest

import research.cap_observation as cap


def test_exact_sphere_and_flat_controls_recover_expected_boundaries() -> None:
    controls = cap.controls()
    sphere = [c for c in controls if c["name"] == "sphere"]
    flat = [c for c in controls if c["name"] == "flat"]
    assert all(abs(c["h"] - .4) <= 1e-8 and c["rmse"] <= 1e-10 for c in sphere)
    assert all(c["h"] == 0 and c["flat_boundary"] and c["rmse"] == 0 for c in flat)


def test_deadline_prevents_a_fit_before_profile_access(monkeypatch) -> None:
    monkeypatch.setattr(cap, "DEADLINE", cap.now() - timedelta(seconds=1))
    result = cap.record_fit("x1_c0.02", .02, .1, "uniform_r")
    assert result["status"] == "deadline_not_started"


def test_durable_records_are_exclusive(tmp_path) -> None:
    path = tmp_path / "record.json"
    cap.exclusive(path, {"ok": True})
    with pytest.raises(FileExistsError):
        cap.exclusive(path, {"ok": False})
