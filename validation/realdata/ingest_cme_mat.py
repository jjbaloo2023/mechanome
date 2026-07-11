"""
Ingest cmeAnalysis .mat cohort files into a normalized IntensityCohort.

cmeAnalysis (DanuserLab) is the standard clathrin-coated-pit detection and
tracking package. Its per-condition output is a struct with:
  data  : per-cell acquisition metadata (markers, framerate, pixelSize, ...)
  res.cohorts : averaged intensity-vs-time trajectories grouped by lifetime bin,
                for each fluorescence channel, with SEM envelopes (Amin/Aplus).

This is OBSERVABLE #1 in the project's observable ladder: a coat-assembly
intensity proxy, NOT a curvature or force measurement. The adapter records that
classification and full provenance so downstream code cannot silently treat it
as curvature. It refuses nothing here; the observable classifier does the
routing.
"""
import os
import datetime
import dataclasses
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import scipy.io as sio


@dataclass
class IntensityCohort:
    """One lifetime-binned intensity cohort from cmeAnalysis, per channel."""
    condition: str                 # e.g. "iso", "hypo", "hyper"
    channels: List[str]            # marker names, e.g. ["RFP", "EGFP"]
    lifetime_bounds_s: List[float] # cohort bin edges (seconds)
    t_by_bin: list                 # per bin: time axis (s), aligned to cohort
    A_by_bin: list                 # per bin: [n_channel] arrays of mean intensity
    Amin_by_bin: list              # per bin: lower SEM envelope, per channel
    Aplus_by_bin: list             # per bin: upper SEM envelope, per channel
    framerate_s: float
    pixel_size_um: float
    n_cells: int
    observable: str = "1_intensity"
    provenance: dict = field(default_factory=dict)

    @property
    def n_bins(self):
        return len(self.lifetime_bounds_s) - 1

    def bin_trajectory(self, bin_idx, channel_idx):
        """(t, A, Amin, Aplus) for one lifetime bin and channel."""
        t = np.ravel(self.t_by_bin[bin_idx]).astype(float)
        A = np.ravel(self.A_by_bin[channel_idx][bin_idx]).astype(float)
        lo = np.ravel(self.Amin_by_bin[channel_idx][bin_idx]).astype(float)
        hi = np.ravel(self.Aplus_by_bin[channel_idx][bin_idx]).astype(float)
        return t, A, lo, hi

    def to_dict(self):
        d = dataclasses.asdict(self)
        # arrays -> lists for JSON
        d["t_by_bin"] = [np.ravel(x).astype(float).tolist() for x in self.t_by_bin]
        d["A_by_bin"] = [[np.ravel(self.A_by_bin[c][b]).astype(float).tolist()
                          for b in range(self.n_bins)] for c in range(len(self.channels))]
        # keep envelopes compact (peaks only) to bound JSON size
        d.pop("Amin_by_bin"); d.pop("Aplus_by_bin")
        return d


def ingest_cme_mat(path, condition=None):
    """Read a cmeAnalysis .mat into an IntensityCohort with provenance."""
    m = sio.loadmat(path, struct_as_record=False, squeeze_me=True)
    if "res" not in m or not hasattr(m["res"], "cohorts"):
        raise ValueError(f"{path}: not a cmeAnalysis result (.res.cohorts missing)")
    data0 = np.atleast_1d(m["data"]).flat[0]
    markers = [str(x) for x in np.atleast_1d(data0.markers)]
    co = np.atleast_1d(m["res"].cohorts).flat[0]
    bounds = [float(x) for x in np.ravel(co.bounds)]
    # A/Amin/Aplus are (n_channel, n_bin) object arrays; t is (n_bin,) object array
    A = co.A
    n_ch = len(markers)
    n_bin = len(bounds) - 1
    A_by_bin = [[A[c][b] for b in range(n_bin)] for c in range(n_ch)]
    Amin_by_bin = [[co.Amin[c][b] for b in range(n_bin)] for c in range(n_ch)]
    Aplus_by_bin = [[co.Aplus[c][b] for b in range(n_bin)] for c in range(n_ch)]
    t_by_bin = [co.t[b] for b in range(n_bin)]
    if condition is None:
        condition = os.path.splitext(os.path.basename(path))[0]
    prov = dict(
        source_path=path,
        source_basename=os.path.basename(path),
        retrieval_date=datetime.date.today().isoformat(),
        package="cmeAnalysis (DanuserLab)",
        acquisition="TIRF",
        markers=markers,
    )
    return IntensityCohort(
        condition=condition, channels=markers, lifetime_bounds_s=bounds,
        t_by_bin=t_by_bin, A_by_bin=A_by_bin, Amin_by_bin=Amin_by_bin,
        Aplus_by_bin=Aplus_by_bin,
        framerate_s=float(getattr(data0, "framerate", np.nan)),
        pixel_size_um=float(getattr(data0, "pixelSize", np.nan)),
        n_cells=int(np.atleast_1d(m["data"]).size),
        provenance=prov)


if __name__ == "__main__":
    import sys
    base = ("/root/projects/Epsin paper comm bio 2020/final figure/"
            "data availability/Figure 2/Osmotic shock")
    for cond in ["iso", "hypo", "hyper"]:
        c = ingest_cme_mat(os.path.join(base, f"{cond}.mat"), condition=cond)
        print(f"{cond}: {c.n_bins} bins, channels={c.channels}, "
              f"{c.n_cells} cells, fr={c.framerate_s}s, obs={c.observable}")
        t, A, lo, hi = c.bin_trajectory(3, 0)
        print(f"   bin3 ch0(RFP): nT={len(t)} peak={A.max():.0f} "
              f"SEM~{np.mean(hi-lo)/2:.1f}")
