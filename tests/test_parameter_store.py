"""Parameter sources must preserve data identity and expose missing adapters."""

import json
import hashlib

import pytest
import requests

from curvo import parameter_store as store


def response(values, status=200):
    result = requests.Response()
    result.status_code, result.url = status, "https://example.test/apl.json"
    result._content = json.dumps(values).encode()
    return result


@pytest.mark.parametrize("simulation", [store._DEFAULT_SIM, "custom"])
def test_cache_preserves_source_and_survives_http_failure(
    tmp_path, monkeypatch, simulation
):
    values = [[i, 60.0 + i] for i in range(5)]
    reply = response(values)
    monkeypatch.setattr(store.requests, "get", lambda *a, **kw: reply)
    live = store.nmrlipids_area_per_lipid(simulation, cache_dir=tmp_path)
    assert live.value == 0.625
    assert live.provenance.access == "live_api"
    assert live.provenance.identifier == simulation
    default = simulation == store._DEFAULT_SIM
    assert live.state_point.composition == ("POPC:CHOL 120:8" if default else "POPC")
    assert live.state_point.temperature_K == (303 if default else None)
    assert live.flags == (
        ["example_mixed_bilayer"] if default else ["simulation_metadata_unverified"]
    )
    assert live.valid_range == {}
    reply.status_code = 503
    cached = store.nmrlipids_area_per_lipid(simulation, cache_dir=tmp_path)
    assert cached.provenance.access == "cached"
    assert cached.value == live.value
    assert cached.provenance.identifier == simulation
    assert json.loads(next(tmp_path.glob("*.json")).read_text()) ["data"] == values
    other = "custom" if default else store._DEFAULT_SIM
    with pytest.raises(requests.HTTPError):
        store.nmrlipids_area_per_lipid(other, cache_dir=tmp_path)


@pytest.mark.parametrize("values", [[], [[0]], [[0, -1]], [[0, float("nan")]]])
def test_invalid_data_cannot_replace_a_valid_cache(tmp_path, monkeypatch, values):
    cache = tmp_path / f"nmrlipids_apl_{hashlib.sha256(store._DEFAULT_SIM.encode()).hexdigest()}.json"
    cache.write_text("[[0, 60.0]]")
    monkeypatch.setattr(store.requests, "get", lambda *a, **kw: response(values))
    with pytest.raises(ValueError, match="area-per-lipid data"):
        store.nmrlipids_area_per_lipid(cache_dir=tmp_path)
    assert cache.read_text() == "[[0, 60.0]]"


def test_adapter_bugs_are_not_hidden_by_cache(tmp_path, monkeypatch):
    (tmp_path / f"nmrlipids_apl_{hashlib.sha256(store._DEFAULT_SIM.encode()).hexdigest()}.json").write_text("[[0, 60.0]]")

    def broken_adapter(*args, **kwargs):
        raise RuntimeError("adapter bug")

    monkeypatch.setattr(store.requests, "get", broken_adapter)
    with pytest.raises(RuntimeError, match="adapter bug"):
        store.nmrlipids_area_per_lipid(cache_dir=tmp_path)


def test_missing_sources_and_unsupported_lipids_fail_explicitly(tmp_path, monkeypatch):
    parameters = store.ParameterStore()
    with pytest.raises(KeyError, match="scaffold_deformation"):
        parameters.get("scaffold_deformation", "ENTH")
    assert not parameters.records
    with pytest.raises(ValueError, match="cannot relabel"):
        store.nmrlipids_area_per_lipid(cache_dir=tmp_path, lipid="DOPE")
    monkeypatch.setattr(
        store,
        "nmrlipids_area_per_lipid",
        lambda **kw: store.literature("kappa", "POPC"),
    )
    row = next(
        row for row in parameters.coverage() if row["param"] == "scaffold_deformation"
    )
    assert row["access"] == "missing"
    assert row["value"] is None
