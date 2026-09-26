# Independent review: LocMoFit observation contract

**Task:** `locmofit-review-001`, attempt 1  
**Registered cycle time:** 2026-09-25 03:46:50 UTC  
**Review checkpoint:** 2026-09-25 03:50 UTC  
**Scope:** source-to-observable contract only; no raw localization download,
refit, synthetic sweep, mechanism fit, or biological inference.

## Disposition

**Accept a descriptive cap-output contract; reject an empirical LocMoFit
likelihood claim from the available processed tables.** The corrected vertical
least-squares calculation remains a useful deterministic sensitivity check, but
it is neither equivalent to nor presently calibratable against the 3D
localization likelihood used for the deposited fits.

The insufficiency is concrete. The tables contain cap geometry outputs and
curation fields, but not the retained localization coordinates, localization
counts and per-point uncertainties, segmentation/ROI support, fitted pose and
background nuisance values, likelihood values, or parameter covariance. The
historical LocMoFit/SMAP code revision and complete per-analysis settings are
also unpinned. These omissions prevent replaying the likelihood, propagating
uncertainty, or fitting a nonspherical mechanical profile through the same
observation operator.

There is also a geometric mismatch independent of the missing noise model. A
single-valued height function `z(r)` cannot represent a whole spherical cap
beyond a hemisphere, because an overhanging cap has more than one height at
some projected radii. The checked processed schema has 1,754 of 2,831 raw rows
with `theta>90 degrees`; after the deposited corrections and unflagged primary
selection, 1,500 of 2,574 rows (58.275%) remain above 90 degrees. Thus the
vertical-profile surrogate cannot be promoted to a whole-structure observation
model for most of that empirical cohort even before localization error is
considered.

## What the primary observation model does

The checked Mund et al. Methods describe maximum-likelihood fitting of 3D
localization coordinates to a parameterized hollow-spherical-cap probability
density. The intrinsic cap parameters are surface area `A` and closing angle
`theta`. Centre position and orientation are nuisance parameters. The model PDF
also includes extra uncertainty and background weight. Discrete spiral or
spherical-Fibonacci surface points approximate the cap surface when constructing
the PDF. Manually retained isolated structures define the empirical support;
the methods do not specify a common physical radial window across sites.

The exact historical executable is unresolved. The paper identifies LocMoFit
and SMAP but does not pin a release, commit, settings file, point count, or full
optimizer configuration. Current official documentation and the public SMAP
`master` tree at commit `d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6`
identify a `models.sphericalCap3D_surfaceArea` model. The documentation calls
the package LocMoFit 1.1.0 while the checked fitter header says 1.0.1, last
updated in 2022. These current artifacts cannot be substituted silently for
the paper's historical implementation.

The version boundary is empirically material. The pinned current model's
`getDerivedPars` returns `pi*R^2` for every positive closing angle, whereas the
deposited column follows the checked piecewise cap silhouette given below.
That is a current-code/deposit mismatch, not evidence that either historical
data or paper is wrong. It strengthens the requirement to preserve deposited
values and to call any use of the pinned current implementation a new synthetic
operator rather than a reproduction of the 2023 export.

For a generic surface model `S(phi)` with latent emitter density `rho` and a
localization `y_i`, the relevant likelihood has the schematic form

\[
p(y_i\mid\phi,\eta)=
(1-\beta)\int_{S(\phi)}
N[y_i;x,\Sigma_i(\eta)]\rho(x\mid\phi,\eta)\,dA
+\beta p_{\rm bg}(y_i\mid\eta),
\]

or its documented discrete-model-point approximation. `phi` contains the cap
geometry and `eta` contains pose, blur/extra uncertainty, background, support,
and related nuisance choices. This equation is a statement of the information
that must be fixed, not a claim that the unavailable historical code implements
this exact notation.

## Why vertical least squares is not that likelihood

The accepted synthetic surrogate minimizes vertical residuals between a known
axisymmetric profile and a single-valued cap height over a chosen radial or
material-area measure. It corresponds only to a much narrower observation
story: projected radius is effectively error-free, one height is observed per
radius, vertical errors are independent and homoscedastic, support and weights
are imposed, pose is already known, and there is no background, label thickness,
linkage blur, latent surface sampling, or ROI truncation.

A 3D localization likelihood instead scores a point cloud against a normalized
spatial PDF. With anisotropic localization error, the effective normal error
depends on surface orientation through quantities such as
`n^T Sigma_i n`; a vertical residual does not reproduce this. Surface-point
density and the PDF normalization also change as cap area and support change.
Nearest-surface or vertical least squares could arise only under additional
small-noise and sampling approximations, none of which are calibrated by the
processed tables. Agreement under uniform-r and uniform-material-area weights
therefore does not cover the relevant empirical nuisance model.

The whole-nominal-coat synthetic fits are not a shortcut to the primary model.
Their support changes with the simulated coat, while empirical support is an
unknown segmented/manual ROI containing a stochastic set of labeled
localizations. Fixed physical windows make the synthetic area comparison fair,
but they are not documented as the LocMoFit support. Neither choice reproduces
the empirical operator.

## Fitted, derived, corrected, and unavailable quantities

The categories must remain separate:

| Category | Quantity | Review consequence |
| --- | --- | --- |
| Localization input, not deposited in the fit tables | retained `x,y,z` coordinates; per-localization precision; point count; segmentation/ROI | Required to evaluate or replay the point-cloud likelihood. Modal precision values cannot reconstruct these inputs. |
| Intrinsic fitted geometry | cap surface area `A`; closing angle `theta` | They are a joint fit and require their covariance for calibrated residual weighting. |
| Fitted nuisance, absent from the processed tables | centre, orientation, extra uncertainty/blur, background weight; exact bounds/settings unresolved | They can trade off with geometry and cannot be held fixed retroactively. |
| Algebraically derived cap geometry | `R=sqrt[A/{2*pi*(1-cos theta)}]`, `H=1/R`, rim length, and projected-area convention | These are not independent observations. Reusing several as separate evidence double-counts one fit. |
| Deposited post-fit curation | corrected `H` and `theta`; `disconnected_sites`; identifiers and cell/file groups | Corrections and flags must be preserved as supplied and analyzed through declared sensitivities; they are not uncertainty estimates. |
| Missing fit diagnostics | joint covariance/Hessian, likelihood, residual, convergence record, nuisance estimates | No per-site precision, likelihood comparison, or covariance-aware test is supportable. |

The repository adapter violates this boundary if its `H_sigma_inv_nm` is read as
data. It sets
`sigma_H=hypot(3.9 nm,12.5 nm)/R^2`, using modal localization precisions as a
radius-error surrogate. This is an adapter heuristic, not a deposited LocMoFit
uncertainty or propagation through the joint nonlinear fit. Its statement that
near-zero curvature is thereby well determined is not established and should
not be used for likelihood weighting. The adapter also describes
`disconnected_sites` as multi-structure fits, while the audit found that this
conflates distinct source filtering and cannot reproduce 18 supplied flags from
the stated curvature thresholds alone.

## Shared-error and area interpretation

Because `A` and `theta` are jointly fitted and `H` is computed from them,

\[
H=\sqrt{2\pi(1-\cos\theta)/A}.
\]

The repository audit verifies this identity across all 2,831 rows to a maximum
relative discrepancy below `6.6e-8`. An `H`-versus-`theta` comparison is
therefore a re-expression of how fitted `A` and fitted `theta` co-vary. It is
not a regression between independent measurements. Adding `R`, rim length, or
projected area as further responses does not add independent evidence.

The fitted cap area `A` also must not be equated automatically with the
mechanical model's controlled spontaneous-curvature patch area. Equality is
a justified target only with a matched exact-cap observation model; finite
noisy fits need not recover it exactly. For a nonspherical membrane, no such
equality is guaranteed: fitted `A` is a likelihood- and support-dependent
pseudo-parameter. Coat labeling, missing localizations, background,
segmentation, pose, and model mismatch can all move it. The processed tables
provide no independent coat-area calibration with which to test the two-area
mechanical prediction.

Indeed, even the negative partial slope at fixed fitted angle is imposed by the
cap parameterization:

\[
\left.{\partial H\over\partial A}\right|_\theta=-{H\over2A}.
\]

It cannot test the passive controlled-area sign. Along an observed population,

\[
{d\log H\over d\log A}={1\over2}\left[
\cot(\theta/2){d\theta\over d\log A}-1\right],
\]

so any marginal slope mixes the joint fitted-angle pattern with the algebraic
cap constraint, population heterogeneity, and shared fit error.

The deposited projected-area convention also confirms why a whole cap cannot
be treated as a rim-bounded height graph after it overhangs. Independent schema
checks found exact agreement across all 2,831 rows (maximum relative discrepancy
`6.56e-8`) with the orthogonal silhouette

\[
A_{\rm proj}=\begin{cases}
\pi R^2\sin^2\theta,&\theta\leq90\;\mathrm{degrees},\\
\pi R^2,&\theta>90\;\mathrm{degrees}.
\end{cases}
\]

The unqualified rim-disk formula fails for 1,744 rows. This projection is still
derived from the fitted cap and does not create a new independent measurement.

## Minimum empirically supportable comparison

With the current processed tables, the strongest supportable analysis is the
already bounded, grouped descriptive comparison in fitted-cap output space:
describe the joint `A_hat, theta_hat` pattern (or one algebraically equivalent
`H_hat` response against `theta_hat`) across held-out file/cell groups, preserve
the deposited corrections and flags with declared sensitivities, and use no
adapter-derived uncertainty weights. Report it as cross-cell transfer of a
static fitted-geometry pattern. It does not validate a full-profile observation
map, a controlled coat-area response, a within-pit trajectory, or a mechanism.

No new empirical comparison between the passive membrane profiles and the
LocMoFit tables is justified from these fields. Binning or regressing fitted
`H` against fitted `A` would recycle the same joint fit and mistake an estimated
cap parameter for an independently controlled area. Restricting to
`theta<=90 degrees` would remove the height-graph impossibility but would not
restore the missing point cloud, likelihood settings, covariance, or
longitudinal control.

If a future exact observation operator becomes available, the smallest forward
validation should be registered before looking at mechanism results:

1. Pin the executable revision and complete settings, including cap model-point
   construction/count, pose conventions, ROI/support, localization-error and
   extra-blur model, background distribution/weight, bounds, initialization,
   and optimizer.
2. Generate one exact spherical-cap control at known `A,theta` with declared
   emitter sampling, per-point uncertainty, point count, ROI, and background;
   require recovery of the joint fitted parameters and record covariance or
   repeated-simulation spread.
3. Apply that same fixed operator to one predeclared passive membrane profile,
   with at most a small registered nuisance sensitivity. Compare recovered
   `A_hat,theta_hat` to the deterministic vertical-fit result and keep the
   distinction between true mechanical patch area and fitted cap area.

That would validate a current or pinned forward operator. Without the
historical revision and settings, it still would not reproduce the deposited
2023 fits exactly. Raw localizations and support metadata would be required for
an empirical replay; this review does not recommend downloading them within the
current bounded cycle.

## Source and artifact checks

Reviewed inputs were `research/NEXT_CYCLE.md`, `research/DATA_AUDIT.md`,
`research/FIRST_COMPARISON.md`, `research/CAP_OBSERVATION_FINDINGS.md`, the
accepted observation theory/review, `validation/realdata/ingest_smlm_locmofit.py`,
`research/data_audit.json`, the source specialist's
`research/LOCMOFIT_OBSERVATION_SOURCE.md`, and the lead's registered schema
checks as communicated during review. The source specialist's primary locators
are Mund et al. (2023) Methods, Wu et al. (2023), current official LocMoFit
documentation, and the current public SMAP source tree. Historical-version and
settings gaps remain explicit.

The contract draft's proposed next action is appropriately bounded if it begins
with a read-only consumer inventory: mark `H_sigma_inv_nm` explicitly as a
heuristic with provenance, prevent it from entering a calibrated likelihood by
default, correct the curation/filtering comments, and preserve deposited
geometry and historical outputs. Do not silently replace the field, recompute
projected area with the current-code convention, or migrate old results. This
code-contract cleanup can prevent unsupported precision claims; it cannot make
the missing empirical observation inputs appear.

**Stop condition reached:** the processed inputs are sufficient for a checked
descriptive cap-output contract and insufficient for the intended calibrated
full-profile-to-LocMoFit comparison. Additional synthetic vertical-fit sweeps
would not repair the missing observation contract.
