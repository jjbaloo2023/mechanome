# Two exponential channels do not identify mean axial height

This is a constructive limit of the idealized distributed-signal model in [STAR_OBSERVATION_THEORY.md](STAR_OBSERVATION_THEORY.md). It is an exact observation-model statement, not an empirical claim about STAR, a membrane shape, or biological timing.

Let a normalized axial distribution assign positive weights to four dimensionless heights $u_i=-\log t_i$, with

\[
(t_1,t_2,t_3,t_4)=\left(\frac14,\frac12,\frac34,1\right).
\]

All heights are finite and nonnegative. Set total coat amount $N=1$, both channel amplitudes to one, attenuation coefficients to $a_1=1$ and $a_2=2$, and measurement noise to zero. The two calibrated intensities are then

\[
I_1=\sum_i w_i e^{-u_i}=\sum_i w_i t_i,\qquad
I_2=\sum_i w_i e^{-2u_i}=\sum_i w_i t_i^2.
\]

Consider the two distributions on this *same known support*:

\[
p=\frac1{24}(7,3,9,5),\qquad
q=\frac1{24}(5,9,3,7).
\]

Every weight is strictly positive, each vector sums to one, and $p\ne q$. Their difference is

\[
p-q=\frac1{12}(1,-3,3,-1).
\]

The difference vector has zero sum and is orthogonal to both measured response vectors:

\[
\begin{aligned}
12\sum_i(p_i-q_i)t_i
 &=\frac14-\frac32+\frac94-1=0,\\
12\sum_i(p_i-q_i)t_i^2
 &=\frac1{16}-\frac34+\frac{27}{16}-1=0.
\end{aligned}
\]

Directly evaluating either distribution gives the shared calibrated intensities

\[
I_1=\frac58,\qquad I_2=\frac{15}{32}.
\]

Yet their mean axial heights differ:

\[
\begin{aligned}
\bar u_p-\bar u_q
&=\sum_i(p_i-q_i)(-\log t_i)\\
&=-\frac1{12}\log\!\left[
  \frac{(1/4)(3/4)^3}{(1/2)^3}
  \right]\\
&=\frac1{12}\log\!\left(\frac{32}{27}\right)>0.
\end{aligned}
\]

Thus even exact knowledge of $N$ and two noiseless, perfectly calibrated exponential intensities does not determine mean height for an unknown axial distribution. Calibration or lower measurement noise alone cannot resolve this structural ambiguity. It also follows that the single-position inverse in the earlier note cannot generally be interpreted as the distribution's mean height.

For this fixed, known four-point support, normalization and the two intensities give three independent linear constraints on four weights. The displayed difference vector spans the remaining one-dimensional freedom, and mean height changes along it. One further independent *linear* scalar constraint that varies along this freedom would identify the weights and hence the mean within this support model. Alternatively, an independently measured mean supplies the target directly. For an unrestricted axial distribution, a restriction on its shape or support must be stated and shown sufficient for identification; an unspecified extra scalar measurement is not a general guarantee. The counterexample closes this observation branch at the static identification question. It supplies no temporal threshold, lag, fate, or independent shape validation.
