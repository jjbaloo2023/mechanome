"""Audit saved rows and perform numeric fixed-center post-tracking rescaling.
No detector/tracker call. Center sampling is an explicitly declared estimator
for the known stationary synthetic spots, not a claim about detector-pixel
photometry: the original result did not preserve detected y/x coordinates.
"""
from pathlib import Path
import datetime, hashlib, json
import numpy as np

R = Path(__file__).resolve().parent

def main():
    p = R / "synthetic_dimming_results.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    d = data["input_design"]["fixed_design"]
    rows = data["per_event_rows"]
    assertions = []
    for row in rows:
        length = row["duration_frames"]
        truth = set(range(d["birth_frame"], d["birth_frame"] + length))
        expected_eligible = {d["birth_frame"] + i for i in range(length)
            if d["background_photons"] + row["gain"] * row["peak_signal_photons"] * np.sin(np.pi * (i + .5) / length) >= 25}
        matched = set(row["union_matched_frames"])
        assert matched <= truth
        assert set(row["truth_frames"]) == truth
        assert set(row["eligible_truth_frames_noiseless_center_ge_25"]) == expected_eligible
        assert row["conditional_coverage_numerator"] == len(matched & expected_eligible)
        assert row["conditional_coverage_denominator"] == len(expected_eligible)
        assert row["unconditional_coverage_numerator"] == len(matched)
        assert row["unconditional_coverage_denominator"] == length
        assert row["observed_span_frames_union"] == (max(matched)-min(matched)+1 if matched else None)
    audits = []
    for summary in data["gain_summaries"]:
        rr = [x for x in rows if x["gain"] == summary["gain"]]
        un = sum(len(x["union_matched_frames"]) for x in rr)
        cond = sum(len(set(x["union_matched_frames"]) & set(x["eligible_truth_frames_noiseless_center_ge_25"])) for x in rr)
        den = sum(len(x["eligible_truth_frames_noiseless_center_ge_25"]) for x in rr)
        assert len(rr) == 45 and sum(x["duration_frames"] for x in rr) == 1440
        assert summary["unconditional_matched_frames"] == un
        assert summary["conditional_matched_frames"] == cond
        assert summary["conditional_eligible_truth_frames"] == den
        assert summary["events_ever_matched"] == sum(bool(x["union_matched_frames"]) for x in rr)
        audits.append({"gain": summary["gain"], "all_frames_matched": un, "all_frames": 1440,
            "eligible_frames_matched": cond, "eligible_frames": den})
    transforms = []
    for row in rows:
        if row["gain"] != 1.0:
            continue
        length, peak = row["duration_frames"], row["peak_signal_photons"]
        rng = np.random.default_rng(row["seed"] * 100000 + length * 1000 + peak)
        noise = rng.normal(0, d["read_noise_sd"], (d["frames"], d["height_width_px"], d["height_width_px"]))
        assert hashlib.sha256(noise.tobytes()).hexdigest() == row["noise_sha256"]
        cy, cx = d["center_yx_px"]
        frames = row["union_matched_frames"]
        raw = np.array([d["background_photons"] + noise[f,cy,cx] + peak*np.sin(np.pi*(f-d["birth_frame"]+.5)/length) for f in frames])
        for gain in [0.6, 0.3]:
            transformed = d["background_photons"] + gain*(raw-d["background_photons"])
            assert np.allclose((transformed-d["background_photons"])/gain, raw-d["background_photons"], rtol=1e-12, atol=1e-12)
            transforms.append({"event_id": row["event_id"], "gain": gain, "frames": frames,
                "baseline_raw_center_pixel": raw.tolist(), "rescaled_center_pixel": transformed.tolist(),
                "retained_track_supports": row["retained_track_supports"]})
    out = {"checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "results_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "method": "Reconstruct identical baseline noise; sample raw pixel at fixed known center on saved gain1 matched frames; apply background+gain*(raw-background). This estimator was specified after the main run to replace a symbolic comparator; it is not detector-coordinate photometry.",
        "new_tracking_calls": 0, "new_parameter_sweep": False,
        "saved_rows_independently_checked": len(rows), "conditional_and_unconditional_denominators_checked": True,
        "gain_audits": audits, "numeric_transform_count": len(transforms),
        "baseline_noise_hashes_verified": True, "numeric_rescale_inverse_check": True,
        "numeric_transforms": transforms}
    (R/"synthetic_dimming_reanalysis.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="numeric_transforms"}))

if __name__ == "__main__":
    main()
