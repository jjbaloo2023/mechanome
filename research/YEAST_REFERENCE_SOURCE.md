# Yeast Figure 6 reference-methods source note

## Primary evidence and access ledger

Primary: Manenschijn et al. (2019), eLife e44215. The sole team search query
was `site:elifesciences.org/articles/44215 "initial position is y = 0" Sla1
Figure 6`. Its indexed primary PDF result supplies the Figure 3C locator:
average Sla1-EGFP centroid inward movement curves are plotted with their
initial position at `y = 0`, time-aligned to the onset of inward movement, and
shown with 95% confidence intervals; it identifies one of two independent
replicates for each genotype and states WT/myo5 deletion trajectories are
reused from Figure 1. The same indexed result identifies the Figure 3 source
data DOI `.012`.

Three `find` probes against that parsed PDF result for Figure 6 text and the
methods heading returned no match. At 2026-09-29T14:03Z the two permitted
primary opens were used: `https://elifesciences.org/articles/44215.pdf` and
`https://elifesciences.org/articles/44215/figures`; both returned HTTP 403.
No body/data file was downloaded; parsed-search/find/open access has no raw-byte
telemetry. This exhausts the one-query/two-open and zero-download caps.

## What is established

For the **Figure 3 Sla1 curves**, the primary caption establishes a positional
baseline (initial plotted position = 0) and an inward-motion time alignment.
The retrieved wording does not separately define the sign/direction of its
plotted position coordinate. It also shows the curve is an average trajectory,
rather than an individual-event trace; the one-of-two-replicates statement does
not turn its time rows into independent biological replicates.

This method-level definition is compatible with a positional reference for a
Sla1 curve whose construction is explicitly stated to follow it. It does not
by itself identify the CSV field-name mapping (`x` in the Figure 6 file versus
`y` in the Figure 3 caption), the reference used for each Figure 6 genotype,
the Figure 6 averaging/alignment procedure, or the stored Figure 6 subset.
It also does not state whether temporal registration is a physical-seconds
additive offset or uses time scaling/warping. A transit duration cancels only
the former, so the latter must not be assumed away.

The Figure 3 caption says its WT/myo5-deletion trajectories are reused from
Figure 1. That is a Figure 3-specific reuse statement and is not transferred to
Figure 6; the Figure 6 reuse history must rest on its separately indexed caption.

## Figure 6 decision

The required explicit bridge to **Figure 6B** was not recovered: neither the
primary Figure 6 caption/method text nor a statement that the Figure 6 curves
use the Figure 3 initial-position and onset-of-inward-motion transform was
retrieved in this bounded pass; the two direct primary endpoints were 403, which
is an access gap rather than proof such a statement is absent. The previously observed Figure 6 CSV anomaly
(bbc1 time starts positive while other blocks include negative values) remains
a stored-time-axis issue, distinct from the Figure 3 method definition.

Therefore a fixed 40--80 nm interval cannot yet be called a comparable
stored-curve descriptor across all four Figure 6 blocks. A constant time shift
would cancel from such a duration, but an unverified vertical reference would
change which physical movement interval 40--80 nm selects; time warping would
also alter duration. If a later source establishes a common spatial
baseline/direction and physical-seconds alignment, the result would still be a
stored-mean descriptor despite changing `n`, not an event-level estimate. The
source supports no numerical contrast, speed estimate, scission claim, force
inference, or within-event actin/motion covariance.

The exact stop condition is reached: Figure 3 provides a reference method, but
the Figure 6-specific applicability and stored-coordinate mapping remain
unverified. No further access or rescue is authorized by this task.
