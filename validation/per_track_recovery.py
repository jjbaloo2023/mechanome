"""
per_track_recovery.py — curvo's Bayesian inverse, run per structure across a field.

This is where the front end (detect+track) meets the validated physics recovery.
For each RECOVERED track (from tracking.run_tracking — genuine end-to-end, not GT
positions), we crop a per-pit ROI following the track over its detected frames and
run the full guarded analyze() endpoint: perception (pixels->geometry) -> Bayesian
inverse (geometry->force) -> mechanism discrimination, with the anti-force-astrology
and plateau guards intact. Each track is matched to its nearest GT structure only to
label truth for scoring.

The output is the multi-structure analog of the single-CCP recovery gate: a grid of
recovered-vs-true force across a crowded field, each point flagged identified or
UNDETERMINED. The honest expectation, seen already in spot checks: recovery in a
crowd is HARDER than the clean single-pit gate (neighbor PSF tails add noise, tracked
lifetimes are partial), so identifiability drops and the guardrail refuses more
often. Quantifying that bias/coverage degradation IS the deliverable.
"""
from __future__ import annotations

import dataclasses
import json
import time
import numpy as np

from curvo import analyze as az


def recover_track(movie, meta, track, roi=32, nlive=150, seed=0):
    """Crop a per-pit ROI following one track and run the guarded analyze()."""
    H, W = movie.shape[2:]
    f0, f1 = track.frames[0], track.frames[-1] + 1
    # follow the track: use its median position for a stable crop box
    cx, cy = int(round(track.x_med)), int(round(track.y_med))
    y0, x0 = max(0, cy - roi), max(0, cx - roi)
    y1, x1 = min(H, cy + roi), min(W, cx + roi)
    sub = movie[f0:f1, :, y0:y1, x0:x1]
    if sub.shape[0] < 6:
        return None                      # too short to recover a trajectory
    res = az.analyze(sub, nm_per_px=meta["nm_per_px"], psf_sigma_nm=meta["psf_sigma_nm"],
                     peak_photons=meta["peak_photons"], channels=meta["channels"],
                     nlive=nlive, seed=seed)
    return res


def recover_field(movie, meta, tracks, gt_tracks, roi=32, nlive=150, seed=0,
                  match_radius_px=20, verbose=True):
    """Recover force for every track; match to GT for truth; return per-structure rows."""
    rows = []
    for t in tracks:
        g = min(gt_tracks, key=lambda gg: np.hypot(t.x_med - gg["x_px"], t.y_med - gg["y_px"]))
        if np.hypot(t.x_med - g["x_px"], t.y_med - g["y_px"]) > match_radius_px:
            continue
        t0 = time.time()
        res = recover_track(movie, meta, t, roi=roi, nlive=nlive, seed=seed)
        if res is None:
            continue
        af = res["forces"].get("active_force_max", {})
        rows.append(dict(
            sid=g["sid"], true_force=g["active_force_pN"],
            point_estimate=af.get("point_estimate"),
            posterior_median=af.get("posterior_median"),
            ci68=af.get("ci68"), identified=bool(af.get("identified")),
            favored=res.get("favored_mechanism", {}).get("favored"),
            rec_lifetime=len(t.frames), secs=round(time.time() - t0, 1)))
        if verbose:
            r = rows[-1]
            print(f"  s{r['sid']}: truth={r['true_force']:.0f}pN "
                  f"median={r['posterior_median']:.1f} "
                  f"{'IDENTIFIED pe=%.1f' % r['point_estimate'] if r['identified'] else 'UNDETERMINED'} "
                  f"({r['secs']}s)")
    return rows


def recover_oracle(movie, meta, gt_tracks, roi=32, nlive=200, seed=0, verbose=True):
    """Recovery given a PERFECT track: crop each GT structure over its full lifetime.

    This isolates the physics inverse's capability in a crowded field from tracking
    fragmentation. Comparing this to recover_field (recovered tracks) separates the
    two failure modes: how much of the end-to-end degradation is the inverse vs the
    tracker. The crop follows the GT (x,y) exactly and spans birth..death."""
    import time
    H, W = movie.shape[2:]
    rows = []
    for g in gt_tracks:
        cx, cy = int(g["x_px"]), int(g["y_px"])
        y0, x0 = max(0, cy - roi), max(0, cx - roi)
        y1, x1 = min(H, cy + roi), min(W, cx + roi)
        sub = movie[g["birth"]:g["death"], :, y0:y1, x0:x1]
        t0 = time.time()
        res = az.analyze(sub, nm_per_px=meta["nm_per_px"], psf_sigma_nm=meta["psf_sigma_nm"],
                         peak_photons=meta["peak_photons"], channels=meta["channels"],
                         nlive=nlive, seed=seed)
        af = res["forces"].get("active_force_max", {})
        rows.append(dict(
            sid=g["sid"], true_force=g["active_force_pN"],
            point_estimate=af.get("point_estimate"), posterior_median=af.get("posterior_median"),
            ci68=af.get("ci68"), identified=bool(af.get("identified")),
            favored=res.get("favored_mechanism", {}).get("favored"),
            rec_lifetime=g["death"] - g["birth"], secs=round(time.time() - t0, 1)))
        if verbose:
            r = rows[-1]
            print(f"  s{r['sid']}: truth={r['true_force']:.0f}pN median={r['posterior_median']:.1f} "
                  f"{'IDENTIFIED pe=%.1f' % r['point_estimate'] if r['identified'] else 'UNDETERMINED'} "
                  f"({r['secs']}s)")
    return rows


def recovery_summary(rows):
    """Aggregate bias/coverage over the field, on the IDENTIFIED subset."""
    ident = [r for r in rows if r["identified"] and r["point_estimate"] is not None]
    n = len(rows); ni = len(ident)
    if ni:
        rel_bias = float(np.mean([(r["point_estimate"] - r["true_force"]) / r["true_force"]
                                  for r in ident]))
        cov = float(np.mean([r["ci68"][0] <= r["true_force"] <= r["ci68"][1]
                             for r in ident if r["ci68"]]))
    else:
        rel_bias = cov = None
    # median-based recovery over ALL tracks (even undetermined) for a trend line
    med_pairs = [(r["true_force"], r["posterior_median"]) for r in rows
                 if r["posterior_median"] is not None]
    return dict(n_tracks=n, n_identified=ni, identified_frac=ni / n if n else 0.0,
                rel_bias_identified=rel_bias, coverage68_identified=cov,
                n_median_pairs=len(med_pairs))


if __name__ == "__main__":
    from validation.field_movie import generate_field
    from validation.tracking import run_tracking
    movie, gts, meta = generate_field(n_struct=8, seed=0)
    gt_json = [dataclasses.asdict(g) for g in gts]
    tracks, _ = run_tracking(movie, meta)
    rows = recover_field(movie, meta, tracks, gt_json)
    summ = recovery_summary(rows)
    print("summary:", summ)
    json.dump(dict(rows=rows, summary=summ), open("outputs/per_track_recovery.json", "w"), indent=2)
