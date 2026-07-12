"""
curvo/constants.py -- the single source of truth for shared physical constants.

Every module that needs the thermal energy scale or the default bilayer bending
modulus imports them from here, so there is exactly one definition of each in
the codebase (see also mechanome.structural_screen, whose vendored energy scale
is checked against these values at import).

Unit conventions (used throughout curvo and mechanome):
    force        pN
    length       nm
    energy       kBT   (thermal energy at 298 K)
    tension      kBT/nm^2  (equivalently pN/nm = mN/m, since 1 pN/nm = 1 mN/m)

Convenient identities:
    kBT = 4.114 pN*nm = 4.114 zJ   (298 K)
    1 mN/m = 1 pN/nm  (surface tension <-> line tension per unit length)
    sigma[pN/nm] * dA[nm^2] = energy in pN*nm; divide by KBT_PN_NM for kBT units.
"""
from __future__ import annotations

# Thermal energy at 298 K. In pN*nm this is numerically identical to zJ
# (1 pN*nm = 1 zJ = 1e-21 J), so KBT_PN_NM == kBT_zJ == 4.114.
KBT_PN_NM: float = 4.114
KBT_ZJ: float = KBT_PN_NM            # alias: zJ and pN*nm are the same number here
KBT_J: float = KBT_PN_NM * 1e-21     # in joules, for code working in SI

# Default bilayer bending modulus. A per-call parameter everywhere, but this is
# the canonical default used by the evaluator, the RL scaffold, and the
# structural screen.
KAPPA_KBT_DEFAULT: float = 20.0

# Default coat stiffening factor for the clathrin-coated-structure evaluator.
COAT_RIGIDITY_FACTOR_DEFAULT: float = 3.0
