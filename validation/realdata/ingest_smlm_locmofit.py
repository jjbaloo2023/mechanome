"""
ingest_smlm_locmofit.py -- SMLM PerceptionProvider adapter (LocMoFit -> curvo).

Ingests the published 3D-SMLM LocMoFit spherical-cap fits from
Mund, Tschanz, Wu, Kaksonen, Avinoam, Schwarz & Ries, "Clathrin coats partially
preassemble and subsequently bend during endocytosis", J Cell Biol 2023
(doi:10.1083/jcb.202206038; data: BioStudies S-BIAD566). Each endocytic site is
fit to a spherical cap parametrised by surface area A and closing angle theta;
radius R and curvature are derived deposited fields. We map that geometry into
curvo's engine, carrying LocMoFit's fields verbatim:

    LocMoFit  ->  curvo
    theta (closing angle, deg)  ->  psi (rad); 180 deg = full sphere
    curvature = 1/R (nm^-1)     ->  H  (mean curvature of the cap; H = 1/R)
    radius R (nm)               ->  R
    deposited fit uncertainty   ->  unavailable in the processed tables

STATIC super-res: no real time axis. This adapter emits deposited geometry ONLY.
Theta sorting can make a descriptive static-population summary, but does not
recover a per-site trajectory. The SMLM path sets force_applicable=False (see
smlm_shape_energetics.py).

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
OBSERVATION_CONTRACT_VERSION = "locmofit-observation-contract-001"

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
    # Processed tables contain no fit covariance or calibrated per-site
    # uncertainty.  It is therefore unknown by default, rather than a weight.
    H_sigma_inv_nm: Optional[float] = None
    # Deposited fields retained so geometry selection cannot overwrite history.
    raw_theta_deg: Optional[float] = None
    raw_H_inv_nm: Optional[float] = None
    corrected_theta_deg: Optional[float] = None
    corrected_H_inv_nm: Optional[float] = None
    corrected_geometry_supplied: bool = False
    raw_R_nm: Optional[float] = None
    rim_length_nm: Optional[float] = None
    disconnected_sites: Optional[bool] = None
    source_key: str = ""
    source_path: str = ""


@dataclass
class SMLMGeometrySet:
    """A population of static geometry fits -- the SMLM PerceptionProvider output.

    This is geometry ONLY (no time axis). Downstream theta sorting is
    descriptive of the static population; any shape-energetics path refuses
    absolute force (force_applicable=False).
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
        # Unknown fit uncertainties must round-trip as JSON null, never NaN.
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(d, handle, indent=2, default=float, allow_nan=False)
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
    """Return the historical exploratory radius-to-curvature heuristic.

    This is not a propagated LocMoFit fit uncertainty: the processed tables lack
    point clouds, fit covariance, nuisance estimates, and calibration inputs.
    Callers must opt in through ``legacy_curvature_sigma=True`` and must not
    label its result calibrated.
    """
    sigma_R = np.hypot(LOC_PRECISION_XY_NM, LOC_PRECISION_Z_NM)  # ~13 nm, 3D
    return sigma_R / np.maximum(R_nm, 1.0) ** 2


# ------------------------------------------------------------------ ingest
def ingest_locmofit(cache_dir: str = _CACHE,
                    cell_lines: Optional[List[str]] = None,
                    drop_disconnected: bool = True,
                    *, geometry: str = "raw_nonnegative",
                    legacy_curvature_sigma: bool = False) -> SMLMGeometrySet:
    """Load every cached LocMoFit CSV into a single SMLMGeometrySet.

    ``geometry="raw_nonnegative"`` is the compatibility default: it retains
    unflagged rows with finite, nonnegative deposited raw curvature.  Select
    ``geometry="corrected"`` deliberately to use the deposited corrected
    curvature and angle; that selection requires both corrected columns.

    ``drop_disconnected`` applies the deposited curation flag. Its biological or
    fitting meaning is not inferred here. ``H_sigma_inv_nm`` is unknown by
    default. ``legacy_curvature_sigma=True`` exposes a repository heuristic for
    exploratory compatibility only; it is not a calibrated uncertainty.
    """
    if geometry not in {"raw_nonnegative", "corrected"}:
        raise ValueError(
            "geometry must be 'raw_nonnegative' or 'corrected', "
            f"got {geometry!r}")
    if not isinstance(legacy_curvature_sigma, bool):
        raise TypeError("legacy_curvature_sigma must be an explicit bool")
    paths = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not paths:
        raise FileNotFoundError(
            f"no LocMoFit CSVs in {cache_dir}; call fetch_locmofit_fits() first")
    sites: List[SMLMSite] = []
    seen_cl = []
    for p in paths:
        df = pd.read_csv(p)
        required = {"ID", "cell_line", "file_number", "theta", "curvature",
                    "radius", "surface_area", "projected_area"}
        missing = sorted(required.difference(df.columns))
        if missing:
            raise ValueError(f"{p}: missing required LocMoFit fields: {missing}")
        has_corrected_theta = "theta_corrected" in df.columns
        has_corrected_curvature = "curvature_corrected" in df.columns
        corrected_supplied = has_corrected_theta and has_corrected_curvature
        if geometry == "corrected" and not corrected_supplied:
            missing = sorted({"theta_corrected", "curvature_corrected"}.difference(df.columns))
            raise ValueError(
                f"{p}: geometry='corrected' requires deposited corrected fields: {missing}")
        for _, r in df.iterrows():
            cl = str(r["cell_line"])
            if cell_lines and cl not in cell_lines:
                continue
            disc_raw = r.get("disconnected_sites")
            disconnected = (
                None if "disconnected_sites" not in df.columns or pd.isna(disc_raw)
                else disc_raw is True or str(disc_raw).upper() == "TRUE")
            if drop_disconnected and disconnected:
                continue
            raw_H = float(r["curvature"])
            raw_th = float(r["theta"])
            raw_R = float(r["radius"])
            corrected_H = (float(r["curvature_corrected"])
                           if has_corrected_curvature else None)
            corrected_th = (float(r["theta_corrected"])
                            if has_corrected_theta else None)
            if geometry == "corrected" and not (
                    np.isfinite(corrected_H) and np.isfinite(corrected_th)):
                raise ValueError(
                    f"{p}: geometry='corrected' requires finite deposited "
                    "corrected curvature and angle values")
            # A missing optional correction stays an explicit null in raw mode;
            # this also keeps strict JSON free of NaN sentinels.
            if corrected_H is not None and not np.isfinite(corrected_H):
                corrected_H = None
            if corrected_th is not None and not np.isfinite(corrected_th):
                corrected_th = None
            H, th = ((raw_H, raw_th) if geometry == "raw_nonnegative"
                     else (corrected_H, corrected_th))
            if not np.isfinite(H) or not np.isfinite(th) or H < 0:
                continue
            if not np.isfinite(raw_R):
                continue
            if cl not in seen_cl:
                seen_cl.append(cl)
            sites.append(SMLMSite(
                site_id=int(r["ID"]), cell_line=cl,
                file_number=int(r["file_number"]),
                psi_rad=float(np.radians(th)), theta_deg=th,
                # R/area/projection remain deposited raw geometry. In particular,
                # corrected H=0 does not induce an infinite radius or replacement
                # projected/deposited area calculation.
                H_inv_nm=H, R_nm=abs(raw_R),
                surface_area_nm2=float(r["surface_area"]),
                projected_area_nm2=float(r["projected_area"]),
                H_sigma_inv_nm=(float(_curvature_sigma(abs(raw_R), th))
                                if legacy_curvature_sigma else None),
                raw_theta_deg=raw_th, raw_H_inv_nm=raw_H,
                corrected_theta_deg=corrected_th, corrected_H_inv_nm=corrected_H,
                corrected_geometry_supplied=corrected_supplied,
                raw_R_nm=raw_R,
                rim_length_nm=(float(r["rim_length"])
                               if "rim_length" in df.columns and pd.notna(r["rim_length"])
                               else None),
                disconnected_sites=disconnected,
                source_key=f"{cl}:{int(r['file_number'])}:{int(r['ID'])}",
                source_path=os.path.abspath(p)))
    prov = dict(
        dataset="BioStudies S-BIAD566",
        paper="Mund, Tschanz, ... Ries, J Cell Biol 2023",
        doi="10.1083/jcb.202206038",
        method="3D-SMLM + LocMoFit spherical-cap fit (LocMoFit: Wu et al., "
               "2023, cited in Mund et al. 2023)",
        resolution_xy_nm=RESOLUTION_XY_NM, resolution_z_nm=RESOLUTION_Z_NM,
        loc_precision_xy_nm=LOC_PRECISION_XY_NM,
        loc_precision_z_nm=LOC_PRECISION_Z_NM,
        observation_contract_version=OBSERVATION_CONTRACT_VERSION,
        geometry_selection=geometry,
        drop_disconnected=drop_disconnected,
        radius_area_projection=(
            "deposited raw-fit fields; R_nm magnitude, signed raw_R_nm; "
            "not recomputed from corrected H/theta"),
        curvature_uncertainty=(
            "exploratory_legacy_heuristic_hypot_localization_precision_over_R2"
            if legacy_curvature_sigma else "unknown_processed_tables_lack_fit_covariance"),
        curvature_uncertainty_calibrated=False,
        calibrated_likelihood=False,
        mechanism_inference_allowed=False,
        note="static super-res; deposited geometry only; force_applicable=False")
    return SMLMGeometrySet(sites=sites, cell_lines=seen_cl, provenance=prov)


if __name__ == "__main__":
    fetch_locmofit_fits()
    gs = ingest_locmofit()
    from collections import Counter
    print(f"loaded {len(gs.sites)} sites across {gs.cell_lines}")
    print("by cell line:", dict(Counter(s.cell_line for s in gs.sites)))
    print("force_applicable:", gs.force_applicable)
