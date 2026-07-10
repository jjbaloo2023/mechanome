"""
mechanome/links.py — curated LINKED edges (flagged mechanotransduction hypotheses).

A LINKED claim consumes GROUNDED force outputs and proposes a downstream
mechanotransduction hypothesis. By schema rule it carries an explicit causal
chain and a proposed experiment, and it CANNOT carry a physical value — the
credibility firewall. These are curated from the literature, NOT learned or
computed; each is honest about being correlative.
"""
from __future__ import annotations

from typing import List

from .schema import MechanoClaim, EpistemicTier, Context, Actor


def emit_tension_yap_link() -> MechanoClaim:
    """LINKED: membrane tension modulates YAP nuclear localization.

    The near-term real hub (Piezo1 / YAP-TAZ mechanotransduction). Correlative,
    multi-step signaling — explicitly NOT force balance. No physical value.
    """
    return MechanoClaim(
        subject=Actor("membrane_tension", type="observable"),
        relation="modulates",
        object="YAP_nuclear_localization",
        epistemic_tier=EpistemicTier.LINKED,
        context=Context(scale="cell", cell_type="epithelial"),
        forward_model=None, value=None, identifiability=None,
        evidence=[
            "chain: membrane_tension -> Piezo1 gating -> [Ca2+] influx -> "
            "cytoskeletal/Hippo modulation -> YAP dephosphorylation -> YAP "
            "nuclear translocation (correlative, literature)",
            "hub: Piezo1, YAP/TAZ mechanotransduction (well-attested but multi-step)"],
        reasoning_trace=(
            "PROPOSED TEST (disambiguating): apply hyperosmotic shock to drop "
            "membrane tension while imaging a YAP-nuclear-localization reporter; a "
            "tension-driven link predicts YAP exits the nucleus as tension falls. "
            "Latrunculin (actin disassembly) and a Piezo1 knockdown separate the "
            "channel-dependent path from bulk-cytoskeletal effects. This edge is a "
            "HYPOTHESIS: it consumes curvo's GROUNDED tension output but asserts no "
            "force value of its own — force-to-transcription is correlative, and the "
            "schema forbids a value here."))


def emit_all() -> List[MechanoClaim]:
    return [emit_tension_yap_link()]


if __name__ == "__main__":
    for c in emit_all():
        print(f"[{c.epistemic_tier.value}] {getattr(c.subject,'id',c.subject)} "
              f"{c.relation} {c.object} | value={c.value} (correctly None)")
        print("  chain:", c.evidence[0][:80], "...")
