# Exact reduction of the spherical-cap model

## Scope and timing

This note analyzes the energy implemented by `curvo/evaluator_tier0.py::_cap_energy`
and its zero-line-tension trajectory specialization in
`curvo/inverse.py::_fast_H_trajectory`. It does not establish scientific
novelty; the line-tension budding competition is classical (for example,
Lipowsky, *Biophysical Journal* 64, 1133--1138, 1993). The result here is an
exact audit of this implementation and its inverse problem.

- Actual start: 2026-09-22 20:20:04 EDT
- Actual end: 2026-09-22 20:47:49 EDT (final independent numerical review;
  the requested eight-minute bound was exceeded, including a runner stall)

## One-coordinate reduction

Let

\[
x=\sin(\psi/2)\in[0,1],\qquad a=\sqrt{A/\pi}.
\]

Here `a` is the radius of the flat disk having the fixed cap area `A`. The cap
geometry becomes

\[
R={a\over2x},\quad H={1\over R}={2x\over a},\quad
L_{\rm rim}=2\pi a\sqrt{1-x^2},\quad
A_{\rm footprint}=A(1-x^2),\quad d=ax.
\]

Therefore the implemented energy, up to the constant
`pi*kappa*a^2*c0^2/2`, is exactly

\[
E(x)=Qx^2-Lx+b\sqrt{1-x^2},
\]

with

\[
Q=8\pi\kappa_{\rm eff}+\sigma A,
\quad L=a\left(4\pi\kappa_{\rm eff}c_0+{F\over k_BT}\right),
\quad b=2\pi\lambda a.
\]

All energies are in `kBT`, lengths in nm, and `F/kBT` has units `nm^-1`
because the code uses `kBT = 4.114 pN nm`. This coordinate removes all apparent
trigonometric complexity from the minimization.

For an interior point,

\[
E'=2Qx-L-{bx\over\sqrt{1-x^2}},\qquad
E''=2Q-{b\over(1-x^2)^{3/2}}.
\]

An interior stationary point is locally stable exactly when `E'' > 0`.
Endpoint stability is one-sided.

## Zero line tension

For `lambda = 0`, `b = 0` and `Q > 0` under the implemented nonnegative
rigidity and tension. The exact global solution is

\[
x_*={\rm clip}\left({L\over2Q},0,1\right),\qquad H_*={2x_*\over a}.
\]

Thus the energy is convex, has one global minimum, and has neither a fold nor a
coexistence transition. With nonnegative spontaneous curvature and force, the
minimum moves continuously from flat toward closed until boundary clipping.
Any abrupt change returned by `_fast_H_trajectory` in this regime is a switch
between neighboring points on its 400-point `psi` grid, not physical
snap-through.

For a uniform angle spacing `Delta psi`, adjacent grid values obey

\[
|\Delta H|={2\over a}|\Delta\sin(\psi/2)|\le {\Delta\psi\over a}.
\]

This gives a direct convergence test: doubling angular resolution must roughly
halve the largest numerical staircase step. For `a = 60 nm`, the inverse
grid's `Delta psi ~= 0.00782` bounds a one-cell jump by about
`1.30e-4 nm^-1`. A larger resolution-independent jump cannot be attributed to
the zero-line-tension fixed-area energy.

## Positive line tension: local and global events differ

Assume `b > 0`, `Q > 0`, and the physically used `L >= 0`. The rim term is
concave in `x`, so it can create a shallow-cap local minimum, an intervening
maximum, and the closed endpoint minimum.

A genuine fold requires `E' = E'' = 0`. It exists only for `b < 2Q` and is

\[
x_f=\sqrt{1-\left({b\over2Q}\right)^{2/3}},\qquad
L_f=2Qx_f^3.
\]

For `0 < L < L_f`, the lower stationary root is a local minimum and the upper
root is a barrier. At `L = L_f` those roots annihilate. This is the genuine
loss of metastability.

The global-minimum crossing generally happens earlier and is not a fold. If an
interior local minimum at `x` has the same energy as the closed endpoint
`x = 1`, stationarity and equal energy reduce to

\[
{b\over Q}=(1-x)\sqrt{1-x^2},\qquad L_{\rm cross}=Qx(1+x).
\]

For positive `L`, this crossing exists when `b < Q`; both competing minima are
still locally stable at the crossing. The global argmin jumps because their
energies cross, not because either stationary point disappears.

The particularly transparent `L = 0` case gives

\[
E(0)=b,\qquad E(1)=Q.
\]

Hence the flat and closed states exchange global stability at `b = Q`.
The flat endpoint remains locally stable until `b = 2Q`, while the closed
endpoint is a one-sided local minimum for every `b > 0` because the rim-energy
slope tends to minus infinity as `x -> 1`. At zero tension and zero spontaneous
curvature, `b = Q` yields

\[
a_c={4\kappa\over\lambda},
\]

which is the closed-form check reported by the evaluator. The interval
`Q < b < 2Q` is therefore a metastable-flat regime, not a fold at the budding
threshold.

The implementation does not include line tension in `_fast_H_trajectory`, so
none of these positive-line-tension barriers is present in the inverse model.
Moreover, both production grids exclude the exact endpoints (`psi = 0` and
`psi = pi`), slightly regularizing endpoint cusps and replacing exact endpoint
states with nearby samples.

## Fixed versus ramped rigidity and identifiability

Write coat coverage as `u(t)`, plateau spontaneous curvature as `C`, plateau
force divided by thermal energy as `P = F_max/kBT`, and `S = sigma*A`. With
zero line tension and no clipping, the inverse implementation has

\[
\kappa(t)=\kappa_0[1+(r-1)u],\qquad
H(t)=u\,{4\pi\kappa(t)C+P\over8\pi\kappa(t)+S}.
\]

If rigidity is fixed in time, curvature observes only the single amplitude

\[
{4\pi\kappa C+P\over8\pi\kappa+S}.
\]

Consequently force and spontaneous curvature are exactly confounded even if
tension is known; if tension is also inferred, an even larger family of
triples has the same trajectory.

Known time-varying rigidity generically supplies extra information. Equality
of the rational function at three or more distinct rigidity values forces two
parameter triples `(C,P,S)` and `(C',P',S')` to be identical, except on the
special manifold

\[
P={CS\over2}.
\]

On that manifold,

\[
H(t)={C\over2}u(t)
\]

for every rigidity history, and every pair `S'`, `P' = C*S'/2` gives the same
curvature. Thus a known rigidity ramp generically breaks the fixed-rigidity
rank deficiency but does not eliminate this exact force--tension ridge. Grid
quantization, boundary clipping, a small rigidity range, and noise can restore
practical non-identifiability away from the exact manifold. An independent
actin-force observable can constrain `P`; curvature alone cannot do so on this
ridge.

## Fixed versus variable area

The reduction above assumes `A` is fixed at each minimization. If a measured,
externally prescribed area varies with time, the same formula applies
frame-by-frame with `a(t)` and `S(t) = sigma*A(t)`. Known area variation can add
information about tension. Unknown area variation instead confounds tension
through the product `sigma*A(t)` and changes the curvature-to-coordinate map.

Allowing area itself to relax is a different physical model. Before discarding
the constant, the energy as a function of both `a` and `x` is

\[
E=8\pi\kappa x^2+a[2\pi\lambda\sqrt{1-x^2}
-x(4\pi\kappa c_0+F/k_BT)]
+\pi a^2[\kappa c_0^2/2+\sigma x^2].
\]

It requires an area reservoir, chemical potential, or stretching penalty and
appropriate boundary conditions. Merely minimizing the current expression over
`A` changes the ensemble and can be ill posed (for example, with zero tension
and spontaneous curvature a sufficiently large force makes the energy decrease
without bound as `a` grows). Fixed-area conclusions therefore must not be
described as variable-area predictions.

## Testable counterexample

Choose any nonconstant, known rigidity ramp, any `C > 0`, `sigma > 0`, fixed
area `A`, and set

\[
F_{\max}=k_BT\,{C\sigma A\over2}.
\]

Provided the continuous minimizer is not clipped, the exact prediction is
`H(t) = C*u(t)/2`, independent of the magnitude or time dependence of rigidity.
Two simulations with different coat-rigidity factors must therefore produce the
same continuous trajectory. If the grid implementation reports differences,
they should vanish under analytic minimization or angular-grid refinement. This
is a precise counterexample to the claim that a known rigidity ramp always
separates active force, spontaneous curvature, and tension from curvature alone.

## Independent numerical cross-check

The separately produced `cap_experiment_v2.json` reports agreement between its
independent energy expression and the source energy to `4.14e-11 kBT`; the
ridge identity and area-perturbation formula agree to about `1e-18`. Holding
the reference-ridge parameters fixed while changing area to `A/2` and `2A`
separates the trajectories by about `0.00105` and `0.00173 nm^-1`, respectively,
as predicted above. The numerical worker's three registered tests passed.

One endpoint caveat matters when interpreting grid convergence. At `a = 60 nm`,
the source grid's fixed lower cutoff `psi_min = 0.02` imposes
`H_min = 2 sin(0.01)/a = 3.33328e-4 nm^-1`. Increasing only the number of grid
points does not remove this physical-flat-endpoint bias; it only refines the
interior staircase. Removing that bias requires including `psi = 0`, moving the
lower cutoff, or using the analytic clipped minimizer.
