"""
bond module -- Bell / catch-slip molecular bond.

Governing law. Bell slip bond:
    k_off(F) = k0 * exp(F * x_dagger / kBT),   lifetime tau(F) = 1 / k_off(F).
Two-pathway catch-slip (Pereverzev et al. 2005, Biophys J 89:1446):
    k_off(F) = kc0 * exp(-F * xc / kBT) + ks0 * exp(F * xs / kBT),
a catch pathway (bond strengthens with force) plus a slip pathway, giving a
biphasic tau(F) with a lifetime peak.

Analytic limit. Pure slip: recover x_dagger and k0 from a synthetic
force-lifetime curve by linear fit of ln(1/tau)=ln(k0)+ (x_dagger/kBT) F, <2%.
Catch-slip: the lifetime-peak force has a closed form (dtau/dF=0).

Applicable validation data. Marshall et al. 2003, Nature 423:190 --
P-selectin/PSGL-1 catch-slip by AFM, biphasic lifetime peaking ~1.1 s near
~10-20 pN; the P-selectin-G1 slip control is pure Bell. Two-pathway analysis:
Pereverzev et al. 2005. Anchor: recover Bell x_dagger from a slip control and the
peak location from catch-slip parameters.

Forces in pN, lengths in nm, energies in kBT (kBT = 4.114 pN*nm at 24 C).

Validation tier: built_analytic.
"""
import numpy as np

from curvo.constants import KBT_PN_NM   # single source of truth (curvo/constants.py)

VALIDATION_ANCHOR = "Marshall et al. 2003 Nature 423:190 (P-selectin/PSGL-1 catch-slip, peak ~1.1 s)"


def koff_bell(F_pN, k0, x_dagger_nm):
    """Bell slip-bond off-rate (1/s)."""
    return k0 * np.exp(np.asarray(F_pN) * x_dagger_nm / KBT_PN_NM)


def lifetime_bell(F_pN, k0, x_dagger_nm):
    return 1.0 / koff_bell(F_pN, k0, x_dagger_nm)


def koff_catch_slip(F_pN, kc0, xc_nm, ks0, xs_nm):
    """Two-pathway catch-slip off-rate (1/s): catch term (- sign) + slip term."""
    F = np.asarray(F_pN, float)
    return kc0 * np.exp(-F * xc_nm / KBT_PN_NM) + ks0 * np.exp(F * xs_nm / KBT_PN_NM)


def lifetime_catch_slip(F_pN, kc0, xc_nm, ks0, xs_nm):
    return 1.0 / koff_catch_slip(F_pN, kc0, xc_nm, ks0, xs_nm)


def catch_slip_peak_force(kc0, xc_nm, ks0, xs_nm):
    """Force (pN) at maximum lifetime: solve d(koff)/dF = 0 in closed form.
        -kc0 xc exp(-F xc/kBT) + ks0 xs exp(F xs/kBT) = 0
        => F* = kBT/(xc+xs) * ln( kc0 xc / (ks0 xs) )
    """
    return KBT_PN_NM / (xc_nm + xs_nm) * np.log((kc0 * xc_nm) / (ks0 * xs_nm))


def fit_bell(F_pN, tau_s):
    """Recover (k0, x_dagger) from a force-lifetime curve by linear fit of
    ln(1/tau) vs F. Returns dict."""
    F = np.asarray(F_pN, float); y = np.log(1.0 / np.asarray(tau_s, float))
    slope, intercept = np.polyfit(F, y, 1)
    return dict(k0=float(np.exp(intercept)), x_dagger_nm=float(slope * KBT_PN_NM))


def self_validate():
    out = {}
    # (1) pure slip (Bell): generate a curve at known params, recover by fit
    k0_true, xd_true = 1.0, 0.4               # 1/s, nm
    F = np.linspace(0, 60, 25)
    tau = lifetime_bell(F, k0_true, xd_true)
    fit = fit_bell(F, tau)
    out["bell"] = dict(k0_true=k0_true, x_dagger_true=xd_true, **fit,
                       k0_rel_err=abs(fit["k0"] - k0_true) / k0_true,
                       xd_rel_err=abs(fit["x_dagger_nm"] - xd_true) / xd_true)
    # (2) catch-slip: analytic peak vs numeric argmax of lifetime
    kc0, xc, ks0, xs = 20.0, 0.30, 0.5, 0.35   # P-selectin-like (biphasic)
    F2 = np.linspace(0, 60, 6001)
    tau2 = lifetime_catch_slip(F2, kc0, xc, ks0, xs)
    F_peak_num = float(F2[np.argmax(tau2)])
    F_peak_ana = float(catch_slip_peak_force(kc0, xc, ks0, xs))
    out["catch_slip"] = dict(peak_force_analytic_pN=F_peak_ana,
                             peak_force_numeric_pN=F_peak_num,
                             peak_lifetime_s=float(tau2.max()),
                             peak_rel_err=abs(F_peak_ana - F_peak_num) / F_peak_num)
    out["passed"] = bool(out["bell"]["k0_rel_err"] < 0.02 and
                         out["bell"]["xd_rel_err"] < 0.02 and
                         out["catch_slip"]["peak_rel_err"] < 0.02)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(self_validate(), indent=2))
