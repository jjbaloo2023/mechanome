# Clathrin research: evidence and decision map

**29 September 2026.** This assessment separates biological questions from the
measurements and controls needed to answer them. It synthesizes the already
reviewed campaign, not a new or exhaustive literature search. The initial
assessment and navigation are preserved in the [pre-synthesis snapshot](campaign_navigation_before_001.zip).

Latest observation-contract result: [shared-channel uncertainty](STAR_OBSERVATION_FINDINGS.md)
is analytically coupled in the idealized point-height model. A derived axial
trace and its input coat channel need joint uncertainty accounting. The
[workbook schema attempt](STAR_WORKBOOK_SCHEMA_FINDINGS.md) stopped on local
socket permissions before access; this does not establish dataset absence.

## What comparison is actually possible?

| Question or candidate | Distinguishing observation, if available | Current evidence | Decision |
| --- | --- | --- | --- |
| Continuous versus delayed bending during coat assembly | Time-resolved membrane shape and coat accumulation for the same event | Static fitted caps and population ordering; [geometry](GEOMETRY_RESULTS.md) and [transfer](GEOMETRY_TRANSFER_FINDINGS.md). New [STAR listing](PAIRED_SHAPE_PUBLIC_FINDINGS.md) offers a conditional axial proxy; workbook schema unverified | Descriptive prediction accepted. No single-pit time course inferred |
| Strict constant-area/constant-curvature descriptions versus a flexible curve | Independently sampled, calibrated geometry under fixed scoring/inclusion rules | Primary average favors flexible, but held-out-line and inclusion-policy reversals occur | Completed conditional comparison; no universal rank or new grid |
| Passive coat curvature versus active membrane loading | Full compatible shape together with independent source/load constraints and mechanics | [Conditional source-separation results](LOAD_IDENTIFIABILITY_FINDINGS.md), [known-load requirements](KNOWN_LOAD_DATA_COMPARISON.md) | Assessed datasets do not enable calibrated source recovery |
| Tension-dependent shape transitions or neck behavior | Full-shape observations and a verified branch/stability model in the applicable regime | Bounded shallow/passive benchmarks; later [nonlinear residual failure](NONLINEAR_NUMERICAL_FINDINGS_003.md) | No neck/scission or finite-amplitude stability result; numerical branch closed |
| Actin adaptation under load versus a fixed work/constitutive reference | Joint event-level displacement and relevant network readout under independently calibrated resistance and controls | [Published-prediction assessment](ACTIN_ADAPTATION_FINDINGS.md); [partial code inventory](ACTIN_CODE_FINDINGS.md) lacks exact output/control mapping | Existing candidate and inventory closed; stronger controls are prerequisites, not a new follow-up |
| Recruitment change versus duration-composition or selection effects | Eligible positive/negative cohort, declared positivity, duration/censoring and independent grouping | [Prospective probability bound](RECRUITMENT_DURATION_FINDINGS.md), but [Myo1E contract](MYO1E_REPOSITORY_FINDINGS.md) remains insufficient | No biological inequality or contrast evaluated; do not repair identifiers by guesswork |
| Cooperative adaptor engagement | An independently calibrated engagement/occupancy readout and a prediction that competing mechanisms do not share | Exploratory supplied model; current fluorescence does not directly establish engaged occupancy | Retained candidate, neither validated nor refuted |

An observed geometry class or a model's lower descriptive error does not name a
molecular cause. Continuous and delayed trajectories can emerge from the same
mechanism under different conditions. Similarly, rejecting a specific
constant-work reference would not rule out every non-adaptive explanation.

## Data-to-inference requirements

| Assessed input | Usable information | Exact missing bridge |
| --- | --- | --- |
| S-BIAD566 / LocMoFit processed tables | Checksum-verified static cap fits, 23 groups, three cell lines, explicit cohorts | Joint fit covariance/localization likelihood, time-resolved same-event shape, culture replication and full surrounding profile |
| Shape2Fate | [Verified observed track tables](ANNOTATION_AUDIT.md) and [dynamin inventory](DYNAMIN_METADATA.md) | Complete event lifetimes, physical endpoint labels, required units and sampling independence |
| DASC/AP2 | [Movie/condition/date/cell metadata](DASC_METADATA.md) and reviewed scoring method | Processed traces, calibrated condition-dependent selection and an independent physical endpoint; [mechanism test parked](DASC_OBSERVATION_DECISION.md) |
| Bucher / Saleem controls | Public EM structure tables and a membrane-calibration precedent | Independent pit-load field and invariant controls; [Bucher figure counts remain unresolved](BUCHER_INCLUSION_FINDINGS.md) |
| Akamatsu simulation inventory | Pinned partial source metadata and a declared prediction | Exact Figure 7 output, held-fixed control set and resistance mapping; author code was not executed |
| Myo1E public table | 1,709 rows and raw condition/group fields inspected | Verified condition/channel codebook, eligible denominator, positive definition and authoritative group/pair mapping |
| Yeast Figure 6 | Two verified CSVs, reported Act1 medians and mean Sla1 curves | Common spatial reference/alignment applicability and event pairing; [one clarification attempt stopped](YEAST_REFERENCE_FINDINGS.md) |

This is an inventory of assessed inputs, not proof that suitable public data
exist nowhere. Same-event pairing, independent culture/movie grouping and shared
data ancestry must be checked for each specific question. A paper, processed
copy and multiple agent notes from the same source do not add independent evidence.

## Which controls matter for which claim?

A descriptive comparison needs a verified measurement definition, eligibility,
inclusion rule, grouping and uncertainty appropriate to that score. It does not
need a complete force map merely to report an observable change. Full source
recovery has stronger requirements: compatible stationary profiles, declared
boundaries, known mechanics and a spatial load field, including its balancing
reaction. A zero-resultant label cannot substitute for that field.

The [LocMoFit observation contract](LOCMOFIT_OBSERVATION_CONTRACT.md) also records
that 58.28% of retained corrected caps overhang the shallow graph representation.
Selecting shallow caps alone would not supply the other missing controls. Jointly
fitted area, angle and curvature cannot be treated as independent measurements.

For event timing, track disappearance is an observation. Testing whether it
corresponds to scission or internalization would require a separately validated
endpoint on the same event and explicit censoring/association rules. A dynamin
flash or movement out of the image is not automatically such a reference. This
would be a measurement-validation question, not a force or mechanism verdict.

## Current decision

The final [distributed-signal counterexample](STAR_DISTRIBUTION_FINDINGS.md) is
accepted and its observation branch is closed. Two perfect calibrated intensities
and known total amount need not determine mean height for an unknown distribution.
This supplements the prior shared-error result; it does not validate actual STAR
calibration or establish a biological mechanism.

The [continuation review](CAMPAIGN_CONTINUATION_REVIEW_20260929.md) finds no distinct
executable next task within the assessed inputs and accepted stops. The [campaign
handoff](CAMPAIGN_CHECKPOINT_20260929.md) preserves results and exact restart
conditions. The recurring schedule has been deleted, avoiding repeated
searches, nearby analytic examples or operational extensions.

The newest workbook remains uninspected after a local permission failure, not a
publisher failure. A permitted retrieval route with a deliberately reopened
bounded inventory, a supplied event object, or a genuinely new independently
measured observable can justify a new registration. The [actin prerequisite](CAMPAIGN_NEXT_EXPERIMENT.md)
remains separate and requires its own controls. No candidate is promoted to an
empirical test until the contract needed for that particular claim is inspected.
[NEXT_CYCLE.md](NEXT_CYCLE.md) has no automatically executable task.

## What has been stopped

The three-attempt nonlinear numerical limit, geometry-transfer stop, Bucher
inclusion stop, Akamatsu inventory stop, Myo1E table stop and yeast reference
stop remain in force. DASC/AP2 is parked as a physical-mechanism test. Completed
analytic sequences and the dimming grid are not automatically rerun. Their
[study records](INDEX.md) preserve failures and uncertainty; a changed approach
must have a distinct rationale, registration, budget and independent review.

The software changes support honest observation contracts. Fifteen targeted
tracking tests and the accepted LocMoFit adapter checks establish specific
implementation behavior; they do not validate all detectors or the generic
`pixels -> geometry -> posterior -> mechanism` pipeline. See [findings](FINDINGS.md)
and [reproduction guidance](REPRODUCE.md).
