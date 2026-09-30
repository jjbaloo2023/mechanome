# Endpoint public source screen — `endpoint-public-source-001`

## Call ledger

All times are UTC, 2026-09-29. No local bodies, archives, movies, data files, or author code were downloaded or executed.

| Time | Call | Target | Outcome |
|---|---|---|---|
| 15:39 | search 1/2 | `clathrin fluorescence tracks pH pulse extracellular accessibility same event scission assay dataset` | Located the candidate primary record/PMC page. |
| 15:39 | search 2/2 | `clathrin mediated endocytosis pulsed pH assay track sealing internalization fluorescence public data` | Confirmed indexed description of the alternating-external-pH assay. |
| 15:40:13 | source primary open 1/2 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3245319/ | Parsed primary available (432 lines); Figure 3/Results and Methods locators recovered. |
| 15:40–15:42 | lead primary open 1/1 | same PMC primary | Lead independently verified title/authors and the 90/10/80 Figure 3 accounting. |

No further calls were made. Initial internal attribution was corrected after the lead’s primary-page check: the paper is **Mattheyses, Atkinson, and Simon (2011), “Imaging single endocytic events reveals diversity in clathrin, dynamin, and vesicle dynamics,” Traffic, PMC3245319.**

## Candidate result and public-data gap

This paper has the desired paper-level same-event design. Cos7 cells co-express **TfR-pHluorin and clathrin-dsRed**; Figure 3 pairs their fluorescence at individual co-localized puncta (Results “Vesicle Scission,” primary lines 162–180; Fig. 3 caption, lines 172–173). External medium alternates pH 5.5/8.0. Loss of TfR-pHluorin responsiveness marks a vesicle lumen becoming inaccessible to extracellular protons, whereas clathrin fluorescence decline is separately timed. The authors explicitly show that clathrin decline does not mark that endpoint reliably (lines 176–180).

The endpoint is a **sealing/accessibility proxy**, not proof of full topological scission: the authors say pH insensitivity can be hemi-scission (lines 166, 225). Sealing at low external pH is structurally undetectable (line 167), so pH phase/acidification is not scission. Of 90 selected co-localized assay-positive puncta, 10 later regained pH sensitivity and were excluded, leaving 80 for Figure 3. Of those retained events, reported timing categories are 22.5% clathrin-decline initiation within 5 s of sealing, 50% delayed, and 27.5% still unresolved at movie end (lines 168, 176–179). These are initiation/censoring categories, not automated track termination, complete disappearance, PPV, or NPV. Selection on visible co-localization and detectable high-pH sealing precludes all-pit sensitivity/recall; no cell/movie/preparation clustering was recovered.

No public per-event table, movie identity, repository accession, named file, or explicit author-request term was verified in the bounded primary inspect. That is a specific public-reanalysis access gap, not a global absence claim. A future registered access check would need a verified object with event IDs, clathrin traces, pH phase/sealing time, exclusions, and movie/cell grouping; Figure 3 percentages alone are not analyzable data.
