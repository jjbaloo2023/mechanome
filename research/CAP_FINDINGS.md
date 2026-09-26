# Collaborative cap-model findings — 2026-09-23

Three specialists worked concurrently on analytical theory, numerical checks,
and primary literature; the lead independently derived the reduction, sent the
compensation hypothesis to the workers, and reviewed the computational checks.
This is a model-conditional result, not a biological measurement. Literature
novelty is unresolved; the antecedent cap-budding theory is established.

## Exact compensation survives changing coat stiffness

For the implemented fixed-area spherical cap, let `u(t)` be the shared coat/force
ramp, `C` the spontaneous-curvature plateau, `F` the force plateau in pN,
`kappa(t)` the effective rigidity in kBT, `sigma` tension in kBT/nm², and `A` the
coat area in nm². With zero line tension and an interior optimum,

`H(t) = u(t) [4*pi*kappa(t)*C + F/kBT] / [8*pi*kappa(t) + sigma*A]`.

On the compensation condition

`F = kBT*C*sigma*A/2`,

the result simplifies exactly to `H(t)=C*u(t)/2`, for **any prescribed rigidity
history**. Different force/tension combinations therefore give the same entire
curvature trajectory. More precise curvature alone cannot identify the location
on this ridge. The finite source grid clips the initial flat state and quantizes
curvature; those numerical limitations must be separated from the exact result.

For the registered synthetic example `A=pi*60² nm²`, `C=0.03 nm⁻¹`, and
`kBT=4.114 pN nm`:

| Tension (kBT/nm²) | Force (pN, rounded) | Exact plateau H (nm⁻¹) |
| --- | ---: | ---: |
| 0.005 | 3.49 | 0.015 |
| 0.020 | 13.96 | 0.015 |
| 0.040 | 27.92 | 0.015 |

This is an exceptional exact force–tension ridge, not proof that all geometry-only
parameter inference is structurally impossible. Known varying rigidity can
generically separate parameters away from it, with enough distinct interior
states. Unknown rigidity scale, clipping, noise and model mismatch add further
limitations. Posterior-width checks do not replace this structural analysis.

## A concrete way to challenge the equivalence

Keep each candidate's `C`, `F`, and `sigma` fixed and change the known coat area
from its reference value `A0`. The same family predicts

`H_A/u = C/2 + C*sigma*(A0-A) / [2*(8*pi*kappa(t)+sigma*A)]`.

The candidates coincide at A0 but can separate at other areas. This supplies a
conditional two-area synthetic identifiability experiment. It is not yet a
biological experiment: if force or spontaneous curvature also changes with area,
the inference must include that change, and compensation can persist. An
independently measured tension would also constrain the ridge. An actin-intensity
label alone is not calibrated force.

## The default inverse cannot produce a fold instability

With `x=sin(psi/2)`, `a=sqrt(A/pi)`, the cap energy is

`E(x)=Q*x²-L*x+b*sqrt(1-x²)+constant`,

where `Q=8*pi*kappa+sigma*A`, `L=a*(4*pi*kappa*c+F/kBT)`, and
`b=2*pi*lambda*a`. For nonnegative tension and positive rigidity, the default
inverse's `lambda=0` gives `E''(x)=2Q>0`: one constrained minimum, no competing
minima or fold. Smooth input parameters give a continuous optimum; finite-grid
steps or hard stage labels are not physical snap-through.

Positive line tension can create a barrier and metastability. When `0<b<2Q`,
the interior fold is `x_f=sqrt(1-(b/(2Q))^(2/3))`, `L_f=2Q*x_f³`.
At zero tilt L=0, endpoint energy equality is b=Q, while flat-state loss of
stability is b=2Q. A global-minimum switch and local stability loss are different
events. None of these cap calculations establishes membrane scission.

Hassinger's published snap-through result uses a richer axisymmetric membrane
boundary-value problem with surrounding membrane and neck geometry. Akamatsu's
model describes a load-adapting filament network. Neither is reproduced by
renaming subsets of this cap model's free parameters. Primary locators and
access limits are in CAP_LITERATURE.md.

## Evidence and review

- CAP_THEORY.md: independently derived stationary and identifiability formulas.
- cap_experiment.py / cap_experiment_v2.json / CAP_NUMERICAL.md: registered
  synthetic tests, source hashes, environment, convergence and limitations.
- CAP_LITERATURE.md: primary-source comparison and bounded novelty assessment.

The lead and theory specialist checked the numerical result. Independent energy
evaluation agrees with the source to 4.14e-11 kBT. All three source-grid
trajectories on the compensation ridge have zero pairwise spread. Same-domain
continuum errors decrease from 6.09e-5 to 2.92e-5 to 1.38e-5 nm⁻¹ on 400, 800,
and 1600 points. The fixed psi=0.02 boundary separately biases an actually flat
state by 3.33e-4 nm⁻¹; grid refinement cannot remove that boundary choice.

Three targeted tests passed. The initial output is preserved in
cap_experiment.json; v2 corrects the endpoint comparison and adds direct
pairwise checks. Area perturbations move the registered trajectories off the
reference by 2.76e-4 to 2.81e-3 nm⁻¹ under the shared-parameter assumption.
This is not an empirical precision claim or proof of joint identifiability.

Accepted as a checked result of the implemented model. Scientific novelty
remains unresolved after a bounded primary-literature check. No production
model was changed, no experimental data fitted, and no finding is promoted to a
new biological law. A plot command failed to start at the tool runner; no figure
is claimed. Actual cycle timing and the interrupted checkpoint are logged in
PROGRESS.md.
