"""
Observable-#3 ingestion: BioTISR live-cell TIRF-SIM clathrin-coated-pit movies.

BioTISR (Zenodo record 13843670, "2D Data of BioTISR dataset"; part of the
BioTISR collection tied to the DPA-TISR paper, Nat Biotech 2025) provides
super-resolution TIRF-SIM time-lapse of CCPs. Each cell's SIM_gt.mrc is a
20-frame 1024x1024 reconstructed super-res stack in which individual clathrin
coats appear as compact puncta -- observable #3, curvature in real time, the
input the force inverse actually needs.

This module:
  - reads the MRC stack (no external MRC dependency; header parsed inline),
  - detects CCP puncta and tracks them across frames,
  - measures a per-frame projected coat footprint radius R_proj(t),
  - converts R_proj(t) to an effective mean-curvature proxy H(t) ~ 1/R_proj,
    with per-frame uncertainty,
emitting a GeometryTrace-compatible object the inverse can consume.

Documented assumptions (recorded in provenance, NOT silently baked in):
  - pixel size 31.3 nm/px is an ASSUMPTION for the SIM_gt reconstruction; it was
    NOT read from the file header (the MRC cell/grid fields are mis-stored) nor
    confirmed against the acquisition paper in this build. The absolute
    curvature scale depends on it, so any absolute H value is provisional until
    the pixel size is verified from the dataset's own metadata.
  - the detector measures an equivalent-disc footprint radius from a
    DoG-thresholded punctum; it does NOT test for annular (ring) structure.
    R_proj is therefore a projected coat-footprint size, used as a PROXY for
    coat curvature (H = 1/R_proj): a growing coat projects a larger footprint;
    as it closes (Omega) the footprint shrinks. This is a geometric proxy, not a
    calibrated 3D curvature -- flagged for the inverse's identifiability firewall.
"""
import os
import struct
import datetime
import dataclasses
from dataclasses import dataclass, field
from typing import List

import numpy as np
from scipy import ndimage as ndi

PX_NM = 31.3            # SIM_gt pixel size ASSUMPTION (unverified; not from header)
FRAME_INTERVAL_S = 1.0  # nominal; refine from acquisition metadata if available


def read_mrc(path):
    """Minimal MRC reader -> (stack[nz,ny,nx] float32)."""
    with open(path, "rb") as fh:
        hdr = fh.read(1024)
        nx, ny, nz = struct.unpack("<3i", hdr[0:12])
        mode = struct.unpack("<i", hdr[12:16])[0]
        dtype = {0: np.int8, 1: np.int16, 2: np.float32, 6: np.uint16}[mode]
        data = np.frombuffer(fh.read(), dtype=dtype).astype(np.float32)
    return data.reshape(nz, ny, nx)


@dataclass
class CurvatureTrace:
    """Per-pit projected-curvature trajectory from a SIM time-lapse."""
    cell_id: str
    track_id: int
    t_s: List[float]
    R_proj_nm: List[float]      # projected coat footprint radius
    R_proj_sd_nm: List[float]
    H_proxy_inv_nm: List[float] # 1 / R_proj  (mean-curvature proxy)
    H_proxy_sd_inv_nm: List[float]
    intensity: List[float]
    observable: str = "3_superres_curvature"
    provenance: dict = field(default_factory=dict)

    def to_dict(self):
        return dataclasses.asdict(self)


def _detect(frame, sig_lo=1.0, sig_hi=6.0, k=5.0, min_px=4, max_px=200):
    enh = ndi.gaussian_filter(frame, sig_lo) - ndi.gaussian_filter(frame, sig_hi)
    mask = enh > enh.std() * k
    lbl, n = ndi.label(mask)
    if n == 0:
        return []
    objs = ndi.find_objects(lbl)
    out = []
    for i, sl in enumerate(objs, start=1):
        m = lbl[sl] == i
        npx = int(m.sum())
        if npx < min_px or npx > max_px:
            continue
        cy, cx = ndi.center_of_mass(m)
        cy += sl[0].start; cx += sl[1].start
        # projected radius from the coat footprint area (equivalent-disc radius)
        R_proj = np.sqrt(npx / np.pi) * PX_NM
        # radius spread within the punctum as an uncertainty proxy
        ys, xs = np.nonzero(m)
        rr = np.sqrt((ys - ys.mean())**2 + (xs - xs.mean())**2) * PX_NM
        R_sd = float(rr.std()) if len(rr) > 2 else R_proj * 0.2
        inten = float(frame[sl][m].sum())
        out.append(dict(y=cy, x=cx, R_proj=R_proj, R_sd=max(R_sd, PX_NM),
                        npx=npx, inten=inten))
    return out


def _link(frames_dets, max_move_nm=250.0):
    """Greedy nearest-neighbour linking across frames."""
    tracks = []
    active = []  # (track_idx, last_y, last_x)
    for t, dets in enumerate(frames_dets):
        assigned = set()
        new_active = []
        for (ti, ly, lx) in active:
            best, bd = None, max_move_nm / PX_NM
            for j, d in enumerate(dets):
                if j in assigned:
                    continue
                dist = np.hypot(d["y"] - ly, d["x"] - lx)
                if dist < bd:
                    bd, best = dist, j
            if best is not None:
                assigned.add(best)
                tracks[ti].append((t, dets[best]))
                new_active.append((ti, dets[best]["y"], dets[best]["x"]))
        for j, d in enumerate(dets):
            if j in assigned:
                continue
            tracks.append([(t, d)])
            new_active.append((len(tracks) - 1, d["y"], d["x"]))
        active = new_active
    return tracks


def extract_curvature_traces(mrc_path, cell_id=None, min_len=6,
                             frame_interval_s=FRAME_INTERVAL_S):
    """Detect+track CCPs, return per-pit CurvatureTrace list."""
    vol = np.clip(read_mrc(mrc_path), 0, None)
    nz = vol.shape[0]
    dets = [_detect(vol[t]) for t in range(nz)]
    tracks = _link(dets)
    if cell_id is None:
        cell_id = os.path.basename(mrc_path).split("_SIM")[0]
    prov = dict(
        source=os.path.basename(mrc_path),
        dataset="BioTISR 2D Data (CCPs)",
        zenodo_record="13843670",
        doi="10.5281/zenodo.13843670",
        collection_doi="10.5281/zenodo.14760518",  # top-level BioTISR record
        acquisition="live-cell TIRF-SIM, SIM_gt reconstruction",
        pixel_size_nm=PX_NM, pixel_size_verified=False,
        frame_interval_s=frame_interval_s,
        retrieval_date=datetime.date.today().isoformat(),
        assumption="R_proj (equivalent-disc footprint radius) is a projected "
                   "coat-curvature proxy; H_proxy = 1/R_proj; absolute scale "
                   "depends on pixel_size_nm (unverified assumption)",
    )
    traces = []
    for k, tr in enumerate(tracks):
        if len(tr) < min_len:
            continue
        t_s = [t * frame_interval_s for t, _ in tr]
        R = np.array([d["R_proj"] for _, d in tr])
        Rsd = np.array([d["R_sd"] for _, d in tr])
        inten = [d["inten"] for _, d in tr]
        H = 1.0 / R
        Hsd = Rsd / R**2               # propagate 1/R uncertainty
        traces.append(CurvatureTrace(
            cell_id=cell_id, track_id=k, t_s=t_s,
            R_proj_nm=R.tolist(), R_proj_sd_nm=Rsd.tolist(),
            H_proxy_inv_nm=H.tolist(), H_proxy_sd_inv_nm=Hsd.tolist(),
            intensity=inten, provenance=prov))
    return traces


if __name__ == "__main__":
    import glob
    for mp in sorted(glob.glob("cache/biotisr/ccp/*_SIM_gt.mrc")):
        traces = extract_curvature_traces(mp)
        cell = os.path.basename(mp).split("_SIM")[0]
        if traces:
            lens = [len(t.t_s) for t in traces]
            Rmed = np.median([np.mean(t.R_proj_nm) for t in traces])
            print(f"{cell}: {len(traces)} tracked CCPs (len>=6), "
                  f"median track len {int(np.median(lens))}, median R_proj {Rmed:.0f} nm")
