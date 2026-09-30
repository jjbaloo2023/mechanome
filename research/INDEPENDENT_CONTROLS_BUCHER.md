# Bucher et al. 2018: independent-controls eligibility

**Study:** Bucher *et al.*, “Clathrin-adaptor ratio and membrane tension regulate the flat-to-curved transition of the clathrin coat during endocytosis,” *Nature Communications* 9, 1109 (2018), DOI [10.1038/s41467-018-03533-0](https://doi.org/10.1038/s41467-018-03533-0). Scope is this primary paper and its linked public record only.

## Source-derived factual summary (157 words)

BSC-1 clathrin-coated structures were examined by metal-replica TEM, correlative light/electron microscopy (CLEM), and live fluorescence imaging. TEM supplied projected areas and visual flat/dome/pit labels; CLEM associated integrated fluorescence intensities with such EM structures; live AP2-eGFP and CLCa-tdtomato tracks were collected at 3-s frames. The authors mapped fluorescence to surface-area estimates and fitted growth laws to infer morphology distributions and transition timing. Hypotonic medium (one part medium to one part water) was used as an intervention described as increasing plasma-membrane tension; it lengthened/stalled events and changed morphology frequencies. The paper’s imaging registration uses three manually selected structures to transform FM to EM. It reports public EM/CLEM/FM data at Figshare DOI 10.6084/m9.figshare.5802903; verified local Figshare metadata (6,615 B) lists seven spreadsheet files totaling 7,575,710 B under CC BY 4.0; payloads were not inspected. The article carries CC BY 4.0; the linked 949-kB supplementary PDF has no separately inspected license statement. Source locators: Results/Figs. 1–7; Methods “Live-cell microscopy,” “Osmotic shock experiments,” “Transformation of images for CLEM,” “TEM and CLEM analysis,” and Data availability.

## Eligibility audit

| Requirement | Evidence / locator | Decision |
|---|---|---|
| Observed geometry, scale, pose, units | TEM resolves projected area and categorical morphology, not a registered membrane height profile. TEM montages: 1.82 nm/pixel (Methods “TEM of metal replica”). FM↔EM is a manual transform using 3 landmarks (Methods “Transformation of images for CLEM”). Live intensity movies: 3-s frames (Methods “Live-cell microscopy”). | **Partial observation only.** No complete membrane profile, height reference/pose covariance, or stated uncertainty model for derivatives. |
| Measured vs inferred | Measured: TEM projected areas / labels; integrated fluorescence; tracks. Inferred: surface-area conversion, contact angle/tip curvature, morphology distributions and transition time via fitted growth models (Results around Figs. 3, 5; Methods “Mathematical growth laws”). | **Does not provide source fields.** Fluorescent coat/adaptor intensity is not calibrated preferred-curvature distribution. |
| Tension / rigidity / traction calibration | Hypotonic treatment is described as increasing PM tension (Results “Membrane tension…”, Fig. 6; Methods “Osmotic shock experiments”), but no force/tension value or independent calibration is reported in inspected text. No membrane rigidity measurement, traction measurement, load map, direction, or balancing reaction geometry reported. | **Fails.** |
| Independent perturbation preserving sources | Hypotonic shock changes event lifetime, AP2/CLC timing and morphology (Figs. 6–7), but these observables can change from tension alone. The broad cellular/osmotic perturbation supplies no test establishing invariant curvature and traction fields. | **Invariance not established.** |
| Spatial reaction / force balance | No measured spatial traction or reaction field. No net-force/boundary contract for a load inversion appears. | **Fails.** |
| Data contract | Article says EM/CLEM/FM datasets are at Figshare DOI (Data availability). Verified Figshare metadata (6,615 B) resolves seven spreadsheet files under CC BY 4.0. The two EM workbooks are normal `EM BSC-1.xlsx` (78,130 B; ID 10256781; MD5 `ce61ee0d469a291ddcfa193310119905`) and shock `EM BSC-1 osmotic shock.xlsx` (72,748 B; ID 10256790; MD5 `529bbaa8d3cfafc95821a4ea2e354708`). Payloads were uninspected at this source-audit stage. Code is request-only (Code availability). | **Metadata contract resolved; profile/mechanical suitability unestablished without payload inspection.** |

## Assessment and decision

This paper supports a narrower, descriptive population comparison of unperturbed and hypotonic morphology, alongside AP2/CLC timing under a stated osmotic intervention. The live time series contains a same-cell before/after segment; destructive EM normal/shock preparations have no established pairing. It cannot separate coat curvature from balanced membrane load in the full-membrane framework. Its key geometric quantities are snapshots/classes or model-derived summaries, the tension intervention lacks a reported independent calibration, rigidity is not varied/calibrated, and neither traction nor balancing reaction is mapped. Observed changes in shape, timing, or morphology do not themselves establish that the curvature and traction source fields changed: a tension change alone can alter those observables. Source invariance is therefore **not established**, rather than disproved, and the required same-source comparison cannot be claimed.

**Stopped empirical branch for this study.** A prospective qualifying cellular experiment would need registered 3-D membrane profiles with image-scale/pose/noise calibration, independently calibrated distinct rigidities (or a spatial traction measurement with its reaction), known tension, and tests that coat-curvature and traction fields remain unchanged across conditions. It must publish condition/replicate maps and small derivative-ready profile/calibration files. Scalar areas, intensity tags, fitted caps, or known net force alone would not close the ambiguity.

## Exact public records

- Article: https://www.nature.com/articles/s41467-018-03533-0
  - Fig. 1 and Results “EM analyses…”: TEM projected areas and flat/dome/pit distributions.
  - Fig. 2 and Results “Clathrin lattice bends…”: CLEM correlation of intensity, area and class.
  - Fig. 3 / Fig. 5: fitted individual intensity tracks used for model-derived distributions.
  - Fig. 6–7 and Methods “Osmotic shock experiments”: intervention and outcomes.
  - Methods “Live-cell microscopy,” “TEM of metal replica,” “Transformation…,” “TEM and CLEM analysis,” “Mathematical growth laws”; “Code availability” and “Data availability.”
- Dataset record: https://doi.org/10.6084/m9.figshare.5802903.v1 (verified local 6,615-B Figshare metadata lists seven spreadsheets totaling 7,575,710 B, including normal EM 78,130 B and shock EM 72,748 B; CC BY 4.0; payloads uninspected).
- Supplementary Information: linked by article as PDF, 949 kB; not retrieved because the primary HTML methods and public metadata decided eligibility.
