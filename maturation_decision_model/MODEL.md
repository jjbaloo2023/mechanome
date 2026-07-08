# Steric-Augmented Maturation-Decision Model

A minimal, CPU-light physics module that computes the maturation energy barrier of a
clathrin-coated pit as a function of membrane tension σ and adaptor surface coverage φ,
and maps that barrier to a **commit/abort decision probability**. Epsin enters through a
physically-resolved curvature term (ENTH wedge **+** disordered-domain steric pressure),
not a lumped constant.

> Module one of a north-star generalizable endocytosis model. This module: the physics
> only. Empirical fitting/validation against live-cell abortive fractions is handled
> separately. The novelty is the **assembly** — a coverage- and tension-dependent
> steric-augmented barrier wired to a maturation-decision probability — not the
> underlying membrane mechanics.

---

## Novelty boundary (what is borrowed vs new)

**Borrowed and cited — foundations, not claimed:**
- **Helfrich–Canham** membrane mechanics (bending + tension + spontaneous curvature).
- **Hassinger, Oster, Drubin & Rangamani, *Design principles for robust vesiculation in
  clathrin-mediated endocytosis*, PNAS 114:E1118–E1127 (2017)**, doi:10.1073/pnas.1617705114 —
  forward model: coat area / C₀ / tension / actin → bud; the flat→budded transition is
  tension-dependent (snap-through).
- **Akamatsu, Vasan, Serwas, Ferrin, Rangamani & Drubin, eLife 9:e49840 (2020)**,
  doi:10.7554/eLife.49840 — continuum-mechanics pit under tension + actin force model; Helfrich-based.
- **Busch, Houser, Hayden, Sherman, Lafer & Stachowiak, *Intrinsically disordered proteins
  drive membrane curvature*, Nat Commun 6:7875 (2015)**, doi:10.1038/ncomms8875 — disordered
  domains of Epsin1/AP180 generate
  curvature by **steric pressure** from their large hydrodynamic radius; coverage-dependent.
  Source of the ENTH (≈16 nm²) and disordered-CTD (≈70 nm²) footprints.
- **Snead/Stachowiak steric-force measurements** — steric-pressure magnitude / scale.
- **Bradley & Radhakrishnan, PNAS 113:E5117–E5124 (2016)**, doi:10.1073/pnas.1605259113 —
  curvature–undulation coupling recovers an effective C₀ from CG-MD undulation spectra of the
  epsin ENTH domain on a bilayer (the MD→C₀→Helfrich provenance).
- **Own 2020 (Commun Biol)** — characterized epsin's tension-responsive recruitment and
  reported the abortive-fraction-vs-tension phenomenon; did **not** build a decision model.

**New (this module):**
1. A **steric-augmented maturation barrier** ΔE_commit(σ, φ) built for the CME maturation
   decision, with epsin's curvature resolved into wedge + coverage-dependent steric terms.
2. The **barrier → decision-probability layer** that turns a single-pit energy barrier into
   a population commit/abort propensity.

---

## The model, in three layers

### 1. Reduced Helfrich barrier (`src/barrier.py`)
A coated patch of **fixed** area A_coat invaginates flat→budded along one reaction
coordinate, the spherical-cap polar angle ψ∈[0,π]. Energy (uniform mean curvature on the cap):

    E(ψ) = (κ/2)(2/R(ψ) − C₀_eff)² · A_coat   +   σ · A_coat · (1−cos ψ)/2

with the fixed-area geometry R(ψ) = √(A_coat / [2π(1−cos ψ)]). This is a **reduced model,
not a shape solver** (deliberate — scope discipline). It is anchored by exact analytic limits,
checked in code:
- C₀=0, ψ=π (closed sphere): E = **8πκ** exactly, independent of A_coat — the textbook
  Helfrich sphere energy.
- flat state ψ→0: ΔE = 0.

For C₀_eff > 0 the patch relaxes to an interior **resting-dome minimum**; from there it can go
forward to the committed budded/closed state (barrier **ΔE_commit**) or back to flat
(**ΔE_abort**). ΔE_commit **rises with tension** and **falls with C₀_eff** — the established
Rangamani behavior, here reproduced from first principles.

### 2. Curvature-source registry (`src/curvature_sources.py`)
C₀_eff is a sum of pluggable, additive contributions — the architecture "slot":

    C₀_eff(φ, σ) = C₀_coat + C₀_ENTH(φ) + C₀_steric(φ, σ)

- **CoatSource** — clathrin lattice, fixed C₀ = 2/R_bud (R_bud ≈ 50 nm).
- **ENTHWedge** — structured helix-0 insertion, modest, linear in coverage: C₀ = c₀·φ.
- **StericBrush** — the dominant epsin term. Lateral steric pressure Π(φ) from a 2D
  crowding equation of state (hard-disk / scaled-particle default, Π = (k_BT/A_mol)·φ/(1−φ)²;
  Alexander–de Gennes brush scaling Π∼φ^9/4 as an alternative), converted to curvature by
  the first-moment-of-lateral-stress relation **κ·C₀_steric = η·Π·z̄**, with a
  phenomenological tension damping 1/(1+σ/σ*).

Adding a protein = adding a source object. Nothing downstream changes.

### 3. Decision layer (`src/decision.py`)
Maps the barrier to a commit/abort probability. Two forms:
- **Competing-barrier Kramers** (default, principled): escape rates over ΔE_commit and
  ΔE_abort → P(commit) = 1/(1 + ν_ratio·exp[−(ΔE_abort−ΔE_commit)]). One free number,
  the log attempt-frequency ratio (a prefactor asymmetry, not an energy re-fit).
- **Reduced logistic** (used for the graded population prediction):
  P(commit) = 1/(1 + exp[+α(ΔE_commit − ΔE½)]). Two free numbers, α and ΔE½.

`src/model.py` wires the three layers into `MaturationDecisionModel`.

---

## Parameter provenance

| symbol | meaning | value | source | status |
|---|---|---|---|---|
| κ | bending rigidity | 20 k_BT | standard (Helfrich; Rangamani) | fixed |
| A_coat | coat patch area | 11 310 nm² (R₀=30 nm) | geometry (full-vesicle scale) | fixed |
| R_bud | coat preferred radius | 50 nm | CME bud scale | fixed |
| A_ENTH | ENTH footprint | 16 nm² | Busch 2015 | fixed |
| A_CTD | disordered-CTD footprint | 70 nm² | Busch 2015 | fixed |
| c₀,ENTH | wedge C₀ at φ=1 | 0.035 nm⁻¹ | structured-wedge scale | fixed |
| z̄ | steric moment arm | ~3 nm | Snead/Stachowiak scale | fixed (O(1)) |
| σ* | steric tension-damping scale | 0.02 mN/m | phenomenological | fixed |
| **η** | **steric→curvature efficiency** | **~1 (swept 0.5–2)** | **O(1); the explicit soft joint** | **sensitivity** |
| α, ΔE½ | decision-layer params | 0.06 k_BT⁻¹, 55 k_BT | **the only floated numbers** | free (1–2) |

Unit bridge: energies in k_BT; tension internally in k_BT/nm² (0.00243 k_BT/nm² = 0.01 mN/m,
using k_BT = 4.114 pN·nm at 300 K). **Everything except α, ΔE½ is fixed from literature.**
The one order-of-magnitude-uncertain physical quantity, η, is exposed and swept — its
uncertainty scales the magnitude of the steric effect but not its direction.

**MD→C₀→Helfrich provenance chain** (cited, not run here): CG-MD undulation spectrum →
effective C₀(φ) via curvature–undulation coupling (Bradley–Radhakrishnan 2016) → consumed by
the continuum Helfrich barrier. MD parameterizes C₀ offline; no inline MD.

---

## Results (figures)

- **`figures/fig_c0_decomposition.png`** — C₀_eff decomposed into coat + ENTH + steric vs
  coverage φ. The steric brush overtakes the structured wedge as the coat crowds (φ≈0.8),
  carrying C₀_eff through the 0.05–0.07 nm⁻¹ budding window.
- **`figures/fig_barrier_landscape.png`** — ΔE_commit(σ, φ) heatmap with the
  spontaneous-budding boundary, plus E(ψ) profiles at low/mid/high tension showing the
  resting dome climbing and sliding back as tension rises.
- **`figures/fig_decision_map.png`** — the two decision-layer mappings and their free params.
- **`figures/fig_pabort_vs_tension.png`** — the headline prediction: P(abort) rises with
  tension, and epsin's disordered-CTD steric term **lowers it and flattens the rise**
  (buffering), robust across η∈[0.5,2].

## Pre-registered prediction
See `PREREGISTRATION.md` — the sign (steric term lowers P(abort) and buffers the
tension-driven rise) was committed before rendering the prediction figure. Confirmed by the
model: buffering Δ = +0.021 / +0.038 / +0.090 at hyper/iso/hypo; the tension-response slope
flattens from +0.256 (ENTH only) to +0.187 (full epsin).

## Reduced-model limitations (stated plainly)
- Single spherical-cap reaction coordinate with **fixed coat area** — not a free-boundary
  shape solver. It captures the flat→budded barrier and its σ/C₀ dependence, not neck
  detail or non-axisymmetric shapes.
- Absolute abortive fractions depend on the two decision-layer parameters; the module tests
  **direction and shape**, not calibrated magnitudes.
- σ* and z̄ are order-of-magnitude estimates; η is swept explicitly.
- The steric→curvature conversion is the first-moment relation, not a full stress-profile
  integral.

## Reproduce
```python
import sys; sys.path.insert(0, "src")
from model import MaturationDecisionModel
import curvature_sources as CS
m = MaturationDecisionModel(CS.build_epsin_full(), decision="logistic", alpha=0.06, dE_half=55.0)
m.p_abort_mNm(phi=0.55, sigma_mNm=0.02)   # population abort probability at iso tension
```
CPU-light; no GPU, no MD, no data dependency. `figures/` are regenerated by the build cells.
