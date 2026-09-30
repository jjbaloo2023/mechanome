# Yeast Figure 6: real aggregate data, with a comparison limit

The two public source tables from **Manenschijn et al. (2019), eLife 44215**
are retrieved and verified. They provide four reported Act1 medians and four
average Sla1 centroid curves. We accept a partial genotype-level observation
contract; we have not established a new biological result or computed a motion
contrast. The [independent review](YEAST_FIGURE6_REVIEW.md) sets the boundary.

## What the deposited numbers contain

The [Figure 6A source table](https://doi.org/10.7554/eLife.44215.020)
reports the following Act1 molecule counts. Values below are source aggregates,
rounded to three decimals, with the source's SEM column; the table does not
identify the independent sampling unit used for that SEM.

| Genotype | Reported median Act1 molecules | Reported SEM |
| --- | ---: | ---: |
| WT | 2145.556 | 336.705 |
| myo5 deletion | 1305.556 | 210.272 |
| bbc1 deletion | 5122.222 | 795.335 |
| myo5 + bbc1 deletion | 2244.444 | 358.666 |

The [Figure 6B source table](https://doi.org/10.7554/eLife.44215.019)
contains 1,106 time rows across four genotype blocks. All time and position
values are finite and time increases strictly within each block. The `n`
column changes along each curve; its ranges are WT 9-37, myo5 11-28,
bbc1 3-22 and double deletion 7-21. There are no zero-n rows. These time rows
are correlated samples of average curves, not independent biological replicates.
[Exact schema checks](yeast_figure6_table_checks.json) preserve the ranges.

The double-deletion labels have opposite gene order in the two tables. A
common genotype key is possible, but it does not establish common events,
cells, cultures or matched strain ancestry across the readouts. The primary
[Figure 6 caption](https://elifesciences.org/articles/44215/figures) says WT and
myo5 controls reuse Figure 1 for Act1 and Figure 2 for Sla1. This is not fresh
replication of either readout.

## Why we have not calculated a motion effect

The stored bbc1 time axis begins at +15.4215 s, whereas the other three begin
at negative times. The caption describes the plotted inward phase, but neither
the full stored subset nor its time origin is established by these CSVs.
Same-time comparisons would therefore be unjustified. The common positional
reference for `x` also needs to be established. The exact interpretation of
`x_err`, averaging, changing cohort size and independent uncertainty is missing.

We considered a first-upward 40-to-80 nm transit on the stored mean curves,
with fixed 30-to-70 and 50-to-90 nm sensitivity windows. **It was not executed.**
The reviewer identified that constant time shifts cancel in such a duration,
but vertical position shifts do not. Without a verified common position
reference, that descriptor could compare different movement intervals. Even
with that reference it would not be the mean individual-event speed, published
speed reproduction, scission, calibrated force or a causal rescue test.

## Disposition and next decision

Acquisition stops after exactly two CSV bodies: 39,979 bytes, two successful
HTTP responses, and two team-wide primary queries within the registered cap.
No author code, numerical solver, genotype test or extra data file was used.
[Source contract](YEAST_FIGURE6_SOURCE.md), [request ledger](metadata/yeast-figure6-001/REQUEST_LEDGER.md)
and [registration](yeast_figure6_contract_design.json) retain provenance.

The lead and reviewer caught and corrected a false zero-n statement. The lead
also removed unqualified inward-phase wording after the source worker completed.
Those corrections precede the [frozen manifest](yeast_figure6_contract_manifest.json).

One targeted primary-methods decision is queued: establish the Figure 6 spatial
reference and trajectory alignment from the named article, or close the
cross-readout motion comparison if those definitions remain unavailable. No
broader dataset search or repeated file download is needed. A usable definition
would permit a separately registered descriptive calculation, not a new
mechanistic inference. [NEXT_CYCLE.md](NEXT_CYCLE.md) supplies the exact bounds.
