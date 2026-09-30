# When two exact graph profiles exclude a compact curvature change

Task nonlinear-uniqueness-theory-001, attempt 1, 2026-09-26. This is a conditional analytic continuation of the registered [nonlinear uniqueness design](nonlinear_uniqueness_design.json) and the [finite source calculation](NONLINEAR_SOURCE_THEORY.md). The prerequisite is **two actual stationary axisymmetric graph profiles** at distinct known positive tensions, with the same prescribed projected-coordinate curvature \(c(r)\), vertical dead load \(f(r)\), uniform \(\kappa>0\), flat reservoir and boundary convention. The proof below is conditional on that prerequisite; prescribed slope curves alone do not supply it.

Let \(g\) be a smooth radially regular curvature change with smooth zero extension outside the fixed disk \(0\le r\le R_0<\infty\). Thus \(g'(0)=0\), \(g(R_0)=0\), and all derivatives needed below match zero at \(R_0\). Write

\[
p_j=h_j',\qquad J_j=\sqrt{1+p_j^2},\qquad
u_j=\frac{p_j}{J_j},\qquad D=u_1-u_2,\qquad S=u_1+u_2.
\]

Slopes are finite and radially regular, and \(c,g\) are smooth enough for the first variation. The preceding exact calculation says that one balanced projected vertical load correction preserves both profiles if and only if

\[
A(rg)' +rD\left(cg+\frac{g^2}{2}\right)=0,\qquad
A=J_1^{-2}-J_2^{-2}. \tag{1}
\]

Because \(J_j^{-2}=1-u_j^2\), **exactly**

\[
A=-(u_1-u_2)(u_1+u_2)=-DS.
\]

Consequently the complete finite compatibility equation is

\[
\boxed{\displaystyle D\left[-S(rg)'+r\left(cg+\frac{g^2}{2}\right)\right]=0.} \tag{2}
\]

No \(g^2\) term has been dropped. Where \(D\ne0\) and \(S\ne0\), put \(w=rg\). Equation (2) is the Riccati initial-value equation

\[
\boxed{\displaystyle
w'=\frac{c}{S}w+\frac{1}{2rS}w^2,\quad r>0.} \tag{3}
\]

Equivalently \(g'=(-1/r+c/S)g+g^2/(2S)\). For an infinitesimal proposal \(g=\varepsilon\phi\), the coefficient of \(\varepsilon\) in (2) is

\[
\boxed{\displaystyle D[-S(r\phi)'+rc\phi]=0,} \tag{4}
\]

and where \(D S\ne0\), \((r\phi)'=(c/S)(r\phi)\). The finite equation can therefore admit algebraic roots that the infinitesimal equation misses.

## A sufficient uniqueness theorem

Suppose, on the **entire declared source interval** \(0<r\le R_0\):

1. \(S(r)\ne0\), including at the outer endpoint \(R_0\); equivalently \(p_1(r)+p_2(r)\ne0\).
2. The set where \(D(r)\ne0\) is dense; equivalently the equal-slope set \(\{p_1=p_2\}\) contains no open interval.

Then a smooth compact \(g\) satisfying (2) is identically zero. In particular, if these conditions hold for two actual common-source stationary profiles, their shared compact curvature change is unique within the declared model: \(g=0\).

**Proof.** On the dense set \(D\ne0\), divide (2) by \(D\). Its bracket is continuous, so the bracket vanishes throughout \(0<r\le R_0\), including isolated or more complicated nowhere-dense equal-slope zeros. Since \(S\ne0\), (3) holds throughout that interval. For each \(\epsilon>0\), \(c/S\) and \(1/(2rS)\) are bounded and continuous on \([\epsilon,R_0]\). The right-hand side of (3) is locally Lipschitz in \(w\), so the initial value \(w(R_0)=R_0g(R_0)=0\) has the unique solution \(w=0\) on \([\epsilon,R_0]\). Letting \(\epsilon\) approach zero gives \(g(r)=0\) for every \(r>0\), and radial continuity gives \(g(0)=0\). The proof propagates from the **outer support boundary**; it does not use a singular origin initial-value theorem. The same argument makes the infinitesimal kernel (4) trivial under these hypotheses.

The theorem asks for a nonsingular outer endpoint. If \(S(R_0)=0\), one may instead start at a positive radius inside a known zero collar of \(g\), but propagation across subsequent zeros of \(S\) needs its own argument. Mere nonzero \(A\) at some isolated points is insufficient.

## Coefficient zeros and the origin

The factorization separates distinct cases:

- **Equal slopes:** \(p_1=p_2\) gives \(D=A=0\), and (2) imposes no local condition. Isolated or nowhere-dense equal-slope zeros do not defeat the theorem when \(S\ne0\), because continuity extends (3) across them. If the slopes agree throughout an open interval, any smooth \(g\) supported strictly inside that interval is algebraically compatible there. Whether such an interval occurs for two actual common-source stationary profiles is a separate equilibrium question.
- **Opposite nonzero slopes:** \(p_1=-p_2\ne0\) gives \(S=A=0\), \(D\ne0\), and the *finite* pointwise condition becomes \(g(c+g/2)=0\): either \(g=0\) or \(g=-2c\) at that radius. At such a point the *infinitesimal* condition is \(c\phi=0\). Thus, if \(c=0\), the linear condition is silent while the finite condition forces \(g=0\); if \(c\ne0\), the finite root \(g=-2c\) is not visible as an infinitesimal branch. On an interval with exactly opposite slopes, \(g=-2c\) is an algebraic compatibility example if smooth \(c\) is supported inside that interval, but it is **not** an example of two jointly realizable stationary profiles.
- **An isolated zero of \(S\):** the pointwise root condition applies when \(D\ne0\), while (3) is singular there. Propagation of the zero solution across that point cannot be inferred from the theorem. The result depends on the local vanishing orders and on \(c\); no equilibrium or uniqueness claim follows merely from a zero in a plotted coefficient.
- **Both slopes zero:** \(D=S=0\), so (2) gives no condition at that point. An interval of equal zero slopes has the same algebraic freedom as an equal-slope interval.

At the origin, smooth radial graphs have \(p_j(r)=a_jr+O(r^3)\), while \(c(r)=c_0+O(r^2)\) and \(g(r)=g_0+O(r^2)\). Then \(S=(a_1+a_2)r+O(r^3)\) and \(D=(a_1-a_2)r+O(r^3)\). If \(a_1\ne a_2\), the leading \(r^2\) term of (2) yields the necessary origin condition

\[
\boxed{\displaystyle
g_0\left[c_0+\frac{g_0}{2}-(a_1+a_2)\right]=0.} \tag{5}
\]

This permits the algebraic values \(g_0=0\) and \(g_0=2(a_1+a_2-c_0)\); it does not establish a smooth global solution from either value. If \(a_1=a_2\), that leading order vanishes and higher profile terms matter. Under the theorem, exterior propagation already gives \(g_0=0\), regardless of these local alternatives.

For a genuine degenerate stationary family, let \(h_1=h_2=0\) at any two positive tensions, take any smooth compact radial \(c\), and prescribe \(f=-\kappa\Delta_r c\). The flat graph is stationary under the declared full-square energy at both tensions. Every smooth compact radial \(g\) then has the common correction \(\delta f=-\kappa\Delta_r g\), with zero net added force. Here \(D=S=0\) everywhere. This actual flat example prevents a global two-tension identifiability claim. In contrast, the equal-slope and opposite-slope cases above only describe coefficients unless their profiles separately pass the common-source stationarity and boundary equations.

## Interpretation

The theorem is a sufficient **structural** test for a fixed compact support and two actual profiles. It does not assert that changing tension produces slopes meeting its hypotheses, or that observed profiles and source fields can be calibrated accurately. If slopes and both source fields scale jointly as \(O(\varepsilon)\), then \(D,S=O(\varepsilon)\), \(A=-DS=O(\varepsilon^2)\), and for \(g=O(\varepsilon)\) both terms in (1) are \(O(\varepsilon^3)\) on a fixed length scale. Thus an exact nonzero coefficient can still provide weak separation in the shallow regime. Recovering slopes, their radial derivatives, source support, registration, and noise behavior remains a separate inverse problem; no precision or empirical mechanism follows here.
