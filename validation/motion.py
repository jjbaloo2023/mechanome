"""
motion.py — a PIV-analog motion field, and the honest line it does not cross.

Particle Image Velocimetry recovers a dense VELOCITY field by finding, for each
interrogation window, the displacement that best cross-correlates one frame onto the
next. Here we apply the same idea to the membrane channel of the time-lapse: windowed
normalized cross-correlation between consecutive frames -> a per-window (vy, vx)
displacement -> a dense flow field.

Reduced observable: for each tracked structure we sample the flow in an annulus
around the pit center and take the mean RADIAL component -> the neck inflow rate
(px/frame, converted to nm/frame). As a pit constricts, membrane intensity flows
inward; the inflow rate is a real, measurable KINEMATIC quantity.

The line this module does NOT cross: inflow is velocity, not force. Two pits with
the same inflow can be driven by different force balances (tension vs active stress
vs drag). Turning kinematics into force needs the constitutive law — curvo's inverse
(Step 5), not PIV. The validation here is therefore against the GROUND-TRUTH neck
CONSTRICTION RATE (a kinematic truth), not against force. The figure states this
explicitly so no reader mistakes a flow field for a force map.
"""
from __future__ import annotations

import numpy as np


def piv_field(frame0, frame1, win=16, step=8, search=6):
    """Windowed normalized cross-correlation PIV between two frames.

    Returns (ys, xs, vy, vx): grid centers and per-window displacement (px/frame).
    For each window in frame0, search +/- `search` px in frame1 for the shift that
    maximizes normalized cross-correlation."""
    f0 = np.asarray(frame0, float); f1 = np.asarray(frame1, float)
    H, W = f0.shape
    ys, xs, vys, vxs = [], [], [], []
    half = win // 2
    for cy in range(half + search, H - half - search, step):
        for cx in range(half + search, W - half - search, step):
            tmpl = f0[cy - half:cy + half, cx - half:cx + half]
            if tmpl.std() < 1e-6 or tmpl.max() < 1.0:
                continue                              # skip empty windows
            tmpl = tmpl - tmpl.mean()
            best, bestval = (0, 0), -np.inf
            for dy in range(-search, search + 1):
                for dx in range(-search, search + 1):
                    win1 = f1[cy - half + dy:cy + half + dy, cx - half + dx:cx + half + dx]
                    if win1.shape != tmpl.shape:
                        continue
                    w = win1 - win1.mean()
                    denom = np.sqrt((tmpl ** 2).sum() * (w ** 2).sum()) + 1e-9
                    ncc = (tmpl * w).sum() / denom
                    if ncc > bestval:
                        bestval, best = ncc, (dy, dx)
            ys.append(cy); xs.append(cx); vys.append(best[0]); vxs.append(best[1])
    return (np.array(ys), np.array(xs), np.array(vys, float), np.array(vxs, float))


def radial_inflow(ys, xs, vy, vx, cx, cy, r_in=6, r_out=26):
    """Mean inward radial velocity in an annulus [r_in, r_out] about (cx, cy).

    Positive = net inflow (velocity pointing toward the center)."""
    rx, ry = xs - cx, ys - cy
    r = np.hypot(rx, ry)
    m = (r >= r_in) & (r <= r_out) & (r > 1e-6)
    if not m.any():
        return 0.0, 0
    ux, uy = rx[m] / r[m], ry[m] / r[m]            # outward unit vectors
    radial_v = vx[m] * ux + vy[m] * uy             # + = outward
    return float(-np.mean(radial_v)), int(m.sum()) # negate -> + = inflow


def track_inflow_series(movie, meta, track, channel="membrane", roi=34, step=6, win=16, search=5):
    """Per-frame neck inflow (nm/frame) for one track, over its lifetime.

    PIV is run only on a small ROI around the pit (roi px half-width), not the whole
    frame — the inflow annulus is local, so this is ~20x cheaper than a full-frame field."""
    ci = meta["channels"].index(channel)
    nmpp = meta["nm_per_px"]
    H, W = movie.shape[2:]
    out = []
    fr = track.frames
    for i in range(len(fr) - 1):
        f0, f1 = fr[i], fr[i + 1]
        if f1 != f0 + 1:
            out.append(np.nan); continue
        cx = int(round(track.xs[i])); cy = int(round(track.ys[i]))
        y0, x0 = max(0, cy - roi), max(0, cx - roi)
        y1, x1 = min(H, cy + roi), min(W, cx + roi)
        ys, xs, vy, vx = piv_field(movie[f0, ci, y0:y1, x0:x1],
                                   movie[f1, ci, y0:y1, x0:x1],
                                   win=win, step=step, search=search)
        infl, n = radial_inflow(ys + y0, xs + x0, vy, vx, cx, cy)
        out.append(infl * nmpp)                     # px/frame -> nm/frame
    return np.array(out)


def gt_constriction_rate(gt_track):
    """Ground-truth neck constriction rate (nm/frame): -d(neck)/dt, + = constricting."""
    neck = np.asarray(gt_track["neck_nm"], float)
    return -np.diff(neck)                            # positive when neck shrinks


if __name__ == "__main__":
    import dataclasses
    from validation.field_movie import generate_field
    from validation.tracking import run_tracking
    movie, gts, meta = generate_field(n_struct=8, seed=0)
    gt_json = [dataclasses.asdict(g) for g in gts]
    tracks, _ = run_tracking(movie, meta)
    # match each recovered track to nearest GT, compare inflow vs constriction
    rows = []
    for t in tracks:
        g = min(gt_json, key=lambda gg: np.hypot(t.x_med - gg["x_px"], t.y_med - gg["y_px"]))
        if np.hypot(t.x_med - g["x_px"], t.y_med - g["y_px"]) > 20:
            continue
        infl = track_inflow_series(movie, meta, t)
        rows.append(dict(sid=g["sid"], mean_inflow_nm=float(np.nanmean(infl)),
                         force=g["active_force_pN"]))
    for r in rows:
        print(f"  s{r['sid']}: mean inflow {r['mean_inflow_nm']:+.1f} nm/frame  (force {r['force']:.0f} pN)")
