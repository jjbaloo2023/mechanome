"""
Orchestration schematic for CME, drawn in the visual idiom of the 2020 epsin
paper's proposed-model figure (Joseph et al., Commun Biol 2020, Fig. 3g): an
explicit phospholipid bilayer with cartooned proteins whose domains are colour-
coded. Here the three panels are not genetic variants but the three MATURATION
STAGES curvo reasons about (flat -> dome -> Omega/scission), showing which actor
does what and what curvo can/cannot recover at each stage.

Colour key. Four colours follow the 2020 figure's own scheme (green clathrin
coil, orange adaptor arm, blue ENTH sheet, purple/magenta H0 wedge); the IDP
tail and actin colours below are our additions (in the 2020 Fig. 3g the
disordered linker is drawn as a plain grey/white squiggle, and actin is not
shown at all):
  clathrin coat      green   (triskelion lattice, the scaffold)  [2020]
  epsin ENTH sheet   blue    (structured N-terminus)             [2020]
  epsin H0 wedge     purple  (amphipathic helix inserted)        [2020]
  epsin adaptor arm  orange  (C-terminal binding arms)           [2020]
  epsin IDP tail     red     (disordered linker; our colour)
  actin              crimson (active force at the neck; our addition)
  bilayer heads      tan
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyArrowPatch, Circle, PathPatch
from matplotlib.path import Path

COL = dict(clathrin="#2f8f4e", enth="#2f4fb0", h0="#7d3fa0", arm="#e08a30",
           idp="#c0392b", actin="#a01c3a", head="#d9b88f", tail="#b8a37a")


def draw_bilayer(ax, x0, x1, y, dip=None, n=26, r=0.045, h=0.14):
    """Explicit phospholipid bilayer between x0..x1 at baseline y. If `dip` is a
    callable x->depth it invaginates the membrane (for dome/Omega stages)."""
    xs = np.linspace(x0, x1, n)
    for x in xs:
        d = dip(x) if dip else 0.0
        yc = y - d
        # upper leaflet head + tail, lower leaflet mirrored
        ax.add_patch(Circle((x, yc + h), r, fc=COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc + h - r, yc + r*0.5], color=COL["tail"], lw=0.8, zorder=1)
        ax.add_patch(Circle((x, yc - h), r, fc=COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc - h + r, yc - r*0.5], color=COL["tail"], lw=0.8, zorder=1)


def _cap_dip(cx, width, depth):
    """A smooth membrane invagination centred at cx."""
    def f(x):
        return depth * np.exp(-((x - cx) / (width * 0.5)) ** 2)
    return f


def draw_clathrin_lattice(ax, cx, cy, r, span_deg, n_tri=5, color=None):
    """A curved clathrin lattice (arc of triskelion vertices) sitting above the
    coat. span_deg controls how far it wraps (flat=small, Omega=wide)."""
    color = color or COL["clathrin"]
    a0 = 90 - span_deg/2; a1 = 90 + span_deg/2
    angs = np.deg2rad(np.linspace(a0, a1, n_tri))
    pts = np.array([(cx + r*np.cos(a), cy + r*np.sin(a) - r) for a in angs])
    for i in range(len(pts)-1):
        ax.plot(pts[[i, i+1], 0], pts[[i, i+1], 1], color=color, lw=2.4, zorder=5,
                solid_capstyle="round")
    for (px, py) in pts:  # triskelion vertices
        ax.add_patch(Circle((px, py), 0.03, fc=color, ec="white", lw=0.5, zorder=6))
    return pts


def draw_epsin(ax, x, ytop, ymemb, inserted=True, enth=True):
    """Cartoon epsin at membrane position x: green clathrin coil (top), orange
    arms, blue ENTH sheet, purple H0 wedge inserted into the bilayer, red IDP."""
    # green clathrin-binding coil at top
    tt = np.linspace(0, 1, 40)
    ax.plot(x + 0.03*np.sin(tt*7*np.pi), ytop - 0.02 - tt*0.16, color=COL["clathrin"], lw=2.2, zorder=6)
    # orange adaptor arm curving down to membrane
    ax.add_patch(FancyArrowPatch((x, ytop-0.18), (x+0.10, ymemb+0.05),
        connectionstyle="arc3,rad=0.5", arrowstyle="-", lw=2.2, color=COL["arm"], zorder=6))
    # red IDP tail
    ax.plot(x + 0.02*np.sin(tt*5*np.pi) + 0.06, ytop-0.2 - tt*0.18, color=COL["idp"], lw=1.5, zorder=5)
    if enth:
        # blue ENTH beta-sheet block just above membrane
        ax.add_patch(mpl.patches.FancyBboxPatch((x-0.05, ymemb+0.02), 0.10, 0.10,
            boxstyle="round,pad=0.005", fc=COL["enth"], ec="#1c2f6b", lw=0.8, zorder=6))
    if inserted:
        # purple H0 wedge inserted into upper leaflet
        ax.add_patch(mpl.patches.Polygon([[x-0.03, ymemb+0.04],[x+0.03, ymemb+0.04],
            [x, ymemb-0.06]], closed=True, fc=COL["h0"], ec="#4d2166", lw=0.8, zorder=7))
