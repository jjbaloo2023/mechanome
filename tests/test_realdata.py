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


def test_epitirf_ratio_monotone_and_calibrated():
    """The epi-TIRF depth model: ratio starts near 1 (flat coat) and drops
    monotonically as the pit invaginates, and the drop scales with penetration
    depth. This is the physics that makes observable #2 dynamic AND
    resolution-compatible."""
    import numpy as _np
    from validation.realdata.epitirf_depth_model import (
        cap_geometry, tirf_epi_ratio_from_psi)
    A = _np.pi * 60 ** 2
    psi, R, depth = cap_geometry(0.02, 0.02, 40.0, A)
    ratio = tirf_epi_ratio_from_psi(psi, R)
    _check(ratio[0] > 0.98, f"flat coat ratio should be ~1, got {ratio[0]:.3f}")
    _check(ratio[-1] < ratio[0], "ratio must drop as the pit invaginates")
    _check(_np.all(depth >= -1e-6), "invagination depth must be non-negative")
    # shallower penetration depth -> larger relative drop (stronger axial contrast)
    r_shallow = tirf_epi_ratio_from_psi(psi, R, d_pen=60.0)
    _check(r_shallow[-1] < ratio[-1],
           "shallower d_pen must yield a larger ratio drop")


def test_epitirf_force_nonrailed():
    """A force recovered from a clean ratio trajectory must track truth and NOT
    rail against the prior ceiling (the improvement over the SIM footprint proxy).
    Formal identification is not required -- force/tension degeneracy is
    structural -- but the estimate must be bounded and centered."""
    import numpy as _np
    from validation.realdata.epitirf_depth_model import predict_ratio, run_ratio_inverse
    from curvo import inverse as _inv
    A = _np.pi * 60 ** 2
    params = _inv.DEFAULT_PARAMS
    ratio = predict_ratio([0.02, 40.0, 0.02], params, A)
    res = run_ratio_inverse(ratio, _np.full_like(ratio, 0.006), A, params=params,
                            nlive=150, seed=0)
    af = _inv.identifiability(res["samples"], res["params"])["active_force_max"]
    _check(20 < af["median"] < 60, f"force median should be near truth 40, got {af['median']:.0f}")
    _check(not af["railed"], "force posterior must NOT be railed against the ceiling")


def test_star_calibration_matches_forward_model():
    """The epi-TIRF depth model reproduces STAR microscopy's published
    calibration (Nawara et al. 2022): applying STAR's own log-ratio*gamma
    map to the ratio our forward geometry predicts recovers the true mean coat
    height. Validates observable #2 against a real instrument calibration."""
    import numpy as _np
    from validation.realdata.epitirf_depth_model import (
        cap_geometry, star_dz_from_psi, STAR_D_488, STAR_D_647, STAR_GAMMA)
    # published constants (their bead calibration): sanity ranges
    _check(160 < STAR_D_488 < 175, f"d_488 should be ~167nm, got {STAR_D_488:.0f}")
    _check(210 < STAR_D_647 < 230, f"d_647 should be ~221nm, got {STAR_D_647:.0f}")
    _check(600 < STAR_GAMMA < 750, f"gamma should be ~679nm, got {STAR_GAMMA:.0f}")
    A = _np.pi * 60 ** 2
    psi, R, _ = cap_geometry(0.02, 0.02, 40.0, A)
    dz = star_dz_from_psi(psi, R)
    # true mean coat-surface height above the rim
    th = _np.linspace(0, 1, 128)[None, :] * psi[:, None]
    z = R[:, None] * (_np.cos(th) - _np.cos(psi)[:, None]); w = _np.sin(th)
    z_mean = _np.trapezoid(z * w, th, axis=1) / _np.trapezoid(w, th, axis=1)
    r = _np.corrcoef(dz, z_mean)[0, 1]
    slope = _np.polyfit(z_mean, dz, 1)[0]
    _check(r > 0.999, f"STAR dz must track true mean height, r={r:.4f}")
    _check(0.9 < slope < 1.1, f"STAR dz slope must be ~1, got {slope:.2f}")


def test_dual_cohort_tension_response_enth_specific():
    """Dual-channel extraction: WT epsin:clathrin recruitment ratio falls with
    membrane tension, and the response is abolished when the ENTH curvature
    domain is deleted. Both use the 2020 osmotic .mat files if present."""
    from validation.realdata.ingest_dual_cohorts import (
        condition_summary, tension_response, CLATHRIN_CH, EPSIN_CH)
    base = "/root/projects/Epsin paper comm bio 2020/final figure/data availability"
    wt_hypo = f"{base}/Figure 2/Osmotic shock/hypo.mat"
    wt_hyper = f"{base}/Figure 2/Osmotic shock/hyper.mat"
    de_hypo = f"{base}/Figure 3/epsin del ENTH/hypo.mat"
    de_hyper = f"{base}/Figure 3/epsin del ENTH/hyper.mat"
    if not all(os.path.exists(p) for p in (wt_hypo, wt_hyper, de_hypo, de_hyper)):
        print("SKIP test_dual_cohort_tension_response_enth_specific (2020 .mat absent)"); return
    _check(CLATHRIN_CH == 0 and EPSIN_CH == 1, "channel roles: RFP=clathrin, EGFP=epsin")
    wt = tension_response(wt_hypo, wt_hyper)
    de = tension_response(de_hypo, de_hyper)
    _check(wt["delta"] < -0.15, f"WT tension response should be a clear drop, got {wt['delta']:.2f}")
    _check(abs(de["delta"]) < 0.15, f"del ENTH response should be ~abolished, got {de['delta']:.2f}")
    _check(wt["delta"] < de["delta"], "WT must drop more than del ENTH (domain-specific)")
    # sanity: a condition summary yields a positive, finite ratio
    s = condition_summary(wt_hypo)
    _check(0 < s["median_epsin_clath"] < 5, "median epsin:clathrin ratio must be finite/positive")


def test_picalm_not_productive_alone_but_in_full_assembly():
    """Orchestration test case: PICALM (ANTH) cannot cross the Omega/scission
    stage on its own, coat and actin alone are insufficient, and the pit
    becomes productive only in the full assembly (coat + actin + crowding)."""
    from validation.realdata.picalm_orchestration import run_ladder, PICALM_P_CROSS_OMEGA
    _check(PICALM_P_CROSS_OMEGA < 0.05, "PICALM autonomous P(cross Omega) must be small")
    ladder = dict(run_ladder())
    _check(not ladder["PICALM alone"]["productive"], "PICALM alone must NOT be productive")
    _check(not ladder["+ clathrin coat"]["productive"], "coat alone must not rescue")
    _check(not ladder["+ actin 40 pN"]["productive"], "coat+actin40 must still be sub-threshold")
    # crowding at fixed 40 pN actin is NOT sufficient (isolates the confound)
    _check(not ladder["+ crowding (actin held 40)"]["productive"],
           "crowding alone (actin held 40) must not reach Omega")
    full = ladder["+ actin raised to 80 pN"]
    _check(full["productive"], "full assembly (crowding + actin 80) must reach Omega")
    # monotone rise in achieved curvature along the ladder
    H = [o["achieved_mean_curvature_inv_nm"] for _, o in run_ladder()]
    _check(all(H[i] < H[i + 1] for i in range(len(H) - 1)),
           f"achieved curvature must rise monotonically along the assembly ladder, got {H}")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print(f"ok  {fn.__name__}")
    print(f"\n{passed}/{len(fns)} real-data tests passed")
