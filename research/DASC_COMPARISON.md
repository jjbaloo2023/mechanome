# DASC comparison decision — 2026-09-22

2026-09-23 update: DASC_OBSERVATION_DECISION.md completes the follow-up. The AP2
contrast is parked as a physical-mechanism test; reproduction and sensitivity
uses remain possible. The proposed two-file I/O check is not active work.

Task `dasc-comparison-design-001`, attempt 1. Independently reviewed within the
engineering/measurement scope; see DASC_DESIGN_REVIEW.md. Lead corrected the
source significance annotation and closed automatic tag-only force permission.
A calibrated, independently reviewed authorization path remains unimplemented.

## Decision

Choose the **AP2-alpha WT versus PIP2-binding-defective K57E/Y58E rescue**
contrast on 2019-06-02 as the better-defined candidate for a future measurement
and tracking feasibility check. Defer CALM knockdown: its broad loss of function
and compensation add interpretations that this initial comparison cannot resolve.
This chooses an experiment to assess, not an AP2-based explanation of pit bending.

**Physical-mechanism discrimination is currently unresolved.** The deposited
single-channel clathrin movies do not supply measured membrane geometry, actin
force or direct scission events. A DASC classification change alone does not
separate altered coat assembly, adaptor engagement, bending mechanics and
condition-dependent observation/selection. Do not fit the existing force inverse
to these intensities or treat DASC class labels as mechanism ground truth.

**Do not download the raw cohort yet.** The next implementation priority is to
make the observation/calibration boundary explicit, then determine whether an
observation-model feasibility check provides enough information to justify data
processing. The known mutant phenotype is a reproduction target, not a new
prediction or blind validation experiment.

## Evidence that constrains the comparison

- Verified deposit/sidecars: 19 WT and 20 mutant movie files from the same date,
  nominal 1 frame/s, 451 frames. File counts do not establish 39 independent
  biological replicates or paired cells. Culture/plate structure is unresolved.
- Primary text: [Wang et al., eLife 53686, PMC7192580](https://pmc.ncbi.nlm.nih.gov/articles/PMC7192580/),
  Results “Validation through perturbation of established CCP initiation and
  stabilization pathways,” Figure 3; Methods “Computational flow of DAS analysis.”
  The mutant signal is dimmer and the validity
  rule changes which structures contribute. Initiation uses all trackable
  structures; CCP fraction uses valid tracks. These denominators must be kept
  separate. DASC's CCP class includes events without demonstrated scission.
- The paper's applicability discussion calls for roughly 20 movies and at least
  200,000 traces per condition to estimate its risk function and movie variation.
  One movie per condition cannot substantiate a DASC effect estimate.
- The separate EPI/TIRF experiment yields a normalized cohort depth proxy. It
  does not provide same-pit absolute curvature or a mutant/control geometry join.
  A shared pit identity with S-BIAD566 is not required for every perturbation test,
  but an explicit forward prediction in the available observable is required.

Detailed source audit: [DASC_METHODS.md](DASC_METHODS.md). Access to the primary
text was recovered through PMC after the lead's earlier eLife reader returned
403. No paper effect size is treated as an independent observation from the
underlying deposited movies.

## Competing explanations and the missing discriminant

The following is an operational measurement question, not a claim that two
complete biological theories have been identified:

| Restricted explanation | Prediction under stated assumptions | Evidence required before a test |
| --- | --- | --- |
| Observation/selection change with shared latent coat kinetics | Independently constrained gain/noise, bleaching and detection differences applied to shared kinetics reproduce the observed track/class shifts | Condition-specific acquisition/noise controls, calibrated detection/validity response and a fixed validated analysis pipeline |
| Altered latent coat assembly/disassembly dynamics | The first explanation fails predictively under those constraints; a model permitting different kinetic transition rates improves held-out movie predictions | The same observation controls, enough independent movies/batches, explicit kinetic models and a frozen comparison rule |

These alternatives overlap when the observation model is unconstrained. An
effect that survives one intensity-matching rule would not prove a molecular
mechanism: intensity itself can mediate the biological perturbation, and matching
may remove real effects or introduce selection. A digital dimming exercise would
test sensitivity to a specified imaging model, not recreate the mutant biology.
Rejecting the restricted first explanation would not select actin, cooperativity
or a membrane-elasticity model.

For a compact illustration, assume background-subtracted one-channel TIRF obeys

`I(t) = g(t) N(t) exp(-z(t)/d) + noise(t)`.

Here `N` is fluorescent coat amount, `z` an effective axial position, `d` field
depth and `g` gain/brightness/bleaching. This is a simplified observation model,
not a validated description of this deposit. Even without noise, for any allowed
shift `delta(t)`, replacing `z` by `z + delta` and `N` by `N exp(delta/d)` leaves
the intensity unchanged. Thus an unconstrained intensity trace alone cannot
identify amount versus depth; force adds further model assumptions. The example
does not claim that all possible kinetic/physical theories make equal predictions.

## Required data contract and comparison controls

Retain condition/date/movie/track/frame identities, source hashes, raw and
background-corrected intensity with units, detection uncertainty, image bounds,
segmentation area, gap/validity flags, first/last-frame contact and exclusions.
Frame indices 0–450 at nominal 1 s spacing span 450 inter-frame intervals; do not
silently substitute this span for the authors' acquisition-duration convention
when computing rates. Record and justify the exposure duration used.

Preserve incomplete tracks and endpoint uncertainty. Birth/death of a detected
track is not physical nucleation/scission. Report all-track and valid-track
counts, coverage, brightness and missingness by condition before any label rate.
Track IDs are local to a movie. Group fitting/splitting/uncertainty at least by
movie and retain batch limits; thousands of tracks are not thousands of cultures.
Do not train condition-specific cluster labels and compare them as if fixed.
Any claimed reproduction must verify author training/boundary conventions from
the pinned implementation before scoring.

No confirmatory p-value or DASC reproduction threshold is specified now: the
necessary observation calibration and validated implementation are missing.
Before an inferential run, freeze hypotheses, metrics, thresholds, exclusions,
grouping, parameter constraints, training data and sensitivity checks. Do not
tune them until a known published effect is recovered.

## Existing software and minimum resource cost

Read-only inspection on 2026-09-22:

| Component | Available behavior | Gap for this comparison |
| --- | --- | --- |
| `validation/realdata/ingest_cme_mat.py` | Reads lifetime-binned cohort averages and envelopes from existing cmeAnalysis MAT results | No such files deposited; cohort averages lose per-track/cell information needed here |
| `validation/tracking.py` | LoG detection and greedy linking for synthetic field movies | Photon thresholds, channel metadata and scale assume the simulator; no validated DASC-camera adapter or per-track intensity/validity contract |
| `validation/realdata/ingest_ome_tiff.py` | Paired single-timepoint OME-TIFF reader | Different acquisition/schema; `tifffile` is absent from the current venv |
| `validation/realdata/classify_observable.py` | Describes measurement families and now refuses automatic force permission for every tag | Pre-fix depth/super-resolution permission is preserved in dasc_capability_audit.json; no calibrated model-specific authorization path exists yet |
| `validation/realdata/epitirf_depth_model.py` | Synthetic cap-to-ratio forward model with default penetration depth | Instrument assumptions and geometry do not establish calibration for DASC or convert the WT/mutant single-channel data into depth |

NumPy/SciPy/pandas are available. `tifffile`, scikit-image, trackpy, OpenCV and
torch were not found in the venv; MATLAB/Octave were not found on PATH. No
installation or model execution was attempted. Eight logical CPUs and about
434 GB free disk were reported; RAM query was unavailable. This is an inventory,
not a performance estimate or permission to process the full dataset.

The AP2 cohort totals **19,279,769,417 compressed bytes** (~19.28 GB decimal).
For a conditional engineering-only I/O check, the lexically first filenames in
each condition total **970,016,272 bytes**; exact entries/checksums are frozen in
`dasc_pilot_inputs.json`. Choosing these names is arbitrary and reproducible,
not representative biological sampling. The file records are a proposal, not a
download queue. Cap any separately justified future two-file I/O check at 1 GiB
compressed input. Such a check can establish file readability/streaming and
metadata only; it cannot estimate or validate DASC class fractions.

Uncompressed dimensions, dtype, memory use and runtime are unverified. A streaming
implementation must inspect headers, set explicit output/memory caps and stop if
they are exceeded; do not guess full-stack feasibility from compressed size.
The current decision needs no user input, new dependency or movie payload.
