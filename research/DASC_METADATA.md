# DASC metadata access audit

**Scope and status (2026-09-22).** This is a bounded metadata-only audit of
Wang *et al.*'s DASC deposit.  It did not download, decompress, or inspect a
movie/archive, and it did not run cmeAnalysis.  The two deposited sidecars were
retrieved locally (31,574 bytes together); public Figshare metadata was used to
enumerate names and sizes.

## Verified locators and deposited sidecars

* Dataset: Wang X. *et al.*, *Live-cell imaging data for DASC (disassembly
  asymmetry score classification) analysis of clathrin-mediated endocytosis*,
  NIH Figshare article **12198225**, DOI
  [10.35092/yhjc.12198225.v1](https://doi.org/10.35092/yhjc.12198225.v1).
  Public metadata endpoint:
  `https://api.figshare.com/v2/articles/12198225`.
* Primary paper: Wang X. *et al.* (2020), eLife 9:e53686, DOI
  [10.7554/eLife.53686](https://doi.org/10.7554/eLife.53686).
* Manifest: 469 files, 223,348,360,171 bytes total (about 208.0 GiB).  Of
  these, 466 are compressed image sequences (`.tif.bz2`); there is no deposited
  track table, DASC class table, or other ready-to-analyse trace file.
* Small sidecars, retained in
  [`research/metadata/dasc-metadata-001`](metadata/dasc-metadata-001):
  `Readme.docx` (Figshare file ID **22438982**, **20,054 bytes**),
  `metadata.xlsx` (ID **22438985**, **11,520 bytes**), and `Decompression.m`
  (ID **22439129**, **1,944 bytes**, not downloaded).  Their direct public
  locators are `https://ndownloader.figshare.com/files/<file-ID>`.

The README says that the filename descriptors separated by `#` are experiment,
condition, date, cell name, and optional channel; decompression reorganizes on
those fields.  That makes filenames a usable **movie-level** condition/cell
map.  It does not create a biological-replicate or per-pit correspondence map.

## What is now mapped

All movies use the HPV-RPE/ARPE-19 system described in the README.  The
single-channel EAP and alphaPIP2 experiments use eGFP-CLCa/TIRFM.  `CLC_AP2_dual`
uses eGFP-alpha-AP2 plus mRuby2-CLCa/TIRFM.  `EpiTIRF` uses eGFP-CLCa and
TIRFM+EPI.  The README and paper both specify **1 frame/s**; each decompressed
TIFF contains **451 frames** (therefore 450 inter-frame intervals from first to
last frame).  EPI/TIRF acquisitions are described as nearly simultaneous 488-nm
EPI and TIRF channels.

| Experiment | Metadata-defined condition/intervention | Raw sequences in manifest | Movie/cell map that is safe to use |
| --- | --- | ---: | --- |
| `EAP_KD` | `siControl`; siCALM, siEPS15, siEPS15R, siEpsin1, siFCHO1, siFCHO2, siITSN1, siITSN2, siNECAP1, siNECAP2, siSNX9 | control 132; each knockdown 17–24 (siCALM 19) | One sequence per filename/cell label.  Conditions carry acquisition dates; controls span 2017-12-09, 2017-12-17, 2018-01-21, 2018-01-22, 2018-02-17, and 2019-04-13, so comparisons must be date-matched rather than pool every control. |
| `alphaPIP2-` | alpha-PIP2 siRNA plus AP2-alpha WT overexpression vs PIP2- (K57E/Y58E) overexpression | 19 WT; 20 PIP2- | One eGFP-CLCa sequence per labeled cell, all dated 2019-06-02. |
| `CLC_AP2_dual` | control/no treatment | 24 | 12 cell labels dated 2019-01-21; each has paired `ap2` and `clc` filename suffixes. |
| `EpiTIRF` | control/no treatment | 32 | 16 cell labels dated 2019-04-15; each has two filename suffixes, `TIRF` and `WT`.  The metadata establishes EPI+TIRF acquisition, but does **not** define what the literal `WT` suffix denotes; retain the label until verified from pixels or acquisition metadata. |

Representative exact raw members (not downloaded):

* `#EAP_KD#siCALM#190413#Cell1_1s#Cell1_1s.tif.bz2` — Figshare file
  **22428066**, **454,687,570 bytes**.
* `#EAP_KD#siControl#171209#Cell1_00_1s#Cell1_00_1s.tif.bz2` — file
  **22428138**, **391,662,563 bytes**.
* `#alphaPIP2-#alphaPIP2_WT#190602#Cell1_00_1s#Cell1_00_1s.tif.bz2` — file
  **22427892**, **436,220,738 bytes**.
* `#CLC_AP2_dual#Control#190121#Cell1_1s#ap2#ap2.tif.bz2` — file
  **22427964**, **711,307,988 bytes**; its same-cell `clc` mate is
  `#CLC_AP2_dual#Control#190121#Cell1_1s#clc#clc.tif.bz2`, file **22427967**,
  **719,034,124 bytes**.
* `#EpiTIRF#Control#190415#Cell1_1s#TIRF#TIRF.tif.bz2` — file **22430070**,
  **289,299,722 bytes**; paired literal-`WT` member
  `#EpiTIRF#Control#190415#Cell1_1s#WT#WT.tif.bz2` — file **22430082**,
  **312,146,265 bytes**.

The intervention protocol is specific enough for a bounded EAP comparison:
two siRNA transfections 24–48 h apart, with measurement on day 5 after plating;
control siRNA was transfected in parallel and the README reports >80% knockdown
efficiency by Western blot.  It does **not** establish that all date/cell
movies are independent biological replicates, nor does it provide a cell-level
batch/plate map beyond date and filename.

## Measurement boundary

The DASC paper defines DASC from fluorescence intensity dynamics and uses it to
separate its algorithmic AC/CCP populations.  Treat that as a **classifier
output**, not physical scission ground truth.  It provides no deposited
fission-event labels.  The paper's EPI:TIRF ratio is an **EPI/TIRF-derived
invagination-depth proxy** based on distinct excitation depths; the paper
reports a normalized depth `Delta z/h`, rather than direct physical scission
labels.  The exact primary-paper locator is [Results: “Validation through
curvature acquisition and CCP stabilization”](https://elifesciences.org/articles/53686),
Figure 3F and Figure 3—figure supplement 3A; its [Materials and methods:
“Microscopy imaging and quantification”](https://elifesciences.org/articles/53686)
states the near-simultaneous EPI/TIRF acquisition.  This audit did not
independently verify a calibration curve or parameters that convert this proxy
into an absolute curvature measurement, so it must not be called a calibrated
curvature measurement.  The peer-review record also says the authors revised
that analysis to reduce intensity-fluctuation distortion.  No curvature
conclusion can be made from ordinary single-channel TIRF movies, and no current
source creates a one-pit join to the static geometry collection.

## One next-data/value decision

**Do not select DASC as the next bounded dynamic-vs-static comparison source.**
It is now well described enough to be valuable for a future, date-matched
EAP-dynamics reanalysis, but it has no small processed traces and no per-pit
geometry correspondence; the minimum usable input is a large raw movie plus
new tracking.  If that future analysis is explicitly prioritized, start with
only the 2019-04-13 `EAP_KD` siCALM and date-matched `siControl` movies and
first verify the control-file count and tracker output schema.  Do not infer
scission or morphology ground truth from the DASC class labels.

## Lead disposition and next design decision

The lead independently reproduced the manifest's 469 files, 466 compressed
movies and total size, verified both sidecars against both published MD5 fields,
and inspected the README and workbook text. Same-date candidate contrasts are:

| Contrast | Acquisition date | Deposited movie files | Total compressed bytes |
| --- | --- | ---: | ---: |
| siCALM / siControl | 2019-04-13 | 19 / 20 | 9,879,417,666 / 10,856,172,713 |
| AP2-alpha WT / PIP2-binding mutant | 2019-06-02 | 19 / 20 | 9,040,952,265 / 10,238,817,152 |

These are file counts, not verified independent biological replicate counts.
No subset was downloaded. The primary article returned HTTP 403 to the lead's
web reader; the source specialist's method/proxy summary remains source-level
input to verify from accessible primary full text before a comparison protocol.

Accept the source specialist's access and measurement boundaries and its
recommendation against an immediate static-versus-dynamic geometry comparison.
Do not interpret the absent same-pit static join as disqualifying DASC from all
mechanistic work: a separate, well-defined perturbation prediction may be testable
without that join. This changes the next step from archive discovery to designing
one informative contrast and assessing its data/analysis cost. No movie download
or tracking implementation is justified merely by finding these conditions.
