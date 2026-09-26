"""The public-data audit must reject altered cached inputs before parsing them."""

import hashlib

import pytest

from research import audit_public_data as audit


def test_corrupted_cached_table_is_not_silently_accepted(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "CACHE", tmp_path)
    (tmp_path / "cell.csv").write_bytes(b"altered")
    entry = {"Files": "cell.csv", "md5": hashlib.md5(b"original").hexdigest()}
    with pytest.raises(ValueError, match="checksum mismatch"):
        audit.audit_table(entry)


@pytest.mark.parametrize("path", ["../outside.csv", "/outside.csv", "cell.txt"])
def test_manifest_cannot_escape_cache(path):
    with pytest.raises(ValueError, match="manifest path"):
        audit.audit_table({"Files": path, "md5": "unused"})
