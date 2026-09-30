# Independent review: two-channel STAR observation model

The registered calculation is an idealized two-channel exponential model with known amplitudes and attenuations, positive coat amount, and additive independent log-channel errors. It is not the published distributed-axial-position STAR forward model, an empirical calibration, or an observation of membrane shape, temporal lag or fate.

## Algebraic review criterion

Write `y_g=log(I_g/A_g)`, `y_r=log(I_r/A_r)`, `n=log N`, and `D=a_g-a_r`. For `D != 0`, the only candidate inverse is `u=(y_r-y_g)/D`, `n=(a_g*y_r-a_r*y_g)/D`. Its noise covariance must follow from this same linear inverse, not from treating inferred axial position and either input intensity as independent. At `D=0`, `u` is not identified; the single observed combination is `n-a_g*u`. As `D` approaches zero, inverse error coefficients scale as `1/|D|` and variances as `1/D²` for nonzero noise.

## Disposition

Accepted within the stated idealized model. `STAR_OBSERVATION_THEORY.md` uses the correct inverse and conditional noise covariance. For independent log errors of variances `v_g,v_r`, it gives `Var(u_hat)=(v_g+v_r)/D²`, `Cov(n_hat,u_hat)=(a_r*v_g+a_g*v_r)/D²`, `Cov(y_g,u_hat|n,u)=-v_g/D`, and `Cov(y_r,u_hat|n,u)=v_r/D`; the latter two show that a measured coat channel and a position inferred from the same channels have shared measurement error. Its equal-coefficient null direction is correct. The note also appropriately limits the inverse to a point axial position or an additionally constrained distribution, distinguishes conditional error covariance from between-event biology, and does not infer a temporal lag from simultaneous formulas.

The one registered exact-rational invocation in `star_observation_checks.json` passed five nonsingular cases and the equal-attenuation null case. Static inspection of `star_observation_checks.py` confirms the matrix inverse, covariance, cross-channel covariance and determinant identities correspond to the design's fixed six inputs; the near-equal cases exhibit the expected `1/D²` growth. No repeat, fit, source call, simulation, or timing calculation was needed. The outcome is a useful observation-contract warning: the two-channel axial proxy and a coat channel cannot be counted as independent measurements merely because they yield two derived traces. It does not validate actual STAR calibration, full coat axial distributions, membrane shape, biological timing, or scission.
