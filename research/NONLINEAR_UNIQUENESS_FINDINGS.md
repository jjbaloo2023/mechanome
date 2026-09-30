# Compact-source uniqueness under two actual profiles

Accepted within scope on 26 September 2026. The exact graph model now has a
sufficient condition under which two profiles rule out a hidden compact change
in preferred curvature. This is a conditional mathematical result; whether a
nonflat pair of actual equilibria satisfies that condition is the next gate.

## Model and result

Keep the [registered conventions](nonlinear_uniqueness_design.json): smooth
axisymmetric graphs, prescribed sources in projected radial coordinates,
vertical dead load per projected area, known uniform rigidity, two distinct
known positive tensions, regular origin and the same decaying flat reservoir.
The two profiles must originally be stationary under the SAME curvature source
`c`, load `f` and rigidity. Overhangs, material-coordinate coats and normal-following
loads are outside this calculation.

Let `p_j=h_j'`, `J_j=sqrt(1+p_j^2)`, `u_j=p_j/J_j`, `D=u_1-u_2`, and
`S=u_1+u_2`. The exact finite source-change condition factors as

```text
D[-S(rg)' + r(cg + g^2/2)] = 0.
```

For a smooth radial change `g` supported in `[0,R0]`, suppose `S != 0` at EVERY
positive radius through and including `R0`, and `D != 0` on a dense subset of
that interval. Then **g is identically zero**, as is its compensating load change.

Indeed, continuity removes the `D` factor. With `y=rg`, the remaining equation
is `y'=(c/S)y+y^2/(2rS)`. Compact support supplies `y(R0)=0`; ordinary local
uniqueness propagates that value on every `[epsilon,R0]`. Continuity handles the
origin. The infinitesimal equation omits the quadratic term and has the same
trivial kernel under these hypotheses. No singular initial-value theorem is
applied at the origin, and the nonzero outer-boundary condition is essential.

## Exceptions and correction during review

An open equal-slope interval is algebraically unconstrained. However, actual
common-load profiles regular at the origin have equal stationary flux globally.
On any equal-slope interval the bending terms cancel, leaving
`(sigma_1-sigma_2)*p/J=0`: the common slope must be zero, including on an annulus.
The earlier local catenoid possibility was corrected before acceptance; a
nonzero integration constant cannot match the global regular-origin condition.

Where slopes are opposite and nonzero, finite compatibility gives `g=0` or
`g=-2c`. These pointwise roots do not establish a global common-source equilibrium.
Zeros of `S`, including the support endpoint, require additional analysis.

A real ambiguity survives: `h_1=h_2=0`, `f=-kappa*Delta_r c` is stationary at every
tension. Any smooth compact radial `g` is hidden by
`delta f=-kappa*Delta_r g`, with zero added net force. Thus unconditional source
identification is false even in this exact model.

## Evidence, limitations and next decision

The [theory](NONLINEAR_UNIQUENESS_THEORY.md), [equilibrium compatibility
check](NONLINEAR_UNIQUENESS_COMPATIBILITY.md), and [independent
review](NONLINEAR_UNIQUENESS_REVIEW.md) agree after the global-flux correction.
The lead independently checked factorization, boundary propagation and flux.

Exact uniqueness does not establish stable inversion: small `D` weakens the
original residual and small `S` enlarges divided coefficients. Joint small
sources and slopes produce cubic corrections to the shallow compensation.
No numerical solver, fitted noise, empirical force estimate, biological
selection, global branch classification or novelty claim was made.

Next: separately register an analytic existence and slope-ordering test for
actual common-source profiles under a small compact curvature forcing at two
positive tensions. See [NEXT_CYCLE.md](NEXT_CYCLE.md). This is preferable to
further coefficient taxonomy or repeating stopped data-access audits.
