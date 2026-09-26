# DASC analysis-source audit — dasc-analysis-source-001

**Scope and timing.** Start was not captured; lead dispatched after
2026-09-23T00:01Z. Earliest verified local tool time is
2026-09-22T20:04:12-04:00; corrected end time is
2026-09-22T20:07:20-04:00. This is a source audit only: no movie/raw-data
download, execution, fit, installation, or current-branch substitution was
performed.

## Answer

**No.** The published rules constrain a *reproduction-style DASC comparison*
of AP2 WT and K57E/Y58E, but do not independently constrain brightness or
selection enough to identify a change in latent coat kinetics from a change in
observation/selection. They support a fixed-control classifier sensitivity
test, conditional on reproducing the authors' acquisition and analysis
conventions. They do not provide an independent calibration of condition-wise
gain, background, camera/noise, bleaching, detection probability, or the
dim-track validity response. Nor do they map the deposited movies to culture,
plate, transduction/sort, or biological-replicate identities.

This is not a claim that no AP2 kinetic effect exists. It is the narrower
identifiability result: with these sources, a WT/mutant DASC difference can be
consistent with altered kinetics, but the stated observation alternative is not
independently restricted enough to test that explanation against it.

## What the primary paper fixes

The retained math-preserving JATS source is Wang et al., *eLife* 2020,
DOI [10.7554/eLife.53686](https://doi.org/10.7554/eLife.53686), section
`s4-1`, **“Computational flow of DAS analysis.”** It says to obtain intensity
traces with cmeAnalysis, count all tracks for CS initiation, define valid tracks
as always diffraction-limited and without consecutive gaps, and use the valid
subset for DAS/classification. It explicitly uses `T = 451 s` in the published
CS-initiation-rate convention. This convention should not be silently replaced
by a 450-inter-frame interpretation of 451 nominal frames.

The paper reports intensity fluctuations arising from low SNR, triskelion
turnover, stochastic bleaching, camera noise, and TIRF-field membrane
fluctuation (Results, **“Disassembly Asymmetry Score Classification (DASC): a
new method to analyze CCP growth and stabilization”**). Those are acknowledged
contributors, not measured controls or a transfer function. High background is
illustrated for outliers. Neither that illustration nor the algorithm is an
independent background/noise calibration.

For AP2, Results, **“Validation through perturbation of established CCP
initiation and stabilization pathways,”** states that the clustering boundaries were determined from
control/WT and applied to the PIP2-binding-defective K57E/Y58E condition. Thus
the published AP2 contrast did not justify its reported class difference by
retraining a mutant-specific boundary. This is a useful fixed-boundary rule for
a reproduction check.

There is a source-text tension that must remain visible: `s4-1` step 9 says to
cluster all traces from a single condition after feature normalization and then
repeat for each condition, whereas the AP2 Results text says WT/control
boundaries were applied to PIP2−. The source inspected here does not resolve
which implementation settings establish that AP2 convention. A future analysis
must pin an archived author implementation/configuration before scoring; do not
invent condition-specific matrices or silently retrain labels.

## Normalization is not independent calibration

The paper has several normalizations with limited meaning:

* `s4-1` computes `D(i,t)` once from observed **control** intensity/time
  transitions and shares that function across conditions; it then normalizes
  the three DAS features using the control mean and standard deviation. That
  deterministically fixes a reference function and feature scale; it does not
  measure fluorescence gain or detector response.
* `s4-3`, **“Data pooling for conditions acquired on different days,”** matches
  each day's siControl intensity CDF to a reference control CDF with a fitted
  linear transform, then applies that day's same transform to all traces,
  including siEAP. It is designed to reduce day-to-day laser/optical variation.
  The transform is derived from controls, has no external standard, and does not
  separately establish background, bleaching, shot/camera noise, or detection
  completeness. It also is not stated as the AP2 WT/PIP2− same-day procedure.
* Normalized probability-density plots and normalized difference maps describe
  display/comparison densities. They do not calibrate raw intensity or recover
  excluded dim events.

The paper requires enough SNR to detect dim AC-related structures and warns
that endogenous-level fluorescent clathrin was too dim for early-assembly
analysis in its setup. The AP2 mutant is reported dimmer, while the validity
rule excludes non-diffraction-limited tracks and tracks with consecutive gaps.
Therefore a brightness-linked detection/valid-track change can alter both the
available intensity transitions and the `N_valid` classifier denominator. The
all-track initiation denominator and valid-track CCP% denominator must remain
separate. This also leaves left/right censoring and endpoint/gap behavior
unresolved as physical-event timing; DASC classes are not observed scission.

## Consequence for the AP2 kinetics question

Published WT-derived features/boundaries can constrain the *analysis
definition*: apply a pre-specified fixed-control DASC pipeline, report raw
brightness, all-track and valid-track counts/fractions, gaps, first/last-frame
contacts, and class results by movie. It can test whether the reported
classifier contrast is reproduced under that definition.

It cannot by itself test whether AP2 mutation changes latent assembly or
disassembly kinetics rather than the observation/selection process. That test
requires, at minimum, condition-wise calibration or held-out validation of
background/gain/noise/bleaching and detection-plus-validity response across the
relevant brightness range, plus source-linked culture/batch structure. A
single-channel intensity track cannot supply these independently. The separate
EPI/TIRF work reports `h = 115 nm` as a setup setting and a normalized cohort
depth proxy; it is not a deposited-movie calibration or same-pit scission readout.

## Author-code family, provenance, and access outcome

The JATS data-availability statement links the primary author code family:
<https://github.com/DanuserLab/cmeAnalysis> (and the eLife archive copy).
The repository README says DASC is embedded in cmeAnalysis. A browser-accessible
mutable-master read of
<https://raw.githubusercontent.com/DanuserLab/cmeAnalysis/master/software/DASCtest.m>
showed it calls `dasMuiltiCondition`, `dasPoolingBootstrap`, `dasParameter`,
and `dasSingleCondition`; it is a current test harness dated March 2020 with
2026 copyright text. It is not a pinned paper-era implementation and supplies
no basis to replace the published AP2 rule with current-branch behavior.

Attempted retrieval of a commit SHA and small named MATLAB sources on
2026-09-22 did not yield a snapshot. The GitHub REST request reported exactly
`Authentication failed, see inner exception.` The subsequent raw-file command
reported `schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS
(0x8009030e)`. These are observed local access-error strings; this note makes
no inference about their underlying cause. No code snapshot was therefore
retained, and no downloaded code was executed. This access failure leaves the
`s4-1`/Results boundary-setting tension unresolved rather than resolved in
favor of either reading.

The paper snapshot is
[`PMC7192580.jats.xml`](metadata/dasc-methods-001/PMC7192580.jats.xml),
retrieved 2026-09-22 from
`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7192580/fullTextXML`,
SHA-256 `99C288FD03D3E0EC4D9ABA72074D7FCAE14BD40B2DBE0952A1E071C4B5BD5E0E`.
