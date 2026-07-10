"""Contract tests for the perception image benchmark.

These lock in the validated behavior: the harness runs, the extractor recovers H
within tolerance in the operating band at calibration, the resolvability split is
sane, and the stressors degrade in the documented direction (occlusion tolerated,
background gradient worse). Kept cheap (small n) so the suite runs without pytest.
"""
import numpy as np

from validation import perception_benchmark as pb


def test_bands_are_ordered_and_disjoint():
    assert pb.BAND_LOW < pb.BAND_HIGH
    from curvo import synth_movie as sm
    _, gt = sm.render_movie(dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.06,
                                 active_force_max_pN=0.0), psf_sigma_nm=18.0, seed=0)
    op, deep = pb._resolvable_frames(gt, 18.0)
    assert set(op).isdisjoint(deep)                     # disjoint bands
    depth = np.asarray(gt.depth_nm)
    for i in op:
        assert pb.BAND_LOW <= depth[i] / 18.0 <= pb.BAND_HIGH
    for i in deep:
        assert depth[i] / 18.0 > pb.BAND_HIGH


def test_calibration_recovery_within_tolerance():
    r = pb.recover_one(n_rep=3, n_boot=6)
    assert r is not None and r["n_dome"] > 0
    # operating-band point estimate is the trustworthy metric: < 25% at calibration
    assert r["dome_rel_err"] < 0.25, f"dome rel-err {r['dome_rel_err']:.2f} too high"
    # deep-Omega under-reads MORE than the operating band (documented failure mode)
    if r["deep_omega_rel_err"] is not None:
        assert r["deep_omega_rel_err"] >= r["dome_rel_err"] - 0.05


def test_coverage_is_reported_even_when_low():
    # the CI under-covers in this band; the harness must REPORT it, not drop it
    r = pb.recover_one(n_rep=3, n_boot=6)
    assert "dome_coverage68" in r
    assert r["dome_coverage68"] is None or 0.0 <= r["dome_coverage68"] <= 1.0


def test_stressor_occlusion_tolerated_gradient_worse():
    out = pb.stressor_suite(n_rep=2, n_boot=6)
    base = out["baseline"]["rel_err_med"]
    # partial occlusion should not blow up (extractor uses the contiguous central dip)
    assert out["partial_occlusion"]["rel_err_med"] <= 2.0 * base
    # a background gradient degrades recovery (intensity-baseline confounder)
    assert out["background_gradient"]["degradation_x"] >= 1.2


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} perception-benchmark tests pass")
