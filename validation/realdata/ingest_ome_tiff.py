"""
Ingest paired TIRF / epi OME-TIFF acquisitions.

The IAV 2022 dataset stores, per cell, a TIRF image and an epi (widefield)
image of the SAME field, each a 3-channel stack:
  488 = epsin-EGFP, 561 = mCherry-CLC (clathrin), 640 = DiD (membrane).

Ground-truth fact that scopes the analysis: these are SINGLE-TIMEPOINT images
(SizeT = 1), not time-lapse movies. The epi/TIRF intensity ratio therefore
yields a per-punctum AXIAL DEPTH across a POPULATION of pits at one instant
(observable #2, a curvature proxy) -- not a depth trajectory over time for one
pit. The adapter records that distinction so downstream code does not fabricate
a time axis.
"""
import os
import re
import glob
import datetime
from dataclasses import dataclass, field
from typing import List

import numpy as np
import tifffile


# marker roles by acquisition wavelength (from the dataset's folder convention
# "epsin EGFP mchc clc" + DiD membrane label)
CHANNEL_ROLES = {"488-TIRF": "epsin", "561-TIRF": "clathrin", "640-TIRF": "membrane"}


@dataclass
class PairedField:
    """One cell imaged in both TIRF and epi, single timepoint, N channels."""
    cell_id: str
    condition: str                 # e.g. "IAV", "UDM"
    channel_names: List[str]
    channel_roles: List[str]
    tirf: np.ndarray               # [C, Y, X]
    epi: np.ndarray                # [C, Y, X]
    n_timepoints: int              # 1 for this dataset (recorded explicitly)
    observable: str = "2_epitirf_depth"
    provenance: dict = field(default_factory=dict)

    def channel(self, role, which="tirf"):
        idx = self.channel_roles.index(role)
        return (self.tirf if which == "tirf" else self.epi)[idx]


def _read_ome(path):
    with tifffile.TiffFile(path) as tf:
        arr = tf.series[0].asarray()
        md = tf.ome_metadata or ""
    names = re.findall(r'Channel[^>]*Name="([^"]+)"', md)
    szt = re.findall(r'SizeT="(\d+)"', md)
    n_t = max((int(x) for x in szt), default=1)
    if arr.ndim == 2:
        arr = arr[None]
    return arr, names, n_t


def ingest_paired_field(tirf_path, epi_path, cell_id=None, condition=None):
    """Read a matched TIRF+epi pair into a PairedField with provenance."""
    tirf, names, n_t = _read_ome(tirf_path)
    epi, names_e, _ = _read_ome(epi_path)
    names = names or [f"ch{i}" for i in range(tirf.shape[0])]
    roles = [CHANNEL_ROLES.get(n, n) for n in names]
    if cell_id is None:
        cell_id = os.path.basename(os.path.dirname(tirf_path))
    prov = dict(
        tirf_path=tirf_path, epi_path=epi_path,
        retrieval_date=datetime.date.today().isoformat(),
        acquisition="paired TIRF + epi (single timepoint)",
        channel_names=names, note="SizeT=1: population snapshot, not time-lapse",
    )
    return PairedField(
        cell_id=cell_id, condition=condition or "", channel_names=names,
        channel_roles=roles, tirf=tirf, epi=epi, n_timepoints=n_t, provenance=prov)


def find_tirf_epi_pairs(condition_dir):
    """Match tirf/cell_N with epi/cell_N under a condition directory."""
    tirf_cells = {os.path.basename(p): p for p in glob.glob(os.path.join(condition_dir, "tirf", "cell_*"))}
    epi_cells = {os.path.basename(p): p for p in glob.glob(os.path.join(condition_dir, "epi", "cell_*"))}
    pairs = []
    for cell in sorted(set(tirf_cells) & set(epi_cells)):
        tf = glob.glob(os.path.join(tirf_cells[cell], "**", "*.ome.tif"), recursive=True)
        ef = glob.glob(os.path.join(epi_cells[cell], "**", "*.ome.tif"), recursive=True)
        if tf and ef:
            pairs.append((cell, tf[0], ef[0]))
    return pairs


if __name__ == "__main__":
    cond = ("/root/projects/IAV paper membranes 2022/IAV and NP data/"
            "080421 epsin EGFP mchc clc IAV/epsin/IAV")
    pairs = find_tirf_epi_pairs(cond)
    print(f"matched TIRF+epi pairs: {len(pairs)}")
    if pairs:
        cell, tp, ep = pairs[0]
        pf = ingest_paired_field(tp, ep, cell_id=cell, condition="IAV")
        print(f"{cell}: channels={pf.channel_names} roles={pf.channel_roles}")
        print(f"   tirf={pf.tirf.shape} epi={pf.epi.shape} nT={pf.n_timepoints} obs={pf.observable}")
        clc = pf.channel("clathrin", "tirf")
        print(f"   clathrin(TIRF) intensity range: {clc.min()}-{clc.max()}")
