# Cap numerical experiment — `cap-numerical-001`, attempt 1

## Registered before execution

This synthetic experiment audits the spherical-cap family used by
`curvo.evaluator_tier0._cap_energy` and `curvo.inverse._fast_H_trajectory`.
It uses `A = pi * 60^2 nm^2`; `kappa = 20` and `60 kBT`; `sigma = 0.001` to
`0.05 kBT/nm^2`; `c0 = 0` to `0.08 nm^-1`; and active force `0` to `60 pN`.
These are deliberately synthetic parameter values, not an empirical fit.

The independent calculation substitutes `m = 1-cos(psi)`. It compares the
resulting energy to the source function, uses 400, 800, and 1600 angular grids,
and, for zero line tension, compares with the exact clipped stationary point.
For positive line tension it records sampled extrema and endpoint energies;
an argmin movement alone is never called snap-through.

The dynamic check uses the source ramp, `T=24`, `kappa=20 kBT`, rigidity factor
3, `C=0.03 nm^-1`, and `sigma = 0.005, 0.02, 0.04`. It tests the proposed ridge
`Fmax/kBT = C*sigma*A/2` and a 25% off-ridge force. The test is falsified if the
analytic ridge does not reproduce `C*g(t)/2`, or the source/grid calculations
disagree beyond their angular discretization.

A registered falsification test holds `C`, `Fmax`, and `sigma` fixed at the
reference-ridge values while changing area to `A/2` and `2A`. Algebra predicts
`H/g=C/2+C*sigma*(A0-A)/(2*(8*pi*kappa(t)+sigma*A))`; these trajectories must
separate from the reference curve. Shared parameters across changed area are an
explicit mathematical assumption, not a biological claim.

## Scope and limitations

The cap family is a restricted shape ansatz. The force work term and time ramps
are model definitions in the repository; this experiment cannot establish their
biological realism, kinetic accessibility, barriers, or empirical identifiability.
The JSON result is exclusive-create so this attempt cannot overwrite a baseline.
The first exclusive result is retained as `cap_experiment.json`; the corrected
endpoint-aware rerun is `cap_experiment_v2.json`. Source grids exclude the
physical flat endpoint (`psi=0`), so grid convergence is assessed against the
analytic solution clipped to that same domain; the physical endpoint bias is
reported separately. For the fixed source lower cutoff `psi=0.02` and flat
radius `60 nm`, that irreducible physical-boundary bias is
`2*sin(0.01)/60 = 3.33328e-4 nm^-1`; increasing grid count alone cannot remove
it.

## Results

The independent reduced energy agrees with `_cap_energy` within
`4.14e-11 kBT` on the registered source points. With zero line tension,
the stationary point is unique and stable when interior: the curvature-only
case (`c0=0.04`) and its fixed-rigidity force equivalent (`F=41.36 pN`) both
give `H=0.0137931 nm^-1`. Under the repository's rigidity ramp, that ordinary
fixed-rigidity equivalence separates. This does not establish general dynamic
identifiability: the exceptional tuned dynamic ridge remains. Its forces
has forces `3.48962`, `13.95847`, and `27.91695 pN` for sigma `0.005`, `0.02`,
and `0.04`; all three source 400-grid trajectories are identical (maximum
pairwise spread `0`) and equal the independent ridge trajectory up to the
400-point angular grid error.

Against the same-domain continuum result, the maximum curvature errors are
`6.09e-5`, `2.92e-5`, and `1.38e-5 nm^-1` for 400, 800, and 1600 points.
This regular refinement, plus the zero-line-tension convex reduction, provides
no evidence for a snap-through caused by a grid argmin. With positive line
tension, lambda `1 kBT/nm` has a single sampled interior maximum and lower
flat endpoint; lambda `2 kBT/nm` has no sampled interior extrema and lower
closed endpoint. Those endpoint/basin statements apply only to the listed
synthetic cases.

The 25% force perturbation moves the tuned trajectory by `1.36e-4` to
`8.65e-4 nm^-1` over the three tensions. Holding each tuned case's `C`, force,
and sigma across area changes separates it from the reference trajectory by
`2.76e-4` to `2.81e-3 nm^-1` over the registered area/tension cases; the area
formula matches direct evaluation below `7e-18 nm^-1`.
