"""Exploratory curve scores for static, jointly fitted SMLM cap outputs.

Legacy curve names and numerical formulas are retained for reproducibility.
Closing angle is not time, fitted scatter is not deposited measurement error,
and cap-derived area/edge scores are not independent held-out evidence.
Explicit opt-in enables conditional numerical diagnostics, never a decisive
mechanism verdict. Historical output files are not rewritten by this module.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

ROLLING_WINDOW = 82          # sites; matches Mund et al. 2023 rolling median
DECISIVE_LNB = 2.5           # legacy diagnostic threshold; no mechanism permission
# uniform priors: preferred curvature H0 (nm^-1), initial rate gamma, scatter s
PRIORS = dict(H0=(0.004, 0.030), gamma=(0.0, 0.05), scatter=(5e-4, 1e-2))


def _require_exploratory(allow_exploratory):
    if allow_exploratory is not True:
        raise ValueError(
            "Static cap outputs lack a calibrated mechanism likelihood; "
            "set allow_exploratory=True only for conditional curve diagnostics."
        )


def H_helfrich(theta_deg, H0, gamma):
    """Non-cooperative linear relaxation toward preferred curvature H0."""
    th = np.radians(np.asarray(theta_deg, float))
    return H0 * (1.0 - np.exp(-gamma * th / H0))


def H_coopcm(theta_deg, H0, gamma):
    """Cooperative Curvature Model (quadratic positive feedback; Eq. 3)."""
    th = np.radians(np.asarray(theta_deg, float))
    return H0 * np.tanh(gamma * th / H0)


MODELS = {"helfrich_linear": H_helfrich, "coopcm": H_coopcm}


@dataclass
class MechanismVerdict:
    cell_line: str
    n_sites: int
    logz: dict
    lnB_coopcm_vs_helfrich: float
    favored: str
    decisive: bool
    verdict: str                  # human-readable, honest
    params: dict
    provenance: dict = field(default_factory=dict)

    def to_json(self, path):
        import dataclasses
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=float)
        return path


def rolling_median(theta, H, window=ROLLING_WINDOW, stride=20):
    """Rolling median of curvature over closing angle (Mund et al. 2023 method)."""
    o = np.argsort(theta); th_s = np.asarray(theta)[o]; H_s = np.asarray(H)[o]
    n = len(H_s); xs, ys = [], []
    for i in range(0, n, stride):
        lo = max(0, i - window // 2); hi = min(n, i + window // 2)
        if hi - lo < window // 2:
            continue
        xs.append(float(np.median(th_s[lo:hi]))); ys.append(float(np.median(H_s[lo:hi])))
    return np.array(xs), np.array(ys)


def _prior_transform(u):
    out = np.empty(3)
    for k, i in (("H0", 0), ("gamma", 1), ("scatter", 2)):
        lo, hi = PRIORS[k]; out[i] = lo + u[i] * (hi - lo)
    return out


def _fit(fn, theta, H, nlive=400, seed=0):
    from dynesty import NestedSampler
    from dynesty.utils import resample_equal
    theta = np.asarray(theta, float); H = np.asarray(H, float)

    def loglike(p):
        H0, gamma, s = p
        r = (fn(theta, H0, gamma) - H) / s
        return float(-0.5 * np.sum(r * r) - len(H) * np.log(s * np.sqrt(2 * np.pi)))

    rng = np.random.default_rng(seed)
    smp = NestedSampler(loglike, _prior_transform, 3, nlive=nlive, rstate=rng)
    smp.run_nested(print_progress=False, dlogz=0.1, maxcall=800_000)
    res = smp.results
    eq = resample_equal(res.samples, np.exp(res.logwt - res.logz[-1]))
    return float(res.logz[-1]), dict(H0=float(np.median(eq[:, 0])),
                                     gamma=float(np.median(eq[:, 1])),
                                     scatter=float(np.median(eq[:, 2])))


def discriminate(gs_cellline, nlive=400, seed=0, decisive_lnB=DECISIVE_LNB, *,
                 allow_exploratory=False):
    """Return conditional curve-score diagnostics after explicit opt-in."""
    _require_exploratory(allow_exploratory)
    theta = gs_cellline.arr("theta_deg"); H = gs_cellline.arr("H_inv_nm")
    xr, yr = rolling_median(theta, H)
    logz, params = {}, {}
    for name, fn in MODELS.items():
        lz, pr = _fit(fn, xr, yr, nlive=nlive, seed=seed)
        logz[name] = lz; params[name] = pr
    lnB = logz["coopcm"] - logz["helfrich_linear"]
    threshold_exceeded = bool(abs(lnB) > decisive_lnB)
    favored = "coopcm" if lnB > 0 else "helfrich_linear"
    verdict = (
        f"Exploratory curve score prefers {favored} (lnB={lnB:+.1f}); "
        "the rolling-median likelihood is uncalibrated and does not identify a mechanism."
    )
    prov = dict(gs_cellline.provenance)
    prov.update(comparison="nested-sampling log-evidence Bayes factor",
                observable="rolling-median curvature H vs closing angle theta (window=82)",
                models="H0 tanh(g th/H0) [CoopCM] vs H0(1-exp(-g th/H0)) [Helfrich]",
                force_note="absolute force not involved; refused on static path",
                analysis_scope="exploratory curve diagnostics",
                calibrated_likelihood=False,
                mechanism_inference_allowed=False,
                uncertainty_model="fitted iid scatter on overlapping rolling medians",
                exploratory_threshold_exceeded=threshold_exceeded)
    return MechanismVerdict(
        cell_line=(gs_cellline.cell_lines[0] if len(gs_cellline.cell_lines) == 1 else "pooled"),
        n_sites=len(gs_cellline.sites), logz=logz,
        lnB_coopcm_vs_helfrich=float(lnB), favored=favored, decisive=False,
        verdict=verdict, params=params, provenance=prov)



# Area and edge are transforms of the same fitted cap. Their scores reweight
# geometric residuals; they are not independent observations or held-out data.


def _cap_from_H(theta_deg, Hm):
    """Spherical-cap surface area and edge length from mean curvature H=1/R."""
    thr = np.radians(np.asarray(theta_deg, float))
    Hm = np.clip(Hm, 1e-6, None); R = 1.0 / Hm
    A = 2 * np.pi * R ** 2 * (1 - np.cos(thr))
    E = 2 * np.pi * R * np.sin(thr)
    return A, E


def _rolling_multi(theta, H, A, E, window=ROLLING_WINDOW, stride=20):
    o = np.argsort(theta); th_s = np.asarray(theta)[o]
    out = {}
    for key, arr in (("H", H), ("A", A), ("E", E)):
        a_s = np.asarray(arr)[o]; n = len(a_s); xs, ys = [], []
        for i in range(0, n, stride):
            lo = max(0, i - window // 2); hi = min(n, i + window // 2)
            if hi - lo < window // 2:
                continue
            xs.append(float(np.median(th_s[lo:hi]))); ys.append(float(np.median(a_s[lo:hi])))
        out[key] = (np.array(xs), np.array(ys))
    return out


def _fit_H_only(fn, x, y, nlive=400, seed=0):
    from dynesty import NestedSampler
    from dynesty.utils import resample_equal

    def pt(u):
        loH, hiH = PRIORS["H0"]; loG, hiG = PRIORS["gamma"]; loS, hiS = PRIORS["scatter"]
        return np.array([loH + u[0] * (hiH - loH), loG + u[1] * (hiG - loG),
                         loS + u[2] * (hiS - loS)])

    def ll(p):
        H0, g, s = p; r = (fn(x, H0, g) - y) / s
        return float(-0.5 * np.sum(r * r) - len(y) * np.log(s * np.sqrt(2 * np.pi)))

    rng = np.random.default_rng(seed)
    smp = NestedSampler(ll, pt, 3, nlive=nlive, rstate=rng)
    smp.run_nested(print_progress=False, dlogz=0.1, maxcall=600_000)
    res = smp.results
    eq = resample_equal(res.samples, np.exp(res.logwt - res.logz[-1]))
    return dict(H0=float(np.median(eq[:, 0])), gamma=float(np.median(eq[:, 1])),
                scatter=float(np.median(eq[:, 2])))


@dataclass
class MultiObservableVerdict:
    cell_line: str
    n_sites: int
    area_logrmse: dict           # per-model log-RMSE predicting A(theta)
    edge_logrmse: dict           # per-model log-RMSE predicting E(theta)
    favored: str                 # lower total cross-observable RMSE wins
    margin: float                # (CoopCM total - Helfrich total); >0 favours Helfrich
    verdict: str
    params: dict                 # H-only-fit params per model
    provenance: dict = field(default_factory=dict)

    def to_json(self, path):
        import dataclasses
        json.dump(dataclasses.asdict(self), open(path, "w"), indent=2, default=float)
        return path


def discriminate_multiobservable(gs_cellline, nlive=400, seed=0, *,
                                allow_exploratory=False) -> MultiObservableVerdict:
    """Score dependent cap transforms as exploratory geometric diagnostics."""
    _require_exploratory(allow_exploratory)
    theta = gs_cellline.arr("theta_deg"); H = gs_cellline.arr("H_inv_nm")
    A = gs_cellline.arr("surface_area_nm2")
    E = 2 * np.pi * gs_cellline.arr("R_nm") * np.sin(np.radians(theta))
    rm = _rolling_multi(theta, H, A, E)
    xH, yH = rm["H"]; xA, yA = rm["A"]; xE, yE = rm["E"]

    area_rmse, edge_rmse, params = {}, {}, {}
    for name, fn in MODELS.items():
        p = _fit_H_only(fn, xH, yH, nlive=nlive, seed=seed)
        params[name] = p
        Am, _ = _cap_from_H(xA, fn(xA, p["H0"], p["gamma"]))
        _, Em = _cap_from_H(xE, fn(xE, p["H0"], p["gamma"]))
        area_rmse[name] = float(np.sqrt(np.mean(
            (np.log(np.clip(Am, 1e-9, None)) - np.log(yA)) ** 2)))
        edge_rmse[name] = float(np.sqrt(np.mean(
            (np.log(np.clip(Em, 1e-9, None)) - np.log(yE)) ** 2)))

    tot_h = area_rmse["helfrich_linear"] + edge_rmse["helfrich_linear"]
    tot_c = area_rmse["coopcm"] + edge_rmse["coopcm"]
    favored = "helfrich_linear" if tot_h < tot_c else "coopcm"
    margin = float(tot_c - tot_h)
    verdict = (
        f"Exploratory geometric score prefers {favored} "
        f"(total log-RMSE {min(tot_h, tot_c):.3f} vs {max(tot_h, tot_c):.3f}). "
        "Area and edge share the curvature fit; this is not independent "
        "held-out evidence or a mechanism conclusion."
    )
    prov = dict(gs_cellline.provenance)
    prov.update(method="fit H(theta), score dependent cap area and edge transforms",
                analysis_scope="exploratory geometric diagnostics",
                calibrated_likelihood=False,
                mechanism_inference_allowed=False,
                uncertainty_model="fitted iid scatter on overlapping rolling medians",
                geometry_combination="selected H/theta, deposited area and radius magnitude; "
                                     "edge uses the legacy 2*pi*R*sin(selected theta) formula",
                caveat="dependent geometry reweights residuals without adding independent data; "
                       "corrected H/theta do not recalculate deposited area or radius")
    return MultiObservableVerdict(
        cell_line=(gs_cellline.cell_lines[0] if len(gs_cellline.cell_lines) == 1 else "pooled"),
        n_sites=len(gs_cellline.sites), area_logrmse=area_rmse, edge_logrmse=edge_rmse,
        favored=favored, margin=margin, verdict=verdict, params=params, provenance=prov)


if __name__ == "__main__":
    from validation.realdata.ingest_smlm_locmofit import ingest_locmofit
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-exploratory", action="store_true")
    args = parser.parse_args()
    if not args.allow_exploratory:
        parser.error("--allow-exploratory is required for these uncalibrated scores")
    gs = ingest_locmofit()
    for cl in ["SKMEL2", "3T3", "U2OS"]:
        gc = gs.by_cell_line(cl)
        v = discriminate(gc, allow_exploratory=args.allow_exploratory)
        mv = discriminate_multiobservable(gc, allow_exploratory=args.allow_exploratory)
        print(f"{cl} n={v.n_sites}:")
        print(f"   [curvature only]  lnB={v.lnB_coopcm_vs_helfrich:+.1f} decisive={v.decisive}")
        print(f"   [multi-observable] favored={mv.favored} "
              f"area-RMSE H={mv.area_logrmse['helfrich_linear']:.4f}/"
              f"C={mv.area_logrmse['coopcm']:.4f} "
              f"edge H={mv.edge_logrmse['helfrich_linear']:.4f}/"
              f"C={mv.edge_logrmse['coopcm']:.4f}")
