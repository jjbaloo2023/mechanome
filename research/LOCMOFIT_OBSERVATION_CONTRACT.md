# LocMoFit observation contract: descriptive geometry only

Task `locmofit-contract-001`, attempt 1. Independently reviewed and accepted within the descriptive scope, 2026-09-25.

The processed tables cannot calibrate or reproduce the mapping from a passive
membrane profile to a LocMoFit cap fit. Two concrete distinctions now reinforce
that boundary: most retained caps extend beyond a hemisphere, and the deposited
projected area follows the cap silhouette rather than the rim disk above a
hemisphere. The accepted vertical-fit experiment remains a synthetic check.

## Primary method and observable map

Mund's Methods identify a 3D localization maximum-likelihood fit with cap area A
and closing angle theta, surface sampling, fitted pose, extra broadening and
background. Radius and curvature are derived. See the [primary paper](https://research-explorer.ista.ac.at/download/14788/14811/2023_JCB_Mund.pdf),
printed page 12, and the separate [source ledger](LOCMOFIT_OBSERVATION_SOURCE.md)
for implementation provenance and limitations. A current official implementation
must not be represented as the historical executable without evidence. The
source specialist pinned SMAP commit d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6.
The lead independently downloaded the 6892-byte cap model as text and verified
Git blob cc03dbd25b5d92c9894174d3d9ab417302af17ca. Its getDerivedPars
(lines 141-144) returns pi*R^2 for every positive closing angle, unlike the
deposited shallow-cap values. This confirms that current code cannot silently
replace the historical export; no source code was executed. See the immutable
[cap source](https://github.com/jries/SMAP/blob/d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6/LocMoFit/models/sphericalCap3D_surfaceArea.m#L125)
and locmofit_cap_source_current_provenance.json.

The article also specifies simulation inputs, including a 5 nm linkage-error
parameter, label/blinking choices and a CRLB procedure. These do not supply
the absent per-site localization inputs, fitted nuisance estimates or settings.
Do not turn missing table fields into a claim that all calibration information
is absent from the article.

| Quantity | Available processed field | Meaning and restriction |
| --- | --- | --- |
| Site/group labels | ID, cell_line, file_number | Site identity and file/cell grouping; culture independence unverified |
| Cap area and closing angle | surface_area, theta | Joint fitted geometry; theta stored in degrees |
| Radius and mean curvature | radius, curvature | Derived from the same fit; H = 1/R in nm^-1 |
| Rim and projected area | rim_length, projected_area | Same-fit geometry transforms; not extra independent measurements |
| Flat corrections | theta_corrected, curvature_corrected | Retain deposited convention separately; do not recalculate other columns from corrected zero curvature |
| Population selection | disconnected_sites | Retain deposited flag and raw fields; not a synonym for excluded double-site fits |
| Point-cloud inputs | absent | xyz, per-localization precision, localization count and site ROI unavailable in these processed tables |
| Likelihood/nuisance output | absent | Pose, background, extra blur, objective/Hessian and A-theta covariance unavailable |

The complete common schema has 12 named science/identity columns. 3T3 and U2OS
also contain an unnamed exported index; this explains the recorded false
same-schema flag and is not a missing science field. All 23 files still match
the accepted audit SHA-256 values. The checks read existing files only.

## Two geometry conventions checked against all 2,831 rows

Using raw radius and angle, H=1/R agrees to 5.25e-10 relative error, cap area
A=4*pi*R^2*sin(theta/2)^2 to 6.57e-8, and rim length
2*pi*abs(R*sin(theta)) to 1.46e-13. These identities check export conventions;
they are not independent validation of the fitted geometry.

The initial registered rim-disk prediction pi*R^2*sin(theta)^2 fails the 1e-4
relative gate in 1,744 rows. That failed check is preserved in
`locmofit_contract_checks.json`. A separately registered silhouette alternative
passes all rows, maximum relative error 6.56e-8:

- theta <= 90 degrees: projected_area = pi*R^2*sin(theta)^2;
- theta > 90 degrees: projected_area = pi*R^2.

This matches the orthogonal silhouette of a spherical cap: after the cap passes
the equator, its widest projected cross-section is the equator, even while its
rim shrinks. It identifies the stored convention numerically; it does not locate
the historical export code. Formula extraction from a PDF is insufficient to
silently replace deposited values. Preserve the difference explicitly.

| Selection | Sites | theta > 90 degrees | Fraction |
| --- | ---: | ---: | ---: |
| All deposited, raw angle | 2,831 | 1,754 | 61.96% |
| Unflagged, deposited corrected angle | 2,574 | 1,500 | 58.28% |
| Unflagged, raw nonnegative curvature | 2,551 | 1,500 | 58.80% |

The earlier single-valued cap height b+h*r^2/(1+sqrt(1-h^2*r^2)) describes one
hemisphere branch. A whole cap with theta > 90 degrees has multiple heights at
some radii and cannot be represented by that graph. These counts establish a
support mismatch, not a failed fit or a biological result. Restricting the data
to theta <= 90 would create a new selected population, and would still leave
the likelihood and nuisance calibration missing.

## Why the passive area sign is not a direct empirical discriminator here

This is an algebraic inference from the cap parameterization, not a source claim.
For A>0 and 0<theta<pi,

    H = sqrt(2*pi*(1-cos(theta))/A)
    (partial H / partial A) at fixed fitted theta = -H/(2*A).

Thus a negative association at fixed fitted closing angle is built into the
cap geometry for every underlying mechanism. Along a varying population curve,

    d log(H) / d log(A) = [cot(theta/2)*d theta/d log(A) - 1]/2.

The mechanical test varied prescribed material coat area while holding other
physical controls fixed. Deposited A and theta are jointly fitted outputs of
heterogeneous static sites. Neither their area label nor their errors provide
an independently controlled perturbation. A population correlation cannot by
itself reproduce or refute that mechanical derivative.

## Minimum supported comparison and stop decision

The existing FIRST_COMPARISON.md grouped descriptive H(theta) comparison is
still valid within its reviewed exploratory scope. Use one response, equal
file/cell weights and declared raw/corrected/flag sensitivities. It has already
run; do not repeat it merely because the likelihood is now better described.
Treat conditional prediction errors as descriptive, not a calibrated likelihood
or evidence for force, mechanism, single-pit kinetics or stability.

For a forward observation study, a future specification would need a parametric
3D surface covering overhangs; a declared emitter density and linkage/thickness
model; per-localization errors and background/ROI normalization; pose fitting;
and a versioned cap fitter in (A,theta). Exact spheres spanning shallow/deep caps
and a small declared nuisance sensitivity would be required controls. Without
measured nuisance inputs this would be explicitly synthetic, not a calibrated
empirical comparison. No such forward fit is authorized by this task's stop rule.

The adapter's H_sigma=hypot(3.9,12.5)/R^2 is a repository heuristic. A fixed-support
near-flat height fit has finite curvature sensitivity; its uncertainty cannot
be justified as vanishing automatically with H^2. Current adapter comments also
conflate population exclusions and segmentation curation. These are concrete
code-contract follow-ups, not reasons to invent missing calibration or silently
change historical numerical results.

Stop this empirical-bridge branch at processed-input insufficiency. No more
synthetic area/window sweeps or repeated access audits are warranted. A bounded
next implementation should enforce these observation limits in the adapter and
its consumers, preserving raw values and historical results. That prevents
unsupported precision or projection conventions from reaching future research.

## Evidence and checks

- Source: LOCMOFIT_OBSERVATION_SOURCE.md and metadata/locmofit-contract-001/.
- Preregistered local check: locmofit_contract_design.json,
  check_locmofit_contract.py, locmofit_contract_checks.json.
- Follow-up convention check: locmofit_projection_amendment.json,
  check_locmofit_projection.py, locmofit_projection_checks.json.
- Independent review: LOCMOFIT_OBSERVATION_REVIEW.md; accepted with corrected fitted-area equality wording.

No data were refit; no raw microscopy, software installation, billing, external
message, commit or push was performed. An identity failure is retained as evidence
of a convention mismatch. It is not repaired by changing the deposited tables.
