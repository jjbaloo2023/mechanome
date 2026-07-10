"""plot_envelope.py — render the perception operating-envelope figure from
envelope_grid.json. Two panels: (left) dome-band H relative error vs each swept
axis with the calibration point marked; (right) the psf x photon rel-error plane.
"""
from __future__ import annotations
import json
import numpy as np
import matplotlib.pyplot as plt


def render(grid_path="outputs/envelope_grid.json", out="outputs/envelope_recovery.png"):
    try:
        apply_figure_style(sizes=(9, 8, 7))
    except NameError:
        pass
    res = json.load(open(grid_path))
    conds = res["conditions"]
    axes_of = {}
    for c in conds:
        axes_of.setdefault(c["axis"], []).append(c)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.4))

    # --- left: dome-band rel error vs swept value, one line per axis ----------
    axis_x = {"psf": ("psf_sigma_nm", "PSF \u03c3 (nm)"),
              "nm_per_px": ("nm_per_px", "pixel size (nm/px)"),
              "photons": ("peak_photons", "peak photons"),
              "depth": ("c_eff_max", "c_eff,max (cap depth)"),
              "off_center": ("off_center_px", "off-center (px)")}
    colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(axis_x)))
    for (ax_name, (key, lbl)), col in zip(axis_x.items(), colors):
        rows = sorted(axes_of.get(ax_name, []), key=lambda r: r[key])
        if not rows:
            continue
        xs = [r[key] for r in rows]
        ys = [100 * r["dome_rel_err"] if r["dome_rel_err"] is not None else np.nan for r in rows]
        # normalize x to [0,1] so axes with different units share the plot
        xs = np.array(xs, float); xn = (xs - xs.min()) / (np.ptp(xs) or 1)
        axL.plot(xn, ys, "o-", color=col, lw=1.8, ms=5, label=lbl)
    axL.axhline(10, ls="--", color="#888", lw=1)
    axL.text(0.02, 10.6, "10% target", fontsize=8, color="#666")
    axL.set_xlabel("swept value (min\u2192max, normalized per axis)")
    axL.set_ylabel("operating-band H relative error (%)")
    axL.set_title("Perception holds across the operating envelope\n(band = cap depth 1.3\u20132.2 \u00d7 PSF \u03c3)", fontsize=10)
    axL.legend(fontsize=7, frameon=False, ncol=2)
    axL.set_ylim(0, max(30, axL.get_ylim()[1]))

    # --- right: psf x photon rel-error heatmap -------------------------------
    plane = res["plane_psf_photons"]
    M = np.array([[np.nan if v is None else 100 * v for v in row] for row in plane["rel_err"]])
    im = axR.imshow(M, origin="lower", aspect="auto", cmap="magma_r", vmin=0, vmax=40)
    axR.set_xticks(range(len(plane["photons"]))); axR.set_xticklabels(plane["photons"])
    axR.set_yticks(range(len(plane["psf"]))); axR.set_yticklabels(plane["psf"])
    axR.set_xlabel("peak photons"); axR.set_ylabel("PSF \u03c3 (nm)")
    axR.set_title("Resolution \u00d7 SNR interaction\n(dome-band H rel. error)", fontsize=10)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.isfinite(M[i, j]):
                axR.text(j, i, f"{M[i,j]:.0f}", ha="center", va="center",
                         color="white" if M[i, j] > 20 else "black", fontsize=8)
            else:
                axR.text(j, i, "\u2014", ha="center", va="center", color="#999", fontsize=9)
    cb = fig.colorbar(im, ax=axR, fraction=0.046, pad=0.04)
    cb.set_label("H rel. error (%)", fontsize=8)
    fig.suptitle("curvo perception — held-out image operating envelope (exact ground truth)",
                 fontsize=11, y=1.04)
    fig.text(0.5, -0.03,
             "Point-estimate accuracy shown. Per-frame CI under-covers in this band "
             "(coverage68\u2248" + "0.30 vs 0.68 nominal) \u2014 uncertainty needs widening; "
             "\u2018\u2014\u2019 = band empty (few frames clear the resolvability floor at large PSF).",
             ha="center", fontsize=7.5, color="#555")
    fig.tight_layout()
    fig.savefig(out, dpi=175, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print("saved", render())
