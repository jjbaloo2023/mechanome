"""
tether_sted.py — curvo inverse validation against force-paired real-membrane data.

Dataset (T1, force-paired gold standard):
    Roy, Steinkuehler, Zhao, Lipowsky & Dimova (2020)
    "Mechanical Tension of Biomembranes Can Be Measured by Super Resolution
     (STED) Microscopy of Force-Induced Nanotubes"
    Nano Letters 20:3185-3191.  doi:10.1021/acs.nanolett.9b05232

Why this dataset: a POPC giant unilamellar vesicle (symmetric bilayer,
spontaneous curvature ~0, so curvo's forward map applies exactly) is pulled into
a membrane nanotube. The tube RADIUS is measured directly by super-resolution
STED; the membrane TENSION is set independently by micropipette aspiration
(15-140 uN/m); and the bending rigidity kappa is measured two independent ways
(23+/-2 kBT by thermal fluctuation analysis, 23+/-5 kBT by tube-pulling). The
tether force, tube radius and tension are linked by the Helfrich closed forms

    R = sqrt(kappa / (2 sigma)),     f = 2*pi*sqrt(2 sigma kappa)

This is exactly curvo's forward map, which makes it the cleanest real test of the
inverse: feed curvo the STED radius (with realistic noise) + kappa as a prior,
infer the tension, propagate to the holding force, and check the recovered force
against the independent aspiration-tension ground truth.

SCOPE: this validates the forward map + Bayesian inverse machinery on the
TUBE/tether geometry (the helfrich_tube evaluator). It is distinct from the CCS
spherical-cap analyze() pipeline (validated separately in recovery.py). The
tether system has no wedge/actin actors -- it is the pure force<->geometry
inference check on real measured forces.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

# import robustly whether run from the repo root or elsewhere on PYTHONPATH
from curvo import evaluator_tier0 as ev


# --- paper ground-truth constants -------------------------------------------
DOI = "10.1021/acs.nanolett.9b05232"
CITATION = ("Roy, Steinkuehler, Zhao, Lipowsky, Dimova (2020) Nano Lett. "
            "20:3185, doi:10.1021/acs.nanolett.9b05232")
KAPPA_KBT = 23.0            # POPC bending rigidity (both methods agree ~23 kBT)
KAPPA_PRIOR_SD = 5.0        # tube-pulling method uncertainty (23 +/- 5 kBT)
TENSION_RANGE_uN_m = (15.0, 140.0)
STED_RADIUS_SIGMA_NM = 5.5  # half the reported +/-11 nm diameter precision
REPORTED_TUBE_DIAMETER_NM = 72.0


def _uN_m_to_kBT_nm2(tension_uN_m):
    """Convert membrane tension in uN/m to kBT/nm^2 (curvo's internal unit)."""
    sigma_pN_nm = tension_uN_m * 1e-3          # 1 uN/m = 1e-3 pN/nm
    return sigma_pN_nm / ev.kBT_zJ             # kBT/nm^2


def tube_forward(tension_uN_m, kappa_kBT=KAPPA_KBT):
    """Closed-form tube radius (nm) and tether force (pN) for a given tension."""
    sigma = _uN_m_to_kBT_nm2(tension_uN_m)
    o = ev.helfrich_tube(kappa_kBT=kappa_kBT, sigma_kBT_nm2=sigma)
    return o["R_equilibrium_nm"], o["tether_force_closed_form_pN"]


# --- Bayesian tube inversion -------------------------------------------------
def _grids(n_sigma=400, n_kappa=300):
    sig = np.geomspace(0.001, 0.06, n_sigma)   # kBT/nm^2
    kap = np.linspace(8.0, 45.0, n_kappa)      # kBT
    SIG, KAP = np.meshgrid(sig, kap, indexing="ij")
    R_model = np.sqrt(KAP / (2.0 * SIG))                       # nm
    f_model = 2 * np.pi * np.sqrt(2 * SIG * KAP) * ev.kBT_zJ   # pN
    kap_logprior = stats.norm(KAPPA_KBT, KAPPA_PRIOR_SD).logpdf(KAP)
    return SIG, KAP, R_model, f_model, kap_logprior


def invert_radius(R_meas, sigma_R=STED_RADIUS_SIGMA_NM, grids=None):
    """Infer the tether-force posterior from one measured tube radius.

    Prior: kappa ~ Normal(23, 5) kBT (the paper's tube-pulling estimate);
           sigma ~ log-uniform over a plausible tension range.
    Likelihood: R_meas ~ Normal(R_model(sigma, kappa), sigma_R).
    Returns median + 68% CI on force (pN) and the tension posterior median (uN/m).
    """
    SIG, KAP, R_model, f_model, kap_logprior = grids or _grids()
    logpost = -0.5 * ((R_meas - R_model) / sigma_R) ** 2 + kap_logprior
    logpost -= logpost.max()
    P = np.exp(logpost); P /= P.sum()

    fs = f_model.ravel(); order = np.argsort(fs)
    cdf = np.cumsum(P.ravel()[order])
    f_lo, f_med, f_hi = np.interp([0.16, 0.5, 0.84], cdf, fs[order])

    ss = SIG.ravel(); so = np.argsort(ss)
    cdfs = np.cumsum(P.ravel()[so])
    sig_med = np.interp(0.5, cdfs, ss[so]) * ev.kBT_zJ / 1e-3   # -> uN/m
    return dict(f_med=f_med, f_lo=f_lo, f_hi=f_hi, sigma_med_uN_m=sig_med)


def validate(tensions_uN_m=(20, 40, 72, 100, 130), n_noise=200, seed=0):
    """Full force-recovery calibration test across the paper's tension range.

    For each aspiration tension: closed-form gives the true radius + force; we
    add STED noise to the radius, invert for the force posterior, and measure
    68% CI coverage of the TRUE force and the recovery bias over n_noise draws.
    """
    rng = np.random.default_rng(seed)
    grids = _grids()
    rows = []
    for t in tensions_uN_m:
        R_true, f_true = tube_forward(t)
        hits, recs = 0, []
        for _ in range(n_noise):
            R_meas = R_true + rng.normal(0, STED_RADIUS_SIGMA_NM)
            out = invert_radius(R_meas, grids=grids)
            hits += (out["f_lo"] <= f_true <= out["f_hi"])
            recs.append(out["f_med"])
        rows.append(dict(
            tension_uN_m=float(t), R_true_nm=round(R_true, 1),
            f_true_pN=round(f_true, 2), f_rec_mean_pN=round(float(np.mean(recs)), 2),
            coverage68=round(hits / n_noise, 3),
            rel_bias=round(float((np.mean(recs) - f_true) / f_true), 4)))
    summary = dict(
        overall_coverage68=round(float(np.mean([r["coverage68"] for r in rows])), 3),
        nominal_coverage=0.68,
        mean_abs_rel_bias=round(float(np.mean([abs(r["rel_bias"]) for r in rows])), 4),
        n_noise_per_point=n_noise)
    return dict(citation=CITATION, doi=DOI, kappa_kBT=KAPPA_KBT,
                rows=rows, summary=summary)


if __name__ == "__main__":
    import json
    res = validate()
    for r in res["rows"]:
        print(f"Sigma={r['tension_uN_m']:3.0f} uN/m: f_true={r['f_true_pN']:5.1f} pN "
              f"f_rec={r['f_rec_mean_pN']:5.1f}  cov68={r['coverage68']:.2f}  "
              f"bias={r['rel_bias']:+.1%}")
    print("\nsummary:", json.dumps(res["summary"]))
