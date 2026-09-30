# Shared-channel observation: conditional result

Accepted after independent theory, arithmetic and scope review on 29 September 2026. The registered idealized model has one coat amount N and one axial coordinate u per event, known channel amplitudes and positive attenuation coefficients. It is a point-height observation model, not the full STAR distribution model.

For normalized log channels y_g = log(N) - a_g*u + e_g and y_r = log(N) - a_r*u + e_r, let D = a_g - a_r. If D is nonzero, u_hat = (y_r-y_g)/D and log(N)_hat = (a_g*y_r-a_r*y_g)/D. Equal coefficients leave a null direction and cannot distinguish amount from height.

With independent zero-mean log errors of variances v_g and v_r, Cov(log(N)_hat,u_hat) = (a_r*v_g+a_g*v_r)/D^2. The two reconstructed quantities therefore have correlated measurement error even when the channel errors are independent. Var(u_hat) = (v_g+v_r)/D^2, so the inversion becomes sensitive to noise as coefficients approach equality. This statement is conditional on fixed latent N,u and calibration; it is not an empirical across-event correlation.

The sole [exact rational check](star_observation_checks.json) verified five nonsingular cases and the equal-coefficient null direction at 17:43:12 UTC, 29 September 2026. It checks algebra for fixed hypothetical inputs, not a biological hypothesis. The [design](star_observation_design.json), [checker](star_observation_checks.py), [theory](STAR_OBSERVATION_THEORY.md) and [independent review](STAR_OBSERVATION_REVIEW.md) define its scope.

## What follows

A future joint comparison should propagate channel-level uncertainty through the shared inverse. Treating raw coat intensity and ratio-derived axial position as independent measurements would require a separate justification. This calculation does not show that the published study made that error, or establish an observed timing bias.

The public workbook remains uninspected after a [local access failure](STAR_WORKBOOK_SCHEMA_FINDINGS.md). Real coats occupy a distribution of heights, amplitudes and attenuation depths need calibration, and threshold timing adds selection and temporal dependence. No membrane-shape validation, force, scission, empirical lag, or novel biological mechanism follows.
