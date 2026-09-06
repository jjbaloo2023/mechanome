"""
mechanome/channel_link.py -- the structural-screen -> channel cross-scale link.

The structural screen (mechanome.structural_screen) ranks membrane proteins by a
structure-derived spontaneous curvature c0 and signed curvature capacity. Its
mechanosensitive-channel hits are the *structural* counterpart to the channel
gating forward model (mechanome.forward_channel / registry ms_gating_v1): the
screen supplies each channel's structure-derived c0, and the gating model turns
membrane tension into an open probability. This module is the explicit seam that
carries a channel from the screen's molecule-scale ranking into the
membrane-scale gating model -- one edge grounded on both ends.

    channels_from_screen()      -> the screen's mechanosensitive-channel rows
    link_channel_to_gating(...) -> a channel's screen c0 + its gating Po(sigma)
"""

from __future__ import annotations

from typing import List, Dict, Optional

from . import structural_screen as _screen
from . import forward_channel as _ch

# Screen protein name -> canonical channel label (those with a gating forward model).
MECHANOSENSITIVE_CHANNELS = {
    "MscL": "MscL",
    "MscS": "MscS",
    "Piezo1": "Piezo1",
    "TRAAK (K2P4.1)": "TRAAK",
    "TREK-1 (K2P2.1)": "TREK-1",
    "OSCA1.2": "OSCA1.2",
    "TRPV4": "TRPV4",
}


def channels_from_screen() -> List[Dict]:
    """The screen's mechanosensitive-channel rows (protein, structure-derived c0,
    signed capacity, gate flag), in ranking order. This is the molecule-scale
    input the channel gating model consumes."""
    rk = _screen.frozen_ranking()
    # the frozen CSV carries the five audited columns; pull c0 from the full
    # stage-3 ranking, joined on protein name.
    full = _screen.full_ranking()
    c0 = dict(zip(full["protein"], full["c0_invnm"]))
    out = []
    for _, row in rk.iterrows():
        name = row["protein"]
        if name in MECHANOSENSITIVE_CHANNELS:
            out.append(
                {
                    "protein": name,
                    "channel": MECHANOSENSITIVE_CHANNELS[name],
                    "c0_inv_nm": float(c0.get(name, float("nan"))),
                    "signed_capacity_kBT": float(row["E_curv_signed"]),
                    "clears_gate": bool(row["clears_gate"]),
                }
            )
    return out


def link_channel_to_gating(
    protein: str,
    sigma_mN_m: float,
    dA_nm2: float = _ch.MSCL_DA_nm2,
    dG_kBT: Optional[float] = None,
) -> Dict:
    """Carry one channel from the screen into the gating model: report its
    structure-derived spontaneous curvature (from the screen) alongside its
    tension-dependent open probability (from ms_gating_v1) at ``sigma_mN_m``.

    dA/dG default to the MscL anchor; pass channel-specific values when known.
    Returns a dict linking the molecule-scale c0 to the membrane-scale Po.
    """
    # accept either the screen's protein key ("TRAAK (K2P4.1)") or the friendly
    # channel display name ("TRAAK") that channels_from_screen() surfaces.
    screened = channels_from_screen()
    rows = {}
    for c in screened:
        rows[c["protein"]] = c
        rows[c["channel"]] = c
    if protein not in rows:
        choices = sorted({c["channel"] for c in screened})
        raise KeyError(
            f"{protein!r} is not a screened mechanosensitive channel; "
            f"choose from {choices}"
        )
    c = rows[protein]
    if dG_kBT is None:
        # place the midpoint at the MscL anchor tension by default
        dG_kBT = _ch.MSCL_SIGMA_HALF_mN_m * dA_nm2 / _ch.KBT_PN_NM
    return {
        "protein": protein,
        "channel": c["channel"],
        "structural_c0_inv_nm": c["c0_inv_nm"],  # from the screen (molecule scale)
        "signed_capacity_kBT": c["signed_capacity_kBT"],
        "sigma_mN_m": sigma_mN_m,
        "open_probability": _ch.open_probability(
            sigma_mN_m, dA_nm2, dG_kBT
        ),  # gating (membrane scale)
        "gating_model": "ms_gating_v1",
        "source_model": "structural_screen_v1",
    }


if __name__ == "__main__":
    import json

    print("Screened mechanosensitive channels (structure-derived c0):")
    for c in channels_from_screen():
        print(
            f"  {c['channel']:9s} c0={c['c0_inv_nm']:+.4f} /nm  "
            f"signed_capacity={c['signed_capacity_kBT']:+6.2f} kBT"
        )
    print("\nExample link (MscL at its midpoint tension 11.8 mN/m):")
    print(json.dumps(link_channel_to_gating("MscL", 11.8), indent=2))
