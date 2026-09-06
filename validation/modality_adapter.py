"""
modality_adapter.py — bridge a cryo-ET DENSITY image into curvo's geometry interface.

The real-image probe (real_image_probe.py) showed curvo's native fluorescence
cap-extractor does not transfer to a cryo-ET density image because the modality
differs on three axes: (1) CONTRAST (membrane dark, not bright), (2) GEOMETRY
(top-down ring cross-section, not a side-view cap), (3) SAMPLE (static subtomogram
average, not a time series). This adapter closes the two axes that are closable
from a single image — contrast and geometry — and emits a GeometryTrace that the
rest of curvo (evaluator, and in principle the inverse) can consume.

WHAT IT BRIDGES:
  * contrast : `contrast="dark"` flips intensity so a low-density membrane reads as
               a bright ridge, matching the extractor's bright-membrane assumption.
  * geometry : fits the membrane RING (radial profile + sub-pixel peak) and converts
               to a mean curvature. `curv_model` selects the interpretation:
                 "cylindrical" (a tube seen end-on)      -> H = 1/(2R)
                 "spherical"   (a vesicle equatorial cut) -> H = 1/R
               Both are the standard mean-curvature H = (c1+c2)/2 of the surface.

WHAT IT CANNOT BRIDGE (stated, not hidden):
  * dynamics/force : a single static average has no time axis and no actin channel,
    so it yields ONE geometry frame and NO force. The emitted trace has
    has_actin_channel=False and a single frame; the inverse force step is not
    applicable to it. Recovering force needs a time-resolved series (the documented
    seam), which this adapter is shaped to accept when one is in hand.

So the adapter turns a real density image into a real, provenance-tagged CURVATURE
measurement — the thing curvo is about — without over-claiming a force it cannot
support from a static average.
"""
from __future__ import annotations

import numpy as np

from curvo.perception import GeometryFrame, GeometryTrace
from curvo.schemas import Provenance


def _radial_profile(img, center=None):
    H, W = img.shape
    cy, cx = center if center else ((H - 1) / 2, (W - 1) / 2)
    yy, xx = np.mgrid[0:H, 0:W]
    rr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    Rmax = int(min(cy, cx))
    prof = np.array([img[(rr >= R) & (rr < R + 1)].mean()
                     if ((rr >= R) & (rr < R + 1)).any() else np.nan
                     for R in range(Rmax)])
    return prof, (cy, cx)


def _subpixel_peak(prof):
    """Parabolic interpolation around the integer argmax for sub-pixel radius."""
    i = int(np.nanargmax(prof))
    if 0 < i < len(prof) - 1 and np.all(np.isfinite(prof[i - 1:i + 2])):
        a, b, c = prof[i - 1], prof[i], prof[i + 1]
        denom = (a - 2 * b + c)
        off = 0.5 * (a - c) / denom if denom != 0 else 0.0
        return i + np.clip(off, -1, 1)
    return float(i)


def fit_ring(img, nm_per_px, contrast="dark", curv_model="cylindrical", n_boot=200, seed=0):
    """Fit membrane ring radius -> mean curvature, with a bootstrap uncertainty.

    Bootstrap: jitter the assumed center by +/-1 px (the dominant systematic for a
    radial fit) and re-fit, giving an honest R and H sigma."""
    signal = -img if contrast == "dark" else img.astype(float)
    signal = signal - np.nanmedian(signal)
    prof0, (cy, cx) = _radial_profile(signal)
    R0 = _subpixel_peak(prof0)
    rng = np.random.default_rng(seed)
    Rs = []
    for _ in range(n_boot):
        dc = rng.normal(0, 1.0, size=2)
        prof, _ = _radial_profile(signal, center=(cy + dc[0], cx + dc[1]))
        Rs.append(_subpixel_peak(prof))
    Rs = np.array(Rs)
    R_nm = R0 * nm_per_px
    R_sig_nm = float(np.std(Rs) * nm_per_px)
    factor = 1.0 if curv_model == "spherical" else 0.5   # H = factor / R
    H = factor / R_nm if R_nm > 0 else np.nan
    # propagate: dH = |factor / R^2| * dR
    H_sig = abs(factor / R_nm ** 2) * R_sig_nm if R_nm > 0 else np.nan
    # membrane band = half-max width about the peak (contrast-flipped profile)
    p = prof0 - np.nanmedian(prof0[:4]); pk = int(np.nanargmax(p)); half = p[pk] / 2
    lo = pk
    while lo > 0 and p[lo - 1] > half:
        lo -= 1
    hi = pk
    while hi < len(p) - 1 and p[hi + 1] > half:
        hi += 1
    snr = float(p[pk] / (np.nanstd(prof0[:4]) + 1e-6))
    return dict(R_nm=R_nm, R_sigma_nm=R_sig_nm, H_inv_nm=H, H_sigma_inv_nm=H_sig,
                neck_nm=2 * R_nm, band_px=(lo, hi), contrast_snr=snr, curv_model=curv_model)


def adapt_density_image(img, nm_per_px, contrast="dark", curv_model="cylindrical",
                        source_id="unknown", citation="", n_boot=200, seed=0):
    """Convert a single density cross-section image into a one-frame GeometryTrace.

    The trace is plumbing-compatible with curvo's perception output, so the
    evaluator/curvature machinery can consume a REAL image. It carries a single
    frame and NO actin channel (a static average has no dynamics) — force
    inference is not applicable and is not attempted."""
    fit = fit_ring(img, nm_per_px, contrast=contrast, curv_model=curv_model,
                   n_boot=n_boot, seed=seed)
    prov = Provenance(source="cryo-ET density image (modality-adapted)",
                      access="local", identifier=source_id,
                      model_version="modality_adapter_v1", retrieved_at="",
                      citation=citation)
    frame = GeometryFrame(
        t=0.0, R_nm=fit["R_nm"], R_sigma_nm=fit["R_sigma_nm"],
        H_inv_nm=fit["H_inv_nm"], H_sigma_inv_nm=fit["H_sigma_inv_nm"],
        neck_nm=fit["neck_nm"], neck_sigma_nm=2 * fit["R_sigma_nm"],
        depth_nm=np.nan, depth_sigma_nm=np.nan,          # no cap depth from a ring
        coat_coverage=np.nan, coat_sigma=np.nan,          # no coat channel
        actin_density=0.0, actin_sigma=np.nan,            # no actin channel
        n_edge_px=int(fit["band_px"][1] - fit["band_px"][0]))
    trace = GeometryTrace(frames=[frame], channels=["density"], nm_per_px=nm_per_px,
                          provenance=prov, extractor="modality_adapter_v1(ring)",
                          has_actin_channel=False)
    meta = dict(fit=fit, force_applicable=False,
                force_note=("single static average -> no time series, no actin "
                            "channel -> force inference not applicable; needs a "
                            "time-resolved series (documented seam)."))
    return trace, meta


if __name__ == "__main__":
    try:
        from validation.real_image_probe import fetch_volume, EMD_ENTRY, EMD_VOXEL_NM
    except Exception:
        from real_image_probe import fetch_volume, EMD_ENTRY, EMD_VOXEL_NM
    vol = np.load(fetch_volume())
    img = vol[vol.shape[0] // 2]
    trace, meta = adapt_density_image(
        img, nm_per_px=EMD_VOXEL_NM, contrast="dark", curv_model="cylindrical",
        source_id=EMD_ENTRY, citation="EMDB " + EMD_ENTRY)
    f = trace.frames[0]
    print(f"modality adapter on {EMD_ENTRY}:")
    print(f"  ring R = {f.R_nm:.2f} +/- {f.R_sigma_nm:.2f} nm  (SNR {meta['fit']['contrast_snr']:.1f})")
    print(f"  mean curvature H = {f.H_inv_nm:.4f} +/- {f.H_sigma_inv_nm:.4f} nm^-1"
          f"  [{meta['fit']['curv_model']}]")
    print(f"  emitted 1-frame GeometryTrace, has_actin={trace.has_actin_channel}")
    print(f"  force applicable: {meta['force_applicable']} ({meta['force_note'][:55]}...)")
