#!/usr/bin/env python
"""
family_screen.py — apply the curvo pipeline across the ENTH/epsin and ANTH
structural families to produce a falsifiable, ranked prediction of which
proteins are autonomous membrane-curvature generators.

    python family_screen.py

No family label is given to the pipeline: each protein's wedge and crowding
capacities are derived only from its own AlphaFold pLDDT profile, N-terminal
amphipathic moment, and disordered-tail bulk. Writes outputs/family_screen.json
and outputs/family_screen.png. See README "Can curvo extract new science?".
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curvo import evaluator_tier0 as ev
from curvo import players as pl
from curvo import structure_provider as sp

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

# UniProt IDs — ENTH (epsin) vs ANTH (adaptor) families
FAMILY = {
    "EPN1":  ("Q9Y6I3", "ENTH/epsin"),
    "EPN2":  ("O95208", "ENTH/epsin"),
    "EPN3":  ("Q9H201", "ENTH/epsin"),
    "PICALM": ("Q13492", "ANTH"),
    "HIP1":  ("O00291", "ANTH"),
    "HIP1R": ("O75146", "ANTH"),
}

SIGMA = 0.02
A_PATCH = np.pi * 60 ** 2
KAPPA = 20.0
OMEGA_THR = 0.030


def n_terminal_ah0(model, window: int = 11, scan: int = 40):
    """Max amphipathic-moment window in the N-terminal `scan` residues.

    The ENTH AH0 signature is amphipathy AT the extreme N-terminus, not
    amphipathy anywhere — so we return both the moment and its start position.
    """
    seq = model.sequence
    best = (0.0, None, None)
    for i in range(0, min(scan, len(seq) - window)):
        seg = seq[i:i + window]
        muH = sp.hydrophobic_moment(seg)
        if muH > best[0]:
            best = (muH, i + 1, seg)   # 1-indexed
    return best


def disordered_residues(call) -> int:
    return sum((s["end"] - s["start"] + 1) for s in call["segments"]
               if s["representation"] == "polymer_brush_crowding")


def screen(cache_dir: str = "cache") -> list:
    rows = []
    for name, (up, fam) in FAMILY.items():
        model = sp.fetch_alphafold(up, cache_dir=cache_dir)
        call = sp.representation_call(model)
        muH, start, seg = n_terminal_ah0(model)
        at_nterm = start is not None and start <= 10
        # wedge prior: amphipathic moment GATED by extreme-N-terminal position
        wedge_c0 = min(0.08, 0.11 * muH) if at_nterm else 0.0
        idr = disordered_residues(call)

        contribs = {}
        if wedge_c0 > 0:
            contribs["wedge"] = pl.WedgePlayer().contribution(
                {"c0_contribution_inv_nm": wedge_c0, "tension_half_kBT_nm2": 0.02,
                 "kappa_softening_factor": 0.9}, SIGMA)
        contribs["crowding"] = pl.CrowdingPlayer().contribution(
            {"c_max_inv_nm": 0.05, "coverage": min(1.0, idr / 400.0), "phi_half": 0.3}, SIGMA)
        contribs["coat"] = pl.CoatPlayer().contribution(
            {"rigidity_factor": 3.0, "intrinsic_c0_inv_nm": 0.0}, SIGMA)
        comb = pl.combine_curvature(contribs, coupling_correction=0.25)
        mo = ev.ccs_curvature(comb["c_eff_inv_nm"], SIGMA, KAPPA, A_PATCH,
                              coat_rigidity_factor=comb["kappa_factor"])

        # a flagged case: strong N-terminal moment in a protein whose family is ANTH
        flagged = at_nterm and "ANTH" in fam
        rows.append(dict(name=name, family=fam, uniprot=up, muH=round(muH, 3),
                         ah0_start=start, ah0_seq=seg, at_nterm=at_nterm,
                         wedge_c0=round(wedge_c0, 4), idr_residues=idr,
                         c_eff=round(comb["c_eff_inv_nm"], 4),
                         H_max=round(mo["achieved_mean_curvature_inv_nm"], 4),
                         stage=mo["stage"],
                         crosses_Omega=mo["achieved_mean_curvature_inv_nm"] >= OMEGA_THR,
                         flagged_false_positive=flagged))
    return sorted(rows, key=lambda r: -r["H_max"])


def render(rows, path=f"{OUT}/family_screen.png"):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    names = [r["name"] for r in rows]
    H = [r["H_max"] for r in rows]
    cols = ["#2c6fbb" if "ENTH" in r["family"] else "#c0392b" for r in rows]
    bars = ax.bar(names, H, color=cols, edgecolor="black", linewidth=0.7, zorder=3)
    for b, r in zip(bars, rows):
        if r["flagged_false_positive"]:
            b.set_hatch("///")
            ax.annotate("flagged:\nN-term false positive",
                        (b.get_x() + b.get_width() / 2, r["H_max"] + 0.001),
                        ha="center", va="bottom", fontsize=7, style="italic", color="#555")
    ax.axhline(OMEGA_THR, ls="--", color="#444", lw=1, zorder=2)
    ax.text(len(rows) - 0.6, OMEGA_THR + 0.0007, f"\u03a9 threshold {OMEGA_THR}",
            ha="right", fontsize=7, color="#444")
    ax.set_ylabel("max achievable mean curvature  H  (nm$^{-1}$)")
    ax.set_title("curvo family screen: autonomous curvature capacity\n"
                 "(ENTH/epsin vs ANTH — structure-derived, no family label used)", fontsize=9)
    ax.legend(handles=[Patch(fc="#2c6fbb", ec="k", label="ENTH / epsin"),
                       Patch(fc="#c0392b", ec="k", label="ANTH")],
              loc="upper right", fontsize=7)
    ax.set_ylim(0, 0.037)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return path


def main():
    rows = screen()
    json.dump(rows, open(f"{OUT}/family_screen.json", "w"), indent=2, default=str)
    print(f"{'rank':>4s} {'prot':7s} {'family':11s} {'H_max':>6s} {'stage':>6s} crossesOmega  flag")
    for i, r in enumerate(rows, 1):
        flag = "  <-- FALSE POSITIVE" if r["flagged_false_positive"] else ""
        print(f"{i:>4d} {r['name']:7s} {r['family']:11s} {r['H_max']:>6.4f} "
              f"{r['stage']:>6s} {str(r['crosses_Omega']):>5s}{flag}")
    try:
        render(rows)
        print(f"\nwrote {OUT}/family_screen.png and {OUT}/family_screen.json")
    except ImportError:
        print(f"\nwrote {OUT}/family_screen.json (install matplotlib for the figure)")


if __name__ == "__main__":
    main()
