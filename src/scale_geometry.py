"""Proteome-scale uniform TM-cone geometry from OPM-oriented PDB files.

ONE metric applied identically to every protein (no per-protein curation):
  - OPM files already place the membrane normal on z and mark bilayer boundaries with DUM atoms.
  - Center on the DUM midplane, restrict to the TM slab (|z|<15 A), take convex-hull cross-sections,
    and fit a cone taper c0 = ((r_out - r_in)/(2*dz)) / r_mid.
  - Chain selection is TWO stages, because the TM-span test alone does NOT strip soluble partners:
    a bound partner (e.g. RhoA in TRPV4 8FC7) can itself straddle the bilayer plane and pass the span
    test (all 8 chains of 8FC7 test TMspan=True). Stage 1: keep chains whose CA reach both above +10
    and below -10 A (drops peripheral/one-leaflet chains). Stage 2 CONTAMINATION GUARD: among the
    spanning chains, restrict to the modal-size subunit class (CA count >= 0.8*max), so a smaller
    hetero-partner is dropped without a hand-curated oligomer table. This is the automated form of the
    stoichiometry cross-check that caught RhoA; validated on the 8FC7 chain composition (keeps the 4
    TRPV4 subunits, drops the 4 RhoA copies, sets contam_flag=True). Report n_chains + contam_flag.

Scope caveat (bank it honestly): this metric is sensitive to transmembrane conical shape. It
UNDERRATES scaffold- (BAR) and crowding- (IDP) based curvature generation, which act outside the
TM slab. Those mechanisms are already well characterized; the interesting hits here are TM proteins
with high cone taper that are NOT textbook curvature generators.
"""
import numpy as np
from scipy.spatial import ConvexHull

TM_HALF = 15.0

def parse_opm(path):
    """Return (ca_coord, ca_chain, dum_z) from an OPM PDB. DUM atoms mark bilayer boundary planes."""
    ca_xyz=[]; ca_ch=[]; dum_z=[]
    with open(path) as fh:
        for ln in fh:
            rec=ln[:6]
            if rec in ("ATOM  ","HETATM"):
                resn=ln[17:20].strip(); atom=ln[12:16].strip()
                try: x,y,z=float(ln[30:38]),float(ln[38:46]),float(ln[46:54])
                except ValueError: continue
                if resn=="DUM":
                    dum_z.append(z)
                elif atom=="CA":
                    ca_xyz.append((x,y,z)); ca_ch.append(ln[21])
    return (np.array(ca_xyz,dtype=float) if ca_xyz else np.zeros((0,3)),
            np.array(ca_ch), np.array(dum_z,dtype=float))

def tm_cone_geometry(path, zlim=TM_HALF):
    ca,ch,dum = parse_opm(path)
    if len(ca)<20:
        return dict(ok=False, reason="too_few_CA", n_ca=len(ca))
    # DUM midplane = membrane center; if no DUM, fall back to CA median z
    z0 = float(np.median(dum)) if len(dum)>=2 else float(np.median(ca[:,2]))
    ca=ca.copy(); ca[:,2]-=z0
    # TM-spanning chains: CA both above +10 and below -10
    span=[]
    for c in np.unique(ch):
        zc=ca[ch==c][:,2]
        if zc.max()>10 and zc.min()<-10: span.append(c)
    if not span:  # no chain spans -> peripheral; not measurable by TM cone
        return dict(ok=False, reason="no_TM_span", n_ca=len(ca), n_chains=0)
    # CONTAMINATION GUARD (automated replacement for the hand-curated stoichiometry cross-check that
    # caught RhoA in TRPV4 8FC7): a soluble partner can straddle the bilayer plane and pass the span
    # test, inflating the footprint. Restrict to the MODAL-SIZE subunit class among spanning chains
    # (CA count >= 0.8*max) so a smaller bound partner (RhoA 190 CA vs TRPV4 631) is dropped without a
    # curated table. Flag residual size heterogeneity among kept chains as a QC signal.
    sizes={c:int((ch==c).sum()) for c in span}
    top=max(sizes.values()); keep=[c for c,n in sizes.items() if n>=0.8*top]
    dropped=[c for c in span if c not in keep]
    kept_sizes=[sizes[c] for c in keep]
    size_cv=float(np.std(kept_sizes)/np.mean(kept_sizes)) if len(kept_sizes)>1 else 0.0
    contam_flag = len(dropped)>0 or size_cv>0.15   # heterosize partner dropped, or kept chains uneven
    sel=np.isin(ch,keep); C=ca[sel]; C=C[np.abs(C[:,2])<zlim]
    if len(C)<20:
        return dict(ok=False, reason="empty_slab", n_ca=len(ca), n_chains=len(keep))
    def rad(a,b):
        m=(C[:,2]>=a)&(C[:,2]<b)
        if m.sum()<3: return np.nan
        try: return np.sqrt(ConvexHull(C[m][:,:2]).volume/np.pi)
        except Exception: return np.nan
    r_out=np.nanmean([rad(zl,zl+3) for zl in np.arange(3,zlim-2,3)])
    r_in =np.nanmean([rad(zl,zl+3) for zl in np.arange(-zlim+2,-3,3)])
    r_mid=rad(-3,3); dz=zlim-3
    if not r_mid or np.isnan(r_mid) or np.isnan(r_out) or np.isnan(r_in):
        return dict(ok=False, reason="nan_radius", n_ca=len(ca), n_chains=len(keep))
    c0=((r_out-r_in)/(2*dz))/r_mid
    return dict(ok=True, n_ca=len(ca), n_chains=len(keep), n_span=len(span),
                n_dropped=len(dropped), contam_flag=bool(contam_flag), size_cv=round(size_cv,3),
                c0_invnm=c0*10.0, A_foot_nm2=np.pi*r_mid**2/100.0,
                r_out=r_out, r_in=r_in, r_mid=r_mid)
