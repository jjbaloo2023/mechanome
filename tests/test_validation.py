"""Contract tests for the real-data validation modules.

The tether test runs offline (closed-form + inversion). The MDDB test needs
network and is skipped gracefully when the API is unreachable.
"""
import numpy as np

from validation import tether_sted as ts


def test_tether_forward_reproduces_paper_regime():
    # the paper's reported ~72 nm tube must map into the aspiration range 15-140 uN/m
    R, f = ts.tube_forward(36.0)          # ~ mid-range tension
    assert 30 <= 2 * R <= 90, f"diameter {2*R:.0f} nm out of paper regime"
    assert 5 <= f <= 40, f"force {f:.1f} pN implausible for a lipid tether"


def test_tether_inverse_recovers_force_calibrated():
    res = ts.validate(tensions_uN_m=(40, 100), n_noise=60, seed=1)
    s = res["summary"]
    # forces recovered near-unbiased and CIs at least nominal (conservative is fine)
    assert s["mean_abs_rel_bias"] < 0.12, s
    assert s["overall_coverage68"] >= 0.68, s
    assert res["doi"] == "10.1021/acs.nanolett.9b05232"


def test_tether_inverse_single_radius_ci_brackets_truth():
    R_true, f_true = ts.tube_forward(72.0)
    out = ts.invert_radius(R_true)        # noiseless radius -> CI must bracket truth
    assert out["f_lo"] <= f_true <= out["f_hi"], (out, f_true)


def test_mddb_adapter_optional():
    from validation import mddb_adapter as md
    if not md.api_online():
        print("SKIP: MDDB API unreachable"); return
    cc = md.crosscheck_thickness("A020P")
    o = cc["md_observable"]
    assert o["units"] == "nm" and o["n_frames"] > 0
    assert o["provenance"]["source"] == "MDDB"
    assert "z_vs_md_fluctuation" in cc


if __name__ == "__main__":
    import traceback
    tests = [test_tether_forward_reproduces_paper_regime,
             test_tether_inverse_recovers_force_calibrated,
             test_tether_inverse_single_radius_ci_brackets_truth,
             test_mddb_adapter_optional]
    npass = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__); npass += 1
        except Exception:
            print("FAIL", t.__name__); traceback.print_exc()
    print(f"\n{npass}/{len(tests)} validation tests pass")
