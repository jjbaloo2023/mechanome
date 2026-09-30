# What the clathrin campaign has established

**Reviewed evidence through 29 September 2026.** Public static geometry supports
conditional prediction, our mechanics models expose requirements for identifying
sources, and the observation pipeline now reports internally consistent tracking
scores. None of these establishes a molecular explanation for pit formation.
The evidence below comes from the retained study records; this synthesis adds no
new fit, source acquisition or claim of literature novelty.

The latest [two-channel observation calculation](STAR_OBSERVATION_FINDINGS.md)
adds a conditional measurement result: coat amount and axial position inferred
from the same channels have correlated errors, and near-equal attenuation
coefficients amplify uncertainty. This has independent review and six exact
checks; it is not a measured biological relationship. The new
[STAR workbook listing](PAIRED_SHAPE_PUBLIC_FINDINGS.md) remains uninspected
after an [environment access failure](STAR_WORKBOOK_SCHEMA_FINDINGS.md).

The [final distributed-signal example](STAR_DISTRIBUTION_FINDINGS.md) strengthens
that limit: two positive distributions with the same known total amount and two
perfect calibrated signals have different mean heights. Thus the point-position
inverse cannot generally be read as a distributed coat's mean height. This exact
counterexample closes the observation branch. The [campaign handoff](CAMPAIGN_CHECKPOINT_20260929.md)
records the remaining evidence gaps and conditions for a concrete restart.

## Public-data results

| Finding | Evidence | Limit | Observation needed for the next inference |
| --- | --- | --- | --- |
| A flexible curve predicts static cap fits better on average when training within each cell line | [23-group comparison](GEOMETRY_RESULTS.md) and [review disposition](REVIEW_DISPOSITION.md) | Fitted curvature and angle share errors; static sampling can mimic a trajectory | Calibrated shape and coat measurements through the same pit over time |
| That ranking does not transfer uniformly across cell lines or inclusion choices | [27-fit transfer study](GEOMETRY_TRANSFER_FINDINGS.md): primary mean favors flexible, U2OS favors area, include-flagged mean favors area | Descriptive point estimates; no calibrated significance or independent culture replication | Independent replicated data with a declared inclusion rule and measurement uncertainty |
| Other public collections provide useful but narrower records | [Shape2Fate annotations](ANNOTATION_AUDIT.md), [DASC decision](DASC_OBSERVATION_DECISION.md), [Myo1E table](MYO1E_REPOSITORY_FINDINGS.md), [yeast tables](YEAST_FIGURE6_FINDINGS.md) | Tracks, metadata and population means do not automatically supply complete lifetimes, same-event joint measurements or force | A verified event/condition/grouping contract and the particular endpoint needed by the comparison |

Constant curvature has the largest target-line mean error in all nine transfer
folds. This does not rule out constant curvature along individual pits: an
[accepted population counterexample](REVIEW_DISPOSITION.md) already separates
population prediction from single-pit dynamics. All target rows, support
exceptions and ranking reversals are retained in the transfer outputs.

## Conditional mechanics results

| Result within the declared model | Evidence | What would be required beyond it |
| --- | --- | --- |
| Fixed-area cap force and tension can compensate; additional known area/rigidity controls can remove a specific ambiguity | [Cap](CAP_FINDINGS.md), [two-area analysis](TWO_AREA_FINDINGS.md) | Verified controls and an observation model; these algebraic conditions are not a biological intervention |
| Passive surrounding-membrane models give decreasing apex curvature over the sampled area regime; fitted cap curvature depends on the observation window | [Full shape](FULL_SHAPE_FINDINGS.md), [passive area](PASSIVE_AREA_FINDINGS.md), [observation mapping](CAP_OBSERVATION_FINDINGS.md) | Appropriate full geometry and calibration; apex, average and fitted curvature are distinct observables |
| In the shallow model, complete ideal shape identifies a combination of preferred curvature and balanced load; varying tension alone does not remove unrestricted source ambiguity | [Load identifiability](LOAD_IDENTIFIABILITY_FINDINGS.md) | An independently constrained source/load field, or the explicitly stated alternative controls |
| Nonlinear compensation depends on slope; conditional uniqueness and local stationary profile existence can be proved, while flat profiles remain ambiguous | [Exact source criterion](NONLINEAR_SOURCE_FINDINGS.md), [uniqueness](NONLINEAR_UNIQUENESS_FINDINGS.md), [existence](NONLINEAR_EXISTENCE_FINDINGS.md) | Stability and reliable finite-amplitude numerics; no global or practical recovery claim follows |
| Unknown balanced load prevents a uniform near-flat inverse bound; fixed known spatial load permits a conditional recovery bound | [Unknown-load limit](NONLINEAR_INVERSE_STABILITY_FINDINGS.md), [known-load theorem](KNOWN_LOAD_RECOVERY_FINDINGS.md) | Complete compatible stationary profiles, known pointwise load and mechanics, with calibrated uncertainty |

Zero net force, an actin-inhibition label or a tube-force resultant is not a
known spatial load field. The [public-data comparison](KNOWN_LOAD_DATA_COMPARISON.md)
finds that the assessed tables do not supply the theorem's complete control set.
These results specify assumptions under which inference could work; they do
not license fitting missing inputs or claim an established new biological law.

## Observation and software results

The [synthetic dimming study](SYNTHETIC_DIMMING_FINDINGS.md) kept latent events
fixed while dimming reduced observed coverage. Detectable-only scores could
remain high despite missed events. This demonstrates a possible observation
effect, not that a published experiment suffers from that artifact. Its
[execution audit](synthetic_dimming_execution_audit.json) records 282 actual
tracker calls against a 150-call cap and missing first-run artifacts; that
failure remains part of the evidence history.

The resulting [tracking validator repair](TRACKING_METRIC_FINDINGS.md) makes
full-presence and detectable-only counts consistent. Fifteen targeted tests
passed with one tracked movie. This verifies a software contract, not detector
calibration or biological lifetime accuracy. Legacy lifetime pairs remain a
labeled diagnostic. The [LocMoFit adapter cleanup](LOCMOFIT_ADAPTER_CLEANUP.md)
similarly makes missing uncertainty and exploratory-only fitting explicit;
it does not make the public geometry a calibrated mechanistic likelihood.

The [duration-composition bound](RECRUITMENT_DURATION_FINDINGS.md) supplies one
prospective falsification rule for a shared conditional recruitment probability.
No biological inequality was evaluated. Missing denominators and grouping are
not repaired by that probability result, and observed duration is not a causal
exposure clock.

The [offline work-unit extension](WORK_UNITS_FINDINGS.md) adds atomic cumulative
reservations to the existing controller. Seventeen targeted tests passed in one
invocation with zero real scientific calls. Independent review caught and closed
an unresolved-call bypass. This is a software capability; live campaign enforcement
remains unverified. The [repaired recovery continuation](WORK_UNIT_RECOVERY_REPAIR_FINDINGS.md)
finished the same dummy attempt after explicit local reconciliation and two
observed process exits. It preserved the original PID-supervision failure and
three-launch/two-callback expenditure. No clean original three-phase run,
host-crash/reboot recovery or exactly-once external effect is claimed.

## Stopped or unresolved work

| Branch | Disposition and reason |
| --- | --- |
| Nonlinear numerical source test | [Three attempts closed](NONLINEAR_NUMERICAL_FINDINGS_003.md); solver convergence did not pass the unchanged physical residual gate. No numerical K/K3 accepted |
| Bucher published-figure reconstruction | [Inclusion mapping unresolved](BUCHER_INCLUSION_FINDINGS.md); deposited entries do not reconcile with caption counts under the inspected metadata. No effect estimated |
| Actin Figure 7 code reproduction | [Exact output/load mapping unverified](ACTIN_CODE_FINDINGS.md); no author simulation executed |
| Myo1E comparison | [Condition, denominator and raw group identities unresolved](MYO1E_REPOSITORY_FINDINGS.md); no date-like identifiers repaired or empirical contrast run |
| Yeast fixed-height transit comparison | [Reference/alignment applicability unresolved](YEAST_REFERENCE_FINDINGS.md); verified mean curves alone did not justify the proposed comparison |
| DASC/AP2 physical-mechanism test | [Selection and observation controls insufficient](DASC_OBSERVATION_DECISION.md); parked, not a null biological result |
| Geometry transfer, duration null and source-recovery theory sequences | Registered questions completed; no additional grid or theorem extension queued |

Implementation failures, source-access failures and absent controls are not
biological refutations. Earlier rejected numerical/observation attempts remain
linked from the [study index](INDEX.md); later acceptance never erases them.

## Research decision

The next useful step must add a discriminating observable or independent control,
not another nearby fit to the same tables. [Assessment](ASSESSMENT.md) separates
those requirements from what is available. The [next-experiment assessment](CAMPAIGN_NEXT_EXPERIMENT.md)
and [independent challenge](CAMPAIGN_SYNTHESIS_REVIEW.md) record the present
decision; [NEXT_CYCLE.md](NEXT_CYCLE.md) gives its executable scope. No new
scientific computation is implied by this synthesis.
