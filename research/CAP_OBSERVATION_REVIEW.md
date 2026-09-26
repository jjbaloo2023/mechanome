# Review: finite-window spherical-cap observation surrogate

**Task:** `cap-observation-theory-001` attempt 1 under `cap-observation-001`  
**Review tool-clock observation:** 2026-09-25 03:08:41 UTC  
**Disposition:** accept corrected numerical attempt 2 for the declared synthetic vertical-fit question, with the limitations below. Numerical attempt 1 remains rejected evidence.

## Reviewed artifacts and correction history

The review covers the frozen attempt-2 design and source, the exclusive aggregate `cap_observation_results_002.json`, its per-fit records, and `cap_observation_lead_checks.json`. The current and frozen attempt-2 source hashes match (`0ab226500539d3716b4c273a2816a8d063b87f3265e49b20e86ee13e72efae03`); the current and frozen design hashes also match (`02b833e25d66a71dbe9c7019ea8c98e95310e4d1a6b0456c85e5788cf1d31ce2`). The aggregate records these dependencies and all six saved-state hashes.

Attempt 1 is preserved and rejected. Its `np.interp` call did not invert the monotone map \(r(\rho)\), and its endpoint-weighted node averages did not represent the declared continuous measures. Its outputs must not enter scientific tables or claims. Attempt 2 instead solves \(r(\rho)=r\) by bracketed roots and uses Gauss-Legendre quadrature.

## Mathematical and numerical checks

The rationalized cap function, its \(h=0\) limit, the analytically eliminated free offset, and

\[
\partial_h g=\frac{r^2}{\sqrt{1-h^2r^2}\,[1+\sqrt{1-h^2r^2}]}
\]

agree with the theory note. The material-area density \(r/\cos\psi\) follows from \(d\alpha/dr=r/\cos\psi\). The exact pole is included as a Hermite-spline knot with regular pole derivatives, while the frozen RHS is evaluated only off the axis.

The corrected aggregate contains all 48 declared membrane fits. All optimizer flags are successful; no membrane fit selects the flat or upper-curvature boundary; every stored objective is no worse than its explicit flat candidate. The maximum inverse-map round-trip error is \(2.494\times10^{-14}\). The largest absolute stored 201-node gradient is \(4.613\times10^{-11}\). Sphere and flat controls pass: the former recovers \(h=0.4\) and \(b=0.02\) within the registered tolerances, and the latter selects the explicit \(h=0\) boundary with zero residual.

The independent lead check reevaluates the objective and normal equation at 401 nodes without another optimization. All 48 normalized stationarity residuals pass the predeclared \(10^{-3}\) gate; the maximum is \(1.780\times10^{-5}\). Stable-function and complex-step derivative checks have maximum errors \(4.34\times10^{-16}\) and \(5.55\times10^{-17}\), respectively, and the objective is invariant to a vertical translation within rounding error. This is an objective/stationarity check at the saved 201-node optimum, not a reoptimized parameter-convergence result.

The pole-series prediction also passes independently. For all twelve \(R=0.1\) amplitude/area/weight combinations, the leading predicted cap-fit bias agrees with the fitted bias to at worst \(4.505\times10^{-4}\) relative error, well inside the declared 2% gate. This validates the small-window mapping and its weight dependence for these profiles.

The aggregate was created at 2026-09-25 03:06:54 UTC, before the fixed 03:10:12 UTC computation cutoff. The implementation checks the deadline before controls and fits, but does not interrupt an optimization already in progress. That weaker guard did not affect this completed run and should not be described as a hard in-fit timeout.

## Result and scope

For every fixed physical window \(R/\ell=0.1,0.25,0.4\), at both amplitudes and under both declared measures, the normalized fitted curvature has the resolved ordering

\[
h(x=0.5)>h(x=1)>h(x=2).
\]

All twelve fixed-window comparisons therefore preserve the sampled negative area ordering previously observed at the apex. The closest adjacent separation is far above the \(10^{-5}\) classification threshold. For example, at \(c_{\rm repo}\ell=0.6\), the uniform-r values are

\[
\begin{array}{c|ccc}
R/\ell & x=0.5 & x=1 & x=2\\ \hline
0.1 & 0.829719 & 0.605018 & 0.281961\\
0.25 & 0.832031 & 0.606698 & 0.282755\\
0.4 & 0.836352 & 0.609835 & 0.284233
\end{array}
\]

for \(h/C_{\rm source}\). Uniform material-area weighting gives the same ordering. The low-amplitude profiles give the same conclusion.

The fit is measurably window-dependent. Relative to apex curvature, the fitted-curvature bias spans about 0.0528--0.0625% at \(R=0.1\), 0.3307--0.3912% at \(R=0.25\), and 0.8494--1.004% at \(R=0.4\). Whole-coat biases range from 1.305% to 27.644%. Whole-coat support changes strongly with \(x\), however, so those fits diagnose measurement-functional mismatch and cannot serve as a fair fixed-support area comparison. Radial and material-area weights also produce distinct values even when their ordering agrees.

These results establish preservation only for six saved, mild-to-moderate passive profiles under a deterministic vertical least-squares cap surrogate. Pointwise apex curvature, nominal material coat mean, and fitted cap curvature remain distinct observables. The calculation is not a LocMoFit likelihood, contains no localization or sampling noise, and does not establish a global area sign, stability, a biological mechanism, or agreement with an empirical measurement pipeline.

## Next decision

Stop the synthetic sweep here. Before comparing with empirical fitted curvatures, decide whether the actual observation model can be represented with a bounded surrogate that matches the relevant LocMoFit sampling and likelihood assumptions, including only a small declared nuisance-weighting sensitivity. If those assumptions cannot be specified from available methods, retain the present result as a synthetic measurement-map check and do not promote it to an empirical fit claim.
