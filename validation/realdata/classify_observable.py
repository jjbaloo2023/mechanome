"""
Observable classifier and router.

The project's central data-reality discipline: single clathrin-coated pits are
diffraction-limited, so curvature is not readable from ordinary fluorescence.
The legacy tags describe three measurement families:

  #1 intensity/lifetime (any TIRF)      -> coat-assembly proxy, NOT curvature
                                            -> front-end / tracking validation only
  #2 epi-TIRF ratio                     -> axial-depth proxy
  #3 TIRF-SIM / super-res               -> projected geometry

Tags do not establish calibration, three-dimensional geometry, or force
identifiability. This descriptive router grants no force permission. A future
authorization path needs independently reviewed, model-specific calibration
evidence; caller-supplied provenance flags cannot provide that authorization.
"""
from dataclasses import dataclass


OBSERVABLES = {
    "1_intensity": dict(
        richness=1, reads="coat-assembly intensity proxy",
        force_inference=False,
        route="front-end / tracking validation only"),
    "2_epitirf_depth": dict(
        richness=2, reads="axial-depth proxy (epi-TIRF ratio)",
        force_inference=False,
        route="measurement QA / depth calibration review"),
    "3_superres_curvature": dict(
        richness=3, reads="projected geometry (SIM / super-res)",
        force_inference=False,
        route="measurement QA / geometry calibration review"),
}


@dataclass
class Routing:
    observable: str
    force_inference_allowed: bool
    route: str
    reason: str


def classify(dataset):
    """Tag any ingested dataset (IntensityCohort / PairedField / trace) by its
    `observable` attribute and return the routing decision."""
    obs = getattr(dataset, "observable", None)
    if obs is None and isinstance(dataset, dict):
        obs = dataset.get("observable")
    if obs not in OBSERVABLES:
        raise ValueError(f"unknown or missing observable tag: {obs!r}")
    spec = OBSERVABLES[obs]
    reason = (f"observable #{spec['richness']} reads {spec['reads']}; "
              "a descriptive tag does not establish calibrated geometry or "
              "model-specific force identifiability; force inference refused")
    return Routing(observable=obs, force_inference_allowed=False,
                   route=spec["route"], reason=reason)


def assert_force_permitted(dataset):
    """Reject tag-only force authorization for every measurement family."""
    r = classify(dataset)
    if not r.force_inference_allowed:
        raise PermissionError(
            f"REFUSED: {r.observable} has no reviewed force authorization. {r.reason}")
    return r


if __name__ == "__main__":
    import os
    from validation.realdata.ingest_cme_mat import ingest_cme_mat
    from validation.realdata.ingest_ome_tiff import ingest_paired_field, find_tirf_epi_pairs

    base = ("/root/projects/Epsin paper comm bio 2020/final figure/"
            "data availability/Figure 2/Osmotic shock")
    coh = ingest_cme_mat(os.path.join(base, "iso.mat"), condition="iso")
    r1 = classify(coh)
    print(f"2020 osmotic iso  -> {r1.observable}: force_ok={r1.force_inference_allowed}")
    print(f"   route: {r1.route}")

    cond = ("/root/projects/IAV paper membranes 2022/IAV and NP data/"
            "080421 epsin EGFP mchc clc IAV/epsin/IAV")
    cell, tp, ep = find_tirf_epi_pairs(cond)[0]
    pf = ingest_paired_field(tp, ep, cell_id=cell, condition="IAV")
    r2 = classify(pf)
    print(f"IAV epi-TIRF {cell} -> {r2.observable}: force_ok={r2.force_inference_allowed}")
    print(f"   route: {r2.route}")

    # demonstrate the refusal
    try:
        assert_force_permitted(coh)
    except PermissionError as e:
        print(f"\nrefusal works: {str(e)[:80]}...")
