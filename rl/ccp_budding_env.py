"""
CCPBuddingEnv -- a Gymnasium RL environment over curvo's forward model.

An episode is a single clathrin-coated-pit budding attempt. Each step the agent
picks ONE orchestration move (recruit a curvature player, ramp actin force,
stiffen the coat, or wait). curvo's validated forward model (ccs_curvature) maps
the accumulated molecular state to an achieved membrane curvature and a
dome/Omega stage. The reward pays for curvature progress toward scission and
charges for the physical cost of force and recruitment -- so a good policy learns
the biologically sensible orchestration ORDER (coat -> crowding -> actin), which
is exactly the PICALM/epsin ladder curvo established from data.

The environment is a scaling scaffold: the physics lives entirely in curvo's
forward model, and the environment exposes it as a sequential decision problem an
agent can search. No new physics is introduced here.

State (Box, float32, 7-d):
    [coverage, c_eff, H, dome_omega_OP, actin_force_pN/ACTIN_MAX,
     coat_rf/COAT_RF_MAX, step/T]
Actions (Discrete 5):
    0 recruit wedge (ENTH/ANTH H0)       -> +c_eff, small cost
    1 recruit crowding partner (IDP)     -> +c_eff, small cost
    2 ramp actin force                   -> +actin_force, force cost
    3 stiffen clathrin coat              -> +coat_rigidity_factor (one-shot), cost
    4 wait                               -> no move, small time cost
Reward:
    dense: + curvature progress toward the Omega threshold, - move cost
    terminal: + BONUS for a productive pit (stage Omega before T), - penalty for
              stalling (no Omega by T) or over-forcing (rupture above F_RUPTURE)
"""
from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from curvo.evaluator_tier0 import ccs_curvature
from curvo.constants import KAPPA_KBT_DEFAULT as KAPPA_KBT   # single source of truth

# --- physical constants (shared with the realdata test cases) ----------------
SIGMA_KBT_NM2 = 0.02
A_COAT_NM2 = np.pi * 60.0 ** 2
OMEGA_OP = 0.66             # dome/Omega order-parameter threshold for scission
OMEGA_H = 0.030            # achieved-curvature threshold (nm^-1), for reference

# --- action effects ----------------------------------------------------------
DC_WEDGE = 0.010           # c_eff increment from a wedge player (tension-gated H0)
DC_CROWD = 0.0125          # c_eff increment from a crowding IDP brush
DACTIN = 20.0              # pN per actin ramp
DCOAT = 2.0                # coat rigidity factor increment (one-shot, capped)
C_EFF_MAX = 0.08
ACTIN_MAX = 120.0
F_RUPTURE = 140.0          # over-forcing above this ruptures the pit
COAT_RF_MAX = 3.0

# --- reward weights ----------------------------------------------------------
W_PROGRESS = 12.0          # per-unit dome_omega_OP gain
COST_RECRUIT = 0.15
COST_ACTIN = 0.02          # per pN ramped
COST_COAT = 0.2
COST_WAIT = 0.05
BONUS_PRODUCTIVE = 10.0
PENALTY_STALL = 3.0
PENALTY_RUPTURE = 8.0


_FORWARD_CACHE: dict = {}   # memoizes ccs_curvature over the reachable state grid


class CCPBuddingEnv(gym.Env):
    """Gymnasium env: orchestrate a productive clathrin-coated pit."""

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, T: int = 12, seed: int | None = None):
        super().__init__()
        self.T = int(T)
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0], np.float32),
            high=np.array([1, C_EFF_MAX, 0.08, 1.0, 1.0, 1.0, 1.0], np.float32),
            dtype=np.float32)
        self._rng = np.random.default_rng(seed)

    def _forward(self):
        # the reachable molecular states form a small discrete grid (c_eff,
        # coat_rf, actin all move in fixed increments), so memoizing the
        # 800-point energy minimization keeps training cheap.
        key = (round(self.c_eff, 5), round(self.coat_rf, 3), round(self.actin_pN, 2))
        hit = _FORWARD_CACHE.get(key)
        if hit is None:
            hit = ccs_curvature(self.c_eff, SIGMA_KBT_NM2, KAPPA_KBT, A_COAT_NM2,
                                coat_rigidity_factor=self.coat_rf,
                                active_force_pN=self.actin_pN)
            _FORWARD_CACHE[key] = hit
        return hit

    def _obs(self):
        return np.array([self.coverage, self.c_eff, self.H, self.op,
                         self.actin_pN / ACTIN_MAX, self.coat_rf / COAT_RF_MAX,
                         self.t / self.T], np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.t = 0
        self.c_eff = 0.0
        self.actin_pN = 0.0
        self.coat_rf = 1.0
        self.coverage = 0.0
        self.ruptured = False
        o = self._forward()
        self.H = o["achieved_mean_curvature_inv_nm"]
        self.op = o["dome_omega_OP"]
        self._prev_op = self.op
        return self._obs(), {"stage": o["stage"]}

    def step(self, action):
        action = int(action)
        self.t += 1
        cost = 0.0
        self.coverage = min(1.0, self.coverage + 0.08)
        if action == 0:      # recruit wedge
            self.c_eff = min(C_EFF_MAX, self.c_eff + DC_WEDGE); cost = COST_RECRUIT
        elif action == 1:    # recruit crowding partner
            self.c_eff = min(C_EFF_MAX, self.c_eff + DC_CROWD); cost = COST_RECRUIT
        elif action == 2:    # ramp actin force
            self.actin_pN = min(ACTIN_MAX, self.actin_pN + DACTIN)
            cost = COST_ACTIN * DACTIN
        elif action == 3:    # stiffen coat (one-shot up to cap)
            self.coat_rf = min(COAT_RF_MAX, self.coat_rf + DCOAT); cost = COST_COAT
        elif action == 4:    # wait
            cost = COST_WAIT

        if self.actin_pN > F_RUPTURE:
            self.ruptured = True

        o = self._forward()
        self.H = o["achieved_mean_curvature_inv_nm"]
        self.op = o["dome_omega_OP"]
        stage = o["stage"]

        progress = self.op - self._prev_op
        reward = W_PROGRESS * progress - cost
        self._prev_op = self.op

        terminated = False
        truncated = False
        productive = (self.op >= OMEGA_OP) and not self.ruptured
        if self.ruptured:
            reward -= PENALTY_RUPTURE; terminated = True
        elif productive:
            reward += BONUS_PRODUCTIVE; terminated = True
        elif self.t >= self.T:
            reward -= PENALTY_STALL; truncated = True

        info = {"stage": stage, "productive": bool(productive),
                "ruptured": bool(self.ruptured), "H": self.H, "op": self.op,
                "c_eff": self.c_eff, "actin_pN": self.actin_pN, "coat_rf": self.coat_rf}
        return self._obs(), float(reward), terminated, truncated, info

    def render(self):
        return (f"t={self.t:2d} c_eff={self.c_eff:.3f} actin={self.actin_pN:5.1f}pN "
                f"coat_rf={self.coat_rf:.1f} H={self.H:.4f} OP={self.op:.2f}")


# --- reference policies (hand-built baselines, not learned) ------------------
def greedy_physics_policy(obs):
    """A hand-built orchestration order respecting the established ladder: lay the
    coat first, then recruit crowding to build c_eff, then ramp actin toward
    scission. Uses only the observation, not privileged state."""
    coverage, c_eff, H, op, actin_norm, coat_norm, tnorm = obs
    if coat_norm < 0.99:              # lay/stiffen the coat first (one-shot)
        return 3
    if c_eff < 0.035:                 # build curvature drive before forcing
        return 1                       # crowding partner (bigger c_eff step)
    if actin_norm < 0.75:             # then ramp actin toward scission
        return 2
    return 1                           # top up crowding if still short


def random_policy(obs, rng):
    return int(rng.integers(0, 5))
