"""
curvo.structure_provider — public ML models as pre-existing data.

A single provider interface so AlphaFold DB (and, later, ESMFold / ColabFold)
is *pre-existing data, not fresh compute*. The key move: pLDDT drives the
representation choice, cross-checked against an INDEPENDENT disorder signal
(TOP-IDP composition scale) so a "confidently folded IDR" is flagged, not
silently trusted, and an amphipathic-moment test that must pass before a folded
domain is called a membrane wedge.

Nothing here decides physics by fiat: it produces *signals* (pLDDT, disorder
z-score, hydrophobic moment) that the orchestrator's search consumes. The
representation labels emitted are the priors/guardrail outputs described in
README § Design and development.
"""
from __future__ import annotations

import math
import os
from urllib.request import urlretrieve

import numpy as np
import requests

from .schemas import Provenance, StructureModel

# --------------------------------------------------------------------------
# Constants (all real, cited scales)
# --------------------------------------------------------------------------
THREE2ONE = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q',
    'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
    'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
    'TYR': 'Y', 'VAL': 'V',
}

# TOP-IDP disorder-propensity scale (Campen et al. 2008, Protein Pept Lett 15:956).
# Positive = disorder-promoting. Independent of pLDDT -> valid cross-check.
TOP_IDP = {
    'W': -0.884, 'F': -0.697, 'Y': -0.510, 'I': -0.486, 'M': -0.397, 'L': -0.326,
    'V': -0.121, 'N': 0.007, 'C': 0.020, 'T': 0.059, 'A': 0.060, 'G': 0.166,
    'R': 0.180, 'D': 0.192, 'H': 0.303, 'Q': 0.318, 'S': 0.341, 'K': 0.586,
    'E': 0.736, 'P': 0.987, 'X': 0.0,
}

# Eisenberg consensus hydrophobicity (Eisenberg et al. 1984) for helix amphipathy.
EISENBERG = {
    'A': 0.62, 'R': -2.53, 'N': -0.78, 'D': -0.90, 'C': 0.29, 'Q': -0.85,
    'E': -0.74, 'G': 0.48, 'H': -0.40, 'I': 1.38, 'L': 1.06, 'K': -1.50,
    'M': 0.64, 'F': 1.19, 'P': 0.12, 'S': -0.18, 'T': -0.05, 'W': 0.81,
    'Y': 0.26, 'V': 1.08, 'X': 0.0,
}

AF_API = "https://alphafold.ebi.ac.uk/api/prediction/{}"


# --------------------------------------------------------------------------
# Provider
# --------------------------------------------------------------------------
def fetch_alphafold(uniprot: str, cache_dir: str = "cache") -> StructureModel:
    """Default zero-compute path: precomputed structure from AlphaFold DB."""
    os.makedirs(cache_dir, exist_ok=True)
    meta = requests.get(AF_API.format(uniprot), timeout=30).json()
    meta = meta[0] if isinstance(meta, list) else meta
    pdb_path = os.path.join(cache_dir, f"AF-{uniprot}.pdb")
    if not os.path.exists(pdb_path):
        urlretrieve(meta["pdbUrl"], pdb_path)
    seq, plddt = _parse_af_pdb(pdb_path)
    prov = Provenance(
        source="AlphaFoldDB", access="live_api", identifier=uniprot,
        model_version=meta.get("latestVersion", meta.get("modelCreatedDate", "v?")),
        citation="Jumper et al. 2021 Nature; Varadi et al. 2022 NAR (AlphaFold DB)",
    )
    return StructureModel(uniprot_id=uniprot, sequence=seq,
                          per_residue_pLDDT=plddt, provenance=prov,
                          coords_path=pdb_path, pae_available=True)


def _parse_af_pdb(path: str):
    seq, plddt, seen = [], [], set()
    with open(path) as f:
        for line in f:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                resnum = int(line[22:26])
                if resnum in seen:
                    continue
                seen.add(resnum)
                seq.append(THREE2ONE.get(line[17:20].strip(), 'X'))
                plddt.append(float(line[60:66]))
    return "".join(seq), plddt


# --------------------------------------------------------------------------
# Signals
# --------------------------------------------------------------------------
def top_idp_profile(seq: str, window: int = 21) -> np.ndarray:
    n, half = len(seq), window // 2
    out = np.zeros(n)
    for i in range(n):
        a, b = max(0, i - half), min(n, i + half + 1)
        out[i] = np.mean([TOP_IDP.get(c, 0.0) for c in seq[a:b]])
    return out


def hydrophobic_moment(seq: str, angle: float = 100.0) -> float:
    """Eisenberg mean hydrophobic moment <muH> on a helical wheel (100 deg/res)."""
    n = len(seq)
    sx = sum(EISENBERG.get(c, 0) * math.cos(math.radians(angle * i)) for i, c in enumerate(seq))
    sy = sum(EISENBERG.get(c, 0) * math.sin(math.radians(angle * i)) for i, c in enumerate(seq))
    return math.hypot(sx, sy) / n


def segment_by_plddt(plddt, hi: float = 70.0, min_len: int = 15, gap: int = 5):
    """Segment into folded (>=hi) vs disordered runs; close short gaps."""
    pl = np.array(plddt)
    sm = pl >= hi
    n, i = len(sm), 0
    while i < n:
        if not sm[i]:
            j = i
            while j < n and not sm[j]:
                j += 1
            if (j - i) <= gap and i > 0 and j < n:
                sm[i:j] = True
            i = j
        else:
            i += 1
    segs, i = [], 0
    while i < n:
        state, j = sm[i], i
        while j < n and sm[j] == state:
            j += 1
        segs.append((i + 1, j, "folded" if state else "disordered", float(pl[i:j].mean())))
        i = j
    merged = []
    for s in segs:
        if merged and merged[-1][2] == s[2]:
            a, _, t, _ = merged[-1]
            merged[-1] = (a, s[1], t, float(pl[a - 1:s[1]].mean()))
        else:
            merged.append(list(s))
    return [tuple(m) for m in merged]


# --------------------------------------------------------------------------
# The representation call (guardrail output; consumed by orchestrator search)
# --------------------------------------------------------------------------
AMPHI_THRESHOLD = 0.35   # Eisenberg <muH> above which a helix is amphipathic


def representation_call(model: StructureModel, min_seg: int = 12) -> dict:
    """Turn pLDDT + disorder cross-check + amphipathy into per-segment calls.

    verdicts:
      folded_confirmed        high pLDDT, compositionally ordered  -> rigid inclusion (+wedge if amphipathic)
      conditional_fold_suspect high pLDDT but disorder-promoting   -> FLAG, ensemble (do not trust pose)
      disorder_confirmed      low pLDDT + disorder-promoting comp  -> polymer-brush crowding + ensemble
      disorder_ambiguous      low pLDDT but order-promoting comp   -> FLAG
    """
    seq, pl = model.sequence, np.array(model.per_residue_pLDDT)
    di = top_idp_profile(seq)
    z = (di - di.mean()) / di.std()
    calls = []
    for a, b, t, m in segment_by_plddt(pl):
        if (b - a + 1) < min_seg:
            continue
        seg_z = float(z[a - 1:b].mean())
        muH = hydrophobic_moment(seq[a - 1:min(a - 1 + 18, b)])  # N-terminal ~helix of segment
        amphipathic = muH > AMPHI_THRESHOLD
        flag = None
        if t == "folded":
            if seg_z < 0.5:
                verdict = "folded_confirmed"
                rep = "rigid_inclusion_wedge" if amphipathic else "rigid_inclusion"
            else:
                verdict = "conditional_fold_suspect"
                rep = "ensemble_flagged"
                flag = "high_pLDDT_but_disorder_promoting_composition"
        else:
            if seg_z > 0:
                verdict = "disorder_confirmed"
                rep = "polymer_brush_crowding"
            else:
                verdict = "disorder_ambiguous"
                rep = "ensemble_flagged"
                flag = "low_pLDDT_but_order_promoting_composition"
        calls.append(dict(
            start=a, end=b, n=b - a + 1, mean_pLDDT=round(m, 1),
            disorder_z=round(seg_z, 2), hydrophobic_moment=round(muH, 3),
            amphipathic=amphipathic, verdict=verdict, representation=rep,
            guardrail_flag=flag,
        ))
    return {
        "uniprot_id": model.uniprot_id,
        "n_residues": model.n_residues,
        "mean_pLDDT": round(float(pl.mean()), 1),
        "provenance": model.provenance.to_dict(),
        "signals_used": ["per_residue_pLDDT (AlphaFold)",
                         "TOP-IDP composition disorder (Campen 2008)",
                         "Eisenberg hydrophobic moment"],
        "segments": calls,
    }
