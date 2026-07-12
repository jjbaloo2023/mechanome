"""
render_picalm_figure.py -- renders the PICALM orchestration test-case figure
(schematic bilayer + productive-pit ladder). Actin is drawn on the CYTOPLASMIC
side (same side as the clathrin coat), as neck-constriction filament bundles --
corrected from an earlier version that drew the force arrows below the lower
leaflet (which incorrectly implied actin on the extracellular/lumenal side).

Run from the curvo repo root:  python -m validation.realdata.render_picalm_figure
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import sys

sys.path.insert(0, '.')

# Load dependency modules
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load required modules
ev_mod = load_module('curvo.evaluator_tier0', '/root/.claude-science/orgs/357bd881-ec67-433c-a3e7-97bfdf0def1a/artifacts/proj_e2e339e89284/1096093c-5664-4a95-8d91-51a128ce2c0d/va75bbcc7_evaluator_tier0.py')
players_mod = load_module('curvo.players', '/root/.claude-science/orgs/357bd881-ec67-433c-a3e7-97bfdf0def1a/artifacts/proj_e2e339e89284/cbe69255-4709-41e2-877d-7ead184edbab/vba943c9c_players.py')
os_ = load_module('orchestration_schematic', '/root/.claude-science/orgs/357bd881-ec67-433c-a3e7-97bfdf0def1a/artifacts/proj_e2e339e89284/4ded847e-7a18-4ccf-b913-2ac74c38e741/v34dc5d86_orchestration_schematic.py')

# Constants
KAPPA_KBT = 20.0
SIGMA_KBT_NM2 = 0.02
A_COAT_NM2 = np.pi * 60.0 ** 2
OMEGA_OP = 0.66
PICALM_H_MED = 0.0194
PICALM_P_CROSS_OMEGA = 0.005

def crowding_ceff():
    return players_mod.PLAYERS["crowding"].contribution(
        {"c_max_inv_nm": 0.04, "coverage": 0.5, "phi_half": 0.3},
        SIGMA_KBT_NM2)["c0_contribution_inv_nm"]

def evaluate_assembly(c_eff, coat_rf=1.0, active_pN=0.0, extra_c=0.0):
    out = ev_mod.ccs_curvature(c_eff + extra_c, SIGMA_KBT_NM2, KAPPA_KBT, A_COAT_NM2,
                        coat_rigidity_factor=coat_rf, active_force_pN=active_pN)
    out["productive"] = out["dome_omega_OP"] >= OMEGA_OP
    return out

def run_ladder():
    crowd = crowding_ceff()
    ladder = [
        ("PICALM alone",               dict(c_eff=PICALM_H_MED)),
        ("+ clathrin coat",            dict(c_eff=PICALM_H_MED, coat_rf=3.0)),
        ("+ actin 40 pN",              dict(c_eff=PICALM_H_MED, coat_rf=3.0, active_pN=40.0)),
        ("+ crowding (actin held 40)", dict(c_eff=PICALM_H_MED, coat_rf=3.0, active_pN=40.0, extra_c=crowd)),
        ("+ actin raised to 80 pN",    dict(c_eff=PICALM_H_MED, coat_rf=3.0, active_pN=80.0, extra_c=crowd)),
    ]
    return [(lbl, evaluate_assembly(**cfg)) for lbl, cfg in ladder]

crowd = crowding_ceff()
ladder_results = run_ladder()

labels_short = ["PICALM\nalone", "+ clathrin\ncoat", "+ actin\n40 pN", "+ crowding\n(actin 40)", "+ actin\nraised 80"]
rows = []
for (lbl, o), s in zip(ladder_results, labels_short):
    rows.append(dict(lbl=s, H=o["achieved_mean_curvature_inv_nm"],
                     OP=o["dome_omega_OP"], stage=o["stage"], prod=o["productive"]))

def bilayer_bulge(ax, x0, x1, y, bulge, cx, width, n=30, r=0.04, h=0.11):
    xs = np.linspace(x0, x1, n)
    for x in xs:
        d = bulge * np.exp(-((x - cx) / (width * 0.5)) ** 2)
        yc = y + d
        ax.add_patch(mpl.patches.Circle((x, yc + h), r, fc=os_.COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc + h - r, yc + r * 0.5], color=os_.COL["tail"], lw=0.7, zorder=1)
        ax.add_patch(mpl.patches.Circle((x, yc - h), r, fc=os_.COL["head"], ec="#9c7f55", lw=0.4, zorder=2))
        ax.plot([x, x], [yc - h + r, yc - r * 0.5], color=os_.COL["tail"], lw=0.7, zorder=1)
    return lambda x: y + bulge * np.exp(-((x - cx) / (width * 0.5)) ** 2)

fig = plt.figure(figsize=(13.8, 5.6))
gs = fig.add_gridspec(1, 2, width_ratios=[0.92, 1.12], wspace=0.22)
# LEFT: bilayer schematic
axL = fig.add_subplot(gs[0])
axL.set_xlim(0, 1); axL.set_ylim(0, 1); axL.axis("off")
axL.set_title("Productive assembly: PICALM + coat + actin + crowding → Ω", fontsize=9.3)
ybase = 0.52; cx = 0.5
top = bilayer_bulge(axL, 0.06, 0.94, ybase, 0.22, cx, 0.5)
os_.draw_clathrin_lattice(axL, cx, top(cx) + 0.14, 0.22, 220, n_tri=7)
for dx in (-0.12, 0.0, 0.12):
    x = cx + dx; ym = top(x) + 0.12
    axL.add_patch(mpl.patches.Polygon([[x - 0.022, ym + 0.02], [x + 0.022, ym + 0.02], [x, ym - 0.05]],
        closed=True, fc=os_.COL["h0"], ec="#4d2166", lw=0.7, zorder=7))
    axL.plot([x - 0.05, x - 0.03], [ym + 0.04, ym + 0.14], color=os_.COL["idp"], lw=1.4, zorder=5)
# actin is CYTOPLASMIC -> same side as the clathrin coat (above the membrane).
# Draw a filament bundle at each neck of the invagination, pushing inward.
for sgn in (-1, 1):
    nx = cx + sgn * 0.26           # neck shoulder, where the bulge meets flat membrane
    ny = top(nx)                    # membrane surface height at the neck
    for k in range(3):
        # filaments run along the cytoplasmic face just above the neck
        axL.plot([nx + sgn * 0.10, nx],
                 [ny + 0.05 + k * 0.045, ny + 0.02 + k * 0.045],
                 color=os_.COL["actin"], lw=1.8, zorder=8)
    # force arrow: pushes inward toward the neck (constriction), on the coat side
    axL.add_patch(mpl.patches.FancyArrowPatch((nx + sgn * 0.11, ny + 0.05),
        (nx + sgn * 0.02, ny + 0.03),
        arrowstyle="-|>", mutation_scale=11, lw=1.8, color=os_.COL["actin"], zorder=9))
axL.text(cx, ybase - 0.02, "actin (active force,\ncytoplasmic — neck constriction)",
         ha="center", va="top", fontsize=6.0, color=os_.COL["actin"])
hd = [mpl.patches.Patch(fc=os_.COL[k], label=l) for k, l in
    [("clathrin", "clathrin coat"), ("h0", "PICALM ANTH wedge"), ("idp", "crowding (epsin IDP)"), ("actin", "actin (force)")]]
axL.legend(handles=hd, loc="lower center", ncol=2, frameon=False, fontsize=6.6, bbox_to_anchor=(0.5, -0.02))
# RIGHT: single-variable ladder
axR = fig.add_subplot(gs[1])
H = [r["H"] for r in rows]; xs = np.arange(len(rows))
cols = ["#c0392b" if not r["prod"] else "#2f6b45" for r in rows]
axR.bar(xs, H, color=cols, width=0.64, zorder=3)
axR.axhline(0.030, color="#33445a", ls="--", lw=1.4, zorder=2)
axR.text(0.02, 0.0304, "Ω / scission threshold (0.030 nm⁻¹)", fontsize=6.6, color="#33445a", va="bottom", ha="left")
for x, r in zip(xs, rows):
    col = "#2f6b45" if r["prod"] else "#c0392b"
    if r["H"] > 0.026:
        axR.annotate(f"{r['H']:.3f}\n{r['stage']}", (x, r["H"] - 0.001), textcoords="offset points", xytext=(0, -2),
                     ha="center", va="top", fontsize=6.8, color="white", fontweight="bold")
    else:
        axR.annotate(f"{r['H']:.3f}\n{r['stage']}", (x, r["H"]), textcoords="offset points", xytext=(0, 3),
                     ha="center", fontsize=6.8, color=col)
axR.set_xticks(xs); axR.set_xticklabels([r["lbl"] for r in rows], fontsize=6.9)
axR.set_ylabel("achieved mean curvature H (nm⁻¹)"); axR.set_ylim(0, 0.038)
axR.set_title("Can PICALM support a productive pit? Not alone — and\nneither crowding nor higher force alone suffices", fontsize=9.3)
axR.text(0.03, 0.97, "PICALM autonomous\nP(cross Ω) = 0.005\n(family-screen MC)", transform=axR.transAxes, fontsize=6.8,
         color="#c0392b", va="top", bbox=dict(boxstyle="round,pad=0.3", fc="#fbeaea", ec="#c0392b", lw=0.8))
fig.suptitle("Test case: PICALM (ANTH) recruited to the membrane — orchestration and productive-pit verdict", y=0.995, fontsize=10.3)
fig.text(0.5, 0.005,
  "PICALM is an ANTH adaptor: its amphipathic wedge gives dome-level autonomous curvature (family-screen H_med 0.019 nm⁻¹) but crosses the Ω/scission threshold with probability 0.005 — it CANNOT make a productive pit alone. Each rung changes ONE factor:\n"
  "the coat and actin (40 pN) each raise curvature but stay sub-threshold; adding the crowding partner (epsin IDP brush) at fixed 40 pN reaches only the dome stage (0.025); the pit crosses to Ω (0.031) only when the crowding partner AND a higher\n"
  "actin force (80 pN) are BOTH present. Neither the crowding partner nor the force increase alone is sufficient. This is a stage/threshold call from the validated forward model with derived c_eff magnitudes — not an inverse on a measured trajectory.",
  ha="center", fontsize=6.3, color="#555")
fig.tight_layout(rect=[0, 0.055, 1, 0.94])
fig.savefig("picalm_orchestration.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved picalm_orchestration.png, size:", os.path.getsize("picalm_orchestration.png"), "bytes")