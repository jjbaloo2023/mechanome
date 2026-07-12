"""
render_screen_to_mechanome.py -- the structural-screen -> channel-gating wiring
figure. Left: the frozen signed curvature-capacity ranking (scaffolds positive /
exocytic, mechanosensitive channels negative / tension leg, channels outlined as
the ones that feed the gating model). Right: the cross-scale seam carrying a
channel's structure-derived c0 into ms_gating_v1, with the MscL worked example.

Run from the repo root:
    python -m mechanome.structural_screen.render_screen_to_mechanome
"""
import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from mechanome import structural_screen as ss, channel_link as cl

EXO = "#c0562f"; MS = "#2f6f8f"
_HERE = os.path.dirname(os.path.abspath(__file__))


def render(out_path=None):
    out_path = out_path or os.path.join(_HERE, "figures", "screen_to_mechanome.png")
    rk = ss.frozen_ranking()
    full = pd.read_csv(os.path.join(ss._RESULTS, "stage3_ranking.csv"))
    rk["leg"] = rk["protein"].map(dict(zip(full["protein"], full["leg"])))
    chans = {c["protein"] for c in cl.channels_from_screen()}

    fig = plt.figure(figsize=(13.5, 6.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.28)
    axL = fig.add_subplot(gs[0]); axR = fig.add_subplot(gs[1])

    order = rk.sort_values("E_curv_signed")
    y = np.arange(len(order))
    colors = [EXO if l == "exocytic" else MS for l in order["leg"]]
    axL.barh(y, order["E_curv_signed"], color=colors, edgecolor="white", lw=0.6, zorder=3)
    for yi, (_, row) in zip(y, order.iterrows()):
        if row["protein"] in chans:
            axL.barh(yi, row["E_curv_signed"], facecolor="none",
                     edgecolor="#123", lw=1.6, zorder=4)
    axL.axvline(0, color="#333", lw=1.0, zorder=2)
    axL.set_yticks(y); axL.set_yticklabels(order["protein"], fontsize=8)
    axL.set_xlabel("signed curvature capacity  $E_{curv}$  (k$_B$T)", fontsize=9)
    axL.text(0.5, -0.115, "\u2190 inward / endocytic          outward / exocytic \u2192",
             transform=axL.transAxes, ha="center", fontsize=8, color="#555")
    axL.set_title("Structural screen: signed curvature-generating capacity",
                  fontsize=9.5, loc="left")
    for yi, (_, row) in zip(y, order.iterrows()):
        v = row["E_curv_signed"]
        if abs(v) >= 2.0:
            axL.text(v + (1.6 if v >= 0 else -1.6), yi, f"{v:.0f}", va="center",
                     ha="left" if v >= 0 else "right", fontsize=7.2, color="#222")
    axL.legend(handles=[Patch(fc=EXO, label="exocytic / scaffold"),
                        Patch(fc=MS, label="mechanosensitive (tension leg)"),
                        Patch(fc="none", ec="#123", lw=1.6, label="feeds channel gating model")],
               loc="lower right", fontsize=7.3, frameon=False)
    axL.margins(y=0.02)

    axR.axis("off"); axR.set_xlim(0, 1); axR.set_ylim(0, 1)

    def box(x, y0, w, h, txt, fc, ec, fs=8.4, tc="#111"):
        axR.add_patch(mpl.patches.FancyBboxPatch((x, y0), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.02", fc=fc, ec=ec, lw=1.4, zorder=3))
        axR.text(x + w / 2, y0 + h / 2, txt, ha="center", va="center", fontsize=fs, color=tc, zorder=4)

    box(0.06, 0.62, 0.40, 0.24,
        "structural_screen_v1\n(molecule scale)\nstructure \u2192 signed $c_0$", "#f2e2d8", EXO)
    box(0.54, 0.62, 0.40, 0.24,
        "ms_gating_v1\n(membrane scale)\n$P_o(\\sigma)$ two-state gating", "#dce8ef", MS)
    axR.add_patch(mpl.patches.FancyArrowPatch((0.46, 0.74), (0.54, 0.74),
        arrowstyle="-|>", mutation_scale=16, lw=2.0, color="#123", zorder=5))
    axR.text(0.50, 0.785, "structure-\nderived $c_0$", ha="center", va="bottom",
             fontsize=7.0, color="#123")
    ex = cl.link_channel_to_gating("MscL", 11.8)
    box(0.20, 0.20, 0.60, 0.24,
        f"MscL:  $c_0$ = {ex['structural_c0_inv_nm']:+.3f} nm$^{{-1}}$  (screen)\n"
        f"\u2192 $P_o$ = {ex['open_probability']:.2f}  at \u03c3 = 11.8 mN/m  (gating)",
        "#eef2ee", "#567", fs=8.2)
    axR.add_patch(mpl.patches.FancyArrowPatch((0.5, 0.60), (0.5, 0.445),
        arrowstyle="-|>", mutation_scale=14, lw=1.6, color="#567", zorder=5))
    axR.text(0.5, 0.925, "The cross-scale link: one channel, both ends grounded",
             ha="center", va="center", fontsize=9.3, color="#111", weight="bold")

    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    return out_path


if __name__ == "__main__":
    print("wrote", render())
