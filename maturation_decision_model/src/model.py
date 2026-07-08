"""
model.py -- MaturationDecisionModel facade: wires barrier + curvature registry
+ decision layer into one object.

    model = MaturationDecisionModel(registry, A_coat=..., kappa=..., decision="logistic", **params)
    model.barrier(phi, sigma)     -> dict from barrier.barrier() at C0_eff(phi,sigma)
    model.p_abort(phi, sigma)     -> population abort probability
    model.p_commit(phi, sigma)    -> 1 - p_abort

Tension may be given in kBT/nm^2 (native) or, via .from_mNm helpers, in mN/m.
Everything physical is fixed upstream; the model's ONLY free numbers are the
decision-layer parameters (see decision.py).
"""
from __future__ import annotations
import numpy as np
import barrier as _B
import decision as _D


class MaturationDecisionModel:
    def __init__(self, registry, A_coat=11310.0, kappa=20.0,
                 decision="logistic", **decision_params):
        self.registry = registry
        self.A_coat = float(A_coat)
        self.kappa = float(kappa)
        self.decision = decision
        self.decision_params = decision_params

    # ---- energetics ----
    def c0_eff(self, phi, sigma):
        return float(self.registry.c0_eff(phi, sigma))

    def barrier(self, phi, sigma):
        c0 = self.registry.c0_eff(phi, sigma)
        return _B.barrier(self.A_coat, float(c0), float(sigma), kappa=self.kappa)

    # ---- decision ----
    def p_commit(self, phi, sigma):
        b = self.barrier(phi, sigma)
        if self.decision == "kramers":
            return float(_D.p_commit_kramers(b["dE_commit"], b["dE_abort"],
                          self.decision_params.get("log_nu_ratio", 0.0)))
        return float(_D.p_commit_logistic(b["dE_commit"],
                      self.decision_params.get("alpha", 0.08),
                      self.decision_params.get("dE_half", 60.0)))

    def p_abort(self, phi, sigma):
        return 1.0 - self.p_commit(phi, sigma)

    # ---- convenience: tension in mN/m ----
    def p_abort_mNm(self, phi, sigma_mNm):
        return self.p_abort(phi, _B.mNm_to_kBT_per_nm2(sigma_mNm))

    def barrier_mNm(self, phi, sigma_mNm):
        return self.barrier(phi, _B.mNm_to_kBT_per_nm2(sigma_mNm))
