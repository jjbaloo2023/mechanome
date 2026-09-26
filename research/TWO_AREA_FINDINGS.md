# When a second area removes the ambiguity — 2026-09-23

Task `cap-two-area-001`, attempt 1. Synthetic measurement-design analysis of the
implemented zero-line-tension spherical-cap model. Numerical and independent
review results are complete and reconciled below. No experimental data or
literature novelty claim is involved.

## Main result and its conditions

Two distinct, known areas can remove the previously demonstrated force–tension
ridge **if spontaneous curvature, force, and tension are shared**, the rigidity
history is known, and enough observations are inside the unclipped region.
Separating force from spontaneous curvature additionally requires different
known rigidity values or another independent constraint. Two area values at
one constant rigidity do not suffice for all three parameters.

This is a structural statement about ideal model predictions. Merely observing
different curves is not proof that all parameters can be recovered accurately
from noisy images. Nor does measuring pits of different sizes establish that
they share force, spontaneous curvature, tension, or matched assembly state.

## A direct derivation

Write `B(t)=4*pi*kappa(t)`, `P=Fmax/kBT`, and `y_i=H_i/u` at nonzero matched
coverage `u`. The interior model is

`y_i = (B*C+P)/(2*B+sigma*A_i)`.

For two known areas with the same B and shared numerator,

`1/y_i = I + S*A_i`,

where `I=2*B/(B*C+P)` and `S=sigma/(B*C+P)`.
Thus `N=B*C+P=2*B/I` and `sigma=N*S`. Two distinct known B values then give
`C=(N2-N1)/(B2-B1)` and `P=N1-B1*C`.

Equivalently, tension follows at an interior matched state from

`sigma = 8*pi*kappa*(H1-H2)/(A2*H2-A1*H1)`.

These identities establish the ideal uniqueness result under nonzero signal
and nonvanishing denominators. They are not proposed noisy-data estimators:
division by weak signals can amplify noise, and the experiment evaluates H
directly. If B is constant, the transformation `C -> C+delta`,
`P -> P-B*delta` leaves the shared numerator unchanged.

## Failure cases that more area measurements cannot automatically fix

| Changed assumption | Consequence within the model |
| --- | --- |
| Force grows with area: `P_i=rho*A_i` | On `rho=C*sigma/2`, every area gives `H_i=C*u/2`. Adding areas does not break this exact ridge. |
| Each area has its own unknown `C_i` | This does not always destroy identifiability. With known varying rigidity, generic cases may be identifiable. But when every `C_i*A_i=2*P/sigma`, all curves sit on their own compensation ridge and a common force–tension ambiguity survives. |
| Rigidity has an unknown multiplicative scale | Scaling `(kappa(t),P,sigma)` by the same positive factor preserves every H prediction at every area. Absolute force and tension need an independent mechanical calibration. |
| Observations are clipped at the flat/closed bounds | Locally saturated values do not supply the interior parameter sensitivity. Boundary observations must be handled explicitly, and u=0 contains no force/tension information. |

Zero force and zero tension with positive C can satisfy the individual ridge
equations at both areas, but that does not create a surviving nontrivial shared
force–tension family. Zero total signal is a separate degenerate limit.

The unknown-rigidity-scale ambiguity is not resolved by an uncalibrated actin
fluorescence channel. Within this model, an independently measured rigidity
scale, independently measured nonzero tension, or another calibrated mechanical
parameter can anchor the absolute scale. Merely knowing tension is nonzero does
not help; the full parameter identifiability conditions must still be checked.

## What the experiment can support

The theory, numerical experiment, and independent review have separate owners.
The numerical work uses a declared synthetic case set, analytic derivatives,
dimensionless parameter scaling, finite-difference checks away from clipping,
and exact symmetry transformations. Any noise levels are hypothetical design
assumptions, not measured microscope performance or biological replication.

The useful next decision follows from the failure cases: test or calibrate the
assumptions that couple conditions before interpreting a multi-area fit as an
absolute force estimate. The existing static geometry data do not supply a
known within-pit rigidity history, so this result alone does not authorize a
mechanical inference on those data.

## Evidence and disposition

- TWO_AREA_THEORY.md: conditions, exact symmetries, and limiting cases.
- two_area_experiment.py / two_area_results.json / TWO_AREA_NUMERICAL.md:
  reproducible numerical checks and declared sensitivity calculations.
- TWO_AREA_REVIEW.md: independent challenge and review disposition.

The declared experiment used areas `A0=pi*60^2 nm^2` and `2*A0`, 24 matched
assembly states, and constant or known threefold-varying rigidity. Across 28
registered cases, analytic Jacobians agreed with finite differences to a maximum
scaled discrepancy of `3.70e-12`. Three focused tests passed.

| Two areas, known varying rigidity | Rank / parameter count |
| --- | --- |
| Shared parameters, generic or former single-area ridge | 3 / 3 |
| Force proportional to area, generic | 3 / 3 |
| Force proportional to area, compensation ridge | 2 / 3 |
| Area-specific C, generic | 4 / 4 |
| Area-specific C, simultaneous compensation ridge | 3 / 4 |
| Unknown global rigidity scale, generic | 3 / 4 |

Exact symmetry transformations changed curvature by at most `5.21e-18 nm^-1`
in surviving-ridge examples. The former shared single-area ridge separated by
`9.83e-4 nm^-1` with the second area. Constant rigidity gave rank 2, not 3.

At hypothetical independent curvature noise SD `1e-4 nm^-1`, local worst-direction
SD in reference-scaled parameter coordinates is 0.0802 for shared parameters,
2.28 for generic force proportional to area, and 0.272 for generic area-specific
curvature. These are conditional linearized design bounds, not individual
parameter confidence intervals or empirical microscope precision. Large values
do not justify nonlinear recovery claims; singular cases receive no finite
pseudoinverse uncertainty. See [TWO_AREA_NOISE.md](TWO_AREA_NOISE.md).

Independent review accepted the result after two corrections. Conditional on
observed curvature, inverse equations are linear: a full-rank two-level design
gives global uniqueness, while rank loss gives an affine continuum; isolated
aliases initially suggested by the theory worker are excluded. The original
figure mislabeled an absolute cutoff as relative. The corrected
[figure](two_area_comparison_v2.png) uses normalized singular values and the
correct relative cutoff. The original JSON and figure are retained; only v2
should be used for interpretation. Lead and reviewer inspected v2 and hashes.

At matched assembly state and rigidity, shared nonnegative total force predicts
nonincreasing curvature with area; area-proportional force can predict either
sign, determined by `2*rho-sigma*C`. This conditional signature merits checking
in a full membrane model. It is not an observed biological law. The next cycle
will establish whether the observable and controlled comparison carry over to
a primary published model before implementing another inverse fit.

The three specialists completed; independent review accepted the conditional
result. No production solver or biological claim has changed.
