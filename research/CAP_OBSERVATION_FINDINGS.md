# Finite-window cap fitting: ordering survives, values depend on the window

Independent review accepts corrected numerical attempt 2 for this synthetic
observation question. All 48 cap fits completed and all 12 comparisons using
fixed physical windows preserved decreasing fitted curvature across the three
sampled coat areas. Attempt 1 is rejected and retained because its radius-to-area
coordinate map was wrong; none of its fit values supports these findings.

The corrected experiment reuses six accepted passive membrane shapes, with
x=0.5,1,2 and c_repo*ell=0.02,0.6. It fits a spherical-cap height function with
a free vertical offset, using either uniform radial or uniform material-area
weighting. This is deterministic vertical least squares, not the LocMoFit
localization likelihood or a biological measurement model.

| Physical fit radius / ell | Fitted curvature above pointwise apex |
| ---: | ---: |
| 0.10 | 0.0528–0.0625% |
| 0.25 | 0.3307–0.3912% |
| 0.40 | 0.8494–1.004% |
| Whole nominal coat | 1.305–27.644% |

The whole-coat fits use different physical supports across areas. Their values
illustrate dependence on how curvature is summarized; they are not fixed-window
comparisons. The earlier 58% difference was between the coat-area mean and the
apex, a different quantity from fitted cap curvature.

A small-window derivation predicts fitted-curvature bias proportional to the
square of the window radius. Its prediction agrees with all twelve smallest-
window fits within 0.0451% relative error. Shrinking the window reduces this
bias, but the linearized amplification of height perturbations grows as the
inverse square of the radius. That is a deterministic conditioning statement,
not an experimental noise estimate or an optimal microscope window.

Validation includes exact-sphere and flat controls, hash-verified inputs and
exact frozen source/design copies. The maximum inverse-coordinate round-trip
error is 2.49e-14. An independent 401-node objective/normal-equation check at
all stored 201-node optima passes: maximum normalized stationarity residual
1.78e-5 versus the declared 1e-3 gate. This does not claim reoptimized parameter
convergence. All fits are interior and no worse than the explicit flat candidate.
Two targeted corrected-version tests passed; after making their clock fixed
for reproducibility, both passed again in 0.82 seconds. No BVP was rerun.

The corrected run finished at 03:06:54 UTC, before the 03:10:12 computation
cutoff. Results were written exclusively per case before aggregation. The UTC
guard prevents starting a late fit; it does not interrupt an optimizer already
running. The invalid first run remains a documented failed attempt, and its
controls did not detect the coordinate bug. An explicit lead source-clearance
gate was used for the correction.

Stop the synthetic sweep here. Before an empirical comparison, identify the
actual LocMoFit observation likelihood, spatial sampling, fitted support and
parameter conventions from cached primary methods and a pinned public source
implementation. Keep missing covariance/calibration explicit. The present result
supports neither a biological mechanism nor global monotonicity or stability.

Evidence: [independent review](CAP_OBSERVATION_REVIEW.md),
[theory](CAP_OBSERVATION_THEORY.md), [accepted results](cap_observation_results_002.json),
[independent checks](cap_observation_lead_checks.json),
[rejected attempt](cap_observation_results_001.json).
