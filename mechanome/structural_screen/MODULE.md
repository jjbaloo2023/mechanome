# structural_screen — the structure-based mechanical screen

Vendored from the standalone **mechanistic-entry-model** project. This is
mechanome's molecular / structure entry point: it ranks membrane proteins by the
**curvature-generating capacity** their conformational activity supplies at the
mechanical scale of particle entry, computed entirely from experimental
structures against a fixed Helfrich energy scale.

## What it does

The reframe is *not* "which protein does a particle bind" (molecular identity —
a saturated field) but "what a protein's *activity* can do mechanically to the
membrane." Every number traces to PDB coordinates and one fixed energy scale;
there are no LLM-estimated involvement probabilities anywhere in the ranking.

The signed capacity `E_curv_signed` separates, from **one** engine
(`E = ½κ(2c₀)²A + γ|ΔA|`), the tension-sensing channels (inward / endocytic,
negative sign) from the curvature-generating scaffolds (outward / exocytic,
positive sign).

## Pipeline (Stages 0–4)

| Stage | Script | Output |
|---|---|---|
| 0 | `src/stage0_energy_scale.py` | mechanical energy scale of entry (gate = 10 kBT/protein) |
| 1 | `src/stage1_candidates.py` | 13 candidates, two legs; verified PDB/UniProt state map |
| 2 | `src/stage2_geometry.py` | membrane-frame alignment + A(z) cross-section geometry engine |
| 3 | `src/stage3_ranking.py` | **signed curvature-generating-capacity ranking** |
| 4 | `src/stage4_enrichment.py` | pre-committed enrichment test vs external GO labels |

The precomputed `results/` and `figures/` are the authoritative outputs.
Re-running the stages requires PDB/OPM/QuickGO downloads (see `docs/REPORT.md`);
raw structure files are git-ignored and never committed.

## Integrity — the frozen ranking

The scored ranking is frozen with a SHA-256 hash (first 16 hex) and a
pre-registered enrichment test whose label set was fixed **before** scoring:

- **Frozen hash:** `41d49328960d4083` (over columns
  `rank, protein, E_curv_kBT, E_curv_signed, clears_gate`).
- **Pre-registration:** `results/stage4_prediction_prereg.md` — nine GO IDs,
  one-directional falsifiable prediction, pre-committed decision rule.
- **Verdict:** SUPPORTED (AUROC 0.750, one-sided p 0.085, Spearman ρ 0.332 > 0).

```python
from mechanome import structural_screen as ss
ss.verify_frozen_ranking()   # {'stored_hash': '41d49328960d4083', ..., 'passed': True}
ss.frozen_ranking()          # the ranking as a DataFrame
```

## Link into the mechanome

The screen's mechanosensitive-channel hits (MscL, MscS, Piezo1, TRAAK, TREK-1,
OSCA1.2, TRPV4) are the structural counterpart to the channel forward model
(`mechanome.forward_channel`, registry `ms_gating_v1`): the screen supplies a
structure-derived spontaneous curvature `c₀` for each channel, which the gating
model turns into a tension-dependent open probability. The screen's ranking is
registered as the forward model `structural_screen_v1` (scale = molecule), and
its validation anchor is that the BAR-domain arc-fit radii reproduce their
independent literature values (amphiphysin ~9.8 nm vs ~11 nm; endophilin
~8.0 nm vs 6–11 nm) — the method validating on home turf.
