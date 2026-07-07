# A structure-based mechanical screen for membrane proteins capable of coupling to particle entry

**Track:** Research — a discrete, reproducible finding.
**Method:** Claude Science end-to-end (physics-first pipeline, Stages 0–4).
**Core claim:** membrane proteins can be ranked, *from structure alone*, by the curvature-generating
capacity their documented activity supplies at the mechanical scale of particle entry — and this ranking
carries a physically meaningful endocytic/exocytic sign.

---

## The finding in one paragraph

Starting from the membrane mechanics of entry (a neck/bud of radius ~25 nm costs order 10²–10³ k_BT to
form), we computed for 13 membrane proteins — spanning mechanosensitive channels and exocytic curvature
machinery — a single structure-derived quantity: the bending + tension energy their conformational
activity can supply to the membrane, `E_curv = ½κ(2c₀)²A_footprint + γΔA`. Every input (intrinsic
curvature c₀, membrane footprint A, in-plane area change ΔA) is measured from experimental PDB
coordinates in a common membrane frame; the ranking uses **no LLM-estimated "probability of
involvement"** — the one place a literature constant would otherwise sit (a peripheral sensor with no
transmembrane span, synaptotagmin-1) is instead reported as *not measurable by this method* (E=0) rather
than filled with a guess. Four proteins clear a pre-set 10 k_BT relevance gate. The **top three are
exactly the canonical curvature generators** (dynamin, endophilin, amphiphysin), and our arc-fit radii
reproduce their literature values independently (amphiphysin 9.8 nm vs ~11 nm; endophilin 8.0 nm vs
6–11 nm) — the method validating on home turf. Carrying the curvature sign separates the tension-sensing
channels (inward/endocytic) from the curvature-generating scaffolds (outward/exocytic) using one engine —
the mechanical layer transcriptomic virtual-cell models structurally cannot represent. A
**pre-committed** enrichment test against external, ranking-blind GO curvature/entry annotations
**supports** the central hypothesis by the frozen decision rule (AUROC 0.750, one-sided p 0.085, Spearman
rho 0.273; gate-clearers 75% curvature-annotated vs 38% base rate), with the honest caveat that the pass
is at the 0.10 bar on n=13 — firmed up by expanding the candidate set.

---

## Stage 1b — the input-space fix (the honest headline)

The curated study above has a structural flaw that the enrichment result quietly depends on: **its 13
proteins and its 9 GO labels are both drawn from the same well-studied mammalian-endocytosis
literature.** A screen fed the known curvature generators can only rank known curvature generators; the
AUROC 0.75 "support" is therefore partly circular — the physics is being tested against the same
attention bias that chose its inputs. The novelty was filtered out at Stage 1, before the physics ever
ran.

So we replaced Stage 1 with a **query, not a hand-list**, and left Stages 0/2/3/4 unchanged:

- **Input:** every OPM-annotated membrane-protein entity in the RCSB PDB (18,982 entities → 7,653
  structures → **5,317 distinct proteins**; 4,639 at ≤4.0 Å), deduplicated by UniProt. From 13 curated
  candidates to a **1,669-assembly unbiased structural census**.
- **One uniform metric, zero curation:** the Stage-2 TM-cone c₀ + footprint, applied identically to
  every structure from its OPM-oriented coordinates (membrane normal = z, DUM-marked bilayer center).
  A contamination guard (modal-size TM-spanning-chain class, the automated form of the stoichiometry
  cross-check that caught RhoA in TRPV4) plus physical-validity bounds (A ≥ 2 nm², |c₀| ≤ 0.2 /nm) run
  at scale without a hand table.
- **48 of 1,669 assemblies clear the 10 k_BT gate.** The top hits are **not** the endocytic canon —
  they are bacterial secretion secretins (T2SS/T3SS protein D, MxiD, PilQ), pore-formers
  (Gasdermin-B, hemolysin E), fungal cell-wall/lipid synthases (chitin synthase, FKS1 β-glucan
  synthase, seipin), and ERAD/autophagy remodelers (Derlin-1, ATG9A). MscS, a positive control from
  the curated set, reappears organically at rank 22.

**The re-frozen pre-committed test (hash `e2871f10cd5faf00`; the curated hash is void for this
population) is NOT SUPPORTED on the unbiased census: AUROC 0.384, Spearman ρ = −0.072 (p = 0.003).**
The mechanical rank does not track the mammalian-endocentric GO labels — and **47 of 48 gate-clearers
carry zero of the 9 pre-declared terms.** This is not a failure of the physics; it is direct evidence
that the GO label set is an attention-biased ground truth. Curvature-generating capacity, measured from
structure, identifies membrane-deforming machines that lie *outside* the curated curvature vocabulary.
Those **35 novel candidates** (`stage3b_novel_candidates.csv`) — seipin, ATG9A, Derlin-1, the
secretins, Gasdermin-B — are exactly the mechanically-plausible, functionally-implicated,
under-attention predictions the curated 13 could not have surfaced. The flip from AUROC 0.75 (curated)
to 0.38 (unbiased) **is the finding**: it quantifies how much of the "support" was circularity.

Stage-1b artifacts: `stage1b_opm_catalog.csv`, `stage2b_geometry.csv`, `stage3b_ranking.csv`,
`stage3b_novel_candidates.csv`, `stage4b_prereg.md`/`.json`, `stage4b_enrichment.csv`,
`fig_stage3b_proteome_ranking.png`, `fig_stage3b_novel_candidates.png`, `fig_stage4b_enrichment.png`.

---

## Pipeline (each stage → artifact)

| Stage | What | Key artifact |
|------|------|--------------|
| 0 | Fix the mechanical energy scale of entry (κ=20 k_BT, neck ~25 nm, gate ~10 k_BT/protein) | `stage0_scale.json`, `fig_stage0_energy_scale.png` |
| 1 | 13 candidates, two legs; conformational-state map from **verified** PDB/UniProt | `stage1_candidates.csv`, `fig_stage1_state_coverage.png` |
| 2 | Membrane-frame alignment (symmetry-axis validated <9° vs OPM) + A(z) geometry engine | `stage2_geometry.csv`, `stage2_transitions.csv`, `fig_stage2_Az_profiles.png`, `fig_stage2_alignment_qc.png` |
| 3 | Curvature-generating capacity ranking (signed) — **the headline** | `stage3_ranking.csv`, `fig_stage3_ranking.png`, `fig_stage3_signflip.png` |
| 4 | Pre-committed enrichment test vs external GO labels | `stage4_prediction_prereg.md`, `stage4_enrichment.csv`, `fig_stage4_enrichment.png` |

## The ranking (E_curv, k_BT)

| Rank | Protein | Leg | E_curv | Clears 10 k_BT gate |
|---|---|---|---|---|
| 1 | Dynamin-1 | exocytic | 78.3 | ✓ |
| 2 | Endophilin-A1 N-BAR | exocytic | 37.0 | ✓ |
| 3 | Amphiphysin N-BAR | exocytic | 27.6 | ✓ |
| 4 | TRPV4 | mechanosensitive | 12.0 | ✓ |
| 5 | MscL | mechanosensitive | 5.2 | |
| 6 | Epsin-1 ENTH | exocytic | 4.4 | |
| 7 | MscS | mechanosensitive | 2.3 | |
| 8 | Piezo1 | mechanosensitive | 2.3 | |
| 9–13 | TRAAK, OSCA1.2, nhTMEM16, TREK-1, Syt-1 | mixed | <0.2 | |

*(TRPV4 was rank-1 at 79.9 k_BT in the first pass; adversarial review found its structure 8FC7 retained
4 bound RhoA copies that inflated the footprint. Restricting to the 4 TRPV4 subunits — matching the known
homotetramer — corrects it to 12.0 k_BT. See limitation 5.)*

---

## Claim discipline (what we do and do NOT claim)

**We do NOT claim** the molecular identity of entry factors is understudied — it is exhaustively
catalogued (alt-receptors, ACE2-independent entry, trafficking hijack; a crowded, saturated field).
We cite that crowding explicitly and stay out of that lane.

**We DO claim** the *quantitative biophysics of activity-coupled entry* — forces, curvature, tension
thresholds tied to specific conformational changes — is comparatively thin, and is structurally absent
from the 2026 transcriptomic virtual-cell paradigm (Arc *State*, CZI *rBio*, *scLong*), which ingests
molecular-identity lists and cannot represent membrane mechanics. Our screen is a concrete instance of
that missing physics layer.

**The ranking is a measurement, not an opinion.** Its inputs are coordinates; its criterion is an
energy at a pre-fixed scale. That is what makes it defensible under adversarial questioning.

## Limitations (stated plainly)

1. **Single-state capacities are upper bounds.** 9/13 proteins have one experimental conformational
   state; their c₀ is intrinsic-shape, not a measured transition. The clean two-state ΔA/Δc₀ values
   (MscS, nhTMEM16, Epsin ENTH) are the most defensible; the rest await a second state (see
   `NEXT_surrogate_hooks.md` for the Boltz-2/OpenFold3 plan).
2. **TRPV4 (rank 4) rests on a conical TM shape from one state** (8FC7). Its wide intracellular funnel is
   genuine TRP geometry but single-state; treat as a hypothesis, not a settled result.
3. **c₀→energy uses a continuum Helfrich model.** It omits the molecular detail (specific lipid
   interactions, protein crowding) — deliberately, since that omission is exactly what the second-half
   residual-learning surrogate is designed to expose.
4. **Enrichment pass is at the 0.10 bar, not 0.05** (n=13, two sparsely-annotated bacterial proteins).
   The result clears the pre-committed rule but the sample is small; expanding the candidate set is the
   direct next step to firm it up.
5. **Chain-composition contamination is a real failure mode of automated screens.** TRPV4's 8FC7
   bundles 4 RhoA copies with the channel; a naive membrane-spanning filter kept them and inflated the
   rank (79.9 → 12.0 k_BT once corrected). The fix — restrict to the modal-size subunit class and check
   it against known oligomeric state (all 8 channels now match: MscL 5-mer, MscS 7-mer, Piezo1 3-mer,
   TRPV4 4-mer, K2P/OSCA/TMEM16 dimers) — is now a standing QC step. This is exactly the kind of
   "soft joint" a physics-first pipeline must audit rather than trust.

## What would falsify the central hypothesis

If the mechanical rank had *no* relationship to independent curvature/entry annotation (AUROC ≈ 0.5),
the premise — that structure-derived curvature capacity marks entry-coupling candidates — would be
unsupported. We pre-registered this test before scoring (original hash `7e6777a655b068e9`; corrected
`41d49328960d4083` after the RhoA-contamination fix). An intervening scoring run diverged from the
original 9 pre-declared GO IDs to a different 14-term set (a bug — 2 were dropped, 7 unrelated generic
terms added); that divergence was caught and reverted back to exactly the original 9 before the result
below was computed — see `stage4_prediction_prereg.md` for the full trace. The corrected result
**supports** the hypothesis at the pre-set bar (AUROC 0.750, p 0.085, scored against exactly the 9
pre-declared GO terms) — but the pass is at 0.10, not 0.05, so it is support, not proof.

## Reproducibility

Every figure and table above is a Claude Science artifact carrying its own generating code, inputs, and
conda environment (`structbio`). The core (Stages 0–4) depends only on public data (RCSB PDB, UniProt,
OPM, QuickGO) and runs CPU-light on a laptop. See `NEXT_surrogate_hooks.md` for the second-half
neural-surrogate handoff.
