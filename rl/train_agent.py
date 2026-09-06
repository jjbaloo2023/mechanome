"""
train_agent.py -- a lightweight tabular Q-learning sanity run on CCPBuddingEnv.

The environment is a scaling scaffold, not a source of new physics. This run
checks two things: (a) the environment is learnable by a generic agent with no
physics knowledge, and (b) the learned policy recovers the same physical priority
curvo established from the PICALM/epsin data: build curvature drive by recruiting
the crowding partner first, then ramp actin only once c_eff is committed. (The
learned sequence is crowd -> crowd -> actin...; it skips the coat-stiffening move
the hand-built greedy policy uses, because with the crowding step it can reach Omega
faster and save the coat move-cost -- a mild optimization the hand-built policy
leaves on the table, not a different ordering of the crowding/actin ladder.)

Tabular Q-learning over a coarse discretization of the 7-d observation; CPU-only,
capped at a few thousand episodes (< ~2 min).
"""
from __future__ import annotations

import numpy as np

from rl.ccp_budding_env import CCPBuddingEnv, greedy_physics_policy, random_policy

# coarse discretization of the continuous observation into a hashable key
C_EFF_MAX, ACTIN_MAX, COAT_RF_MAX = 0.08, 120.0, 3.0
N_ACTIONS = 5


def discretize(obs):
    coverage, c_eff, H, op, actin_n, coat_n, tnorm = obs
    return (int(min(4, c_eff / C_EFF_MAX * 5)),      # c_eff bin 0..4
            int(min(4, actin_n * 5)),                # actin bin 0..4
            int(round(coat_n)),                      # coat 0/1
            int(min(4, op * 5)))                     # op bin 0..4


def train(episodes=4000, alpha=0.5, gamma=0.97, eps0=1.0, eps_min=0.05,
          T=12, seed=0):
    rng = np.random.default_rng(seed)
    env = CCPBuddingEnv(T=T)
    Q = {}

    def qrow(s):
        if s not in Q:
            Q[s] = np.zeros(N_ACTIONS)
        return Q[s]

    returns = []
    for ep in range(episodes):
        eps = max(eps_min, eps0 * (1 - ep / episodes))
        obs, _ = env.reset(seed=int(rng.integers(1 << 30)))
        s = discretize(obs); acc = 0.0
        for _ in range(T):
            a = (int(rng.integers(N_ACTIONS)) if rng.random() < eps
                 else int(np.argmax(qrow(s))))
            obs2, r, term, trunc, info = env.step(a)
            s2 = discretize(obs2)
            target = r + (0.0 if (term or trunc) else gamma * qrow(s2).max())
            qrow(s)[a] += alpha * (target - qrow(s)[a])
            s = s2; acc += r
            if term or trunc:
                break
        returns.append(acc)
    return Q, np.array(returns), env


def greedy_from_Q(Q):
    """Return a policy that acts greedily w.r.t. the learned Q-table."""
    def policy(obs):
        s = discretize(obs)
        if s in Q:
            return int(np.argmax(Q[s]))
        return 4  # wait if unseen
    return policy


def evaluate(policy, n=300, T=12, seed=9000):
    env = CCPBuddingEnv(T=T)
    rets = []; prod = 0
    for i in range(n):
        obs, _ = env.reset(seed=seed + i); acc = 0.0
        for _ in range(T):
            obs, r, term, trunc, info = env.step(policy(obs)); acc += r
            if term or trunc:
                break
        rets.append(acc); prod += int(info["productive"])
    return np.array(rets), prod / n


def learned_action_order(Q, T=12):
    """Roll out the learned greedy policy once and report the action sequence."""
    env = CCPBuddingEnv(T=T); obs, _ = env.reset(seed=0)
    pol = greedy_from_Q(Q); seq = []
    names = ["wedge", "crowd", "actin", "coat", "wait"]
    for _ in range(T):
        a = pol(obs); obs, r, term, trunc, info = env.step(a)
        seq.append(names[a])
        if term or trunc:
            break
    return seq, info


if __name__ == "__main__":
    import time
    t0 = time.time()
    Q, returns, _ = train(episodes=4000, seed=0)
    learned = greedy_from_Q(Q)
    r_learned, p_learned = evaluate(learned)
    rng = np.random.default_rng(1)
    r_rand, p_rand = evaluate(lambda o: random_policy(o, rng))
    r_greedy, p_greedy = evaluate(greedy_physics_policy)
    seq, info = learned_action_order(Q)
    print(f"trained {len(Q)} states in {time.time()-t0:.1f}s")
    print(f"learned  : mean {r_learned.mean():.2f}  productive {p_learned:.2f}")
    print(f"greedy   : mean {r_greedy.mean():.2f}  productive {p_greedy:.2f}")
    print(f"random   : mean {r_rand.mean():.2f}  productive {p_rand:.2f}")
    print(f"learned action order: {seq}  (productive={info['productive']})")
