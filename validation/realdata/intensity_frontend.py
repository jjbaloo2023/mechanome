"""
Observable-#1 front-end: 2020 osmotic-shock intensity cohorts.

This routes the cmeAnalysis intensity cohorts (observable #1) through a front-end
validation and a TENSION CROSS-CHECK. It does NOT infer force -- intensity is a
coat-assembly proxy, and the classifier refuses force inference on it. What it
CAN do is test whether curvo ingests the real cohorts faithfully and whether the
tension-dependence direction matches the 2020 paper's finding:

  Membrane tension impedes CCP maturation. Under hypertonic shock (HIGH tension)
  relative to isotonic and hypotonic (LOW tension), productive pits should be
  fewer and more structures abortive.

Tension order (low -> high): hypo (hypotonic, cell swells / membrane relaxes)
                             iso  (isotonic, baseline)
                             hyper (hypertonic, cell shrinks / membrane tenses)
"""
import os
import json
import numpy as np
import scipy.io as sio

from validation.realdata.ingest_cme_mat import ingest_cme_mat
from validation.realdata.classify_observable import classify

OSMOTIC_BASE = ("/root/projects/Epsin paper comm bio 2020/final figure/"
                "data availability/Figure 2/Osmotic shock")
TENSION_ORDER = ["hypo", "iso", "hyper"]     # low -> high membrane tension


def lifetime_features(mat_path):
    """Maturation features from cmeAnalysis lftRes: productive/abortive fractions,
    nucleation density, mean CCP lifetime."""
    m = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    lft = m["res"].lftRes
    t = np.ravel(lft.t).astype(float)
    out = dict(
        pct_productive=float(np.ravel(lft.pctCCP).mean()),   # bona-fide CCP fraction
        pct_abortive=float(np.ravel(lft.pctCS).mean()),      # short-lived fraction
        init_density=float(np.ravel(lft.initDensityCCP).mean()),
    )
    h = np.ravel(lft.meanLftHistCCP)
    out["mean_ccp_lifetime_s"] = float(np.sum(t * h) / np.sum(h)) if len(h) == len(t) else float("nan")
    return out


def cohort_peak(cohort, channel="RFP"):
    """Peak intensity of the longest-lifetime (most mature) cohort, one channel."""
    ch = cohort.channels.index(channel) if channel in cohort.channels else 0
    _, A, _, _ = cohort.bin_trajectory(cohort.n_bins - 1, ch)
    return float(np.max(A))


def tension_crosscheck(base=OSMOTIC_BASE):
    """Run the front-end + tension cross-check across iso/hypo/hyper."""
    rows = {}
    for cond in TENSION_ORDER:
        path = os.path.join(base, f"{cond}.mat")
        coh = ingest_cme_mat(path, condition=cond)
        assert classify(coh).observable == "1_intensity"      # front-end only
        feats = lifetime_features(path)
        feats["clathrin_peak"] = cohort_peak(coh, "RFP")
        feats["n_cells"] = coh.n_cells
        rows[cond] = feats

    # direction checks: does HIGH tension (hyper) impede maturation vs LOW (hypo)?
    checks = dict(
        productive_falls_with_tension=bool(rows["hyper"]["pct_productive"]
                                           < rows["hypo"]["pct_productive"]),
        abortive_rises_with_tension=bool(rows["hyper"]["pct_abortive"]
                                         > rows["hypo"]["pct_abortive"]),
        clathrin_peak_falls_at_high_tension=bool(rows["hyper"]["clathrin_peak"]
                                                 < rows["iso"]["clathrin_peak"]),
    )
    verdict = ("consistent with the 2020 finding (tension impedes maturation)"
               if sum(checks.values()) >= 2 else "inconsistent — re-examine")
    return dict(conditions=rows, tension_order=TENSION_ORDER,
                direction_checks=checks, verdict=verdict,
                observable="1_intensity",
                scope="coat-assembly proxy; NO force inference (classifier refuses #1)")


if __name__ == "__main__":
    res = tension_crosscheck()
    for c in TENSION_ORDER:
        r = res["conditions"][c]
        print(f"{c:5s}: productive={r['pct_productive']:.3f} abortive={r['pct_abortive']:.3f} "
              f"initDens={r['init_density']:.0f} meanLft={r['mean_ccp_lifetime_s']:.1f}s "
              f"CLCpeak={r['clathrin_peak']:.0f}")
    print("checks:", res["direction_checks"])
    print("verdict:", res["verdict"])
    json.dump(res, open("outputs/tension_crosscheck.json", "w"), indent=2)
