# First exploratory geometry comparison

Status: independently reviewed for narrow descriptive scope; review corrections
tested by the lead. See [REVIEW_DISPOSITION.md](REVIEW_DISPOSITION.md).
No molecular mechanism selected; numerical results below are unchanged.

Subsequent [self-audit](REVIEW_RESULTS.md) retained this descriptive ranking but
demonstrated a population-sampling counterexample to single-pit interpretation.
Six additional sensitivity scenarios preserve the average ordering; calibrated
measurement uncertainty remains unresolved. Independent review has since completed.

The comparison uses 23 held-out file/cell groups within three cell lines.
Each fit sees only the other groups in that cell line. Groups have equal total
training weight and equal weight in the reported average. The primary analysis
uses 2,574 sites, retaining deposited flat-site corrections while excluding the
257 flagged sites. Sensitivities use 2,551 raw nonnegative/unflagged sites and all
2,831 corrected sites, respectively.

## Primary prediction errors

Mean absolute curvature error on held-out groups, in inverse nm (lower is better):

| Cell line | Groups | Constant curvature | Constant area | Flexible reference |
| --- | ---: | ---: | ---: | ---: |
| 3T3 | 7 | 0.002455 | 0.000983 | 0.000745 |
| SKMEL2 | 13 | 0.002359 | 0.001181 | 0.001036 |
| U2OS | 3 | 0.002168 | 0.001079 | 0.000916 |

Average ordering is unchanged across the three filtering policies: flexible
reference, then constant area, then constant curvature. This is not unanimous
across cells. Constant area outpredicts the flexible reference in SKMEL2 groups
1 and 10 in the primary and raw-nonnegative analyses. Including flagged sites
adds 3T3 group 2 and SKMEL2 group 13 to those exceptions.

The primary SKMEL2 angle-bin check also favors the flexible reference in each
bin's average over groups containing sites in that bin. Its largest error
advantage over constant curvature is in the 0–45 degree bin. This is descriptive:
bins can contain different groups, and neither the bins nor observations are
independent confirmatory experiments. All cell-line/bin/fold scores are retained
in the JSON rather than selecting only favorable regions.

## Interpretation and limits

The flexible curve is a five-coefficient descriptive reference, not a physical
theory. Its predictive advantage suggests that these data contain systematic
angle-dependent geometry not captured by the two strict one-coefficient forms.
It does not identify adaptor cooperativity, actin forces, neck instability, or
real-time bending kinetics. A constant-area description doing better than
constant curvature here does not establish a literal constant-area trajectory
for each pit.

Correlated geometric fitting errors, selection and heterogeneity remain plausible
contributors. Per-site fit covariance is unavailable in these tables. Group-level
prediction reduces within-cell leakage but does not establish culture-level
independence, transportability to another experiment, or a blind holdout. Only
three U2OS groups are available. No significance test or calibrated uncertainty
claim is made.

## Reproduction and next decision

Run `python research/compare_geometry.py` from the repository root after the
public-data audit. No network or API access is used. SHA-256 hashes are verified
before fitting. [geometry_results.json](geometry_results.json) retains every
fold, training group, coefficient, filter count, paired error difference, angle
bin, software version and input/specification/script hash. The fixed protocol is
in [FIRST_COMPARISON.md](FIRST_COMPARISON.md).

Twenty tests passed, including synthetic recovery, trigonometric units, boundary
handling, nonnegative basis, group-weight invariance, held-out target isolation,
data checksum rejection and controller recovery contracts. Ruff passed.

Next, independently review the fitting/selection assumptions and seek measurement
error calibration or accessible raw-localization simulations. Keep expanding the
theory/data map for public perturbation and live-trajectory data. These results
justify that next assessment step, not immediate commitment to a molecular model.
