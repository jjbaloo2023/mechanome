# Why ideal shape may not separate coat curvature from pulling

2026-09-26; `load-identifiability-001`, attempt 1. This is a conditional result
for a linear membrane model, not a clathrin mechanism discovery or an empirical
force estimate. The [design](load_identifiability_design.json) was frozen before
calculation; [theory](LOAD_IDENTIFIABILITY_THEORY.md),
[numerical records](load_identifiability_results_001.json), and
[independent review](LOAD_IDENTIFIABILITY_REVIEW.md) give the evidence.

## Result and its meaning

Even a perfect complete membrane profile cannot generally separate an unknown
spatial coat-curvature field from an unknown balanced normal-load field. In this
model, changing tension alone does not remove that ambiguity. Independently
prescribing their spatial forms can make their amplitudes distinguishable, but
the two simple geometric summaries tested here carry nearly the same information
about the two sources. Structural identifiability is therefore only the first
step toward a usable measurement.

This extends the earlier [cap compensation result](CAP_FINDINGS.md) to a spatial
source ambiguity in the full membrane operator. It is not another area sweep.

## Exact ambiguity, including force balance

On an infinite flat reservoir, assume a shallow axisymmetric membrane with
known positive uniform rigidity `kappa` and tension `sigma`, regular at the
origin and with height and slope vanishing at infinity. The declared energy is

`E = integral [kappa/2*(Delta h-c)^2 + sigma/2*|grad h|^2 - f*h] d^2x`.

Here `c` is preferred total curvature, `H=Delta h/2` is mean curvature, and
positive signed normal traction `f` does work in the positive-height direction.
Variation gives

`(kappa*Delta^2 - sigma*Delta) h = kappa*Delta c + f`.

For any smooth localized axisymmetric change `delta c`, choosing
`delta f = -kappa*Delta(delta c)` leaves the whole shape unchanged. The added
load has zero integrated force. The same pair of source changes cancels for
any tension at fixed rigidity. More precise shape measurements, or more tension
conditions alone, cannot identify unrestricted sources under these assumptions.
A net unbalanced force would require a stated reaction or finite boundary; it
cannot be added silently to this infinite-reservoir calculation.

## What changes when source shapes are independently fixed?

Before inspecting rank, we chose a Gaussian curvature patch of known width `a`
and a normal load comprising equal/opposite normalized Gaussians of widths `a`
and `b=2a`. The broader component explicitly supplies the balancing reaction.
`F` is their signed component amplitude; net force is zero, and `F` is not the
integrated positive-lobe force. The patch width is an imposed control, not a
public fitted cap area.

Their complete response fields are linearly independent. For just apex curvature
and depth referenced to radius `a`, the registered calculation used
`a=sqrt(kappa/sigma)=1`, `b=2`, `kappa=sigma=1`. The dimensionless response matrix is:

| Measured summary | Coat amplitude `C*a` | Load amplitude `F*a/kappa` |
| --- | ---: | ---: |
| `a*H_apex` | 0.26927234 | -0.02234464 |
| `[h(a)-h(0)]/a` | 0.11437934 | -0.01009604 |

Its determinant is `-1.62819e-4`, resolved relative to the propagated quadrature
error diagnostic `4.74e-14`. The columns are nevertheless nearly antiparallel:
the sine of their angle is `0.02270`; the condition number on these declared
axes is about `529`. These are scaling-dependent numerical diagnostics. They
do not supply measurement noise, posterior precision, or a universal imaging
threshold. Full-profile rank does not imply every pair of summaries has rank two.

Only two basis responses and one tighter-precision repeat ran. Matrix values
changed by at most `3.47e-18`; an independent exponential-integral apex formula
agreed within `5.56e-17`; the integrated unit load was `-6.51e-18`. Numerical
quadrature estimates are not rigorous interval bounds. Basis coefficients are
linear derivatives, not finite-amplitude physical states. The
[checker](check_load_identifiability.py) ran under a 45-second process timeout
and finished in approximately 0.004 seconds of recorded calculation time.

## One prospective way to break the unrestricted ambiguity

Measure two registered complete profiles at distinct, independently calibrated
rigidities `kappa_1` and `kappa_2`, with known tensions and the **same** curvature
and traction fields, reaction geometry and boundary conditions. Define
`S_j=(kappa_j*Delta^2-sigma_j*Delta)h_j`. Then

`Delta c = (S_2-S_1)/(kappa_2-kappa_1)`, and `f = S_1-kappa_1*Delta c`.

Localization/decay fixes the harmonic freedom in `c`. This is a mathematical
protocol, not a demonstrated way to vary rigidity independently in a living pit.
It requires tests that the perturbation preserves the sources, calibrated
mechanical and image scales, registered geometry, and an observation model for
spatial derivatives. An independent spatial traction measurement is another
route described in the theory note; knowing only net force is insufficient.

Both scalar summaries remove a constant height offset, but unknown center,
lateral/height scale, widths or tension-to-rigidity ratio introduce nuisances.
Scaling `kappa`, `sigma` and `F` together leaves shape invariant, so an unknown
mechanical scale prevents absolute load estimation. None of the processed public
cap tables supplies the controls needed to turn this result into a calibrated
mechanism comparison.

## Decision

Stop this bounded mathematical branch at its reviewed ambiguity and rank result.
The next informative step is an independent-control feasibility assessment for
a public experimental system: can its observations and perturbations actually
satisfy the invariance and calibration requirements above? Increasing synthetic
resolution or repeating cap rankings would not answer that question. The
[queued task](NEXT_CYCLE.md) limits that assessment to two primary studies and
requires a stop if the necessary controls or accessible data are absent.
