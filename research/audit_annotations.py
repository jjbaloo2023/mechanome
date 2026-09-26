"""Audit the saved Shape2Fate references without converting tracks into biology."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parents[1]
DATA = REPO.parent / "work" / "dynamic-annotations-001"
RETRIEVAL = REPO / "research/metadata/dynamic-annotations-001/retrieval.json"
# Frozen before this schema audit; changing inputs requires a versioned decision.
RETRIEVAL_SHA256 = "fd43634ae322e98850744d7a5c51238c05c0f67459ed8bc172a43d5aefb89902"
COLUMNS = ["track_id", "x", "y", "frame"]


def verified_bytes(path: Path, expected_sha256: str) -> bytes:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError(f"Input checksum mismatch: {path.name}")
    return data


def nonnegative_integer(text: str) -> int:
    text = text.strip()
    if not text.isascii() or not text.isdecimal():
        raise ValueError("Expected a nonnegative integer identifier/frame")
    return int(text)


def extent(values):
    return [min(values), max(values)] if values else None


def distribution(values):
    return (
        {"min": min(values), "median": median(values), "max": max(values)}
        if values
        else None
    )


def audit_table(path: Path, expected_sha256: str) -> dict:
    content = verified_bytes(path, expected_sha256)
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), strict=True)
    if reader.fieldnames != COLUMNS:
        raise ValueError(f"Unexpected annotation schema: {reader.fieldnames}")

    tracks = defaultdict(list)
    key_positions = defaultdict(set)
    key_counts = Counter()
    point_tracks = defaultdict(set)
    invalid_examples = []
    rows = invalid_rows = 0
    for row in reader:
        rows += 1
        try:
            if set(row) != set(COLUMNS) or any(value is None for value in row.values()):
                raise ValueError("Missing or surplus CSV fields")
            track, frame = nonnegative_integer(row["track_id"]), nonnegative_integer(
                row["frame"]
            )
            x, y = float(row["x"]), float(row["y"])
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Nonfinite coordinate")
        except (ValueError, TypeError) as error:
            invalid_rows += 1
            if len(invalid_examples) < 5:
                invalid_examples.append({"data_row": rows, "reason": str(error)})
            continue
        tracks[track].append((frame, x, y))
        key_counts[track, frame] += 1
        key_positions[track, frame].add((x, y))
        point_tracks[frame, x, y].add(track)

    observations = [point for points in tracks.values() for point in points]
    frame_counts = Counter(frame for frame, _, _ in observations)
    frame_range = extent(list(frame_counts))
    track_summaries = []
    for track, points in sorted(tracks.items()):
        frames = sorted({frame for frame, _, _ in points})
        jumps = [right - left for left, right in pairwise(frames)]
        track_summaries.append(
            {
                "track_id": track,
                "observations": len(points),
                "unique_frames": len(frames),
                "first_frame": frames[0],
                "last_frame": frames[-1],
                "span_in_frame_indices": frames[-1] - frames[0],
                "gap_intervals": sum(jump > 1 for jump in jumps),
                "missing_frames_inside_span": sum(jump - 1 for jump in jumps),
            }
        )
    duplicate_keys = sum(count - 1 for count in key_counts.values())
    usable = rows > 0 and invalid_rows == 0 and duplicate_keys == 0
    return {
        "file": path.name,
        "sha256": expected_sha256,
        "columns": reader.fieldnames,
        "rows": rows,
        "invalid_rows": invalid_rows,
        "invalid_row_examples": invalid_examples,
        "statistics_population": "structurally_valid_rows_only",
        "track_count": len(tracks),
        "duplicate_track_frame_rows": duplicate_keys,
        "conflicting_track_frame_keys": sum(
            len(positions) > 1 for positions in key_positions.values()
        ),
        "coordinate_frame_points_shared_by_tracks": sum(
            len(ids) > 1 for ids in point_tracks.values()
        ),
        "frame_range": frame_range,
        "observed_frame_count": len(frame_counts),
        "unobserved_frame_count_inside_range": (
            (frame_range[1] - frame_range[0] + 1 - len(frame_counts))
            if frame_range
            else None
        ),
        "observations_per_observed_frame": distribution(list(frame_counts.values())),
        "x_range": extent([x for _, x, _ in observations]),
        "y_range": extent([y for _, _, y in observations]),
        "negative_coordinate_rows": sum(x < 0 or y < 0 for _, x, y in observations),
        "track_observation_counts": distribution(
            [item["observations"] for item in track_summaries]
        ),
        "tracks_with_gaps": sum(item["gap_intervals"] > 0 for item in track_summaries),
        "tracks_touching_first_observed_frame": sum(
            item["first_frame"] == frame_range[0] for item in track_summaries
        ),
        "tracks_touching_last_observed_frame": sum(
            item["last_frame"] == frame_range[1] for item in track_summaries
        ),
        "usable_for_tracking_audit": usable,
        "tracks": track_summaries,
    }


def main():
    output = REPO / "research/annotation_audit.json"
    if output.exists():
        raise FileExistsError("Preserve the completed audit; version any new analysis")
    record = json.loads(verified_bytes(RETRIEVAL, RETRIEVAL_SHA256))
    expected_names = {f"annotations_{index}.csv" for index in (1, 2, 3)}
    members = record["members"]
    if len(members) != 3 or {item["saved_as"] for item in members} != expected_names:
        raise ValueError("Unexpected member list")
    tables = [audit_table(DATA / item["saved_as"], item["sha256"]) for item in members]
    result = {
        "task_id": "dynamic-annotations-001",
        "attempt_number": 1,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "retrieval_sha256": RETRIEVAL_SHA256,
        "implementation_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "source_url": record["url"],
        "execution_status": "completed",
        "data_contract_status": (
            "usable_for_tracking_audit_only"
            if all(item["usable_for_tracking_audit"] for item in tables)
            else "requires_data_resolution"
        ),
        "units": {
            "time": "frame_index",
            "position": "image_coordinates_physical_scale_unverified",
        },
        "identity_scope": "track_id is local to each annotation file; no cross-file identity assumed",
        "limitations": [
            "One movie, three references, not biological replicates",
            "Observed endpoints are not established initiation or scission events",
            "No intensity, axial geometry, perturbation or productive-event fields",
            "No calibrated physical scale, time interval or annotation uncertainty",
            "No inter-reference agreement comparison performed",
        ],
        "tables": tables,
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(
        json.dumps(
            {
                "status": result["data_contract_status"],
                "tables": [
                    {key: value for key, value in item.items() if key != "tracks"}
                    for item in tables
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
