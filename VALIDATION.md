# Validation

Empirical support for the mechanome / CME commitment framework. This document
records the reverse-validation results that test the model's forward predictions
against independent experimental data. All figures and per-site data referenced
here are archived as project artifacts; the analysis code for the CME line is
maintained separately from the structural-screen pipeline documented in
[`README.md`](README.md).

Two validations are reported:

1. **Cross-cell-line curvature trajectory** — the predicted coat-curvature
   program, tested for reproducibility across three cell lines using an
   independent super-resolution dataset.
2. **Cargo-selective adaptor usage in influenza A virus entry** — the
   division-of-labor prediction (curvature-driver vs size-setter), tested
   against a viral cargo.

---

## 1. Cross-cell-line curvature trajectory (reverse validation)

**Dataset.** BioImage Archive **S-BIAD566** (Mund et al. 2023, *J Cell Biol*,
doi:10.1083/jcb.202206038). 3D single-molecule
localization microscopy of clathrin-coated structures with per-site LocMoFit
geometric model fits, grouped by cell line.

**Method.** For each cell line, sites were sorted by closing angle θ to build a
pseudo-temporal curvature trajectory H(θ), and a saturating curvature law
`H(θ) = H₀·(1 − exp(−γθ/H₀))` was fit to the per-site geometry. Sites flagged
as disconnected were removed prior to fitting.

**Result.** The curvature trajectory reproduces in all three cell lines: mean
curvature rises monotonically from a near-flat coat (~0.003 nm⁻¹) to a curved
cap, and the fitted saturating curvature scale H₀ clusters within a narrow band
across a human melanoma line, a mouse fibroblast line, and a human osteosarcoma
line.

| Cell line | QC sites | H₀ (10⁻³ nm⁻¹) | γ (10⁻³) | R² |
|---|---|---|---|---|
| SK-MEL-2 | 1645 | 15.6 ± 0.2 | 11.7 | 0.81 |
| NIH-3T3  | 688  | 12.0 ± 0.1 | 10.3 | 0.89 |
| U2OS     | 241  | 13.1 ± 0.4 | 9.9  | 0.82 |

The coat-curvature program is therefore not specific to the cell line on which
the model was originally validated; the same saturating trajectory is recovered
in each, with H₀ confined to 12.0–15.6 × 10⁻³ nm⁻¹ (R² 0.81–0.89).

**Scope.** This is a geometry-only validation. Force is not estimated on this
path, consistent with the framework's epistemic firewall: pseudo-temporal
sorting of static snapshots supports a shape trajectory but cannot bear a force
value.

**Artifacts.** `celltype_iav_validation.png` (panels a–b),
`celltype_iav_validation.json` (fits + provenance),
`biad566_allcelllines.csv` (combined per-site geometry).

---

## 2. Cargo-selective adaptor usage in IAV entry

**Source.** Joseph et al. 2022, *Biomechanical Role of Epsin in Influenza A
Virus Entry* (paired epi/TIRF imaging; author's own data).

**Prediction tested.** The commitment rule assigns distinct roles to
curvature-driving wedges (epsin, ENTH) and size-setting crowders (CALM/PICALM,
ANTH). If this division of labor is real, a curvature-dependent cargo should
depend selectively on the curvature-driver.

**Result — colocalization.** IAV colocalizes with epsin-containing
clathrin-coated structures at 90%, versus ~65% with CALM — a structurally
similar ENTH/ANTH protein that lacks the ubiquitin-interacting motifs. Epsin
acts as the cargo-specific adaptor for IAV entry.

**Result — loss of function.** Deletion of the epsin ENTH domain reduces IAV
colocalization with coated structures and reduces internalization, while bulk
uptake is unaffected by epsin overexpression. The curvature-generating domain
is required for the epsin-dependent entry route.

**Scope and limitations.**

- Colocalization and internalization are recruitment/entry readouts, not
  curvature or force measurements — the same epistemic tier as recruitment
  cohort data.
- A per-coat epi/TIRF depth readout is **not** available from this dataset: the
  epi and TIRF images are different fields of view (separate cells imaged in the
  two modes, not the same cells imaged both ways), so a per-punctum epi/TIRF
  ratio has no physical meaning. A registered same-field epi-TIRF acquisition or
  a z-stack would be required.

---

## Summary

| Validation | Data | Tier | Outcome |
|---|---|---|---|
| Curvature trajectory | S-BIAD566, 3 cell lines | GROUNDED (geometry) | Trajectory reproduces; H₀ 12.0–15.6 × 10⁻³ nm⁻¹ |
| IAV cargo selectivity | Joseph et al. 2022 | LINKED (recruitment) | Epsin is the cargo-specific adaptor; ENTH required |
