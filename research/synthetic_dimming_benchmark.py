"""Frozen synthetic dimming-before-detection benchmark.

This deliberately uses the existing validation.tracking.run_tracking unchanged.
It is an observation-model sensitivity calculation, not an empirical analysis or
physical inverse.  See synthetic_dimming_design.json for the registered inputs.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

from validation.tracking import run_tracking


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DESIGN_PATH = HERE / "synthetic_dimming_design.json"
TRACKER_PATH = ROOT / "validation" / "tracking.py"
RESULT_PATH = HERE / "synthetic_dimming_results.json"
CHECK_PATH = HERE / "synthetic_dimming_checks.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def kernel(height: int, width: int, cy: float, cx: float, sigma: float) -> np.ndarray:
    y, x = np.mgrid[:height, :width]
    return np.exp(-((y - cy) ** 2 + (x - cx) ** 2) / (2 * sigma ** 2))


def envelope(duration: int) -> np.ndarray:
    age = np.arange(duration, dtype=float)
    return np.sin(np.pi * (age + 0.5) / duration)


def make_movie(d, duration: int, peak: float, gain: float, noise: np.ndarray,
               present: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Return [T,1,H,W] image and gain-specific noiseless center values."""
    T, H = d["frames"], d["height_width_px"]
    cy, cx = d["center_yx_px"]
    movie = d["background_photons"] + noise.copy()
    center = np.full(T, float(d["background_photons"]))
    if present:
        signal = gain * peak * envelope(duration)
        k = kernel(H, H, cy, cx, d["psf_sigma_px"])
        b = d["birth_frame"]
        movie[b:b + duration] += signal[:, None, None] * k[None, :, :]
        center[b:b + duration] += signal
    return movie[:, None, :, :], center


def tracked_event_row(event, gain: float, movie: np.ndarray, noiseless_center: np.ndarray,
                      d, noise_hash: str) -> dict:
    """Score retained tracker points directly against the one known latent event."""
    meta = {"psf_sigma_nm": d["psf_sigma_px"], "nm_per_px": 1.0, "channels": ["coat"]}
    tracks, dets = run_tracking(movie, meta, gate_px=4, max_gap=0, min_track_len=4)
    birth, death = d["birth_frame"], d["birth_frame"] + event["duration_frames"]
    cy, cx = d["center_yx_px"]
    fragments, union, fp_points, retained_points = [], set(), 0, 0
    for track in tracks:
        matched = []
        for frame, y, x in zip(track.frames, track.ys, track.xs):
            retained_points += 1
            good = birth <= frame < death and np.hypot(y - cy, x - cx) <= d["ground_truth_matching_radius_px"]
            if good:
                matched.append(frame)
                union.add(frame)
            else:
                fp_points += 1
        if matched:
            fragments.append({"track_id": track.tid, "matched_frames": sorted(matched),
                              "track_frames": list(track.frames), "n_matched_frames": len(matched)})
    truth_frames = list(range(birth, death))
    eligible = [f for f in truth_frames if noiseless_center[f] >= 25.0]
    # Observed span is the inclusive first-to-last frame of the UNION of matched
    # points across retained fragments.  It is deliberately null for a missing event.
    observed_span = (max(union) - min(union) + 1) if union else None
    row = {
        "event_id": event["event_id"], "seed": event["seed"], "duration_frames": event["duration_frames"],
        "peak_signal_photons": event["peak_signal_photons"], "gain": gain,
        "noise_sha256": noise_hash, "truth_frames": truth_frames,
        "eligible_truth_frames_noiseless_center_ge_25": eligible,
        "union_matched_frames": sorted(union), "n_union_matched_frames": len(union),
        "ever_matched": bool(union), "n_fragments": len(fragments), "fragments": fragments,
        "observed_span_frames_union": observed_span,
        "unconditional_coverage_numerator": len(union), "unconditional_coverage_denominator": len(truth_frames),
        "conditional_coverage_numerator": sum(f in set(eligible) for f in union),
        "conditional_coverage_denominator": len(eligible),
        "retained_track_count": len(tracks), "retained_point_count": retained_points,
        "retained_track_supports": [{"track_id": t.tid, "frames": list(t.frames)} for t in tracks],
        "false_positive_points": fp_points, "raw_detection_count_all_lengths": sum(len(x) for x in dets),
    }
    return row


def summarize(rows, gain: float) -> dict:
    un_num = sum(r["unconditional_coverage_numerator"] for r in rows)
    un_den = sum(r["unconditional_coverage_denominator"] for r in rows)
    co_num = sum(r["conditional_coverage_numerator"] for r in rows)
    co_den = sum(r["conditional_coverage_denominator"] for r in rows)
    present = [r for r in rows if r["ever_matched"]]
    return {
        "gain": gain, "n_events": len(rows), "events_ever_matched": len(present), "events_denominator": len(rows),
        "unconditional_matched_frames": un_num, "unconditional_truth_frames": un_den,
        "unconditional_coverage": un_num / un_den,
        "conditional_matched_frames": co_num, "conditional_eligible_truth_frames": co_den,
        "conditional_coverage": co_num / co_den if co_den else None,
        "missing_event_count": len(rows) - len(present),
        "observed_span_frames_among_matched_events": [r["observed_span_frames_union"] for r in present],
        "mean_observed_span_frames_among_matched_events": float(np.mean([r["observed_span_frames_union"] for r in present])) if present else None,
        "total_fragments": sum(r["n_fragments"] for r in rows),
        "false_positive_points": sum(r["false_positive_points"] for r in rows),
        "retained_point_count": sum(r["retained_point_count"] for r in rows),
    }


def main() -> None:
    started = datetime.now(timezone.utc)
    design = json.loads(DESIGN_PATH.read_text())
    d = design["fixed_design"]
    events = []
    for seed in d["seeds"]:
        for duration in d["latent_durations_frames"]:
            for peak in d["peak_signal_photons"]:
                event_id = f"seed{seed}_duration{duration}_peak{peak}"
                rng = np.random.default_rng(seed * 100000 + duration * 1000 + peak)
                noise = rng.normal(0.0, d["read_noise_sd"], size=(d["frames"], d["height_width_px"], d["height_width_px"]))
                events.append(({"event_id": event_id, "seed": seed, "duration_frames": duration,
                                "peak_signal_photons": peak}, noise, hashlib.sha256(noise.tobytes()).hexdigest()))
    rows = []
    for event, noise, noise_hash in events:
        for gain in d["gain_factors"]:
            movie, center = make_movie(d, event["duration_frames"], event["peak_signal_photons"], gain, noise)
            rows.append(tracked_event_row(event, gain, movie, center, d, noise_hash))
    summaries = [summarize([r for r in rows if r["gain"] == gain], gain) for gain in d["gain_factors"]]

    # Registered controls: five all-background/no-event movies sharing the same
    # per-seed noise model, and one noise-free, all-frames-above-floor positive.
    negative = []
    for seed in d["seeds"]:
        rng = np.random.default_rng(seed * 100000 + 777)
        noise = rng.normal(0.0, d["read_noise_sd"], size=(d["frames"], d["height_width_px"], d["height_width_px"]))
        movie, _ = make_movie(d, d["latent_durations_frames"][0], 0.0, 0.0, noise, present=False)
        meta = {"psf_sigma_nm": d["psf_sigma_px"], "nm_per_px": 1.0, "channels": ["coat"]}
        tracks, dets = run_tracking(movie, meta, gate_px=4, max_gap=0, min_track_len=4)
        negative.append({"seed": seed, "retained_track_count": len(tracks),
                         "retained_point_count": sum(len(t.frames) for t in tracks),
                         "raw_detection_count_all_lengths": sum(len(x) for x in dets)})
    high_noise = np.zeros((d["frames"], d["height_width_px"], d["height_width_px"]), dtype=float)
    high_duration, high_peak = 48, 1000.0
    high_movie, high_center = make_movie(d, high_duration, high_peak, 1.0, high_noise)
    high_event = {"event_id": "high_snr_noisefree", "seed": None, "duration_frames": high_duration,
                  "peak_signal_photons": high_peak}
    high_row = tracked_event_row(high_event, 1.0, high_movie, high_center, d, hashlib.sha256(high_noise.tobytes()).hexdigest())

    # This is intentionally a post-tracking arithmetic comparator only.  Its IDs
    # and supports are copied from gain=1; values are rescaled afterward.
    base = {r["event_id"]: r for r in rows if r["gain"] == 1.0}
    comparator = []
    for gain in [0.6, 0.3]:
        for event_id, b in base.items():
            comparator.append({"event_id": event_id, "gain": gain,
                               "retained_track_count": b["retained_track_count"],
                               "retained_track_supports": b["retained_track_supports"],
                               "matched_support": b["union_matched_frames"],
                               "operation": "background + gain * (gain1_extracted_raw - background); no retracking"})
    checks = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "registered_run_count": len(rows), "control_run_count": len(negative) + 1,
        "total_movie_runs": len(rows) + len(negative) + 1,
        "fixed_event_count_per_gain": {str(g): sum(r["gain"] == g for r in rows) for g in d["gain_factors"]},
        "fixed_unconditional_truth_frame_denominator_per_gain": {str(g): sum(r["unconditional_coverage_denominator"] for r in rows if r["gain"] == g) for g in d["gain_factors"]},
        "paired_noise_hashes_identical_within_event": all(len({r["noise_sha256"] for r in rows if r["event_id"] == e[0]["event_id"]}) == 1 for e in events),
        "negative_control": negative,
        "high_snr_noisefree_control": high_row,
        "post_tracking_comparator": comparator,
    }
    checks["assertions"] = {
        "registered_runs_are_135": checks["registered_run_count"] == 135,
        "total_runs_within_150": checks["total_movie_runs"] <= 150,
        "each_gain_has_45_events": all(n == 45 for n in checks["fixed_event_count_per_gain"].values()),
        "each_gain_has_1440_unconditional_truth_frames": all(n == 1440 for n in checks["fixed_unconditional_truth_frame_denominator_per_gain"].values()),
        "paired_noise": checks["paired_noise_hashes_identical_within_event"],
        "posttracking_rescale_keeps_gain1_supports": all(
            c["retained_track_supports"] == base[c["event_id"]]["retained_track_supports"]
            for c in comparator),
        "negative_has_no_retained_tracks": all(x["retained_track_count"] == 0 for x in negative),
        "high_snr_all_truth_frames_eligible": high_row["conditional_coverage_denominator"] == high_duration,
        "high_snr_full_matched_union": high_row["n_union_matched_frames"] == high_duration,
        "high_snr_one_unfragmented_track": high_row["n_fragments"] == 1 and high_row["observed_span_frames_union"] == high_duration,
        "coverage_numerators_are_union_counts": all(r["unconditional_coverage_numerator"] == r["n_union_matched_frames"] for r in rows),
        "conditional_is_same_eligible_subset": all(r["conditional_coverage_numerator"] <= r["conditional_coverage_denominator"] for r in rows),
    }
    if not all(checks["assertions"].values()):
        raise RuntimeError("frozen-design validation failed: " + json.dumps(checks["assertions"], sort_keys=True))
    results = {
        "task_id": design["task_id"], "attempt_number": design["attempt_number"],
        "started_at_utc": started.isoformat(), "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "fixed synthetic observation benchmark; no empirical data, physical inverse, tracker edit, or parameter retuning",
        "input_design": design, "input_design_sha256": sha256_path(DESIGN_PATH),
        "tracker_sha256": sha256_path(TRACKER_PATH),
        "runtime": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "matching_definition": "retained tracker point is matched only if within 3 px of center and within the event presence interval; union is used across fragments",
        "span_definition": "inclusive first-to-last matched frame in the union across fragments; null for missing events",
        "per_event_rows": rows, "gain_summaries": summaries,
        "post_tracking_rescale_definition": "copy gain=1 retained supports/IDs and rescale extracted intensities after tracking only; comparator cannot change supports",
    }
    RESULT_PATH.write_text(json.dumps(results, indent=2) + "\n")
    CHECK_PATH.write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"results": str(RESULT_PATH), "checks": str(CHECK_PATH), "summaries": summaries}, indent=2))


if __name__ == "__main__":
    main()
