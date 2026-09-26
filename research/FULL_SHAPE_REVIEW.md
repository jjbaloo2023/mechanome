# Independent review: cap area sign versus a surrounding membrane

Task `cap-full-shape-review-001`, attempt 1. The initial independent challenge preceded reading the new specialist notes.
The lead had received it by the observed 11:23:20 UTC clock. Worker-stated
11:24/11:22 timings were not verified and are not used as activity telemetry. This note reviews arXiv:1604.08629v1 only; it does not
mix in the later PNAS version. It makes no biological, novelty, or empirical
precision claim.

## Decision

The cap's negative area response is a useful **passive, local-curvature
benchmark**, but it cannot by itself distinguish fixed-total-force from
area-proportional-force scaling after the surrounding membrane and neck are
admitted. The smallest justified implementation is the force-free linear patch
calculation, used as a convention and solver check. A force-discrimination
claim should wait for a specified load support, force-control protocol,
mechanical reaction/boundary condition, area definition, branch-selection rule,
and measurement functional in a nonlinear full-shape model.

This conclusion is stronger than saying that the spherical cap is inaccurate.
The comparison is not identified as posed: the source paper's force experiment
does not hold either a common total force or a common force density while coat
area varies, and its plotted observables are not interchangeable.

## Primary-source audit and mapping

The checked primary source is [Hassinger et al., arXiv:1604.08629v1
(28 April 2016)](https://arxiv.org/html/1604.08629v1). Main Eq. (1), repeated as
S11, uses `W=k(H-C)^2+kbar K` and explicitly says its `k` is twice the usual
Helfrich modulus. Matching the repository convention
`kappa/2*(2H-c0)^2` therefore requires

`k = 2*kappa`, and `C_Hassinger = c0/2`.

The factor two must remain attached to the symbol names: the repository cap
formula uses its `c0` (called `C` in the cap summaries), whereas the paper's
`C` is half that value. With `B=4*pi*kappa`, zero force, full coverage, and
`A=pi*R^2`, the cap prediction is

`H_cap/(c0/2) = 1/(1+(R/ell)^2/8)`, `ell=sqrt(kappa/sigma)`.

Main Eq. (2)/S12 is the nonlinear shape equation. S18, S22, S24, S26, and S27
give the axisymmetric first-order system; S28 fixes regularity at the pole and
joins the finite patch to a flat boundary with prescribed reservoir tension.
S29 prescribes pole displacement for pulling and S30 prescribes pole curvature
for pinching. The source distinguishes local mean curvature from shape and
depth; Fig. 4B and Fig. S6 plot **mean curvature at the bud tip**, not a
cap-fitted curvature. Its `A_coat` is coat surface area, while S35/S36 also use
the total simulated membrane area and S44 uses whole-patch excess area.

The force is a density `f` in Eq. (2); the supplement states that total force is
its integral over the applied area. For Fig. 8/S10 the force is uniform over the
coat, but the authors prescribe pole depth and let the boundary-value solver
determine the force (supplement simulation methods, PDF p. 29). While the coat
area is subsequently increased, the tip is held at `Z=-200 nm`; the reported
upper branch is approximately 6 pN, rather than an experiment comparing a
declared shared total force with a declared shared density. Thus Fig. 8 cannot
label either cap force-scaling hypothesis as correct.

Two v1 source cautions matter for any nonlinear reproduction. Main Eq. (3) has
the opposite sign for the spontaneous-curvature contribution to the tension
gradient from S13/S14/S27/S32c/S40c. The supplement is internally consistent
with `lambda_,alpha = -partial W/partial x^alpha` for
`W=k(H-C)^2`, but this discrepancy should be resolved from the variational
derivation before implementing the nonlinear system. It does not alter the
present linear calculation because that tension variation is quadratic in the
small curvature amplitude. Also, Fig. S6's caption calls its reproduced
intermediate case `0.002 pN/nm`, while Fig. 4 and the main text specify
`0.02 pN/nm`; those cases must not be blended.

## Independent small-slope check

For

`E = integral [kappa/2*(Delta h-c0(r))^2 + sigma/2*|grad h|^2] dA`

with `sigma>0`, homogeneous `kappa`, no pressure or force, a circular step
`c0(r)=c` for `r<R`, regularity at the origin, and `h -> 0` at infinity, the
Euler-Lagrange equation is

`kappa*Delta(Delta h-c0)-sigma*Delta h=0`.

Writing `ell=sqrt(kappa/sigma)` and `x=R/ell`, the regular/decaying solution is

`h_in/(c ell^2) = x K1(x) I0(r/ell)-1`,

`h_out/(c ell^2) = -x I1(x) K0(r/ell)`.

It makes height, slope, bending moment `Delta h-c0`, and its normal derivative
continuous at the step. The apex local mean curvature, coat-average mean
curvature, and reservoir-referenced depth are respectively

`H_tip/(c/2)=x K1(x)`,

`H_coat_mean/(c/2)=2 I1(x) K1(x)`,

`d_reservoir/(c ell^2)=1-x K1(x)`.

Since `d[x K1(x)]/dx=-x K0(x)<0`, local apex curvature decreases as projected
patch area grows, while reservoir-referenced depth increases. This preserves
the cap's passive curvature sign but also proves that increasing depth is not
increasing curvature. The quantitative transfer is poor: the membrane tip
curvature decays exponentially at large `x`, the cap result decays algebraically,
and the coat-average is a third response.

Depth requires an explicit reference. The membrane's edge-to-tip depth is

`d_edge/(c ell^2)=x K1(x)*(I0(x)-1)`.

It agrees with the cap edge-to-tip depth `x^2/[4*(1+x^2/8)]` at leading small
`x` order, but approaches 1/2 rather than 2 and is not globally monotone. A
figure may show reservoir depth and cap depth together only if it does not imply
a same-reference quantitative comparison; a corrected view should include the
membrane edge-referenced curve.

## Numerical-artifact review

`linear_patch_benchmark.py` and `linear_patch_results.json` were inspected.
The six registered cases use `x=0.1,0.5,1,2,5,10` and `c*ell=0.01`. The maximum
reported membrane slope is 0.004982, so the declared small-slope calculation is
self-consistent for these synthetic inputs. The Green-function identity agrees
to `5.13e-16`. An independently discretized radial finite-volume solve at
40/80/160 cells per `ell`, with a boundary 20 `ell` beyond the coat edge,
converges monotonically in every case; its maximum finest-grid normalized apex
error is `3.97e-6`. The three focused tests passed before review.

These checks validate the implemented linear boundary-value problem, not the
nonlinear paper model. The code's `generalized_shear` residual is hard-coded as
an analytic identity and is correctly disclosed as not an independent numerical
check. The step in `c0` is distributionally legitimate but idealized; smoothing
it as in the paper can change edge-local observables. Projected and surface coat
area agree only to leading order. The infinite-domain result requires positive
tension and contains no neck, overhang, stiffness jump, pressure, branch switch,
or snap-through.

Most importantly, a nonzero net normal force cannot simply be added to this
infinite, flat-at-infinity tension problem: its long-wavelength response needs a
reaction and generally produces a logarithmic far field. A finite boundary,
balanced load, or another explicit reaction model is required. Fixed total
force additionally does not determine its spatial traction profile, and uniform
force density over a growing coat is a separate assumption. The current
force-free benchmark therefore supplies no evidence that area-curvature sign
can discriminate those force scalings.

## Required interpretation of the source figures

Fig. S6 states that in the high-tension force-free case tip curvature falls
toward zero as coat area grows, while in the low-tension case it stays near the
coat spontaneous curvature. The intermediate case has multiple branches and a
snap-through in Fig. 4. These results support using tip curvature as a defined
observable and show that its response depends on tension and branch. They do not
establish a universal monotone law, and the force-controlled Fig. 8 uses a
different protocol. Cap-fitted curvature, invagination depth, neck radius, coat
area, and total area must remain separate columns in any later comparison.

## Disposition

Accept the linear patch calculation after adding or clearly separating the
same-reference depth comparison. Use it as the smallest forward benchmark and
as a validation target for a later solver: reproduce the Bessel solution in the
small-amplitude, homogeneous, force-free limit before attempting Fig. 4-like
continuation. Do not interpret its passive sign as force-scaling evidence.

Before the nonlinear step, specify: (1) paper versus repository curvature
conventions; (2) projected versus material coat area; (3) finite-domain boundary
conditions and force reaction; (4) fixed total force versus fixed force density,
including support; (5) continuation/branch selection; and (6) the measured
functional—tip `H`, coat-average `H`, cap fit, depth with reference plane, or
neck radius. Resolve the Eq. (3)/S13 sign discrepancy by a fresh variation.

The lead observed the completed review by 2026-09-23 11:32:35 UTC
(worker reported completion at 11:32). `FULL_SHAPE_SOURCE.md` correctly
preserves both v1 inconsistencies and version-specific locators.
`FULL_SHAPE_MAPPING.md` correctly keeps the factor-of-two convention, the four
sharp-interface conditions, the surface/projected-area distinction, and the
force-free scope. `linear_patch_comparison_v2.png` is visually legible and
corrects the depth-reference problem; its derived slope-integral check agrees to
`1.11e-16` without altering the registered solution. `FULL_SHAPE_FINDINGS.md`
accurately limits the result to a passive benchmark, treats all observables
separately, and selects validation before nonlinear implementation. **Accepted
for this cycle with no remaining blocking correction.**
