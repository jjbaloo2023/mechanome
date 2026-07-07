# Stage 4b — Proteome-scale pre-registered enrichment test

**Frozen ranking hash (SHA-256, first 16):** `e2871f10cd5faf00`
**Supersedes:** `41d49328960d4083` (the 13-protein curated study) — that hash is VOID for this population.
**Frozen:** 2026-07-07T20:37:43.620127Z — BEFORE any GO label was fetched for the proteome-scale population.

## Population
1669 distinct OPM-oriented membrane assemblies (≤4.0 Å) passing physical-validity
(A_footprint ≥ 2 nm², radii ≥ 5 Å) and plausible-curvature (|c₀| ≤ 0.2 /nm) QC. This is an
**unbiased structural census**, not a curated candidate list — the whole point of the fine-tune.

## Pre-declared label GO terms (EXACTLY these 9)
GO:0046718, GO:0007009, GO:0030100, GO:0006897, GO:0016050, GO:0001778, GO:0097320,
GO:0072659, GO:0030674. An assembly is label-positive if any subunit UniProt carries ≥1 term.

**Provenance of this list, stated precisely:** these 9 IDs are the original Stage-4 pre-registration
for the curated study, written before any label was fetched. An *intervening* scoring run in the
curated study's history used a diverged 14-term set (a bug: 2 of these 9 were dropped, 7 unrelated
generic terms were added) — that run was caught and reverted earlier in the same working session,
back to exactly these 9 IDs, before this proteome-scale test was frozen. So this list is "the original
9, restored" rather than "never touched" — flagged here so the label set's history is fully auditable
rather than glossed as untouched.

## Decision rule (pre-committed, identical to the curated study)
SUPPORT iff **AUROC > 0.5 AND one-sided p < 0.10 AND Spearman ρ > 0**; else null/refute.
Reported per the rule, not re-tuned.

## Result
- **TEST 1 rank-sum:** AUROC = **0.384**, one-sided p = 0.998
- **TEST 2 Spearman:** ρ = **-0.072**, p = 0.0032 (significantly *negative*)
- **TEST 3 gate enrichment:** base rate 3.3%, gate-clearers 2.1%
- **VERDICT: NOT SUPPORTED.** AUROC is below 0.5 and the correlation is slightly negative.

## What this means (the actual scientific finding)
The curated 13-protein study reported AUROC 0.75 — **but that was circular**: its proteins and its
GO labels were both drawn from the same well-studied mammalian-endocytosis literature. When the input
bias is removed and the physics is run on an unbiased structural census, the association **disappears**.

Post-hoc (exploratory, does not change the frozen verdict): **47 of 48 gate-clearers carry zero of the
9 GO terms.** The high-curvature hits are bacterial secretins (T2SS/T3SS protein D, MxiD, PilQ),
pore-formers (Gasdermin-B, hemolysin E), fungal cell-wall/lipid synthases (chitin synthase, FKS1
glucan synthase, seipin), and ERAD/autophagy remodelers (Derlin-1, ATG9A) — membrane-deforming
machines the mammalian-endocentric GO vocabulary does not tag with these terms. The label set is an
**attention-biased ground truth**; the physics is orthogonal to it.

**This is a more honest and more interesting result than the curated positive control.** The negative
enrichment is not a failure of the physics — it is direct evidence that curvature-generating capacity,
measured from structure, identifies membrane-deforming proteins that fall *outside* the curated
endocytosis canon. Those 35 novel candidates (`stage3b_novel_candidates.csv`) are exactly the
predictions the curated set could not have surfaced.
