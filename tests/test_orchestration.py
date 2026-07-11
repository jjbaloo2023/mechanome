"""
Contract tests for the multi-structure orchestration pipeline (Steps 2-6).

These lock in the load-bearing behaviors without re-running the expensive nested
sampling: the field generator produces exact per-structure ground truth, detection's
absolute-intensity gate rejects empty frames, tracking recovers structures, the
motion field is a kinematic (not force) observable, the generator's active_delay is
the switch that makes orchestration falsifiable (delay=0 keeps the recovery gate
intact), and the orchestration claim respects the mechanome LINKED-tier firewall.
"""
import os, sys
import dataclasses
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from curvo import synth_movie as sm
from validation import field_movie as fm
from validation import tracking as tk
from validation import orchestration as orch


def _small_field(seed=0):
    return fm.generate_field(n_struct=4, field_px=160, T_field=32, lifetime=20, seed=seed)


def test_field_has_exact_ground_truth():
    movie, tracks, meta = _small_field()
    assert movie.ndim == 4 and movie.shape[1] == len(meta["channels"])
    for t in tracks:
        assert 0 <= t.birth < t.death <= meta["T_field"]
        assert len(t.H_inv_nm) == t.death - t.birth          # geometry(t) per lifetime frame
        assert len(t.active_force_series_pN) == t.death - t.birth


def test_detection_absolute_gate_rejects_empty_frames():
    """The load-bearing gate: a structure-free (noise-only) frame yields ~0 detections."""
    rng = np.random.default_rng(0)
    empty = rng.normal(2.0, 2.0, size=(160, 160)).clip(0)   # read-noise floor only
    dets = tk.detect_blobs(empty, psf_sigma_px=9.0)
    assert len(dets) == 0, f"empty frame fired {len(dets)} spurious detections"


def test_tracking_recovers_structures():
    movie, tracks, meta = _small_field()
    gt = [dataclasses.asdict(t) for t in tracks]
    rec, _ = tk.run_tracking(movie, meta)
    val = tk.validate_tracking(rec, gt, meta, movie=movie)
    # most seeded structures should be found; a pit whose coat never clears the
    # optical floor within a short lifetime is legitimately undetectable, so we
    # require the majority rather than all (recall is physically bounded).
    assert val["gt_detected_frac"] >= 0.5, val
    assert val["n_tracks"] >= val["gt_structures_detected"], val


def test_active_delay_controls_force_lag():
    """delay=0 keeps curvature/force coincident (recovery gate intact); delay>0 lags force."""
    tr0 = sm.simulate_trajectory(c_eff_max_inv_nm=0.065, active_force_max_pN=50, active_delay=0.0)
    trd = sm.simulate_trajectory(c_eff_max_inv_nm=0.065, active_force_max_pN=50, active_delay=0.30)
    # delay=0: force ramp == magnitude * coverage (unchanged from the calibrated model)
    assert np.max(np.abs(tr0["active"] - 50 * tr0["coverage"])) < 1e-6
    # delayed force onset is strictly later
    o0 = orch.onset_frame(tr0["active"]); od = orch.onset_frame(trd["active"])
    assert od > o0, f"delayed onset {od} not later than {o0}"


def test_orchestration_claim_respects_linked_firewall():
    """The emitted claim is LINKED tier and carries NO physical value (firewall)."""
    _, tracks, _ = _small_field()
    gt = [dataclasses.asdict(t) for t in tracks]
    rows = [dict(sid=t.sid, posterior_median=40.0, point_estimate=None,
                 identified=False, ci68=None, true_force=t.active_force_pN) for t in tracks]
    model = orch.build_orchestration_model(rows, gt)
    claim = orch.to_mechano_claim(model)          # raises TierViolation if value attached
    assert claim is not None
    assert claim.value is None                    # firewall: LINKED carries no value
    assert model["falsifiable"]["fraction_curvature_first"] is not None


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} orchestration tests pass")
