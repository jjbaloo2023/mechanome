"""
ingest_smlm_locmofit.py -- SMLM PerceptionProvider adapter (LocMoFit -> curvo).

Ingests the published 3D-SMLM LocMoFit spherical-cap fits from
Mund, Tschanz, Wu, Kaksonen, Avinoam, Schwarz & Ries, "Clathrin coats partially
preassemble and subsequently bend during endocytosis", J Cell Biol 2023
(doi:10.1083/jcb.202206038; data: BioStudies S-BIAD566). Each endocytic site is
fit to a spherical cap parametrised by radius R and closing angle theta; we map
that geometry into curvo's engine, carrying LocMoFit's fields verbatim:

    LocMoFit  ->  curvo
    theta (closing angle, deg)  ->  psi (rad); 180 deg = full sphere
    curvature = 1/R (nm^-1)     ->  H  (mean curvature of the cap; H = 1/R)
    radius R (nm)               ->  R
    localization precision      ->  geometry uncertainty (3.9 nm xy / 12.5 nm z)

STATIC super-res: no real time axis. This adapter emits geometry ONLY. Pseudo-
temporal ordering (by theta) and the force-refusing inverse live downstream --
the SMLM path sets force_applicable=False (see smlm_shape_energetics.py).

Data are NOT committed (raw-imaging firewall); they are cached under
cache/smlm_locmofit/ and re-fetchable from the documented BioStudies URL by
fetch_locmofit_fits().
"""
from __future__ import annotations

import dataclasses
import glob
import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ constants
# Modal localization precision, quoted verbatim from Mund et al. 2023 (JCB,
# doi:10.1083/jcb.202206038): "modal values of the localization precision at
# 3.9 nm in x/y and 12.5 nm in z" (imaging pipeline of Li et al., 2018, cited
# there). Resolution "about 10 nm in x/y and 30 nm in z".
LOC_PRECISION_XY_NM = 3.9
LOC_PRECISION_Z_NM = 12.5
RESOLUTION_XY_NM = 10.0
RESOLUTION_Z_NM = 30.0
FULL_SPHERE_DEG = 180.0

_BIOSTUDIES_BASE = (
    "https://ftp.ebi.ac.uk/biostudies/fire/S-BIAD/566/S-BIAD566/Files/"
)
_INDEX_TSV = "3_Model_Fit_Results%20-%20Tabellenblatt1.tsv"
_CACHE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cache", "smlm_locmofit",
)


# ------------------------------------------------------------------ data model
@dataclass
class SMLMSite:
    """One clathrin-coated structure: a static spherical-cap LocMoFit fit."""
    site_id: int
    cell_line: str
    file_number: int
    psi_rad: float          # closing angle theta, in radians
    theta_deg: float        # closing angle, degrees (LocMoFit verbatim)
    H_inv_nm: float         # mean curvature of the cap (= curvature = 1/R)
    R_nm: float             # spherical-cap radius
    surface_area_nm2: float
    projected_area_nm2: float
    H_sigma_inv_nm: float   # curvature uncertainty from localization precision


@dataclass
class SMLMGeometrySet:
    """A population of static geometry fits -- the SMLM PerceptionProvider output.

    This is geometry ONLY (no time axis). Downstream, pseudo-temporal sorting by
    theta reconstructs the average shape trajectory, and the inverse fits shape-
    energetics while refusing absolute force (force_applicable=False).
    """
    sites: List[SMLMSite]
    cell_lines: List[str]
    extractor: str = "locmofit_spherical_cap"
    observable: str = "4_static_superres_geometry"
    force_applicable: bool = False      # static snapshot: no rates -> no force
    provenance: dict = field(default_factory=dict)

    def arr(self, attr):
        return np.array([getattr(s, attr) for s in self.sites])

    def by_cell_line(self, cl):
        return SMLMGeometrySet(
            sites=[s for s in self.sites if s.cell_line == cl],
            cell_lines=[cl], extractor=self.extractor, observable=self.observable,
            force_applicable=self.force_applicable, provenance=self.provenance)

    def to_json(self, path):
        d = dict(
            extractor=self.extractor, observable=self.observable,
            force_applicable=self.force_applicable, cell_lines=self.cell_lines,
            n_sites=len(self.sites), provenance=self.provenance,
            sites=[dataclasses.asdict(s) for s in self.sites])
        json.dump(d, open(path, "w"), indent=2, default=float)
        return path


# ------------------------------------------------------------------ fetch
def fetch_locmofit_fits(cache_dir: str = _CACHE) -> List[str]:
    """Download the per-cell LocMoFit CSVs from BioStudies S-BIAD566 into
    cache_dir (idempotent). Returns the list of local CSV paths. Raw data are
    never committed; this is the documented re-fetch path."""
    os.makedirs(cache_dir, exist_ok=True)
    idx = urllib.request.urlopen(_BIOSTUDIES_BASE + _INDEX_TSV, timeout=90)
    rows = [l.split("\t") for l in idx.read().decode().splitlines()[1:]]
    out = []
    for rel, _cell, _md5 in rows:
        local = os.path.join(cache_dir, os.path.basename(rel))
        if not os.path.exists(local):
            raw = urllib.request.urlopen(
                _BIOSTUDIES_BASE + urllib.request.quote(rel), timeout=120).read()
            open(local, "wb").write(raw)
        out.append(local)
    return out


def _curvature_sigma(R_nm, theta_deg):
    """Propagate localization precision to a curvature (1/R) uncertainty.

    A spherical-cap radius fit from a point cloud has a radius uncertainty that
    scales with the localization precision divided by sqrt(rim points); we use a
    conservative geometric estimate sigma_R ~ precision, so sigma_H = sigma_R/R^2.
    Near-flat caps (large R) get correspondingly tiny H-sigma, which is correct:
    curvature is well-determined near zero even when R is ill-defined."""
    sigma_R = np.hypot(LOC_PRECISION_XY_NM, LOC_PRECISION_Z_NM)  # ~13 nm, 3D
    return sigma_R / np.maximum(R_nm, 1.0) ** 2


# ------------------------------------------------------------------ ingest
def ingest_locmofit(cache_dir: str = _CACHE,
                    cell_lines: Optional[List[str]] = None,
                    drop_disconnected: bool = True) -> SMLMGeometrySet:
    """Load every cached LocMoFit CSV into a single SMLMGeometrySet.

    Drops disconnected_sites (multi-structure fits) by default, and any row with
    a non-finite curvature. theta is the closing angle in degrees; we carry both
    it and psi = radians(theta)."""
    paths = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not paths:
        raise FileNotFoundError(
            f"no LocMoFit CSVs in {cache_dir}; call fetch_locmofit_fits() first")
    sites: List[SMLMSite] = []
    seen_cl = []
    for p in paths:
        df = pd.read_csv(p)
        for _, r in df.iterrows():
            cl = str(r["cell_line"])
            if cell_lines and cl not in cell_lines:
                continue
            disc = r.get("disconnected_sites", False)
            if drop_disconnected and (disc is True or str(disc).upper() == "TRUE"):
                continue
            H = float(r["curvature"])
            R = float(r["radius"])
            th = float(r["theta"])
            if not np.isfinite(H) or not np.isfinite(th) or H < 0:
                continue
            if cl not in seen_cl:
                seen_cl.append(cl)
            sites.append(SMLMSite(
                site_id=int(r["ID"]), cell_line=cl,
                file_number=int(r["file_number"]),
                psi_rad=float(np.radians(th)), theta_deg=th,
                H_inv_nm=H, R_nm=abs(R),
                surface_area_nm2=float(r["surface_area"]),
                projected_area_nm2=float(r["projected_area"]),
                H_sigma_inv_nm=float(_curvature_sigma(abs(R), th))))
    prov = dict(
        dataset="BioStudies S-BIAD566",
        paper="Mund, Tschanz, ... Ries, J Cell Biol 2023",
        doi="10.1083/jcb.202206038",
        method="3D-SMLM + LocMoFit spherical-cap fit (LocMoFit: Wu et al., "
               "2023, cited in Mund et al. 2023)",
        resolution_xy_nm=RESOLUTION_XY_NM, resolution_z_nm=RESOLUTION_Z_NM,
        loc_precision_xy_nm=LOC_PRECISION_XY_NM,
        loc_precision_z_nm=LOC_PRECISION_Z_NM,
        note="static super-res; geometry only; force_applicable=False")
    return SMLMGeometrySet(sites=sites, cell_lines=seen_cl, provenance=prov)


if __name__ == "__main__":
    fetch_locmofit_fits()
    gs = ingest_locmofit()
    from collections import Counter
    print(f"loaded {len(gs.sites)} sites across {gs.cell_lines}")
    print("by cell line:", dict(Counter(s.cell_line for s in gs.sites)))
    print("force_applicable:", gs.force_applicable)
