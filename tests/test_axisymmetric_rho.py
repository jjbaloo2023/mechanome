from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

import research.axisymmetric_rho as rho


ROOT = Path(__file__).resolve().parents[1]


def test_chain_rule_matches_alpha_system_at_regular_state() -> None:
    coordinate = np.array([0.4, 1.3])
    state = np.array([[0.42, 1.31], [-.01, -.002], [.002, .004],
                      [.003, .001], [.0002, .0004], [.5, .5]])
    fun, _ = rho.system(.005, .5, .01, 1e-3)
    transformed = fun(coordinate, state, np.array([.003, -.01, .5]))
    expected = coordinate * rho.alpha_rhs(coordinate*coordinate/2, state, .005, .5, .01)
    assert np.allclose(transformed, expected)


def test_timeout_is_retained_as_a_case_record(monkeypatch) -> None:
    def timed_out(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("rho", 45)
    monkeypatch.setattr(rho.subprocess, "run", timed_out)
    record = rho.run_all()
    assert len(record["records"]) == 4
    assert all(r["status"] == "timeout" and not r["success"] for r in record["records"])


def test_frozen_rho_result_recovers_prior_and_high_amplitude_cases() -> None:
    with (ROOT / "research/axisymmetric_rho_results_002.json").open(encoding="utf-8") as handle:
        records = json.load(handle)["records"]
    assert all(r["success"] for r in records)
    values = [r["observables"]["apex_H_over_C_source"] for r in records]
    assert abs(values[0] - .6019321799722624) < 2e-6
    assert abs(values[1] - .6019327465645625) < 2e-6
    assert records[2]["nodes_final"] < 12000
    assert max(records[2]["max_abs_arc_length_cross_coordinate_defect"]) < 2e-8
