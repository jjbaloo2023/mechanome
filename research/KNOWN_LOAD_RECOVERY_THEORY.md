# One-profile curvature recovery with a fixed known vertical load

Task `known-load-recovery-001`, attempt 1, 2026-09-29. This result concerns the registered axisymmetric projected-source Helfrich graph model, with fixed known rigidity \(\kappa>0\), tension \(\sigma>0\), and smooth compact balanced vertical dead load \(f\). The curvature source \(c\) is smooth, radially regular, and has smooth zero extension outside the **known** projected disk \(0\le r\le1\). Heights have a regular origin and a decaying flat reservoir. The statement compares *actual stationary graphs* with the same \(\kappa,\sigma,f\), not arbitrary measured curves. The zero load is an especially simple permitted case.

**Result.** One complete normalized-slope profile \(u=h'/\sqrt{1+h'^2}\) determines \(c\) uniquely. Moreover, there are \(\delta_*>0\) and \(L<\infty\), depending only on \(\kappa,\sigma\), the fixed load through \(B=\|q\|_{C^0[0,1]}\) below, and the declared support radius 1, such that any two admitted stationary profiles with \(\|u_j\|_{C^1[0,1]}\le\delta_*\) satisfy

\[
 \boxed{\quad\|c_1-c_2\|_{C^0([0,\infty))}
 \le L\|u_1-u_2\|_{C^1([0,1])}.\quad} \tag{1}
\]

The same \(L\) works as both profiles approach flatness. This is a one-derivative inverse estimate: the source is controlled in the uniform norm by one radial derivative of normalized slope. The estimate is conditional on the two profiles lying in the stationary-profile range with the same known load; it does not say that an arbitrary perturbed slope admits a smooth compact source. Same-profile uniqueness does not need the smallness restriction.

## Exact flux and terminal reconstruction

Put \(p=h'\), \(u=p/\sqrt{1+p^2}\), \(C=u'+u/r\), \(t=C-c\), and \(\lambda=\sigma/\kappa\). The exact full-square first variation gives total radial flux

\[
 Q=\kappa\left[-(1-u^2)t'-tuu'+\frac{t^2}{2}u\right]+\sigma u.
 \tag{2}
\]

This is the flux of [NONLINEAR_EXISTENCE_THEORY.md](NONLINEAR_EXISTENCE_THEORY.md), with \(\kappa\) restored; it retains the \(c^2\) contribution. Because the vertical load enters the energy as \(-2\pi\int rfh\,dr\), stationarity has sign

\[
 (rQ)'=-rf. \tag{3}
\]

As a direct check against the accepted [finite source calculation](NONLINEAR_SOURCE_THEORY.md), replacing \(c\) by \(c+g\) at the same graph changes \(Q/\kappa\) by exactly \((1-u^2)g'-gu^2/r+(cg+g^2/2)u\). The \(g^2\) term is retained and the sign agrees with (3).

At the regular origin, \(u=O(r)\), \(C'=O(r)\), \(c'=O(r)\), and \(Q=O(r)\). Thus the integration constant in (3) vanishes. The known load fixes the entire flux:

\[
 q(r):=\frac{Q(r)}{\kappa}
 =-\frac{1}{\kappa r}\int_0^r s f(s)\,ds,\qquad q(0)=0. \tag{4}
\]

The load's balance makes \(Q=0\) beyond its support, as required by the decaying reservoir. On the source disk, (2) is the first-order Riccati equation

\[
 \boxed{\quad
 t'=F(r,t,u,u')
 :=\frac{-q(r)-tuu'+(t^2/2+\lambda)u}{1-u^2}.
 \quad} \tag{5}
\]

A finite graph has \(|u|<1\), so the coefficient \(1-u^2\) never vanishes. Smooth zero extension of \(c\) supplies the outer terminal value

\[
 t(1)=C(1)=u'(1)+u(1). \tag{6}
\]

For an admitted profile, solve (5) backward from (6), then recover \(c(r)=u'(r)+u(r)/r-t(r)\) on \(0<r\le1\), extend at the regular origin by \(C(0)=2u'(0)\), and set \(c=0\) for \(r\ge1\). This is a mathematical reconstruction formula, not an assertion of solvability or smooth matching for arbitrary input. The complete profile supplies the values on the source disk and verifies the required exterior stationary equation and decay. At the origin \(q(0)=u(0)=0\), so (5) also gives \(t'(0)=0\) for a regular admitted solution.

If two sources give the *same* admitted \(u\), their two \(t\)'s have the same terminal value. Subtracting (5) gives a homogeneous linear equation for their difference:

\[
 (t_1-t_2)'=
 \frac{-uu'+\tfrac12u(t_1+t_2)}{1-u^2}(t_1-t_2). \tag{7}
\]

Ordinary terminal-value uniqueness on every \([\epsilon,1]\), followed by \(\epsilon\downarrow0\) and radial continuity, yields \(t_1=t_2\) and \(c_1=c_2\). The flux condition at the origin is essential: without it, an unknown point reaction could contribute an integration constant to (4).

## Uniform near-flat Lipschitz bound

Here the fixed load, \(\kappa\), and \(\sigma\) are identical for both profiles, so \(q\) and \(\lambda\) in (5) are identical. Write \(B=\|q\|_{C^0[0,1]}\), and select \(M=4(B+\lambda+1)\). Choose \(0<\delta_*<1/2\) sufficiently small that

\[
 2\delta_*+2B+2\delta_*^2M+\delta_*M^2+2\lambda\delta_*<M. \tag{8}
\]

Such a choice exists because the left side tends to \(2B<M\) as \(\delta_*\downarrow0\). For \(\|u\|_{C^1[0,1]}\le\delta_*\), the terminal value has \(|t(1)|\le2\delta_*\) and \((1-u^2)^{-1}\le2\). While \(|t|\le M\), backward integration of (5) over an interval of length at most one gives

\[
 |t(r)|\le
 2\delta_*+2B+2\delta_*^2M+\delta_*M^2+2\lambda\delta_*<M. \tag{9}
\]

A first-exit argument from the terminal point proves \(\|t\|_{C^0[0,1]}\le M\) for **every admitted** profile in this slope ball. No bound on an unknown source was assumed to obtain \(M\).

On the compact coefficient set \(|u|,|u'|\le\delta_*\), \(|t|\le M\), \(|q|\le B\), the rational right side of (5) has finite Lipschitz constants \(L_t,L_d\) in \(t\) and in the pair \((u,u')\), uniformly in \(r\). Let \(d=\|u_1-u_2\|_{C^1[0,1]}\). The terminal values differ by at most \(2d\); subtracting (5) and applying backward Gronwall therefore gives

\[
 \|t_1-t_2\|_{C^0[0,1]}
 \le e^{L_t}(2+L_d)d. \tag{10}
\]

Because \(u_j(0)=0\), the mean-value theorem gives \(|(u_1-u_2)(r)/r|\le d\) for \(r>0\), including its continuous origin limit. Consequently \(\|C_1-C_2\|_{C^0[0,1]}\le2d\). Since \(c_j=C_j-t_j\) and both sources vanish outside the disk, (1) holds with the explicit permissible choice \(L=2+e^{L_t}(2+L_d)\). The constants remain bounded as \(u_j\to0\), including for the fixed zero load, where \(B=0\). The estimate does not claim a zero-noise bound from slope values alone; it requires their radial derivatives.

## Scope relative to earlier inverse and observation results

This known-load conclusion is consistent with [NONLINEAR_INVERSE_STABILITY_THEORY.md](NONLINEAR_INVERSE_STABILITY_THEORY.md): that counterexample **changes the load** while keeping one profile fixed and makes a second profile differ by only cubic order. Its pairs also defeat a uniform estimate in the present weaker norms if the load is allowed to vary: their source difference has \(C^0\) size \(\varepsilon\|\phi\|_{C^0}\), whereas their complete slope difference has \(C^1\) size at most \(O(\varepsilon^3)\). Equation (4) forbids that compensation when \(f\) is fixed. Compact source support supplies the terminal value (6), and origin regularity supplies the flux (4); together they remove the source/load ambiguity for one exact profile.

The theorem is structural for the registered graph and projected-load convention. The [LocMoFit observation contract](LOCMOFIT_OBSERVATION_CONTRACT.md) does not provide a calibrated complete normalized-slope profile, and most deposited deep caps cannot be represented by a single-valued whole-cap graph. The [independent controls audit](INDEPENDENT_CONTROLS_FINDINGS.md) does not establish a measured spatial load or the needed registered profile. Thus (1) does not yet yield a source estimate or mechanism preference from those processed data. No BVP, numerical conditioning experiment, new empirical claim, or external search is used here.
