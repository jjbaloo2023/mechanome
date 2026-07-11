"""
Structure identification + model routing for super-res movies.

The reframed workflow: look at the image, identify which structure is being
imaged, and route it to the curvo model appropriate to that structure. curvo's
inverse is a coated-pit (spherical-cap) membrane-mechanics engine -- it applies
to clathrin-coated pits, NOT to filaments, tubules, or organelles. This module
makes that routing explicit and refuses to run the CCS inverse on structures
whose physics the forward model does not describe.

Identity is established two ways and cross-checked:
  1. dataset label (BioTISR names the structure in the archive path), and
  2. a morphology signature computed from the image itself -- puncta vs
     filaments vs extended tubules/organelles -- so a mislabelled or unlabelled
     movie is still classified from pixels.

Routing:
  clathrin-coated pit -> curvo CCS inverse (spherical-cap; force via coat prior)
  F-actin             -> machinery / orchestration partner (force-GENERATING;
                         not a membrane cap, so no CCS inverse -- it informs the
                         active term, it is not a substrate for it)
  microtubule / mitochondria / lysosome -> OUT OF SCOPE for the CCS inverse
                         (not endocytic coated pits; reported, not modelled)
"""
import dataclasses
from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi

# structure -> (is CME machinery?, curvo route)
STRUCTURE_ROUTES = {
    "clathrin_coated_pit": (True, "ccs_inverse",
        "spherical-cap membrane inverse; force identified via structural coat prior"),
    "f_actin": (True, "orchestration_partner",
        "force-generating machinery; informs the active term, not a CCS substrate"),
    "microtubule": (False, "out_of_scope",
        "cytoskeletal filament, not an endocytic coated pit -- CCS inverse N/A"),
    "mitochondria": (False, "out_of_scope",
        "organelle, not an endocytic coated pit -- CCS inverse N/A"),
    "lysosome": (False, "out_of_scope",
        "organelle, not an endocytic coated pit -- CCS inverse N/A"),
}

# BioTISR archive label -> canonical structure key
LABEL_MAP = {
    "ccps": "clathrin_coated_pit", "ccp": "clathrin_coated_pit",
    "f-actin": "f_actin", "f-actin_nonlinear": "f_actin", "factin": "f_actin",
    "microtubules": "microtubule", "mts": "microtubule",
    "mitochondria": "mitochondria", "mito": "mitochondria",
    "lysosomes": "lysosome", "lyso": "lysosome",
}


@dataclass
class StructureCall:
    structure: str
    is_cme_machinery: bool
    route: str
    route_note: str
    morphology: str            # puncta | filaments | extended
    label_source: str          # archive label used (or "none")
    morphology_agrees: bool
    signature: dict

    def to_dict(self):
        return dataclasses.asdict(self)


def morphology_signature(frame):
    """Compact morphology descriptor: are the bright features point-like
    (puncta), elongated (filaments), or extended (organelles/tubules)?"""
    f = frame.astype(float)
    f = np.clip(f, 0, None)
    enh = ndi.gaussian_filter(f, 1.0) - ndi.gaussian_filter(f, 6.0)
    mask = enh > enh.std() * 5
    lbl, n = ndi.label(mask)
    if n == 0:
        return dict(n_objects=0, median_elongation=np.nan,
                    median_area_px=np.nan, morphology="empty")
    elong, areas = [], []
    for i, sl in enumerate(ndi.find_objects(lbl), start=1):
        m = lbl[sl] == i
        a = int(m.sum())
        if a < 3:
            continue
        ys, xs = np.nonzero(m)
        # principal-axis ratio via covariance eigenvalues -> elongation
        cov = np.cov(np.vstack([ys - ys.mean(), xs - xs.mean()]))
        ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
        el = float(np.sqrt(ev[0] / ev[1])) if ev[1] > 1e-6 else 10.0
        elong.append(el); areas.append(a)
    if not areas:
        return dict(n_objects=0, median_elongation=np.nan,
                    median_area_px=np.nan, morphology="empty")
    med_el = float(np.median(elong)); med_area = float(np.median(areas))
    # decision: filaments are elongated (median principal-axis ratio >= ~1.6;
    # empirically CCP puncta ~1.25, F-actin/MT segments ~2.0 in BioTISR SIM_gt);
    # organelles are large-area; else point-like puncta.
    if med_el >= 1.6:
        morph = "filaments"
    elif med_area >= 80:
        morph = "extended"
    else:
        morph = "puncta"
    return dict(n_objects=len(areas), median_elongation=round(med_el, 2),
                median_area_px=round(med_area, 1), morphology=morph)


# morphology consistent with each structure
_MORPH_OK = {
    "clathrin_coated_pit": {"puncta"},
    "f_actin": {"filaments"},
    "microtubule": {"filaments"},
    "mitochondria": {"extended", "filaments"},
    "lysosome": {"puncta", "extended"},
}


def classify_structure(frame=None, label=None):
    """Identify structure from an archive label and/or an image frame."""
    key, src = None, "none"
    if label:
        key = LABEL_MAP.get(label.strip().lower())
        if key:
            src = label
    sig = morphology_signature(frame) if frame is not None else dict(morphology="unknown")
    morph = sig.get("morphology", "unknown")
    if key is None:
        # no usable label -> guess from morphology (coarse)
        key = {"puncta": "clathrin_coated_pit", "filaments": "f_actin",
               "extended": "mitochondria"}.get(morph, "clathrin_coated_pit")
    is_mach, route, note = STRUCTURE_ROUTES[key]
    agrees = morph in _MORPH_OK.get(key, set()) if morph not in ("unknown", "empty") else True
    return StructureCall(structure=key, is_cme_machinery=is_mach, route=route,
                         route_note=note, morphology=morph, label_source=src,
                         morphology_agrees=bool(agrees), signature=sig)


def assert_ccs_applicable(call):
    """Guard: only clathrin-coated pits may enter the CCS spherical-cap inverse."""
    if call.route != "ccs_inverse":
        raise PermissionError(
            f"REFUSED: structure '{call.structure}' routes to '{call.route}' "
            f"-- the CCS spherical-cap inverse does not describe its physics. "
            f"{call.route_note}")
    return True


if __name__ == "__main__":
    import glob, os
    from ingest_biotisr_sim import read_mrc
    for mp in sorted(glob.glob("cache/biotisr/**/*_SIM_gt.mrc", recursive=True)):
        vol = read_mrc(mp)
        # label from parent dir name if it encodes structure; here cache/ccp -> CCP
        lbl = "CCPs" if "ccp" in mp.lower() else None
        call = classify_structure(frame=np.clip(vol[vol.shape[0] // 2], 0, None), label=lbl)
        print(f"{os.path.basename(mp):28s} -> {call.structure:20s} "
              f"morph={call.morphology:9s} agrees={call.morphology_agrees} "
              f"route={call.route}")
