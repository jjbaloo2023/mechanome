"""Contract tests for the cryo-ET density -> GeometryTrace modality adapter.

Uses a SYNTHETIC dark-contrast ring (a known radius) so the test needs no network
and the expected curvature is exact. Locks in: the adapter recovers a known ring
radius, contrast flip is required (bright-membrane assumption would fail on dark
input), the two curvature models differ by the correct factor of 2, and force is
correctly withheld for a static single frame.
"""
import numpy as np

from validation import modality_adapter as ma


def _dark_ring(R_px=12.0, W=96, sigma=2.0):
    """A synthetic DARK membrane ring: low intensity at radius R on a bright field."""
    yy, xx = np.mgrid[0:W, 0:W]
    rr = np.sqrt((yy - (W - 1) / 2) ** 2 + (xx - (W - 1) / 2) ** 2)
    ring = np.exp(-((rr - R_px) ** 2) / (2 * sigma ** 2))
    return 100.0 * (1.0 - 0.8 * ring)                 # membrane = dark dip


def test_recovers_known_ring_radius():
    img = _dark_ring(R_px=12.0)
    fit = ma.fit_ring(img, nm_per_px=1.0, contrast="dark", n_boot=50)
    assert abs(fit["R_nm"] - 12.0) < 1.5, f"recovered R={fit['R_nm']:.1f}, expected ~12"
    assert fit["R_sigma_nm"] > 0 and np.isfinite(fit["H_sigma_inv_nm"])


def test_contrast_flip_is_load_bearing():
    img = _dark_ring(R_px=12.0)
    dark = ma.fit_ring(img, nm_per_px=1.0, contrast="dark", n_boot=20)
    bright = ma.fit_ring(img, nm_per_px=1.0, contrast="bright", n_boot=20)
    # with the correct (dark) contrast the peak SNR is high; wrong contrast is worse
    assert dark["contrast_snr"] > bright["contrast_snr"]


def test_curv_model_factor_of_two():
    img = _dark_ring(R_px=12.0)
    cyl = ma.fit_ring(img, nm_per_px=1.0, curv_model="cylindrical", n_boot=10)
    sph = ma.fit_ring(img, nm_per_px=1.0, curv_model="spherical", n_boot=10)
    assert abs(sph["H_inv_nm"] / cyl["H_inv_nm"] - 2.0) < 1e-6


def test_force_withheld_for_static_frame():
    img = _dark_ring(R_px=12.0)
    trace, meta = ma.adapt_density_image(img, nm_per_px=1.0, source_id="synthetic")
    assert len(trace.frames) == 1
    assert trace.has_actin_channel is False
    assert meta["force_applicable"] is False
    assert trace.frames[0].actin_density == 0.0


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} modality-adapter tests pass")
