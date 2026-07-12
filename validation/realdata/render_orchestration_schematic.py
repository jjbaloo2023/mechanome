"""
render_orchestration_schematic.py — the three-stage CME orchestration schematic.

Drawn in the visual idiom of Joseph et al. (Commun Biol 2020, Fig. 3g): an
explicit phospholipid bilayer with domain-coloured epsin. The three panels are
the maturation stages curvo reasons over (flat -> dome -> Omega/scission),
showing which actor does what and what curvo can or cannot recover at each stage.

The membrane bulges upward with the clathrin coat on the cytoplasmic (top) face,
so actin — a cytoplasmic filament system — is drawn ABOVE the upper leaflet at
each neck, with force arrows pushing inward toward the neck (constriction).
cytoplasm/extracellular side cues pin the orientation.

Run:  python -m validation.realdata.render_orchestration_schematic
Output: outputs/orchestration_schematic.png
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Circle

COL = dict(clathrin="#2f8f4e", enth="#2f4fb0", h0="#7d3fa0", arm="#e08a30",
           idp="#c0392b", actin="#a01c3a", head="#d9b88f", tail="#b8a37a")


def draw_clathrin_lattice(ax, cx, cy, r, span_deg, n_tri=5, color=None):
    """A curved clathrin lattice arc; span_deg controls how far it wraps."""
    color = color or COL["clathrin"]
    a0 = 90 - span_deg / 2
    a1 = 90 + span_deg / 2
    angs = np.deg2rad(np.linspace(a0, a1, n_tri))
    pts = np.array([(cx + r * np.cos(a), cy + r * np.sin(a) - r) for a in angs])
    for i in range(len(pts) - 1):
        ax.plot(pts[[i, i + 1], 0], pts[[i, i + 1], 1], color=color, lw=2.4,
                zorder=5, solid_capstyle="round")
    for (px, py) in pts:
        ax.add_patch(Circle((px, py), 0.03, fc=color, ec="white", lw=0.5, zorder=6))
    return pts


def bilayer_bulge(ax, x0, x1, y, bulge, cx, width, n=30, r=0.042, h=0.12):
    """Explicit bilayer between x0..x1, invaginated upward by a Gaussian bulge
    centred at cx. Returns the top-leaflet-baseline profile as a callable."""
    xs = np.linspace(x0, x1, n)
    for x in xs:
        d = bulge * np.exp(-((x - cx) / (width * 0.5)) ** 2)
        yc = y + d
        ax.add_patch(Circle((x, yc + h), r, fc=COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc + h - r, yc + r * 0.5], color=COL["tail"], lw=0.7, zorder=1)
        ax.add_patch(Circle((x, yc - h), r, fc=COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc - h + r, yc - r * 0.5], color=COL["tail"], lw=0.7, zorder=1)
    return lambda x: y + bulge * np.exp(-((x - cx) / (width * 0.5)) ** 2)


def epsin_at(ax, x, ymemb_top, reach=0.15):
    """A cartoon epsin at membrane position x: green clathrin coil, blue ENTH
    sheet, purple H0 wedge inserted into the upper leaflet, orange arm, red IDP."""
    tt = np.linspace(0, 1, 30)
    ax.plot(x + 0.02 * np.sin(tt * 7 * np.pi), ymemb_top + 0.06 + tt * reach,
            color=COL["clathrin"], lw=1.8, zorder=6)
    ax.add_patch(mpl.patches.FancyBboxPatch((x - 0.035, ymemb_top + 0.0), 0.07, 0.07,
        boxstyle="round,pad=0.004", fc=COL["enth"], ec="#1c2f6b", lw=0.7, zorder=6))
    ax.add_patch(mpl.patches.Polygon(
        [[x - 0.022, ymemb_top + 0.02], [x + 0.022, ymemb_top + 0.02], [x, ymemb_top - 0.05]],
        closed=True, fc=COL["h0"], ec="#4d2166", lw=0.7, zorder=7))
    ax.add_patch(mpl.patches.FancyArrowPatch((x + 0.02, ymemb_top + 0.06), (x + 0.09, ymemb_top + 0.0),
        connectionstyle="arc3,rad=0.4", arrowstyle="-", lw=1.6, color=COL["arm"], zorder=5))
    ax.plot(x - 0.05 + 0.015 * np.sin(tt * 5 * np.pi), ymemb_top + 0.02 + tt * 0.10,
            color=COL["idp"], lw=1.2, zorder=5)


def render(out_path="outputs/orchestration_schematic.png"):
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.4))
    stages = [
        ("i) Flat / initiation", "flat", 0.0, 60,
         "Clathrin nucleates a flat lattice. Epsin\nENTH+H\u2080 engages the bilayer; the H\u2080\namphipathic wedge senses membrane tension.",
         "curvo \u2014 geometry \u2248 flat (\u03a9\u22480):\nforce UNDETERMINED (no shape change yet)"),
        ("ii) Dome / invagination", "dome", 0.14, 150,
         "The coat curves; epsin recruitment tracks\ncurvature. Actin begins to assemble at\nthe neck.",
         "curvo \u2014 recovers the H(t) trajectory:\nforce IDENTIFIED only if curvature is\ndynamic AND the actin channel is present"),
        ("iii) \u03a9 / scission", "omega", 0.24, 240,
         "Deep \u03a9 coat; actin applies inward axial\nforce at the neck and dynamin constricts.\nThe vesicle buds off.",
         "curvo \u2014 high curvature + active force,\nrecovered with a calibrated CI; else the\nfirewall returns a lower bound, not a point"),
    ]
    ybase = 0.50
    cx = 0.5
    h = 0.12                       # half-thickness used by bilayer_bulge
    for ax, (title, shape, bulge, span, narr, curvo) in zip(axes, stages):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title, fontsize=10, pad=4)
        top = bilayer_bulge(ax, 0.06, 0.94, ybase, bulge, cx, 0.55, h=h)
        ytop = top(cx) + 0.12
        draw_clathrin_lattice(ax, cx, ytop + 0.02, 0.20 if shape != "flat" else 0.16, span, n_tri=6)
        dxs = (-0.15, 0.0, 0.15) if shape == "flat" else (-0.12, 0.0, 0.12)
        for dx in dxs:
            epsin_at(ax, cx + dx, top(cx + dx) + 0.12)
        if shape == "omega":
            # actin is CYTOPLASMIC: draw bundles ABOVE the upper leaflet at each
            # neck, with force arrows pushing inward toward the neck (constriction).
            lift = 0.075                       # clear gap above the upper leaflet head
            for sgn in (-1, 1):
                nx = cx + sgn * 0.24
                ny = top(nx) + h               # upper-leaflet head surface at the neck
                for k in range(3):
                    ax.plot([nx + sgn * 0.10, nx + sgn * 0.01],
                            [ny + lift + 0.05 + k * 0.045, ny + lift + 0.01 + k * 0.045],
                            color=COL["actin"], lw=1.8, zorder=8)
                # force arrow: inward and down toward the neck, staying above the leaflet
                ax.add_patch(mpl.patches.FancyArrowPatch(
                    (nx + sgn * 0.12, ny + lift + 0.04), (nx + sgn * 0.02, ny + lift - 0.01),
                    arrowstyle="-|>", mutation_scale=11, lw=1.8, color=COL["actin"], zorder=9))
            ax.text(cx, top(cx) + 0.40, "actin (active force) \u2014 cytoplasmic, neck constriction",
                    ha="center", va="bottom", fontsize=6.3, color=COL["actin"])
            # side cues pin which face of the bilayer is which
            ax.text(0.03, ybase + 0.18, "cytoplasm", rotation=90, va="center", ha="center",
                    fontsize=6.0, color="#777", style="italic")
            ax.text(0.03, ybase - 0.16, "extracellular", rotation=90, va="center", ha="center",
                    fontsize=6.0, color="#777", style="italic")
        ax.text(0.5, 0.26, narr, ha="center", va="top", fontsize=6.9, color="#333")
        ax.add_patch(mpl.patches.FancyBboxPatch((0.05, 0.02), 0.90, 0.115, boxstyle="round,pad=0.008",
            fc="#eef2f7", ec="#8aa1c1", lw=1.0, zorder=1))
        ax.text(0.5, 0.077, curvo, ha="center", va="center", fontsize=6.5, color="#26456e", zorder=2)

    handles = [mpl.patches.Patch(fc=COL[k], label=lbl) for k, lbl in
               [("clathrin", "clathrin coat"), ("enth", "epsin ENTH (curvature)"),
                ("h0", "epsin H\u2080 (tension sensor)"), ("arm", "adaptor arm"),
                ("idp", "IDP tail"), ("actin", "actin (force)")]]
    fig.legend(handles=handles, loc="upper center", ncol=6, frameon=False, fontsize=7.2,
               bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("curvo orchestration model of clathrin-mediated endocytosis \u2014 actor roles and what curvo recovers, by maturation stage",
                 y=0.94, fontsize=10.5)
    fig.text(0.5, 0.004,
             "Drawn in the idiom of Joseph et al. (Commun Biol 2020, Fig. 3g): explicit bilayer, domain-coloured epsin. The three panels are the maturation stages curvo reasons over. Clathrin scaffolds; epsin's ENTH senses/generates\n"
             "curvature and its H\u2080 amphipathic wedge senses membrane tension; actin supplies inward axial force at the neck on the cytoplasmic face. The blue box gives curvo's identifiability verdict per stage \u2014 force is claimed only when a\n"
             "dynamic curvature trajectory AND a degeneracy-breaking channel (actin, or independent tension) are present; otherwise the firewall returns a bound, never a point estimate.",
             ha="center", fontsize=6.5, color="#555")
    fig.tight_layout(rect=[0, 0.05, 1, 0.895])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return fig


if __name__ == "__main__":
    render()
    print("wrote outputs/orchestration_schematic.png")
