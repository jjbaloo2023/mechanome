"""Compare competing explanations of membrane bending using Bayesian evidence.

Each hypothesis frees a subset of the same forward model's parameters. All fits
use the same observations and equal model priors. discriminate() ranks their
evidence, checks the winning model's extra actors for identifiability, and
returns either a supported winner or UNDETERMINED with a proposed experiment.
"""

from __future__ import annotations

import numpy as np

from . import inverse

# hypothesis = which forces are FREE parameters (others held at null)
HYPOTHESES = {
    "tension_only": ["sigma"],
    "wedge_only": ["c_eff_max", "sigma"],
    "actin_only": ["active_force_max", "sigma"],
    "wedge+actin": ["c_eff_max", "active_force_max", "sigma"],
}


def _params_for(free_names):
    """Build the dynesty param list for a hypothesis (subset of DEFAULT_PARAMS)."""
    parameters_by_name = {p.name: p for p in inverse.DEFAULT_PARAMS}
    return [parameters_by_name[n] for n in free_names]


def fit_hypothesis(
    name,
    H_obs,
    H_sigma,
    A_coat_nm2,
    mask=None,
    nlive=250,
    seed=0,
    actin_obs=None,
    actin_sigma=None,
):
    """Fit one restricted hypothesis; return posterior + log Z + identifiability."""
    free = HYPOTHESES[name]
    params = _params_for(free)
    posterior = inverse.run_nested(
        H_obs,
        H_sigma,
        A_coat_nm2,
        params=params,
        mask=mask,
        nlive=nlive,
        seed=seed,
        actin_obs=actin_obs,
        actin_sigma=actin_sigma,
    )
    identifiability = inverse.identifiability(posterior["samples"], params)
    return dict(
        name=name,
        free=free,
        logz=posterior["logz"],
        logz_err=posterior["logz_err"],
        identifiability=identifiability,
        n_params=len(params),
    )


def _overfit_downgrade(top: dict, second: dict):
    """Reject an evidence win explained by extra actors the data cannot identify."""
    extra_actors = [name for name in top["free"] if name not in second["free"]]
    unidentified_actors = [
        name
        for name in extra_actors
        if not top["identifiability"].get(name, {}).get("identified", False)
    ]
    if not unidentified_actors:
        return None
    return dict(
        extra_actors=extra_actors,
        unidentified=unidentified_actors,
        note=(
            "top model beat the runner-up via actor(s) that are NOT "
            "identifiable in its own posterior -- an evidence gain along a "
            "degeneracy direction, not a supported mechanism. Verdict "
            "downgraded to UNDETERMINED."
        ),
    )


def discriminate(
    H_obs,
    H_sigma,
    A_coat_nm2,
    mask=None,
    actin_obs=None,
    actin_sigma=None,
    hypotheses=None,
    nlive=250,
    seed=0,
    decisive_lnB=2.5,
    verbose=False,
):
    """Rank hypotheses by evidence; return favored mechanism or UNDETERMINED.

    decisive_lnB: minimum log-Bayes-factor of the top model over the runner-up to
    declare a decisive winner (2.5 ~ Bayes factor ~12, 'strong' on the Jeffreys
    scale). Below this the verdict is UNDETERMINED and a disambiguating experiment
    is proposed.
    """
    selected_hypotheses = hypotheses or list(HYPOTHESES.keys())
    fits = []
    for i, hypothesis in enumerate(selected_hypotheses):
        fit = fit_hypothesis(
            hypothesis,
            H_obs,
            H_sigma,
            A_coat_nm2,
            mask=mask,
            nlive=nlive,
            seed=seed + i,
            actin_obs=actin_obs,
            actin_sigma=actin_sigma,
        )
        fits.append(fit)
        if verbose:
            print(
                f"  {hypothesis:14s} logZ={fit['logz']:.2f} +/- {fit['logz_err']:.2f} ({fit['n_params']} params)"
            )
    fits.sort(key=lambda d: d["logz"], reverse=True)
    log_evidence = np.array([fit["logz"] for fit in fits])
    # posterior model probabilities (equal prior over hypotheses)
    probabilities = np.exp(log_evidence - log_evidence.max())
    probabilities /= probabilities.sum()
    for fit, probability in zip(fits, probabilities):
        fit["model_prob"] = float(probability)
    top, second = fits[0], fits[1]
    log_bayes_factor = top["logz"] - second["logz"]
    decisive = log_bayes_factor >= decisive_lnB

    overfit_flag = _overfit_downgrade(top, second) if decisive else None
    if overfit_flag:
        decisive = False

    verdict = dict(
        favored=top["name"] if decisive else "UNDETERMINED",
        top_two=[top["name"], second["name"]],
        ln_bayes_factor=float(log_bayes_factor),
        decisive=bool(decisive),
        decisive_threshold=decisive_lnB,
        ranking=[
            dict(
                name=fit["name"],
                logz=fit["logz"],
                model_prob=fit["model_prob"],
                n_params=fit["n_params"],
            )
            for fit in fits
        ],
    )
    if overfit_flag:
        verdict["overfit_downgrade"] = overfit_flag
    if not decisive:
        verdict["suggested_experiment"] = propose_experiment(top, second)
    return verdict, fits


def propose_experiment(top, second):
    """Propose the intervention that best separates two tied hypotheses."""
    names = {top["name"], second["name"]}
    # wedge vs actin tie -> the actin channel / a force perturbation separates them
    if (
        names == {"wedge_only", "actin_only"}
        or names == {"wedge+actin", "wedge_only"}
        or names == {"wedge+actin", "actin_only"}
    ):
        return dict(
            question="Is the invagination driven by spontaneous curvature (wedge) or cortical force (actin)?",
            observable="cortical actin-density channel co-imaged with the membrane",
            intervention="acute actin depolymerization (e.g. latrunculin) OR amphipathic-helix (H0) mutation",
            predicted_contrast=(
                "actin_only / wedge+actin: invagination stalls or reverses when "
                "actin is depolymerized; wedge_only: invagination proceeds. "
                "H0 mutation removes curvature drive in the wedge models only."
            ),
            rationale=(
                "c_eff_max and active_force_max are degenerate from geometry(t) alone "
                "(they trade off in the cap energy). An independent actin readout or a "
                "targeted perturbation breaks the degeneracy, which the recovery "
                "validation shows lifts active_force to identified."
            ),
        )
    # tension vs a force actor
    if "tension_only" in names:
        return dict(
            question="Is curvature change driven by a membrane force actor or by tension change alone?",
            observable="membrane tension (e.g. tether-pulling / Flipper-TR lifetime) time course",
            intervention="osmotic / micropipette tension clamp",
            predicted_contrast="a force-actor model predicts curvature grows at fixed tension; "
            "tension_only predicts curvature tracks the measured tension drop.",
            rationale="clamping tension removes the tension_only explanatory pathway.",
        )
    return dict(
        question="Which mechanism dominates?",
        observable="an independent channel constraining the tied actor",
        intervention="targeted perturbation of the distinguishing actor",
        predicted_contrast="the models predict divergent trace responses to the perturbation.",
        rationale="the current data leave the tied actors underdetermined.",
    )
