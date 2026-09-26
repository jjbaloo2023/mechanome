"""Descriptive angle ordering of static, jointly fitted SMLM cap geometry.

Closing angle orders a population of fixed sites; it is not a measured single-pit
trajectory or time coordinate. Binned geometry and historical summary field names
remain available for exploratory calculations, without mechanistic calibration.
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
    A0_flat_fraction: float         # first retained bin area / last-three-bin mean
    theta_bend_onset_deg: float     # first bin passing the chosen curvature threshold
    observable: str = "4_static_superres_geometry"
    force_applicable: bool = False
    provenance: dict = field(default_factory=dict)

    def to_json(self, path):
        import dataclasses
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=float)
        return path


def sort_by_pseudotime(gs: SMLMGeometrySet, n_bins: int = 18,
                       bend_H_frac: float = 0.15) -> PseudotimeTrajectory:
    """Bin static cap outputs by angle and retain descriptive population summaries.

    The historical A0 and bend-onset fields describe the chosen bins and
    threshold; they do not measure assembly history or a bending event.
    """
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

    # Reference summary: mean area in the last three retained angle bins.
    A_closed = float(np.mean(Amed[-3:]))
    A_flat = float(Amed[0])                      # theta -> 0
    A0 = A_flat / A_closed
    A_frac = (Amed / A_closed).tolist()

    # Historical onset summary: first bin crossing a relative curvature threshold.
    H_plateau = float(np.mean(Hmed[-3:]))
    thr = bend_H_frac * H_plateau
    above = np.where(Hmed >= thr)[0]
    theta_bend = float(centres[above[0]]) if len(above) else float("nan")

    prov = dict(gs.provenance)
    prov.update(sort_proxy="closing angle theta (Mund et al. 2023)",
                A_closed_nm2=A_closed, H_plateau_inv_nm=H_plateau,
                observation_space="joint cap-fit outputs ordered by angle",
                within_pit_trajectory=False,
                calibrated_likelihood=False,
                mechanism_inference_allowed=False,
                note="descriptive static population ordering; no measured time axis")
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
