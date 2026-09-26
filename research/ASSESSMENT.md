# Clathrin formation: initial research assessment

Status: theory/data/capability assessment, updated 2026-09-26. Public evidence
only. Exploratory geometry prediction and the tracking-data contract have been
independently reviewed within their limited scopes; no mechanistic candidate is
selected. This remains a starting map, not an exhaustive literature review.
Source statements are paraphrases; comparison priorities are our assessment.

## Current evidence and direction

**Latest reviewed milestone (2026-09-26):** the LocMoFit adapter now exposes
missing per-site curvature uncertainty as null, preserves its 2,551-site raw
default cohort, and supports an explicit corrected cohort of 2,574 sites.
All legacy geometry values match exactly across 23 checksum-verified tables.
The shape inverse and curve-comparison consumers construct their own uncertainty
scales, so both now require explicit exploratory opt-in before computation.
Their outputs deny calibrated likelihood and mechanism permission; a large
conditional score cannot create a decisive mechanism verdict.

Independent review accepts the bounded cleanup. The relevant suite passed
18 tests with four cached-data integration skips; the whole-table compatibility
audit and mocked sampler tests cover the actual changes without empirical refits.
Nine numerical helper functions match the preserved originals. Old results and
raw inputs remain unchanged. See [cleanup](LOCMOFIT_ADAPTER_CLEANUP.md) and
[independent review](LOCMOFIT_ADAPTER_REVIEW.md).

The empirical bridge remains stopped: processed cap fits lack likelihood inputs
and covariance, 58.28% of retained caps overhang the shallow graph surrogate,
and the fixed-angle fitted area-curvature slope follows cap algebra. The next
bounded theoretical question concerns spontaneous curvature versus a balanced
normal load in the full membrane linear operator, with explicit templates,
physical controls and boundary/reaction. It must add a spatial nullspace/rank
result or an informative perturbation design, rather than repeat cap two-area
algebra or synthetic area/window sweeps. No biological mechanism is selected.

| Evidence | What is established | What it cannot currently decide |
| --- | --- | --- |
| S-BIAD566 geometry | Descriptive held-out ranking and a synthetic counterexample to interpreting population trends as pit trajectories | Single-pit dynamics, molecular mechanism or calibrated geometry uncertainty |
| Shape2Fate tracking references | Verified local table contract; three references with 479, 418 and 480 track IDs over observed frames 0–119, independently reviewed | Curvature, complete event lifetimes, physical units, scission or biological replication |
| Shape2Fate dynamin inventory | Seven acquisitions, seven masks, one channel-registration JSON; no separate event table in the directory | Whether the movies can discriminate a mechanism, event definitions or replicate independence |
| DASC metadata and sidecars | Public raw movies with condition/date/cell mapping, stated 1 fps cadence, and same-date CALM knockdown/control and AP2 mutant/WT contrasts | No deposited processed traces, verified biological replicate structure, physical scission labels or calibrated absolute curvature |

The AP2-alpha WT versus K57E/Y58E PIP2-binding mutant remains a possible
reproduction or detection-sensitivity benchmark, but is now **parked as a test
of physical mechanism**. Primary methods fix the control-derived reference
score, feature normalization and (explicitly in AP2 Results) cluster boundaries.
They do not independently constrain missed/invalid structures or all optical
nuisance terms. A fixed scoring rule cannot recover the latent distribution
from arbitrarily condition-dependent selection. The analytical construction and
scoped decision were independently reviewed; no biological absence or imaging
artifact has been established.

No movie was downloaded. The proposed two-file I/O check is parked. The exact
paper-version author code was not pinned because local retrieval failed; an
apparent Results/Methods clustering wording discrepancy remains visible. This
access limitation is separate from missing calibration. Corrected earlier
source locators and AP2 control-boundary wording are recorded in the source note.

The descriptive observable router's refusal of tag-only force permission passed
independent review. It is not a global gate on numerical inverse functions.
RESEARCH.md and two historical output JSONs now flag outdated permission claims;
all old numerical values were preserved, not revalidated. No positive calibrated
authorization path has been added.

Next test the conditional information content of full membrane shape under
prescribed spontaneous-curvature and balanced-load families. The broad scope
is sufficient; no user decision is needed.

Evidence: [DASC_OBSERVATION_DECISION.md](DASC_OBSERVATION_DECISION.md),
[DASC_ANALYSIS_RULES.md](DASC_ANALYSIS_RULES.md),
[DASC_OBSERVATION_REVIEW.md](DASC_OBSERVATION_REVIEW.md), and
[OBSERVABLE_PERMISSION_REVIEW.md](OBSERVABLE_PERMISSION_REVIEW.md).
Earlier data contracts and decisions remain in ANNOTATION_AUDIT.md,
ANNOTATION_REVIEW.md, DYNAMIN_METADATA.md, and DASC_COMPARISON.md.

## Earlier theory and data triage

**Update:** processed BioStudies tables are now downloaded and checksum-verified;
the Mund full paper was read from its institutional copy. The earlier access
failures below describe the initial pass and are superseded by
[DATA_AUDIT.md](DATA_AUDIT.md). Scott's data-availability statement specifies
author request, so those data are not counted as directly accessible public data.
The next comparison is specified in [FIRST_COMPARISON.md](FIRST_COMPARISON.md).

That exploratory comparison has now run: see [GEOMETRY_RESULTS.md](GEOMETRY_RESULTS.md)
for held-out prediction errors and limitations. Independent review accepted only
the descriptive result, with corrections recorded in REVIEW_DISPOSITION.md.

| Candidate or distinction | Evidence and locator | Testability and current gap |
| --- | --- | --- |
| Continuous versus delayed bending trajectories | Scott et al. 2018, [abstract and Simulation methods](https://www.nature.com/articles/s41467-018-02818-8): live-cell pol-TIRF and complementary microscopy report different relationships between coat assembly and bending. | Useful for timing, but trajectories do not uniquely identify mechanisms. Need the polarization/TIRF observation model, calibration and track-level data before fitting. Raw-data access not verified. |
| Partial preassembly versus strict constant area/curvature descriptions | Mund et al. 2023, [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9929656/), abstract and data-availability search excerpt: static geometry with pseudotime, data accession S-BIAD566. Full article retrieval was blocked during this pass. | Existing `ingest_smlm_locmofit.py` maps spherical-cap fits to geometry and explicitly lacks a real time axis. Promising low-cost geometry comparison; raw repository availability and fit uncertainty still need verification. |
| Coat/adaptor rearrangement coupled to tension | Bucher et al. 2018, [abstract and model/data comparison](https://www.nature.com/articles/s41467-018-03533-0): combines EM structure and TIRF dynamics to investigate coat rearrangement. | Need to distinguish directly measured geometry from inferred timing and adaptor-ratio interpretation. Dataset access and perturbation comparability unresolved. |
| Membrane mechanics with neck geometry and tension-dependent transitions | Hassinger et al., [author preprint abstract](https://arxiv.org/abs/1604.08629): continuum calculations report different budding behavior with tension and an intermediate snap-through regime. | A theoretical candidate, not experimental proof of a biological transition. Need full shape equations, boundary conditions and branch/stability checks; cap-only predictions cannot establish neck behavior. |
| Active actin mechanics under load | Akamatsu et al., [eLife abstract/intro search excerpt](https://elifesciences.org/articles/49840): combines membrane mechanics, filament simulations and measurements. Full page retrieval failed in this pass. | Include actin-assisted explanations. Existing `actin_only` parameter restriction is not equivalent to the published filament-network model. Need perturbation datasets and force-to-observation mapping. |
| Cooperative adaptor engagement | Exploratory model in the supplied shared chat; not independently validated here. | Retain as one candidate. Fluorescence does not directly measure engaged occupancy; cooperative parameters and stability claims need independent derivation and experimental constraints. |

## Data access and independence

The [BioStudies accession](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD566)
could not be retrieved by the web reader in this pass. The repo already contains
an adapter with explicit public download locations; that establishes an existing
code path, not proof that downloads currently work. Next verify the manifest,
license, per-cell identities and checksums before downloading substantial data.

Pits from one cell must not silently count as independent biological replicates.
Multiple papers, processed tables and agent summaries derived from the same raw
data do not add independent evidence. Static shape distributions do not supply
single-pit kinetics. Published/publicly inspected data cannot be described as an
unseen confirmatory holdout.

## First comparison to assess for feasibility

Start by checking whether the published per-site geometry supports a fair
comparison of strict constant-area and constant-curvature descriptions against
a flexible growth/bending description. This is a geometry-level diagnostic,
not an adjudication of adaptor, neck or actin mechanisms.

Before selecting it: verify public data access; recover cell-level grouping and
exclusions; propagate geometric fit uncertainty; examine shared fitting biases;
specify predictions and scoring; assess whether candidate differences exceed
measurement uncertainty. If those checks fail, retain an unresolved finding and
prioritize an accessible dataset with suitable measurements instead.

In parallel, audit live curvature/coat trajectories and tension/actin
perturbations for their ability to distinguish mechanical explanations. Do not
implement a large suite of models until that audit identifies an informative
comparison. The next assessment revision needs full methods, data manifests,
equations and an independent review; the current search excerpts are insufficient
for promoting scientific claims.
