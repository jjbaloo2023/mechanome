"""Read and verify the checked-in structural screen without rerunning it.

The frozen record owns the ranking hash and pre-registered GO terms. The
stage-3 table supplies the additional geometry columns used by channel_link.
"""

from __future__ import annotations

import hashlib
from io import StringIO
import json
from pathlib import Path

import pandas as pd

from curvo.constants import KAPPA_KBT_DEFAULT, KBT_J

_RESULTS = Path(__file__).parent / "results"
_RANKING_COLUMNS = ["rank", "protein", "E_curv_kBT", "E_curv_signed", "clears_gate"]


def _frozen_record() -> dict:
    return json.loads(
        (_RESULTS / "stage4_frozen_ranking.json").read_text(encoding="utf-8")
    )


def frozen_ranking() -> pd.DataFrame:
    """Return the ranking exactly as frozen before the enrichment test."""
    return pd.read_csv(
        StringIO(_frozen_record()["frozen_ranking_csv"]), float_precision="round_trip"
    )


def full_ranking() -> pd.DataFrame:
    """Return stage-3 scores and geometry, including structure-derived c0."""
    return pd.read_csv(_RESULTS / "stage3_ranking.csv")


def prereg_go_terms() -> set[str]:
    """Return the label set stored in the pre-registration record."""
    return set(_frozen_record()["label_go_terms"])


def verify_frozen_ranking() -> dict:
    """Check both saved ranking representations against the original hash.

    Use the same default pandas float parsing as stage4_enrichment.freeze_ranking
    and explicit Unix newlines to reproduce its serialization on Windows.
    """
    record = _frozen_record()
    stage3_csv = full_ranking()[_RANKING_COLUMNS].to_csv(
        index=False, lineterminator="\n"
    )
    frozen_hash = hashlib.sha256(record["frozen_ranking_csv"].encode()).hexdigest()[:16]
    stage3_hash = hashlib.sha256(stage3_csv.encode()).hexdigest()[:16]
    return {
        "stored_hash": record["rank_hash"],
        "hash_from_frozen_csv": frozen_hash,
        "hash_from_stage3_csv": stage3_hash,
        "passed": frozen_hash == stage3_hash == record["rank_hash"],
    }


def verify_energy_scale_consistency() -> dict:
    """Check the screen's thermal energy and bending modulus against curvo."""
    from .src import stage0_energy_scale

    thermal_energy_matches = abs(stage0_energy_scale.KBT_J - KBT_J) <= KBT_J * 1e-12
    bending_modulus_matches = stage0_energy_scale.KAPPA_KBT == KAPPA_KBT_DEFAULT
    return {
        "thermal_energy_matches": thermal_energy_matches,
        "bending_modulus_matches": bending_modulus_matches,
        "consistent": thermal_energy_matches and bending_modulus_matches,
    }
