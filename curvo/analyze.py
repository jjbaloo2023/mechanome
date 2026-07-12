"""
analyze.py — the top-level agent endpoint.

    analyze(video, question, ...) -> {
        forces,               # posterior over mechanical forces (median + CI) —
                              #   POINT VALUE ONLY where identifiable, else posterior
        favored_mechanism,    # evidence-ranked hypothesis, or UNDETERMINED
        uncertainty,          # per-force CI68/CI95 + posterior width
        identifiability,      # which actors the data can/can't constrain + why
        suggested_experiment, # disambiguating experiment when UNDETERMINED
        provenance,           # models, params, versions, data hashes
    }

An LLM/agent hands curvo a microscopy movie (numpy array [T, C, H, W]) + a
mechanistic question in plain language; curvo runs the full pipeline
    pixels --perception--> geometry(t) --inverse--> force posterior
                       \\--mechanism--> evidence ranking + experiment
and returns a single structured object.

THE ANTI-"FORCE-ASTROLOGY" GUARDRAIL
------------------------------------
The endpoint NEVER reports a confident point value for a force the data cannot
constrain. Every force is checked against the identifiability report: if it is
degenerate with another actor or railed against a prior bound, `forces[name]`
carries `point_estimate=None`, `status="underdetermined"`, the full posterior CI,
and the reason. Recovery validation (Step 5) is what licenses this: only forces
shown there to be calibrated (active_force under an actin channel: cov68=0.96,
bias +2%) are ever returned as point values. This is the difference between an
inference engine and a horoscope.
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

from . import perception as pcp
from . import inverse as inv
from . import mechanism as mech
from .schemas import version_hashes_of


# Forces the SYNTHETIC RECOVERY VALIDATION (Step 5) demonstrated are calibrated
# (posterior median tracks truth with correct CI coverage across the noise grid).
# Only these may be returned as POINT estimates; every other actor is returned as
# a posterior flagged underdetermined, EVEN IF a single-shot identifiability report
# looks narrow -- a per-analysis posterior can be narrow yet biased (perception
# bias absorbed into the parameter), and only the recovery grid, which knows the
# truth, can certify calibration. This is the hard credibility gate.
#   active_force_max: recovery cov68|identified=0.96, rel_bias +2.0%  -> CALIBRATED
#   c_eff_max:        recovery identified  0/40 (degenerate from geometry) -> NOT
#   sigma:            recovery identified  0/40 (uninformative)            -> NOT
RECOVERY_CALIBRATED = {"active_force_max"}


def _hash_movie(movie):
    return hashlib.sha256(np.ascontiguousarray(movie).tobytes()).hexdigest()[:16]


def _question_to_hypotheses(question, has_actin):
    """Map a plain-language question to the hypothesis set to compare.

    Kept deliberately simple/transparent (keyword routing); an LLM orchestrator
    can override by passing `hypotheses=` explicitly. The point is that the
    physics/evidence machinery is fixed and auditable — only the hypothesis
    SELECTION is language-driven.
    """
    q = (question or "").lower()
    full = ["tension_only", "wedge_only", "actin_only", "wedge+actin"]
    if "actin" in q and ("or" in q or "vs" in q or "versus" in q or "wedge" in q or "curvature" in q):
        return ["wedge_only", "actin_only", "wedge+actin"]
    if "tension" in q:
        return full
    return full


def analyze(video, question=None, *, nm_per_px=2.0, psf_sigma_nm=18.0,
            peak_photons=220.0, channels=None, A_coat_nm2=None, host=None,
            hypotheses=None, nlive=200, seed=0, verbose=False):
    """Run the full pixels->forces->mechanism pipeline; return a structured result.

    video : np.ndarray [T, C, H, W]   multi-channel side-view movie
    question : str                     plain-language mechanistic question
    """
    t_start = time.time()
    video = np.asarray(video, float)
    T, C = video.shape[0], video.shape[1]
    if channels is None:
        channels = ["membrane", "coat"] + (["actin"] if C >= 3 else [])
    has_actin = "actin" in channels
    if A_coat_nm2 is None:
        A_coat_nm2 = np.pi * 60.0 ** 2

    # 1) PERCEPTION: pixels -> geometry(t) with per-frame uncertainty
    meta = dict(nm_per_px=nm_per_px, channels=channels, psf_sigma_nm=psf_sigma_nm,
                peak_photons=peak_photons, movie_id=_hash_movie(video))
    trace = pcp.PerceptionProvider(host=host).extract(video, meta, seed=seed)
    H = trace.arr("H_inv_nm"); Hs = trace.arr("H_sigma_inv_nm")
    depth = trace.arr("depth_nm"); mask = depth >= psf_sigma_nm
    actin_obs = trace.arr("actin_density") if has_actin else None
    actin_sig = trace.arr("actin_sigma") if has_actin else None
    n_resolved = int(mask.sum())

    # 2) INVERSE: full-model posterior over forces + identifiability
    res = inv.run_nested(H, Hs, A_coat_nm2, mask=mask, nlive=nlive, seed=seed,
                         actin_obs=actin_obs, actin_sigma=actin_sig)
    ident = inv.identifiability(res["samples"], res["params"])

    # 3) MECHANISM: evidence ranking + (if needed) disambiguating experiment
    hyps = hypotheses or _question_to_hypotheses(question, has_actin)
    verdict, fits = mech.discriminate(H, Hs, A_coat_nm2, mask=mask,
                                      actin_obs=actin_obs, actin_sigma=actin_sig,
                                      hypotheses=hyps, nlive=nlive, seed=seed)

    # 4) ASSEMBLE with the anti-force-astrology guardrail
    forces = {}
    for name, info in ident.items():
        # a point value is licensed only if the single-shot report says identified
        # AND recovery validation certified this force calibrated
        recovery_ok = name in RECOVERY_CALIBRATED
        identified = bool(info["identified"] and recovery_ok)
        entry = dict(
            units=info["units"],
            posterior_median=info["median"],
            ci68=info["ci68"], ci95=info["ci95"],
            identified=identified,
            single_shot_identified=bool(info["identified"]),
            recovery_calibrated=recovery_ok)
        if identified:
            entry["point_estimate"] = info["median"]
            entry["status"] = "identified"
        else:
            # GUARDRAIL: refuse a point value; return the posterior + why
            entry["point_estimate"] = None
            entry["status"] = "underdetermined"
            reasons = []
            if info.get("degenerate_with"):
                reasons.append("degenerate with " +
                               ", ".join(d["partner"] for d in info["degenerate_with"]))
            if info.get("railed"):
                reasons.append("posterior railed against prior bound (data uninformative)")
            if not info.get("marginal_constrained"):
                reasons.append("posterior ~ prior (no information gain)")
            if info["identified"] and not recovery_ok:
                reasons.append("single-shot posterior looks narrow but recovery "
                               "validation shows this actor is NOT calibrated from "
                               "this observable set (biased); returning posterior, "
                               "not a point value")
            entry["reason"] = "; ".join(reasons) or "not constrained by the data"
        forces[name] = entry

    result = dict(
        question=question,
        forces=forces,
        favored_mechanism=dict(
            favored=verdict["favored"], decisive=verdict["decisive"],
            ln_bayes_factor=verdict["ln_bayes_factor"],
            ranking=verdict["ranking"]),
        uncertainty=dict(
            n_frames=T, n_resolved_frames=n_resolved,
            note=("unresolved frames (cap shallower than the PSF) are down-weighted "
                  "with inflated H uncertainty, not trusted as point values")),
        identifiability={k: dict(identified=v["identified"],
                                 width_ratio=v["width_ratio"],
                                 info_gain_bits=v["info_gain_bits"],
                                 degenerate_with=[d["partner"] for d in v["degenerate_with"]],
                                 railed=v.get("railed", False)) for k, v in ident.items()},
        suggested_experiment=verdict.get("suggested_experiment"),
        provenance=dict(
            movie_sha256_16=meta["movie_id"], channels=channels, has_actin=has_actin,
            nm_per_px=nm_per_px, psf_sigma_nm=psf_sigma_nm, A_coat_nm2=float(A_coat_nm2),
            extractor=trace.extractor, engine="dynesty-nested+identifiability",
            module_versions=version_hashes_of(pcp, inv, mech),
            logz_full_model=res["logz"], runtime_s=round(time.time() - t_start, 2),
            credibility_note=("force point-estimates are returned ONLY for actors the "
                              "recovery-validation gate shows calibrated; all others are "
                              "returned as posteriors flagged underdetermined")),
    )
    return result
