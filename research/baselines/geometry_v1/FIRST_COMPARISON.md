# First comparison specification — version 1

Status: specified before fitting; exploratory because these public data and
published interpretations have already been inspected. No blind holdout claim.

Implementation choices fixed before the first run: fit nonnegative coefficients
by group-weighted least squares; evaluate using the MAE specified below. Preserve
the deposit's 0.0001-degree corrected flat-site convention without recomputing
area. Report held-out errors in fixed 0–45, 45–90, 90–135 and 135–180 degree bins
without refitting or choosing bins based on rankings. Rank-deficient training
designs stop with an unresolved error. No p-values or confidence claims are made.

**Question:** how well do strict constant-curvature and constant-area geometric
descriptions predict curvature versus closing angle across withheld file/cell
groups within each cell line? This asks about geometric descriptions, not which
molecular mechanism generated them.

## Inputs and observation boundary

Use only the checksum-verified processed tables in `data_audit.json`. Retain raw
and corrected values, supplied exclusion flags and source keys without overwrite.
Report all filter counts by group. Use deposited corrections and exclusion flags
for the primary descriptive analysis; repeat using raw nonnegative values and
including flagged populations as separate sensitivity analyses. Resolve flat-site
conventions before implementation; do not infer zero area from zero curvature.

Both curvature and angle are fitted quantities and may have correlated errors.
Area, radius, angle and curvature are not independent measurements. Score one
response (curvature) rather than treating derived area as additional evidence.
Missing covariance limits the interpretation of residuals and model rankings.

## Candidate predictions

- Constant curvature: H(theta) = h, with h >= 0.
- Constant area: H(theta) = sqrt(2*pi*(1-cos(theta))/A), with A > 0.
- Flexible descriptive reference: nonnegative piecewise-linear curvature versus
  angle, with fixed knots at 0, 45, 90, 135 and 180 degrees. This is a predictive
  reference, not a proposed mechanism or the paper's cooperative model.

Use radians inside trigonometric functions; H is in inverse nm and A in nm^2.
Fit on training groups only. Freeze these forms before observing fit rankings.

## Scoring and fairness

Leave one file/cell group out within each cell line. Give training groups equal
total weight. Report held-out mean absolute curvature error per group, then its
equal-group average; also report every fold and paired candidate error differences.
Do not pool cell lines into independent replicates or tune knots on held-out data.
With only three U2OS groups, display all folds and avoid strong precision claims.

Use the same observations and folds for every candidate in each sensitivity run.
Compare ranking stability across filtering choices and angle ranges. No automatic
biological winner: a flexible curve fitting better can reflect selection, geometric
fit bias or heterogeneity rather than a particular physical mechanism.

## Checks and stopping

Before fitting, test constant-area and constant-curvature synthetic recovery,
unit conventions, nonnegative predictions, group leakage and boundary handling.
Missing groups, changed hashes or inconsistent corrections stop execution for
inspection. Solver failure produces an unresolved attempt, not negative science.

Report compatibility or predictive mismatch within the tested description and
data selection, and preserve inconclusive or sensitivity-dependent outcomes.
Require an independently briefed review before promoting the comparison to a
scientific conclusion. Force inference, real-time kinetics, bistability, and
mechanistic adjudication are outside this comparison's scope.
