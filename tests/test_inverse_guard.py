"""Plateau-guard tests for run_nested.

The image->force pipeline once hung ~6h on a dynesty likelihood plateau because
run_nested had no stopping caps. These lock in the guard: a maxcall cap trips
`stopped_early` and returns promptly, and a normal run finishes WITHOUT tripping
the cap (the guard bounds runaway cost, it does not truncate a healthy run).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from curvo import inverse as inv


def _synth_traj(seed=0):
    """A simple resolvable dome H-trajectory + actin channel with known force."""
    T = 24
    t = np.linspace(0, 1, T)
    cov = 1.0 / (1.0 + np.exp(-(t - 0.45) / 0.12))
    H = 0.002 + 0.02 * cov                    # rises into the dome band
    Hs = np.full(T, 0.003)
    A_coat = np.pi * 60.0 ** 2
    actin = cov * (40.0 / 60.0)               # force 40 pN / ACTIN_CALIB 60
    asig = np.full(T, 0.05)
    return H, Hs, A_coat, actin, asig


def test_maxcall_trips_stopped_early():
    H, Hs, Ac, a, asig = _synth_traj()
    r = inv.run_nested(H, Hs, Ac, actin_obs=a, actin_sigma=asig,
                       nlive=100, seed=0, maxcall=2000)
    assert r["stopped_early"] is True
    assert r["ncall"] is not None and r["ncall"] < 20000   # bounded, not runaway


def test_normal_run_does_not_trip_cap():
    H, Hs, Ac, a, asig = _synth_traj()
    r = inv.run_nested(H, Hs, Ac, actin_obs=a, actin_sigma=asig,
                       nlive=100, seed=0)                  # default guards
    assert r["stopped_early"] is False
    assert np.isfinite(r["logz"])


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} inverse-guard tests pass")
