"""Guard static-fit observation boundaries without running an inverse fit."""
from types import SimpleNamespace

import numpy as np
import pytest

from validation.realdata import smlm_mechanism as mechanism
from validation.realdata import smlm_shape_energetics as energetics
from validation.realdata.smlm_pseudotime import sort_by_pseudotime


class Geometry:
    def __init__(self):
        theta = np.linspace(10, 170, 108)
        curvature = mechanism.H_coopcm(theta, 0.013, 0.01)
        area, _ = mechanism._cap_from_H(theta, curvature)
        self.values = dict(theta_deg=theta, H_inv_nm=curvature,
                           R_nm=1/curvature, surface_area_nm2=area)
        self.sites = [None] * len(theta)
        self.cell_lines = ['fixture']
        # Caller-supplied assertions must not grant calibrated permission.
        self.provenance = dict(calibrated_likelihood=True,
                               mechanism_inference_allowed=True,
                               h_sigma_status='unknown', geometry='raw_nonnegative')

    def arr(self, field):
        return self.values[field]


@pytest.mark.parametrize('entry', ['shape', 'curvature', 'transforms'])
def test_static_fits_refuse_before_data_or_sampler(entry, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Default refusal must happen before observation conversion or fitting')

    monkeypatch.setattr(energetics, '_trajectory_to_obs', forbidden)
    monkeypatch.setattr(mechanism, '_fit', forbidden)
    monkeypatch.setattr(mechanism, '_fit_H_only', forbidden)
    untrusted = SimpleNamespace(provenance={'calibrated_likelihood': True})
    with pytest.raises(ValueError, match='allow_exploratory=True'):
        if entry == 'shape':
            energetics.fit_shape_energetics(untrusted, 50000)
        elif entry == 'curvature':
            mechanism.discriminate(untrusted)
        else:
            mechanism.discriminate_multiobservable(untrusted)


def test_large_conditional_score_cannot_become_a_mechanism_verdict(monkeypatch):
    def fake_fit(fn, *args, **kwargs):
        score = 100.0 if fn is mechanism.H_coopcm else 0.0
        return score, dict(H0=0.013, gamma=0.01, scatter=0.001)

    monkeypatch.setattr(mechanism, '_fit', fake_fit)
    result = mechanism.discriminate(Geometry(), allow_exploratory=True)
    assert result.lnB_coopcm_vs_helfrich == 100
    assert result.favored == 'coopcm'
    assert result.decisive is False
    assert result.provenance['exploratory_threshold_exceeded'] is True
    assert result.provenance['calibrated_likelihood'] is False
    assert result.provenance['mechanism_inference_allowed'] is False
    assert 'does not identify a mechanism' in result.verdict


def test_transformed_score_labels_follow_actual_preference(monkeypatch):
    monkeypatch.setattr(mechanism, '_fit_H_only',
                        lambda *args, **kwargs: dict(H0=0.013, gamma=0.01, scatter=0.001))
    result = mechanism.discriminate_multiobservable(Geometry(), allow_exploratory=True)
    assert result.favored == 'coopcm'
    assert 'prefers coopcm' in result.verdict
    assert 'not independent held-out evidence' in result.verdict
    assert result.provenance['mechanism_inference_allowed'] is False
    assert result.provenance['calibrated_likelihood'] is False


def test_population_summary_preserves_provenance_without_trajectory_claim():
    result = sort_by_pseudotime(Geometry())
    assert result.provenance['h_sigma_status'] == 'unknown'
    assert result.provenance['geometry'] == 'raw_nonnegative'
    assert result.provenance['within_pit_trajectory'] is False
    assert result.provenance['calibrated_likelihood'] is False
    assert result.provenance['mechanism_inference_allowed'] is False
    assert result.n_sites == 108
    assert np.isfinite(result.H_median).all()


def test_shape_optin_keeps_posterior_conditional(monkeypatch):
    calls = []

    def fake_nested(H, sigma, area, **kwargs):
        calls.append((H, sigma, area))
        return dict(samples=np.zeros((2, 1)), params=['c_eff_max'], logz=1.0)

    monkeypatch.setattr(energetics.inv, 'run_nested', fake_nested)
    monkeypatch.setattr(energetics.inv, 'identifiability',
                        lambda *args: {'c_eff_max': {'median': 0.01, 'ci68': [0.005, 0.02]}})
    result = energetics.fit_shape_energetics(
        sort_by_pseudotime(Geometry()), 50000, allow_exploratory=True)
    assert len(calls) == 1
    assert np.isfinite(calls[0][1]).all()
    assert result.absolute_force_reported is None
    assert result.provenance['calibrated_likelihood'] is False
    assert result.provenance['mechanism_inference_allowed'] is False
    assert 'arbitrary floor' in result.provenance['uncertainty_model']
    assert result.provenance['analysis_scope'] == 'exploratory surrogate diagnostics'
