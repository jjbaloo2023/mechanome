# Finite-window spherical-cap observation theory

**Task:** `cap-observation-theory-001` attempt 1 under `cap-observation-001`  
**Registered tool-clock observation:** 2026-09-25 02:58:50 UTC  
**Scope:** a synthetic observation surrogate applied to six saved passive profiles. This task performs no BVP solve, empirical fit, noise sweep, stability analysis, or biological inference.

## Question and fixed inputs

The calculation asks whether the sampled area ordering seen in pointwise apex curvature is retained by a finite-window spherical-cap fit. It reuses only the saved profiles at

\[
x\in\{0.5,1,2\},\qquad c_{\rm repo}\ell\in\{0.02,0.6\}.
\]

Each profile receives four supports: the fixed physical-radius windows \(R/\ell=0.1,0.25,0.4\), when contained inside the nominal coat, and the whole nominal coat. Each support is fit with uniform radial and uniform material-area weights, for at most \(6\times4\times2=48\) membrane fits. The whole-coat radius is case-dependent and therefore is a support diagnostic, not a fair fixed-window comparison across area labels.

All coordinates below are nondimensionalized by \(\ell\): \(r,z,b\) have units of \(\ell\) removed and the fitted \(h\) denotes \(h_{\rm dimensional}\ell\).

## Stable cap model

For nonnegative curvature, fit

\[
\widehat z(r;b,h)=b+g(h,r),\qquad
g(h,r)=\frac{h r^2}{1+\sqrt{1-h^2r^2}},\qquad h\geq0.
\]

This is the rationalized form of \((1-\sqrt{1-h^2r^2})/h\) for \(h>0\), but remains regular at \(h=0\). Define \(g(0,r)=0\). Its small-curvature expansion is

\[
g(h,r)=\frac{h r^2}{2}+\frac{h^3r^4}{8}+O(h^5r^6),
\]

and its derivative is

\[
\frac{\partial g}{\partial h}
=\frac{r^2}{s(1+s)},\qquad s=\sqrt{1-h^2r^2},
\]

with the continuous limit \(r^2/2\) at \(h=0\). For an exact sphere in this sign convention, \(h\) is its pole mean curvature.

For a support ending at \(R\), search the closed interval

\[
0\leq h\leq h_{\max}=\frac{1-10^{-10}}{R}.
\]

The flat candidate \(h=0\) and the upper endpoint must be evaluated explicitly. An optimum at the upper bound is rejected because the cap slope is approaching its geometric singularity.

## Profile reconstruction and the axis

Reconstruct \(r(\rho),z(\rho)\) from each saved state without resolving the BVP. The physical fitting coordinate is \(r\), while \(\rho=\sqrt{2\alpha}\) remains a material label. On these accepted mild profiles, \(r\) must be monotone over every requested support and \(\cos\psi>0\).

The exact pole \((r,z)=(0,z_p)\) must be included. Omitting the previous finite cutoff would remove about 1.4% of the uniform-radial measure in the smallest window. Do not evaluate the frozen RHS at \(\rho=0\), where algebraically removable ratios appear. The regular pole derivatives with respect to \(\rho\) are inserted analytically:

\[
(r_\rho,z_\rho,\psi_\rho,H_\rho,L_\rho,\lambda_\rho)_{\rho=0}
=(1,0,H_p,0,0,0).
\]

Saved-state hashes and source-profile identifiers are required in the result record.

## Two declared observation measures

For any integrand \(q\), uniform physical-radius weighting is

\[
\langle q\rangle_r=\frac1R\int_0^R q(r)\,dr.
\]

Uniform material-area weighting is

\[
\langle q\rangle_a
=\frac1{\alpha_R}\int_0^{\alpha_R}q\,d\alpha
=\frac1{\alpha_R}\int_0^R q(r)\frac{r}{\cos\psi(r)}\,dr,
\]

where \(\alpha_R\) is the material coordinate at physical radius \(R\); for the whole-coat fit, \(\alpha_R=\alpha_c\). These are continuous measures, not equal weighting of interpolation nodes.

## Offset elimination and one-dimensional fit

For either normalized measure, minimize the vertical least-squares objective

\[
J(h,b)=\left\langle [z-b-g(h,r)]^2\right\rangle.
\]

The free vertical offset is eliminated exactly:

\[
b(h)=\langle z-g(h,r)\rangle.
\]

Writing \(e=z-b(h)-g(h,r)\), the envelope derivative is

\[
\frac{dJ}{dh}=-2\left\langle e\frac{\partial g}{\partial h}\right\rangle.
\]

Thus an interior solution must satisfy \(\langle e\,\partial_hg\rangle=0\). Report \(\sqrt J\) as vertical RMSE. The minimizer must be checked against both endpoints and against a direct objective evaluation; optimizer success alone is insufficient.

## Predeclared checks and outputs

Controls are separate from the 48-profile ceiling:

- Exact synthetic spheres within the declared domain must recover \(|\Delta h|\leq10^{-8}\), \(|\Delta b|\leq10^{-10}\), and RMSE \(\leq10^{-10}\) under both weights.
- An exact flat control must return \(h\leq10^{-8}\) and RMSE \(\leq10^{-10}\), with \(h=0\) treated as a valid boundary solution.
- Every membrane fit must have finite parameters and objective, valid square-root arguments, \(J\leq J(h=0)\) up to numerical roundoff, and an optimum away from \(h_{\max}\).
- Requested fixed windows must lie inside the nominal coat; otherwise that fit is explicitly inapplicable rather than silently clipped.

For every accepted fit, record the profile and state hashes, \(x\), imposed amplitude, support name, \(R\), \(\alpha_R\), weight, \(h\), \(b\), RMSE, endpoint objectives, stationarity residual when interior, distance from the upper bound, pointwise apex curvature, and nominal coat-mean curvature. Preserve failures and boundary solutions.

For each fixed window, compare the three area labels at the same amplitude and weight. Classify adjacent differences using

\[
\epsilon_h=\max\left(10^{-5},\ 5\max |\Delta h|_{\rm controls}\right).
\]

A difference below \(\epsilon_h\) is unresolved. The fitted cap curvature, pointwise apex curvature, and material coat mean are distinct measurement functionals and must remain separate in tables and claims.

An additional small-window check follows from the regular expansion

\[
z(r)=z_p+\frac{H_p r^2}{2}+\frac{(H_p^3+h_2)r^4}{8}+O(r^6),
\qquad h_2=\frac{C'_0+H_pQ_p}{2}.
\]

After eliminating the offset, linear regression of the quartic mismatch gives

\[
h_{\rm fit}-H_p=\frac{3h_2}{14}R^2+O(R^4)
\quad\hbox{(uniform radial)},\qquad
h_{\rm fit}-H_p=\frac{h_2}{4}R^2+O(R^4)
\quad\hbox{(uniform material area)}.
\]

The coefficients use \(\operatorname{Cov}(r^2,r^4)/\operatorname{Var}(r^2)=6R^2/7\) for uniform radial measure and \(R^2\) for the leading material-area density proportional to \(r\). The corresponding operator norms from normalized-L2 height perturbations to fitted-curvature perturbations are \(\sqrt{45}/R^2\) and \(\sqrt{48}/R^2\). This is a deterministic conditioning statement only; it supplies no experimental noise model.

## Interpretation and stopping rule

Preservation of the sampled apex ordering across the fixed windows and both weights would show that this ordering survives these declared synthetic observation maps for the six saved shapes. A resolved reversal would localize sensitivity to window or weighting; it would not reverse the membrane mechanics. Mixed or unresolved outcomes would show that this surrogate cannot assign a robust observational sign.

This vertical least-squares construction is not the LocMoFit likelihood and does not represent localization uncertainty, angular sampling, cap-area/closing-angle covariance, or experimental nuisance parameters. No result establishes a global area sign, branch stability, or a biological mechanism.

After the bounded result, stop. If the ordering is preserved, the next useful decision is whether to implement one independently specified finite-profile observation likelihood with a small nuisance-weighting sensitivity before any empirical mechanistic comparison. If it reverses or is unresolved, first identify the responsible support/weight dependence. Neither path warrants more amplitude or area sweeps in this cycle.
