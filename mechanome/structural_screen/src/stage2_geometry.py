"""Stage 2 - A(z) cross-section profiles, intrinsic curvature, wedge volume, charge moment.

Mechanism-appropriate curvature extraction:
  - channels: TM-restricted (|z|<15A) cone-shape c0, membrane-spanning chains only (strips Fabs/partners)
  - BAR/scaffolds: circular arc fit to the dimer backbone centerline, c0 = 1/R
     (validated: amphiphysin R~9.8nm vs lit ~11nm; endophilin R~8.0nm vs lit 6-11nm)
"""
import numpy as np
from scipy.spatial import ConvexHull
from scipy.integrate import trapezoid

CHARGE = {"ARG":+1,"LYS":+1,"ASP":-1,"GLU":-1}
TM_HALF = 15.0

def area_profile(coords, z_half=TM_HALF, dz=2.0):
    z=coords[:,2]; zs=np.arange(-z_half,z_half+1e-6,dz); zc=0.5*(zs[:-1]+zs[1:])
    A=np.full(len(zc),np.nan)
    for i,(lo,hi) in enumerate(zip(zs[:-1],zs[1:])):
        pts=coords[(z>=lo)&(z<hi)][:,:2]
        if len(pts)>=3:
            try: A[i]=ConvexHull(pts).volume
            except Exception: pass
    return zc,A

def circle_fit_algebraic(x,y):
    A=np.column_stack([x,y,np.ones_like(x)]); b=x**2+y**2
    D,E,F=np.linalg.lstsq(A,b,rcond=None)[0]; cx,cy=D/2,E/2
    R=np.sqrt(cx**2+cy**2+F); res=np.hypot(x-cx,y-cy)-R
    return R, np.sqrt((res**2).mean())

def channel_tm_cone(atom_array, zlim=TM_HALF):
    """TM-restricted cone c0 for a channel, using the modal largest-size chain class only.

    Rationale: cryo-EM channel structures often bundle soluble partners (RhoA in TRPV4 8FC7) or Fab
    fragments (TRAAK 4I9W). A membrane-spanning z-test alone does NOT strip a partner that happens to
    straddle the bilayer plane. Restricting to the modal-size subunit class recovers the true oligomer;
    ALWAYS cross-check len(kept_chains) against the known oligomeric state (see stoichiometry table).
    """
    ca = atom_array.atom_name == "CA"
    chs, cnts = np.unique(atom_array.chain_id[ca], return_counts=True)
    top = cnts.max(); keep = [c for c, n in zip(chs, cnts) if n >= 0.8 * top]
    sel = np.isin(atom_array.chain_id, keep)
    coords = atom_array.coord[sel]; z = coords[:, 2]; C = coords[np.abs(z) < zlim]
    def rad(a, b):
        m = (C[:, 2] >= a) & (C[:, 2] < b)
        return np.sqrt(ConvexHull(C[m][:, :2]).volume / np.pi) if m.sum() >= 3 else np.nan
    r_out = np.nanmean([rad(zl, zl + 3) for zl in np.arange(3, zlim - 2, 3)])
    r_in  = np.nanmean([rad(zl, zl + 3) for zl in np.arange(-zlim + 2, -3, 3)])
    r_mid = rad(-3, 3); dz = zlim - 3
    c0 = ((r_out - r_in) / (2 * dz)) / r_mid if r_mid else np.nan
    return dict(kept_chains=keep, n_chains=len(keep), c0_invnm=c0 * 10,
                A_foot_nm2=np.pi * r_mid ** 2 / 100 if r_mid else np.nan)

# Known oligomeric state — assert n_chains matches before trusting a channel's geometry.
KNOWN_OLIGOMER = {"2OAR":5, "2VV5":7, "6B3R":3, "8FC7":4, "6MGV":2, "4WFF":2, "4TWK":2, "6QMB":2}

def bar_arc_curvature(coords, nbins=18):
    """c0 = 1/R of the BAR dimer concave face. Requires the biological assembly (both monomers)."""
    Xc=coords-coords.mean(0); U,S,Vt=np.linalg.svd(Xc,full_matrices=False); P=Xc@Vt.T
    long=P[:,0]; edges=np.linspace(long.min(),long.max(),nbins); cl=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        m=(long>=lo)&(long<hi)
        if m.sum()>=3: cl.append([long[m].mean(),P[m,1].mean(),P[m,2].mean()])
    cl=np.array(cl); best=None
    for j in [1,2]:  # bending plane = the one with largest centerline sagitta
        x,y=cl[:,0],cl[:,j]; sag=np.ptp(y-np.polyval(np.polyfit(x,y,1),x))
        R,rmse=circle_fit_algebraic(x,y)
        if best is None or sag>best[2]: best=(R,rmse,sag)
    R=best[0]; L=np.ptp(P[:,0]); W=np.ptp(P[:,1])
    return dict(c0_invnm=10.0/R, R_nm=R/10, A_foot_nm2=L*W/100)
