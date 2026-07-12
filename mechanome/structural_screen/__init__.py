"""
structural_screen -- structure-based mechanical screen (vendored from the
mechanistic-entry-model project).

Ranks membrane proteins by the *curvature-generating capacity* their
conformational activity supplies at the mechanical scale of particle entry,
computed entirely from experimental structures against a fixed Helfrich energy
scale (kappa = 20 kBT, gate = 10 kBT/protein). This is mechanome's molecular /
structure entry point: it takes PDB structures in and emits a signed
curvature-capacity ranking that feeds the multi-scale map. Its
mechanosensitive-channel hits (MscL, MscS, Piezo1, TRAAK, TREK-1, OSCA1.2,
TRPV4) are the structural counterpart to the channel forward model
(``mechanome.forward_channel`` / registry ``ms_gating_v1``).

The pipeline is Stages 0-4 (``src/stage{0..4}_*.py``); the scored ranking is
frozen with a SHA-256 integrity hash and a pre-registered enrichment test
(``results/stage4_prediction_prereg.md``). The precomputed ``results/`` are the
authoritative outputs -- re-running the stages requires PDB/OPM downloads.

Key entry points:
    verify_frozen_ranking()  -> re-derive the SHA-256 hash from the stored
                                ranking and confirm it matches the frozen value.
    frozen_ranking()         -> the frozen ranking as a DataFrame.
    load_energy_scale()      -> the Stage-0 energy-scale constants (dict).
"""
from __future__ import annotations
import hashlib
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_RESULTS = os.path.join(_HERE, "results")

# The five ranking columns whose CSV serialization defines the frozen hash.
FROZEN_COLUMNS = ["rank", "protein", "E_curv_kBT", "E_curv_signed", "clears_gate"]


def _frozen_record() -> dict:
    with open(os.path.join(_RESULTS, "stage4_frozen_ranking.json")) as fh:
        return json.load(fh)


def verify_frozen_ranking() -> dict:
    """Re-derive the SHA-256 (first 16 hex) of the frozen ranking CSV and check
    it against the stored ``rank_hash``. Also confirm the computed
    ``stage3_ranking.csv`` reproduces the same hash over ``FROZEN_COLUMNS``.

    Returns a dict with the stored hash, both recomputed hashes, and a
    ``passed`` flag. Raises nothing -- callers assert on ``passed``.
    """
    import pandas as pd

    rec = _frozen_record()
    stored = rec["rank_hash"]
    from_json = hashlib.sha256(rec["frozen_ranking_csv"].encode()).hexdigest()[:16]

    stage3 = pd.read_csv(os.path.join(_RESULTS, "stage3_ranking.csv"))
    csv = stage3[FROZEN_COLUMNS].to_csv(index=False)
    from_stage3 = hashlib.sha256(csv.encode()).hexdigest()[:16]

    return {
        "stored_hash": stored,
        "hash_from_frozen_csv": from_json,
        "hash_from_stage3_csv": from_stage3,
        "passed": from_json == stored and from_stage3 == stored,
    }


def frozen_ranking():
    """The frozen curvature-capacity ranking as a pandas DataFrame."""
    import io
    import pandas as pd

    return pd.read_csv(io.StringIO(_frozen_record()["frozen_ranking_csv"]))


def load_energy_scale() -> dict:
    """The Stage-0 energy-scale constants (kappa, gamma, relevance threshold)."""
    with open(os.path.join(_RESULTS, "stage0_scale.json")) as fh:
        return json.load(fh)


def prereg_go_terms() -> list:
    """The nine pre-registered GO IDs the enrichment test scored against."""
    return list(_frozen_record()["label_go_terms"])
