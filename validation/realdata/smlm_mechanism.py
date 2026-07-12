"""
smlm_mechanism.py -- Helfrich vs Cooperative Curvature Model on real SMLM data.

The scientific payload. From the pseudo-temporally-sorted curvature trajectory
H(theta), discriminate two mechanistic rate laws for coat-curvature generation
by Bayesian model comparison (nested-sampling log-evidence -> Bayes factor):

  * Helfrich relaxation (non-cooperative).  Curvature relaxes toward a preferred
    value H0 at a rate proportional to the REMAINING gap -- the standard linear
    restoring dynamics of a Helfrich energy with a fixed preferred curvature:
        dH/dtheta = gamma (1 - H/H0)      ->   H(theta) = H0 (1 - exp(-gamma theta / H0))
  * Cooperative Curvature Model (CoopCM; Mund et al. 2023, Eqs. 2-3).  Positive
    feedback: the rate depends QUADRATICALLY on the curvature gap, so triskelia
    already in a curved lattice cooperatively promote further bending:
        dH/dtheta = gamma (1 - H^2/H0^2)  ->   H(theta) = H0 tanh(gamma theta / H0)

Both are two-parameter (H0, gamma) with a shared scatter nuisance, so the Bayes
factor reflects fit quality, not complexity. We fit the ROLLING MEDIAN of
curvature over theta (window = 82 sites), matching the original analysis.

RESULT (identifiability firewall applied to MECHANISM): on the curvature-vs-theta
observable alone, tanh and 1-exp are functionally near-identical saturating
curves, and the Bayes factor is INCONCLUSIVE (|lnB| < 2.5) for all three cell
lines. curvo reproduces the paper's geometry and both candidate laws, but
refuses to declare a decisive winner the single observable does not support --
the paper's decisive CoopCM preference rests on a JOINT fit over curvature AND
surface area AND edge length (their Fig. 3, B-D). Absolute force is not involved
and remains refused on this static path.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

ROLLING_WINDOW = 82          # sites; matches Mund et al. 2023 rolling median
DECISIVE_LNB = 2.5           # Kass & Raftery "decisive"
# uniform priors: preferred curvature H0 (nm^-1), initial rate gamma, scatter s
PRIORS = dict(H0=(0.004, 0.030), gamma=(0.0, 0.05), scatter=(5e-4, 1e-2))


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


def discriminate(gs_cellline, nlive=400, seed=0, decisive_lnB=DECISIVE_LNB):
    """Fit both rate laws to the rolling-median H(theta) of a single cell line
    and compare evidence. gs_cellline is an SMLMGeometrySet (one cell line)."""
    theta = gs_cellline.arr("theta_deg"); H = gs_cellline.arr("H_inv_nm")
    xr, yr = rolling_median(theta, H)
    logz, params = {}, {}
    for name, fn in MODELS.items():
        lz, pr = _fit(fn, xr, yr, nlive=nlive, seed=seed)
        logz[name] = lz; params[name] = pr
    lnB = logz["coopcm"] - logz["helfrich_linear"]
    decisive = bool(abs(lnB) > decisive_lnB)
    favored = "coopcm" if lnB > 0 else "helfrich_linear"
    if decisive:
        verdict = (f"{favored} favored decisively (lnB={lnB:+.1f})")
    else:
        verdict = (f"INCONCLUSIVE on H(theta) alone (lnB={lnB:+.1f}, |lnB|<{decisive_lnB}): "
                   "tanh and 1-exp are near-identical saturating laws on this "
                   "observable; decisive separation needs the joint "
                   "curvature+area+edge fit (Mund et al. 2023, Fig. 3 B-D)")
    prov = dict(gs_cellline.provenance)
    prov.update(comparison="nested-sampling log-evidence Bayes factor",
                observable="rolling-median curvature H vs closing angle theta (window=82)",
                models="H0 tanh(g th/H0) [CoopCM] vs H0(1-exp(-g th/H0)) [Helfrich]",
                force_note="absolute force not involved; refused on static path")
    return MechanismVerdict(
        cell_line=(gs_cellline.cell_lines[0] if len(gs_cellline.cell_lines) == 1 else "pooled"),
        n_sites=len(gs_cellline.sites), logz=logz,
        lnB_coopcm_vs_helfrich=float(lnB), favored=favored, decisive=decisive,
        verdict=verdict, params=params, provenance=prov)


if __name__ == "__main__":
    from validation.realdata.ingest_smlm_locmofit import ingest_locmofit
    gs = ingest_locmofit()
    for cl in ["SKMEL2", "3T3", "U2OS"]:
        v = discriminate(gs.by_cell_line(cl))
        print(f"{cl} n={v.n_sites}: lnB={v.lnB_coopcm_vs_helfrich:+.1f} decisive={v.decisive}")
        print(f"   {v.verdict}")
        print(f"   CoopCM H0={v.params['coopcm']['H0']:.4f} gamma={v.params['coopcm']['gamma']:.4f}")
