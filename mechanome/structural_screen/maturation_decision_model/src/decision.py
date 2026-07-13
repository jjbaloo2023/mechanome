"""
decision.py -- barrier -> maturation-decision probability (the NEW layer).

A coated pit sitting in its metastable resting-dome minimum (barrier.py) has two
escape routes:
    FORWARD  over dE_commit  -> committed / productive vesicle
    BACKWARD over dE_abort   -> disassembled / abortive pit

Two mappings are provided; both expose 1-2 free parameters and NOTHING else
(all membrane/steric physics is fixed upstream in barrier.py + curvature_sources.py).

(A) competing-barrier Kramers (physically principled, DEFAULT)
    Escape rate over a barrier ~ nu * exp(-dE/kBT) (Kramers/Arrhenius high-barrier).
    P(commit) = k_commit / (k_commit + k_abort)
              = 1 / (1 + (nu_ratio) * exp(-(dE_abort - dE_commit)/kBT))
              = 1 / (1 + nu_ratio * exp(-(dE_abort - dE_commit)))     [kBT units]
    Free parameter:
        log_nu_ratio = ln(nu_abort / nu_commit)   -- attempt-frequency asymmetry
        (commit needs neck constriction/fission machinery; abort is coat
         disassembly -- different prefactors). One free number, physically a
         prefactor ratio, NOT a re-fit of the energy.

(B) logistic-in-commit-barrier (the reduced form named in the spec)
    P(commit) = 1 / (1 + exp(+alpha * (dE_commit - dE_half)))
    Free parameters: alpha (barrier sensitivity, 1/kBT), dE_half (midpoint, kBT).

P(abort) = 1 - P(commit) in both. Feed dE_commit / dE_abort from barrier.barrier().
"""
from __future__ import annotations
import numpy as np


def p_commit_kramers(dE_commit, dE_abort, log_nu_ratio=0.0):
    """Competing-barrier Kramers commit probability. Free param: log_nu_ratio.
    log_nu_ratio>0 biases toward abort (abort attempts more frequent)."""
    dEc = np.asarray(dE_commit, float); dEa = np.asarray(dE_abort, float)
    # P = 1/(1 + exp(log_nu_ratio) * exp(-(dEa - dEc)))
    x = log_nu_ratio - (dEa - dEc)
    return 1.0 / (1.0 + np.exp(x))


def p_commit_logistic(dE_commit, alpha=0.05, dE_half=60.0):
    """Reduced logistic on the commit barrier alone. Free params: alpha, dE_half."""
    dEc = np.asarray(dE_commit, float)
    return 1.0 / (1.0 + np.exp(alpha * (dEc - dE_half)))


def p_abort_kramers(dE_commit, dE_abort, log_nu_ratio=0.0):
    return 1.0 - p_commit_kramers(dE_commit, dE_abort, log_nu_ratio)


def p_abort_logistic(dE_commit, alpha=0.05, dE_half=60.0):
    return 1.0 - p_commit_logistic(dE_commit, alpha, dE_half)
