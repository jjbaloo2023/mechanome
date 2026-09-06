"""
field_movie.py — a crowded, multi-structure synthetic time-lapse with GT tracks.

Each structure is an INDEPENDENT clathrin-coated pit rendered by the validated
single-pit pipeline (synth_movie.render_movie): the same forces -> trajectory ->
spherical-cap -> multi-channel render that the perception benchmark and recovery
gate certified. A field is built by compositing N such pits at scattered positions
with STAGGERED birth times and per-structure forces, so at any frame the field
holds a mix of nascent, maturing, and vanished pits — the real-microscopy
condition the single-CCP tests never exercised.

Ground truth is exact and per-structure: (x, y) position, birth/death frame,
force parameters, and the full geometry(t) track (H, neck, depth, stage). This is
the reference the tracking (Step 3) and per-track recovery (Step 5) validate
against.

Compositing note: per-pit renders are summed into the field canvas (fluorescence
is additive) and one field-level read-noise floor is added. Overlapping PSF tails
between nearby pits produce genuine crowding confounds — the thing being tested.
"""
from __future__ import annotations

import dataclasses
import json
import numpy as np

from curvo import synth_movie as sm


@dataclasses.dataclass
class StructureTrack:
    """Exact ground truth for one structure in the field."""
    sid: int
    x_px: float
    y_px: float
    birth: int
    death: int                      # exclusive: active for frames [birth, death)
    active_force_pN: float
    c_eff_max: float
    sigma: float
    active_delay: float             # phase lag of actin force vs coat curvature (0..1)
    H_inv_nm: list                  # per-lifecycle-frame (len = death-birth)
    neck_nm: list
    depth_nm: list
    stage: list
    active_force_series_pN: list    # per-frame actin force (reflects the delay)


def _place(field, frame_small, cx, cy):
    """Add a small per-structure frame [C,h,w] into the field [C,H,W] centered at
    (cx,cy), clipping at the field border."""
    C, h, w = frame_small.shape
    H, W = field.shape[1:]
    y0, x0 = int(cy - h // 2), int(cx - w // 2)
    ys0, xs0 = max(0, -y0), max(0, -x0)
    y0, x0 = max(0, y0), max(0, x0)
    ye, xe = min(H, y0 + h - ys0), min(W, x0 + w - xs0)
    ys, xs = ys0, xs0
    field[:, y0:ye, x0:xe] += frame_small[:, ys:ys + (ye - y0), xs:xs + (xe - x0)]


def generate_field(n_struct=8, field_px=256, T_field=48, nm_per_px=2.0,
                   psf_sigma_nm=18.0, peak_photons=220.0, read_noise=2.0,
                   struct_px=64, lifetime=24, has_actin=True, seed=0,
                   force_range=(20.0, 60.0), min_sep_px=34,
                   active_delay_range=(0.05, 0.30)):
    """Composite N staggered single-pit renders into a crowded field time-lapse.

    Returns (movie [T_field, C, field_px, field_px], list[StructureTrack], meta).
    Each structure's per-pit movie is rendered NOISELESS (read_noise=0) so that only
    ONE field-level noise floor is applied after compositing."""
    rng = np.random.default_rng(seed)
    n_ch = 3 if has_actin else 2
    channels = ["membrane", "coat"] + (["actin"] if has_actin else [])
    movie = np.zeros((T_field, n_ch, field_px, field_px), float)

    # scatter positions with a minimum separation (rejection sampling)
    pos = []
    tries = 0
    while len(pos) < n_struct and tries < 4000:
        tries += 1
        p = rng.uniform(struct_px // 2 + 2, field_px - struct_px // 2 - 2, size=2)
        if all(np.hypot(p[0] - q[0], p[1] - q[1]) >= min_sep_px for q in pos):
            pos.append(p)
    pos = np.array(pos)
    n_struct = len(pos)

    tracks = []
    for sid in range(n_struct):
        cx, cy = pos[sid]
        birth = int(rng.integers(0, max(1, T_field - lifetime)))
        death = min(T_field, birth + lifetime)
        force = float(rng.uniform(*force_range))
        c_eff = float(rng.uniform(0.045, 0.075))
        sigma = 0.02
        active_delay = float(rng.uniform(*active_delay_range))
        gt_forces = dict(sigma_kBT_nm2=sigma, c_eff_max_inv_nm=c_eff,
                         active_force_max_pN=force, T=lifetime, active_delay=active_delay)
        pit, gt = sm.render_movie(gt_forces, field_px=struct_px, nm_per_px=nm_per_px,
                                  psf_sigma_nm=psf_sigma_nm, has_actin=has_actin,
                                  seed=seed * 1000 + sid, peak_photons=peak_photons,
                                  read_noise=0.0)
        for k in range(death - birth):
            _place(movie[birth + k], pit[k], cx, cy)
        tracks.append(StructureTrack(
            sid=sid, x_px=float(cx), y_px=float(cy), birth=birth, death=death,
            active_force_pN=force, c_eff_max=c_eff, sigma=sigma, active_delay=active_delay,
            H_inv_nm=list(map(float, gt.H_inv_nm)), neck_nm=list(map(float, gt.neck_nm)),
            depth_nm=list(map(float, gt.depth_nm)), stage=list(gt.stage),
            active_force_series_pN=list(map(float, gt.active_force_pN))))

    # one field-level noise floor: Poisson shot + Gaussian read
    movie = rng.poisson(np.clip(movie, 0, None)).astype(float)
    movie += rng.normal(0, read_noise, size=movie.shape)
    movie = np.clip(movie, 0, None)

    meta = dict(field_px=field_px, T_field=T_field, nm_per_px=nm_per_px,
                psf_sigma_nm=psf_sigma_nm, peak_photons=peak_photons,
                channels=channels, n_struct=n_struct, lifetime=lifetime,
                struct_px=struct_px, has_actin=has_actin, seed=seed)
    return movie, tracks, meta


def tracks_to_json(tracks, meta, path):
    d = dict(meta=meta, tracks=[dataclasses.asdict(t) for t in tracks])
    json.dump(d, open(path, "w"), indent=2)
    return path


if __name__ == "__main__":
    movie, tracks, meta = generate_field(n_struct=8, seed=0)
    np.save("outputs/field_movie.npy", movie)
    tracks_to_json(tracks, meta, "outputs/field_tracks.json")
    print(f"field {movie.shape}  {meta['n_struct']} structures")
    for t in tracks:
        print(f"  s{t.sid}: pos=({t.x_px:.0f},{t.y_px:.0f}) frames[{t.birth},{t.death}) "
              f"force={t.active_force_pN:.0f}pN c_eff={t.c_eff_max:.3f}")
