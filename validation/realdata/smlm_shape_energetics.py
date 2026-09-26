"""Exploratory inverse diagnostics for angle-ordered static cap outputs.

The observation mapping and per-bin uncertainty are uncalibrated. Callers must
opt in explicitly; returned posterior summaries are conditional on this legacy
surrogate and do not establish physical parameters, kinetics, or mechanisms.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from curvo import inverse as inv
from validation.realdata.smlm_pseudotime import (
    PseudotimeTrajectory, sort_by_pseudotime)
from validation.realdata.ingest_smlm_locmofit import ingest_locmofit

H_SIGMA_FLOOR = 5e-4     # exploratory likelihood-scale floor, not measured SEM


def _trajectory_to_obs(tr: PseudotimeTrajectory, T: int):
    """Apply the legacy exploratory mapping from fitted cap area to coverage.

    Sorting population bin medians by fitted area and interpolating onto the
    model grid is a surrogate assumption, not observed assembly or time. Its
    IQR-based scale and floor are uncalibrated likelihood choices.
    """
    H = np.array(tr.H_median); Hlo = np.array(tr.H_lo); Hhi = np.array(tr.H_hi)
    n = np.array(tr.n_per_bin); frac = np.array(tr.A_surf_frac)
    H_sigma = np.maximum((Hhi - Hlo) / 2 / np.sqrt(n), H_SIGMA_FLOOR)
    o = np.argsort(frac)
    cov = np.linspace(frac[o].min(), frac[o].max(), T)
    H_obs = np.interp(cov, frac[o], H[o])
    H_sig = np.interp(cov, frac[o], H_sigma[o])
    return H_obs, H_sig


@dataclass
class ShapeEnergeticsResult:
    cell_line: str
    n_sites: int
    A_coat_nm2: float
    logz: float
    identifiability: dict           # per-parameter report from inverse
    c_eff_shape_inv_nm: float       # median effective spontaneous curvature
    c_eff_ci68: List[float]
    force_applicable: bool = False  # STATIC snapshot: force refused by construction
    absolute_force_reported: Optional[float] = None   # always None on this path
    refusal_reason: str = (
        "static super-res: no time axis and no degeneracy-breaking channel; "
        "absolute cortical force is structurally underdetermined")
    provenance: dict = field(default_factory=dict)

    def to_json(self, path):
        import dataclasses
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=float)
        return path


def fit_shape_energetics(tr: PseudotimeTrajectory, A_coat_nm2: float,
                        nlive: int = 250, seed: int = 0, *,
                        allow_exploratory: bool = False) -> ShapeEnergeticsResult:
    """Run the legacy surrogate only with explicit exploratory permission."""
    if allow_exploratory is not True:
        raise ValueError(
            "Static cap outputs lack a calibrated observation likelihood; "
            "set allow_exploratory=True only for conditional surrogate diagnostics."
        )
    if tr.force_applicable:
        raise ValueError("expected a static (force_applicable=False) trajectory")
    T = inv.FIXED["T"]
    H_obs, H_sig = _trajectory_to_obs(tr, T)
    res = inv.run_nested(H_obs, H_sig, A_coat_nm2, nlive=nlive, seed=seed)
    rep = inv.identifiability(res["samples"], res["params"])

    ce = rep["c_eff_max"]
    prov = dict(tr.provenance)
    prov.update(engine="dynesty nested sampling",
                inverse="curvo.inverse.run_nested",
                analysis_scope="exploratory surrogate diagnostics",
                calibrated_likelihood=False,
                mechanism_inference_allowed=False,
                uncertainty_model="population IQR/(2*sqrt(n)) with an arbitrary floor",
                uncertainty_floor_inv_nm=H_SIGMA_FLOOR,
                note="conditional posterior summaries; no calibrated physical inference")
    return ShapeEnergeticsResult(
        cell_line=tr.cell_line, n_sites=tr.n_sites, A_coat_nm2=float(A_coat_nm2),
        logz=res["logz"], identifiability=rep,
        c_eff_shape_inv_nm=float(ce["median"]), c_eff_ci68=[float(x) for x in ce["ci68"]],
        force_applicable=False, absolute_force_reported=None, provenance=prov)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-exploratory", action="store_true")
    args = parser.parse_args()
    if not args.allow_exploratory:
        parser.error("--allow-exploratory is required for this uncalibrated surrogate")
    gs = ingest_locmofit()
    tr = sort_by_pseudotime(gs.by_cell_line("SKMEL2"))
    A = float(np.median(gs.by_cell_line("SKMEL2").arr("surface_area_nm2")))
    r = fit_shape_energetics(tr, A, allow_exploratory=args.allow_exploratory)
    print(f"SKMEL2 n={r.n_sites}  logz={r.logz:.1f}")
    print(f"  shape c_eff = {r.c_eff_shape_inv_nm:.4f} nm^-1 "
          f"CI68 {r.c_eff_ci68}")
    print(f"  force_applicable = {r.force_applicable}  "
          f"absolute_force = {r.absolute_force_reported}")
    for k, v in r.identifiability.items():
        print(f"    {k:16s} identified={v['identified']} "
              f"(wr={v['width_ratio']:.2f} railed={v['railed']})")
