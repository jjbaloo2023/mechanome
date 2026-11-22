"""Run a microscopy movie through perception, inference, and mechanism ranking.

The flow in analyze() is pixels -> geometry -> posterior -> mechanism -> report.
_report_forces() requires completed sampling, single-run identifiability,
and successful synthetic recovery calibration for point estimates. Other forces
keep their posterior intervals and an explanation of what remains unknown.

Input movies use [frame, channel, height, width] order. Output dictionaries keep
forces, uncertainty, identifiability, suggested experiments, and provenance.
"""

from __future__ import annotations

import hashlib
import time
import dataclasses

import numpy as np

from . import perception
from . import inverse
from . import mechanism
from .schemas import version_hashes_of

# The historical active-force calibration predates the geometry validity gate.
# A single successful recovery is not a current-version calibration grid.
# Keep point estimates disabled until that qualification is recorded and reviewed.
RECOVERY_CALIBRATED = set()


def _hash_movie(movie):
    return hashlib.sha256(np.ascontiguousarray(movie).tobytes()).hexdigest()[:16]


def _question_to_hypotheses(question):
    """Route question keywords to a hypothesis set; callers can supply their own."""
    q = (question or "").lower()
    full = ["tension_only", "wedge_only", "actin_only", "wedge+actin"]
    if "actin" in q and (
        "or" in q or "vs" in q or "versus" in q or "wedge" in q or "curvature" in q
    ):
        return ["wedge_only", "actin_only", "wedge+actin"]
    return full


def _report_forces(identifiability: dict, *, stopped_early: bool = False,
                   calibration_supported: bool = False) -> dict:
    """Require completed sampling, identifiability, and recovery calibration."""
    forces = {}
    for name, info in identifiability.items():
        recovery_ok = name in RECOVERY_CALIBRATED and calibration_supported
        identified = bool(info["identified"] and recovery_ok and not stopped_early)
        entry = dict(
            units=info["units"],
            posterior_median=info["median"],
            ci68=info["ci68"],
            ci95=info["ci95"],
            identified=identified,
            single_shot_identified=bool(info["identified"]),
            recovery_calibrated=recovery_ok,
            sampling_stopped_early=stopped_early,
        )
        if identified:
            entry["point_estimate"] = info["median"]
            entry["status"] = "identified"
        else:
            entry["point_estimate"] = None
            entry["status"] = "underdetermined"
            reasons = []
            if stopped_early:
                reasons.append("sampling reached its limit; posterior is provisional")
            if not calibration_supported:
                reasons.append("observation context is outside the declared synthetic recovery calibration")
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
                    "synthetic recovery does not support a point estimate "
                    "for this parameter"
                )
            entry["reason"] = "; ".join(reasons) or "not constrained by the data"
        forces[name] = entry

    return forces


def _calibration_issues(context, video, nm_per_px, psf_sigma_nm, peak_photons, area, has_actin):
    """Check declared synthetic conditions; this does not certify real images."""
    issues = []
    if not RECOVERY_CALIBRATED:
        issues.append("current extraction/inference revision awaits recovery qualification")
    if context.input_kind != "synthetic" or context.calibration_id != "synthetic_renderer_v1":
        issues.append("no supported synthetic calibration declaration")
    if context.coverage is not None:
        issues.append("custom coverage has not passed recovery calibration")
    if context.actin_force_scale_pN != inverse.sm.ACTIN_CALIB_PN:
        issues.append("changed fluorescence-to-force scale")
    if video.shape[2:] != (128, 128) or (nm_per_px, psf_sigma_nm, peak_photons) != (2.0, 18.0, 220.0):
        issues.append("imaging conditions differ from the recovery grid")
    if not np.isclose(area, np.pi * 60.0**2):
        issues.append("coat area differs from the recovery grid")
    if not has_actin:
        issues.append("no calibrated actin channel")
    return issues


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
    context=None,
):
    """Run the full pixels->forces->mechanism pipeline; return a structured result.

    video : np.ndarray [T, C, H, W]   multi-channel side-view movie
    question : str                     plain-language mechanistic question
    """
    t_start = time.time()
    video = np.asarray(video, float)
    if video.ndim != 4 or any(size == 0 for size in video.shape):
        raise ValueError(
            "video must have nonempty [frame, channel, height, width] axes"
        )
    n_frames, n_channels = video.shape[0], video.shape[1]
    if n_frames != inverse.FIXED["T"]:
        raise ValueError(
            f"analyze requires {inverse.FIXED['T']} frames; got {n_frames}"
        )
    if not np.all(np.isfinite(video)):
        raise ValueError("video must contain only finite values")
    if channels is None:
        if n_channels not in (2, 3):
            raise ValueError(
                "provide channel names for movies with other than 2 or 3 channels"
            )
        channels = ["membrane", "coat"] + (["actin"] if n_channels == 3 else [])
    if (
        len(channels) != n_channels
        or len(set(channels)) != n_channels
        or channels[0] != "membrane"
        or "coat" not in channels
    ):
        raise ValueError(
            "channels must be unique, match the movie, and include membrane first and coat"
        )
    has_actin = "actin" in channels
    if A_coat_nm2 is None:
        A_coat_nm2 = np.pi * 60.0**2
    for name, value in (("nm_per_px", nm_per_px), ("psf_sigma_nm", psf_sigma_nm),
                        ("peak_photons", peak_photons), ("A_coat_nm2", A_coat_nm2)):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    context = context or inverse.ObservationContext()
    context.coverage_array(n_frames)
    calibration_issues = _calibration_issues(
        context, video, nm_per_px, psf_sigma_nm, peak_photons, A_coat_nm2, has_actin
    )

    # 1) PERCEPTION: pixels -> geometry(t) with per-frame uncertainty
    metadata = dict(
        nm_per_px=nm_per_px,
        channels=channels,
        psf_sigma_nm=psf_sigma_nm,
        peak_photons=peak_photons,
        movie_id=_hash_movie(video),
        input_kind=context.input_kind,
    )
    trace = perception.PerceptionProvider(host=host).extract(video, metadata, seed=seed)
    curvature = trace.arr("H_inv_nm")
    curvature_sigma = trace.arr("H_sigma_inv_nm")
    depth_nm = trace.arr("depth_nm")
    resolved_frames = (depth_nm >= psf_sigma_nm) & trace.arr("geometry_valid").astype(bool)
    actin_obs = trace.arr("actin_density") if has_actin else None
    actin_sigma = trace.arr("actin_sigma") if has_actin else None
    n_resolved = int(resolved_frames.sum())
    if not n_resolved:
        return dict(
            question=question, analysis_status="unsupported", forces={}, identifiability={},
            favored_mechanism=dict(favored="UNDETERMINED", decisive=False, ranking=[],
                                   ln_bayes_factor=None, incomplete_fits=[]),
            uncertainty=dict(n_frames=n_frames, n_resolved_frames=0,
                             note="no valid resolved geometry; sampling was not run"),
            suggested_experiment=dict(observable="resolved sub-hemisphere membrane geometry"),
            provenance=dict(movie_sha256_16=metadata["movie_id"],
                            observation_context=dataclasses.asdict(context),
                            calibration_issues=calibration_issues, extractor=trace.extractor,
                            extraction_quality=[f.quality_reason for f in trace.frames]),
        )

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
        context=context,
    )
    identifiability = inverse.identifiability(posterior["samples"], posterior["params"])

    # 3) MECHANISM: evidence ranking + (if needed) disambiguating experiment
    selected_hypotheses = (
        _question_to_hypotheses(question) if hypotheses is None else hypotheses
    )
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
        context=context,
    )

    # 4) Report only what the data and recovery validation support.
    forces = _report_forces(identifiability, stopped_early=posterior["stopped_early"],
                            calibration_supported=not calibration_issues)
    if calibration_issues or posterior["stopped_early"]:
        verdict["favored"], verdict["decisive"] = "UNDETERMINED", False
        verdict.setdefault("suggested_experiment", dict(
            observable="independent calibration and validated observation model",
            rationale="conditional fit scores do not validate this observation context",
        ))

    result = dict(
        question=question,
        analysis_status="exploratory" if calibration_issues else (
            "provisional" if posterior["stopped_early"] else "synthetic_model_conditional"),
        forces=forces,
        favored_mechanism=dict(
            favored=verdict["favored"],
            decisive=verdict["decisive"],
            ln_bayes_factor=verdict["ln_bayes_factor"],
            ranking=verdict["ranking"],
            incomplete_fits=verdict["incomplete_fits"],
            numerical_gap_lower_bound=verdict["numerical_gap_lower_bound"],
        ),
        uncertainty=dict(
            n_frames=n_frames,
            n_resolved_frames=n_resolved,
            extraction_quality=[f.quality_reason for f in trace.frames],
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
            full_model_stopped_early=posterior["stopped_early"],
            observation_context=dataclasses.asdict(context),
            calibration_issues=calibration_issues,
            coverage_source="fixed_synthetic_ramp" if context.coverage is None else "supplied_conditional_trace",
            extracted_coat_coverage=trace.arr("coat_coverage").tolist(),
            runtime_s=round(time.time() - t_start, 2),
            credibility_note=(
                "point estimates require completed sampling, identifiability, "
                "and synthetic recovery calibration under the model assumptions"
            ),
        ),
    )
    return result
