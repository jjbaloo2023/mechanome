# From the spherical cap to a full membrane: a bounded area-response benchmark

Cycle `cap-full-shape-001`, attempt 1. The registered cycle start was
2026-09-23 11:19:54 UTC. This note owns only the mathematical mapping and the
smallest justified forward comparison. It does not reproduce the published
nonlinear solver, infer parameters, or make a biological or novelty claim.

## Decision

Use **apex mean curvature** as the primary source-aligned geometric observable,
with a declared local-fit window when it is measured from images. In the
passive, small-slope, constant-rigidity limit, its response to circular coat
area has the same sign as the zero-line-tension spherical-cap model: at fixed
spontaneous curvature and positive reservoir tension, apex curvature decreases
as coat area increases. This is a conditional transfer of the sign, not of the
cap response magnitude and not of the cap's active-force term.

The smallest useful next comparison is therefore one passive forward sweep of
the published axisymmetric equations, beginning on the shallow high-tension
branch and first validating the analytic small-slope result below. No inverse
fit or large new solver is justified by this result.

## Primary-model correspondence

Hassinger et al., *Membrane tension is a key determinant of bud morphology in
clathrin-mediated endocytosis*, arXiv v1, use

\[
W=k(H-C)^2+\bar k K
\]

([Eq. S11 and the authors' factor-of-two convention](https://arxiv.org/html/1604.08629v1)).
The repository cap uses

\[
W_{\rm repo}={\kappa\over2}(2H-c_0)^2.
\]

The exact notation map is

\[
k=2\kappa,\qquad C={c_0\over2}.
\]

This factor is essential: the source's preferred spherical mean curvature is
`C`, whereas the repository's `c0` is the preferred total curvature `2H`.
For a Monge height field, `H = Delta h/2 + O(|grad h|^2)`. The source prescribes
the tension at the outer boundary and permits local tension to vary when `C`
varies. There is a primary-source sign inconsistency that must not be hidden:
main-text Eq. 3 prints
`lambda_,alpha=-2k(H-C) C_,alpha-f.a_alpha`, whereas supplement Eqs. S13-S14,
S27, S32c and S40c print the curvature term with a plus sign. The plus sign
follows directly from the supplement's preceding identity
`lambda_,alpha=-partial W/partial x_exp` and `W=k(H-C)^2`, since the explicit
derivative of `W` is `-2k(H-C) C_,alpha`. The discrepancy does not affect the
present linear benchmark: either version makes the tension variation quadratic
in the small curvature amplitude, because it is proportional to
`(H-C) grad C`. Thus `lambda=lambda0=sigma` at first order. A nonlinear
reproduction must inspect the supplied source code or otherwise register which
sign it uses before it can be called a reproduction.

The paper defines and plots mean curvature at the bud tip versus coat area
(main Figure 4B and Figures S6/S8), so `H_apex=H(0)` is a direct like-for-like
simulation observable. A pointwise second derivative is fragile in microscopy;
an experimental implementation should fit the axisymmetric tip profile over a
declared physical window and apply the identical fit to simulated profiles.
Invagination depth, neck radius, cap-fitted curvature, and coat-mean curvature
must be reported separately.

## Analytic full-membrane benchmark

Take an infinite, initially flat membrane with a circular spontaneous-curvature
patch of projected radius `R`, no pressure and no applied force. Let
`chi_R(r)=1` for `r<R` and zero otherwise, and write the repository spontaneous
curvature as `c` (`C_source=c/2`). The quadratic energy is

\[
E[h]=\int_{\mathbb R^2}\left\{
 {\kappa\over2}[\Delta h-c\chi_R]^2
 +{\sigma\over2}|\nabla h|^2\right\}\,d^2x .
\]

Its Euler-Lagrange equation is

\[
\kappa\Delta(\Delta h-c\chi_R)-\sigma\Delta h=0.
\]

Set `q=sqrt(sigma/kappa)` and `x=qR`. Regularity at the origin and a flat
far field give the axisymmetric solution

\[
h_{\rm in}(r)={c\over q^2}
  [xK_1(x)I_0(qr)-1],
\qquad
h_{\rm out}(r)=-{c\over q^2}xI_1(x)K_0(qr),
\]

where `I_n` and `K_n` are modified Bessel functions. An arbitrary common
vertical offset has been fixed by `h(infinity)=0`.

For the sharp interface, variation of the energy gives four matching
conditions:

\[
[h]=0,\quad [\partial_r h]=0,\quad
[\kappa(\Delta h-c\chi_R)]=0,\quad
[\kappa\partial_r(\Delta h-c\chi_R)-\sigma\partial_r h]=0.
\]

With common `kappa` and `sigma`, the last condition reduces to continuity of
`partial_r Delta h`. The solution above satisfies all four. Its coefficients
follow from the Wronskian identity
`I0(x)K1(x)+I1(x)K0(x)=1/x`. The paper uses a smooth hyperbolic-tangent coat
edge rather than a step; the sharp-interface result is its controlled narrow-edge
benchmark.

The apex mean curvature is

\[
H_{\rm apex}={1\over2}\Delta h(0)
={c\over2}xK_1(x)=C_{\rm source}\,xK_1(x).
\]

Because

\[
{d\over dx}[xK_1(x)]=-xK_0(x)<0\qquad(x>0),
\]

`H_apex` decreases strictly with `R` and with the patch area `A=pi R^2` when
`c>0` and `sigma>0`. Its limits are

\[
{H_{\rm apex}\over C_{\rm source}}\to1\quad(x\to0),
\qquad
{H_{\rm apex}\over C_{\rm source}}\sim
\sqrt{\pi x/2}\,e^{-x}\quad(x\to\infty).
\]

The coat-mean curvature is a useful secondary check,

\[
\langle H\rangle_{r<R}=cI_1(x)K_1(x),
\]

but it is not the quantity plotted in the primary source. The apex depth,
using the far field as zero, is

\[
d=-h(0)={c\over q^2}[1-xK_1(x)],
\]

which increases with area even while apex curvature decreases. Thus an
unqualified claim that a larger coat causes "more" or "less" deformation is
not well defined.

For comparison with cap depth, use the same coat-edge reference:
`d_edge/(c*ell^2)=x*K1(x)*(I0(x)-1)`. It is not globally increasing: the
registered values fall from 0.53065 at x=5 to 0.52491 at x=10. Only the
reservoir-referenced depth above is strictly increasing. Review revision 2 of
the figure shows both references and compares like-for-like edge depths.

Two limit cautions matter. First, as `R` tends to zero the pointwise sharp-edge
curvature tends to `C_source`, while the depth and spatial extent vanish; a
finite-resolution fit will not retain that pointwise limit. Second, at fixed
`R`, the curvature limit `sigma -> 0` is finite,
`H_apex -> C_source`, but the infinite-domain, flat-height condition becomes
singular and the depth has no finite limit. A finite membrane or another height
reference is needed for zero-tension depth.

## Comparison with the spherical cap

For the passive matched case `u=1`, `P=0`, `B=4*pi*kappa`, and
`A=pi R^2`, the cap formula reduces to

\[
{H_{\rm cap}\over C_{\rm source}}
={1\over1+x^2/8}.
\]

Both `xK1(x)` and `1/(1+x^2/8)` are decreasing, so the passive area sign
survives this first full-membrane test. The functions are quantitatively
different: the full membrane relaxes through the uncoated exterior and its
apex response decays exponentially for large `x`, whereas the constrained
uniform-curvature cap decays algebraically. Agreement of signs therefore does
not validate the cap as a quantitative surrogate.

This analytic result also matches the qualitative source check in Figure S6:
at high tension the tip mean curvature falls nearly to zero as coat area grows,
whereas at low tension it remains near the preferred coat curvature. The
source's intermediate-tension nonlinear solutions include multiple branches
and snap-through. The quadratic theory is convex and single-valued; it cannot
establish, refute, or locate that instability.

Figure S6's intermediate-tension caption prints `0.002 pN/nm`, while main
Figure 4 and its surrounding text give `0.02 pN/nm`. This note uses S6 only for
the qualitative high/low-tension check and treats `0.02 pN/nm` as the verified
main-text value for the intermediate case; a future reproduction should record
the discrepancy rather than silently mixing the values.

The cap's active parameter `P` is deliberately excluded. In the repository it
is total axial force coupled to cap depth. In the paper, force is a distributed
traction; the pulling protocol applies it across the coat, and some calculations
prescribe tip displacement and solve for the required force. Holding traction
density fixed makes total force area-dependent. Until force location, direction,
controlled quantity, and total-force versus force-density convention are
matched, the passive sign is the only justified transfer.

## Surface area and controlled variables

The analytic patch uses projected area `pi R^2`; the paper specifies coat
surface area. For small slopes,

\[
A_{\rm surface}=\int_{r<R}\sqrt{1+|\nabla h|^2}\,d^2x
=\pi R^2+O(|\nabla h|^2),
\]

so the two agree at the order retained here. They must not be interchanged in
the nonlinear comparison. The matched passive sweep holds spontaneous
curvature, bending rigidity, outer-boundary tension, total membrane area,
pressure, force, domain size, and coat-edge width fixed while varying only coat
surface area. The source normally uses a homogeneous bending modulus; its
stiffer-coat study is a separate comparison.

## Smallest forward comparison

Use the source's passive axisymmetric system (Eqs. S18, S22, S24, S26, S27),
with `p=0` and `f=0`. At the center impose `r=0`, `psi=0`, and `L=0`; at the
outer boundary impose `z=0`, `psi=0`, and `lambda=lambda0` (Eqs. S28/S33 or
their area-coordinate equivalents S37/S41). Use the source's smooth coat edge,
fix a sufficiently large total membrane area, and vary coat surface area.

The comparison should proceed in two bounded stages:

1. Choose small `C_source*sqrt(kappa/sigma)` and shallow solutions. Plot
   `H_apex/C_source` against
   `x=sqrt[sigma*A_coat/(pi*kappa)]`. Verify convergence to `xK1(x)` as the
   curvature amplitude and edge width are reduced and the outer domain is
   enlarged. Also verify center symmetry, outer flatness, and insensitivity to
   further domain enlargement.
2. Only after that check, run one source-parameter passive sweep corresponding
   to the high-tension branch of Figure S6, reporting tip curvature, tip depth,
   and actual coat surface area separately. Continue from neighboring shallow
   solutions. Do not use this stage to claim snap-through; intermediate-branch
   continuation and stability analysis are additional work.

This is the smallest comparison that tests the transferred sign in the
published geometry while exposing where nonlinear geometry changes its
magnitude. A paper figure alone is a qualitative check, not a numerical
reproduction.

## Inputs and review disposition

Inputs inspected: `research/NEXT_CYCLE.md`, `research/TWO_AREA_FINDINGS.md`,
`research/CAP_THEORY.md`, `curvo/evaluator_tier0.py::_cap_energy`, and the
accessible arXiv v1 HTML including Supplement Sections 1.2-1.3, Simulation
Methods, Eq. S43-S44, and Figures S4-S8. No raw data or production files were
changed.

Independent cross-check confirmed the Bessel solution, interface conditions,
monotonic derivative, depth/curvature distinction, and the singular zero-tension
depth limit. Review also required making the projected-area versus surface-area
distinction explicit and starting any nonlinear work from the shallow
high-tension branch before discussing snap-through. A final primary-source
cross-check identified the main-text/supplement tension-gradient sign conflict
and the Figure S6 intermediate-tension caption discrepancy; both are flagged
above. Those corrections are incorporated here.
