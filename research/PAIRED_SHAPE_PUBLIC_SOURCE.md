# Paired shape/public source screen — `paired-shape-public-screen-001`

## Ledger

Times UTC, 2026-09-29; no files, source-data workbook, movies, raw images, code, or author contact were used.

| Time | Call | Exact target | Outcome |
|---|---|---|---|
| 17:32 | Search 1/2 | `clathrin coated pit membrane orientation polarization TIRF time series public dataset` | Returned only excluded Scott 2018 as the direct pol-TIRF record, plus an unrelated image-dataset listing. |
| 17:32 | Search 2/2 | `clathrin coat curvature dynamics fluorescence membrane shape single event data repository` | Located the new Nawara et al. primary record. |
| 17:32 | Primary open 1/2 | https://www.nature.com/articles/s41467-022-29317-1 | Parsed primary available; recovered method, eligibility, grouping, and publisher Source Data listing. |
| 17:32:54 | Primary open 2/2 | same URL, requested at page line 500 | Recovered the publisher’s public `Source Data (download XLSX)` listing (lines 448–450) and article CC BY 4.0 notice (lines 451–454). |

No further search or page access occurred. This is one bounded screen, not a universal absence claim.

## One new candidate: useful but does not yet satisfy the strict object contract

**Nawara et al., “Imaging vesicle formation dynamics supports the flexible model of clathrin-mediated endocytosis,” Nature Communications 13, 1732 (2022), DOI 10.1038/s41467-022-29317-1.** This is distinct from all listed exclusions. The article has a publisher-listed public **Source Data XLSX** at the exact primary page’s Source Data entry; no workbook body, sheet name, schema, event IDs, or raw-track contents were inspected. Thus this is a verified public listing, not a verified reusable paired-track object. The page is CC BY 4.0, but file-specific licence/third-party status was not checked.

In Cos-7 cells, CLCa is dual-tagged iRFP713-EGFP. Simultaneous 488/647 TIRF acquisition produces each individual track’s two intensity signals and a ratio-derived Δz (lines 88–94, 100–105). The authors calibrate the ratio against dual-labelled microspheres for axial position (lines 98–99), then state that, for dual-tagged clathrin in CME, the clathrin **z-distribution indirectly reports** plasma-membrane shape/curvature (lines 90–93). This is not an independent membrane-orientation channel or direct membrane morphology measurement: it is a clathrin-derived axial proxy, with a membrane-shape interpretation conditional on the stated biological/optical model. It therefore does not fully meet the requested independent shape-plus-coat signal object.

## Pairing, registration, selection, and grouping

The two fluorophores are acquired simultaneously, avoiding fast dynamics between channels (line 91). Δz at each time is normalized to the mean of the first ten frames (line 103). Individual puncta are detected from EGFP; curvature-positive tracks cross a Δz threshold of two background SD, and flat tracks do not (lines 104–105). For timing, both CLCa and Δz must exceed threshold for five consecutive images; the beginning-time difference defines the reported classes (lines 127–130). This registration/threshold rule is explicit, but does not substitute for deposited per-event values.

The main cohort began with 1,948 de novo tracks from 13 cells/five independent repeats; pre-existing and >100-s tracks were excluded (lines 107–110). Fig. 2 panels use smaller filtered event totals (e.g., 1,225 curved and 328 flat from 11 cells/three repeats; lines 116–119). These nested event/cell/repeat counts require grouping by cell and experiment in any reuse; events are not independent replicates. Existing primary text does not establish a file-level map of those filters, cells, or repeats in the XLSX.

## Stop gap

The verified XLSX listing makes this a concrete public-access candidate, but its uninspected schema leaves open whether it contains summaries only or event-level paired time series. More fundamentally, STAR’s Δz is derived from the same dual-tagged clathrin probe, not an independently labelled membrane orientation/shape measurement. A future separately registered, small workbook-schema check could decide table reuse; it cannot convert the proxy into independent membrane-shape readout without additional validation.
