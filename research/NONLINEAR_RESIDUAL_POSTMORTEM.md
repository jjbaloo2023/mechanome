# Why a converged solve failed the physical equation check

The saved cubic profile values agree under the registered refinement checks,
but a derivative consistency defect fails the registered physical residual.
This diagnosis uses only attempt 2's saved coefficients. It does not validate
those profiles, change their failed disposition, or compute K.

Let v be the first polynomial component, w the separately interpolated second
component, A=1-r^2 v^2, and delta=v'-w. Let Q_sys/r be the flux formed with w and
its actual polynomial derivative w', treating the first-order system as exact.
The physical flux instead uses v' and v''. Direct algebra gives

```text
Q_physical/r = Q_sys/r - A*(3*delta/r + delta')
              - r*v*delta*(v+r*w) - 0.5*v*r^2*delta^2

delta' = v'' - w'
```

The diagnostic Q_sys is not a replacement acceptance test. A small delta does
not ensure a small delta'. The original gate correctly differentiates the
actual interpolating shape rather than substituting the equation's right side.

The fixed checking grid was augmented with 17 points in every final polynomial
interval and both one-sided neighborhoods of interior knots. For all 12 fine
cases, the augmented physical maximum is 2.41885e-4 to 2.42247e-4 after division
by epsilon. It occurs just left of r=0.8416667, in the interval [0.8375,0.8416667].
The original sparse-in-that-region grid reported 1.45767e-4 to 1.53030e-4.
Both fail the same 1e-5 threshold; denser checking strengthens the rejection.

The auxiliary first-order flux maximum is only 1.46225e-7 to 5.57911e-7 on the
augmented grids. The derivative-consistency term accounts for the physical
maximum to roundoff. The full decomposition holds to below 1e-12 in normalized
units on every checking grid. This is an algebraic attribution of the saved
polynomial's defect, not proof of the error relative to an unknown exact solution.

All 12 saved fine polynomials have actual v'(0)=w(0)=0. Under that regularity,
the pole difference is -4*(v''(0)-w'(0)). The checker asserts and records the
regularity before using this finite limit. A nonzero v'(0) would invalidate
that limit and must not be hidden by assigning a finite endpoint residual.

The proposed remedy retains the model, cubic representation, 26 cases, domain
sizes, solver tolerances, node cap and all scientific thresholds. A fixed mesh
with 16 times the original interval counts has 5,761 initial nodes, below the
20,000 cap. Its source intervals are eight times smaller than the interval
containing the observed worst defect. Second-derivative error of cubic Hermite
interpolation scales as h^2 under smooth-solution and accurate-endpoint
assumptions; that suggests a reduction to about 3.8e-6 here. This is a heuristic,
not a guarantee that all regions or cases pass. The augmented residual grid and
explicit pole check become additional requirements for any final attempt.

The alternatives of weakening the gate or checking only the auxiliary w
component would conceal the defect. Changing interpolation order introduces a
larger reconstruction change. A fixed mesh change is the narrower falsifiable
test. There will be no mesh search or fourth attempt: if the final bounded
attempt fails, preserve the failure and close this computational branch.

Status: diagnosis and bounded preparation proposal independently reviewed and
accepted by the lead. This acceptance does not validate attempt 2. No new BVP calls;
no attempt 3 implementation or execution in this stage. Next is a reviewed
003 implementation and a no-BVP preflight, followed by a separately registered
last attempt only if those checks pass.

Evidence: [diagnostic source](nonlinear_residual_postmortem.py),
[diagnostic results](nonlinear_residual_postmortem.json),
[theory review](NONLINEAR_RESIDUAL_THEORY.md),
[independent review](NONLINEAR_RESIDUAL_REVIEW.md),
[fixed mesh proposal](nonlinear_numerical_mesh_plan.json).
