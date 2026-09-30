# Actual-equilibrium restrictions on two-profile source compatibility

Task `nonlinear-uniqueness-compatibility-001`, attempt 1. Observed work interval: 2026-09-26 16:23–16:28 UTC. This note uses the projected-radius graph energy, balanced vertical dead load, positive uniform tensions, and common `c,f,kappa` frozen in [nonlinear_source_design.json](nonlinear_source_design.json). It supplements the algebraic source-change criterion in [NONLINEAR_SOURCE_THEORY.md](NONLINEAR_SOURCE_THEORY.md). The profiles discussed below must **already solve the unperturbed stationary equation**; compatible coefficient functions by themselves are not evidence of such profiles.

## The equation the two profiles must actually satisfy

For `p=h'`, `J=sqrt(1+p^2)`, `C=(rp/J)'/r`, write the radial first-variation flux as

\[
 Q_\sigma[p;c]= -\kappa\frac{[(C-c)J]'}{J^3}
 +\left[\frac{\kappa}{2}(C-c)^2+\sigma\right]\frac pJ . \tag{1}
\]

Varying the registered energy with a compactly supported height variation gives the stationary equation

\[
 f=-\frac{(rQ_\sigma)'}r. \tag{2}
\]

Thus two proposed slopes at distinct tensions are jointly realizable with the *same* `c` and `f` only if `r(Q_{sigma1}[p1;c]-Q_{sigma2}[p2;c])=constant` globally. The regular origin fixes that single global constant to zero. One cannot choose a fresh integration constant on an annular interval. This is a separate prerequisite from the `g`-compatibility equation. The associated `f` must also satisfy the registered force and reservoir conditions.

## Equal-slope intervals

Suppose `p1=p2=p` on a nonempty open interval. Then `C` and the bending part of (1) agree there. The globally zero flux difference gives

\[
 (\sigma_1-\sigma_2)\frac pJ=0.
\]

Because the known positive tensions differ, **the common slope must be flat, `p=0`, on any such interval**, including an annulus. Subtracting only the differential equations locally gives the weaker condition `C=0`, hence a formal catenoid segment

\[
 \frac pJ=\frac K r,\qquad p=\frac{K}{\sqrt{r^2-K^2}}
 \quad (r>|K|), \tag{3}
\]

with the sign carried by `K`, but the global zero-flux condition forces `K=0`. Therefore a nonzero annular catenoid equality segment cannot occur for actual globally regular common-source profiles. If the slopes coincide on the entire radial domain, the shared flat reservoir fixes both profiles to `h=0`.

The equal-slope interval automatically satisfies the algebraic two-profile source-change equation for any local `g`, but it is available to *actual* equilibria only where both slopes vanish. Smooth matching and (2) outside the interval remain to be checked.

## Opposite-slope intervals

If `p2=-p1=-p` on an interval, then `J2=J1=J` and `C2=-C1=-C`. Direct substitution in (1) gives the necessary equilibrium relation

\[
 -2\kappa\frac{(CJ)'}{J^3}
 +[\kappa(C^2+c^2)+\sigma_1+\sigma_2]\frac pJ
 =0, \tag{4}
\]

The right-hand side is zero even for an annular interval, because the two full profiles share the same load and regular origin. The interval must also match the adjoining solution at its endpoints. Separately, the exact finite source-change compatibility equation reduces where `p` is nonzero to

\[
 g\left(c+\frac g2\right)=0. \tag{5}
\]

Therefore a smooth nonzero `g` on such an interval requires `g=-2c` there. In particular, `c=0` excludes nonzero `g` on an opposite-slope interval with nonzero slope. Equations (4) and (5) are both necessary. Equation (5) alone cannot promote arbitrary opposite-slope test curves to common-source equilibria.

There is a stronger global check in the special case `c=0`. Assume the profiles are exact opposites everywhere, have finite bending and excess-area energies, and permit the standard dilation variation with vanishing boundary work. The two stationary equations imply that `h` is stationary for the *even* functional

\[
 F[h]=2\pi\int_0^\infty r\left\{\frac\kappa2 C^2J+\bar\sigma(J-1)\right\}dr,
 \qquad \bar\sigma=(\sigma_1+\sigma_2)/2>0.
\]

Under the uniform geometric dilation `h_lambda(r)=lambda*h(r/lambda)`, its bending term is invariant and its excess-area term scales as `lambda^2`. Stationarity at `lambda=1` therefore requires `2*bar_sigma*integral r(J-1)dr=0`. Since `J>=1`, the profile is flat. Thus nonflat globally opposite stationary profiles do not exist under these stated assumptions when `c=0`, regardless of the common balanced load. This global dilation argument does not rule out an opposite-slope *interval*, or a nonzero spatial `c`, for which the `c^2 J` term breaks the scaling argument.

## Genuine flat ambiguity

For `h=0`, (1) becomes `Q=kappa*c'`, independent of tension, and (2) becomes `f=-kappa*Delta_r c`. For any smooth compactly supported radial `c`, this `f` is balanced and the flat graph is stationary at every positive tension. For any smooth compactly supported radial `g`, set `c_new=c+g` and `f_new=f-kappa*Delta_r g`; the same flat graph remains stationary at both tensions and the new load is balanced. This is an **actual common-source stationary counterexample** to blanket uniqueness, not just an algebraic coefficient example. It does not assert stability or selection of the flat branch.

## Boundary of this check

The restrictions above do not classify all pairs of common-source equilibria. An opposite-slope segment still requires a smooth global solution of (2), regular origin, flat reservoir, and balanced shared `f`. This note supplies necessary conditions and one real degenerate family; it neither constructs nonflat branches nor claims that an arbitrary slope example realizes one.
