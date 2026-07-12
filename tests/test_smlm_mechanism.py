"""Tests for SMLM mechanism discrimination (Helfrich vs CoopCM)."""
import os
import numpy as np
import pytest

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "cache", "smlm_locmofit")


def _have_data():
    import glob
    return bool(glob.glob(os.path.join(CACHE, "*.csv")))


needs_data = pytest.mark.skipif(
    not _have_data(), reason="SMLM LocMoFit CSVs not cached")


def test_rate_laws_analytic_limits():
    """Both curvature laws start at H=0 (theta=0) and saturate toward H0."""
    from validation.realdata.smlm_mechanism import H_helfrich, H_coopcm
    H0 = 0.013
    for fn in (H_helfrich, H_coopcm):
        assert abs(fn(0.0, H0, 0.01)) < 1e-9              # H(0) = 0
        assert fn(1e5, H0, 0.01) == pytest.approx(H0, rel=1e-3)   # saturates to H0
    # CoopCM (positive feedback) gives a FASTER initial curvature rise than the
    # non-cooperative linear relaxation: tanh(x)=x-x^3/3 exceeds 1-exp(-x)=x-x^2/2
    # for small x (the paper's "fast initial curvature increase").
    th = 20.0
    assert H_coopcm(th, H0, 0.01) > H_helfrich(th, H0, 0.01)


@needs_data
def test_discrimination_is_inconclusive_on_curvature_alone():
    """On H(theta) alone the two rate laws are near-identical: the Bayes factor
    must be non-decisive (|lnB| < 2.5), and the verdict must say so honestly
    rather than over-claim a mechanism the single observable cannot separate."""
    from validation.realdata.ingest_smlm_locmofit import ingest_locmofit
    from validation.realdata.smlm_mechanism import discriminate
    gs = ingest_locmofit()
    v = discriminate(gs.by_cell_line("SKMEL2"), nlive=250, seed=0)
    assert v.decisive is False
    assert abs(v.lnB_coopcm_vs_helfrich) < 2.5
    assert "INCONCLUSIVE" in v.verdict
    # both models must have finite, comparable evidence
    assert np.isfinite(v.logz["coopcm"]) and np.isfinite(v.logz["helfrich_linear"])
    # recovered preferred curvature is physical (mature CCV ~ 0.010-0.015 nm^-1)
    assert 0.008 < v.params["coopcm"]["H0"] < 0.020
