# Two-area local noise-design bound — `cap-two-area-noise-001`, attempt 1

This small follow-up reads the immutable
`research/two_area_results.json` (SHA-256
`8f1a59e52fc5266743631ff060caaa653e55b87af6315a9d3f0d67905973bca7`).
It does not refit or simulate curvature data.

For each **two-area, varying-rigidity** record that has full column rank, the
reported local worst-direction standard deviation in the registered scaled
coordinates is

`sd(z_worst) = sigma_H / s_min(J_z)`.

Here `z_j=theta_j/registered_scale_j`, so this describes a unit direction in
the reference-scaled parameter coordinates, not an individual parameter's
relative confidence interval. The frozen, hypothetical design noise values are
iid equal-variance Gaussian curvature noise `sigma_H = 1e-5, 1e-4, 1e-3
nm^-1`; they are not empirical microscope-noise claims. A short reproduction is:

```python
record = next(r for r in data["records"] if r["label"] == label)
smin = record["singular_values"][-1]
bound = sigma_H / smin
```

| Model case | `s_min` (nm^-1) | `sd(z_worst)` at 1e-5 / 1e-4 / 1e-3 nm^-1 |
| --- | ---: | ---: |
| Shared generic | 1.2463e-3 | 0.00802 / 0.0802 / 0.802 |
| Force proportional to area, generic | 4.3896e-5 | 0.228 / 2.28 / 22.8 |
| Area-specific curvature, generic | 3.6799e-4 | 0.0272 / 0.272 / 2.72 |
| Shared, former single-area exception | 1.2565e-3 | 0.00796 / 0.0796 / 0.796 |

The unknown-rigidity-scale, force-density-ridge, and simultaneous
area-specific-curvature-ridge cases are rank deficient. Their worst-direction
value is explicitly **unidentifiable** (`null` in the JSON); no pseudoinverse
finite uncertainty is supplied.

These values are local conditional CRLB-style design bounds. Large values do
not justify nonlinear precision inference. This calculation does not model
temporal correlation, uncertainty in the parameter-sharing assumption, or any
empirical noise process.
