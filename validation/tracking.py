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
    """Track-level recovery + detection P/R/F1 on the DETECTABLE subset.

    match_radius_px ~ 2*PSF: the LoG locks onto the coat's brightness centroid,
    which sits ~1 PSF off the pit's geometric (GT) center, so a one-PSF match radius
    would split one structure into an FP+FN pair. PSF sigma is 9 px here, so 2*PSF is
    18 px; 20 px rounds that up for a small margin and counts one coat detection as
    one structure.

    Recall is reported over DETECTABLE presence only: a pit whose coat has not yet
    assembled above `coat_floor` (its first ~7 nascent frames) is below the optical
    detection limit and cannot be found — counting those as misses would penalize the
    detector for a physical fact, not a failure. When `movie` is given, GT presence
    is gated on the coat peak; otherwise all GT-present frames count (a lower bound)."""
    T = meta["T_field"]
    coat_idx = meta["channels"].index("coat") if movie is not None else None
    # build GT presence: {frame: [(sid, x, y, detectable)]}
    gt_by_frame = {f: [] for f in range(T)}
    for g in gt_tracks:
        for f in range(g["birth"], g["death"]):
            det = True
            if movie is not None:
                y, x = int(g["y_px"]), int(g["x_px"])
                peak = movie[f, coat_idx, max(0, y - 8):y + 8, max(0, x - 8):x + 8].max()
                det = bool(peak >= coat_floor)
            gt_by_frame[f].append((g["sid"], g["x_px"], g["y_px"], det))
    # detection P/R on the detectable subset: match each track point to nearest GT
    tp = fp = fn = 0
    for f in range(T):
        preds = [(t.xs[t.frames.index(f)], t.ys[t.frames.index(f)]) for t in tracks if f in t.frames]
        gts = gt_by_frame[f]
        detectable_idx = [gi for gi, g in enumerate(gts) if g[3]]
        used = set()
        for (px, py) in preds:
            best, bestd = None, match_radius_px + 1
            for gi, (sid, gx, gy, det) in enumerate(gts):
                if gi in used:
                    continue
                d = np.hypot(px - gx, py - gy)
                if d < bestd:
                    best, bestd = gi, d
            if best is not None:
                tp += 1; used.add(best)
            else:
                fp += 1
        fn += sum(1 for gi in detectable_idx if gi not in used)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

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
    detected_frac = len(matched_gt) / len(gt_tracks) if gt_tracks else 0.0
    return dict(precision=prec, recall=rec, f1=f1, tp=tp, fp=fp, fn=fn,
                n_gt=len(gt_tracks), n_tracks=len(tracks),
                gt_structures_detected=len(matched_gt),
                gt_detected_frac=detected_frac, lifetime_pairs=lifetime_pairs)


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
            rows.append(dict(axis=nkind, value=v, f1=val["f1"], precision=val["precision"],
                             recall=val["recall"], detected_frac=val["gt_detected_frac"],
                             n_gt=val["n_gt"], n_tracks=val["n_tracks"]))
    return rows


if __name__ == "__main__":
    from validation.field_movie import generate_field, tracks_to_json
    movie, gts, meta = generate_field(n_struct=8, seed=0)
    gt_json = [dataclasses.asdict(g) for g in gts]
    tracks, dets = run_tracking(movie, meta)
    val = validate_tracking(tracks, gt_json, meta, movie=movie)
    print(f"detection: P={val['precision']:.2f} R={val['recall']:.2f} F1={val['f1']:.2f}")
    print(f"GT structures detected: {val['gt_structures_detected']}/{val['n_gt']} "
          f"(recovered {val['n_tracks']} tracks)")
    for lp in val["lifetime_pairs"]:
        print(f"  s{lp['sid']}: gt_life={lp['gt_life']} rec_life={lp['rec_life']} "
              f"completeness={lp['completeness']:.0%}")
    json.dump(val, open("outputs/tracking_validation.json", "w"), indent=2)
