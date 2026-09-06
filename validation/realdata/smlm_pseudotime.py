"""
smlm_pseudotime.py -- pseudo-temporal sorting of static SMLM geometry.

Static super-res has no time axis. Following Mund, Tschanz, ... Ries (JCB 2023),
we use the closing angle theta as a monotone proxy for endocytic progression and
sort thousands of static clathrin-coated structures into an AVERAGE geometry-vs-
pseudotime trajectory R(theta), H(theta), A(theta).

Pseudotime != real time: this recovers the average SHAPE trajectory (the order in
which geometry changes), not absolute rates. It reproduces the paper's central
qualitative finding -- the coat assembles as a flat lattice to a fraction A0 of
its final area, then bends continuously -- as an internal consistency check, and
provides the geometry(pseudotime) input the shape-energetics inverse consumes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List

import numpy as np

from validation.realdata.ingest_smlm_locmofit import (
    SMLMGeometrySet, ingest_locmofit, FULL_SPHERE_DEG)


@dataclass
class PseudotimeTrajectory:
    """Binned average geometry vs pseudo-temporal closing angle theta."""
    cell_line: str
    n_sites: int
    theta_bin_deg: List[float]      # bin centre
    theta_edges_deg: List[float]
    n_per_bin: List[int]
    H_median: List[float]           # mean curvature per bin
    H_lo: List[float]               # 25th pct
    H_hi: List[float]               # 75th pct
    R_median: List[float]           # spherical-cap radius per bin
    A_surf_median: List[float]      # coat surface area per bin
    A_surf_frac: List[float]        # A_surf normalised to its closed-coat value
    A0_flat_fraction: float         # coat-area fraction assembled flat before bending
    theta_bend_onset_deg: float     # theta at which curvature departs from flat
    observable: str = "4_static_superres_geometry"
    force_applicable: bool = False
    provenance: dict = field(default_factory=dict)

    def to_json(self, path):
        import dataclasses
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=float)
        return path


def sort_by_pseudotime(gs: SMLMGeometrySet, n_bins: int = 18,
                       bend_H_frac: float = 0.15) -> PseudotimeTrajectory:
    """Sort a geometry set by closing angle and bin into an average trajectory.

    A0 (flat-lattice area fraction) follows the paper's definition: the coat
    surface area at theta->0 relative to the closed-coat area at theta->180.
    The bend onset is the theta where median curvature first exceeds
    bend_H_frac of its closed-coat plateau -- the flat-to-curved transition."""
    theta = gs.arr("theta_deg"); H = gs.arr("H_inv_nm")
    R = gs.arr("R_nm"); A = gs.arr("surface_area_nm2")
    edges = np.linspace(0.0, FULL_SPHERE_DEG, n_bins + 1)
    idx = np.clip(np.digitize(theta, edges) - 1, 0, n_bins - 1)

    centres, nper, Hmed, Hlo, Hhi, Rmed, Amed = [], [], [], [], [], [], []
    for b in range(n_bins):
        sel = idx == b
        if sel.sum() < 3:
            continue
        centres.append(0.5 * (edges[b] + edges[b + 1]))
        nper.append(int(sel.sum()))
        Hmed.append(float(np.median(H[sel])))
        Hlo.append(float(np.percentile(H[sel], 25)))
        Hhi.append(float(np.percentile(H[sel], 75)))
        Rmed.append(float(np.median(R[sel])))
        Amed.append(float(np.median(A[sel])))
    Hmed = np.array(Hmed); Amed = np.array(Amed); centres = np.array(centres)

    # closed-coat plateau = mean of the last 3 bins (theta near 180)
    A_closed = float(np.mean(Amed[-3:]))
    A_flat = float(Amed[0])                      # theta -> 0
    A0 = A_flat / A_closed
    A_frac = (Amed / A_closed).tolist()

    # bend onset: first theta where H exceeds bend_H_frac of its plateau
    H_plateau = float(np.mean(Hmed[-3:]))
    thr = bend_H_frac * H_plateau
    above = np.where(Hmed >= thr)[0]
    theta_bend = float(centres[above[0]]) if len(above) else float("nan")

    prov = dict(gs.provenance)
    prov.update(sort_proxy="closing angle theta (Mund et al. 2023)",
                A_closed_nm2=A_closed, H_plateau_inv_nm=H_plateau,
                note="pseudotime != real time; shape trajectory only")
    return PseudotimeTrajectory(
        cell_line=gs.cell_lines[0] if len(gs.cell_lines) == 1 else "pooled",
        n_sites=len(gs.sites), theta_bin_deg=centres.tolist(),
        theta_edges_deg=edges.tolist(), n_per_bin=nper,
        H_median=Hmed.tolist(), H_lo=Hlo, H_hi=Hhi, R_median=Rmed,
        A_surf_median=Amed.tolist(), A_surf_frac=A_frac,
        A0_flat_fraction=A0, theta_bend_onset_deg=theta_bend,
        force_applicable=False, provenance=prov)


if __name__ == "__main__":
    gs = ingest_locmofit()
    for cl in ["SKMEL2", "3T3", "U2OS"]:
        tr = sort_by_pseudotime(gs.by_cell_line(cl))
        print(f"{cl}: n={tr.n_sites}, A0={tr.A0_flat_fraction:.2f}, "
              f"bend onset theta={tr.theta_bend_onset_deg:.0f} deg")
