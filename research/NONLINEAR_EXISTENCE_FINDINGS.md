# Actual nonflat profiles satisfying the uniqueness criterion

Task `nonlinear-existence-001`, attempt 1. Disposition: accepted after independent
review of the companion existence proof and corrected equation transcription.

The registered exact graph model has a local pair of stationary branches for
sufficiently small positive curvature amplitude, with the same compact preferred
curvature source and zero load. Their normalized slopes are strictly ordered
through the entire source disk. This supplies a realizable example for the
previous conditional compact-source uniqueness theorem.

## What is fixed

Use [nonlinear_existence_design.json](nonlinear_existence_design.json): rigidity
one, tensions one and two, zero vertical dead load, and
`c(r)=epsilon*exp(1-1/(1-r^2))` inside the unit disk, zero outside. Sources use
projected radial coordinates. Graphs have a regular origin and decay to the
same flat reservoir. No material-coordinate coat or normal-following load is
substituted.

## Exact stationary construction

Put `u=p/sqrt(1+p^2)`, where `p=h'`, and let `U(x)=u(r)e_r` on the plane.
Write `t=div U-c`. Regular origin and zero load force the stationary flux to
vanish globally. Its exact vector form, restricted to radial fields, is

```text
F_sigma(U,epsilon) = -(1-|U|^2) grad t
                    - t (DU)U + (t^2/2 + sigma) U = 0.
```

The radial subspace consists of vector fields equivariant under every rotation
and reflection in O(2); reflection excludes an azimuthal component. On that
space, `grad div U=Delta U`. The derivative at zero is therefore the invertible
screened operator `-Delta+sigma`.

Use exponentially weighted radial-vector Holder spaces with two derivatives
for the unknown and zero for the residual, `0<alpha<1` and weight rate
`0<mu<1`. The screened Green kernel beats this weight at both tensions. A
weighted convolution bound plus local Schauder estimates supplies a bounded
inverse. The displayed polynomial is a smooth map between these spaces.
The implicit-function argument yields a locally unique small stationary
branch for each tension. This is uniqueness in the chosen neighborhood and
function space, not classification of all membrane equilibria.

Smallness ensures `|U|<1`. Recover `p=u/sqrt(1-u^2)` and
`h(r)=-integral_r^infinity p(s) ds`; exponential decay gives a flat reservoir,
and radial regularity supplies a smooth origin. These are actual stationary
profiles of the frozen energy, not curves chosen to make an algebraic test pass.

## Why the slopes satisfy the earlier criterion

The first-order normalized slope `v_sigma` solves

```text
(-d^2/dr^2 - (1/r)d/dr + 1/r^2 + sigma) v_sigma = -phi'(r).
```

Set `z_sigma=v_sigma/r`. It satisfies the four-dimensional radial screened
equation `(-Delta_4+sigma)z_sigma=-phi'/r`. The source is smooth and nonnegative,
with value two at the origin and positive values inside the unit disk.
The positive heat-kernel inverse gives `z_2>0` and `z_1-z_2>0`; both have
strictly positive minima on `[0,1]`, including the source edge.

The nonlinear branch estimate controls the derivative of its radial vector
field. Since that field vanishes at zero, the mean-value bound also controls
its slope divided by radius. The strictly positive linear margins therefore
persist for sufficiently small positive epsilon:

```text
u_1(r) > u_2(r) > 0,    0 < r <= 1.
```

Thus both `D=u_1-u_2` and `S=u_1+u_2` are positive on the required support
interval. The [previous theorem](NONLINEAR_UNIQUENESS_FINDINGS.md) excludes any
nonzero smooth curvature change supported in that disk that one common load
change could hide from both profiles.

## What this does and does not establish

This is a local existence and profile-conditional source-separation result in
one specified model. The flat-family counterexample elsewhere in that model
still stands. The theorem gives no numerical amplitude threshold, selected
stable branch, practical noise tolerance, actual cellular perturbation protocol,
or biological mechanism. The nonlinear separation becomes weak near the
shallow limit; exact uniqueness is not a precision guarantee.

Evidence: [existence proof](NONLINEAR_EXISTENCE_THEORY.md), [ordering and boundary
proof](NONLINEAR_EXISTENCE_ORDERING.md), and [independent
review](NONLINEAR_EXISTENCE_REVIEW.md). The lead separately checked the exact
normalized-slope transformation, origin treatment and transfer of the uniform
ordering margin. A finite-amplitude numerical realization would require its
own registration, residual, boundary and convergence checks.
