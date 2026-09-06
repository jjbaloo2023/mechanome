"""
curvo.evaluator_tier0 — the cheap analytic evaluator (microseconds/call).

Under the bitter-lesson reframing this is the *engine*, not a fallback: search
dominates only when each evaluation is cheap, so closed-form Helfrich energetics
carry the loop. Every function here evaluates the physical model — the LLM orchestrator never
produces a curvature or an energy number; it only proposes what to evaluate.

Three models, all with analytic checks:

  1. helfrich_tube      — membrane tether pulled at tension sigma; closed forms
                          R* = sqrt(kappa/2 sigma), f0 = 2 pi sqrt(2 kappa sigma)
                          (Derenyi, Julicher & Prost 2002).
  2. budding_cap        — line-tension budding of a domain via a spherical-cap
                          shape family; analytic boundary a* = 4 kappa / lambda
                          at sigma=0, c0=0 (Lipowsky 1992).
  3. ccs_curvature      — CCS flat->dome->Omega readout: effective spontaneous
                          curvature (from players) vs tension, on the same cap
                          family; returns achieved mean curvature + dome/Omega OP.

Units: kappa in kBT converted to zJ internally; lengths in nm; tension sigma in
kBT/nm^2; curvature in nm^-1. kBT at 298 K = 4.114 zJ = 4.114 pN·nm.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar

from .schemas import EvaluatorResult
from .constants import KBT_ZJ as kBT_zJ   # single source of truth (constants.py)


# --------------------------------------------------------------------------
# 1. Helfrich tube (tether) — closed form + energetics
# --------------------------------------------------------------------------
def helfrich_tube(kappa_kBT: float, sigma_kBT_nm2: float, c0: float = 0.0,
                  force_pN: float | None = None):
    """Equilibrium radius and energy/length of a membrane tube.

    E/L(R) = 2 pi R [ (kappa/2)(1/R - c0)^2 + sigma ] - f
    Closed form (c0=0): R* = sqrt(kappa / (2 sigma)), f0 = 2 pi sqrt(2 kappa sigma).
    Returns dict with numeric minimum and (when c0=0) the analytic values.
    """
    kappa = kappa_kBT      # keep in kBT; sigma in kBT/nm^2 -> consistent
    sigma = sigma_kBT_nm2

    def EL(R):
        return 2 * np.pi * R * ((kappa / 2) * (1.0 / R - c0) ** 2 + sigma)

    res = minimize_scalar(EL, bounds=(0.5, 200.0), method="bounded")
    R_num = float(res.x)
    out = {
        "R_equilibrium_nm": R_num,
        "mean_curvature_inv_nm": 1.0 / (2 * R_num),   # cylinder H = 1/(2R)
        "energy_per_length_kBT_nm": float(res.fun),
    }
    if abs(c0) < 1e-9:
        out["R_closed_form_nm"] = float(np.sqrt(kappa / (2 * sigma)))
        out["tether_force_closed_form_pN"] = float(2 * np.pi * np.sqrt(2 * kappa * sigma) * kBT_zJ)
    if force_pN is not None:
        out["net_energy_per_length_kBT_nm"] = float(res.fun - force_pN / kBT_zJ)
    return out


# --------------------------------------------------------------------------
# Spherical-cap shape family (shared by budding + CCS)
# --------------------------------------------------------------------------
def _cap_energy(psi, A, kappa, lam, sigma, c0, active_force_pN=0.0):
    """Helfrich + line + tension + active-cortex energy of a spherical cap of area A.

    psi in (0, pi): opening angle. psi->0 flat disk, psi=pi complete sphere.
    R(psi) = sqrt(A / (2 pi (1 - cos psi))).  H = 1/R.  perimeter = 2 pi R sin psi.
    tension term = sigma (A - footprint), footprint = pi (R sin psi)^2.

    active_force_pN: a minimal cortical active-stress actor. A cortical/actin
    machine applies an axial force pulling the cap inward; the work it does as
    the cap invaginates is -f * d, where the invagination depth d = R(1 - cos psi).
    A positive force lowers the energy of deeper caps, driving psi toward closure
    (actin-driven invagination) -- physically distinct from tension (which opposes
    footprint) and from c0 (which sets the preferred curvature). f is in pN, d in
    nm, so f*d is in pN*nm = zJ; divide by kBT_zJ to match the kBT energy units.
    """
    one_minus_cos = 1.0 - np.cos(psi)
    one_minus_cos = max(one_minus_cos, 1e-9)
    R = np.sqrt(A / (2 * np.pi * one_minus_cos))
    bending = (kappa / 2) * (2.0 / R - c0) ** 2 * A
    line = lam * 2 * np.pi * R * np.sin(psi)
    footprint = np.pi * (R * np.sin(psi)) ** 2
    tension = sigma * (A - footprint)
    depth = R * one_minus_cos                       # invagination depth (nm)
    active = -(active_force_pN * depth) / kBT_zJ     # work by cortical force (kBT)
    return bending + line + tension + active, R


def budding_cap(A_nm2: float, kappa_kBT: float, lam_kBT_nm: float,
                sigma_kBT_nm2: float = 0.0, c0: float = 0.0):
    """Minimize cap energy over psi; classify flat vs budded.

    Analytic check (sigma=0, c0=0): domain buds when its flat radius a exceeds
    a* = 4 kappa / lambda.
    """
    psis = np.linspace(0.02, np.pi - 0.001, 600)
    E = np.array([_cap_energy(p, A_nm2, kappa_kBT, lam_kBT_nm, sigma_kBT_nm2, c0)[0]
                  for p in psis])
    i = int(np.argmin(E))
    psi_opt = float(psis[i])
    _, R_opt = _cap_energy(psi_opt, A_nm2, kappa_kBT, lam_kBT_nm, sigma_kBT_nm2, c0)
    a_flat = np.sqrt(A_nm2 / np.pi)
    E_flat = _cap_energy(0.02, A_nm2, kappa_kBT, lam_kBT_nm, sigma_kBT_nm2, c0)[0]
    E_bud = _cap_energy(np.pi - 0.001, A_nm2, kappa_kBT, lam_kBT_nm, sigma_kBT_nm2, c0)[0]
    budded = psi_opt > (np.pi / 2)
    return {
        "psi_opt_rad": psi_opt,
        "psi_opt_deg": np.degrees(psi_opt),
        "R_bud_nm": float(R_opt),
        "mean_curvature_inv_nm": 1.0 / float(R_opt),
        "state": "budded" if budded else "flat",
        "E_flat_kBT": float(E_flat),
        "E_bud_kBT": float(E_bud),
        "a_flat_nm": float(a_flat),
        "a_critical_closed_form_nm": float(4 * kappa_kBT / lam_kBT_nm),
    }


def budding_critical_radius(kappa_kBT: float, lam_kBT_nm: float) -> float:
    """Closed-form ground truth: a* = 4 kappa / lambda (sigma=0, c0=0)."""
    return 4 * kappa_kBT / lam_kBT_nm


# --------------------------------------------------------------------------
# 3. CCS flat -> dome -> Omega curvature readout
# --------------------------------------------------------------------------
def ccs_curvature(c_eff_inv_nm: float, sigma_kBT_nm2: float, kappa_kBT: float,
                  A_coat_nm2: float, coat_rigidity_factor: float = 1.0,
                  lam_kBT_nm: float = 0.0, active_force_pN: float = 0.0):
    """Achieved membrane curvature for a clathrin-coated patch.

    The active players supply an effective spontaneous curvature c_eff and the
    coat stiffens the patch (raises effective kappa). Tension opposes budding.
    The patch relaxes on the spherical-cap family to the curvature the physics
    allows; we read out the achieved mean curvature and a dome/Omega order
    parameter (psi/pi: ~0.5 = dome/hemisphere, ->1 = Omega/closed).
    """
    kappa_eff = kappa_kBT * coat_rigidity_factor
    psis = np.linspace(0.02, np.pi - 0.001, 800)
    E = np.array([_cap_energy(p, A_coat_nm2, kappa_eff, lam_kBT_nm,
                              sigma_kBT_nm2, c_eff_inv_nm, active_force_pN)[0] for p in psis])
    i = int(np.argmin(E))
    psi_opt = float(psis[i])
    _, R = _cap_energy(psi_opt, A_coat_nm2, kappa_eff, lam_kBT_nm,
                       sigma_kBT_nm2, c_eff_inv_nm, active_force_pN)
    H = 1.0 / float(R)
    op = psi_opt / np.pi   # dome/Omega order parameter
    if op < 0.33:
        stage = "flat"
    elif op < 0.66:
        stage = "dome"
    else:
        stage = "Omega"
    return {
        "achieved_mean_curvature_inv_nm": H,
        "R_nm": float(R),
        "psi_opt_deg": np.degrees(psi_opt),
        "dome_omega_OP": op,
        "stage": stage,
        "kappa_eff_kBT": kappa_eff,
        "c_eff_inv_nm": c_eff_inv_nm,
        "active_force_pN": active_force_pN,
    }


# --------------------------------------------------------------------------
# Objective wrapper: turn a model output into an EvaluatorResult
# --------------------------------------------------------------------------
def score_ccs(model_out: dict, target_curvature_inv_nm: float,
              tol: float = 0.004) -> EvaluatorResult:
    """Score a CCS result against a target mean curvature (the clathrin-track
    ground-truth observable). objective = |achieved - target|."""
    ach = model_out["achieved_mean_curvature_inv_nm"]
    obj = abs(ach - target_curvature_inv_nm)
    return EvaluatorResult(
        tier="tier0_analytic",
        observables={"achieved_mean_curvature_inv_nm": ach,
                     "stage": model_out["stage"],
                     "dome_omega_OP": model_out["dome_omega_OP"],
                     "R_nm": model_out["R_nm"]},
        objective_value=float(obj),
        target_met=bool(obj <= tol and model_out["stage"] in ("dome", "Omega")),
        detail={"target_curvature_inv_nm": target_curvature_inv_nm, "tol": tol,
                "c_eff_inv_nm": model_out["c_eff_inv_nm"]},
    )
