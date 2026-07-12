"""
mechanism.py — Bayesian mechanism-discrimination core.

Given an extracted geometry(t) trace (+ optional actin channel), rank COMPETING
MECHANISTIC HYPOTHESES for how the membrane was bent, by Bayesian evidence, and —
when the data cannot separate them — propose the DISAMBIGUATING EXPERIMENT.

Hypotheses (each = a restricted forward model, i.e. a subset of active forces; the
rest held at their null value):
  * wedge_only   : spontaneous curvature (c_eff_max) only; no cortical force
  * actin_only   : cortical/active force only; no spontaneous curvature
  * wedge+actin  : both actors free (the full model)
  * tension_only : neither actor; curvature driven by tension change alone (null-ish)

Ranking is by log-evidence log Z (nested sampling integrates the likelihood over
the prior, automatically penalizing unnecessary parameters — a built-in Occam
factor). We report:
  * per-hypothesis log Z and the Bayes factors / posterior model probabilities,
  * the FAVORED mechanism (if any clears a decisive threshold),
  * and when the top models are within a "not decisive" band, an explicit
    UNDETERMINED verdict + a proposed experiment that would separate them.

Disambiguating-experiment proposer
-----------------------------------
When wedge and actin are evidence-indistinguishable (the c_eff/active degeneracy
from geometry alone), the separating observable is the ACTIN CHANNEL: imaging
cortical actin recruitment, or a perturbation (e.g. actin depolymerization ->
force drops; H0-helix mutation -> c_eff drops). The proposer picks the
intervention whose predicted effect on the trace differs most between the tied
hypotheses. This closes the loop the analyze() endpoint requires.
"""
from __future__ import annotations

import json
import numpy as np

from . import inverse as inv


# hypothesis = which forces are FREE parameters (others held at null)
HYPOTHESES = {
    "tension_only": ["sigma"],
    "wedge_only":   ["c_eff_max", "sigma"],
    "actin_only":   ["active_force_max", "sigma"],
    "wedge+actin":  ["c_eff_max", "active_force_max", "sigma"],
}


def _params_for(free_names):
    """Build the dynesty param list for a hypothesis (subset of DEFAULT_PARAMS)."""
    by = {p.name: p for p in inv.DEFAULT_PARAMS}
    return [by[n] for n in free_names]


def fit_hypothesis(name, H_obs, H_sigma, A_coat_nm2, mask=None, nlive=250,
                   seed=0, actin_obs=None, actin_sigma=None):
    """Fit one restricted hypothesis; return posterior + log Z + identifiability."""
    free = HYPOTHESES[name]
    params = _params_for(free)
    res = inv.run_nested(H_obs, H_sigma, A_coat_nm2, params=params, mask=mask,
                         nlive=nlive, seed=seed,
                         actin_obs=actin_obs, actin_sigma=actin_sigma)
    ident = inv.identifiability(res["samples"], params)
    return dict(name=name, free=free, logz=res["logz"], logz_err=res["logz_err"],
                identifiability=ident, n_params=len(params))


def discriminate(H_obs, H_sigma, A_coat_nm2, mask=None, actin_obs=None,
                 actin_sigma=None, hypotheses=None, nlive=250, seed=0,
                 decisive_lnB=2.5, verbose=False):
    """Rank hypotheses by evidence; return favored mechanism or UNDETERMINED.

    decisive_lnB: minimum log-Bayes-factor of the top model over the runner-up to
    declare a decisive winner (2.5 ~ Bayes factor ~12, 'strong' on the Jeffreys
    scale). Below this the verdict is UNDETERMINED and a disambiguating experiment
    is proposed.
    """
    hyps = hypotheses or list(HYPOTHESES.keys())
    fits = []
    for i, h in enumerate(hyps):
        f = fit_hypothesis(h, H_obs, H_sigma, A_coat_nm2, mask=mask, nlive=nlive,
                           seed=seed + i, actin_obs=actin_obs, actin_sigma=actin_sigma)
        fits.append(f)
        if verbose:
            print(f"  {h:14s} logZ={f['logz']:.2f} +/- {f['logz_err']:.2f} ({f['n_params']} params)")
    fits.sort(key=lambda d: d["logz"], reverse=True)
    logzs = np.array([f["logz"] for f in fits])
    # posterior model probabilities (equal prior over hypotheses)
    w = np.exp(logzs - logzs.max()); w /= w.sum()
    for f, p in zip(fits, w):
        f["model_prob"] = float(p)
    top, second = fits[0], fits[1]
    lnB = top["logz"] - second["logz"]
    decisive = lnB >= decisive_lnB

    # OVERFIT GUARDRAIL: a more-complex model may beat a simpler one only by
    # exploiting an UNIDENTIFIABLE degeneracy direction (e.g. wedge+actin fits H(t)
    # better than wedge_only purely via the c_eff/active trade-off, with no actin
    # data to pin active_force). If the top model's DISTINGUISHING extra actor(s)
    # -- the params it has that the runner-up lacks -- are not themselves
    # identified in its posterior, the evidence win is spurious overfitting: demote
    # to UNDETERMINED so analyze() proposes the disambiguating experiment instead of
    # claiming a mechanism the data cannot support.
    overfit_flag = None
    if decisive:
        extra = [p for p in top["free"] if p not in second["free"]]
        unident_extra = [p for p in extra
                         if not top["identifiability"].get(p, {}).get("identified", False)]
        if extra and unident_extra:
            decisive = False
            overfit_flag = dict(
                extra_actors=extra, unidentified=unident_extra,
                note=("top model beat the runner-up via actor(s) that are NOT "
                      "identifiable in its own posterior -- an evidence gain along a "
                      "degeneracy direction, not a supported mechanism. Verdict "
                      "downgraded to UNDETERMINED."))
    verdict = dict(
        favored=top["name"] if decisive else "UNDETERMINED",
        top_two=[top["name"], second["name"]],
        ln_bayes_factor=float(lnB), decisive=bool(decisive),
        decisive_threshold=decisive_lnB,
        ranking=[dict(name=f["name"], logz=f["logz"], model_prob=f["model_prob"],
                      n_params=f["n_params"]) for f in fits])
    if overfit_flag:
        verdict["overfit_downgrade"] = overfit_flag
    if not decisive:
        verdict["suggested_experiment"] = propose_experiment(top, second)
    return verdict, fits


def propose_experiment(top, second):
    """Propose the intervention that best separates two tied hypotheses."""
    names = {top["name"], second["name"]}
    # wedge vs actin tie -> the actin channel / a force perturbation separates them
    if names == {"wedge_only", "actin_only"} or names == {"wedge+actin", "wedge_only"} \
       or names == {"wedge+actin", "actin_only"}:
        return dict(
            question="Is the invagination driven by spontaneous curvature (wedge) or cortical force (actin)?",
            observable="cortical actin-density channel co-imaged with the membrane",
            intervention="acute actin depolymerization (e.g. latrunculin) OR amphipathic-helix (H0) mutation",
            predicted_contrast=("actin_only / wedge+actin: invagination stalls or reverses when "
                                "actin is depolymerized; wedge_only: invagination proceeds. "
                                "H0 mutation removes curvature drive in the wedge models only."),
            rationale=("c_eff_max and active_force_max are degenerate from geometry(t) alone "
                       "(they trade off in the cap energy). An independent actin readout or a "
                       "targeted perturbation breaks the degeneracy, which the recovery "
                       "validation shows lifts active_force to identified."))
    # tension vs a force actor
    if "tension_only" in names:
        return dict(
            question="Is curvature change driven by a membrane force actor or by tension change alone?",
            observable="membrane tension (e.g. tether-pulling / Flipper-TR lifetime) time course",
            intervention="osmotic / micropipette tension clamp",
            predicted_contrast="a force-actor model predicts curvature grows at fixed tension; "
                               "tension_only predicts curvature tracks the measured tension drop.",
            rationale="clamping tension removes the tension_only explanatory pathway.")
    return dict(
        question="Which mechanism dominates?",
        observable="an independent channel constraining the tied actor",
        intervention="targeted perturbation of the distinguishing actor",
        predicted_contrast="the models predict divergent trace responses to the perturbation.",
        rationale="the current data leave the tied actors underdetermined.")
