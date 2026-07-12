"""Tests for the SMLM shape-energetics path: force MUST be refused."""
import os
import numpy as np
import pytest

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "cache", "smlm_locmofit")


def _have_data():
    import glob
    return bool(glob.glob(os.path.join(CACHE, "*.csv")))


needs_data = pytest.mark.skipif(
    not _have_data(),
    reason="SMLM LocMoFit CSVs not cached; run fetch_locmofit_fits()")


def test_ingest_sets_force_not_applicable():
    """A static SMLM geometry set carries force_applicable=False, unconditionally."""
    from validation.realdata.ingest_smlm_locmofit import SMLMGeometrySet
    gs = SMLMGeometrySet(sites=[], cell_lines=[])
    assert gs.force_applicable is False
    assert gs.observable == "4_static_superres_geometry"


@needs_data
def test_pseudotime_reproduces_flat_then_bend():
    """Sorting by theta recovers the paper's flat-lattice-then-bend geometry:
    a substantial flat-area fraction A0 and a finite bend onset."""
    from validation.realdata.ingest_smlm_locmofit import ingest_locmofit
    from validation.realdata.smlm_pseudotime import sort_by_pseudotime
    gs = ingest_locmofit()
    tr = sort_by_pseudotime(gs.by_cell_line("SKMEL2"))
    assert 0.2 < tr.A0_flat_fraction < 0.7          # ~half the coat assembles flat
    assert 0 < tr.theta_bend_onset_deg < 90
    # curvature must be monotone-ish increasing with pseudotime
    H = np.array(tr.H_median)
    assert H[-1] > H[0]


@needs_data
def test_shape_energetics_refuses_absolute_force():
    """The SMLM inverse must REFUSE absolute force by construction, and never
    return a force point estimate, regardless of posterior shape."""
    from validation.realdata.ingest_smlm_locmofit import ingest_locmofit
    from validation.realdata.smlm_pseudotime import sort_by_pseudotime
    from validation.realdata.smlm_shape_energetics import fit_shape_energetics
    gs = ingest_locmofit()
    gcl = gs.by_cell_line("SKMEL2")
    tr = sort_by_pseudotime(gcl)
    A = float(np.median(gcl.arr("surface_area_nm2")))
    r = fit_shape_energetics(tr, A, nlive=150, seed=0)
    # THE firewall assertions:
    assert r.force_applicable is False
    assert r.absolute_force_reported is None
    assert "underdetermined" in r.refusal_reason
    # active force must be flagged not-identified (railed or degenerate)
    af = r.identifiability["active_force_max"]
    assert af["identified"] is False
    # a shape c_eff IS reported (geometry is what SMLM constrains)
    assert r.c_eff_shape_inv_nm > 0
