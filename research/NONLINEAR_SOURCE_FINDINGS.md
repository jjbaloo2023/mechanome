# Nonlinear graph geometry changes the source-compensation rule

For the exact axisymmetric graph energy declared in the [design](nonlinear_source_design.json), the load correction that hides a change of preferred curvature depends on the observed slope. The shallow rule is therefore not a universal nonlinear source transformation. This alone does not establish identifiability from two tensions, and a flat family remains exactly ambiguous.

## Model and exact result

Let `p=h'(r)`, `J=sqrt(1+p^2)`, and `C=(r*p/J)'/r=2H`. With known uniform positive rigidity and tension,

```text
E = 2*pi*integral r*[kappa/2*(C-c)^2*J + sigma*(J-1) - f*h] dr.
```

Here `c(r)` and the vertical dead load per projected area `f(r)` are prescribed in projected radial coordinates. They are not material labels or calibrated molecular fields. The origin is regular, the membrane decays to a flat reservoir, and the curvature change `g(r)` is smooth, compactly supported and radially regular. Net vertical load includes its prescribed return load and is zero. This single-valued graph excludes overhangs and neck closure.

For any specified stationary profile, change `c` to `c+g` and define

```text
A = c*g + g^2/2
T_h = (r*g)'/(1+p^2) - g + r*A*p/J
    = r*g'/(1+p^2) - g*p^2/(1+p^2) + r*A*p/J

delta_f_h = -(kappa/r)*T_h'.
```

This is an exact finite source change, including the preferred-curvature square and surface-area factor. It preserves that profile's stationarity. Regularity and compact support give `T_h(0)=T_h(infinity)=0`, so the correction is balanced. No point force is silently inserted at the origin. It does not assert that the profile is stable or dynamically realized.

For two profiles `h1,h2` originally stationary under the same `c,f,kappa` and two known tensions, the **same** load correction preserves both if and only if

```text
(r*g)' * [1/J1^2 - 1/J2^2]
  + r*(c*g + g^2/2) * [p1/J1 - p2/J2] = 0
```

throughout the source support. The boundary conditions eliminate an otherwise constant flux difference. This is a source-equivalence criterion for given profiles; it does not prove that a suitable pair exists or that the only allowed `g` is zero.

## Checks and limitations

When slopes AND both curvature fields scale jointly as a small amplitude `epsilon`, the leading correction is `-kappa*Delta_r(g)` and the first extra terms are cubic. Small slope alone with finite curvature does not justify dropping the `c^2*J` contribution. The preceding [linear result](LOAD_IDENTIFIABILITY_FINDINGS.md) remains valid for its declared quadratic model.

If both profiles are flat, `T_h=r*g'` exactly for any allowed `g`. In particular `f=-kappa*Delta_r(c)` makes the flat profile stationary at every tension, and changing to `c+g` with the corresponding load change preserves it. Thus nonlinear geometry does not guarantee that tension changes separate arbitrary sources.

The [independent theory](NONLINEAR_SOURCE_THEORY.md) and [review](NONLINEAR_SOURCE_REVIEW.md) check the variation, force balance, shallow limit and degenerate case. No numerical solver, fitted model, experiment, practical precision estimate or novelty claim accompanies this result. Public Bucher/Saleem data still lack the observation/control contract needed to use it.

A useful next analytic question is whether the two-profile criterion admits nonzero compact curvature changes on a fixed declared source support. Any sufficient uniqueness condition must state where slope-coefficient differences vanish, preserve finite and infinitesimal distinctions, and remain conditional on actual stationary profiles with invariant sources. Do not replace that question with a claim of global recovery or an arbitrary synthetic profile pair.
