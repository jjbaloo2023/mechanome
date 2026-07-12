"""
schematic_idiom.py -- the "2020 Comm Bio Fig 7" schematic idiom for curvo.

Foreground / background rendering, matching the reference figure's emphasis:

  * PRIMARY player (the protein under investigation, e.g. epsin) is drawn as a
    real secondary-structure CARTOON sprite rendered from its structure: helices
    as thick depth-shaded ribbons, sheets as arrows, coil as thin tube. ENTH is
    RCSB 1H0A (X-ray); ANTH is AlphaFold PICALM (Q13492) res 1-289. Secondary
    structure is assigned from the CA trace by biotite's P-SEA algorithm.

  * The intrinsically disordered region (IDP) is NOT a per-molecule tail. It is
    rendered as a CROWDING BRUSH -- a translucent entropic-pressure cloud plus a
    dense set of packed disordered chains on the cytoplasmic face -- because
    epsin's disordered region generates curvature by molecular crowding, not by a
    single wedge. Brush density scales with the number of epsins in the state.

  * SUPPORTING cast (proteins not under investigation: clathrin, AP2, ...) are
    simple drawn cartoons, not detailed structures: the hatched clathrin "comb"
    on the outer membrane face and a small AP2 tri-lobe glyph. This keeps the
    figure's attention on the player being studied.

  * The phospholipid bilayer is drawn (two leaflets of head beads + tails). Pit
    depth scales with node width (depth ~ curvature * width).

Cartoon sprites are cached under cache/structures/sprites/ (gitignored,
re-buildable via build_sprites(); source PDBs re-fetchable from RCSB / AlphaFold
DB through fetch_structures()).
"""
from __future__ import annotations
import os, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle, Ellipse, Rectangle, FancyBboxPatch
from scipy.ndimage import gaussian_filter
from scipy.interpolate import splprep, splev
from matplotlib.colors import to_rgb

PAL = dict(
    panel_pink="#fcddde", panel_green="#d9f2e5",
    enth="#3f6fd0", anth="#2f9e8f", idp="#f26522", ap2="#9b4fa0",
    clathrin="#3a3a3a", lipid_head="#8f9296", lipid_tail="#b9bcc0", arrow="#111111",
    header_enth="#2e3192", header_idp="#f26522",
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(_HERE, "..", "..", "cache", "structures")
SPRITE_DIR = os.path.join(_CACHE, "sprites")

# ---- primary-player structures (secondary-structure cartoons) ----
CARTOON_SOURCES = {
    "enth_cartoon": dict(pdb="1H0A",     resrange=None,      color=PAL["enth"],
                         note="epsin-1 ENTH domain, X-ray 1H0A"),
    "anth_cartoon": dict(uniprot="Q13492", resrange=(1, 289), color=PAL["anth"],
                         note="PICALM ANTH domain (AlphaFold)"),
}
STRUCTURE_URLS = {
    "1H0A":   "https://files.rcsb.org/download/1H0A.pdb",
    "Q13492": "https://alphafold.ebi.ac.uk/files/AF-Q13492-F1-model_v6.pdb",
}


# ================= structure IO + secondary structure =================
def _read_ca(path, resrange=None, chain=None):
    import biotite.structure.io.pdb as _pdb
    import biotite.structure as _struc
    arr = _pdb.PDBFile.read(path).get_structure(model=1)
    arr = arr[_struc.filter_amino_acids(arr)]
    if chain is not None:
        arr = arr[arr.chain_id == chain]
    ca = arr[arr.atom_name == "CA"]
    if resrange:
        ca = ca[(ca.res_id >= resrange[0]) & (ca.res_id <= resrange[1])]
    return ca.coord


def _assign_sse(path, resrange=None, chain=None):
    import biotite.structure.io.pdb as _pdb
    import biotite.structure as _struc
    arr = _pdb.PDBFile.read(path).get_structure(model=1)
    arr = arr[_struc.filter_amino_acids(arr)]
    ch = arr.chain_id[0] if chain is None else chain
    sub = arr[arr.chain_id == ch]
    sse = _struc.annotate_sse(sub)
    resids = np.unique(sub.res_id)
    if resrange:
        m = (resids >= resrange[0]) & (resids <= resrange[1])
        return sse[m]
    return sse


def _pca_project(P):
    P = P - P.mean(0)
    _, _, Vt = np.linalg.svd(P, full_matrices=False)
    return P @ Vt.T


def _smooth(xy, n=400):
    if len(xy) < 4:
        return xy
    tck, _ = splprep([xy[:, 0], xy[:, 1]], s=0.0, k=min(3, len(xy) - 1))
    return np.column_stack(splev(np.linspace(0, 1, n), tck))


# ================= cartoon sprite renderer (primary player) =================
def render_cartoon(pdb_path, resrange=None, chain=None, color="#3f6fd0", px=360, out=None,
                   helix_lw=15, coil_lw=4, sheet_lw=11):
    """Secondary-structure cartoon sprite: helices thick ribbons, sheets arrows, coil thin."""
    ca = _read_ca(pdb_path, resrange, chain)
    sse = _assign_sse(pdb_path, resrange, chain)
    L = min(len(ca), len(sse))
    P = _pca_project(ca[:L]); sse = sse[:L]
    xy, z = P[:, :2], P[:, 2]
    fig, ax = plt.subplots(figsize=(3, 3)); ax.axis("off"); ax.set_aspect("equal")
    base = np.array(to_rgb(color)); zc = (z - z.min()) / (np.ptp(z) + 1e-9)
    runs = []; i = 0
    while i < L:
        j = i
        while j + 1 < L and sse[j + 1] == sse[i]:
            j += 1
        runs.append((sse[i], i, j)); i = j + 1
    order = {"c": 0, "b": 1, "a": 2}
    for typ, a, b in sorted(runs, key=lambda r: (order[r[0]], zc[r[1]:r[2] + 1].mean())):
        seg = xy[max(0, a - 1):b + 2]
        if len(seg) < 2:
            continue
        sm = _smooth(seg, n=max(24, (b - a + 1) * 10)) if len(seg) >= 4 else seg
        zseg = np.interp(np.linspace(0, 1, len(sm)), np.linspace(0, 1, len(seg)),
                         zc[max(0, a - 1):min(L, b + 2)]); zm = zseg.mean()
        col = base * (0.58 + 0.42 * zm)
        if typ == "a":
            ax.plot(sm[:, 0], sm[:, 1], color=base * 0.45, lw=helix_lw + 3, solid_capstyle="round", zorder=10 + zm, alpha=0.9)
            ax.plot(sm[:, 0], sm[:, 1], color=col, lw=helix_lw, solid_capstyle="round", zorder=10.1 + zm)
            ax.plot(sm[:, 0], sm[:, 1], color=np.clip(col * 1.3, 0, 1), lw=helix_lw * 0.35, solid_capstyle="round", zorder=10.2 + zm, alpha=0.7)
        elif typ == "b":
            ax.plot(sm[:, 0], sm[:, 1], color=col, lw=sheet_lw, solid_capstyle="butt", zorder=6 + zm)
        else:
            ax.plot(sm[:, 0], sm[:, 1], color=col * 0.9, lw=coil_lw, solid_capstyle="round", zorder=2 + zm)
    ax.margins(0.06)
    if out:
        fig.savefig(out, dpi=px / 3, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return out


_SPRITE = {}
def load_sprite(name):
    if name not in _SPRITE:
        p = os.path.join(SPRITE_DIR, f"{name}.png")
        if not os.path.exists(p):
            raise FileNotFoundError(f"sprite {name} not built; run build_sprites()")
        _SPRITE[name] = mpimg.imread(p)
    return _SPRITE[name]


def place_sprite(ax, name, x, y, w=0.06, z=6):
    img = load_sprite(name)
    h = w * img.shape[0] / img.shape[1]
    ax.imshow(img, extent=[x - w / 2, x + w / 2, y - h / 2, y + h / 2],
              zorder=z, interpolation="bilinear", aspect="auto")


# ================= membrane primitives (drawn) =================
def _profile(xs, w, curv, neck=False):
    u = xs / (w * 0.5)
    d = min(curv, 0.55) * w
    yc = -d * np.exp(-(np.abs(u) / 0.58) ** 2.6)
    dy = np.gradient(yc, xs); nx = -dy; ny = np.ones_like(xs); L = np.hypot(nx, ny)
    return yc, nx / L, ny / L


def _center_depth(w, curv):
    return -min(curv, 0.55) * w


def draw_bilayer(ax, cx, cy, w, curv=0.0, neck=False, n=30, z=2):
    xs = np.linspace(-w / 2, w / 2, n); yc, nx, ny = _profile(xs, w, curv, neck); t = 0.042 * w
    for sgn in (+1, -1):
        hx = cx + xs + sgn * nx * t; hy = cy + yc + sgn * ny * t
        ax.plot(hx, hy, color=PAL["lipid_tail"], lw=0.6, zorder=z)
        ax.scatter(hx, hy, s=8, c=PAL["lipid_head"], edgecolors="none", zorder=z + 0.1)


def draw_clathrin_comb(ax, cx, cy, w, curv, neck=False, n=26, z=5):
    """Supporting cast: simple hatched clathrin comb on the OUTER membrane face."""
    xs = np.linspace(-w / 2, w / 2, n); yc, nx, ny = _profile(xs, w, curv, neck); off = 0.10 * w
    bx = cx + xs + nx * off; by = cy + yc + ny * off
    ax.plot(bx, by, color=PAL["clathrin"], lw=1.6, zorder=z, solid_capstyle="round")
    for i in range(n):
        ax.plot([cx + xs[i] + nx[i] * off * 0.2, bx[i]],
                [cy + yc[i] + ny[i] * off * 0.2, by[i]],
                color=PAL["clathrin"], lw=0.9, zorder=z - 0.1)


def draw_ap2(ax, x, y, s=1.0, z=6):
    """Supporting cast: simple AP2 tri-lobe glyph (not a detailed structure)."""
    for dx, dy in [(-0.028, 0.0), (0.028, 0.0), (0.0, -0.032)]:
        ax.add_patch(Ellipse((x + dx * s, y + dy * s), 0.06 * s, 0.052 * s,
                             fc=PAL["ap2"], ec="#5e2b62", lw=0.6, zorder=z))


# ================= IDP crowding brush (drawn) =================
def draw_idp_crowd(ax, x0, x1, ybase, height, n_chains=9, color=None, seed=0, z=4,
                   alpha_cloud=0.13, direction=-1.0):
    """Molecular-crowding brush: translucent entropic-pressure cloud + packed disordered chains.

    direction=-1 draws the brush BELOW ybase (cytoplasmic face). Chain and cloud
    density represent the steric/entropic pressure of the disordered region -- the
    curvature-generating mechanism is crowding, not a single wedge tail.
    """
    color = color or PAL["idp"]
    rng = np.random.default_rng(seed)
    cx = (x0 + x1) / 2.0
    ax.add_patch(Ellipse((cx, ybase + direction * height * 0.4), (x1 - x0) * 1.05, height * 1.6,
                 fc=color, ec="none", alpha=alpha_cloud, zorder=z - 0.2))
    xs = np.linspace(x0, x1, n_chains)
    for i, cxi in enumerate(xs):
        npts = int(rng.integers(5, 8)); t = np.linspace(0, 1, npts)
        px = cxi + np.cumsum(rng.normal(0, (x1 - x0) / (n_chains * 2.2), npts)); px[0] = cxi
        py = ybase + direction * height * t + rng.normal(0, height * 0.12, npts)
        pts = np.column_stack([px, py])
        sm = _smooth(pts, n=40) if npts >= 4 else pts
        ax.plot(sm[:, 0], sm[:, 1], color=color, lw=1.3, alpha=0.85,
                solid_capstyle="round", zorder=z + i * 0.01)


# ================= composite node =================
def node(ax, cx, cy, w, curv, n_eps, neck=False, ap2=True, primary="enth_cartoon", idp=True):
    """Membrane-state cartoon: bilayer + clathrin comb + n_eps cartoon players
    + IDP crowding brush (density ~ n_eps) + AP2 glyph."""
    draw_bilayer(ax, cx, cy, w, curv, neck)
    draw_clathrin_comb(ax, cx, cy, w, curv, neck)
    ew = 0.34 * w
    if n_eps > 0:
        xs = np.linspace(-w * 0.30, w * 0.30, n_eps) if n_eps > 1 else np.array([0.0])
        yc = (_profile(xs, w, curv, neck)[0] if n_eps > 1
              else np.array([_center_depth(w, curv)]))
        for i, ex in enumerate(xs):
            place_sprite(ax, primary, cx + ex, cy + yc[i] - 0.11 * w, w=ew, z=6)
        if idp:
            # crowding brush spans the epsin footprint, on the cytoplasmic (lower) face
            yb = cy + float(np.min(yc)) - 0.11 * w - ew * 0.22
            draw_idp_crowd(ax, cx + xs[0] - ew * 0.4, cx + xs[-1] + ew * 0.4, yb,
                           height=0.07 * w + 0.012 * w * n_eps,
                           n_chains=max(6, 2 * n_eps + 3), seed=int(abs(cx * 1000) + n_eps), z=4)
    if ap2:
        draw_ap2(ax, cx, cy - 0.12 * w + _center_depth(w, curv), s=w / 0.9, z=7)


def branch_arrow(ax, x0, y0, x1, y1, lw=7, color=None):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>,head_length=1.1,head_width=0.8",
                                lw=lw, color=color or PAL["arrow"], shrinkA=0, shrinkB=0),
                zorder=3)


def legend_box(ax, x, y, w=0.36, h=0.085, primary="enth_cartoon"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006",
                 fc="white", ec="#333", lw=1.0, zorder=10))
    items = [("Clathrin", "comb"), ("Lipid", "pin"), ("Epsin (ENTH)", "primary"),
             ("AP2", "ap2"), ("IDP crowding", "crowd")]
    xs = np.linspace(x + w * 0.10, x + w * 0.90, len(items)); gy = y + h * 0.60
    for (lab, kind), gx in zip(items, xs):
        if kind == "primary":
            place_sprite(ax, primary, gx, gy, w=0.05, z=11)
        elif kind == "ap2":
            draw_ap2(ax, gx, gy, s=0.5, z=11)
        elif kind == "comb":
            ax.plot([gx - 0.02, gx + 0.02], [gy, gy], color=PAL["clathrin"], lw=1.6, zorder=11)
            for tx in np.linspace(gx - 0.02, gx + 0.02, 5):
                ax.plot([tx, tx], [gy, gy + 0.012], color=PAL["clathrin"], lw=0.7, zorder=11)
        elif kind == "pin":
            ax.add_patch(Circle((gx, gy + 0.008), 0.006, fc=PAL["lipid_head"], ec="none", zorder=11))
            ax.plot([gx, gx], [gy + 0.008, gy - 0.01], color=PAL["lipid_tail"], lw=0.8, zorder=11)
        elif kind == "crowd":
            draw_idp_crowd(ax, gx - 0.022, gx + 0.022, gy + 0.012, height=0.022,
                           n_chains=5, seed=3, z=11, direction=-1.0)
        ax.text(gx, y + h * 0.13, lab, ha="center", va="center", fontsize=5.0, zorder=11)


# ================= fetch + build (cached, gitignored) =================
def fetch_structures(cache_dir=None):
    import urllib.request as u
    scdir = cache_dir or _CACHE
    os.makedirs(scdir, exist_ok=True)
    written = {}
    for key, url in STRUCTURE_URLS.items():
        fname = f"{key}.pdb" if key == "1H0A" else f"AF_{key}.pdb"
        path = os.path.join(scdir, fname)
        if not (os.path.exists(path) and os.path.getsize(path) > 1000):
            open(path, "wb").write(u.urlopen(url, timeout=60).read())
        written[key] = path
    return written


def build_sprites(cache_dir=None, out_dir=None):
    scdir = cache_dir or _CACHE
    fetch_structures(scdir)
    odir = out_dir or SPRITE_DIR
    os.makedirs(odir, exist_ok=True)
    meta = {}
    for name, src in CARTOON_SOURCES.items():
        path = (os.path.join(scdir, f"{src['pdb']}.pdb") if "pdb" in src
                else os.path.join(scdir, f"AF_{src['uniprot']}.pdb"))
        render_cartoon(path, resrange=src["resrange"], color=src["color"],
                       out=os.path.join(odir, f"{name}.png"))
        meta[name] = src
    json.dump(meta, open(os.path.join(odir, "cartoon_meta.json"), "w"), indent=2, default=str)
    return meta
