"""
curvature_sources.py -- pluggable spontaneous-curvature sources for C0_eff.

The coated patch's effective spontaneous curvature is a SUM of independent,
additive contributions from whatever curvature-active objects sit on it:

    C0_eff(phi, sigma) = sum_s  source_s.c0(phi, sigma)          [1/nm]

Each source is a small object exposing .c0(phi, sigma) and .footprint_nm2.
Adding a new protein/mechanism = adding a source object; nothing else changes.
This is the "registry / slots" architecture (see MODEL.md) instantiated for CME
with epsin = {ENTH wedge} + {disordered-CTD steric brush}.

Sign convention: C0 > 0 favors the bud (curves toward the vesicle interior),
consistent with barrier.py.

Parameter provenance (see MODEL.md table for full citations):
    A_ENTH  = 16 nm^2   ENTH-domain membrane footprint      Busch et al. Nat Commun 2015
    A_CTD   = 70 nm^2   epsin disordered-CTD footprint       Busch et al. Nat Commun 2015
    kappa   = 20 kBT    bending rigidity                     standard
    z_bar   ~ 3 nm      steric moment arm (brush centroid    Snead/Stachowiak steric-force
                        above bilayer neutral surface)        scale; order-of-magnitude
    eta_steric ~ 1      steric->curvature efficiency          THE explicit soft joint:
                        (leaflet-asymmetry fraction x          literature fixes it only to
                        geometric detail)                      O(1); swept for sensitivity.
    sigma_star ~ 0.02   tension scale that damps steric       phenomenological (high tension
              mN/m      curvature efficiency                   flattens the asymmetry)

Steric pressure model Pi(phi): 2D hard-disk equation of state (Helfand-Frisch-
Lebowitz scaled-particle),  Pi = (kBT/A_mol) * phi/(1-phi)^2,  which rises steeply
as coverage approaches jamming -- the coverage-dependence Stachowiak reports.
Alexander-de Gennes brush scaling (Pi ~ phi^(9/4)) is provided as an alternative EOS.

Steric -> curvature: first moment of the lateral stress profile (Helfrich),
    kappa * C0_steric = eta_steric * Pi * z_bar,
i.e. an asymmetric lateral pressure Pi acting a distance z_bar off the neutral
surface exerts a bending moment; eta_steric folds in the asymmetric fraction.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

KBT = 1.0  # energies in kBT

# ---------- steric pressure equations of state ----------
def pi_hard_disk(phi, A_mol):
    """2D hard-disk (scaled-particle) lateral pressure [kBT/nm^2]. Pi->inf as phi->1."""
    phi = np.clip(np.asarray(phi, float), 0.0, 0.95)
    return (KBT / A_mol) * phi / (1.0 - phi) ** 2

def pi_brush(phi, A_mol, phi_ref=0.5):
    """Alexander-de Gennes brush scaling Pi ~ phi^(9/4) [kBT/nm^2], matched to
    the hard-disk value at phi_ref so the two EOS are comparable in magnitude."""
    phi = np.clip(np.asarray(phi, float), 0.0, 0.99)
    scale = pi_hard_disk(phi_ref, A_mol) / (phi_ref ** 2.25)
    return scale * phi ** 2.25


class CurvatureSource:
    """Base: a curvature-active object on the coat. Override c0()."""
    name = "source"
    footprint_nm2 = 0.0
    def c0(self, phi, sigma):
        raise NotImplementedError


@dataclass
class CoatSource(CurvatureSource):
    """Clathrin coat scaffold: a fixed intrinsic curvature set by the preferred
    bud radius R_bud. Coverage-independent (the lattice sets the geometry)."""
    R_bud_nm: float = 50.0
    name: str = "clathrin_coat"
    footprint_nm2: float = 0.0
    def c0(self, phi, sigma):
        return np.full_like(np.asarray(phi, float), 2.0 / self.R_bud_nm)


@dataclass
class ENTHWedge(CurvatureSource):
    """ENTH helix-0 amphipathic insertion: a modest, structured wedge curvature
    that scales linearly with adaptor coverage (dilute shallow insertions add up).
    c0 = c0_per_full * phi."""
    c0_per_full: float = 0.035     # 1/nm at phi=1 (structured wedge; modest)
    name: str = "ENTH_wedge"
    footprint_nm2: float = 16.0    # Busch 2015
    def c0(self, phi, sigma):
        return self.c0_per_full * np.asarray(phi, float)


@dataclass
class StericBrush(CurvatureSource):
    """Disordered-CTD steric pressure -> curvature (the dominant epsin mechanism).
    C0 = eta * Pi(phi) * z_bar / kappa, with a tension damping 1/(1+sigma/sigma*)."""
    A_mol: float = 70.0            # nm^2, Busch 2015 (disordered CTD)
    z_bar_nm: float = 3.0          # steric moment arm
    kappa: float = 20.0
    eta: float = 1.0               # efficiency (the explicit soft joint)
    sigma_star: float = 0.00486    # kBT/nm^2  (= 0.02 mN/m) tension damping scale
    eos: str = "hard_disk"         # or "brush"
    name: str = "steric_brush"
    footprint_nm2: float = 70.0
    def pressure(self, phi):
        if self.eos == "brush":
            return pi_brush(phi, self.A_mol)
        return pi_hard_disk(phi, self.A_mol)
    def c0(self, phi, sigma):
        Pi = self.pressure(phi)
        damp = 1.0 / (1.0 + np.asarray(sigma, float) / self.sigma_star)
        return self.eta * Pi * self.z_bar_nm / self.kappa * damp


class CurvatureRegistry:
    """Sums c0 contributions from a list of sources -> C0_eff(phi, sigma)."""
    def __init__(self, sources=None):
        self.sources = list(sources or [])
    def add(self, s):
        self.sources.append(s); return self
    def c0_eff(self, phi, sigma):
        tot = np.zeros_like(np.asarray(phi, float), dtype=float)
        for s in self.sources:
            tot = tot + s.c0(phi, sigma)
        return tot
    def decompose(self, phi, sigma):
        """dict name -> c0 contribution array, for stacked plots."""
        return {s.name: np.asarray(s.c0(phi, sigma), float) for s in self.sources}


# ---- canonical builders for the CME/epsin instantiation ----
def build_control(R_bud_nm=50.0):
    """Coat only (no epsin)."""
    return CurvatureRegistry([CoatSource(R_bud_nm=R_bud_nm)])

def build_epsin_enth_only(R_bud_nm=50.0, **enth):
    """Coat + ENTH wedge (structured curvature only; no steric term)."""
    return CurvatureRegistry([CoatSource(R_bud_nm=R_bud_nm), ENTHWedge(**enth)])

def build_epsin_full(R_bud_nm=50.0, enth=None, steric=None):
    """Coat + ENTH wedge + disordered-CTD steric brush (full epsin)."""
    return CurvatureRegistry([CoatSource(R_bud_nm=R_bud_nm),
                              ENTHWedge(**(enth or {})),
                              StericBrush(**(steric or {}))])
