"""
Dual-channel co-recruitment extractor for cmeAnalysis cohort output (2020
epsin osmotic dataset, observable #1 refined).

The .mat files store `res.cohorts.A` = a (2 channel x 6 lifetime-cohort) array
of mean amplitude trajectories: master **clathrin (RFP)** and slave **epsin
(EGFP)**, ~17 timepoints per cohort, framerate 2 s. This is the dual-channel
co-recruitment signal -- how much epsin is recruited relative to clathrin as a
function of pit lifetime and osmotic (membrane-tension) condition.

HONEST SCOPE. This is conventional TIRF *intensity*, not curvature: single CCPs
are diffraction-limited puncta, so amplitude reads adaptor/coat recruitment
(who is present, how much, when) -- NOT membrane shape. It therefore feeds the
mechanism/ordering + orchestration side (which actor when), and cross-checks the
tension story, but does NOT feed the curvature inverse. Force is not claimed.

The robust cross-condition observable is the **epsin:clathrin peak-amplitude
ratio within each condition** -- it is self-normalising (same cells/imaging per
file), so it cancels the per-session intensity scale that makes raw amplitudes
non-comparable across files. Per-cohort baseline-subtracted shapes are noisy
(some cohorts show unstable init fractions); we report the median over cohorts,
not individual cohorts, as the defensible quantity.

Raw per-track ProcessedTracks.mat are NOT available (they lived on the authors'
original acquisition drive); this module works from the shipped cohort averages.
"""
import numpy as np
import scipy.io as sio

CLATHRIN_CH = 0   # RFP master (canonical lifetime-rising bell)
EPSIN_CH = 1      # EGFP slave


def load_cohorts(path):
    """Return (markers, bounds, t_list, A) where A is a (2, nCohort) object
    array of per-channel mean amplitude trajectories."""
    m = sio.loadmat(path, struct_as_record=False, squeeze_me=True)
    coh = m["res"].cohorts
    markers = list(np.atleast_1d(np.atleast_1d(m["data"]).ravel()[0].markers))
    bounds = np.array(coh.bounds)
    ncoh = len(bounds) - 1
    t = [np.atleast_1d(x).astype(float)
         for x in np.atleast_1d(np.array(coh.t, dtype=object))]
    Araw = np.array(coh.A, dtype=object)
    A = np.empty((2, ncoh), dtype=object)
    for ci in range(2):
        row = np.atleast_1d(np.atleast_1d(Araw)[ci])
        for k in range(ncoh):
            A[ci, k] = np.atleast_1d(row.ravel()[k]).astype(float)
    return markers, bounds, t, A


def cohort_corecruitment(A, t, k):
    """Per-cohort clathrin/epsin co-recruitment metrics."""
    cla = np.asarray(A[CLATHRIN_CH, k], float)
    eps = np.asarray(A[EPSIN_CH, k], float)
    tt = np.asarray(t[k], float)
    ci, ei = int(np.nanargmax(cla)), int(np.nanargmax(eps))
    cpk, epk = float(np.nanmax(cla)), float(np.nanmax(eps))
    return dict(clath_peak=cpk, epsin_peak=epk,
                epsin_clath_ratio=(epk / cpk if cpk > 0 else np.nan),
                peak_lag_s=float(tt[ei] - tt[ci]))


def condition_summary(path):
    """Robust median epsin:clathrin ratio (and clathrin peak) over cohorts."""
    markers, bounds, t, A = load_cohorts(path)
    ncoh = A.shape[1]
    cohorts = []
    for k in range(ncoh):
        c = cohort_corecruitment(A, t, k)
        c["cohort_s"] = f"{bounds[k]}-{bounds[k+1]}"
        cohorts.append(c)
    ratios = np.array([c["epsin_clath_ratio"] for c in cohorts])
    return dict(
        markers=markers,
        median_epsin_clath=float(np.nanmedian(ratios)),
        median_clath_peak=float(np.nanmedian([c["clath_peak"] for c in cohorts])),
        cohorts=cohorts)


def tension_response(hypo_path, hyper_path):
    """Change in median epsin:clathrin ratio from low (hypo) to high (hyper)
    tension. A negative delta means tension suppresses epsin recruitment."""
    lo = condition_summary(hypo_path)["median_epsin_clath"]
    hi = condition_summary(hyper_path)["median_epsin_clath"]
    return dict(hypo=lo, hyper=hi, delta=hi - lo)
