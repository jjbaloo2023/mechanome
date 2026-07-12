"""
cortex module -- active-gel cortical tension via Young-Laplace.

Governing law: Laplace pressure jump across the actomyosin cortex,
  dP = 2 gamma / R,
with cortical tension gamma set by myosin activity. Micropipette critical-
pressure form (hemispherical projection, aspiration radius R_p, cell radius R_c):
  gamma = P_c / [ 2 (1/R_p - 1/R_c) ].

Analytic limit: given gamma and R, predict dP and re-solve for gamma (<1%);
recover gamma from a synthetic (P_c, R_p, R_c) micropipette measurement.

Applicable validation data: micropipette aspiration cortical tension --
Tinevez et al. 2009 PNAS 106(44):18581; Hochmuth 2000 J Biomech 33:15. Reported
magnitudes gamma ~ 0.03-1 mN/m (neutrophil ~0.03; mitotic cells up to ~1).
Anchor here: recover gamma in this range from the Laplace balance.

Validation tier: built_analytic.
"""
import numpy as np

VALIDATION_ANCHOR = "Tinevez et al. 2009 PNAS 106:18581 (micropipette cortical tension 0.03-1 mN/m)"


def laplace_pressure(gamma_mN_m, R_um):
    """dP (Pa) = 2 gamma / R. gamma in mN/m (=mJ/m^2), R in micrometres."""
    gamma_SI = gamma_mN_m * 1e-3            # N/m
    R_SI = R_um * 1e-6                      # m
    return 2.0 * gamma_SI / R_SI            # Pa


def tension_from_laplace(dP_Pa, R_um):
    """Invert dP = 2 gamma / R for gamma (mN/m)."""
    R_SI = R_um * 1e-6
    gamma_SI = dP_Pa * R_SI / 2.0
    return gamma_SI * 1e3                   # mN/m


def tension_from_micropipette(Pc_Pa, Rp_um, Rc_um):
    """Cortical tension from micropipette critical aspiration pressure.

    gamma = P_c / [ 2 (1/R_p - 1/R_c) ]  (Laplace law of a liquid drop; the
    projection just clears the pipette at the critical pressure). Returns mN/m.
    """
    Rp, Rc = Rp_um * 1e-6, Rc_um * 1e-6
    gamma_SI = Pc_Pa / (2.0 * (1.0 / Rp - 1.0 / Rc))
    return gamma_SI * 1e3


def self_validate():
    out = {}
    # (1) round-trip gamma -> dP -> gamma over the reported range
    for g in (0.03, 0.3, 1.0):
        dP = laplace_pressure(g, R_um=5.0)
        g_rec = tension_from_laplace(dP, R_um=5.0)
        out[f"roundtrip_gamma_{g}"] = dict(dP_Pa=dP, gamma_rec=g_rec,
                                           rel_err=abs(g_rec - g) / g)
    out["roundtrip_max_rel_err"] = max(v["rel_err"] for k, v in out.items()
                                       if k.startswith("roundtrip"))
    # (2) synthetic micropipette recovery: assume a true gamma, generate Pc, recover
    gamma_true = 0.4                        # mN/m (mitotic-ish)
    Rp, Rc = 2.5, 7.5                       # um
    Pc = 2.0 * (gamma_true * 1e-3) * (1.0 / (Rp * 1e-6) - 1.0 / (Rc * 1e-6))  # Pa
    gamma_rec = tension_from_micropipette(Pc, Rp, Rc)
    out["micropipette"] = dict(gamma_true=gamma_true, Pc_Pa=Pc, gamma_rec=gamma_rec,
                               rel_err=abs(gamma_rec - gamma_true) / gamma_true)
    out["passed"] = bool(out["roundtrip_max_rel_err"] < 0.01 and
                         out["micropipette"]["rel_err"] < 0.01)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(self_validate(), indent=2))
