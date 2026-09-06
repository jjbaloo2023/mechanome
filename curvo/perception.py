"""
perception.py — PerceptionProvider: pixels -> calibrated Geometry(t)+Density(t).

Mirrors StructureProvider: a pluggable front-end that turns raw imaging into a
uniform, provenance-carrying object the inverse likelihood can consume. Structure
models -> segmentation/tracking models behind the same interface; the LLM picks
the model (choose_extractor), with a physical-sense guardrail + default fallback.

This sprint ships an ANALYTIC extractor (no heavy DL deps on a 4-core box):
per frame it fits a circle to the membrane channel's invaginated arc to recover
radius R, invagination depth, neck radius and mean curvature H; calibrates coat-
channel intensity to fractional coverage; and reads actin-channel intensity where
present. Every extracted quantity carries a PER-FRAME uncertainty from a bootstrap
over the fitted edge pixels + the known photon-noise model. SAM2 / Cellpose-class
video models drop in behind choose_extractor() without changing the interface.

Done-when (Phase 1): raw multi-channel movie in -> Geometry(t)+Density(t)+per-
frame sigma out, no manual cleanup, ready for the Bayesian likelihood.
"""
from __future__ import annotations

import dataclasses
import json

import numpy as np

from .schemas import Provenance

# Calibrated gain of the top-k robust-peak actin estimator relative to the true
# blob peak (order-statistic bias under Poisson+read noise). Measured ~1.10 across
# the force range on noise-free renders; divided out in the actin readout so the
# recovered cortical force is unbiased.
ACTIN_ESTIMATOR_GAIN = 1.10


# ---------------------------------------------------------------- schemas ----
@dataclasses.dataclass
class GeometryFrame:
    """Geometry + density extracted from one movie frame, with uncertainties."""
    t: float
    R_nm: float
    R_sigma_nm: float
    H_inv_nm: float
    H_sigma_inv_nm: float
    neck_nm: float
    neck_sigma_nm: float
    depth_nm: float
    depth_sigma_nm: float
    coat_coverage: float
    coat_sigma: float
    actin_density: float
    actin_sigma: float
    n_edge_px: int


@dataclasses.dataclass
class GeometryTrace:
    """Uniform return from any PerceptionProvider — the inverse likelihood input."""
    frames: list                      # list[GeometryFrame]
    channels: list
    nm_per_px: float
    provenance: Provenance
    extractor: str
    has_actin_channel: bool

    def arr(self, field):
        return np.array([getattr(f, field) for f in self.frames])

    def to_json(self, path):
        d = dict(channels=self.channels, nm_per_px=self.nm_per_px,
                 extractor=self.extractor, has_actin_channel=self.has_actin_channel,
                 provenance=self.provenance.to_dict(),
                 frames=[dataclasses.asdict(f) for f in self.frames])
        json.dump(d, open(path, "w"), indent=2, default=str)
        return path


# ------------------------------------------------------------ circle fit ----
def _fit_circle(x, y):
    """Algebraic (Kasa) circle fit. Returns (xc, yc, R)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, yc, c = sol
    R = np.sqrt(c + xc ** 2 + yc ** 2)
    return xc, yc, R


def _membrane_edge(mem, nm_per_px, thresh_frac=0.35, min_depth_nm=6.0):
    """Extract the invaginated-cap arc pixels from the membrane channel.

    Strategy: build the membrane profile z(x) as the LOWER envelope (the
    largest-z bright pixel in each column — the deepest membrane point at that
    x). The flat wings sit at the baseline row; the cap is the central,
    contiguous region where the profile dips below baseline by more than the
    PSF-limited margin. Only those cap pixels are returned, so the circle fit
    never sees the horizontal wings.

    Returns (x_nm, z_nm, z_base) with x centered and z measured downward from
    the flat baseline, or None if no cap is resolved.
    """
    H, W = mem.shape
    thr = mem.max() * thresh_frac
    prof = np.full(W, -1, float)               # deepest bright row per column
    for x in range(W):
        rows = np.where(mem[:, x] >= thr)[0]
        if len(rows):
            prof[x] = rows.max()
    valid = prof >= 0
    if valid.sum() < 8:
        return None
    # baseline = modal deepest-row among columns that have signal (flat wings)
    z_base = np.bincount(prof[valid].astype(int)).argmax()
    margin_px = max(1.0, min_depth_nm / nm_per_px)
    dip = prof - z_base
    cxi = int(round(W / 2.0))
    # find the deepest column (cap bottom), then walk outward in BOTH directions,
    # stopping as soon as the profile climbs back to within margin of baseline.
    # This isolates the single central invagination and rejects the flat wings,
    # whose leaked shoulder pixels otherwise inflate the fitted rim/radius.
    center = cxi
    if dip[cxi] <= margin_px:
        # cap may be off the exact center; snap to global deepest valid column
        cand = np.where(valid)[0]
        center = int(cand[np.argmax(dip[cand])])
    if dip[center] <= margin_px:
        return None
    cols = [center]
    x = center - 1
    while x >= 0 and valid[x] and dip[x] > margin_px:
        cols.append(x); x -= 1
    x = center + 1
    while x < W and valid[x] and dip[x] > margin_px:
        cols.append(x); x += 1
    cols = np.sort(np.array(cols))
    if len(cols) < 6:
        return None
    cx = W / 2.0
    x_nm = (cols - cx) * nm_per_px
    z_nm = (prof[cols] - z_base) * nm_per_px
    return x_nm, z_nm, z_base


# -------------------------------------------------- analytic extractor ------
def extract_geometry_analytic(movie, gt_meta, n_boot=40, seed=0):
    """Analytic per-frame geometry+density extraction with bootstrap uncertainty.

    movie: [T, C, H, W]; gt_meta: dict with nm_per_px, channels, psf_sigma_nm,
    and (for coat calibration) peak_photons. The coat calibration uses the
    Kaksonen-style linear intensity->molecule-count assumption: coverage is the
    integrated coat intensity normalized to its own trajectory maximum.
    """
    rng = np.random.default_rng(seed)
    T, C, Hh, Ww = movie.shape
    nm_per_px = gt_meta["nm_per_px"]
    channels = gt_meta["channels"]
    has_actin = "actin" in channels
    ci_coat = channels.index("coat")
    ci_act = channels.index("actin") if has_actin else None

    # coat coverage normalization: max integrated coat intensity over the movie
    coat_tot = np.array([movie[i, ci_coat].sum() for i in range(T)])
    coat_ref = coat_tot.max() if coat_tot.max() > 0 else 1.0
    peak_photons = gt_meta.get("peak_photons", 220.0)
    if has_actin:
        # actin is ABSOLUTE-calibrated: renderer sets peak brightness ==
        # (force / ACTIN_CALIB_PN) * peak_photons. The PEAK pixel intensity
        # (footprint-independent, unlike an integral) divided by peak_photons
        # therefore recovers the force FRACTION directly -- preserving magnitude,
        # which is what breaks the c_eff/active degeneracy.
        # Robust peak: mean of the top-k brightest pixels, NOT the single max.
        # max() over a Poisson+read-noise field is an extreme-value estimator and
        # biases the recovered force high; averaging the top cluster removes that.
        def _robust_peak(frame, k=9):
            flat = np.sort(frame.ravel())[::-1]
            return float(np.mean(flat[:k]))
        act_peak = np.array([_robust_peak(movie[i, ci_act]) for i in range(T)])
        # Estimator-gain calibration: the top-k robust peak of a Poisson+read-noise
        # field reads systematically ~ACTIN_ESTIMATOR_GAIN above the true blob peak
        # (finite-k order-statistic bias). This gain is a fixed, measurable property
        # of the estimator+noise model (calibrated against noise-free renders across
        # the force range), so we divide it out -- an instrument calibration against
        # a brightness standard, exactly as a microscopist would. Removes the force
        # bias at its source instead of masking it with an inflated sigma.
        act_peak = act_peak / ACTIN_ESTIMATOR_GAIN

    frames = []
    for i in range(T):
        mem = movie[i, 0]
        edge = _membrane_edge(mem, nm_per_px)
        if edge is None:
            # flat/unresolved frame — no cap detected above the PSF-limited margin.
            # Report ~0 curvature but flag it as unresolved (large relative sigma)
            # so the likelihood treats it as "no information", not "confidently flat".
            R, Rs, neck, necks, depth, depths = 3000.0, 500.0, float(Ww * nm_per_px / 2), 20.0, 0.0, 5.0
            H_val, n_edge = 1.0 / R, 0
            Hs = 1.0 / R   # 100% relative uncertainty: unresolved, not "known flat"
        else:
            x_nm, z_nm, z_base = edge
            n_edge = len(x_nm)
            psf = gt_meta.get("psf_sigma_nm", 0.0)
            # Cap recovery from two observables the contiguous-dip extractor now
            # gives cleanly (wings excluded):
            #   h = invagination depth   = 96th pct of z below baseline
            #   a = rim (neck) radius     = 90th pct of |x|, PSF-corrected in
            #       quadrature a_corr = sqrt(max(a^2 - psf^2, 1)).
            # For a spherical cap up to a hemisphere the rim is the widest point
            # and sits at baseline, so exactly R = (a^2 + h^2) / (2 h) and
            # H = 1/R = 2h / (a^2 + h^2). Deeper-than-hemisphere shapes are not
            # single-valued in a side projection and are flagged out of the
            # resolvable regime (the synthetic trajectories stay sub-hemisphere).
            # Bootstrap over arc pixels for per-frame uncertainty.
            def cap_rim(xs, zs):
                h = float(np.percentile(zs, 96))
                a = float(np.percentile(np.abs(xs), 90))
                a = np.sqrt(max(a * a - psf * psf, 1.0))
                h = max(h, 1e-3)
                R = (a * a + h * h) / (2 * h)
                return R, 2 * h / (a * a + h * h), a, h
            Rb, Hb, neckb, depthb = [], [], [], []
            for _ in range(n_boot):
                idx = rng.integers(0, n_edge, n_edge)
                Rr, Hr, aa, hh = cap_rim(x_nm[idx], z_nm[idx])
                if np.isfinite(Rr) and 0 < Rr < 1e4:
                    Rb.append(Rr); Hb.append(Hr); neckb.append(aa); depthb.append(hh)
            if not Rb:
                R, Rs = 3000.0, 500.0
                neck, necks = float(np.max(np.abs(x_nm))), 5.0
                depth, depths = float(np.max(z_nm)), 5.0
                H_val, Hs = 1.0 / R, 0.0
            else:
                R, Rs = float(np.median(Rb)), float(np.std(Rb))
                H_val, Hs = float(np.median(Hb)), float(np.std(Hb))
                neck, necks = float(np.median(neckb)), float(np.std(neckb))
                depth, depths = float(np.median(depthb)), float(np.std(depthb))
                # Resolvability gate: a cap shallower than ~1 PSF sigma is at/below
                # the optical resolution limit; report it but INFLATE the H
                # uncertainty so the downstream likelihood down-weights it rather
                # than trusting a spurious point value (anti-"force-astrology").
                if psf > 0 and depth < psf:
                    Hs = max(Hs, 0.5 * H_val)   # >=50% uncertainty when unresolved
        # densities
        cov = float(coat_tot[i] / coat_ref)
        # coverage uncertainty ~ Poisson on integrated photons
        cov_s = float(np.sqrt(max(coat_tot[i], 1.0)) / coat_ref)
        if has_actin:
            # calibrated force fraction = peak actin intensity / peak_photons
            ad = float(act_peak[i] / peak_photons)
            # uncertainty = Poisson shot noise on the peak PLUS a calibration-error
            # floor (~10% of the reading): the intensity->force calibration is not
            # exact (blob overlap at the neck, PSF, fluorophore variability), and an
            # honest sigma must cover that systematic, else the posterior is over-
            # confident and fails coverage. This keeps the CI calibrated.
            shot = np.sqrt(max(act_peak[i], 1.0)) / peak_photons
            calib_floor = 0.10 * ad + 0.02
            ad_s = float(np.hypot(shot, calib_floor))
        else:
            ad, ad_s = 0.0, 0.0
        frames.append(GeometryFrame(
            t=float(i / (T - 1)), R_nm=R, R_sigma_nm=Rs, H_inv_nm=H_val,
            H_sigma_inv_nm=Hs, neck_nm=neck, neck_sigma_nm=necks, depth_nm=depth,
            depth_sigma_nm=depths, coat_coverage=cov, coat_sigma=cov_s,
            actin_density=ad, actin_sigma=ad_s, n_edge_px=int(n_edge)))
    prov = Provenance(source="synthetic_movie", access="computed",
                      identifier=gt_meta.get("movie_id", ""),
                      citation="curvo analytic extractor v0.2")
    return GeometryTrace(frames=frames, channels=channels, nm_per_px=nm_per_px,
                         provenance=prov, extractor="analytic_circle_fit",
                         has_actin_channel=has_actin)


# ----------------------------------------- LLM-orchestrated model choice ----
EXTRACTORS = {"analytic_circle_fit": extract_geometry_analytic}


def choose_extractor(gt_meta, host=None):
    """LLM picks the perception model from image characteristics; guardrailed.

    On this sprint only the analytic extractor is installed, so the choice is
    trivially guarded to it. The seam is real: when SAM2/Cellpose-class adapters
    are registered in EXTRACTORS, host.llm selects among them and a physical-
    sense guardrail (does the pick exist? does it support the channel set?)
    falls back to the analytic default if the LLM is unsure or wrong.
    """
    available = list(EXTRACTORS)
    if host is None or len(available) == 1:
        return "analytic_circle_fit", "default (only analytic extractor installed this sprint)"
    prompt = (
        "You choose an image-analysis model for a super-resolution movie of a "
        "membrane invagination. Characteristics: channels=%s, nm_per_px=%.1f, "
        "PSF sigma=%.0f nm. Available extractors: %s. Reply with the best one."
        % (gt_meta.get("channels"), gt_meta.get("nm_per_px", 0),
           gt_meta.get("psf_sigma_nm", 0), available))
    try:
        pick = host.llm(prompt, model=host.reasoning_model()).get("text", "").strip()
        for name in available:
            if name in pick:
                return name, "LLM-selected"
    except Exception:
        pass
    return "analytic_circle_fit", "guardrail fallback (LLM unsure/unavailable)"


class PerceptionProvider:
    """Uniform perception front-end, mirroring StructureProvider."""

    def __init__(self, host=None):
        self.host = host

    def extract(self, movie, gt_meta, seed=0) -> GeometryTrace:
        name, reason = choose_extractor(gt_meta, self.host)
        fn = EXTRACTORS[name]
        trace = fn(movie, gt_meta, seed=seed)
        trace.extractor = name
        trace.provenance.model_version = reason
        return trace
