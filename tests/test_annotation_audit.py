"""Verify contracts that matter before using annotation tracks as evidence."""

import hashlib

import pytest

from research.audit_annotations import audit_table


def audit_text(tmp_path, text):
    path = tmp_path / "annotations.csv"
    data = text.encode()
    path.write_bytes(data)
    return audit_table(path, hashlib.sha256(data).hexdigest())


def test_tampered_input_is_rejected_before_parsing(tmp_path):
    path = tmp_path / "annotations.csv"
    path.write_text("not even a CSV")
    with pytest.raises(ValueError, match="checksum"):
        audit_table(path, "0" * 64)


def test_unordered_tracks_preserve_gaps_and_observed_boundaries(tmp_path):
    result = audit_text(
        tmp_path, "track_id,x,y,frame\n4,1,2,5\n4,1,2,2\n8,3,4,3\n4,1,2,3\n"
    )
    assert result["usable_for_tracking_audit"]
    assert result["track_count"] == 2
    assert result["tracks"][0]["missing_frames_inside_span"] == 1
    assert result["tracks"][0]["span_in_frame_indices"] == 3
    assert result["tracks_touching_first_observed_frame"] == 1
    assert result["tracks_touching_last_observed_frame"] == 1
    assert result["unobserved_frame_count_inside_range"] == 1


def test_duplicate_track_frames_block_contract_even_if_positions_match(tmp_path):
    result = audit_text(tmp_path, "track_id,x,y,frame\n0,1,2,0\n0,1,2,0\n0,3,2,0\n")
    assert not result["usable_for_tracking_audit"]
    assert result["duplicate_track_frame_rows"] == 2
    assert result["conflicting_track_frame_keys"] == 1


@pytest.mark.parametrize(
    "row",
    [
        "0,nan,2,0",
        "0,1,inf,0",
        "0,1,2,0.5",
        "-1,1,2,0",
        "0,1,2,-1",
        "0,1,2",
        "0,1,2,0,extra",
    ],
)
def test_invalid_coordinates_identifiers_and_rows_block_contract(tmp_path, row):
    result = audit_text(tmp_path, "track_id,x,y,frame\n" + row + "\n")
    assert result["invalid_rows"] == 1
    assert not result["usable_for_tracking_audit"]


def test_empty_table_is_not_usable(tmp_path):
    result = audit_text(tmp_path, "track_id,x,y,frame\n")
    assert not result["usable_for_tracking_audit"]
    assert result["frame_range"] is None


def test_extra_column_requires_a_new_schema_decision(tmp_path):
    with pytest.raises(ValueError, match="schema"):
        audit_text(tmp_path, "track_id,x,y,frame,condition\n0,1,2,0,control\n")
