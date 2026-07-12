"""
mechanome/mechano_schematic.py — render a set of MechanoClaims as a tiered graph.

The single highest-impact visual: it makes the whole thesis legible at a glance.
    GROUNDED nodes  -> solid border
    MEASURED nodes  -> solid, lighter
    LINKED nodes    -> DASHED border (a hypothesis, visibly not a measurement)
Every edge carries its provenance / tier. A LINKED node never shows a value.

Two renderers, same layout: a pure-Python SVG (dependency-free, the 'generalized
curvo schematic') and a matplotlib PNG raster (embeds inline in reports).
"""
from __future__ import annotations

from typing import List, Dict, Tuple

from .schema import MechanoClaim, EpistemicTier

TIER_STYLE = {
    "GROUNDED": dict(edge="#1a7d3c", fill="#e5f4ea", dash=None,   label="GROUNDED"),
    "MEASURED": dict(edge="#2c6fbb", fill="#e7f0fb", dash=None,   label="MEASURED"),
    "LINKED":   dict(edge="#b03a5b", fill="#fbeaf0", dash="6,4", label="LINKED (hypothesis)"),
}


def _node_text(claim: MechanoClaim) -> Tuple[str, str, str]:
    """(title, value_line, tier) for a claim node."""
    subj = getattr(claim.subject, "id", claim.subject)
    title = f"{subj} {claim.relation} {claim.object}"
    if claim.value is not None:
        v = claim.value
        vline = f"{v.estimate} \u00b1 {v.uncertainty} {v.units}  ({claim.identifiability.value})"
    else:
        vline = "no value (hypothesis) \u2014 experiment proposed"
    return title, vline, claim.epistemic_tier.value


# --------------------------------------------------------------------------- #
#  SVG renderer (dependency-free)                                             #
# --------------------------------------------------------------------------- #
def render_svg(claims: List[MechanoClaim], out_path: str,
               title: str = "Mechanome walk \u2014 one query, tiered by how we know it") -> str:
    W, H = 900, 130 + 96 * len(claims)
    x0, bw, bh, gap = 60, 780, 74, 22
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">\n'
         f'<rect width="{W}" height="{H}" fill="white"/>\n')
    s += _svg_text(W / 2, 34, title, 16, "#222", "bold", "middle")
    # legend
    lx = 60
    for t in ("GROUNDED", "MEASURED", "LINKED"):
        st = TIER_STYLE[t]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        s += (f'<rect x="{lx}" y="50" width="16" height="12" fill="{st["fill"]}" '
              f'stroke="{st["edge"]}" stroke-width="2"{dash}/>\n')
        s += _svg_text(lx + 22, 60, st["label"], 11, st["edge"], "bold", "start")
        lx += 210
    # nodes + connecting arrows
    y = 92
    centers = []
    for c in claims:
        title_t, vline, tier = _node_text(c)
        st = TIER_STYLE[tier]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        s += (f'<rect x="{x0}" y="{y}" width="{bw}" height="{bh}" rx="8" '
              f'fill="{st["fill"]}" stroke="{st["edge"]}" stroke-width="2.5"{dash}/>\n')
        s += _svg_text(x0 + 14, y + 24, title_t, 13, "#1a1a1a", "bold", "start")
        s += _svg_text(x0 + 14, y + 44, vline, 11.5,
                       st["edge"] if tier != "LINKED" else "#b03a5b", "normal", "start")
        prov = (c.evidence[0] if c.evidence else "")[:96]
        s += _svg_text(x0 + 14, y + 62, "prov: " + prov, 9.5, "#666", "italic", "start")
        s += _svg_text(x0 + bw - 10, y + 20, st["label"], 10, st["edge"], "bold", "end")
        centers.append((x0 + bw / 2, y, y + bh))
        y += bh + gap
    # arrows between consecutive nodes
    for (cx, _, y_bot), (_, y_top, _) in zip(centers, centers[1:]):
        s += (f'<line x1="{cx}" y1="{y_bot}" x2="{cx}" y2="{y_top}" stroke="#888" '
              f'stroke-width="2" marker-end="url(#a)"/>\n')
    s = s.replace("<rect width",
                  '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="6" refY="3" '
                  'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#888"/></marker></defs>\n<rect width', 1)
    s += "</svg>\n"
    with open(out_path, "w") as f:
        f.write(s)
    return out_path


def _svg_text(x, y, t, size, col, weight, anchor, italic=False):
    style = ' font-style="italic"' if italic else ""
    t = (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{style}>{t}</text>\n')


# --------------------------------------------------------------------------- #
#  matplotlib PNG renderer (embeds inline)                                    #
# --------------------------------------------------------------------------- #
def render_png(claims: List[MechanoClaim], out_path: str,
               title: str = "Mechanome walk \u2014 one query, tiered by how we know it"):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    try:
        apply_figure_style(sizes=(9, 8, 7))   # kernel helper if loaded
    except NameError:
        pass
    n = len(claims)
    fig, ax = plt.subplots(figsize=(9, 1.15 * n + 1.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, n + 0.6); ax.axis("off")
    ax.set_title(title, fontsize=12, weight="bold", pad=14)
    y = n - 0.5
    mids = []
    for c in claims:
        title_t, vline, tier = _node_text(c)
        st = TIER_STYLE[tier]
        ls = "--" if st["dash"] else "-"
        box = FancyBboxPatch((0.4, y - 0.34), 9.2, 0.68,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=2.2, edgecolor=st["edge"], facecolor=st["fill"],
                             linestyle=ls, zorder=2)
        ax.add_patch(box)
        ax.text(0.62, y + 0.14, title_t, fontsize=10.5, weight="bold", va="center", zorder=3)
        vcol = st["edge"]
        ax.text(0.62, y - 0.12, vline, fontsize=9.5, color=vcol, va="center", zorder=3)
        ax.text(9.45, y + 0.20, st["label"], fontsize=8.5, color=st["edge"],
                weight="bold", ha="right", va="center", zorder=3)
        prov = (c.evidence[0] if c.evidence else "")[:82]
        ax.text(0.62, y - 0.27, "prov: " + prov, fontsize=7.2, color="#666",
                style="italic", va="center", zorder=3)
        mids.append(y)
        y -= 1.15
    for y_top, y_bot in zip(mids, mids[1:]):
        ax.add_patch(FancyArrowPatch((5, y_top - 0.36), (5, y_bot + 0.36),
                     arrowstyle="-|>", mutation_scale=14, color="#888", lw=1.8, zorder=1))
    fig.tight_layout()
    fig.savefig(out_path, dpi=175, bbox_inches="tight")
    import matplotlib.pyplot as _plt; _plt.close(fig)
    return out_path


def flagship_walk() -> List[MechanoClaim]:
    """The demo spine: GROUNDED force -> GROUNDED capacity -> LINKED YAP hypothesis."""
    from . import emit, links
    claims = [emit.emit_tether_force_claim()]
    claims += emit.emit_family_capacity_claims(top=1)   # epsin EPN1
    claims += links.emit_all()                          # the dashed YAP edge
    return claims


if __name__ == "__main__":
    cl = flagship_walk()
    render_svg(cl, "outputs/mechanome_schematic.svg")
    render_png(cl, "outputs/mechanome_schematic.png")
    print(f"rendered {len(cl)} tiered claims -> mechanome_schematic.svg / .png")
