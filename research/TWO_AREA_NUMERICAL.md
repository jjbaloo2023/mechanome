# Two-area numerical experiment — `cap-two-area-numerical-001`, attempt 1

This is a registered synthetic measurement-design calculation. It uses the
zero-line-tension cap limit, with `A0 = pi*60^2 nm^2`, `A1=A0`, `A2=2A0`,
`C=0.03 nm^-1`, `sigma=0.02 kBT nm^-2`, `kappa0=20 kBT`, a rigidity factor of
3, and 24 coverage frames. `P0=F0/kBT=C*sigma*A0/2` (`F0=13.96 pN`) is the
single-area ridge reference. These are not empirical estimates.

The observable was calculated as

`H_i = clip_domain[u(4*pi*kappa*C_i + P_i)/(8*pi*kappa + sigma*A_i)]`.

The clip is the actual source angular domain (`psi=0.02` through `pi-0.001`),
not an unconstrained continuum endpoint. Analytic derivatives are zero on clip
saturation. Finite differences check only interior analytic values, never a
grid argmin. The stored SVD uses dimensionless columns `z_j=theta_j/scale_j`,
with scales `(C,C_i)=0.03 nm^-1`, `P=3.3929 nm^-1`,
`sigma=0.02 kBT nm^-2`, `rho=P0/A0`, and rigidity scale one.

For shared `C,P,sigma`, a varying known rigidity ramp gives generic rank 3 at
one area. At the exceptional single-area condition `P=C*sigma*A0/2`, rank is
2; adding the second known area restores rank 3 because the same `P` cannot
satisfy that condition at two distinct areas. With constant rigidity, two
areas remain rank 2: two scalar area observations cannot identify three shared
parameters.

If force is constrained to `P_i=rho*A_i`, the exact transformation
`sigma -> alpha*sigma, rho -> alpha*rho` preserves every two-area trajectory on
`rho=C*sigma/2`; the second area does not break that ridge. With area-specific
curvatures, the generic two-area varying-rigidity system is full rank 4. Its
exception is narrower: both areas must obey `C_i*A_i=2P/sigma`, after which
`sigma -> alpha*sigma, P -> alpha*P` is exact. An unknown global rigidity
scale always has `(kappa scale,P,sigma) -> alpha*(kappa scale,P,sigma)` as an
exact symmetry, leaving generic rank 3 of 4 even with two areas.

The two-area, varying-rigidity, full-rank cases have dimensionless-Jacobian
condition numbers of about 46.3 (shared generic), 1,339 (force proportional to
area, generic), and 118.8 (area-specific curvature, generic). These are local
design/scaling amplification proxies, not microscope precision or empirical
error bars: changing the declared parameter scales or area/rigidity schedule
changes them. The original experiment did not include noise; the subsequent local design
postprocess is recorded separately in TWO_AREA_NOISE.md. Equal or nearly equal areas, a
small area contrast relative to `8*pi*kappa/sigma`, and a small rigidity
contrast are expected to yield degeneracy or poor conditioning; they were not
numerically swept here.

The JSON stores clipping counts, ranks, singular values, finite-difference
agreement, symmetry errors, source hashes, and environment. The original PNG
is retained as a historical first render. `render_two_area.py` reads only the
immutable JSON and exclusively creates `two_area_comparison_v2.png`, plotting
each singular spectrum normalized by its largest value. Its true rank line is
therefore `1e-10` in unitless relative sensitivity; values below `1e-16` use a
display floor. Render input SHA-256:
`8f1a59e52fc5266743631ff060caaa653e55b87af6315a9d3f0d67905973bca7`.
Renderer SHA-256: `5a2a60633dff4eb8f626ee0c8d2ed499f3daa764887b34cd3f5add020e92137e`.
Rendered at `2026-09-23T01:21:47.533572+00:00` with Matplotlib's Agg backend.
