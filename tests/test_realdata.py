"""
Contract tests for the real-data ingestion + observable-classifier pipeline.

These tests guard the data-boundary discipline: ingestion round-trips real files
with provenance, the classifier tags observables correctly, and force inference
is REFUSED on intensity-only data (observable #1). Tests that need the raw files
under /root/projects or the BioTISR cache skip cleanly when those are absent, so
the suite passes in a clean clone without the (never-committed) raw imaging.
"""
import os
import numpy as np

from validation.realdata.classify_observable import (
    classify, assert_force_permitted, OBSERVABLES)

EPSIN_OSMOTIC = ("/root/projects/Epsin paper comm bio 2020/final figure/"
                 "data availability/Figure 2/Osmotic shock")
IAV_COND = ("/root/projects/IAV paper membranes 2022/IAV and NP data/"
            "080421 epsin EGFP mchc clc IAV/epsin/IAV")
BIOTISR = "cache/biotisr/ccp/Cell_001_SIM_gt.mrc"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ------------------------------------------------- classifier (no files) ----

def test_classifier_refuses_intensity():
    """Observable #1 must be refused for force inference."""
    class Fake: observable = "1_intensity"
    r = classify(Fake())
    _check(r.force_inference_allowed is False, "intensity #1 must refuse force")
    raised = False
    try:
        assert_force_permitted(Fake())
    except PermissionError:
        raised = True
    _check(raised, "assert_force_permitted must raise on #1")


def test_classifier_permits_curvature():
    """Observables #2 and #3 must permit force inference."""
    for obs in ("2_epitirf_depth", "3_superres_curvature"):
        class Fake: pass
        f = Fake(); f.observable = obs
        _check(classify(f).force_inference_allowed is True, f"{obs} must permit force")


def test_classifier_rejects_unknown():
    class Fake: observable = "bogus"
    raised = False
    try:
        classify(Fake())
    except ValueError:
        raised = True
    _check(raised, "unknown observable must raise")


# ------------------------------------------------- .mat ingestion ------------

def test_cme_mat_roundtrip():
    if not os.path.isdir(EPSIN_OSMOTIC):
        print("SKIP test_cme_mat_roundtrip (raw data absent)"); return
    from validation.realdata.ingest_cme_mat import ingest_cme_mat
    c = ingest_cme_mat(os.path.join(EPSIN_OSMOTIC, "iso.mat"), condition="iso")
    _check(c.observable == "1_intensity", "cohort must be observable #1")
    _check(c.n_bins == 6, f"expected 6 lifetime bins, got {c.n_bins}")
    _check(len(c.channels) == 2, "expected 2 channels")
    _check("source_path" in c.provenance and "retrieval_date" in c.provenance,
           "provenance must record source + retrieval date")
    t, A, lo, hi = c.bin_trajectory(3, 0)
    _check(len(t) == len(A) == len(lo) == len(hi), "trajectory arrays must align")
    _check(np.all(hi >= lo), "SEM envelope must be ordered")


def test_cme_mat_refused_for_force():
    if not os.path.isdir(EPSIN_OSMOTIC):
        print("SKIP test_cme_mat_refused_for_force (raw data absent)"); return
    from validation.realdata.ingest_cme_mat import ingest_cme_mat
    c = ingest_cme_mat(os.path.join(EPSIN_OSMOTIC, "iso.mat"), condition="iso")
    raised = False
    try:
        assert_force_permitted(c)
    except PermissionError:
        raised = True
    _check(raised, "intensity cohort must be refused for force inference")


# ------------------------------------------------- OME-TIFF ingestion --------

def test_ome_tiff_pairing():
    if not os.path.isdir(IAV_COND):
        print("SKIP test_ome_tiff_pairing (raw data absent)"); return
    from validation.realdata.ingest_ome_tiff import find_tirf_epi_pairs, ingest_paired_field
    pairs = find_tirf_epi_pairs(IAV_COND)
    _check(len(pairs) >= 1, "expected at least one tirf/epi pair")
    cell, tp, ep = pairs[0]
    pf = ingest_paired_field(tp, ep, cell_id=cell, condition="IAV")
    _check(pf.observable == "2_epitirf_depth", "paired field must be observable #2")
    _check(pf.n_timepoints == 1, "IAV data is single-timepoint (recorded honestly)")
    _check("clathrin" in pf.channel_roles, "clathrin role must be resolved")
    _check("note" in pf.provenance, "provenance must record the snapshot note")


# ------------------------------------------------- BioTISR SIM extraction ----

def test_biotisr_curvature_extraction():
    if not os.path.exists(BIOTISR):
        print("SKIP test_biotisr_curvature_extraction (SIM cache absent)"); return
    from validation.realdata.ingest_biotisr_sim import extract_curvature_traces
    traces = extract_curvature_traces(BIOTISR, cell_id="Cell_001", min_len=6)
    _check(len(traces) > 10, "expected many tracked CCPs")
    t = traces[0]
    _check(t.observable == "3_superres_curvature", "SIM trace must be observable #3")
    _check(len(t.t_s) == len(t.R_proj_nm) == len(t.H_proxy_inv_nm),
           "trace arrays must align")
    _check(all(h > 0 for h in t.H_proxy_inv_nm), "H proxy must be positive")
    _check("doi" in t.provenance and "assumption" in t.provenance,
           "provenance must record DOI + the proxy assumption")


# ------------------------------------------------- structure routing --------

def test_structure_routing_refuses_noncoated():
    """Only clathrin-coated pits may enter the CCS spherical-cap inverse."""
    from validation.realdata.classify_structure import (
        classify_structure, assert_ccs_applicable, STRUCTURE_ROUTES)
    # CCP routes to the inverse
    ccp = classify_structure(frame=None, label="CCPs")
    _check(ccp.route == "ccs_inverse", "CCP must route to ccs_inverse")
    _check(assert_ccs_applicable(ccp) is True, "CCP must pass the CCS guard")
    # F-actin and non-endocytic structures must be refused
    for lbl in ("F-actin", "Microtubules", "Mitochondria"):
        call = classify_structure(frame=None, label=lbl)
        _check(call.route != "ccs_inverse", f"{lbl} must NOT route to ccs_inverse")
        raised = False
        try:
            assert_ccs_applicable(call)
        except PermissionError:
            raised = True
        _check(raised, f"CCS guard must refuse {lbl}")


def test_structure_morphology_discriminates():
    """Morphology signature separates puncta (CCP) from filaments (actin)."""
    import numpy as _np
    from validation.realdata.classify_structure import classify_structure
    from validation.realdata.ingest_biotisr_sim import read_mrc
    ccp = "cache/biotisr/ccp/Cell_001_SIM_gt.mrc"
    fac = "cache/biotisr/factin/Factin_Cell_001_SIM_gt.mrc"
    if not (os.path.exists(ccp) and os.path.exists(fac)):
        print("SKIP test_structure_morphology_discriminates (SIM cache absent)"); return
    c_ccp = classify_structure(frame=_np.clip(read_mrc(ccp)[10], 0, None), label=None)
    c_fac = classify_structure(frame=_np.clip(read_mrc(fac)[10], 0, None), label=None)
    _check(c_ccp.morphology == "puncta", f"CCP should read as puncta, got {c_ccp.morphology}")
    _check(c_fac.morphology == "filaments", f"actin should read as filaments, got {c_fac.morphology}")


def test_resolution_regime_biotisr_out_of_band():
    """The validated cap-fit extractor must NOT report reliable frames at
    BioTISR's acquisition resolution (~31 nm/px, PSF sigma ~55 nm): the
    resolvability band is empty there, so curvo does not silently trust it.
    Guards the measured finding that BioTISR is outside the validated envelope."""
    from validation.perception_benchmark import recover_one
    # validated control returns frames; BioTISR-scale returns none
    core = recover_one(c_eff_max=0.06, psf_sigma_nm=18, nm_per_px=2.0,
                       field_px=128, n_rep=2, n_boot=6, seed0=0)
    _check(core is not None and core["n_frames"] > 0,
           "validated core must yield resolvable frames")
    bio = recover_one(c_eff_max=0.06, psf_sigma_nm=55, nm_per_px=31.3,
                      field_px=48, n_rep=2, n_boot=6, seed0=0)
    _check(bio is None or bio["n_frames"] == 0,
           "BioTISR-scale must yield ZERO resolvable frames (out of validated band)")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print(f"ok  {fn.__name__}")
    print(f"\n{passed}/{len(fns)} real-data tests passed")
