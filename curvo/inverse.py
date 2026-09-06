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


_PSI = np.linspace(0.02, np.pi - 0.001, 400)  # cap opening-angle grid


def _fast_H_trajectory(
    sigma, c_eff_max, active_max, kappa, coat_rig, A, T, ramp_mid=0.45, ramp_width=0.12
):
    """Vectorized H(t): the same spherical-cap energy minimization as the
    evaluator's ccs_curvature, but computed as numpy array ops over the whole
    (frame x psi) grid at once -- ~50x faster than the per-psi Python loop, which
    matters for the thousands of likelihood calls a sampler makes. Reproduces
    evaluator_tier0._cap_energy exactly (bending + line(=0) + tension + active).
    """
    kBT = ev.kBT_zJ
    coverage = _coverage_ramp(T, ramp_mid, ramp_width)
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


def predict_H(theta, params, A_coat_nm2, fixed=FIXED):
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
    )


# ---------------------------------------------------------- likelihood -------
def make_loglike(
    H_obs,
    H_sigma,
    params,
    A_coat_nm2,
    fixed=FIXED,
    mask=None,
    actin_obs=None,
    actin_sigma=None,
):
    """Gaussian log-likelihood in H(t) with per-frame sigma; masked frames dropped.

    If an ACTIN-density channel is supplied (actin_obs/actin_sigma, normalized to
    [0,1]), an extra Gaussian term ties active_force_max to the observed actin
    intensity: actin recruitment is proportional to the cortical force the machine
    can exert, so the coat-assembly-scaled active force predicts the normalized
    actin trace. This independent observable is what BREAKS the c_eff/active
    degeneracy that H(t) alone cannot resolve. Without an actin channel the term
    is absent and the degeneracy stands (correctly reported by identifiability()).
    """
    H_obs = np.asarray(H_obs, float)
    H_sigma = np.clip(np.asarray(H_sigma, float), 1e-4, None)
    if mask is None:
        mask = np.ones(len(H_obs), bool)
    frame_indices = np.where(mask)[0]
    use_actin = actin_obs is not None
    if use_actin:
        actin_values = np.asarray(actin_obs, float)
        actin_uncertainty = np.clip(np.asarray(actin_sigma, float), 1e-3, None)
        coverage = _coverage_ramp(fixed["T"])

    def loglike(theta):
        predicted_curvature = predict_H(theta, params, A_coat_nm2, fixed)
        curvature_residual = (
            predicted_curvature[frame_indices] - H_obs[frame_indices]
        ) / H_sigma[frame_indices]
        log_likelihood = float(
            -0.5 * np.sum(curvature_residual * curvature_residual)
            - np.sum(np.log(H_sigma[frame_indices]))
            - 0.5 * len(frame_indices) * np.log(2 * np.pi)
        )
        if use_actin:
            # predicted calibrated actin = assembly ramp * (active_force/ACTIN_CALIB).
            # This matches the perception observable (peak actin / peak_photons ==
            # force/ACTIN_CALIB_PN), so the channel constrains force MAGNITUDE.
            # CRUCIAL for model comparison: this term applies to EVERY hypothesis,
            # using active_force_max=0 when that actor is not free. A wedge-only
            # model then predicts ZERO actin and is correctly PENALIZED against a
            # real actin signal -- so all models are scored on the same data (a
            # requirement for valid Bayesian evidence comparison).
            parameter_values = {p.name: v for p, v in zip(params, theta)}
            calibrated_force = (
                parameter_values.get("active_force_max", 0.0) / sm.ACTIN_CALIB_PN
            )
            predicted_actin = coverage * calibrated_force
            actin_residual = (
                predicted_actin[frame_indices] - actin_values[frame_indices]
            ) / actin_uncertainty[frame_indices]
            log_likelihood += float(
                -0.5 * np.sum(actin_residual * actin_residual)
                - np.sum(np.log(actin_uncertainty[frame_indices]))
                - 0.5 * len(frame_indices) * np.log(2 * np.pi)
            )
        return log_likelihood

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
):
    """dynesty static nested sampling -> posterior samples + log-evidence.

    Plateau guard: the loglikelihood can plateau (e.g. an actin channel that is
    flat across a whole restricted model, or a near-degenerate direction). Without
    stopping caps, dynesty can spin for hours on such a run. We therefore pass
    explicit, deterministic bounds:
      * dlogz    -- early stop when the estimated remaining evidence is negligible.
                    0.05 is well below the lnB~0.3 resolution the model-comparison
                    decisions need, so it does not affect a verdict. It is TIGHTER
                    than dynesty's own nlive-dependent default (1e-3*(nlive-1)+0.01,
                    ~0.16-0.26 here), so the run samples at least as long as before
                    the explicit cap -- the guard bounds runaway cost, it does not
                    truncate a healthy run early.
      * maxcall  -- hard cap on likelihood evaluations (~0.2 ms each, so 500k bounds
                    worst-case wall-clock to a few minutes; a healthy run uses
                    ~10-30k and stops on dlogz long before this).
      * maxiter  -- optional hard iteration cap (None = governed by dlogz/maxcall).
    `stopped_early` in the result flags when a cap (not dlogz) terminated the run,
    so a caller can widen the cap or down-weight that fit rather than trust a
    truncated evidence.
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
    samples = resample_equal(res.samples, weights)
    return dict(
        samples=samples,
        logz=float(res.logz[-1]),
        logz_err=float(res.logzerr[-1]),
        params=params,
        engine="dynesty",
        ncall=ncall,
        niter=niter,
        stopped_early=stopped_early,
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
