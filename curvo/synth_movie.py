"""
synth_movie.py — forward-simulate a curvature trajectory from KNOWN forces and
render it as a noisy multi-channel super-res-style movie, with ground truth
stored alongside. This is the backbone of curvo's validation ladder: no force
claim ships without recovering it from a synthetic movie generated here.

Trajectory model
----------------
A clathrin coat assembles over time: coverage(t) ramps sigmoidally from 0 to a
plateau. The active players scale with coverage — spontaneous curvature c_eff
(wedge + crowding) and, optionally, cortical active force — so the membrane cap
deepens flat -> dome -> Omega. Each frame's geometry (opening angle psi, radius
R, neck radius, invagination depth, mean curvature H) is the evaluator's
energy-minimizing spherical cap at that instant.

Rendering (side view, x-z cross-section)
----------------------------------------
- membrane channel : the bilayer profile as a bright curve
- coat channel     : intensity on the coated cap, proportional to coverage(t)
- actin channel    : intensity at the neck/base rim, proportional to active force
Each channel is blurred by a Gaussian PSF (super-res-scale) and corrupted with
Poisson shot noise + Gaussian read noise. The per-pixel noise model is stored so
the perception layer can propagate per-frame uncertainty.

Output: a MovieStack (numpy array [T, C, H, W]) + a GroundTruth dict.
"""
from __future__ import annotations

import dataclasses
import json
from typing import Optional

import numpy as np
from scipy.ndimage import gaussian_filter

from . import evaluator_tier0 as ev

# actin-channel intensity calibration: this many pN of cortical force -> full
# (peak_photons) actin brightness. Fixes the absolute intensity->force mapping the
# inverse likelihood uses, so the actin channel carries magnitude not just shape.
ACTIN_CALIB_PN = 60.0


@dataclasses.dataclass
class GroundTruth:
    """The forces and per-frame geometry used to generate a movie."""
    sigma_kBT_nm2: float
    c_eff_max_inv_nm: float           # plateau spontaneous curvature (wedge+crowding)
    active_force_max_pN: float        # plateau cortical force (0 if no actin actor)
    kappa_kBT: float
    coat_rigidity_factor: float
    A_coat_nm2: float
    has_actin_channel: bool
    # per-frame arrays (length T)
    t: list
    coverage: list
    c_eff: list
    active_force_pN: list
    R_nm: list
    psi_deg: list
    neck_nm: list
    depth_nm: list
    H_inv_nm: list
    stage: list
    # rendering metadata
    nm_per_px: float
    psf_sigma_nm: float
    channels: list

    def to_json(self, path):
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=str)


def _sigmoid(x, x0, k):
    return 1.0 / (1.0 + np.exp(-(x - x0) / k))


def simulate_trajectory(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.06,
                        active_force_max_pN=0.0, kappa_kBT=20.0,
                        coat_rigidity_factor=3.0, A_coat_nm2=None,
                        T=24, ramp_mid=0.45, ramp_width=0.12, active_delay=0.0):
    """Evolve the cap geometry as the coat assembles (coverage 0 -> plateau).

    active_delay (in units of the normalized time axis, 0..1) phase-shifts the
    ACTIVE (actin) force ramp LATER than the coat-curvature ramp. Default 0 keeps
    curvature and force perfectly coupled (the single-CCP recovery gate assumes this
    and is unaffected). A positive delay models sequential orchestration — coat
    curvature first, actin force after — giving a ground-truth onset lag for the
    orchestration model to recover rather than a coupling built in by construction."""
    if A_coat_nm2 is None:
        A_coat_nm2 = np.pi * 60 ** 2
    t = np.linspace(0, 1, T)
    coverage = _sigmoid(t, ramp_mid, ramp_width)
    coverage = (coverage - coverage.min()) / (coverage.max() - coverage.min())
    c_eff = c_eff_max_inv_nm * coverage
    # actin force follows a ramp shifted later by active_delay
    active_ramp = _sigmoid(t, ramp_mid + active_delay, ramp_width)
    active_ramp = (active_ramp - active_ramp.min()) / (active_ramp.max() - active_ramp.min() + 1e-12)
    active = active_force_max_pN * active_ramp
    # coat rigidity ramps in with coverage too (1 -> plateau)
    rig = 1.0 + (coat_rigidity_factor - 1.0) * coverage
    R, psi, neck, depth, H, stage = [], [], [], [], [], []
    for i in range(T):
        mo = ev.ccs_curvature(c_eff[i], sigma_kBT_nm2, kappa_kBT, A_coat_nm2,
                              coat_rigidity_factor=rig[i], active_force_pN=active[i])
        Ri = mo["R_nm"]; psii = np.radians(mo["psi_opt_deg"])
        R.append(Ri); psi.append(mo["psi_opt_deg"])
        neck.append(float(Ri * np.sin(psii)))         # rim (neck) radius
        depth.append(float(Ri * (1 - np.cos(psii))))   # invagination depth
        H.append(mo["achieved_mean_curvature_inv_nm"]); stage.append(mo["stage"])
    return dict(t=t, coverage=coverage, c_eff=c_eff, active=active,
                R=np.array(R), psi=np.array(psi), neck=np.array(neck),
                depth=np.array(depth), H=np.array(H), stage=stage, rig=rig,
                A_coat_nm2=A_coat_nm2)


def _render_frame(R, psi_deg, neck, depth, coverage, active_frac,
                  has_actin, field_px, nm_per_px, psf_sigma_nm, rng,
                  peak_photons=220.0, read_noise=2.0):
    """Render one (C,H,W) multi-channel frame, side view (x-z)."""
    psi = np.radians(psi_deg)
    C = 3 if has_actin else 2
    img = np.zeros((C, field_px, field_px), float)
    cx = field_px / 2.0
    z0 = field_px * 0.28            # flat-membrane baseline row (near top)
    # Spherical cap: rim at baseline (x=+/-neck, z=0), bottom at (0, depth).
    # x = R sin(t), z_down = R cos(t) - R cos(psi): z=0 at rim (t=psi),
    # z=depth at bottom (t=0). z increases DOWNWARD into the cell.
    n_arc = 600
    t_arc = np.linspace(0, psi, n_arc)
    x_half = R * np.sin(t_arc)
    z_half = R * np.cos(t_arc) - R * np.cos(psi)
    x_nm = np.concatenate([-x_half[::-1], x_half])
    z_nm = np.concatenate([z_half[::-1], z_half])
    xpx_arc = cx + x_nm / nm_per_px
    zpx_arc = z0 + z_nm / nm_per_px
    foot = neck
    # flat membrane wings outside the footprint, at baseline
    wing = np.linspace(foot, field_px * nm_per_px / 2, 300)
    wx = np.concatenate([cx - wing / nm_per_px, cx + wing / nm_per_px])
    wz = np.full_like(wx, z0)
    # membrane = arc + wings, rendered as a distance-field "tube" (robust to blur)
    mem_x = np.concatenate([xpx_arc, wx])
    mem_z = np.concatenate([zpx_arc, wz])
    gz, gx = np.mgrid[0:field_px, 0:field_px]
    tube_w = max(1.2, 6.0 / nm_per_px)          # membrane half-width in px
    # nearest-point distance from every pixel to the membrane point cloud
    # (vectorized in chunks over the curve samples)
    d2 = np.full((field_px, field_px), 1e12)
    for k in range(0, len(mem_x), 40):
        px = mem_x[k:k + 40][:, None, None]
        pz = mem_z[k:k + 40][:, None, None]
        dd = (gx[None] - px) ** 2 + (gz[None] - pz) ** 2
        d2 = np.minimum(d2, dd.min(0))
    img[0] = np.exp(-d2 / (2 * tube_w ** 2))
    # coat channel: only on the CAP arc (not the wings), scaled by coverage
    d2c = np.full((field_px, field_px), 1e12)
    for k in range(0, len(xpx_arc), 40):
        px = xpx_arc[k:k + 40][:, None, None]
        pz = zpx_arc[k:k + 40][:, None, None]
        dd = (gx[None] - px) ** 2 + (gz[None] - pz) ** 2
        d2c = np.minimum(d2c, dd.min(0))
    img[1] = coverage * np.exp(-d2c / (2 * tube_w ** 2))
    # actin channel: concentrated at the two neck rims. Deposit a UNIT-amplitude
    # blob shape; it is peak-normalized after blur so the calibration is exact.
    actin_shape = np.zeros((field_px, field_px))
    if has_actin:
        # A single actin focus at the neck (on-axis). Using ONE blob keeps the
        # intensity->force calibration exact: two overlapping rim blobs summed to
        # ~1.15x a unit blob after blur, injecting a systematic high bias into the
        # recovered force. A single centered focus removes that bias at the source.
        actin_shape += np.exp(-((gx - cx) ** 2 + (gz - z0) ** 2) /
                              (2 * (2 * tube_w) ** 2))
    ps = psf_sigma_nm / nm_per_px
    # membrane: shape marker, peak-normalized to peak_photons
    img[0] = gaussian_filter(img[0], ps)
    m0 = img[0].max()
    if m0 > 0:
        img[0] = img[0] / m0 * peak_photons
    # coat: brightness proportional to coverage in [0,1] (absolute density)
    img[1] = gaussian_filter(img[1], ps) * peak_photons
    # actin: peak intensity after blur == active_frac * peak_photons EXACTLY, so
    # peak_actin/peak_photons recovers the force fraction regardless of PSF width
    # (mirrors a fluorophore brightness-calibration standard).
    if has_actin:
        blurred = gaussian_filter(actin_shape, ps)
        bpk = blurred.max()
        if bpk > 0:
            img[2] = blurred / bpk * active_frac * peak_photons
    # Poisson shot noise + Gaussian read noise
    noisy = rng.poisson(np.clip(img, 0, None)).astype(float)
    noisy += rng.normal(0, read_noise, noisy.shape)
    return np.clip(noisy, 0, None)


def render_movie(gt_forces: dict, field_px=128, nm_per_px=2.0, psf_sigma_nm=30.0,
                 has_actin=False, seed=0, peak_photons=220.0, read_noise=2.0):
    """Full pipeline: forces -> trajectory -> noisy multi-channel movie + GroundTruth."""
    rng = np.random.default_rng(seed)
    traj = simulate_trajectory(**gt_forces)
    T = len(traj["t"])
    frames = []
    # actin fluorescence encodes ABSOLUTE force via a fixed calibration
    # (ACTIN_CALIB_PN pN -> full brightness), NOT self-normalized per trajectory,
    # so the channel carries force MAGNITUDE (needed to break the c_eff/active
    # degeneracy), not merely the assembly-ramp shape.
    for i in range(T):
        af = float(traj["active"][i] / ACTIN_CALIB_PN) if has_actin else 0.0
        af = min(af, 1.0)
        fr = _render_frame(traj["R"][i], traj["psi"][i], traj["neck"][i],
                           traj["depth"][i], float(traj["coverage"][i]), af,
                           has_actin, field_px, nm_per_px, psf_sigma_nm, rng,
                           peak_photons, read_noise)
        frames.append(fr)
    movie = np.stack(frames, 0)   # [T, C, H, W]
    channels = ["membrane", "coat"] + (["actin"] if has_actin else [])
    gt = GroundTruth(
        sigma_kBT_nm2=gt_forces.get("sigma_kBT_nm2", 0.02),
        c_eff_max_inv_nm=gt_forces.get("c_eff_max_inv_nm", 0.06),
        active_force_max_pN=gt_forces.get("active_force_max_pN", 0.0),
        kappa_kBT=gt_forces.get("kappa_kBT", 20.0),
        coat_rigidity_factor=gt_forces.get("coat_rigidity_factor", 3.0),
        A_coat_nm2=float(traj["A_coat_nm2"]), has_actin_channel=has_actin,
        t=traj["t"].tolist(), coverage=traj["coverage"].tolist(),
        c_eff=traj["c_eff"].tolist(), active_force_pN=traj["active"].tolist(),
        R_nm=traj["R"].tolist(), psi_deg=traj["psi"].tolist(),
        neck_nm=traj["neck"].tolist(), depth_nm=traj["depth"].tolist(),
        H_inv_nm=traj["H"].tolist(), stage=list(traj["stage"]),
        nm_per_px=nm_per_px, psf_sigma_nm=psf_sigma_nm, channels=channels)
    return movie, gt
