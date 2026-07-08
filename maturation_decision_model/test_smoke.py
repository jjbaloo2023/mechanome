"""Smoke test: analytic limits + pre-registered prediction direction."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import barrier as B, curvature_sources as CS
from model import MaturationDecisionModel

def test_sphere_limit():
    assert abs(B.bending_energy(np.pi, 11310., 0.0, 20.0)/(8*np.pi*20.0) - 1) < 1e-6

def test_flat_zero():
    _, dE = B.energy_profile(11310., 0.05, B.mNm_to_kBT_per_nm2(0.02))
    assert abs(dE[0]) < 1e-9

def test_barrier_rises_with_tension():
    lo = B.barrier(11310., 0.05, B.mNm_to_kBT_per_nm2(0.005))["dE_commit"]
    hi = B.barrier(11310., 0.05, B.mNm_to_kBT_per_nm2(0.04))["dE_commit"]
    assert hi > lo

def test_steric_lowers_pabort():
    p = dict(decision="logistic", alpha=0.06, dE_half=55.0)
    wo = MaturationDecisionModel(CS.build_epsin_enth_only(), **p).p_abort_mNm(0.55, 0.038)
    w  = MaturationDecisionModel(CS.build_epsin_full(),      **p).p_abort_mNm(0.55, 0.038)
    assert w < wo   # steric term buffers

if __name__ == "__main__":
    for f in [test_sphere_limit, test_flat_zero, test_barrier_rises_with_tension, test_steric_lowers_pabort]:
        f(); print("PASS", f.__name__)
