"""
curvo.parameter_store — the "use existing data" backbone.

Adapters return uniform ParameterRecords {value, uncertainty, units,
state_point, provenance, valid_range}. Every record knows the state point it
was measured at and the range it is valid over, so the orchestrator can decide
use-data vs flag-MD (schemas.ParameterRecord.applies_at).

Adapter status this sprint:
  - NMRlipids/FAIRMD : LIVE (GitHub-hosted databank data; example bilayer set)
  - AlphaFold DB     : LIVE (structure_provider.py)
  - OPM              : SPA (no open JSON on the allowlisted host) -> curated insertion depth
  - MemProtMD        : host not on allowlist -> stubbed deformation context (P2, not a demo player)
  - literature table : CURATED (Rand-Fuller c0, kappa per lipid, line tensions) -- always the
                       physically load-bearing anchor for c0/lambda, which no open API serves cleanly.

Nothing is silently faked: access="live_api"|"cached"|"stub" is stamped on every record.
"""
from __future__ import annotations

import json
import os
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


def nmrlipids_area_per_lipid(sim_path: str = _DEFAULT_SIM, cache_dir: str = "cache",
                             lipid: str = "POPC") -> ParameterRecord:
    """LIVE: pull area-per-lipid time series from the NMRlipids databank and
    reduce to a value+uncertainty (equilibrated mean, first 20% discarded)."""
    os.makedirs(cache_dir, exist_ok=True)
    cache = os.path.join(cache_dir, "nmrlipids_apl.json")
    access = "live_api"
    try:
        apl = requests.get(GH_RAW.format(sim_path + "/apl.json"), timeout=15).json()
        json.dump(apl, open(cache, "w"))
    except Exception:
        apl = json.load(open(cache))  # fall back to cache if rate-limited
        access = "cached"
    arr = np.array([v for _, v in apl])
    eq = arr[len(arr) // 5:]
    mean, sd = eq.mean() / 100.0, eq.std() / 100.0   # A^2 -> nm^2
    return ParameterRecord(
        param="area_per_lipid", value=round(float(mean), 4), uncertainty=round(float(sd), 4),
        units="nm^2", state_point=StatePoint(temperature_K=303, composition=lipid,
                                             notes="atomistic MD, equilibrated"),
        provenance=Provenance(source="NMRlipids/FAIRMD databank", access=access,
                              identifier=sim_path,
                              citation="Kiirikki et al. 2024 Nat Commun (NMRlipids Databank)"),
        valid_range={"temperature_K": [298, 320]},
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
# MemProtMD adapter: STUBBED (host not on allowlist; P2 scaffold, not a demo player)
# --------------------------------------------------------------------------
def memprotmd_deformation(system: str = "ENTH") -> ParameterRecord:
    return ParameterRecord(
        param="scaffold_deformation", value=0.0, uncertainty=0.5, units="nm",
        state_point=StatePoint(notes="CG self-assembly bilayer deformation context"),
        provenance=Provenance(source="MemProtMD", access="stub", identifier=system,
                              citation="Newport et al. 2019 NAR (MemProtMD) — host not reachable this sprint"),
        valid_range={}, flags=["stub_domain_not_on_allowlist", "P2_not_a_demo_player"],
    )


# --------------------------------------------------------------------------
# The store
# --------------------------------------------------------------------------
class ParameterStore:
    """Uniform access + a local cache of every resolved record for provenance."""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.records: list[ParameterRecord] = []

    def _log(self, rec: ParameterRecord) -> ParameterRecord:
        self.records.append(rec)
        return rec

    def get(self, param: str, system: str, target: StatePoint | None = None) -> ParameterRecord:
        """Resolve a parameter, preferring live adapters, falling back to literature.

        If a target state point is given and the resolved record does not apply
        there, the record is returned with a 'state_point_mismatch' flag so the
        orchestrator can decide use-data vs flag-MD (see md_gap_queue)."""
        rec = self._resolve(param, system)
        if target is not None:
            ok, why = rec.applies_at(target)
            if not ok:
                rec.flags = list(rec.flags) + [f"state_point_mismatch:{why}"]
        return self._log(rec)

    def _resolve(self, param: str, system: str) -> ParameterRecord:
        if param == "area_per_lipid":
            return nmrlipids_area_per_lipid(lipid=system, cache_dir=self.cache_dir)
        if param == "insertion_depth":
            return opm_insertion_depth(system)
        if param == "scaffold_deformation":
            return memprotmd_deformation(system)
        if (param, system) in LITERATURE:
            return literature(param, system)
        raise KeyError(f"No adapter or literature entry for ({param}, {system})")

    def coverage(self) -> list[dict]:
        """What is covered live vs cached vs stubbed — for the coverage figure."""
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
