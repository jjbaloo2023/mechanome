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
    "anth_ap180_cartoon": dict(uniprot="O60641", resrange=(1, 289), color=PAL["anth"],
                         note="AP180 (SNAP91) ANTH domain (AlphaFold)"),
}
STRUCTURE_URLS = {
    "1H0A":   "https://files.rcsb.org/download/1H0A.pdb",
    "Q13492": "https://alphafold.ebi.ac.uk/files/AF-Q13492-F1-model_v6.pdb",
    "O60641": "https://alphafold.ebi.ac.uk/files/AF-O60641-F1-model_v6.pdb",
    "2XA7":   "https://files.rcsb.org/download/2XA7.pdb",   # AP2 core (Jackson et al. 2010)
}

# ---- supporting-cast structures drawn as space-filling silhouettes (atomic, from PDB) ----
SPACEFILL_SOURCES = {
    "ap2_core": dict(pdb="2XA7", color=PAL["ap2"],
                     note="AP2 clathrin-adaptor core heterotetramer, X-ray 2XA7"),
}

# ---- per-primary IDP region: residue count + folded-domain size (nm) for Rh scaling ----
# Epsin EPN1 (576 aa): ENTH 1-158, IDP 159-576 (418 aa). PICALM (652): ANTH 1-289,
# IDP ~362 aa. AP180/SNAP91 (907): ANTH 1-289, IDP ~617 aa.
IDP_META = {
    "enth_cartoon":       dict(idp_res=418, fold_nm=2.8),
    "anth_cartoon":       dict(idp_res=362, fold_nm=3.0),
    "anth_ap180_cartoon": dict(idp_res=617, fold_nm=3.0),
}
RH_REF_NM = 5.2   # epsin IDP Rh, the reference for the on-figure coil scale


def idp_Rh_nm(n_res, nu=0.54, r0=0.20):
    """Hydrodynamic radius (nm) of an intrinsically disordered chain of n_res residues,
    Rh = r0 * N**nu (Marsh & Forman-Kay 2010 IDP scaling). A steric-hindrance measure."""
    return r0 * (n_res ** nu)


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


def render_spacefill(pdb_path, color="#9b4fa0", chain=None, resrange=None, px=340,
                     out=None, grid=340, r=5):
    """Space-filling silhouette sprite from atomic coordinates (all atoms), PCA-oriented
    and depth-shaded. Used for supporting-cast structures where a full ribbon cartoon
    would be too busy at glyph size (e.g. the AP2 heterotetramer core)."""
    import biotite.structure.io.pdb as _pdb
    import biotite.structure as _struc
    from scipy.ndimage import binary_closing, binary_fill_holes
    arr = _pdb.PDBFile.read(pdb_path).get_structure(model=1)
    arr = arr[_struc.filter_amino_acids(arr)]
    if chain is not None:
        arr = arr[arr.chain_id == chain]
    if resrange:
        arr = arr[(arr.res_id >= resrange[0]) & (arr.res_id <= resrange[1])]
    P = arr.coord - arr.coord.mean(0)
    _, _, Vt = np.linalg.svd(P, full_matrices=False); P = P @ Vt.T
    xy, z = P[:, :2], P[:, 2]
    lo, hi = xy.min(0), xy.max(0); span = (hi - lo).max() * 1.10; c = (lo + hi) / 2
    gx = ((xy[:, 0] - c[0]) / span + 0.5) * (grid - 1)
    gy = ((xy[:, 1] - c[1]) / span + 0.5) * (grid - 1)
    zb = np.full((grid, grid), -np.inf)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; disk = (xx * xx + yy * yy <= r * r)
    for i in np.argsort(z):
        xi, yi = int(round(gx[i])), int(round(gy[i]))
        x0, x1 = max(0, xi - r), min(grid, xi + r + 1)
        y0, y1 = max(0, yi - r), min(grid, yi + r + 1)
        dsub = disk[(y0 - (yi - r)):(y1 - (yi - r)), (x0 - (xi - r)):(x1 - (xi - r))]
        block = zb[y0:y1, x0:x1]; block[dsub & (z[i] > block)] = z[i]
    mask = binary_fill_holes(binary_closing(np.isfinite(zb), iterations=2))
    zz = zb.copy(); zz[~np.isfinite(zz)] = np.nanmin(zz[np.isfinite(zz)])
    znorm = (zz - zz.min()) / (np.ptp(zz) + 1e-9)
    base = np.array(to_rgb(color)); rgba = np.zeros((grid, grid, 4))
    shade = 0.5 + 0.5 * gaussian_filter(znorm, 1.5)
    for k in range(3):
        rgba[:, :, k] = np.clip(base[k] * shade, 0, 1)
    rgba[:, :, 3] = gaussian_filter(mask.astype(float), 0.7)
    fig, ax = plt.subplots(figsize=(3, 3)); ax.axis("off"); ax.set_aspect("equal")
    ax.imshow(np.flipud(rgba), interpolation="bilinear")
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


def draw_clathrin_envelope(ax, cx, cy, w, curv, neck=False, n_facets=9, z=3, color=None, off=0.19):
    """Clathrin coat as a faceted ENVELOPE on the cytoplasmic-distal face: straight
    facet chords between vertices that lie ON the membrane-parallel offset curve, so
    the lattice stays tangential to the curvature with shallow bend angles at each
    vertex (edge-of-a-buckyball / geodesic-dome idiom). Drawn below the membrane-
    proximal adaptor heads (epsin/AP2), on the same cytoplasmic side."""
    color = color or PAL["clathrin"]
    xs = np.linspace(-w / 2, w / 2, n_facets)
    yc, nx, ny = _profile(xs, w, curv, neck)
    vx = cx + xs; vy = cy + yc - ny * off * w        # offset along -normal (cytoplasmic)
    ax.plot(vx, vy, color=color, lw=2.3, zorder=z, solid_capstyle="round", solid_joinstyle="round")
    ax.scatter(vx, vy, s=15, c=color, edgecolors="none", zorder=z + 0.1)


def draw_ap2(ax, x, y, s=1.0, z=6, w=None):
    """Supporting cast: AP2 adaptor core as an atomic space-filling sprite (PDB 2XA7).
    Falls back to a tri-lobe glyph if the sprite has not been built."""
    ew = w if w is not None else 0.075 * s
    try:
        place_sprite(ax, "ap2_core", x, y, w=ew, z=z)
    except FileNotFoundError:
        for dx, dy in [(-0.028, 0.0), (0.028, 0.0), (0.0, -0.032)]:
            ax.add_patch(Ellipse((x + dx * s, y + dy * s), 0.06 * s, 0.052 * s,
                                 fc=PAL["ap2"], ec="#5e2b62", lw=0.6, zorder=z))


# ================= IDP crowding brush (drawn) =================
def draw_idp_coil(ax, x0, y0, radius, color=None, seed=0, z=4, down=-1.0, halo=True,
                  nseg=9):
    """Intrinsically disordered region of ONE molecule as a single ENTANGLED shoelace
    anchored at the folded domain's C-terminus (x0, y0): a smooth confined random walk
    that folds back and crosses itself, contained within the IDP's hydrodynamic radius
    Rh (a steric-hindrance measure). Crowding is shown by the overlap of adjacent
    chains' excluded-volume halos. Epsin = ENTH + IDP; AP180/CALM = ANTH + IDP.
    """
    color = color or PAL["idp"]
    rng = np.random.default_rng(seed)
    cxc, cyc = x0, y0 + down * radius * 0.95        # chain centre ~Rh from the C-terminus
    if halo:
        ax.add_patch(Circle((cxc, cyc), radius, fc=color, ec="none", alpha=0.10, zorder=z - 0.3))
    # random waypoints filling the Rh disc; spline through them -> self-crossing tangle
    ang = rng.uniform(0, 2 * np.pi, nseg)
    rad = radius * np.sqrt(rng.uniform(0.1, 1.0, nseg))
    wx = np.concatenate([[x0], cxc + rad * np.cos(ang), [cxc]])
    wy = np.concatenate([[y0], cyc + rad * np.sin(ang) * 0.9, [cyc]])
    tck, _ = splprep([wx, wy], s=0, k=3)
    sm = np.array(splev(np.linspace(0, 1, 170), tck)).T
    ax.plot(sm[:, 0], sm[:, 1], color=color, lw=1.4, alpha=0.9, solid_capstyle="round", zorder=z)


# ================= composite node =================
def node(ax, cx, cy, w, curv, n_eps, neck=False, ap2=True, primary="enth_cartoon", idp=True):
    """Membrane-state cartoon: bilayer + clathrin comb + n_eps cartoon players
    + IDP crowding brush (density ~ n_eps) + AP2 glyph."""
    draw_bilayer(ax, cx, cy, w, curv, neck)
    draw_clathrin_envelope(ax, cx, cy, w, curv, neck)
    ew = 0.34 * w
    # IDP coil radius (data units): Rh of THIS protein's IDP relative to epsin's, scaled
    # so epsin's coil ~ the folded-head width. A steric-hindrance size, not a chain count.
    meta = IDP_META.get(primary, IDP_META["enth_cartoon"])
    coil_r = ew * 0.42 * (idp_Rh_nm(meta["idp_res"]) / RH_REF_NM)
    if n_eps > 0:
        xs = np.linspace(-w * 0.30, w * 0.30, n_eps) if n_eps > 1 else np.array([0.0])
        yc = (_profile(xs, w, curv, neck)[0] if n_eps > 1
              else np.array([_center_depth(w, curv)]))
        for i, ex in enumerate(xs):
            ay = cy + yc[i] - 0.09 * w
            place_sprite(ax, primary, cx + ex, ay, w=ew, z=6)
            if idp:
                draw_idp_coil(ax, cx + ex, ay - ew * 0.34, coil_r,
                              seed=int(abs(cx * 1000) + i), z=4)
    if ap2:
        # Multiple AP2 adaptors per coated pit, spread along the coat floor. More
        # adaptors on a wider/deeper pit; each is an atomic sprite from PDB 2XA7.
        n_ap2 = 2 if n_eps <= 1 else 3
        axs = np.linspace(-w * 0.20, w * 0.20, n_ap2)
        ayc = _profile(axs, w, curv, neck)[0]
        for k, adx in enumerate(axs):
            draw_ap2(ax, cx + adx, cy + ayc[k] - 0.11 * w, w=ew * 0.7, z=7 + 0.01 * k)


def branch_arrow(ax, x0, y0, x1, y1, lw=7, color=None):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>,head_length=1.1,head_width=0.8",
                                lw=lw, color=color or PAL["arrow"], shrinkA=0, shrinkB=0),
                zorder=3)


def legend_box(ax, x, y, w=0.36, h=0.085, primary="enth_cartoon", primary_label="Epsin (ENTH)"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006",
                 fc="white", ec="#333", lw=1.0, zorder=10))
    items = [("Clathrin", "facet"), ("Lipid", "pin"), (primary_label, "primary"),
             ("AP2", "ap2"), ("IDP", "idp")]
    xs = np.linspace(x + w * 0.10, x + w * 0.90, len(items)); gy = y + h * 0.60
    for (lab, kind), gx in zip(items, xs):
        if kind == "primary":
            place_sprite(ax, primary, gx, gy, w=0.05, z=11)
        elif kind == "ap2":
            draw_ap2(ax, gx, gy, w=0.05, z=11)
        elif kind == "facet":
            # short faceted clathrin envelope segment (straight chords, shallow bends)
            fx = np.linspace(gx - 0.026, gx + 0.026, 5)
            fy = gy + np.array([0.006, -0.004, 0.006, -0.004, 0.006])
            ax.plot(fx, fy, color=PAL["clathrin"], lw=2.0, zorder=11,
                    solid_capstyle="round", solid_joinstyle="round")
            ax.scatter(fx, fy, s=10, c=PAL["clathrin"], edgecolors="none", zorder=11.1)
        elif kind == "pin":
            ax.add_patch(Circle((gx, gy + 0.008), 0.006, fc=PAL["lipid_head"], ec="none", zorder=11))
            ax.plot([gx, gx], [gy + 0.008, gy - 0.01], color=PAL["lipid_tail"], lw=0.8, zorder=11)
        elif kind == "idp":
            draw_idp_coil(ax, gx, gy + 0.014, 0.017, seed=3, z=11, down=-1.0, halo=True)
        ax.text(gx, y + h * 0.13, lab, ha="center", va="center", fontsize=5.0, zorder=11)


# ================= fetch + build (cached, gitignored) =================
def fetch_structures(cache_dir=None):
    import urllib.request as u
    scdir = cache_dir or _CACHE
    os.makedirs(scdir, exist_ok=True)
    written = {}
    for key, url in STRUCTURE_URLS.items():
        if key == "1H0A":
            fname = f"{key}.pdb"
        elif key == "2XA7":
            fname = f"AP2_{key}.pdb"
        else:
            fname = f"AF_{key}.pdb"
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
    for name, src2 in SPACEFILL_SOURCES.items():
        path = os.path.join(scdir, f"{src2['pdb']}.pdb") if os.path.exists(
            os.path.join(scdir, f"{src2['pdb']}.pdb")) else os.path.join(scdir, f"AP2_{src2['pdb']}.pdb")
        render_spacefill(path, color=src2["color"], out=os.path.join(odir, f"{name}.png"))
        meta[name] = src2
    json.dump(meta, open(os.path.join(odir, "cartoon_meta.json"), "w"), indent=2, default=str)
    return meta
