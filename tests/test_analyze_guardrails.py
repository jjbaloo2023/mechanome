"""
Guardrail tests for the analyze() endpoint — the anti-"force-astrology" contract.

These are the tests that keep the endpoint honest as the code evolves:
  1. An identifiable, recovery-calibrated force (active_force under an actin
     channel) IS returned as a point estimate near truth.
  2. A force that is NOT recovery-calibrated (c_eff from geometry) is NEVER
     returned as a point value, even when its single-shot posterior looks narrow.
  3. From geometry alone, the mechanism verdict is UNDETERMINED (no spurious
     'decisive' win via an unidentifiable degeneracy) and an experiment is
     proposed.
  4. The provenance block records the movie hash, engine, and module versions.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from curvo import synth_movie as sm
from curvo import analyze as az


def _actin_movie(seed=5):
    mv, gt = sm.render_movie(
        dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.008, active_force_max_pN=40.0,
             kappa_kBT=20, coat_rigidity_factor=3.0, T=24),
        field_px=128, nm_per_px=2.0, psf_sigma_nm=18.0, has_actin=True, seed=seed)
    return mv, gt


def _wedge_movie(seed=1):
    mv, gt = sm.render_movie(
        dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.045, active_force_max_pN=0.0,
             kappa_kBT=20, coat_rigidity_factor=3.0, T=24),
        field_px=128, nm_per_px=2.0, psf_sigma_nm=18.0, has_actin=False, seed=seed)
    return mv, gt


def test_identifiable_force_returns_point_estimate():
    mv, gt = _actin_movie()
    r = az.analyze(mv, question="wedge or actin?", channels=gt.channels, seed=0)
    af = r["forces"]["active_force_max"]
    assert af["status"] == "identified", af
    assert af["point_estimate"] is not None
    assert 25.0 <= af["point_estimate"] <= 55.0, af["point_estimate"]  # truth 40


def test_uncalibrated_force_never_point_estimate():
    mv, gt = _actin_movie()
    r = az.analyze(mv, question="wedge or actin?", channels=gt.channels, seed=0)
    ce = r["forces"]["c_eff_max"]
    # c_eff is not recovery-calibrated from this observable set -> no point value,
    # regardless of how narrow the single-shot posterior is
    assert ce["point_estimate"] is None, ce
    assert ce["status"] == "underdetermined"
    assert ce["recovery_calibrated"] is False


def test_geometry_only_is_undetermined_and_suggests_experiment():
    mv, gt = _wedge_movie()
    r = az.analyze(mv, question="wedge or actin?", channels=gt.channels, seed=0)
    assert r["favored_mechanism"]["favored"] == "UNDETERMINED", r["favored_mechanism"]
    assert r["suggested_experiment"] is not None
    assert "actin" in r["suggested_experiment"]["observable"].lower()
    # no force may be a point estimate without the actin channel
    assert all(v["point_estimate"] is None for v in r["forces"].values())


def test_provenance_recorded():
    mv, gt = _actin_movie()
    r = az.analyze(mv, question="wedge or actin?", channels=gt.channels, seed=0)
    p = r["provenance"]
    assert len(p["movie_sha256_16"]) == 16
    assert "dynesty" in p["engine"]
    assert p["module_versions"] and all(isinstance(v, str) for v in p["module_versions"].values())


if __name__ == "__main__":
    import traceback
    tests = [test_identifiable_force_returns_point_estimate,
             test_uncalibrated_force_never_point_estimate,
             test_geometry_only_is_undetermined_and_suggests_experiment,
             test_provenance_recorded]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} analyze guardrail tests pass")
