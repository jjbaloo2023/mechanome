"""Resolve cited parameters and record their source, uncertainty, and validity.

The NMRlipids adapter reads a time series over HTTP or from a local cache.
Insertion depth and the literature table use curated values. Unimplemented
sources raise KeyError; coverage() lists them as missing.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import numpy as np
import requests

from .schemas import ParameterRecord, Provenance, StatePoint

GH_RAW = "https://raw.githubusercontent.com/NMRLipids/Databank/main/{}"


# --------------------------------------------------------------------------
# Curated literature table (real, cited values). This is the anchor.
# --------------------------------------------------------------------------
# Monolayer spontaneous curvature c0 (nm^-1), sign convention: negative => tendency
# to curve toward the water (Type II / negative-curvature lipid). Rand & Fuller 1994;
# Kollmitzer et al. 2013 (Soft Matter) for PC/PE/PS at 35C.
LITERATURE = {
    # param, lipid/system : (value, uncertainty, units, T_K, composition, valid_range, citation)
    ("c0", "DOPC"):   (-0.091, 0.02, "nm^-1", 308, "DOPC", {"temperature_K": [298, 320]},
                       "Kollmitzer et al. 2013 Soft Matter 9:10877"),
    ("c0", "DOPE"):   (-0.399, 0.03, "nm^-1", 308, "DOPE", {"temperature_K": [298, 320]},
                       "Kollmitzer et al. 2013 Soft Matter 9:10877"),
    ("c0", "POPC"):   (-0.022, 0.02, "nm^-1", 308, "POPC", {"temperature_K": [298, 320]},
                       "Kollmitzer et al. 2013 Soft Matter 9:10877"),
    ("c0", "DOPS"):   (-0.100, 0.03, "nm^-1", 308, "DOPS", {"temperature_K": [298, 320]},
                       "Kollmitzer et al. 2013 Soft Matter 9:10877"),
    ("c0", "PIP2"):   (-0.050, 0.04, "nm^-1", 298, "PI(4,5)P2", {"temperature_K": [293, 310]},
                       "estimate from headgroup geometry; conical (Kooijman 2009 JBC)"),
    # Bending rigidity kappa (kBT). Dimova 2014 review; Nagle 2013.
    ("kappa", "POPC"): (20.0, 3.0, "kBT", 303, "POPC", {"temperature_K": [298, 320]},
                        "Dimova 2014 Adv Colloid Interface Sci 208:225"),
    ("kappa", "DOPC"): (19.0, 3.0, "kBT", 303, "DOPC", {"temperature_K": [298, 320]},
                        "Dimova 2014"),
    ("kappa", "SOPC"): (25.0, 4.0, "kBT", 303, "SOPC", {"temperature_K": [298, 320]},
                        "Dimova 2014"),
    # Line tension lambda at Lo/Ld domain boundary (pN). Garcia-Saez 2007; Tian 2007; Honerkamp-Smith 2008.
    ("lambda_line", "DPPC/DOPC/Chol"): (1.0, 0.5, "pN", 298, "DPPC:DOPC:Chol coexistence",
                                        {"temperature_K": [293, 300]},
                                        "Garcia-Saez et al. 2007 JBC 282:33537"),
    ("lambda_line", "DSPC/DOPC/Chol"): (3.3, 1.0, "pN", 298, "DSPC:DOPC:Chol coexistence",
                                        {"temperature_K": [293, 300]},
                                        "Honerkamp-Smith et al. 2008 Biophys J"),
}


def literature(param: str, system: str) -> ParameterRecord:
    v, u, units, T, comp, vr, cite = LITERATURE[(param, system)]
    return ParameterRecord(
        param=param, value=v, uncertainty=u, units=units,
        state_point=StatePoint(temperature_K=T, composition=comp),
        provenance=Provenance(source=f"literature:{cite.split()[0]}", access="cached",
                              identifier=system, citation=cite),
        valid_range=vr,
    )


# --------------------------------------------------------------------------
# LIVE adapter: NMRlipids / FAIRMD databank (area/leaflet, thickness)
# --------------------------------------------------------------------------
_DEFAULT_SIM = "src/fairmd/lipids/data/ToyData/Simulations.2/aa2"
# Source composition and temperature are recorded in this simulation's README:
# https://raw.githubusercontent.com/NMRLipids/Databank/main/src/fairmd/lipids/data/ToyData/Simulations.2/aa2/README.yaml
_DEFAULT_COMPOSITION = "POPC:CHOL 120:8"


def nmrlipids_area_per_lipid(sim_path: str = _DEFAULT_SIM, cache_dir: str = "cache",
                             lipid: str = "POPC") -> ParameterRecord:
    """Average the time series after discarding its first 20%.

    Keep each simulation's cache separate. HTTP and JSON failures may use a
    previously validated cache; filesystem and data-shape errors propagate.
    The default example contains cholesterol. Custom simulation metadata is
    caller-supplied; this adapter does not retrieve its composition or temperature.
    """
    default_simulation = sim_path == _DEFAULT_SIM
    if default_simulation and lipid != "POPC":
        raise ValueError(f"default simulation is {_DEFAULT_COMPOSITION}; cannot relabel it as {lipid}")
    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_name = f"nmrlipids_apl_{hashlib.sha256(sim_path.encode()).hexdigest()}.json"
    cache = cache_root / cache_name
    access = "live_api"
    try:
        response = requests.get(GH_RAW.format(sim_path + "/apl.json"), timeout=15)
        response.raise_for_status()
        apl = response.json()
    except (requests.RequestException, ValueError):
        if not cache.is_file():
            raise
        saved = json.loads(cache.read_text(encoding="utf-8"))
        if not isinstance(saved, dict) or saved.get("simulation") != sim_path:
            raise ValueError("cached simulation identity mismatch")
        apl = saved["data"]
        digest = hashlib.sha256(json.dumps(apl, sort_keys=True, allow_nan=False).encode()).hexdigest()
        if saved.get("sha256") != digest:
            raise ValueError("cached payload checksum mismatch")
        access = "cached"
    series = np.asarray(apl, dtype=float)
    if (
        series.ndim != 2 or series.shape[0] == 0 or series.shape[1] != 2
        or not np.all(np.isfinite(series)) or np.any(series[:, 1] <= 0)
    ):
        raise ValueError("area-per-lipid data must be finite [time, positive area] pairs")
    digest = hashlib.sha256(json.dumps(apl, sort_keys=True, allow_nan=False).encode()).hexdigest()
    if access == "live_api":
        cache.write_text(json.dumps(dict(simulation=sim_path, sha256=digest, data=apl)), encoding="utf-8")
    arr = series[:, 1]
    eq = arr[len(arr) // 5:]
    mean, sd = eq.mean() / 100.0, eq.std() / 100.0   # A^2 -> nm^2
    return ParameterRecord(
        param="area_per_lipid", value=round(float(mean), 4), uncertainty=round(float(sd), 4),
        units="nm^2", state_point=StatePoint(
            temperature_K=303 if default_simulation else None,
            composition=_DEFAULT_COMPOSITION if default_simulation else lipid,
            notes="MD time-series mean after discarding 20%; uncertainty is temporal SD",
        ),
        provenance=Provenance(source="NMRlipids/FAIRMD databank", access=access,
                              identifier=sim_path,
                              model_version=f"payload_sha256:{digest}",
                              citation="Kiirikki et al. 2024 Nat Commun (NMRlipids Databank)"),
        valid_range={},
        flags=["example_mixed_bilayer"] if default_simulation else ["simulation_metadata_unverified"],
    )


# --------------------------------------------------------------------------
# OPM adapter: H0 insertion depth (curated -- OPM host serves a JS SPA, no open JSON)
# --------------------------------------------------------------------------
def opm_insertion_depth(system: str = "ENTH_H0") -> ParameterRecord:
    """H0 amphipathic-helix insertion depth below the phosphate plane.
    Curated from OPM-class measurements for ENTH/epsin (Ford 2002; Lai 2012)."""
    return ParameterRecord(
        param="insertion_depth", value=0.9, uncertainty=0.3, units="nm",
        state_point=StatePoint(composition="PIP2-containing bilayer",
                               notes="H0 inserts ~1 helical turn into cis leaflet"),
        provenance=Provenance(source="OPM-class / literature", access="cached",
                              identifier=system,
                              citation="Ford et al. 2002 Nature 419:361; Lai et al. 2012 JMB"),
        valid_range={},
        flags=["curated_OPM_SPA_no_open_json"],
    )


# --------------------------------------------------------------------------
# The store
# --------------------------------------------------------------------------
class ParameterStore:
    """Uniform access + a local cache of every resolved record for provenance."""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.records: list[ParameterRecord] = []

    def get(self, param: str, system: str, target: StatePoint | None = None) -> ParameterRecord:
        """Resolve a parameter, preferring live adapters, falling back to literature.

        If a target state point is given and the resolved record does not apply
        there, the record is returned with a 'state_point_mismatch' flag so the
        orchestrator can decide use-data vs flag-MD (see md_gap_queue)."""
        rec = self._resolve(param, system)
        if target is not None:
            ok, why = rec.applies_at(target)
            if not ok:
                flag = "applicability_unknown" if why.startswith("unknown applicability") else "state_point_mismatch"
                rec.flags = list(rec.flags) + [f"{flag}:{why}"]
        self.records.append(rec)
        return rec

    def _resolve(self, param: str, system: str) -> ParameterRecord:
        if param == "area_per_lipid":
            return nmrlipids_area_per_lipid(lipid=system, cache_dir=self.cache_dir)
        if param == "insertion_depth":
            return opm_insertion_depth(system)
        if (param, system) in LITERATURE:
            return literature(param, system)
        raise KeyError(f"No adapter or literature entry for ({param}, {system})")

    def coverage(self) -> list[dict]:
        """List resolved sources and missing adapters for the coverage figure."""
        rows = []
        catalogue = [
            ("area_per_lipid", "POPC", "P1 lipid"),
            ("c0", "PIP2", "P1 lipid"),
            ("c0", "POPC", "P1 lipid"),
            ("c0", "DOPE", "P1 lipid"),
            ("kappa", "POPC", "membrane"),
            ("insertion_depth", "ENTH_H0", "P3 wedge"),
            ("lambda_line", "DPPC/DOPC/Chol", "P5 phase"),
            ("scaffold_deformation", "ENTH", "P2 scaffold"),
        ]
        for param, system, player in catalogue:
            try:
                rec = self._resolve(param, system)
                rows.append(dict(param=param, system=system, player=player,
                                 access=rec.provenance.access, source=rec.provenance.source,
                                 value=rec.value, units=rec.units))
            except KeyError:
                rows.append(dict(param=param, system=system, player=player,
                                 access="missing", source="-", value=None, units="-"))
        return rows
