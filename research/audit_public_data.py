"""Fetch and audit published fit tables without fitting or ranking mechanisms.

Run from the repository root: python research/audit_public_data.py
Raw files stay in the ignored cache; the small provenance report is retained.
"""

import csv
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np
import pandas as pd

BASE = "https://ftp.ebi.ac.uk/biostudies/fire/S-BIAD/566/S-BIAD566/Files/"
INDEX = "3_Model_Fit_Results - Tabellenblatt1.tsv"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache" / "smlm_locmofit" / "audit"
LIMIT = 10 * 1024 * 1024


def fetch(url):
    with urlopen(url, timeout=30) as response:
        content = response.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError("Audit input exceeds 10 MiB limit")
    return content


def audit_table(entry):
    relative = PurePosixPath(entry["Files"])
    if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".csv":
        raise ValueError("Unexpected manifest path")
    url = BASE + quote(str(relative))
    path = CACHE.joinpath(*relative.parts)
    content = path.read_bytes() if path.exists() else fetch(url)
    actual_md5 = hashlib.md5(content).hexdigest()
    if actual_md5.lower() != entry["md5"].lower():
        raise ValueError(f"Published checksum mismatch: {relative}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(content)
    table = pd.read_csv(io.BytesIO(content))
    required = {
        "ID",
        "cell_line",
        "file_number",
        "curvature",
        "radius",
        "theta",
        "surface_area",
        "projected_area",
        "disconnected_sites",
        "theta_corrected",
        "curvature_corrected",
    }
    if not required.issubset(table.columns):
        raise ValueError(f"Missing fields: {required - set(table.columns)}")
    numeric = table[
        ["curvature", "radius", "theta", "surface_area", "projected_area"]
    ].apply(pd.to_numeric, errors="coerce")
    disconnected = table["disconnected_sites"].astype(str).str.lower().eq("true")
    # Mirrors the current adapter's inclusion rule, not a newly endorsed filter.
    adapter_kept = (
        ~disconnected
        & np.isfinite(numeric.curvature)
        & np.isfinite(numeric.theta)
        & (numeric.curvature >= 0)
    )
    threshold = table.cell_line.map({"SKMEL2": 0.016, "U2OS": 0.013, "3T3": 0.014})
    return {
        "path": str(relative),
        "url": url,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "published_md5": entry["md5"],
        "md5_verified": True,
        "rows": len(table),
        "cell_lines": sorted(table.cell_line.astype(str).unique().tolist()),
        "file_numbers": sorted(table.file_number.dropna().unique().tolist()),
        "columns": table.columns.tolist(),
        "disconnected_values": table.disconnected_sites.astype(str)
        .value_counts()
        .to_dict(),
        "flagged_disconnected": int(disconnected.sum()),
        "current_adapter_kept": int(adapter_kept.sum()),
        "negative_curvature": int((numeric.curvature < 0).sum()),
        "corrected_curvature_changes": int(
            (table.curvature != table.curvature_corrected).sum()
        ),
        "corrected_theta_changes": int((table.theta != table.theta_corrected).sum()),
        "flag_threshold_disagreements": int(
            ((numeric.curvature > threshold) != disconnected).sum()
        ),
        "zero_curvature": int((numeric.curvature == 0).sum()),
        "nonfinite_rows": int((~np.isfinite(numeric)).any(axis=1).sum()),
        "nonfinite_kept_rows": int(
            ((~np.isfinite(numeric)).any(axis=1) & adapter_kept).sum()
        ),
        "duplicate_site_keys": int(
            table.duplicated(["cell_line", "file_number", "ID"]).sum()
        ),
        "theta_range_deg": [float(numeric.theta.min()), float(numeric.theta.max())],
    }


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest_url = BASE + quote(INDEX)
    manifest = fetch(manifest_url)
    (CACHE / "manifest.tsv").write_bytes(manifest)
    entries = list(
        csv.DictReader(io.StringIO(manifest.decode("utf-8-sig")), delimiter="\t")
    )
    with ThreadPoolExecutor(max_workers=4) as pool:
        tables = list(pool.map(audit_table, entries))
    groups = {}
    for table in tables:
        for line in table["cell_lines"]:
            group = groups.setdefault(
                line,
                {
                    "tables": 0,
                    "rows": 0,
                    "current_adapter_kept": 0,
                    "flagged_disconnected": 0,
                },
            )
            for key in group:
                group[key] += 1 if key == "tables" else table[key]
    report = {
        "dataset": "S-BIAD566",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "manifest": {
            "url": manifest_url,
            "sha256": hashlib.sha256(manifest).hexdigest(),
        },
        "scope": "Published processed fit tables, not raw localization data; no model fitting",
        "dataset_license": "not independently verified; article CC BY 4.0 is not assumed to license every deposit",
        "tables": tables,
        "by_cell_line": groups,
        "total_rows": sum(t["rows"] for t in tables),
        "total_bytes": sum(t["bytes"] for t in tables),
        "cell_independence": "Per-file grouping retained; experimental replicate structure still requires metadata audit",
    }
    output = ROOT / "research" / "data_audit.json"
    output.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "tables": len(tables),
                "total_rows": report["total_rows"],
                "total_bytes": report["total_bytes"],
                "by_cell_line": groups,
            }
        )
    )


if __name__ == "__main__":
    main()
