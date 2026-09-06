"""
Observable-#2 forward model: epi-TIRF ratiometric invagination depth.

Motivation (the dynamic-vs-resolution tension). curvo's cap-fit perception
reads curvature from LATERAL shape in the image plane, and the benchmark
extension showed that dies at live-super-res resolution (BioTISR ~31 nm/px:
zero resolvable frames). But the mechanically-relevant signal of invagination
is AXIAL, and the axial signature needs no lateral super-resolution:

  In TIRF, excitation decays into the cell as I(z) = I0 * exp(-z / d_pen)
  (evanescent penetration depth d_pen ~ 90-150 nm). As a clathrin-coated pit
  invaginates, its coat moves away from the coverslip (z increases), so its TIRF
  signal drops relative to epifluorescence (which is ~z-independent). The
  TIRF/epi ratio therefore reads the coat's mean axial position -- a CALIBRATED
  absolute length (via the known d_pen) -- at ordinary diffraction-limited
  lateral resolution and live frame rates. This is observable #2 (Danuser /
  Saffarian / Kural epi-TIRF), the modality that is dynamic AND
  resolution-compatible.

This module encodes that forward map on curvo's own spherical-cap geometry:
  forces -> (per-frame psi, R via the SAME energy minimization as the inverse)
         -> coat surface z-distribution
         -> TIRF/epi ratio(t) = < exp(-z/d_pen) >_coat
and provides a likelihood so the inverse can be run on a ratio trajectory. A
companion recovery study (recover_depth_spec) measures what ratiometric SNR is
needed to constrain force -- i.e. the data spec a real dataset must meet.

Sign convention: coat rim sits at the membrane plane z=0; the dome invaginates
INTO the cell (z > 0, away from the coverslip in an inverted-TIRF geometry), so
the coat's mean z rises monotonically with the opening angle psi.
"""

import numpy as np

from curvo import evaluator_tier0 as ev
from curvo import inverse as inv

# TIRF evanescent penetration depth (nm). Typical 488 nm / high-NA objective
# TIRF: d_pen ~ 90-150 nm. Treated as a KNOWN instrument constant (it is set by
# incidence angle + wavelength + indices and is calibrated per microscope).
D_PEN_NM = 110.0

_PSI_GRID = np.linspace(0.02, np.pi - 0.001, 400)
_THETA = np.linspace(0.0, 1.0, 128)   # fractional angle along the cap, scaled by psi


def cap_geometry(sigma, c_eff_max, active_max, A_coat_nm2,
                 kappa=20.0, coat_rig=3.0, T=24, ramp_mid=0.45, ramp_width=0.12):
    """Per-frame (psi, R, depth) from the SAME cap energy minimization the
    inverse uses. Returns arrays of shape (T,)."""
    kBT = ev.kBT_zJ
    t = np.linspace(0, 1, T)
    cov = 1.0 / (1.0 + np.exp(-(t - ramp_mid) / ramp_width))
    cov = (cov - cov.min()) / (cov.max() - cov.min())
    c_eff = c_eff_max * cov
    active = active_max * cov
    rig = 1.0 + (coat_rig - 1.0) * cov
    kappa_eff = kappa * rig
    psi = _PSI_GRID[None, :]
    omc = np.clip(1.0 - np.cos(psi), 1e-9, None)
    R = np.sqrt(A_coat_nm2 / (2 * np.pi * omc))
    depth = R * omc
    footprint = np.pi * (R * np.sin(psi)) ** 2
    bending = (kappa_eff[:, None] / 2) * (2.0 / R - c_eff[:, None]) ** 2 * A_coat_nm2
    tension = sigma * (A_coat_nm2 - footprint)
    active_E = -(active[:, None] * depth) / kBT
    E = bending + tension + active_E
    i = np.argmin(E, axis=1)
    return _PSI_GRID[i], R[0, i], depth[0, i]


def tirf_epi_ratio_from_psi(psi, R, d_pen=D_PEN_NM):
    """Mean evanescent attenuation over a spherical-cap coat surface.

    A surface point at polar angle theta in [0, psi] sits at height above the rim
    z(theta) = R (cos theta - cos psi). Fluorophores are uniform over the coat
    surface, whose area element weights as sin(theta). The TIRF/epi ratio is the
    surface-averaged exp(-z/d_pen):
        ratio = int_0^psi exp(-z/d_pen) sin(theta) dtheta / (1 - cos psi)
    -> 1 for a flat coat (z=0 everywhere), decreasing as the pit invaginates.
    Vectorized over frames.
    """
    psi = np.atleast_1d(psi).astype(float)
    R = np.atleast_1d(R).astype(float)
    th = _THETA[None, :] * psi[:, None]                 # (T, Ntheta)
    z = R[:, None] * (np.cos(th) - np.cos(psi)[:, None]) # (T, Ntheta), >= 0
    w = np.sin(th)                                        # area weight
    _trap = getattr(np, "trapezoid", getattr(np, "trapz", None))
    num = _trap(np.exp(-z / d_pen) * w, th, axis=1)
    den = _trap(w, th, axis=1)
    return num / np.clip(den, 1e-9, None)


def predict_ratio(theta_forces, params, A_coat_nm2, d_pen=D_PEN_NM,
                  fixed=inv.FIXED):
    """Forward model: force vector -> TIRF/epi ratio trajectory."""
    d = {p.name: v for p, v in zip(params, theta_forces)}
    psi, R, _ = cap_geometry(
        sigma=d.get("sigma", 0.02), c_eff_max=d.get("c_eff_max", 0.0),
        active_max=d.get("active_force_max", 0.0), A_coat_nm2=A_coat_nm2,
        kappa=fixed["kappa_kBT"], coat_rig=fixed["coat_rigidity_factor"],
        T=fixed["T"])
    return tirf_epi_ratio_from_psi(psi, R, d_pen)


# --------------------------------------------------- STAR two-colour mode ----
# Real published calibration from Nawara et al., Nat Commun 2022 (STAR
# microscopy, doi:10.1038/s41467-022-29317-1), read from their released code
# (github.com/Mattheyses-Lab/Nawara_et_al._NatCommun_2022, D. Beads/
# dream_tirf_bead_TN.m). STAR dual-tags clathrin with two fluorophores excited
# at different wavelengths; the wavelength-dependent evanescent penetration
# depth means the two channels sample axial position differently, and the
# log-ratio maps to absolute height dz. This is the two-colour generalisation
# of the single-channel epi/TIRF ratio above -- SAME evanescent physics.

def star_penetration_depth(lambda_nm, n_glass=1.515, n_sample=1.43,
                           theta_rad=1.2741):
    """Evanescent penetration depth d = lambda/(4 pi sqrt(n_g^2 sin^2 theta -
    n_s^2)). Their exact bead-calibration parameters as defaults (TIRF angle
    73 deg, ~2.3 deg above the 70.7 deg critical angle -> a deep field)."""
    return lambda_nm / (4 * np.pi * np.sqrt(
        n_glass ** 2 * np.sin(theta_rad) ** 2 - n_sample ** 2))


# Their two channels and the ratio->dz scale gamma (dream_tirf_bead_TN.m l.22-25)
STAR_D_488 = star_penetration_depth(488.0)   # ~167 nm
STAR_D_647 = star_penetration_depth(647.0)   # ~221 nm
STAR_GAMMA = 1.0 / ((STAR_D_647 - STAR_D_488) / (STAR_D_647 * STAR_D_488))  # ~679 nm


def star_ratio_from_psi(psi, R, d_short=STAR_D_488, d_long=STAR_D_647):
    """STAR two-colour intensity ratio I_long / I_short over the coat surface.

    Each channel is a surface-averaged evanescent attenuation at its own
    penetration depth; the ratio grows as the coat invaginates (the deeper-
    penetrating long-wavelength channel attenuates less with height). Maps to
    their dz via dz = gamma * log(ratio / ratio_0)  (their l.204).
    """
    I_short = tirf_epi_ratio_from_psi(psi, R, d_pen=d_short)
    I_long = tirf_epi_ratio_from_psi(psi, R, d_pen=d_long)
    return I_long / I_short


def star_dz_from_psi(psi, R, d_short=STAR_D_488, d_long=STAR_D_647,
                     gamma=STAR_GAMMA):
    """Recovered absolute height dz(t) using STAR's own log-ratio*gamma map,
    referenced to the first frame (as their code does)."""
    ratio = star_ratio_from_psi(psi, R, d_short, d_long)
    return np.log(ratio / ratio[0]) * gamma


# ------------------------------------------------------------- inverse -------

def _make_ratio_loglike(ratio_obs, ratio_sigma, params, A_coat_nm2, d_pen):
    ro = np.asarray(ratio_obs); rs = np.asarray(ratio_sigma)
    def loglike(theta):
        pred = predict_ratio(theta, params, A_coat_nm2, d_pen)
        return float(-0.5 * np.sum(((pred - ro) / rs) ** 2))
    return loglike


def run_ratio_inverse(ratio_obs, ratio_sigma, A_coat_nm2, params=None,
                      d_pen=D_PEN_NM, nlive=200, seed=0):
    """Nested-sampling inverse on an epi-TIRF ratio trajectory."""
    from dynesty import NestedSampler
    from dynesty.utils import resample_equal
    params = params or inv.DEFAULT_PARAMS
    loglike = _make_ratio_loglike(ratio_obs, ratio_sigma, params, A_coat_nm2, d_pen)
    ndim = len(params)
    rng = np.random.default_rng(seed)
    s = NestedSampler(loglike, lambda u: inv.prior_transform(u, params), ndim,
                      nlive=nlive, rstate=rng)
    s.run_nested(print_progress=False, dlogz=0.05, maxcall=500_000)
    res = s.results
    logwt = res.logwt - res.logz[-1]
    samples = resample_equal(res.samples, np.exp(logwt))
    return dict(samples=samples, logz=float(res.logz[-1]), params=params)


if __name__ == "__main__":
    A = np.pi * 60 ** 2
    # a known maturing pit driven by active force
    forces = [0.02, 40.0, 0.02]  # c_eff, active, sigma
    psi, R, depth = cap_geometry(0.02, 0.02, 40.0, A)
    ratio = tirf_epi_ratio_from_psi(psi, R)
    print(f"d_pen = {D_PEN_NM} nm")
    print(f"invagination depth: {depth[0]:.0f} -> {depth[-1]:.0f} nm")
    print(f"TIRF/epi ratio:     {ratio[0]:.3f} -> {ratio[-1]:.3f} "
          f"(drops {100*(1-ratio[-1]/ratio[0]):.0f}% as the pit matures)")
