# Two-channel axial observation: an idealized inverse

This note studies an idealized observation model motivated by the dual-tagged clathrin axial-ratio approach of Nawara et al. (2022). It is an independent calculation, not a reconstruction of their full STAR forward model or inference method.

Let $x=\log N$, where $N>0$, and $u=z/d_{\rm ref}$. Divide each intensity by its known amplitude $A_c>0$ before taking logs. For channels $c\in\{g,r\}$, assume

\[
y_g=x-a_g u+e_g,\qquad y_r=x-a_r u+e_r,
\]

where $a_g,a_r>0$ are known and fixed. Conditional on the true $x,u$, the log errors have mean zero, finite variances $v_g,v_r$, and are independent. All covariances below are conditional on fixed $x,u$; they describe measurement uncertainty, not variation between biological events.

## Inverse and identification

Put $\Delta=a_g-a_r$. If $\Delta\ne0$, solving the two linear equations gives

\[
\hat u=\frac{y_r-y_g}{\Delta},\qquad
\hat x=\widehat{\log N}=\frac{a_g y_r-a_r y_g}{\Delta},\qquad
\hat N=\exp(\hat x).
\]

These estimators are unbiased for $u$ and $x$ under the stated log-error assumptions; this does not make $\hat N$ unbiased for $N$. At $a_g=a_r=a$, both noiseless channels measure only $q=x-au$. Every pair $(x+at,u+t)$, for any real $t$, gives the same $q$. Thus $x$ and $u$ are not separately identifiable, even with noiseless measurements.

## Shared measurement uncertainty

Subtracting the true values from the inverse yields

\[
\hat x-x=\frac{-a_r e_g+a_g e_r}{\Delta},\qquad
\hat u-u=\frac{-e_g+e_r}{\Delta}.
\]

Independence therefore gives the complete covariance matrix, in the order $(\hat x,\hat u)$:

\[
\operatorname{Cov}\!\begin{pmatrix}\hat x\\\hat u\end{pmatrix}
=\frac{1}{\Delta^2}
\begin{pmatrix}
a_r^2v_g+a_g^2v_r & a_rv_g+a_gv_r\\
a_rv_g+a_gv_r & v_g+v_r
\end{pmatrix}.
\]

The off-diagonal entry is positive when the variances are positive: inferred coat amount and axial position share the same channel errors. Likewise, each *measured log channel* is coupled to the inferred position:

\[
\operatorname{Cov}(y_g,\hat u\mid x,u)=-\frac{v_g}{\Delta},\qquad
\operatorname{Cov}(y_r,\hat u\mid x,u)=\frac{v_r}{\Delta}.
\]

These signs presume the written channel order and can reverse when $\Delta$ changes sign. If events with different true $x,u$ are pooled, each observed channel-position covariance also contains the biological covariance $\operatorname{Cov}(x-a_cu,u)$; the formulas above isolate only the error-induced component. Consequently, a correlation of a channel with inferred position cannot by itself establish an independent biological relationship.

As $a_g\to a_r$, the inverse divides channel differences by $\Delta$. With nonzero fixed noise variances, $\operatorname{Var}(\hat u)=(v_g+v_r)/\Delta^2$ diverges. For positive attenuations approaching a common positive value, the variance of $\hat x$ and its covariance with $\hat u$ also grow as $1/\Delta^2$. This is the approach to the exact nonidentifiability at equality, not a numerical artifact.

## Scope of the calculation

Real axially distributed coat signal is more naturally written as $I_c/A_c=\int n(z)\exp[-a_c z/d_{\rm ref}]\,dz$. If $N=\int n(z)\,dz$ and $p(z)=n(z)/N$, its log channel is $\log N+\log\mathbb E_p[\exp(-a_c z/d_{\rm ref})]$. The log of this weighted integral generally is not $\log N-a_c u$ for one common physical $u$. With an unknown distribution $p$, two channel values cannot identify $N$ and the distribution or independently validate a membrane shape. The inverse above applies exactly to a point axial position, and otherwise only under additional, stated constraints on that distribution.

Known amplitudes and attenuations are assumptions, not calibration results. Errors or drift in $A_c$ or $a_c$, cross-channel error covariance, backgrounds, and deviations from the exponential response can bias the inverse or alter its covariance. These formulas also concern simultaneous observations only. A time at which a noisy inferred trace crosses a threshold depends on sampling, filtering, threshold choice, and correlated errors across time; no threshold-time uncertainty, biological lag, or fate follows from the static covariance calculation.
