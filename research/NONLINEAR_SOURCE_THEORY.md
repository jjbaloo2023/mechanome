# Finite curvature–load compensation for an axisymmetric Helfrich graph

Task `nonlinear-source-theory-001`, attempt 1, 2026-09-26. This analytic note follows the registered [nonlinear design](nonlinear_source_design.json) and the preceding [shallow result](LOAD_IDENTIFIABILITY_FINDINGS.md). It characterizes stationarity of specified graph profiles. It does not establish that such profiles are realized equilibria, stable branches, or biological perturbations.

## Model and first-variation difference

Let \(p=h'(r)\), \(J=(1+p^2)^{1/2}\), and \(C=(rp/J)'/r\), the total curvature \(2H\). The registered energy is

\[
 E[h;c,f]=2\pi\int_0^\infty r\left\{\frac{\kappa}{2}(C-c)^2J+\sigma(J-1)-fh\right\}\,dr.
\]

Here \(\kappa>0\) and \(\sigma>0\) are uniform. The prescribed fields \(c(r)\), \(f(r)\), and the proposed change \(g(r)\) use the *projected* radial coordinate. The load is a vertical dead load per projected area; it has potential \(-2\pi\int rfh\,dr\). Source fields therefore do not move under a height variation.

For a finite change \(c\mapsto c+g\), \(f\mapsto f+\delta f\), subtraction of the two energies at the same arbitrary test graph gives exactly

\[
 \Delta E=2\pi\int_0^\infty r\left\{\kappa\left[-g(C-c)+\frac{g^2}{2}\right]J-\delta f\,h\right\}\,dr. \tag{1}
\]

Thus the full square, in particular its \(g^2J/2\) term, remains in the calculation. For a height variation \(u=\delta h\), \(\delta J=(p/J)u'\) and \(\delta C=r^{-1}(ru'/J^3)'\). Integrating the \(\delta C\) term once gives

\[
 \delta\Delta E=2\pi\int_0^\infty r\{\kappa q_h u'-\delta f\,u\}\,dr,
 \qquad q_h=\frac{(gJ)'}{J^3}+g\left(c-C+\frac g2\right)\frac pJ. \tag{2}
\]

Using \(C=p'/J^3+p/(rJ)\), the apparent \(p'\) terms cancel:

\[
 q_h=\frac{g'}{1+p^2}
      +g\left(c+\frac g2\right)\frac{p}{J}
      -\frac{g p^2}{r(1+p^2)}. \tag{3}
\]

For compact variations and vanishing boundary work, a specified stationary profile \(h\) remains stationary **if and only if**

\[
 \boxed{\displaystyle\delta f_h(r)=-\frac{\kappa}{r}\frac{d}{dr}\big[rq_h(r)\big]
 =-\frac{\kappa}{r}\frac{d}{dr}\left[\frac{rg'}{1+p^2}
 +rg\left(c+\frac g2\right)\frac pJ
 -\frac{gp^2}{1+p^2}\right].} \tag{4}
\]

Necessity follows from the fundamental lemma applied to the arbitrary compactly supported \(u\). Sufficiency follows by reversing the variation. Tension drops out of (4) directly, but the shape slope \(p\) generally depends on tension. This is an exact finite compensation **for one specified stationary profile**, rather than a source transformation shared automatically by all profiles.

## Regularity, net force, and two profiles

Assume the graph and smooth radial sources are regular at the origin: \(p(0)=0\), \(p=O(r)\), and \(g'=O(r)\). Equation (3) gives \(q_h=O(r)\), so (4) is finite at \(r=0\). For example, writing \(a=h''(0)\),

\[
 \delta f_h(0)=-2\kappa\left[g''(0)+g(0)\left(c(0)+\frac{g(0)}2\right)a-g(0)a^2\right]. \tag{5}
\]

If \(g\) is smooth and compactly supported, the correction is compactly supported and has no origin singularity. Its signed net vertical force is

\[
 2\pi\int_0^\infty r\,\delta f_h\,dr
 =-2\pi\kappa[rq_h]_0^\infty=0. \tag{6}
\]

The same endpoint conditions remove the integration boundary terms in (2). Thus a preexisting balanced \(f\) remains balanced. With noncompact decaying sources, the same statements require the displayed flux boundary limits explicitly.

Now take two **specified stationary** registered profiles \(h_1,h_2\), possibly at distinct known tensions \(\sigma_1,\sigma_2\), with the same \(\kappa,c,f\), reservoir and source coordinates. Put \(p_j=h_j'\), \(J_j=(1+p_j^2)^{1/2}\). The same proposed \(g\) and the same \(\delta f\) preserve both precisely when \((r(q_1-q_2))'=0\). Regularity makes the integration constant zero, so the necessary and sufficient pointwise condition is

\[
 \boxed{\displaystyle
 g'\left(\frac1{J_1^2}-\frac1{J_2^2}\right)
 +g\left(c+\frac g2\right)\left(\frac{p_1}{J_1}-\frac{p_2}{J_2}\right)
 -\frac gr\left(\frac{p_1^2}{J_1^2}-\frac{p_2^2}{J_2^2}\right)=0
 \quad\text{for all }r>0.} \tag{7}
\]

Equation (7), together with the explicit common \(\delta f\) from (4), is the conditional two-profile criterion. Different tensions alone do not imply it fails: it is a condition on the actual slopes where \(g\) is supported. For instance, identical slopes on that support make (7) automatic. Nor does (7) assert that two suitable equilibrium branches exist.

## Shallow limit and degenerate control

In a *joint* small-source/small-slope expansion \(p=O(\epsilon)\), \(c=O(\epsilon)\), \(g=O(\epsilon)\), with derivatives controlled on a fixed length scale, (3) becomes \(q_h=g'+O(\epsilon^3)\). Equation (4) therefore reduces at leading order to

\[
 \delta f=-\kappa\Delta_r g+O(\epsilon^3),\qquad
 \Delta_r g=\frac1r(rg')'. \tag{8}
\]

This recovers the universal shallow transformation in the preceding theory. It does not follow merely from a small slope if \(c\) or finite \(g\) remains large.

A flat control shows why failure of a universal finite transformation is not a global identifiability theorem. Let \(h_1=h_2=0\), \(c=f=0\), and take any smooth compact radial \(g\). Both flat profiles are stationary at any positive tensions. Their common exact correction from (4) is \(\delta f=-\kappa\Delta_r g\), balanced by (6), and the full finite square makes no further variation at the flat profile because \(\delta J=0\) there. More generally, coincident slopes on the source support can preserve a local ambiguity. These are stationary-profile statements; they do not claim stability or physical realizability.
