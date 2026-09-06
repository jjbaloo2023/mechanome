"""Run a microscopy movie through perception, inference, and mechanism ranking.

The flow in analyze() is pixels -> geometry -> posterior -> mechanism -> report.
_report_forces() enforces the reporting rule: a point estimate needs both
single-run identifiability and successful recovery calibration. Other forces
keep their posterior intervals and an explanation of what remains unknown.

Input movies use [frame, channel, height, width] order. Output dictionaries keep
forces, uncertainty, identifiability, suggested experiments, and provenance.
"""

from __future__ import annotations

import hashlib
import time

import numpy as np

from . import perception
from . import inverse
from . import mechanism
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


def _question_to_hypotheses(question):
    """Map a plain-language question to the hypothesis set to compare.

    Kept deliberately simple/transparent (keyword routing); an LLM orchestrator
    can override by passing `hypotheses=` explicitly. The point is that the
    physics/evidence machinery is fixed and auditable — only the hypothesis
    SELECTION is language-driven.
    """
    q = (question or "").lower()
    full = ["tension_only", "wedge_only", "actin_only", "wedge+actin"]
    if "actin" in q and (
        "or" in q or "vs" in q or "versus" in q or "wedge" in q or "curvature" in q
    ):
        return ["wedge_only", "actin_only", "wedge+actin"]
    return full


def _report_forces(identifiability: dict) -> dict:
    """Allow point estimates only for identified, recovery-calibrated forces."""
    forces = {}
    for name, info in identifiability.items():
        # a point value is licensed only if the single-shot report says identified
        # AND recovery validation certified this force calibrated
        recovery_ok = name in RECOVERY_CALIBRATED
        identified = bool(info["identified"] and recovery_ok)
        entry = dict(
            units=info["units"],
            posterior_median=info["median"],
            ci68=info["ci68"],
            ci95=info["ci95"],
            identified=identified,
            single_shot_identified=bool(info["identified"]),
            recovery_calibrated=recovery_ok,
        )
        if identified:
            entry["point_estimate"] = info["median"]
            entry["status"] = "identified"
        else:
            # GUARDRAIL: refuse a point value; return the posterior + why
            entry["point_estimate"] = None
            entry["status"] = "underdetermined"
            reasons = []
            if info.get("degenerate_with"):
                reasons.append(
                    "degenerate with "
                    + ", ".join(d["partner"] for d in info["degenerate_with"])
                )
            if info.get("railed"):
                reasons.append(
                    "posterior railed against prior bound (data uninformative)"
                )
            if not info.get("marginal_constrained"):
                reasons.append("posterior ~ prior (no information gain)")
            if info["identified"] and not recovery_ok:
                reasons.append(
                    "single-shot posterior looks narrow but recovery "
                    "validation shows this actor is NOT calibrated from "
                    "this observable set (biased); returning posterior, "
                    "not a point value"
                )
            entry["reason"] = "; ".join(reasons) or "not constrained by the data"
        forces[name] = entry

    return forces


def analyze(
    video,
    question=None,
    *,
    nm_per_px=2.0,
    psf_sigma_nm=18.0,
    peak_photons=220.0,
    channels=None,
    A_coat_nm2=None,
    host=None,
    hypotheses=None,
    nlive=200,
    seed=0,
    verbose=False,
):
    """Run the full pixels->forces->mechanism pipeline; return a structured result.

    video : np.ndarray [T, C, H, W]   multi-channel side-view movie
    question : str                     plain-language mechanistic question
    """
    t_start = time.time()
    video = np.asarray(video, float)
    n_frames, n_channels = video.shape[0], video.shape[1]
    if channels is None:
        channels = ["membrane", "coat"] + (["actin"] if n_channels >= 3 else [])
    has_actin = "actin" in channels
    if A_coat_nm2 is None:
        A_coat_nm2 = np.pi * 60.0**2

    # 1) PERCEPTION: pixels -> geometry(t) with per-frame uncertainty
    metadata = dict(
        nm_per_px=nm_per_px,
        channels=channels,
        psf_sigma_nm=psf_sigma_nm,
        peak_photons=peak_photons,
        movie_id=_hash_movie(video),
    )
    trace = perception.PerceptionProvider(host=host).extract(video, metadata, seed=seed)
    curvature = trace.arr("H_inv_nm")
    curvature_sigma = trace.arr("H_sigma_inv_nm")
    depth_nm = trace.arr("depth_nm")
    resolved_frames = depth_nm >= psf_sigma_nm
    actin_obs = trace.arr("actin_density") if has_actin else None
    actin_sigma = trace.arr("actin_sigma") if has_actin else None
    n_resolved = int(resolved_frames.sum())

    # 2) INVERSE: full-model posterior over forces + identifiability
    posterior = inverse.run_nested(
        curvature,
        curvature_sigma,
        A_coat_nm2,
        mask=resolved_frames,
        nlive=nlive,
        seed=seed,
        actin_obs=actin_obs,
        actin_sigma=actin_sigma,
    )
    identifiability = inverse.identifiability(posterior["samples"], posterior["params"])

    # 3) MECHANISM: evidence ranking + (if needed) disambiguating experiment
    selected_hypotheses = hypotheses or _question_to_hypotheses(question)
    verdict, _fits = mechanism.discriminate(
        curvature,
        curvature_sigma,
        A_coat_nm2,
        mask=resolved_frames,
        actin_obs=actin_obs,
        actin_sigma=actin_sigma,
        hypotheses=selected_hypotheses,
        nlive=nlive,
        seed=seed,
    )

    # 4) Report only what the data and recovery validation support.
    forces = _report_forces(identifiability)

    result = dict(
        question=question,
        forces=forces,
        favored_mechanism=dict(
            favored=verdict["favored"],
            decisive=verdict["decisive"],
            ln_bayes_factor=verdict["ln_bayes_factor"],
            ranking=verdict["ranking"],
        ),
        uncertainty=dict(
            n_frames=n_frames,
            n_resolved_frames=n_resolved,
            note=(
                "unresolved frames (cap shallower than the PSF) are excluded "
                "from the likelihood, not trusted as point values"
            ),
        ),
        identifiability={
            k: dict(
                identified=v["identified"],
                width_ratio=v["width_ratio"],
                info_gain_bits=v["info_gain_bits"],
                degenerate_with=[d["partner"] for d in v["degenerate_with"]],
                railed=v.get("railed", False),
            )
            for k, v in identifiability.items()
        },
        suggested_experiment=verdict.get("suggested_experiment"),
        provenance=dict(
            movie_sha256_16=metadata["movie_id"],
            channels=channels,
            has_actin=has_actin,
            nm_per_px=nm_per_px,
            psf_sigma_nm=psf_sigma_nm,
            A_coat_nm2=float(A_coat_nm2),
            extractor=trace.extractor,
            engine="dynesty-nested+identifiability",
            module_versions=version_hashes_of(perception, inverse, mechanism),
            logz_full_model=posterior["logz"],
            runtime_s=round(time.time() - t_start, 2),
            credibility_note=(
                "force point-estimates are returned ONLY for actors the "
                "recovery-validation gate shows calibrated; all others are "
                "returned as posteriors flagged underdetermined"
            ),
        ),
    )
    return result
