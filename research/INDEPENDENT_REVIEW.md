# Independent review of the exploratory geometry comparison

Review date: 2026-09-19. This was one bounded review of the frozen comparison,
its audit, outputs, self-audit, and focused tests. No model redesign or new data
collection was performed.

## Disposition

**Pass for a narrow exploratory claim:** in these curated S-BIAD566 spherical-cap
fit tables, a five-knot nonnegative curve predicts deposited curvature from
deposited closing angle across held-out cells better on average than either strict
one-parameter description. The strict constant-area description predicts better
than strict constant curvature. This ordering is reproducible and survives the
reported filtering, endpoint, and uniform radius-shift checks.

**Do not promote this to a dynamic or molecular conclusion.** The observations
are fixed-cell snapshots, the response and predictor come from the same spherical
cap fit, cohort filtering uses the same geometry being compared, measurement
covariance is unavailable, and a constructed population counterexample reproduces
the flexible preference while every individual pit has constant curvature.

## Checks

| Check | Result | Evidence and limit |
| --- | --- | --- |
| Geometry and units | **Pass** | For a spherical cap, constant area gives `H = sqrt(2*pi*(1-cos(theta))/A)`; the implemented basis is equivalent and uses degrees only at the explicit conversion. Synthetic recovery and boundary tests pass. |
| Implemented group split | **Pass** | `group = cell_line:file_number`; every fold excludes the held-out group from fitting. The primary paper identifies the 13 SK-MEL-2, 7 3T3, and 3 U2OS files as cells, matching the audit. Training groups have equal total squared-error weight and reported means weight cells equally. |
| Direct train/test target leakage | **Pass** | Held-out target perturbation leaves fitted coefficients unchanged. All 11 focused geometry/audit tests pass. |
| Prospective or biologically independent validation | **Unresolved** | The 23 cells are from one published study; preparation/culture-level replication is not recorded in the processed tables. Deposited exclusion labels were defined from the study-wide curvature/angle pattern before this cross-validation, so errors are conditional on that curation rather than a fresh prospective holdout. |
| Input integrity for the recorded run | **Pass, conditional** | All 23 cached tables were MD5-checked by the audit, the comparison verifies their SHA-256 values, and the stored script/spec/audit hashes still match the files reviewed. The integrity chain has a code defect described below. |
| Filtering robustness | **Pass within tested policies** | Ordering is unchanged for corrected/unflagged (2,574 sites), raw-nonnegative/unflagged (2,551), and corrected/include-flagged (2,831). Constant area nevertheless beats the flexible reference in 2 of 23 held-out cells in the first two policies and 4 of 23 when flags are included. |
| Endpoint and linkage-radius sensitivity | **Pass within tested scenarios** | Ordering is unchanged for 0/±10 nm uniform radius shifts, with all angles or 20–160°. These six deterministic transformations are not calibrated uncertainty draws. |
| Joint measurement uncertainty | **Unresolved** | No per-site standard errors or angle/curvature covariance are deposited. The source simulation reports larger angle error below 20° and above 160°, but it does not provide a joint experimental observation model usable here. |
| Single-pit curvature dynamics | **Fail as an inference** | The stored counterexample yields the flexible ranking from phase-dependent sampling even though curvature is constant within every synthetic pit. |
| Molecular mechanism discrimination | **Fail as an inference** | No perturbation, molecular observable, live trajectory, force measurement, or mechanism-specific likelihood is tested. The flexible curve is not a mechanism. |

## Findings that control interpretation

The numerical result is real but modest relative to the unresolved observation
model. In the corrected run, the flexible-reference advantage over constant area
is 0.000238, 0.000145, and 0.000163 nm^-1 for 3T3, SK-MEL-2, and U2OS,
respectively. The advantage over constant curvature is larger (0.00171, 0.00132,
and 0.00125 nm^-1). No interval estimate is justified, particularly for U2OS
with only three cells.

The compared columns are not independent measurements. The primary methods say
that LocMoFit fits a hollow spherical cap parameterized by surface area `A` and
closing angle `theta`; curvature `H` follows from that cap. Direct audit of all
2,831 deposited rows confirms
`A = 2*pi*(1-cos(theta))/H^2` to a maximum relative discrepancy of
`6.6e-8`. Thus the constant-area curve is the spherical-cap identity with `A`
held fixed, and the flexible curve describes how the fitted cap area and angle
co-vary. Cross-cell prediction still checks whether that fitted-geometry pattern
replicates, but it is not independent evidence that physical curvature changes
with time. See the [primary article's fitting methods and simulation limits](https://rupress.org/jcb/article/222/3/e202206038/213855/Clathrin-coats-partially-preassemble-and).

Filtering is outcome-dependent. The authors excluded a visibly disconnected
high-curvature population, supported by an AP2 control, using cell-line-specific
curvature thresholds. That is a defensible cohort definition, but it conditions
the comparison on the same `H`-versus-`theta` geometry. The include-flagged
sensitivity reduces this concern without removing it and keeps the average
ordering. The audit's 18 threshold/flag disagreements show that the supplied flag
cannot be reconstructed from a threshold alone; the deposited flag should remain
authoritative unless fuller curation metadata are obtained.

The corrected primary run is not an exact reproduction of the paper's stated
negative-curvature filter. It retains 23 raw-negative fits after the deposited
flat-site correction to `H=0`, `theta=0.0001°`; the paper's methods also state
that negative-curvature sites were excluded from fitting. The predeclared
raw-nonnegative sensitivity is therefore the closer source-method analysis, and
its unchanged ordering is useful. Reports should name the corrected run as a
repository policy rather than the paper's unique canonical filter.

The labels “constant curvature” and “constant area” are acceptable for strict
geometric functions, but not as complete mechanism tests. In particular, the
historical constant-curvature mechanism treats flat lattices as outside its
endocytic trajectory, whereas this cohort includes corrected flat sites. The
source paper also distinguishes those mechanisms through surface area and edge
behavior, not curvature prediction alone. The current report mostly observes
this distinction and should continue to do so.

## Actionable defects

1. **The promised changed-hash stop is incomplete.** `main()` records the current
   hashes of the script, specification, and audit but never compares them with a
   frozen expected digest. `load_verified()` checks each table only against the
   mutable SHA-256 value in `data_audit.json`; it does not recompute the deposited
   `published_md5`. Simultaneously changing a table and its audit entry would pass.
   Freeze expected protocol/audit digests outside the generated output and verify
   each table against both SHA-256 and its retained published MD5. Add a test for
   a jointly altered table plus audit, not only an altered table.

2. **The observation description is imprecise.** `FIRST_COMPARISON.md` says angle
   and curvature are fitted quantities. The source methods specify fitted `A` and
   `theta`, with `H` algebraically derived within the cap geometry. Amend the
   specification and result narrative so readers do not mistake the two columns
   for independent measurements.

3. **The strict constant-area boundary is not enforced.** The specification says
   `A > 0`, but NNLS permits its coefficient `1/sqrt(A)` to be exactly zero, which
   corresponds to infinite rather than positive finite area. It does not occur in
   the recorded folds. Reject or explicitly label that boundary if it occurs and
   add a test.

## Permitted scientific scope

The supported statement is: **within each of three cell lines in this curated
fixed-cell dataset, an angle-dependent descriptive curve transfers across cells
better on average than strict constant-area or constant-curvature functions;
constant area transfers better than constant curvature, with some cell-level
exceptions.** This supports seeking independent raw-localization calibration,
live within-pit trajectories, and perturbation data.

It does not establish a temporal trajectory for any pit, literal constant-area
or changing-curvature behavior, cooperative clathrin remodeling, adaptor action,
actin force, bistability, or rejection of a molecular mechanism. Those questions
remain unresolved by this comparison.
