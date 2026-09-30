# Myo1E repository contract — one bounded API recovery

**Disposition:** the named public repository contains an actual small
three-color Myo1E osmotic-shock track table, but the bounded files do not
document the Fig. 4C Myo1E-positive/negative denominator or pre/post pairing.
This is enough to establish a concrete deposited-table candidate, not enough to
compute the claimed ratio or infer independent replicate units.

## Pinned availability

The direct GitHub API recovery, prompted by the prior browser cache miss, pinned
the current default-branch response to commit
`aa43f751b03378783b3226a719b64773bff8e91a` (committer date 2025-11-12) and
tree `2c7f823b1cad4d458fd383877b7ed841e220e655`. This is a repository revision,
not proven paper-version provenance. Its recursive tree was untruncated and had
14 entries. It lists an oversized 25,773,834-byte notebook (not retrieved) and
several CSVs; the relevant retained file is
`three_color_tracking_myosin1e_osmotic_shock.csv`, Git blob
`51fecfa7b3460ce6be63167389d41170733bf363`, size 226,600 bytes.

The raw file is saved in
`metadata/myo1e-repository-001/03-three_color_tracking_myosin1e_osmotic_shock.csv`.
The accompanying [request ledger](metadata/myo1e-repository-001/REQUEST_LEDGER.md)
records all three HTTP-200 requests, UTC response times, body sizes, SHA-256
hashes, and 236,777 cumulative bytes of the 1 MiB cap.

## Verified table schema

The CSV has 1,709 data rows. Its columns are:

`lifetime`, `max_ch1`, `max_ch2`, `max_ch3`, `ch1_lifetime`, `ch2_lifetime`,
`ch3_lifetime`, `ch1_dist`, `ch2_dist`, `ch3_dist`, `md_ch1`, `md_ch2`,
`md_ch3`, `track_category`, `condition`, `replicate`, and `cell_id`.

It contains condition codes 0--4 (row counts 560, 187, 150, 323, 489), replicate
codes 1--3 (634, 569, 506 rows), track categories 1 and 4 (686, 1,023 rows),
and nonempty `cell_id` values. These fields can support a future nested
movie/cell/condition analysis **only after** their codebook and relationship to
the Fig. 4 labels are verified. `cell_id` values such as `0-1` and `1-Jan` are
identifiers, not evidence of pre/post pairing, movie identity, well identity,
or biological independence. Their raw pattern also shows an apparent
spreadsheet date-coercion ambiguity: condition 1 includes `1-1` and
`1-Jan` through `6-Jan`, while conditions 2--4 contain analogous `1-Feb`...
`6-Feb`, `1-Mar`...`6-Mar`, and `1-Apr`...`6-Apr` strings. Thus these labels
cannot safely be counted as 49 independent cells/movies or used to reconstruct
pre/post linkage without the original identifier/codebook.

This is a key-integrity gap, not an automatic repair rule: the date-like labels
suggest coercion but do not prove it, so `1-1` and `1-Jan` must not be merged.
The table has no blank cells and no exact duplicate full rows, but neither fact
establishes group identity, a one-to-one match, or pair metadata.

The table is consistent with a three-channel tracking output relevant to the
paper's AP2/Dnm2/Myo1E observation process, but this file alone does not label
which channel is Myo1E, define the positivity threshold, identify the Fig. 4C
numerator/denominator, or map condition codes to 300/225/150/75 mOsm. It also
does not establish whether `track_category` encodes active/persistent status.
Accordingly it must not be used to silently substitute a fraction for the
published positive-to-negative ratio, create unverified pre/post pairs, or turn
fluorescence values into force or tension.

## Bounded decision

The specific availability gap is now narrower: a deposited, small track-level
CSV exists, but its required codebook/denominator/pairing contract is not in
the retrieved material. The only apparent analysis notebook in the pinned tree
exceeds the full retrieval budget, and no range workaround was attempted. This
candidate's acquisition closes here under the registered stop condition; there
is no automatic follow-up retrieval or analysis.
