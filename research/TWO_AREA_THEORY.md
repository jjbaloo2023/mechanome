# Two known areas: structural identifiability of the cap inverse

## Scope and timing

This note analyzes the zero-line-tension, continuous spherical-cap optimum used
by `curvo/inverse.py::_fast_H_trajectory`.  It assumes that the two areas are
known and that observations compared across areas have matched coat coverage
`u` and rigidity.  It is a model audit and an experimental-design result, not a
biological or novelty claim.

- Actual start: 2026-09-22 21:14:37 EDT (2026-09-23 01:14:37 UTC)
- Actual end after review correction: 2026-09-22 21:24:24 EDT (2026-09-23 01:24:24 UTC)

Write

\[
B(t)=4\pi\kappa(t),\qquad y_i(t)={H_i(t)\over u(t)},\qquad A_1\ne A_2.
\]

At an unclipped interior optimum and `u>0`, the stated model is

\[
y_i(B)={BC+P\over 2B+\sigma A_i},\qquad P={F\over k_BT}.                 \tag{1}
\]

The conclusions below concern this continuum expression.  The source inverse
instead minimizes on a 400-point angle grid excluding both exact endpoints, so
its staircase and its positive lower-curvature floor are numerical effects.

## Shared `C`, `P`, and `sigma`

### Known constant rigidity

At one known `B`, two nonzero area observations determine the common numerator
`N=BC+P` and tension:

\[
\sigma={2B(y_1-y_2)\over A_2y_2-A_1y_1},\qquad
N=y_i(2B+\sigma A_i).                                                  \tag{2}
\]

They do not split `C` from `P`.  The exact surviving symmetry is

\[
C\mapsto C+\delta,\qquad P\mapsto P-B\delta,\qquad \sigma\mapsto\sigma. \tag{3}
\]

Thus the two-output Jacobian has generic rank two for three parameters.  At
zero numerator (`C=P=0` under nonnegative bounds), both curves are zero and its
rank falls to one: tension is then invisible.

### Known varying rigidity

At any rigidity state having nonzero signal, the cross-area ratio identifies
`sigma` by (2).  Once `sigma` is known, each state gives `N(B)=BC+P`; two
distinct known `B` values determine its slope and intercept.  Therefore two
areas and two distinct rigidity states have local rank three and are globally
one-to-one for shared `(C,P,sigma)`, except when every measured numerator is
zero.  With two distinct `B` values the latter exception forces `C=P=0`, while
`sigma` remains arbitrary (rank two at that point).

For one area the familiar compensation condition is `P=C sigma A_i/2`, on
which `y_i=C/2` for every rigidity.  A second distinct known area removes that
nontrivial ridge: it cannot hold for both areas unless `C sigma=0`.  The case
`P=sigma=0`, `C>0` is rigidity-independent but is still uniquely identified by
the two-area data; it is not a surviving ridge.

At matched `B`, area itself also supplies a falsifiable sign:

\[
{\partial y\over\partial A}
=-{\sigma(BC+P)\over(2B+\sigma A)^2}.                                  \tag{4}
\]

Thus positive tension and signal require curvature per coverage to decrease
with area under the shared-force model.

## Force proportional to area

If force is a density, `P_i=rho A_i`, then

\[
y_i(B)={BC+\rho A_i\over2B+\sigma A_i}.                                \tag{5}
\]

At constant rigidity there are only two independent outputs for the three
parameters `(C,rho,sigma)`, so the Jacobian has rank two.  For fixed observed
`y_i`, its exact affine null family can be parameterized by `delta sigma`:

\[
\delta\rho={A_2y_2-A_1y_1\over A_2-A_1}\,\delta\sigma,
\qquad
\delta C={A_1\over B}(y_1\delta\sigma-\delta\rho).                      \tag{6}
\]

Varying known rigidity gives generic rank three, but an exact one-dimensional
ridge survives every number of areas and rigidity states:

\[
\rho={C\sigma\over2},\qquad y_i(B)={C\over2}.                           \tag{7}
\]

Along it `C` is fixed while `sigma` can vary and `rho=C sigma/2`.  Away from
this ridge, two distinct rigidity values at two areas are generically full
rank and globally unique.  Indeed, after the observed `y_ij` are fixed, every
equation `B_j C+A_i rho-A_i y_ij sigma=2B_j y_ij` is linear in the unknowns;
a singular design therefore leaves an affine continuum, not isolated aliases.
Three distinct rigidity values remove accidental two-level singularities and
leave only the exact ridge (7).  The area signature is

\[
{\partial y\over\partial A}
={B(2\rho-\sigma C)\over(2B+\sigma A)^2},                               \tag{8}
\]

so it may increase, decrease, or vanish; the zero case is exactly (7).

## Area-specific spontaneous curvature, shared `P` and `sigma`

Now let

\[
y_i(B)={BC_i+P\over2B+\sigma A_i},                                     \tag{9}
\]

with four unknowns `(C_1,C_2,P,sigma)`.  At constant known rigidity the
Jacobian has rank two and the exact two-dimensional family is

\[
\delta C_i={A_i y_i\,\delta\sigma-\delta P\over B},                    \tag{10}
\]

where `delta P` and `delta sigma` are free.  Allowing `C_i` to differ therefore
does destroy identification in a single snapshot, but it does **not** do so
generically when rigidity varies.

With at least three distinct known rigidity values, equality of two candidate
rational functions forces equality of their quadratic cross-products.  The
four-parameter Jacobian and the global map are generically full rank/unique.
The only nontrivial exact ridge is simultaneous compensation:

\[
q=C_1A_1=C_2A_2,\qquad P={q\sigma\over2}.                               \tag{11}
\]

Then `C_i=q/A_i` are fixed, `y_i=C_i/2`, and `sigma` may vary together with
`P=q sigma/2`.  This includes the boundary point `P=sigma=0` only when
`C_1A_1=C_2A_2`; if those products differ, that point is locally identifiable.

Exactly two distinct rigidity values provide four observations and are
generically globally one-to-one (rank four), but have an additional accidental singular
hypersurface.  For rigidity values `B_1 != B_2`, the determinant vanishes when

\[
{A_1[2B_1B_2C_1+P\{2(B_1+B_2)+\sigma A_1\}]
 \over(2B_1+\sigma A_1)(2B_2+\sigma A_1)}
=
{A_2[2B_1B_2C_2+P\{2(B_1+B_2)+\sigma A_2\}]
 \over(2B_1+\sigma A_2)(2B_2+\sigma A_2)}.                             \tag{12}
\]

For fixed observed `y_ij`, equation (9) rearranges to
`B_j C_i+P-A_i y_ij sigma=2B_j y_ij`, a linear system in the four unknowns.
Consequently, off (12), full rank already implies global uniqueness; on (12),
the surviving alternatives form an affine continuum (possibly truncated by
physical bounds), never isolated aliases.  A third distinct rigidity level
removes this design-specific rank loss and leaves only (11).

## Unknown multiplicative rigidity scale

If only the shape of the rigidity history is known,
`B(t)=alpha B_bar(t)`, then every area and time is invariant under

\[
(\alpha,P,\sigma)\mapsto(g\alpha,gP,g\sigma),\qquad C\mapsto C,
\quad g>0.                                                              \tag{13}
\]

Equivalently, curvature can identify only `P/alpha` and `sigma/alpha`.
No number of known areas removes this absolute-scale symmetry.  With varying
`B_bar`, shared `(C,P,sigma)` therefore has generic rank three out of four;
the force-density and area-specific-curvature variants retain (13) in addition
to their compensation exceptions (7) and (11).  At constant `B_bar`, the
`C`/`P` translation also remains, so only two combinations are observed.

## Coverage, clipping, and parameter bounds

Frames with `u=0` always have `H_i=0` and zero sensitivity to all mechanical
parameters.  Very small `u` makes the division defining `y_i` noise-amplifying.
The continuous cap constraint is

\[
0\le H_i\le {2\over a_i}=2\sqrt{\pi/A_i}.
\]

Within either clipped plateau, equality data become inequalities and the
observation has zero local derivative.  If all informative states are clipped,
the rank conclusions above do not apply; if only some are clipped, rank must be
computed from the remaining interior states.  At zero signal, nonnegative
parameter bounds may reduce the zero set to a boundary such as `C=P=0`, but
that one-sided restriction is not data identification.  Likewise, finite prior
bounds can truncate any exact ridge without eliminating its structural
symmetry.

## Testable design result

Use two calibrated, distinct coat areas and at least three matched, calibrated
rigidity levels, retaining only `u>0` interior states.  Under shared force and
tension this design is generically globally identifying even if each area has
its own unknown spontaneous curvature.  Failure occurs only on the directly
testable simultaneous condition `C_1A_1=C_2A_2=2P/sigma`; an uncalibrated
rigidity amplitude always leaves the scale symmetry (13).  Comparing the sign
of the area response in (4) with (8) further distinguishes shared total force
from force proportional to area, subject to the same sharing and clipping
assumptions.
