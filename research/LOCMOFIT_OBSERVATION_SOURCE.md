# LocMoFit observation-source ledger

**Task:** `locmofit-source-001` attempt 1  
**UTC checked:** 2026-09-25T03:48:42Z  
**Scope:** primary method and public official implementation documentation only; no raw microscopy or refitting.

## Checked source-to-observable contract

Mund et al. (2023), Methods, “Quantitative geometric analysis of
clathrin-coated structures,” is the primary source for the deposited
per-site geometry. It says that manually curated, isolated sites were
analysed by LocMoFit as a maximum-likelihood fit of localization coordinates
to the PDF of a parameterized *hollow spherical cap*. The intrinsic
parameters are surface area `A` and closing angle `theta`; the model also
fits centre position and orientation, and applies an extra uncertainty and a
background weight to the PDF. The cap is represented by spiral or spherical
Fibonacci surface points that are treated as discrete fluorophore coordinates
when the PDF is built. Thus the relevant fitted support is the entire
segmented, manually retained structure—not a declared circular radial window.

Radius and curvature are derived quantities, not independently fitted
responses: `r = sqrt(A / (2*pi*(1-cos(theta))))` and `H = 1/r`. Consequently
the published `H`, `A`, and `theta` share the same fit and should not enter a
comparison as independent observations. `theta=0.0001 degree` is a
downstream growth-model convention; it is not a replacement for a flat-cap
localization likelihood. For fits with slightly negative curvature, the
authors manually/explicitly set `H=0` and `theta=0`.

### What is identified

| Contract component | Checked evidence | Status for a reproducible likelihood |
| --- | --- | --- |
| Likelihood target | MLE of a model PDF against 3D localization coordinates | Identified at the framework level |
| Latent emitter/surface sampling | Discrete spiral or spherical-Fibonacci points approximating an even cap-surface distribution | Identified qualitatively; point count/realised grid settings absent |
| Geometry | hollow cap, fitted `A` and `theta`; position/orientation nuisance parameters; derived `r`, `H`, projected area, edge length | Identified |
| Blurring/error | LocMoFit PDF includes extra uncertainty; paper says it accounts for coat thickness, antibody size, and localization-precision blur | Per-site fitted/fixed values absent from deposited tables |
| Background | Background weight is applied to the PDF | Numerical value/ROI/background distribution absent |
| Data selection/support | Semiautomatic candidate detection followed by manual retention of single isolated sites; later curation removes upside-down, double/adjacent, plaque, and antibody-cluster cases | Exact ROIs/segmentation masks/point clouds absent |
| Localization inputs | x/y/z locs filtered at 0--20/0--30 nm precision; modal precisions 3.9/12.5 nm | Per-localization precisions and raw localizations absent from processed tables |
| Fit uncertainty | No parameter covariance, likelihood, residual, point count, nuisance estimate, or calibration table in the processed per-site outputs inspected by the repository audit | Absent |

## Implication for the deterministic vertical least-squares surrogate

It cannot be called LocMoFit, nor a calibrated approximation to LocMoFit. It
fits a height profile on a predeclared radial/support weighting, whereas the
primary pipeline maximizes a 3D point-cloud PDF over an empirically segmented
whole structure with discrete approximately uniform cap-surface model points,
localization precision, extra uncertainty, background weight, rigid pose, and
physical label/thickness blur. The surrogate may remain a deterministic
measurement-functional sensitivity check only. Mapping it to the actual
likelihood would require, at minimum, the raw retained localizations with
per-localization uncertainties, the segment/ROI support, exact model-point
construction/count, coat-thickness and linkage model, extra-uncertainty and
background settings, optimizer/bounds/initialization, and a code revision.

The processed `H(theta)` tables can support a descriptive vertical response
comparison if stated as such, but cannot support a LocMoFit likelihood,
parameter-covariance weighting, or an empirical test calibrated to the
fitting pipeline. Do not synthesize `H_sigma` from modal localization
precision: that does not propagate the joint nonlinear cap fit.

## Version/source provenance

* **Historical analysis:** Mund et al. name LocMoFit / Wu et al. (2023) and
  SMAP, but do not report a LocMoFit release, SMAP commit, model settings MAT
  file, model-point count, optimizer, or a source hash. Exact historical
  executable version is therefore **not pinned** by checked public sources.
* **Current public implementation (now pinned):** the official public
  [jries/SMAP](https://github.com/jries/SMAP/tree/master/LocMoFit) repository
  has `master` commit `d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6` as checked
  at 03:50:03Z. Relevant blob IDs are `f0baeaaadd6bef20c3ff51763384a3aed5283fd7`
  (`@LocMoFit/LocMoFit.m`),
  `a1f10bc1b44ce5ff90e7c9dbf01b591c4984f8b1` (`@functionModel/functionModel.m`),
  and `cc03dbd25b5d92c9894174d3d9ab417302af17ca`
  (`models/sphericalCap3D_surfaceArea.m`). Verified immutable raw locators:
  `https://raw.githubusercontent.com/jries/SMAP/d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6/LocMoFit/models/sphericalCap3D_surfaceArea.m`,
  `https://raw.githubusercontent.com/jries/SMAP/d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6/LocMoFit/%40LocMoFit/LocMoFit.m`, and
  `https://raw.githubusercontent.com/jries/SMAP/d066594d7a5e5d35f2dbf9402cf7cfcfe07679c6/LocMoFit/%40functionModel/functionModel.m`.
  The documentation labels itself
  LocMoFit **1.1.0**, while the checked fitter file's own header says 1.0.1
  (last update 2022-07-25); that mismatch is another reason not to infer the
  2023 analysis executable.

  In this current source, `sphericalCap3D_surfaceArea` is a **discretized**
  3D model. Its code constructs a Fibonacci sphere subset and uses a
  sampling count that depends on cap radius, `locsPrecFactor`, and the fitter
  `refPoint_spacing` (default 0.75 in sigma units). The generic fitter's
  objective is `sum(compensationFactor .* log(prob))`; its default solver is
  `fminsearchbnd`, although the historical solver/settings remain unknown.
  The current discrete-model path takes `locprecnm` and `locprecznm` per
  localization, whereas continuous models floor those values at their
  medians by default. Background can be parameterized as a weight or density
  (default setting: weight). These concrete defaults are current-code facts,
  not historical settings.

  A relevant rendering/formula issue is visible in this current blob:
  `getDerivedPars` computes `projectionArea = pi*radius^2` whenever
  `realCloseAngle > 0` (its alternative `pi*(radius*cos(-theta-90))^2`
  executes only at nonpositive angle). It therefore does **not** implement
  the physical silhouette `pi*r^2*sin(theta)^2` for positive shallow caps,
  followed by `pi*r^2` above 90 degrees. This is a current-code
  rendering/export distinction only: it does not explain a failed rim-disk
  check when deposited values obey the piecewise silhouette, and does not
  establish which function/revision generated the deposited values.

The paper's simulation section specifies a 5 nm linkage-error parameter,
`p_label=0.6`, reactivation probability 0.5, mean on-time 1.6 frames, and
photon/background/CRLB simulation inputs. These are simulation choices, not
per-site fitted settings recoverable from the processed table; they are not
claimed absent from the article.

## Source locators

1. Mund et al., JCB 2023, doi:10.1083/jcb.202206038, article Methods
   **Quantitative geometric analysis** and **Superresolution image
   reconstruction**: https://rupress.org/jcb/article/222/3/e202206038/213855/Clathrin-coats-partially-preassemble-and
2. Wu et al., *Nature Methods* 2023, doi:10.1038/s41592-022-01676-z:
   framework publication (MLE, model PDFs).
3. Official current documentation, Structure (continuous versus discrete
   model behaviour and fitter): https://locmofit.readthedocs.io/en/latest/basics/structure.html
4. Official current documentation, model library (spherical-cap parameters):
   https://locmofit.readthedocs.io/en/stable/LocMoFit.modelLibrary.html
5. Official current source tree:
   https://github.com/jries/SMAP/tree/master/LocMoFit

No exact quotations are retained; findings are paraphrases of the sources.
