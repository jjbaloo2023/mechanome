"""Infer mechanical parameters from a curvature trajectory.

predict_H() evaluates spherical-cap mechanics over all frames. make_loglike()
compares that prediction with measured curvature and optional actin density.
run_nested() returns posterior samples and evidence; run_mcmc() provides an
independent posterior check. identifiability() checks posterior width, parameter
correlations, and proximity to prior bounds before a force can be reported.

The default model has 24 frames, fixed bending modulus and coat rigidity, and
three inferred parameters: spontaneous curvature, active force, and tension.
Scientific parameter names and units are retained at the public API boundary.
"""

from __future__ import annotations

import dataclasses

import numpy as np

from . import evaluator_tier0 as ev
from . import synth_movie as sm


# ------------------------------------------------------------- parameters ----
@dataclasses.dataclass
class Param:
    name: str
    lo: float
    hi: float
    units: str


# default inference parameters + flat-prior ranges (informed by parameter store)
DEFAULT_PARAMS = [
    Param("c_eff_max", 0.0, 0.08, "nm^-1"),  # spontaneous curvature plateau
    Param("active_force_max", 0.0, 60.0, "pN"),  # cortical force plateau
    Param("sigma", 0.001, 0.05, "kBT/nm^2"),  # membrane tension
]

# fixed context (not inferred this run; can be promoted to params later)
FIXED = dict(kappa_kBT=20.0, coat_rigidity_factor=3.0, T=24)


@dataclasses.dataclass(frozen=True)
class ObservationContext:
    """Declared observation assumptions, not an experimental certification.

    Custom coverage replaces the synthetic assembly clock in every hypothesis.
    Its measurement uncertainty is not propagated by this conditional model.
    """
    input_kind: str = "unknown"
    calibration_id: str | None = None
    coverage: tuple[float, ...] | None = None
    actin_force_scale_pN: float = sm.ACTIN_CALIB_PN

    def __post_init__(self):
        if self.coverage is not None:
            values = np.asarray(self.coverage, float)
            if values.ndim != 1:
                raise ValueError("coverage must be a one-dimensional trace")
            object.__setattr__(self, "coverage", tuple(map(float, values)))

    def coverage_array(self, n_frames):
        if self.input_kind not in ("unknown", "synthetic", "experimental"):
            raise ValueError("input_kind must be unknown, synthetic, or experimental")
        if not np.isfinite(self.actin_force_scale_pN) or self.actin_force_scale_pN <= 0:
            raise ValueError("actin force scale must be finite and positive")
        values = _coverage_ramp(n_frames) if self.coverage is None else np.asarray(self.coverage, float)
        if values.shape != (n_frames,) or not np.all(np.isfinite(values) & (values >= 0) & (values <= 1)):
            raise ValueError("coverage must match frames and contain finite fractions in [0, 1]")
        return values


_PSI = np.linspace(0.02, np.pi - 0.001, 400)  # cap opening-angle grid


def _fast_H_trajectory(
    sigma, c_eff_max, active_max, kappa, coat_rig, A, T, ramp_mid=0.45, ramp_width=0.12,
    coverage=None,
):
    """Vectorized H(t): the same spherical-cap energy minimization as the
    evaluator's ccs_curvature, but computed as numpy array ops over the whole
    (frame x psi) grid at once -- ~50x faster than the per-psi Python loop, which
    matters for the thousands of likelihood calls a sampler makes. Reproduces
    evaluator_tier0._cap_energy exactly (bending + line(=0) + tension + active).
    """
    kBT = ev.kBT_zJ
    coverage = _coverage_ramp(T, ramp_mid, ramp_width) if coverage is None else coverage
    c_eff = c_eff_max * coverage  # (T,)
    active_force = active_max * coverage  # (T,)
    rigidity = 1.0 + (coat_rig - 1.0) * coverage  # (T,)
    kappa_eff = kappa * rigidity  # (T,)
    psi = _PSI[None, :]  # (1,P)
    one_minus_cos = np.clip(1.0 - np.cos(psi), 1e-9, None)  # (1,P)
    radius = np.sqrt(A / (2 * np.pi * one_minus_cos))  # (1,P) - psi-only
    depth = radius * one_minus_cos  # (1,P)
    footprint = np.pi * (radius * np.sin(psi)) ** 2  # (1,P)
    # energy terms broadcast over (T,P)
    bending = (kappa_eff[:, None] / 2) * (2.0 / radius - c_eff[:, None]) ** 2 * A
    tension = sigma * (A - footprint)
    active_energy = -(active_force[:, None] * depth) / kBT
    energy = bending + tension + active_energy  # (T,P); line term lam=0
    minimum_indices = np.argmin(energy, axis=1)  # (T,)
    optimal_radius = radius[0, minimum_indices]
    return 1.0 / optimal_radius  # H(t)


def predict_H(theta, params, A_coat_nm2, fixed=FIXED, context=None):
    """Forward model: force vector theta -> mean-curvature trajectory H(t)."""
    parameter_values = {p.name: v for p, v in zip(params, theta)}
    return _fast_H_trajectory(
        sigma=parameter_values.get("sigma", 0.02),
        c_eff_max=parameter_values.get("c_eff_max", 0.0),
        active_max=parameter_values.get("active_force_max", 0.0),
        kappa=fixed["kappa_kBT"],
        coat_rig=fixed["coat_rigidity_factor"],
        A=A_coat_nm2,
        T=fixed["T"],
        coverage=(context or ObservationContext()).coverage_array(fixed["T"]),
    )


# ---------------------------------------------------------- likelihood -------
def _gaussian_term(values, sigma, mask, n_frames, floor):
    """Validate observations once and return their masked Gaussian likelihood."""
    values, sigma = np.asarray(values, float), np.asarray(sigma, float)
    if values.shape != (n_frames,) or sigma.shape != (n_frames,):
        raise ValueError(
            f"observations and uncertainties must have shape {(n_frames,)}"
        )
    values, sigma = values[mask], sigma[mask]
    if not np.all(np.isfinite(values)):
        raise ValueError("selected observations must be finite")
    if not np.all(np.isfinite(sigma) & (sigma > 0)):
        raise ValueError("selected uncertainties must be finite and positive")
    sigma = np.clip(sigma, floor, None)
    log_sigma = np.sum(np.log(sigma))
    normalization = 0.5 * len(values) * np.log(2 * np.pi)

    def score(prediction):
        residual = (prediction[mask] - values) / sigma
        return float(-0.5 * np.sum(residual * residual) - log_sigma - normalization)

    return score


def make_loglike(
    H_obs,
    H_sigma,
    params,
    A_coat_nm2,
    fixed=FIXED,
    mask=None,
    actin_obs=None,
    actin_sigma=None,
    context=None,
):
    """Score curvature and optional actin data on the same selected frames.

    Actin density follows the renderer's force calibration. Every hypothesis
    scores that channel, including models whose active force is fixed at zero.
    """
    if not np.isfinite(A_coat_nm2) or A_coat_nm2 <= 0:
        raise ValueError("coat area must be finite and positive")
    n_frames = fixed["T"]
    context = context or ObservationContext()
    coverage = context.coverage_array(n_frames)
    mask = np.ones(n_frames, bool) if mask is None else np.asarray(mask, dtype=bool)
    if mask.shape != (n_frames,) or not mask.any():
        raise ValueError(
            "mask must match the observations and select at least one frame"
        )
    curvature_term = _gaussian_term(H_obs, H_sigma, mask, n_frames, 1e-4)
    if (actin_obs is None) != (actin_sigma is None):
        raise ValueError("actin_obs and actin_sigma must be supplied together")
    actin_term = None
    if actin_obs is not None:
        actin_term = _gaussian_term(actin_obs, actin_sigma, mask, n_frames, 1e-3)

    def loglike(theta):
        total = curvature_term(predict_H(theta, params, A_coat_nm2, fixed, context))
        if actin_term is not None:
            values = {p.name: v for p, v in zip(params, theta)}
            force_fraction = values.get("active_force_max", 0.0) / context.actin_force_scale_pN
            total += actin_term(coverage * force_fraction)
        return total

    return loglike


def _coverage_ramp(T, ramp_mid=0.45, ramp_width=0.12):
    time = np.linspace(0, 1, T)
    coverage = 1.0 / (1.0 + np.exp(-(time - ramp_mid) / ramp_width))
    return (coverage - coverage.min()) / (coverage.max() - coverage.min())


def prior_transform(u, params):
    """Map unit cube -> flat priors on each parameter (dynesty convention)."""
    return np.array([p.lo + (p.hi - p.lo) * ui for p, ui in zip(params, u)])


# ------------------------------------------------------ nested sampling ------
def run_nested(
    H_obs,
    H_sigma,
    A_coat_nm2,
    params=None,
    mask=None,
    nlive=250,
    seed=0,
    fixed=FIXED,
    actin_obs=None,
    actin_sigma=None,
    dlogz=0.05,
    maxcall=500_000,
    maxiter=None,
    context=None,
):
    """Return posterior samples and evidence from dynesty static sampling.

    dlogz controls the remaining-evidence tolerance. maxcall and maxiter limit
    sampling cost. stopped_early flags a reached cap; downstream reporting treats
    that posterior as provisional and withholds decisive claims.
    """
    from dynesty import NestedSampler
    from dynesty.utils import resample_equal

    params = params or DEFAULT_PARAMS
    loglike = make_loglike(
        H_obs,
        H_sigma,
        params,
        A_coat_nm2,
        fixed,
        mask,
        actin_obs=actin_obs,
        actin_sigma=actin_sigma,
        context=context,
    )
    ndim = len(params)
    rng = np.random.default_rng(seed)
    sampler = NestedSampler(
        loglike, lambda u: prior_transform(u, params), ndim, nlive=nlive, rstate=rng
    )
    sampler.run_nested(
        print_progress=False, dlogz=dlogz, maxcall=maxcall, maxiter=maxiter
    )
    res = sampler.results
    ncall = int(np.sum(res.ncall)) if hasattr(res, "ncall") else None
    niter = int(res.niter) if hasattr(res, "niter") else None
    stopped_early = bool(
        (ncall is not None and ncall >= maxcall)
        or (maxiter is not None and niter is not None and niter >= maxiter)
    )
    logwt = res.logwt - res.logz[-1]
    weights = np.exp(logwt)
    samples = resample_equal(res.samples, weights, rstate=rng)
    return dict(
        samples=samples,
        logz=float(res.logz[-1]),
        logz_err=float(res.logzerr[-1]),
        params=params,
        engine="dynesty",
        ncall=ncall,
        niter=niter,
        stopped_early=stopped_early,
        observation_context=dataclasses.asdict(context or ObservationContext()),
    )


# --------------------------------------------------------------- MCMC --------
def run_mcmc(
    H_obs,
    H_sigma,
    A_coat_nm2,
    params=None,
    mask=None,
    nwalkers=32,
    nsteps=2000,
    burn=500,
    seed=0,
    fixed=FIXED,
    actin_obs=None,
    actin_sigma=None,
    context=None,
):
    """emcee affine-invariant MCMC -> posterior samples (independent cross-check)."""
    import emcee

    params = params or DEFAULT_PARAMS
    loglike = make_loglike(
        H_obs,
        H_sigma,
        params,
        A_coat_nm2,
        fixed,
        mask,
        actin_obs=actin_obs,
        actin_sigma=actin_sigma,
        context=context,
    )
    ndim = len(params)

    def logpost(theta):
        for p, v in zip(params, theta):
            if not (p.lo <= v <= p.hi):
                return -np.inf
        return loglike(theta)

    rng = np.random.default_rng(seed)
    p0 = np.array(
        [[p.lo + (p.hi - p.lo) * rng.random() for p in params] for _ in range(nwalkers)]
    )
    sampler = emcee.EnsembleSampler(nwalkers, ndim, logpost)
    sampler.run_mcmc(p0, nsteps, progress=False)
    chain = sampler.get_chain(discard=burn, flat=True)
    return dict(
        samples=chain,
        params=params,
        engine="emcee",
        acceptance=float(np.mean(sampler.acceptance_fraction)),
    )


# ------------------------------------------------- identifiability report ----
def identifiability(
    samples, params, width_ratio_thresh=0.5, corr_thresh=0.7, rail_frac=0.15
):
    """Per-parameter identifiability from posterior vs (flat) prior, PLUS a
    joint-degeneracy check from the posterior correlation matrix.

    A parameter's MARGINAL is 'constrained' if its posterior is appreciably
    narrower than its prior (width_ratio < thresh). But a narrow marginal is NOT
    sufficient for identifiability: two parameters can each have a tight marginal
    yet be jointly DEGENERATE (only a combination is constrained; along the
    degeneracy direction the data say nothing). We detect this from |posterior
    correlation| > corr_thresh and demote BOTH members of a degenerate pair to
    identified=False, recording the partner. This is the anti-"force-astrology"
    gate: analyze() must not report a confident point value for a parameter that
    is only apparently pinned because it is trading off against another actor.
    """
    n_params = len(params)
    correlation = np.corrcoef(samples.T) if n_params > 1 else np.array([[1.0]])
    # find strongly-correlated (degenerate) pairs
    degenerate = {parameter.name: [] for parameter in params}
    for i in range(n_params):
        for j in range(i + 1, n_params):
            if abs(correlation[i, j]) > corr_thresh:
                degenerate[params[i].name].append(
                    dict(partner=params[j].name, corr=float(correlation[i, j]))
                )
                degenerate[params[j].name].append(
                    dict(partner=params[i].name, corr=float(correlation[i, j]))
                )
    report = {}
    for j, parameter in enumerate(params):
        posterior_samples = samples[:, j]
        prior_std = (parameter.hi - parameter.lo) / np.sqrt(12.0)  # uniform prior std
        post_std = float(np.std(posterior_samples))
        width_ratio = post_std / prior_std if prior_std > 0 else np.nan
        info_bits = (
            float(0.5 * np.log((prior_std**2) / (post_std**2 + 1e-12)) / np.log(2))
            if post_std > 0
            else np.inf
        )
        marginal_constrained = width_ratio < width_ratio_thresh
        partners = degenerate[parameter.name]
        # RAIL check: if the posterior piles up against a prior boundary, the data
        # are not localizing the parameter -- they only push it to the edge, and
        # the "narrow" marginal is an artifact of the wall, not information. Flag as
        # railed if the median sits within rail_frac of the prior span from either bound.
        span = parameter.hi - parameter.lo
        median = float(np.median(posterior_samples))
        railed = bool(
            (median - parameter.lo) < rail_frac * span
            or (parameter.hi - median) < rail_frac * span
        )
        # identified only if the MARGINAL is constrained, NOT degenerate with
        # another actor, and NOT railed against a prior boundary.
        identified = bool(marginal_constrained and not partners and not railed)
        report[parameter.name] = dict(
            median=float(np.median(posterior_samples)),
            ci68=[
                float(np.percentile(posterior_samples, 16)),
                float(np.percentile(posterior_samples, 84)),
            ],
            ci95=[
                float(np.percentile(posterior_samples, 2.5)),
                float(np.percentile(posterior_samples, 97.5)),
            ],
            post_std=post_std,
            prior_std=float(prior_std),
            width_ratio=float(width_ratio),
            info_gain_bits=info_bits,
            marginal_constrained=bool(marginal_constrained),
            degenerate_with=partners,
            railed=railed,
            identified=identified,
            units=parameter.units,
        )
    return report


def summarize(result):
    """Compact posterior summary + identifiability for a nested/mcmc result."""
    identifiability_report = identifiability(result["samples"], result["params"])
    summary = dict(engine=result["engine"], identifiability=identifiability_report)
    if "logz" in result:
        summary["logz"] = result["logz"]
        summary["logz_err"] = result.get("logz_err")
    if "acceptance" in result:
        summary["acceptance"] = result["acceptance"]
    return summary
