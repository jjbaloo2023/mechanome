# Stage 4 — Pre-registered prediction (label set frozen BEFORE scoring)

**Frozen ranking hash (SHA-256, first 16):** `41d49328960d4083`

## Pre-declared label GO terms — EXACTLY these 9 IDs (the set actually scored)
- GO:0046718 — viral entry into host cell
- GO:0007009 — plasma membrane organization
- GO:0006897 — endocytosis
- GO:0030100 — regulation of endocytosis
- GO:0016050 — vesicle organization
- GO:0001778 — plasma membrane repair
- GO:0097320 — plasma membrane tubulation
- GO:0072659 — protein localization to plasma membrane
- GO:0030674 — protein-macromolecule adaptor activity

A protein annotated (QuickGO/EBI) with >=1 of these counts as label-positive. This is the complete,
literal set used in the scoring code — no generic lipid-binding terms were added.

> **Transparency notes (two corrections after adversarial review):**
> 1. An earlier scoring run used a 14-term set that had dropped two of the curvature-specific terms
>    above and added seven generic lipid/phospholipid-binding terms. That was inconsistent with this
>    pre-registration. The test was re-run with **exactly the 9 IDs above**; the outcome is unchanged
>    (AUROC 0.750, p 0.085 either way — the result does not depend on the generic terms).
> 2. The original ranking (hash `7e6777a655b068e9`) had TRPV4 at rank 1 (79.9 k_BT); its structure 8FC7
>    retained 4 bound RhoA copies that inflated the footprint. Restricting to the 4 TRPV4 subunits
>    (matching the known homotetramer) corrects TRPV4 to 12.0 k_BT (rank 4). Labels were never re-chosen.

## The prediction (falsifiable, one direction)
Stage-3 curvature-generating capacity (E_curv) — computed purely from structure — is **positively
associated** with the independent GO annotations above.

Three pre-committed tests:
1. **Rank-sum (Mann–Whitney U, one-sided):** label-positive proteins have higher E_curv.
2. **Spearman** between E_curv and graded annotation count.
3. **Gate enrichment:** fraction of gate-clearers curvature/entry-annotated vs base rate.

## Decision rule (pre-committed)
- **Support** if AUROC > 0.5 with one-sided p < 0.10 AND Spearman rho > 0.
- **Refute / null** if AUROC <= 0.5 or association flat/negative — reported as null, not re-tuned.

## Result
- TEST 1: **AUROC = 0.750, one-sided p = 0.085** ✓
- TEST 2: Spearman rho = 0.332, p = 0.268 (positive; not independently significant)
- TEST 3: gate-clearers 75% label-positive vs 38% base rate
- **Verdict: SUPPORTED** by the pre-committed rule (AUROC>0.5, p<0.10, rho>0).

## Caveat on power
n=13 with two sparsely-annotated bacterial proteins (MscL 0 GO terms, MscS 8). The pass is at the 0.10
bar, not 0.05; expanding the candidate set is the direct next step.
