# Yeast joint-observables screen

## Candidate and access

The single candidate is Manenschijn et al., *Type-I myosins promote actin polymerization
to drive membrane bending in endocytosis*, eLife (2019), e44215, DOI
[10.7554/eLife.44215](https://doi.org/10.7554/eLife.44215), in *S.
cerevisiae*. The indexed primary record says the authors used MYO3/MYO5
deletion/duplication backgrounds, measured myosin recruitment and Sla1 inward
movement, and report a dose-dependent myosin contribution to invagination
(Fig. 3, “Myo3 and Myo5 contribute to invagination in a dose-dependent way”).

This is a yeast-specific recruitment/motion perturbation, but no same-event
processed-data contract was verified. The indexed record does not establish
whether myosin amount and Sla1 trajectories are paired event-by-event rather
than summarized by genotype. It also omits event selection, replicate hierarchy,
and uncertainty for the joint relationship. Sla1 inward motion is an
invagination proxy, not direct vesicle completion or a mammalian force/tension
readout.

## Perturbation and controls

The intervention is myosin-I gene dosage in haploid/diploid backgrounds. The
indexed result states recruitment generally followed dosage and compares Sla1
dynamics in WT, myo3 deletion, and myo5 deletion contexts. It does not report a calibrated
load or membrane-tension manipulation. The source identifies myosin recruitment
plus Sla1 motion, which is the required myosin-or-actin/motion combination.
The unresolved requirement is whether those measurements are paired on the
same tracked events, with event IDs and a usable schema.

## Public processed-data listing and contract gap

Lead's indexed primary eLife figures check verifies three main source files:
`elife-44215-fig1-data1-v1.csv` (Fig. 1 trajectories; DOI
10.7554/eLife.44215.003), `elife-44215-fig2-data1-v1.csv` (assembly rates,
centroid speeds, and peak numbers; DOI 10.7554/eLife.44215.006), and
`elife-44215-fig3-data1-v1.csv` (average trajectories for Fig. 3C/E/F; DOI
10.7554/eLife.44215.012). It also lists `elife-44215-supp1-v1.docx`, with
tables including Sla1 centroid speeds by genotype, myosin molecule numbers, and
trajectory counts. The earlier indexed result also names smaller Fig. 3
supplemental Abp1-lifetime and median-molecule files.

The same lead primary listing additionally names Fig. 6, “Actin content and
Sla1 dynamics in myo5 deletion bbc1 deletion double deletion,” with
`elife-44215-fig6-data1-v1.csv` (Fig. 6B average trajectories; DOI
10.7554/eLife.44215.019) and `elife-44215-fig6-data2-v1.csv` (median Act1
molecules for Fig. 6A; DOI 10.7554/eLife.44215.020). This is a second,
genotype-level aggregate contrast candidate only; its schema, units, control
ancestry, and causal interpretation were not retrieved or verified.

These verified public listings provide a narrower aggregate-genotype candidate:
Sla1 centroid speed versus myosin dosage/recruitment across backgrounds. They do
not verify a same-event table: no body, schema, row-level event ID, channel
pairing, selection rule, or replicate linkage was retrieved.

The eLife article page returned a JavaScript challenge and its figures endpoint
returned HTTP 403. No dataset landing, CSV body, archive member list, or schema
was retrieved. Publisher source-data listings are verified, but actual body
access/schema and any richer same-event record remain unresolved. This is an
access/contract gap, not evidence the joint data are absent.

## Bounded ledger and decision

The three worker queries were used: `yeast endocytosis actin myosin
recruitment inward movement processed data repository`; `site:pmc.ncbi.nlm.nih.gov
yeast endocytosis Myo5 actin inward movement data availability`; and
`site:figshare.com yeast endocytosis actin myosin tracking dataset`. One primary
candidate was selected. The lead made one additional narrow author/title
verification query after the worker cap, exceeding the registered three-query
cap; the disclosed total is four queries. No further acquisition followed; no
local download, archive/movie access, author code, or model was used.

Stop at this exact gap. A separately registered metadata check would need to
verify schemas, units, genotype/control ancestry, and replicate/selection
metadata before an aggregate comparison; same-event event IDs and channel
pairing would additionally be needed for a joint event-level analysis.
