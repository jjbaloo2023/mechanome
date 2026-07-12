"""
smlm_shape_energetics.py -- shape-energetics inverse on a static SMLM trajectory.

Runs curvo's Bayesian inverse on the pseudo-temporally-sorted SMLM curvature
trajectory H(theta) to fit the shape-energetics (the tension / spontaneous-
curvature / bending trade-off consistent with the observed shape sequence).

THE FORCE FIREWALL, ONE LEVEL EARLIER. A static super-res population has no real
time axis and no co-imaged actin channel, so absolute cortical force is
structurally underdetermined -- not merely statistically noisy. The SMLM path
therefore sets force_applicable=False and REFUSES an absolute-force point
estimate categorically, independent of what any single posterior happens to look
like. What the inverse CAN report is the shape-energetics: the effective
spontaneous curvature the coat must express to sit where it does on the H(theta)
sequence, with a calibrated identifiability verdict.

This extends the anti-force-astrology firewall (Roy 2020 STED / ENTH+AP180
inverse: refuse a force the data do not identify) to the frozen-snapshot regime:
here the refusal is by construction of the observable, not by posterior width.
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

H_SIGMA_FLOOR = 5e-4     # curvature SEM floor per bin (nm^-1)


def _trajectory_to_obs(tr: PseudotimeTrajectory, T: int):
    """Resample the binned H(theta) trajectory onto the forward model's T-frame
    coverage coordinate. The sort is monotone in theta; we index by the coat-area
    fraction (the model's assembly coordinate) so the geometry maps onto the same
    sigmoidal coverage ramp the forward model uses."""
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
                        nlive: int = 250, seed: int = 0) -> ShapeEnergeticsResult:
    """Fit shape-energetics to a pseudo-temporal SMLM trajectory and REFUSE
    absolute force (force_applicable=False by construction of the observable)."""
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
                note="force_applicable=False: absolute force refused by "
                     "construction (static snapshot), NOT merely by posterior width")
    return ShapeEnergeticsResult(
        cell_line=tr.cell_line, n_sites=tr.n_sites, A_coat_nm2=float(A_coat_nm2),
        logz=res["logz"], identifiability=rep,
        c_eff_shape_inv_nm=float(ce["median"]), c_eff_ci68=[float(x) for x in ce["ci68"]],
        force_applicable=False, absolute_force_reported=None, provenance=prov)


if __name__ == "__main__":
    gs = ingest_locmofit()
    tr = sort_by_pseudotime(gs.by_cell_line("SKMEL2"))
    A = float(np.median(gs.by_cell_line("SKMEL2").arr("surface_area_nm2")))
    r = fit_shape_energetics(tr, A)
    print(f"SKMEL2 n={r.n_sites}  logz={r.logz:.1f}")
    print(f"  shape c_eff = {r.c_eff_shape_inv_nm:.4f} nm^-1 "
          f"CI68 {r.c_eff_ci68}")
    print(f"  force_applicable = {r.force_applicable}  "
          f"absolute_force = {r.absolute_force_reported}")
    for k, v in r.identifiability.items():
        print(f"    {k:16s} identified={v['identified']} "
              f"(wr={v['width_ratio']:.2f} railed={v['railed']})")
