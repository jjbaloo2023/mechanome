# Independent DASC design review — 2026-09-22

Task `dasc-design-review-001`, attempt 1. Scope: adversarial read-only review of
`DASC_COMPARISON.md`, `DASC_METHODS.md`, `dasc_pilot_inputs.json`, the retained
primary JATS, the retained Figshare manifest, and the current observable router
and BioTISR-SIM ingester. No network access, movie payload, fitting, or source
implementation change was used.

## Disposition

**Accept within the stated engineering/measurement scope, subject to the two
source/contract corrections below.** The central decision is supported: the
same-date AP2-alpha WT versus K57E/Y58E PIP2-binding-defective rescue is a
better-bounded candidate than CALM depletion for a future tracking and
measurement feasibility exercise. It is not presently a force comparison or a
physical-mechanism test. No raw download is justified by the current evidence.

This acceptance does not imply that no mechanism could ever be tested. A future
study could test a mechanism that makes a frozen prediction in an actually
calibrated observable. The deposited single-channel intensity movies and the
current unrestricted observation models do not supply such a discriminant.

## Required corrections

1. **Correct one significance annotation in `DASC_METHODS.md`.** Its AP2
   summary says “CCP% fell 27%*.” The retained primary JATS Table 1 reports
   alpha-PIP2 CCP% `down 27%***` (`p < 0.001`). The same row reports initiation
   `up 36%***`, CCP rate `up 27%**`, and median CCP lifetime `down *`; those
   other annotations are faithful. The biological direction and design choice
   are unaffected.
2. **Do not treat the current observable tag as scientific permission.** In
   `classify_observable.py`, any object or dictionary carrying the literal tag
   `2_epitirf_depth` or `3_superres_curvature` is routed to the force inverse.
   There is no check for units, source measurement, calibration identity,
   calibration status, uncertainty, temporal registration, or whether the
   stated forward model is identifiable. This is a real fail-open gap, not only
   a documentation issue. `ingest_biotisr_sim.py` demonstrates it: an unverified
   pixel-size assumption and an equivalent-disc punctum footprint are converted
   to `H_proxy = 1/R_proj`, tagged `3_superres_curvature`, and thereby permitted,
   even though the ingester itself says that it does not establish annular
   structure or calibrated 3-D curvature. The module header's claim that
   TIRF-SIM is “the input the force inverse actually needs” is therefore stronger
   than its implemented measurement supports.

The lead's bounded probe in `dasc_capability_audit.json` reproduces this behavior:
both richer tags return `force_inference_allowed: true` even when their supplied
provenance explicitly marks pixel size, frame interval, and observation-model
validation false. No inverse was run.

The minimum next implementation should separate descriptive classification
from authorization. Classification should report intensity, depth proxy, or
projected geometry and route all three to measurement QA by default.
`assert_force_permitted` should require a pinned, model-specific calibration
and scientific-review artifact controlled outside the caller's dataset object,
including geometry definition and units, calibration identity and status,
uncertainty model, applicable inverse/model version, and identifiability scope.
A new caller-supplied boolean would merely rename the existing tag-only gap and
is not an acceptable gate. Add small synthetic unit tests showing that a bare
tag, explicitly unverified provenance, and the current BioTISR proxy are
refused; test acceptance only against a fixture representing an independently
registered review artifact. That work is smaller and more informative than
downloading either DASC movie, and it does not require changing the force model.

## Evidence checks

The compact illustration

`I(t) = g(t) N(t) exp(-z(t)/d) + noise(t)`

correctly establishes an intensity/amount/depth non-identifiability in its
stated simplified model. With noise fixed, `z -> z + delta` and
`N -> N exp(delta/d)` leave `I` unchanged. This is an existence result about an
unconstrained one-channel observation model; it does not show that every
mechanistic prediction is observationally equivalent. `DASC_COMPARISON.md`
states that limit correctly.

The observation-only/shared-latent-kinetics and changed-latent-kinetics rows are
acceptable as restricted operational hypotheses. They are not complete or
mutually exhaustive biological theories. The proposed failure criterion only
becomes testable after the gain/noise/bleaching/detection model, latent-kinetics
family, grouping, and held-out scoring rule are fixed. Rejection of the first
row would support condition-dependent kinetics within that restricted model
class; it would not identify AP2-mediated bending, actin force, cooperativity,
or membrane elasticity. The comparison note preserves that boundary.

Selection, censoring, and grouping are handled materially correctly. The paper
uses all trackable structures for initiation but valid tracks for CCP fraction;
the mutant is dimmer, so detection, consecutive-gap, diffraction-limited, and
validity rules can change the denominators by condition. Track endpoints are
not physical nucleation or scission. The review correctly requires retention of
incomplete tracks and endpoint flags, separate all-track and valid-track
summaries, movie-level grouping, and batch limits. Nineteen and twenty files do
not establish independent cultures, and hundreds of thousands of tracks do not
replace biological replication. Control-derived boundaries must be frozen;
condition-specific refitting would destroy label comparability.

The primary-source claims checked against the math-preserving JATS are otherwise
faithful. DASC Equations 1--6 construct intensity traces, the disassembly-risk
series, and features `d1`--`d3`; they do not measure force or geometry. The
methods state that more than 200,000 traces, typically from more than 20 movies,
are needed for stable transition probabilities, while the reported experiments
collected at least 19 movies per condition. Table 1 gives 19 WT and 20 mutant
movies and the already published AP2 effects. Consequently, recovering the
direction of the AP2 result is a reproduction target, not a blind prediction or
independent validation.

The two-file input is consistently marked `proposal_only_not_download_authorization`,
`downloaded: false`, and “Conditional engineering I/O feasibility.” Its ordinal
lexicographic rule does select the recorded Cell10 files; their sizes sum to
970,016,272 bytes, below the 1 GiB cap. The full-condition totals also reproduce
from the retained manifest: 19 WT files/9,040,952,265 bytes and 20 mutant
files/10,238,817,152 bytes. A two-file run could establish decompression,
streaming, headers, and output schema only. It could not validate DASC, estimate
a condition effect, or establish representativeness. The JSON's `supplied_md5`
and `computed_md5` values are Figshare manifest fields and have not been locally
verified against movie bytes; any future report should label them that way.

## Unresolved before any biological comparison

Independent culture/plate structure, exposure duration, raw shape/dtype,
detector and background behavior, bleaching, saturation, cell masks/areas,
cmeAnalysis/DASC version and training conventions, and a calibrated validity
response remain unresolved. So do a predeclared estimand, held-out scoring rule,
minimum movie/batch support, exclusion rules, and sensitivity thresholds. These
are reasons to stop at design and contract hardening now, not reasons to claim
that all future mechanistic tests are impossible.
