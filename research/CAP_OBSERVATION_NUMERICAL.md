# Finite-window cap-fit numerical record

Accepted evidence is corrected attempt 2: cap_observation_results_002.json and
cap_observation_records_002/. The first attempt is invalid and preserved; its
inverse interpolation mapped coordinates in the wrong direction and its node
weights did not implement the declared continuous quadrature. Its tests checked
analytic controls but missed the spatial-map defect. Do not use those fit values.

Attempt 2 solves r(rho)=r with bracketed roots, verifies source NPZ hashes,
includes the regular pole, uses 201-node Gauss-Legendre quadrature with either
uniform radial or r/cos(psi) material-area weighting, and eliminates a free real
height offset analytically. The actual physical support defines the curvature
bound. Flat and upper endpoints are evaluated explicitly; endpoint objectives,
fit gradient and inverse-map residuals are retained.

All four sphere/flat controls pass and all 48 membrane fits completed before
03:10:12 UTC; aggregate creation was 03:06:54 UTC. Each control and fit has an
exclusive durable JSON record. Exact source/design byte copies were frozen before
execution and match recorded hashes. Deadline checks occur before controls/fits;
there is no hard in-optimizer interruption.

Two corrected-version tests cover nonidentity inverse-map round trip, sphere/flat
controls and deadline refusal. The lead made test time deterministic so future
runs do not fail solely because the historical deadline has passed; final result
was 2 passed in 0.82 seconds. No membrane optimization or BVP was repeated by the
lead audit. Independent 401-node objective/stationarity and analytic pole-series
checks are in cap_observation_lead_checks.json. See CAP_OBSERVATION_REVIEW.md for
the limited scientific disposition and CAP_OBSERVATION_FINDINGS.md for the result.
