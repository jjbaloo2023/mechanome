"""
mddb_adapter.py — live adapter to the Molecular Dynamics Data Bank (MDDB).

MDDB (https://mddbr.eu, REST API at https://mmb.mddbr.eu/api/rest/current/) is the
European repository for biosimulation data, modeled on the PDB.
This adapter pulls REAL, per-frame membrane observables from deposited all-atom
MD trajectories and returns them as curvo ParameterRecords with provenance, so
curvo's membrane elastic parameters can be cross-checked against an independent
MD source rather than a single literature value.

WHAT MDDB ACTUALLY SERVES (verified against the live API, 2026):
    Per-project membrane analyses = {mem-map, apl, thickness, lipid-order,
    density, lipid-inter, ...}. These are STRUCTURAL observables.

    MDDB does NOT serve a lateral stress/pressure profile or a membrane-tension
    time series. Extracting a stress profile would require the per-atom virial
    from the full trajectory, which the API does not expose. So MDDB is an
    independent MD source for curvo's membrane elastic PARAMETERS (thickness,
    area-per-lipid), NOT a direct force ground truth. The real force-paired
    validation in this package is validation/tether_sted.py (STED nanotubes with
    micropipette-set tension). This adapter's role is provenance breadth:
    a second, orthogonal source for the structural inputs that set kappa.

The force connection is therefore INDIRECT and stated as such: bilayer thickness
and area-per-lipid constrain the bending rigidity kappa via the polymer-brush
relation kappa ~ k_A * d^2 / beta (Rawicz et al. 2000), and kappa is what sets the
tether force f = 2*pi*sqrt(2 sigma kappa). This adapter surfaces the structural
inputs; it does not claim to measure force.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import requests

API = "https://mmb.mddbr.eu/api/rest/current/"
MEMBRANE_ANALYSES = ("thickness", "apl", "lipid-order", "density", "mem-map")


@dataclass
class MDObservable:
    """A membrane observable extracted from one MDDB project."""
    accession: str
    name: str
    observable: str          # e.g. "bilayer_thickness"
    value: float
    uncertainty: float
    units: str
    n_frames: int
    temperature_K: Optional[float]
    provenance: dict = field(default_factory=dict)


def _get(path, **params):
    r = requests.get(API + path, params=params or None, timeout=60)
    r.raise_for_status()
    return r.json()


def api_online() -> bool:
    try:
        eps = _get("")["endpoints"]
        return "projects" in eps
    except Exception:
        return False


def find_membrane_projects(search="membrane", limit=10):
    """List published projects matching a search term (with membrane analyses)."""
    d = _get("projects", search=search, limit=limit)
    out = []
    for p in d.get("projects", []):
        md = p.get("metadata", {})
        out.append(dict(accession=p["accession"],
                        name=str(md.get("NAME", ""))[:70],
                        temp_K=md.get("TEMP"),
                        pdbids=md.get("PDBIDS")))
    return dict(filtered_count=d.get("filteredCount"), projects=out)


def fetch_thickness(accession: str) -> MDObservable:
    """Fetch the per-frame bilayer-thickness series and reduce to mean +/- fluctuation.

    Thickness is returned by MDDB in Angstrom; we convert to nm (curvo's unit).
    The reported uncertainty is the standard deviation across frames -- a genuine
    MD fluctuation, not a fit error.
    """
    proj = _get(f"projects/{accession}")
    md = proj.get("metadata", {})
    j = _get(f"projects/{accession}/analyses/thickness")["data"]
    th = np.asarray(j["thickness"], float)         # Angstrom, per frame
    th = th[np.isfinite(th)]
    mean_nm = float(th.mean()) / 10.0
    std_nm = float(th.std()) / 10.0
    return MDObservable(
        accession=accession, name=str(md.get("NAME", ""))[:70],
        observable="bilayer_thickness", value=round(mean_nm, 4),
        uncertainty=round(std_nm, 4), units="nm", n_frames=int(th.size),
        temperature_K=float(md["TEMP"]) if md.get("TEMP") else None,
        provenance=dict(source="MDDB", access="live REST API", api=API,
                        identifier=accession, analysis="thickness",
                        retrieved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        citation="Molecular Dynamics Data Bank (MDDB), mddbr.eu; "
                                 "'A new paradigm for molecular dynamics databases', "
                                 "Nucleic Acids Res. 2024, 52:D393-D403, "
                                 "doi:10.1093/nar/gkad991"))


def crosscheck_thickness(accession: str, stored_nm: float = 4.26,
                         stored_source: str = "NMRlipids POPC (curvo parameter_store)"):
    """Cross-check an MDDB thickness against curvo's stored value.

    Returns the MD observable, the stored value, and the z-score of the stored
    value under the MD fluctuation. A |z| within a few sigma means the two
    independent sources agree at the level MD fluctuations allow. NOTE: different
    lipid composition / protein content shifts thickness, so a large offset is
    informative (composition mismatch), not necessarily a contradiction.
    """
    obs = fetch_thickness(accession)
    dz = (stored_nm - obs.value) / obs.uncertainty if obs.uncertainty > 0 else float("nan")
    return dict(
        md_observable=obs.__dict__,
        stored_nm=stored_nm, stored_source=stored_source,
        offset_nm=round(stored_nm - obs.value, 4),
        z_vs_md_fluctuation=round(dz, 2),
        note=("MDDB serves structural observables, not stress profiles; this is a "
              "parameter cross-check, not a force measurement. Thickness offsets "
              "reflect lipid composition / protein content differences between the "
              "MD system and the reference POPC value."))


if __name__ == "__main__":
    if not api_online():
        print("MDDB API unreachable (needs network allowlist for mmb.mddbr.eu)"); raise SystemExit
    hits = find_membrane_projects("membrane", limit=5)
    print(f"MDDB membrane projects: {hits['filtered_count']} match 'membrane'")
    for p in hits["projects"][:3]:
        print("  ", p["accession"], "|", p["name"], "| T=", p["temp_K"])
    cc = crosscheck_thickness("A020P")
    o = cc["md_observable"]
    print(f"\n{o['accession']} thickness = {o['value']} +/- {o['uncertainty']} nm "
          f"({o['n_frames']} frames, T={o['temperature_K']} K)")
    print(f"stored ({cc['stored_source']}) = {cc['stored_nm']} nm | "
          f"offset {cc['offset_nm']} nm | z vs MD fluctuation = {cc['z_vs_md_fluctuation']}")
