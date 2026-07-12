"""
channel module -- mechanosensitive gating (MscL / Piezo-type).

Governing law. Two-state Boltzmann gating driven by membrane tension sigma:
    Po(sigma) = 1 / (1 + exp(-(sigma*dA - dG)/kBT)),
where dA is the in-plane gating-area change and dG the intrinsic (zero-tension)
free-energy difference. Midpoint sigma_half = dG/dA; slope at midpoint
dPo/dsigma = dA/(4 kBT).

Units: tension sigma in mN/m (= pN/nm), area dA in nm^2, energy in kBT.
Convenient identity: sigma[pN/nm] * dA[nm^2] = energy in pN*nm; divide by
kBT = 4.114 pN*nm to get kBT units. (1 mN/m = 1 pN/nm exactly.)

Analytic limit. Recover dA and sigma_half from a synthetic Po-tension sigmoid to
<2%; verify slope at midpoint = dA/(4 kBT).

Applicable validation data. MscL patch-clamp Po(sigma) -- Sukharev et al. 1999,
J Gen Physiol 113:525-540 (doi:10.1085/jgp.113.4.525): midpoint T_half = 11.8
dyn/cm (=11.8 mN/m), max slope 0.63 dyn/cm per e-fold, dE = 18.6 kBT unstressed,
gating area dA = 6.5 nm^2 (two-state analysis) -- all quoted from the paper.
Anchor: reproduce the MscL sigmoid at dA=6.5 nm^2, sigma_half=11.8 mN/m and
round-trip those parameters.

Coupling to curvo: the channel reads the membrane module's inferred tension
sigma directly (open_probability_at_curvo_tension), the one cross-scale link
grounded on both ends.

Validation tier: built_analytic.
"""
import numpy as np
from scipy.optimize import curve_fit

from curvo.constants import KBT_PN_NM   # single source of truth (curvo/constants.py)

# verified MscL anchor (Sukharev et al. 1999)
MSCL_SIGMA_HALF_mN_m = 11.8
MSCL_DA_nm2 = 6.5
VALIDATION_ANCHOR = "Sukharev et al. 1999 J Gen Physiol 113:525 (MscL: sigma_half=11.8 mN/m, dA=6.5 nm^2)"


def open_probability(sigma_mN_m, dA_nm2, dG_kBT):
    """Two-state Boltzmann open probability. sigma in mN/m (=pN/nm)."""
    sigma = np.asarray(sigma_mN_m, float)
    dE_kBT = (sigma * dA_nm2) / KBT_PN_NM - dG_kBT     # (sigma*dA)/kBT - dG
    return 1.0 / (1.0 + np.exp(-dE_kBT))


def midpoint_tension(dA_nm2, dG_kBT):
    """sigma_half = dG/dA, returned in mN/m. dG in kBT, dA in nm^2."""
    return (dG_kBT * KBT_PN_NM) / dA_nm2


def slope_at_midpoint(dA_nm2):
    """dPo/dsigma at the midpoint = dA/(4 kBT), in (mN/m)^-1."""
    return dA_nm2 / (4.0 * KBT_PN_NM)


def fit_gating(sigma_mN_m, Po):
    """Recover (dA, dG) from a Po-tension curve by nonlinear least squares."""
    p0 = [5.0, 10.0]
    popt, _ = curve_fit(open_probability, np.asarray(sigma_mN_m, float),
                        np.asarray(Po, float), p0=p0, maxfev=20000)
    return dict(dA_nm2=float(popt[0]), dG_kBT=float(popt[1]),
                sigma_half_mN_m=float(midpoint_tension(*popt)))


def open_probability_at_curvo_tension(sigma_kBT_nm2, dA_nm2=MSCL_DA_nm2, dG_kBT=None):
    """Cross-scale link: feed curvo's inferred membrane tension (in kBT/nm^2)
    into the channel open probability. Converts kBT/nm^2 -> mN/m via
    sigma[pN/nm] = sigma[kBT/nm^2] * kBT[pN*nm]/nm ... i.e. multiply by kBT.
    """
    if dG_kBT is None:
        dG_kBT = MSCL_SIGMA_HALF_mN_m * dA_nm2 / KBT_PN_NM   # so midpoint = 11.8 mN/m
    sigma_mN_m = np.asarray(sigma_kBT_nm2, float) * KBT_PN_NM  # kBT/nm^2 -> pN/nm = mN/m
    return float(open_probability(sigma_mN_m, dA_nm2, dG_kBT))


def self_validate():
    out = {}
    # true MscL params: dA=6.5 nm^2, midpoint 11.8 mN/m -> dG = sigma_half*dA/kBT
    dA_true = MSCL_DA_nm2
    dG_true = MSCL_SIGMA_HALF_mN_m * dA_true / KBT_PN_NM
    sigma = np.linspace(0, 25, 60)
    Po = open_probability(sigma, dA_true, dG_true)
    fit = fit_gating(sigma, Po)
    out["mscl"] = dict(dA_true=dA_true, dG_true=dG_true,
                       sigma_half_true=MSCL_SIGMA_HALF_mN_m, **fit,
                       dA_rel_err=abs(fit["dA_nm2"] - dA_true) / dA_true,
                       sigma_half_rel_err=abs(fit["sigma_half_mN_m"] - MSCL_SIGMA_HALF_mN_m)
                       / MSCL_SIGMA_HALF_mN_m)
    # slope identity check: numeric dPo/dsigma at midpoint vs dA/(4kBT)
    h = 1e-4
    num = (open_probability(MSCL_SIGMA_HALF_mN_m + h, dA_true, dG_true)
           - open_probability(MSCL_SIGMA_HALF_mN_m - h, dA_true, dG_true)) / (2 * h)
    ana = slope_at_midpoint(dA_true)
    out["slope_check"] = dict(numeric=float(num), analytic=float(ana),
                              rel_err=abs(num - ana) / ana)
    # cross-scale link sanity: at curvo tension = sigma_half/kBT, Po ~ 0.5
    sig_kBT = MSCL_SIGMA_HALF_mN_m / KBT_PN_NM
    out["curvo_link_Po_at_midpoint"] = open_probability_at_curvo_tension(sig_kBT)
    out["passed"] = bool(out["mscl"]["dA_rel_err"] < 0.02 and
                         out["mscl"]["sigma_half_rel_err"] < 0.02 and
                         out["slope_check"]["rel_err"] < 0.02 and
                         abs(out["curvo_link_Po_at_midpoint"] - 0.5) < 0.02)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(self_validate(), indent=2))
