from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np

import research.cap_observation_v2 as cap


def test_inverse_roundtrip_on_nonidentity_monotone_profile() -> None:
    rho = np.linspace(0, 1, 101)
    spline = cap.CubicHermiteSpline(rho, rho + .2*rho*rho, 1 + .4*rho)
    radii = np.array([.03, .4, .9])
    inverted = cap.inverse_r(spline, radii, 1.)
    assert np.max(np.abs(spline(inverted) - radii)) < 1e-10


def test_sphere_flat_and_deadline_guards(monkeypatch) -> None:
    fixed_time = datetime(2026, 9, 25, 3, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(cap, "now", lambda: fixed_time)
    sphere = cap.control("sphere", "uniform_r")
    flat = cap.control("flat", "uniform_material_alpha")
    assert abs(sphere["h"] - .4) <= 1e-8
    assert flat["h"] == 0 and flat["flat_boundary"]
    original = cap.DEADLINE
    cap.DEADLINE = cap.now() - timedelta(seconds=1)
    try:
        assert cap.control("sphere", "uniform_r")["status"] == "deadline_not_started"
    finally:
        cap.DEADLINE = original
