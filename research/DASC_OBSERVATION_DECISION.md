# DASC observation-model decision — 2026-09-23

Task `dasc-observation-model-001`, attempt 1. Independently reviewed; accepted
within the scope stated below. See DASC_OBSERVATION_REVIEW.md.

## Decision

**Park the AP2 single-channel DASC contrast as a test of physical mechanism.**
Keep it as a possible published-result reproduction or detection-sensitivity
benchmark. The primary analysis rules establish how tracks are scored, but do
not independently establish which structures were missed or excluded in each
condition. No raw-movie download or kinetic/force fit follows from this decision.

This is a limit of the proposed comparison with currently verified evidence,
not a finding that AP2 has no biological effect or that intensity data can never
test a specified model. The published phenotype remains published evidence;
we have not reanalyzed it or shown it is an imaging artifact.

## What the published rules actually constrain

Source: [Wang et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7192580/),
retained math-preserving JATS in `metadata/dasc-methods-001/PMC7192580.jats.xml`.
SHA-256: `99c288fd03d3e0ec4d9aba72074d7fcae14bd40b2dbe0952a1e071c4b5bd5e0e`.

| Source locator | Constrained processing choice | What remains unmeasured |
| --- | --- | --- |
| Methods, “Computational flow of DAS analysis,” s4-1 | First statistically significant detection defines track age; intensities rounded to integer arbitrary units; only valid traces enter DASC | Physical initiation time, subthreshold structures, condition-specific detection/validity response |
| Same section | Control tracks determine transition probabilities and one reference D(i,t); control means/SD normalize the three features | Camera gain/noise, bleaching, amount-versus-depth relation, completeness |
| Results, “Validation through perturbation of established CCP initiation and stabilization pathways” | Explicitly says control-derived cluster boundaries were applied to AP2 perturbation tracks | Exact paper-version implementation; Methods step 9 has apparently different repeat-clustering wording |
| Methods, “Data pooling for conditions acquired on different days,” s4-3 | Control intensity CDFs determine one affine transform per day, applied to that day's conditions | Independent instrument calibration; does not establish condition-specific corrections for AP2 |
| Methods s4-1 and applicability discussion | All-track initiation and valid-track class fractions have different denominators; authors use T=451 s for rates | Missing tracks, independent culture/plate structure and residual boundary censoring |

The AP2 control-boundary statement is explicit. Earlier notes that restricted
it to siRNA or said the paper left the AP2 boundary convention entirely unstated
were too narrow. The Methods/implementation discrepancy still needs a pinned
paper-version resolution for an exact reproduction, but is not the main reason
to park the mechanistic comparison.

451 frames at 1 fps have 450 inter-frame intervals. Reproducing the authors'
reported rate convention nevertheless requires their stated T=451 s; these are
different quantities, not a reason to silently replace their denominator.

## A restricted null that could be tested with additional evidence

Let K describe the latent distribution of coat histories and let the observation
process include brightness, background/noise, axial weighting, detection,
linking, validity selection and first-detection alignment.

- **H0, restricted observation change:** WT and mutant share K. Permit only a
  predeclared, bounded brightness transformation and measured noise/background
  changes. Fix the analysis pipeline and constrain its response using controls
  independent of the phenotype being tested. Keep the axial/labeling assumptions
  explicit. A scalar-gain-only version is a narrower null than arbitrary
  time-dependent brightness and cannot represent all observation effects.
- **H1, changed kinetics within the chosen model:** retain those same observation
  constraints, but allow specified assembly/disassembly parameters to differ.
  Rejecting H0 in favor of H1 would concern this restricted kinetic model;
  it would not select actin force, direct AP2 bending or membrane elasticity.

With full detection and a known scalar gain, a time-independent intensity
rescaling cannot change a normalized trace's temporal shape. In real detected
tracks, rescaling can change missed frames, linking, endpoints, validity and
time zero. Consequently, intensity rescaling after tracking does not reproduce
the effect of dimming before detection. A digital dimming/retracking exercise
would be a sensitivity experiment for its specified noise model, not an
independent reconstruction of mutant biology.

If observation constraints become defensible, compare predictions on held-out
movies using a frozen joint score for detection/count coverage and retained
track dynamics, with reference D/features/boundaries fitted on training controls
only. Biological replication must be established separately. No particular
score, threshold or confirmatory p-value is justified by the current evidence.
The already inspected published effect is not an unseen confirmatory target.

## Why a fixed scoring rule alone does not identify the latent change

For a latent track summary x and condition c, write

`f_observed,c(x) = q_c(x) f_K,c(x) / integral[q_c(u) f_K,c(u) du]`,

where q is the probability that a history is detected and retained. This is a
conceptual selection model, not a calibrated detector for this dataset.

Even exact knowledge of the downstream classifier does not determine q. As a
constructive existence example, for any two observed densities p_W and p_M,
choose a shared latent density `f_K = (p_W + p_M)/2` and
`q_c = p_c/(p_W + p_M)` on their combined support. Then `0 <= q_c <= 1`,
the retention probability is 1/2, and conditioning produces p_c exactly.
The two conditions can therefore have different observed distributions with
the same latent distribution if selection is unrestricted. Where both densities
are zero, q can be set to zero. Arbitrary q is not evidence that the actual
detector behaved this way; its purpose is to show why an independently bounded
selection response is needed before identifying latent kinetics.

The separate one-channel amount/depth ambiguity in DASC_COMPARISON.md also
remains. Neither argument establishes that every mechanistic prediction is
equivalent or that the published biological interpretation is false.

## Missing evidence and the next useful research direction

Minimum requirements for reopening this mechanistic branch are: a concrete
kinetic prediction, independently constrained observation nuisance terms and
detection/validity response, verified grouping/censoring, and an analysis version
whose reference/training rules are fixed. Background statistics may be estimated
from raw movies, but the present audit has not done that and those statistics
alone would not measure all missing structures or separate coat amount/depth.

A two-movie I/O check would establish readability, not resolve these requirements.
Do not build a tracker, a new approval registry or a 19 GB reproduction pipeline
as a substitute for a discriminating prediction.

Return to the broad theory/data assessment. The next bounded task should read
the full primary mechanics models already in the map (membrane tension/shape and
actin-network assistance), extract their equations and control assumptions, and
ask for one observable prediction on which the models differ under matched
constraints. Nested parameter choices and different imposed force histories
must not be relabeled distinct biological mechanisms. Identify the measurement
needed before any new archive search or model implementation.

## Review and implementation status

Source reconciliation is complete (DASC_ANALYSIS_RULES.md). The lead corrected
earlier section locators and the AP2 control-boundary summary. Author code could
be viewed at a mutable URL, but local retrieval did not produce a pinned
paper-version snapshot; exact implementation remains unresolved. This access
failure is distinct from the missing independent observation calibration.

The independent scientific reviewer accepted this decision without required
correction (DASC_OBSERVATION_REVIEW.md), including the selection construction
and restricted scope. The separate tag-only force-permission correction was
also accepted within its API-local scope (OBSERVABLE_PERMISSION_REVIEW.md).
Stale RESEARCH.md and two historical output metadata claims were corrected;
all numerical payloads were preserved and were not revalidated. None of this
calibrates DASC or establishes a global guard on direct inverse calls.
