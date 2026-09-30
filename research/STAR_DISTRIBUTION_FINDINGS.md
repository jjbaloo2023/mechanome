# Identical fluorescence signals can hide different mean heights

**Accepted after independent review, 29 September 2026.** In the registered idealized model, two different positive axial distributions have the same total coat amount and exactly the same two calibrated fluorescence intensities, yet different mean axial heights. Noise reduction alone cannot resolve this ambiguity.

This is a mathematical observation limit. It is not a reconstructed membrane, an empirical STAR result, or a biological mechanism claim.

## The exact example

Set total amount to one, channel amplitudes to one, and attenuation coefficients to one and two. At each height u, let t=exp(-u). Both distributions use the same four finite, nonnegative heights.

| t | Height u | Distribution P weight | Distribution Q weight |
| --- | --- | --- | --- |
| 1/4 | log(4) | 7/24 | 5/24 |
| 1/2 | log(2) | 3/24 | 9/24 |
| 3/4 | log(4/3) | 9/24 | 3/24 |
| 1 | 0 | 5/24 | 7/24 |

Every weight is strictly positive; each column sums to one. The measured signals are the weighted means of t and t squared. Both distributions give **5/8 and 15/32**. Their mean-height difference is nevertheless **log(32/27)/12 > 0**, P minus Q.

The [proof](STAR_DISTRIBUTION_THEORY.md) shows why the weight difference leaves both signals unchanged. The sole [exact arithmetic invocation](star_distribution_checks.json), at 18:02:56 UTC, checked the fixed pair without searching, approximating logarithms or running a second example. The [independent review](STAR_DISTRIBUTION_REVIEW.md) accepted the algebra and scope. Inputs and limits were [registered first](star_distribution_design.json).

## What this changes

The earlier [single-position inverse](STAR_OBSERVATION_FINDINGS.md) remains correct under its assumptions. Its inferred axial coordinate cannot generally be called the mean height of a distributed coat. A biological comparison needs a stated distribution family or support restriction shown to make the target identifiable, or an independent measurement that constrains the missing quantity. For this fixed four-point support, a further independent linear constraint can remove its remaining freedom; that does not establish a general three-channel solution for arbitrary distributions.

The observation branch is closed. No adjacent example, new grid, timing simulation or access rescue follows automatically. The public workbook's schema remains unknown after its [local permission failure](STAR_WORKBOOK_SCHEMA_FINDINGS.md). No empirical lag, scission, force or molecular-mechanism result was obtained.
