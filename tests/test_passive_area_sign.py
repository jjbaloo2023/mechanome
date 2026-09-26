from __future__ import annotations

import hashlib
from pathlib import Path

import research.passive_area_sign as area


ROOT = Path(__file__).resolve().parents[1]


def _accepted(case: dict) -> dict:
    return {"case": case, "success": True, "status": 0,
            "gates": {"solver": True, "rms": True, "outer_bc": True, "Q": True,
                      "positive_radius": True, "psi_bound": True, "cos_psi_bound": True, "finite": True},
            "state_path": case["state_path"], "state_sha256": "mock",
            "observables": {"max_abs_psi_radians": .1}}


def test_stopped_sequence_never_retries_later_amplitudes(monkeypatch) -> None:
    invoked: list[str] = []
    def fake(case: dict) -> dict:
        invoked.append(case["label"])
        if case["label"] == "x0.5_c0.02":
            return {"case": case, "success": False, "status": "timeout", "message": "mock"}
        return _accepted(case)
    monkeypatch.setattr(area, "run_subprocess", fake)
    result = area.run_all()
    assert "x0.5_c0.02" in invoked
    assert not any(label.startswith("x0.5_c0.1") or label.startswith("x0.5_c0.3") or label.startswith("x0.5_c0.6") for label in invoked)
    skipped = [r for r in result["records"] if r["case"]["label"].startswith("x0.5_") and r["status"] == "skipped"]
    assert len(skipped) == 3


def test_next_case_receives_preceding_accepted_seed(monkeypatch) -> None:
    seen: dict[str, dict] = {}
    def fake(case: dict) -> dict:
        seen[case["label"]] = case.copy()
        return _accepted(case)
    monkeypatch.setattr(area, "run_subprocess", fake)
    area.run_all()
    assert seen["x1_c0.1"]["seed_state_path"].endswith("x1_c0.02.npz")
    assert seen["x1_c0.3"]["seed_state_path"].endswith("x1_c0.1.npz")


def test_saved_result_is_not_changed_by_mocked_control_flow(monkeypatch) -> None:
    path = ROOT / "research/passive_area_results_001.json"
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(area, "run_subprocess", lambda case: _accepted(case))
    area.run_all()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
