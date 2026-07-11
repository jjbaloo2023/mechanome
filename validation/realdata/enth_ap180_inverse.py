"""
Inverse identifiability closure for the ENTH+AP180 construct.

enth_fusion_cases predicts ENTH+AP180-IDP reaches Omega at ~55 pN of actin force
(a stage/threshold call). This module CLOSES THE LOOP: it simulates the construct
forward at a KNOWN 55 pN, then inverts the noisy trajectory with the Bayesian
engine (dynesty nested sampling) and asks whether curvo recovers that force with
calibrated uncertainty -- or honestly refuses.

Two runs make the point:
  WITH the actin-density channel (which breaks the c_eff/force degeneracy):
      force IDENTIFIED at the true value, calibrated CI68.
  WITHOUT it:
      force degenerate with c_eff -> identifiability firewall REFUSES a point value.

This validates the engine + identifiability logic on self-consistent synthetic
data (calibration, degeneracy handling), not the real-imaging perception front
end. The active-force prior is widened to [0,120] pN so 55 pN is well inside the
box (the default 60 pN ceiling was tuned for a lower-force regime).
"""
import numpy as np

import curvo.synth_movie as sm
import curvo.inverse as inv

C_EFF_TRUE = 0.0485       # ENTH + AP180 IDP operating point (from enth_fusion_cases)
FORCE_TRUE = 55.0         # known actin force (pN) -- the recovery target
SIGMA_TRUE = 0.02
T = 24
H_NOISE = 0.010           # per-frame ratiometric curvature noise
ACTIN_NOISE = 0.05
A_COAT = np.pi * 60 ** 2

PARAMS = [inv.Param("c_eff_max", 0.0, 0.08, "nm^-1"),
          inv.Param("active_force_max", 0.0, 120.0, "pN"),   # widened past default 60
          inv.Param("sigma", 0.001, 0.05, "kBT/nm^2")]


def make_observation(seed=7):
    traj = sm.simulate_trajectory(sigma_kBT_nm2=SIGMA_TRUE, c_eff_max_inv_nm=C_EFF_TRUE,
                                  active_force_max_pN=FORCE_TRUE, kappa_kBT=20.0,
                                  coat_rigidity_factor=3.0, A_coat_nm2=A_COAT, T=T)
    rng = np.random.default_rng(seed)
    H_obs = traj["H"] + rng.normal(0, H_NOISE, T)
    cov = inv._coverage_ramp(T)
    actin_true = cov * (FORCE_TRUE / sm.ACTIN_CALIB_PN)
    actin_obs = actin_true + rng.normal(0, ACTIN_NOISE, T)
    return traj, H_obs, np.full(T, H_NOISE), actin_obs, np.full(T, ACTIN_NOISE)


def recover(H_obs, H_sigma, actin_obs=None, actin_sigma=None, nlive=300, seed=0):
    res = inv.run_nested(H_obs, H_sigma, A_COAT, params=PARAMS,
                         actin_obs=actin_obs, actin_sigma=actin_sigma,
                         nlive=nlive, seed=seed)
    return res, inv.identifiability(res["samples"], PARAMS)


if __name__ == "__main__":
    traj, H_obs, H_sig, a_obs, a_sig = make_observation()
    _, id_yes = recover(H_obs, H_sig, a_obs, a_sig)
    _, id_no = recover(H_obs, H_sig)
    fy, fn = id_yes["active_force_max"], id_no["active_force_max"]
    print(f"true force = {FORCE_TRUE} pN")
    print(f"  WITH actin channel:  med={fy['median']:.1f} CI68=[{fy['ci68'][0]:.1f},{fy['ci68'][1]:.1f}] "
          f"identified={fy['identified']}")
    print(f"  WITHOUT actin channel: med={fn['median']:.1f} CI68=[{fn['ci68'][0]:.1f},{fn['ci68'][1]:.1f}] "
          f"identified={fn['identified']} degenerate_with={[d['partner'] for d in fn['degenerate_with']]}")
