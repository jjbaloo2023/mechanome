# Mechanome forward models — physics and validation anchors

The mechanome spans mechanical scales. `membrane` (curvo, `helfrich_v1`) is the
one module validated against **real force-paired data** (STED tether, Roy et al.
2020). This note fixes the governing law, the analytic self-check, and the
**applicable real/published validation data** for the four modules being
promoted from `registered_stub` to a new `built_analytic` status.

`built_analytic` is a deliberately weaker bar than `built_validated`: each model
is verified to recover a **known closed-form limit** and to **reproduce a
canonical published measurement's parameters**, but is NOT paired against a
raw experimental dataset acquired here. Every claim these modules emit carries
`validation=analytic_limit` on its face so the epistemic bar is explicit.

On data availability: the canonical measurements below are published
force–response *curves* (patch-clamp Po–tension, AFM force–lifetime, micropipette
pressure–radius, junction-angle tensions), not deposited numeric datasets that
are downloadable in this environment. The applicable-data strategy is therefore:
(1) recover the analytic limit exactly, and (2) reconstruct each published
curve at its **reported parameter values** and confirm the forward+inverse round
-trips those parameters. Where a real dataset is reachable it can be swapped into
the same `self_validate` seam unchanged.

---

## 1. tissue — vertex / junction force inference

**Governing law.** Force balance at a tri-cellular vertex (Young / Lami):
Σ_i T_i **t̂**_i = 0, where T_i are the edge (interface) tensions meeting at the
vertex and **t̂**_i the unit tangents. Equivalently T_1/sin θ_1 = T_2/sin θ_2 =
T_3/sin θ_3 (law of sines on the three opening angles).

**Analytic self-check.** A symmetric vertex (three equal tensions) sits at
θ = 120° for all angles; conversely, recovering relative tensions from measured
angles must return T_1:T_2:T_3 = 1:1:1 at 120°, and the general law-of-sines
ratios for asymmetric angles, to <1%.

**Applicable validation data.** Bayesian force inference from cell-array
geometry — Ishihara & Sugimura 2012, *J Theor Biol* 313:201–211
(doi:10.1016/j.jtbi.2012.08.017); CellFIT, Brodland et al. 2014. These methods
are validated against vertex-model simulation and laser-ablation recoil. Anchor:
recover relative junction tensions from a synthetic tri-junction geometry.

**Inverse seam.** Bayesian junction-tension inference (least-squares / MAP on the
force-balance residual over a vertex graph).

---

## 2. cortex — active-gel cortical tension (Young–Laplace)

**Governing law.** Laplace law across the actomyosin cortex: ΔP = 2γ/R, with
cortical tension γ set by myosin activity. Micropipette critical-pressure form
(hemispherical cap, L_p = R_p): γ = P_c / [2(1/R_p − 1/R_c)].

**Analytic self-check.** Round-trip: given γ and R, predict ΔP and re-solve for γ
to <1%; recover γ from a synthetic (P_c, R_p, R_c) micropipette measurement.

**Applicable validation data.** Micropipette aspiration cortical tension —
Tinevez et al. 2009, *PNAS* 106(44):18581 (doi:10.1073/pnas.0903353106);
Hochmuth 2000, *J Biomech* 33:15. Reported magnitudes: mitotic/interphase cells
~0.1–1 mN/m; neutrophil ~0.03 mN/m (≈30 pN/µm). Anchor: recover γ in this range
from the Laplace balance.

**Inverse seam.** TFM / active-gel stress inference (here the closed-form Laplace
inverse; a full active-gel PDE is the documented next tier).

---

## 3. bond — Bell / catch–slip molecular bond

**Governing law.** Bell slip bond: k_off(F) = k0 · exp(F·x‡ / kBT), bond lifetime
τ(F) = 1/k_off(F). Two-pathway catch–slip (Pereverzev et al. 2005):
k_off(F) = k_c0·exp(−F·x_c/kBT) + k_s0·exp(F·x_s/kBT) — a catch pathway (negative
sign) plus a slip pathway (positive), giving a biphasic τ(F) with a lifetime
peak.

**Analytic self-check.** Pure slip: recover x‡ and k0 from a synthetic
force–lifetime curve by linear fit of ln(1/τ) vs F to <2%. Catch–slip: recover
the lifetime-peak force from the two-pathway parameters analytically.

**Applicable validation data.** Marshall et al. 2003, *Nature* 423:190
(doi:10.1038/nature01605) — P-selectin/PSGL-1 catch–slip by AFM, biphasic
lifetime peaking ~1.1 s near ~10–20 pN; P-selectin–G1 slip-bond control is pure
Bell. Two-pathway analysis: Pereverzev et al. 2005, *Biophys J* 89:1446. Anchor:
recover Bell x‡ from the slip control and the peak location from the catch–slip
parameters.

**Inverse seam.** MLE/Bayesian fit of Bell or two-pathway parameters to a
force–lifetime dataset (AFM / BFP / optical tweezers).

---

## 4. channel — mechanosensitive gating (MscL / Piezo)

**Governing law.** Two-state Boltzmann gating driven by membrane tension σ:
Po(σ) = 1 / (1 + exp(−(σ·ΔA − ΔG)/kBT)), where ΔA is the in-plane gating-area
change and ΔG the intrinsic (zero-tension) free-energy difference; midpoint
σ½ = ΔG/ΔA.

**Analytic self-check.** Recover ΔA and σ½ from a synthetic Po–tension sigmoid to
<2%; verify the slope dPo/dσ at midpoint = ΔA/(4 kBT).

**Applicable validation data.** MscL patch-clamp Po(σ) — Sukharev et al. 1999,
*J Gen Physiol* 113(4):525–540 (doi:10.1085/jgp.113.4.525): sigmoidal Po with
**midpoint T½ = 11.8 dyn/cm (= 11.8 mN/m)**, maximal slope sensitivity 0.63
dyn/cm per e-fold, unstressed closed↔open energy ΔE = 18.6 kBT, and in-plane
gating-area change **ΔA = 6.5 nm²** (two-state analysis; ≈6 nm² summed over all
transitions) — all quoted directly from the paper's abstract. Comparators
(other mechanosensitive channels, lower midpoints): Piezo1 ~1.4 mN/m (Cox et al.
2016, *Nat Commun* 7:10366); MscS midpoint ~6.3 mN/m in azolectin liposomes vs
~17.8 mN/m in spheroplasts (Shaikh, Cox & Nomura 2014, *Channels* 8:321,
doi:10.4161/chan.28366); TRAAK (Brohawn et al. 2014, *PNAS* 111:3614). Anchor:
reproduce the MscL sigmoid at
ΔA = 6.5 nm², σ½ = 11.8 mN/m and round-trip those parameters.

**Coupling to curvo.** The channel module reads the **membrane module's inferred
tension σ** directly, so a curvo tension estimate feeds channel open-probability
— the one cross-scale link that is physically grounded on both ends.

**Inverse seam.** Boltzmann fit of (ΔA, ΔG) to a patch-clamp Po–tension curve.

---

### Validation-tier summary

| module   | analytic limit                          | published anchor (reproduce params)        | real-data paired? |
|----------|-----------------------------------------|--------------------------------------------|-------------------|
| membrane | a*=4κ/λ, tube R,f                       | STED tether (Roy 2020)                     | **yes** (built_validated) |
| tissue   | 120° ↔ equal tensions                   | Bayesian force inference (Ishihara 2012)   | no (analytic)     |
| cortex   | ΔP=2γ/R round-trip                      | micropipette γ (Tinevez 2009)              | no (analytic)     |
| bond     | ln(1/τ) vs F slope = x‡/kBT             | P-selectin catch–slip (Marshall 2003)      | no (analytic)     |
| channel  | dPo/dσ|½ = ΔA/4kBT                      | MscL Po(σ) (Sukharev 1999)                 | no (analytic)     |
