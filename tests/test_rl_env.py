"""
Contract tests for CCPBuddingEnv (the Gymnasium RL scaffold over curvo's forward
model). Guards the env API (reset/step shapes, reward sign conventions, seed
determinism) and the two reference policies. Skips cleanly if gymnasium is not
installed (the scaffold lives in the dedicated curvo-rl environment).
"""
import numpy as np
import pytest

gym = pytest.importorskip("gymnasium")

from rl.ccp_budding_env import (CCPBuddingEnv, greedy_physics_policy,
                                random_policy, OMEGA_OP)
from rl import train_agent as ta


def test_spaces():
    env = CCPBuddingEnv()
    assert env.action_space.n == 5
    assert env.observation_space.shape == (7,)


def test_reset_returns_obs_info():
    env = CCPBuddingEnv()
    obs, info = env.reset(seed=0)
    assert obs.shape == (7,)
    assert obs.dtype == np.float32
    assert env.observation_space.contains(obs)
    assert "stage" in info


def test_step_contract():
    env = CCPBuddingEnv()
    env.reset(seed=0)
    obs, r, term, trunc, info = env.step(1)
    assert obs.shape == (7,)
    assert isinstance(r, float)
    assert isinstance(term, bool) and isinstance(trunc, bool)
    for k in ("stage", "productive", "ruptured", "H", "op", "c_eff"):
        assert k in info


def test_seed_determinism():
    e1 = CCPBuddingEnv(); e2 = CCPBuddingEnv()
    o1, _ = e1.reset(seed=42); o2, _ = e2.reset(seed=42)
    assert np.allclose(o1, o2)
    # identical action sequence -> identical trajectory
    for a in (3, 1, 1, 2, 2):
        s1 = e1.step(a); s2 = e2.step(a)
        assert np.allclose(s1[0], s2[0]) and s1[1] == s2[1]


def test_greedy_reaches_omega():
    env = CCPBuddingEnv(T=12)
    obs, _ = env.reset(seed=0)
    info = {}
    for _ in range(12):
        obs, r, term, trunc, info = env.step(greedy_physics_policy(obs))
        if term or trunc:
            break
    assert info["productive"]
    assert info["op"] >= OMEGA_OP


def test_greedy_beats_random():
    env = CCPBuddingEnv(T=12)

    def rollout(pol, seeds):
        tot = []
        for s in seeds:
            o, _ = env.reset(seed=s); acc = 0.0
            for _ in range(12):
                o, r, te, tr, i = env.step(pol(o)); acc += r
                if te or tr:
                    break
            tot.append(acc)
        return np.mean(tot)

    rng = np.random.default_rng(0)
    g = rollout(greedy_physics_policy, range(100))
    rnd = rollout(lambda o: random_policy(o, rng), range(100))
    assert g > rnd


def test_reward_sign_conventions():
    # a wait move with no curvature change costs reward (negative dense term)
    env = CCPBuddingEnv()
    env.reset(seed=0)
    _, r, _, _, _ = env.step(4)   # wait
    assert r < 0


def test_qlearning_learns():
    # short training must beat the random baseline (sanity, not benchmark)
    Q, returns, _ = ta.train(episodes=800, seed=0)
    learned = ta.greedy_from_Q(Q)
    r_learned, p_learned = ta.evaluate(learned, n=100)
    rng = np.random.default_rng(1)
    r_rand, _ = ta.evaluate(lambda o: random_policy(o, rng), n=100)
    assert r_learned.mean() > r_rand.mean()
    assert p_learned > 0.5
