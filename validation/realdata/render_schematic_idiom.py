"""
render_schematic_idiom.py -- compose the epsin/CME decision-tree figure in the
2020 Comm Bio Fig 7 idiom.

Primary player (epsin ENTH) is a real secondary-structure cartoon sprite; the
disordered region is an IDP crowding brush (density ~ epsin count); supporting
cast (clathrin, AP2) are simple drawn cartoons.

Run from the repo root:  python -m validation.realdata.render_schematic_idiom
Sprites build on demand from cache/structures/ (fetched from RCSB / AlphaFold DB).
"""
import os
import matplotlib.pyplot as plt
import matplotlib.text, matplotlib.image
from matplotlib.patches import Rectangle
from validation.realdata import schematic_idiom as si

OUT = os.path.join(os.path.dirname(__file__), "schematic_idiom_epsin.png")


def _overlap_report(fig):
    """Text-vs-(text+image) overlap check -- catches labels colliding with graphics,
    which a text-only bbox check misses."""
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(matplotlib.text.Text)
             if t.get_text().strip() and t.get_visible()]
    imgs = [im.get_window_extent(r) for im in fig.findobj(matplotlib.image.AxesImage)]
    tt = [(a.get_text()[:14], b.get_text()[:14]) for i, (a, ba) in enumerate(texts)
          for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    ti = [a.get_text()[:16] for a, ba in texts for eb in imgs if ba.overlaps(eb)]
    return tt, ti


def compose(path=OUT, dpi=200):
    fig = plt.figure(figsize=(10.5, 12.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1.18)
    ax.axis("off"); ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0.635), 1, 0.545, fc=si.PAL["panel_pink"], ec="none", zorder=0))
    ax.add_patch(Rectangle((0, 0.0), 1, 0.635, fc=si.PAL["panel_green"], ec="none", zorder=0))
    def title(cx, cy, s, fs=8.0, va="bottom"):
        ax.text(cx, cy, s, ha="center", va=va, fontsize=fs, zorder=8, linespacing=0.95)
    def lab(cx, cy, s, fs=8.2):
        ax.text(cx, cy, s, ha="center", va="center", fontsize=fs, fontweight="bold", zorder=8, linespacing=0.95)
    N, A = si.node, si.branch_arrow
    # TOP: without epsin
    ax.text(0.03, 1.13, "Coat assembly without epsin", fontsize=14.5, fontweight="bold", zorder=8)
    N(ax, 0.12, 0.88, 0.13, 0.0, 0); title(0.12, 0.935, "flat clathrin\nlattice")
    A(ax, 0.20, 0.88, 0.29, 0.88, lw=7)
    N(ax, 0.40, 0.88, 0.12, 0.18, 0); title(0.40, 0.935, "clathrin coat\nassembly")
    lab(0.585, 1.00, "Low tension\nfavors"); lab(0.585, 0.77, "High tension\nfavors")
    A(ax, 0.49, 0.905, 0.67, 0.98, lw=7); A(ax, 0.49, 0.86, 0.67, 0.77, lw=7)
    N(ax, 0.82, 0.98, 0.12, 0.45, 0, neck=True); title(0.82, 1.035, "productive\ncoated-pit")
    N(ax, 0.82, 0.755, 0.11, 0.14, 0); title(0.82, 0.815, "aborted coat\nassembly")
    # BOTTOM: with epsin
    ax.text(0.03, 0.60, "Coat assembly with epsin recruitment", fontsize=14.5, fontweight="bold", zorder=8)
    ax.add_patch(Rectangle((0.31, 0.55), 0.18, 0.026, fc=si.PAL["header_enth"], ec="none", zorder=8))
    ax.add_patch(Rectangle((0.49, 0.55), 0.18, 0.026, fc=si.PAL["header_idp"], ec="none", zorder=8))
    ax.text(0.40, 0.563, "mediated by ENTH domain", color="white", fontsize=7.4, ha="center", va="center", fontweight="bold", zorder=9)
    ax.text(0.58, 0.563, "mediated by IDP domain", color="white", fontsize=7.4, ha="center", va="center", fontweight="bold", zorder=9)
    N(ax, 0.12, 0.40, 0.13, 0.0, 2); title(0.12, 0.455, "flat lattice\n+ epsin")
    lab(0.265, 0.495, "Low tension favors\nless epsin nucleation", 7.4)
    lab(0.265, 0.295, "High tension favors\nmore epsin nucleation", 7.4)
    A(ax, 0.20, 0.41, 0.34, 0.47, lw=6); A(ax, 0.20, 0.39, 0.34, 0.30, lw=6)
    N(ax, 0.44, 0.47, 0.11, 0.20, 3); title(0.44, 0.395, "clathrin coat\nassembly", va="top")
    N(ax, 0.44, 0.28, 0.11, 0.22, 5); title(0.44, 0.205, "clathrin coat\nassembly", va="top")
    A(ax, 0.545, 0.495, 0.75, 0.55, lw=6); A(ax, 0.545, 0.29, 0.75, 0.20, lw=6)
    A(ax, 0.55, 0.46, 0.75, 0.385, lw=5); A(ax, 0.55, 0.29, 0.75, 0.375, lw=5)
    lab(0.70, 0.575, "More\nfavored", 7.8); lab(0.70, 0.315, "Less\nfavored", 7.8); lab(0.63, 0.14, "More\nfavored", 7.8)
    N(ax, 0.88, 0.55, 0.115, 0.45, 5, neck=True); title(0.88, 0.605, "productive\ncoated-pit")
    N(ax, 0.88, 0.375, 0.10, 0.12, 3); title(0.88, 0.315, "aborted coat\nassembly", va="top")
    N(ax, 0.88, 0.17, 0.115, 0.45, 5, neck=True); title(0.88, 0.225, "productive\ncoated-pit")
    si.legend_box(ax, 0.03, 0.03, 0.36, 0.085)
    tt, ti = _overlap_report(fig)
    if tt or ti:
        import warnings; warnings.warn(f"overlaps: text-text={tt} text-image={ti}")
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    if not os.path.exists(os.path.join(si.SPRITE_DIR, "enth_cartoon.png")):
        si.build_sprites()
    print("wrote", compose())
