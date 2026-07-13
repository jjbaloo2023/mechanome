"""
barrier.py -- Reduced Helfrich-Canham spherical-cap maturation barrier.

A clathrin-coated patch of FIXED membrane area A_coat invaginates flat -> budded
along a one-parameter reaction coordinate: the spherical-cap polar angle psi in
[0, pi].  psi=0 is the flat patch; psi=pi is a complete sphere (the vesicle).

This is a *reduced* model, NOT a shape solver (deliberately -- see MODEL.md scope).
The coat area is held fixed and the shape is constrained to a spherical cap, so the
whole flat->budded path is a single closed-form curve E(psi). This is the minimal
object that (i) makes tension oppose budding, (ii) lets spontaneous curvature C0
lower the barrier, and (iii) recovers the exact closed-sphere Helfrich energy 8*pi*kappa.

Energy (Helfrich-Canham, uniform mean curvature on the cap):

    E(psi) = (kappa/2) * (2/R(psi) - C0_eff)^2 * A_coat        [bending]
           + sigma * A_coat * (1 - cos psi) / 2                 [tension work]

with the fixed-area cap geometry
    A_coat = 2*pi*R^2*(1 - cos psi)   =>   R(psi) = sqrt(A_coat / (2*pi*(1-cos psi))).

Conventions / units (kBT-nm system, matches Stage 0 of this project):
    kappa   [kBT]         bending rigidity (~20)
    A_coat  [nm^2]        fixed coat membrane area
    C0_eff  [1/nm]        effective spontaneous curvature (sphere of radius R0 -> C0=2/R0)
    sigma   [kBT/nm^2]    membrane tension (0.00243 kBT/nm^2 ~ 0.01 mN/m)
    E       [kBT]

The barrier DeltaE_dagger is measured relative to the flat state E(psi->0), so the
flat-coat frustration offset (kappa/2)*C0_eff^2*A_coat cancels out of the barrier.
"""
from __future__ import annotations
import numpy as np

# ---- unit bridge (documented, not used internally; internal unit is kBT/nm^2) ----
KBT_PN_NM = 4.114            # k_B T at 300 K, in pN*nm
def mNm_to_kBT_per_nm2(sigma_mNm: float) -> float:
    """Convert tension in mN/m (== pN/nm) to kBT/nm^2."""
    return sigma_mNm / KBT_PN_NM         # (pN/nm) / (pN*nm/kBT) = kBT/nm^2

_EPS = 1e-9

def cap_radius(psi, A_coat):
    """Sphere radius R(psi) [nm] of a fixed-area cap. R->inf as psi->0 (flat)."""
    psi = np.asarray(psi, float)
    one_minus_cos = np.clip(1.0 - np.cos(psi), _EPS, None)
    return np.sqrt(A_coat / (2.0 * np.pi * one_minus_cos))

def projected_footprint(psi, A_coat):
    """Base-plane footprint A_proj = A_coat*(1+cos psi)/2. =A_coat flat, ->0 sphere."""
    psi = np.asarray(psi, float)
    return A_coat * (1.0 + np.cos(psi)) / 2.0

def bending_energy(psi, A_coat, c0_eff, kappa=20.0):
    """(kappa/2)(2/R - C0)^2 A_coat  [kBT].  Uniform mean curvature H=1/R on the cap."""
    R = cap_radius(psi, A_coat)
    return 0.5 * kappa * (2.0 / R - c0_eff) ** 2 * A_coat

def tension_energy(psi, A_coat, sigma):
    """sigma * A_coat * (1-cos psi)/2  [kBT]. Membrane area recruited into the bud."""
    psi = np.asarray(psi, float)
    return sigma * A_coat * (1.0 - np.cos(psi)) / 2.0

def total_energy(psi, A_coat, c0_eff, sigma, kappa=20.0):
    """Total cap energy E(psi) [kBT] (absolute, includes flat-state offset)."""
    return bending_energy(psi, A_coat, c0_eff, kappa) + tension_energy(psi, A_coat, sigma)

def energy_profile(A_coat, c0_eff, sigma, kappa=20.0, n=901, psi_max=np.pi):
    """Return (psi grid, DeltaE(psi) [kBT] relative to the flat state)."""
    psi = np.linspace(_EPS, psi_max, n)
    E = total_energy(psi, A_coat, c0_eff, sigma, kappa)
    E_flat = total_energy(_EPS, A_coat, c0_eff, sigma, kappa)
    return psi, E - float(E_flat)

def barrier(A_coat, c0_eff, sigma, kappa=20.0, n=1201):
    """
    Maturation decision barriers along the flat->budded reaction coordinate.

    A coated patch relaxes to an interior partial-dome MINIMUM (the metastable
    resting shape); from there it can either go FORWARD to the committed, fully
    budded/closed state (psi=pi, neck fully constricted -> the transition state
    for fission) or BACKWARD to the flat, disassembled state (abort). This
    single-interior-minimum structure is a property of the fixed-area cap:
    dE/dx (x=1-cos psi) has exactly one zero, a minimum, for C0_eff > 0.

      dE_commit : E(budded) - E(resting_min)  [kBT] >= 0
                  the maturation barrier -- RISES with tension, FALLS with C0_eff.
      dE_abort  : E(flat)   - E(resting_min)  [kBT] >= 0
                  the barrier to disassemble back to flat.
      dE_bud    : E(budded) - E(flat)         [kBT]
                  net thermodynamic drive; = dE_commit - dE_abort.
      psi_rest  : resting-minimum cap angle [rad] (0 if flat is the min).
      spontaneous : True if the resting min IS the budded state (commit barrier ~0).

    The decision layer consumes dE_commit (see decision.py).
    """
    psi, dE = energy_profile(A_coat, c0_eff, sigma, kappa, n=n)
    dE_bud = float(dE[-1])
    i_rest = int(np.argmin(dE))
    dE_rest = float(dE[i_rest])
    dE_commit = dE_bud - dE_rest                 # forward climb (>=0)
    dE_abort = 0.0 - dE_rest                      # backward climb to flat (>=0)
    spontaneous = (i_rest >= n - 2) or (dE_commit < 1e-6)
    return dict(dE_commit=float(dE_commit), dE_abort=float(dE_abort),
                dE_bud=dE_bud, psi_rest=float(psi[i_rest]),
                spontaneous=bool(spontaneous))
