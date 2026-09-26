# What changes when the surrounding membrane is included?

2026-09-23; `cap-full-shape-001`, attempt 1. This cycle resumed from the saved
two-area checkpoint after the user reported a computer update. No intervening
research activity was verified.

## Result

The passive area-curvature sign survives a controlled small-deformation test,
but its magnitude depends strongly on geometry and on which curvature is
measured. A growing patch can become deeper relative to the distant membrane
while its apex curvature decreases. This is a model result, not a biological
discovery or a reproduction of nonlinear budding.

We derived a membrane model that includes the uncoated exterior, checked it
with an independent finite-volume calculation, and compared it with the
existing spherical cap. The calculation is force-free: it does not validate
using the cap's area response to discriminate active force mechanisms.

## Matched inputs and distinct observables

The calculation holds bending modulus, positive reservoir tension and imposed
coat curvature fixed, and increases a circular patch radius R. Define
`ell=sqrt(kappa/sigma)` and `x=R/ell`. The synthetic amplitude is `c*ell=0.01`,
where c is the repository's spontaneous **total** curvature. The preferred
mean curvature is c/2. The numerical cases are x=0.1, 0.5, 1, 2, 5 and 10.

For the energy

`E = integral [kappa/2*(Delta h-c*patch)^2 + sigma/2*|grad h|^2] dA`,

regularity at the center and flatness at infinity give the following responses.
I and K denote modified Bessel functions. These formulas are our derivation;
details and interface conditions are in [FULL_SHAPE_MAPPING.md](FULL_SHAPE_MAPPING.md).

| Observable | Surrounding-membrane model | Spherical cap |
| --- | --- | --- |
| Apex mean curvature / (c/2) | x K1(x) | 1/(1+x^2/8) |
| Mean curvature over the coat / (c/2) | 2 I1(x) K1(x) | Same as cap apex |
| Edge-to-tip depth / (c ell^2) | x K1(x) [I0(x)-1] | x^2/[4(1+x^2/8)] |
| Reservoir-to-tip depth / (c ell^2) | 1-x K1(x) | Exterior reservoir absent |

At x=1, the membrane's normalized apex curvature is **0.602**, its coat mean is
**0.680**, and the cap predicts **0.889**. At x=5 these become 0.0202, 0.197 and
0.242. Thus the measurement definition can matter as much as the choice of model.

Both apex-curvature responses decrease. Reservoir depth increases, while
edge-referenced membrane depth is not globally monotone: it is 0.531 at x=5
and 0.525 at x=10. Comparing different depth references would obscure this.
The [reviewed figure](linear_patch_comparison_v2.png) matches the edge reference
for its solid depth curves and shows reservoir depth separately as a dashed line.

Projected coat area and surface area agree only to the retained small-slope
order. The largest membrane slope in these cases is 0.004982. Sharp patch edges,
uniform stiffness and first-order uniform tension are deliberate approximations.
The calculation has no neck, overhang, applied force or snap-through. Zero
tension is a singular limit for infinite-reservoir depth, even though apex
curvature has a finite limit.

## Source comparison and an implementation issue

The accessible [Hassinger arXiv v1](https://arxiv.org/html/1604.08629v1) defines
local tip curvature and a membrane boundary-value problem. Its bending
convention maps as `k_source=2*kappa_repo`, `C_source=c_repo/2` (Eq. 1).
Its main Eq. 3 and supplement S13/S27 disagree on the curvature-gradient sign
in the tension equation. This conflict must be addressed explicitly before
nonlinear implementation; it does not affect the first-order benchmark.
Version-specific locators and another caption inconsistency are preserved in
[FULL_SHAPE_SOURCE.md](FULL_SHAPE_SOURCE.md). We have not resolved the discrepancy
against the published version or independently reproduced its nonlinear figures.

## Numerical evidence and review

- Independent radial finite-volume equations used 40, 80 and 160 cells per ell.
  Every registered case converged toward the closed form; the maximum finest-grid
  normalized apex error was 3.97e-6. The finite boundary was R+20 ell.
- An independent Green-integral evaluation agreed to 5.14e-16. Interface height,
  slope and moment matched to roundoff. The analytic shear check is an identity,
  not an independent discretization check.
- Three focused tests passed in 4.18 seconds. The depth correction was separately
  checked by integrating slope; the maximum difference was 1.12e-16.
- Original results and the first figure are preserved. Review revision 2 adds
  an edge-referenced depth comparison without changing the numerical solution.
  Source hashes are recorded, and the lead inspected both rendered figures.

Independent review accepted this cycle with no remaining blocking correction;
see [FULL_SHAPE_REVIEW.md](FULL_SHAPE_REVIEW.md). The source sign conflict remains
explicit for future nonlinear work, rather than being silently resolved.

## Decision

Use apex curvature as the first forward-model comparison, and retain coat-mean
curvature and both depth references as separate outputs. A future image-based
comparison must apply the same local fitting window to simulated and measured
profiles; pointwise curvature is not automatically a microscope observable.

Next: resolve the tension-gradient convention by a variational check, then
implement the smallest passive axisymmetric solver and require it to approach
this analytic solution at small amplitude. Only after residual, boundary,
mesh, edge-width and domain checks pass should it enter larger-deformation
regimes. No inverse fitting, force-mechanism selection or biological inference
is justified by the current comparison. Any later nonzero-net-force extension
also needs a specified finite boundary or balancing reaction: adding a net load
to the infinite flat-at-infinity model is not automatically well posed.
