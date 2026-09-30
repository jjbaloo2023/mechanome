"""
tracking.py — detect + link structures in a crowded time-lapse.

Front end for the physics recovery: turn a field movie [T,C,H,W] into per-structure
TRACKS (position over time + lifetime) that Step 5 feeds to curvo's inverse.

Detection: scale-matched Laplacian-of-Gaussian blob detection on the coat channel
(the coat is the brightest, most compact marker of a pit). LoG responds to bright
compact spots at a chosen scale; we set that scale to the coat's PSF-broadened size.
No scikit-image dependency — scipy.ndimage only.

Linking: greedy nearest-neighbor association across frames with a gating radius
(max plausible per-frame displacement) and a track-continuity rule that tolerates a
short gap (a missed detection mid-lifetime) before closing a track. Births and
deaths fall out naturally as track starts/ends.

Validation (against field_movie ground truth): detection precision / recall / F1,
track purity (fraction of a track's points matched to one GT structure) and
completeness (fraction of a GT lifetime covered), and recovered-vs-true lifetime.
"""
from __future__ import annotations

import dataclasses
import json
import numpy as np
from scipy import ndimage as ndi


def detect_blobs(frame_coat, psf_sigma_px, min_peak_photons=25.0,
                 min_rel_intensity=0.30, min_distance_px=10):
    """LoG blob detection on one coat-channel frame. Returns list of (y, x, score).

    LoG at scale sigma = psf_sigma_px peaks at bright compact spots of that scale.
    Two gates, both required:
      * ABSOLUTE: the raw coat intensity at the peak must exceed min_peak_photons.
        This is the load-bearing gate — without it, a structure-FREE frame (whose
        max is just read/shot noise, ~8 photons) fires dozens of spurious peaks
        because a relative threshold has no absolute reference. A real coat peak is
        ~90-135 photons, so a floor at 25 cleanly rejects empty frames.
      * RELATIVE: LoG response > min_rel_intensity * (max LoG this frame), to reject
        weak secondary maxima once a real structure sets the scale."""
    img = np.asarray(frame_coat, float)
    if img.max() <= min_peak_photons:
        return []
    sig = max(1.0, psf_sigma_px)
    log = -(sig ** 2) * ndi.gaussian_laplace(img, sigma=sig)   # bright spot -> positive
    log[log < 0] = 0
    if log.max() <= 0:
        return []
    fp = np.ones((int(2 * min_distance_px + 1),) * 2)
    mx = ndi.maximum_filter(log, footprint=fp)
    peaks = (log == mx) & (log > min_rel_intensity * log.max())
    ys, xs = np.where(peaks)
    # apply the absolute raw-intensity gate at each candidate peak
    out = []
    for y, x in zip(ys, xs):
        if img[y, x] >= min_peak_photons:
            out.append((float(y), float(x), float(log[y, x])))
    return out


@dataclasses.dataclass
class Track:
    tid: int
    frames: list          # frame indices
    ys: list
    xs: list

    @property
    def birth(self): return self.frames[0]
    @property
    def death(self): return self.frames[-1] + 1
    @property
    def x_med(self): return float(np.median(self.xs))
    @property
    def y_med(self): return float(np.median(self.ys))
    @property
    def lifetime(self): return self.death - self.birth


def link_tracks(detections_per_frame, gate_px=14, max_gap=2):
    """Greedy nearest-neighbor linking with a gating radius and gap tolerance."""
    tracks = []
    active = []   # dict(tid, last_frame, y, x, frames, ys, xs)
    next_id = 0
    for f, dets in enumerate(detections_per_frame):
        unmatched = list(range(len(dets)))
        # try to extend active tracks (closest detection within gate)
        for tr in active:
            if not unmatched:
                break
            best, bestd = None, gate_px + 1
            for di in unmatched:
                y, x, _ = dets[di]
                d = np.hypot(y - tr["y"], x - tr["x"])
                if d < bestd:
                    best, bestd = di, d
            if best is not None:
                y, x, _ = dets[best]
                tr.update(y=y, x=x, last_frame=f)
                tr["frames"].append(f); tr["ys"].append(y); tr["xs"].append(x)
                unmatched.remove(best)
        # close tracks that have exceeded the gap tolerance
        still = []
        for tr in active:
            if f - tr["last_frame"] > max_gap:
                tracks.append(Track(tr["tid"], tr["frames"], tr["ys"], tr["xs"]))
            else:
                still.append(tr)
        active = still
        # start new tracks from unmatched detections
        for di in unmatched:
            y, x, _ = dets[di]
            active.append(dict(tid=next_id, last_frame=f, y=y, x=x,
                               frames=[f], ys=[y], xs=[x]))
            next_id += 1
    for tr in active:
        tracks.append(Track(tr["tid"], tr["frames"], tr["ys"], tr["xs"]))
    return tracks


def run_tracking(movie, meta, gate_px=20, max_gap=3, min_track_len=4):
    """Detect on the coat channel every frame, link, drop too-short tracks."""
    psf_px = meta["psf_sigma_nm"] / meta["nm_per_px"]
    coat_idx = meta["channels"].index("coat")
    dets = [detect_blobs(movie[f, coat_idx], psf_px) for f in range(movie.shape[0])]
    tracks = link_tracks(dets, gate_px=gate_px, max_gap=max_gap)
    tracks = [t for t in tracks if len(t.frames) >= min_track_len]
    return tracks, dets


# ------------------------------------------------------- validation ----------
def validate_tracking(tracks, gt_tracks, meta, match_radius_px=20,
                      coat_floor=25.0, movie=None):
    """Validate retained track points under explicit full and eligible cohorts.

    ``all_presence`` scores every GT-present frame.  ``detectable`` restricts
    TP/FN to the observed-image eligible subset: with a movie, the local coat
    peak is at least ``coat_floor``; without a movie every present frame is
    eligible and the fallback is labeled in the returned contract.  Both blocks
    use one one-to-one per-frame matching pass.  Predictions matched to
    ineligible GT are ignored by the conditional precision denominator rather
    than relabeled false positives.  Explicit rates are ``None`` when their
    denominator is zero; legacy top-level scalar rates retain the prior 0.0
    fallback and now represent all-presence metrics.

    ``lifetime_pairs`` remains a legacy positional diagnostic: it is not a
    complete-event or continuous-lifetime score.  The event counts below use
    framewise matches, so missed and wholly ineligible events remain visible.
    """
    T = meta["T_field"]
    coat_idx = meta["channels"].index("coat") if movie is not None else None
    eligibility_source = "movie_local_coat_peak_ge_floor" if movie is not None else "all_presence_no_movie_fallback"
    # Build GT presence: {frame: [(sid, x, y, eligible)]}.
    gt_by_frame = {f: [] for f in range(T)}
    for g in gt_tracks:
        for f in range(g["birth"], g["death"]):
            eligible = True
            if movie is not None:
                y, x = int(g["y_px"]), int(g["x_px"])
                peak = movie[f, coat_idx, max(0, y - 8):y + 8, max(0, x - 8):x + 8].max()
                eligible = bool(peak >= coat_floor)
            gt_by_frame[f].append((g["sid"], g["x_px"], g["y_px"], eligible))
    eligible_event_ids = {sid for frame_gts in gt_by_frame.values()
                          for sid, _, _, eligible in frame_gts if eligible}

    all_tp = all_fp = 0
    eligible_tp = eligible_fp = ignored_ineligible_matches = 0
    all_presence_total = eligible_presence_total = 0
    ever_matched_all, ever_matched_eligible = set(), set()
    for f in range(T):
        preds = [(t.xs[t.frames.index(f)], t.ys[t.frames.index(f)]) for t in tracks if f in t.frames]
        gts = gt_by_frame[f]
        all_presence_total += len(gts)
        eligible_presence_total += sum(g[3] for g in gts)
        used = set()
        for (px, py) in preds:
            best, bestd = None, float("inf")
            for gi, (sid, gx, gy, det) in enumerate(gts):
                if gi in used:
                    continue
                d = np.hypot(px - gx, py - gy)
                # Strictly closer wins; input order resolves an exact distance tie.
                if d <= match_radius_px and (best is None or d < bestd):
                    best, bestd = gi, d
            if best is not None:
                sid, _, _, eligible = gts[best]
                used.add(best)
                all_tp += 1
                ever_matched_all.add(sid)
                if eligible:
                    eligible_tp += 1
                    ever_matched_eligible.add(sid)
                else:
                    ignored_ineligible_matches += 1
            else:
                all_fp += 1
                eligible_fp += 1
    all_fn = all_presence_total - all_tp
    eligible_fn = eligible_presence_total - eligible_tp

    def metric_block(tp, fp, fn, extra=None):
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        f1_denominator = 2 * tp + fp + fn
        f1 = 2 * tp / f1_denominator if f1_denominator else None
        out = dict(tp=tp, fp=fp, fn=fn, precision=precision, recall=recall, f1=f1)
        if extra:
            out.update(extra)
        return out

    all_presence = metric_block(all_tp, all_fp, all_fn, dict(
        gt_presence_frames=all_presence_total,
        gt_events_total=len(gt_tracks),
        gt_events_ever_matched=len(ever_matched_all),
        gt_event_detected_frac=(len(ever_matched_all) / len(gt_tracks) if gt_tracks else None),
    ))
    detectable = metric_block(eligible_tp, eligible_fp, eligible_fn, dict(
        eligible_gt_presence_frames=eligible_presence_total,
        eligible_gt_events_total=len(eligible_event_ids),
        eligible_gt_events_ever_matched=len(ever_matched_eligible),
        ignored_ineligible_matches=ignored_ineligible_matches,
        eligibility_source=eligibility_source,
        coat_floor=coat_floor if movie is not None else None,
    ))

    # per-GT-structure: assign each recovered track to the GT it best overlaps
    lifetime_pairs = []
    matched_gt = {}
    for t in tracks:
        # which GT is this track closest to (by median position)?
        best, bestd = None, 1e9
        for g in gt_tracks:
            d = np.hypot(t.x_med - g["x_px"], t.y_med - g["y_px"])
            if d < bestd:
                best, bestd = g, d
        if best is not None and bestd <= match_radius_px:
            matched_gt.setdefault(best["sid"], []).append((t, bestd))
    for g in gt_tracks:
        cand = matched_gt.get(g["sid"], [])
        if not cand:
            continue
        t = min(cand, key=lambda c: c[1])[0]
        gt_life = g["death"] - g["birth"]
        completeness = len(t.frames) / gt_life
        lifetime_pairs.append(dict(sid=g["sid"], gt_life=gt_life,
                                   rec_life=t.lifetime, completeness=completeness,
                                   force=g["active_force_pN"]))
    # Compatibility keys are all-presence values.  Legacy scalar rates use 0.0
    # only where an explicit block reports an undefined (zero-denominator) rate.
    zero = lambda value: 0.0 if value is None else value
    return dict(metric_contract_version="tracking-validation-v2",
                precision=zero(all_presence["precision"]), recall=zero(all_presence["recall"]),
                f1=zero(all_presence["f1"]), tp=all_tp, fp=all_fp, fn=all_fn,
                n_gt=len(gt_tracks), n_tracks=len(tracks),
                gt_structures_detected=len(ever_matched_all),
                gt_detected_frac=zero(all_presence["gt_event_detected_frac"]),
                all_presence=all_presence, detectable=detectable,
                lifetime_pairs=lifetime_pairs,
                lifetime_pairs_scope="legacy positional median-track diagnostic")


def tracking_sweep(crowding=(4, 8, 12), photons=(80, 220, 400), seed0=0):
    """F1 + detected-fraction vs crowding (n_struct) and SNR (peak_photons)."""
    from validation.field_movie import generate_field
    rows = []
    for nkind, vals, key in [("crowding", crowding, "n_struct"),
                             ("photons", photons, "peak_photons")]:
        for v in vals:
            kw = dict(n_struct=8, peak_photons=220, seed=seed0)
            kw[key] = v
            movie, gts, meta = generate_field(**kw)
            gt_json = [dataclasses.asdict(g) for g in gts]
            trks, _ = run_tracking(movie, meta)
            val = validate_tracking(trks, gt_json, meta, movie=movie)
            rows.append(dict(axis=nkind, value=v, metric_contract_version=val["metric_contract_version"],
                             all_presence_f1=val["all_presence"]["f1"],
                             all_presence_precision=val["all_presence"]["precision"],
                             all_presence_recall=val["all_presence"]["recall"],
                             detectable_f1=val["detectable"]["f1"],
                             detectable_precision=val["detectable"]["precision"],
                             detectable_recall=val["detectable"]["recall"],
                             all_presence_gt_event_detected_frac=val["all_presence"]["gt_event_detected_frac"],
                             n_gt=val["n_gt"], n_tracks=val["n_tracks"]))
    return rows


if __name__ == "__main__":
    from validation.field_movie import generate_field
    movie, gts, meta = generate_field(n_struct=8, seed=0)
    gt_json = [dataclasses.asdict(g) for g in gts]
    tracks, dets = run_tracking(movie, meta)
    val = validate_tracking(tracks, gt_json, meta, movie=movie)
    print(f"all-presence detection: P={val['precision']:.2f} R={val['recall']:.2f} F1={val['f1']:.2f}")
    print(f"GT structures detected: {val['gt_structures_detected']}/{val['n_gt']} "
          f"(recovered {val['n_tracks']} tracks)")
    print("Legacy positional lifetime diagnostic:")
    for lp in val["lifetime_pairs"]:
        print(f"  s{lp['sid']}: gt_life={lp['gt_life']} rec_life={lp['rec_life']} "
              f"completeness={lp['completeness']:.0%}")
    json.dump(val, open("outputs/tracking_validation.json", "w"), indent=2)
