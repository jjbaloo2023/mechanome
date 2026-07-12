"""
tissue module -- vertex / junction force inference.

Governing law: force balance at a tri-cellular vertex (Young / Lami),
  sum_i T_i * t_hat_i = 0,
equivalently the law of sines on the three opening angles,
  T_1/sin(theta_1) = T_2/sin(theta_2) = T_3/sin(theta_3).

Analytic limit: a symmetric vertex sits at theta = 120 deg with equal tensions;
recovering relative tensions from angles returns T_1:T_2:T_3 = sin th_1 : sin th_2
: sin th_3 (= 1:1:1 at 120 deg).

Applicable validation data: Bayesian force inference (Ishihara & Sugimura 2012,
J Theor Biol 313:201; CellFIT, Brodland 2014), validated against vertex-model
simulation and laser-ablation recoil. Anchor here: recover relative junction
tensions from a synthetic tri-junction geometry.

Validation tier: built_analytic (analytic limit + published-method anchor; NOT
real-data force-paired).
"""
import numpy as np

VALIDATION_ANCHOR = "Ishihara & Sugimura 2012 J Theor Biol 313:201 (Bayesian force inference)"


def tensions_from_angles(a12_deg, a23_deg, a31_deg):
    """Relative edge tensions at a tri-junction from the three opening angles.

    Angles are the openings between CONSECUTIVE edges going around the vertex
    (a12 between edges 1&2, a23 between 2&3, a31 between 3&1) and must sum to 360.
    With edges placed at cumulative directions [0, a12, a12+a23], the angle
    OPPOSITE edge i is the opening spanned by the other two edges; by the law of
    sines the tension on edge i is proportional to sin(that opposite angle):
        T1 ~ sin(a23), T2 ~ sin(a31), T3 ~ sin(a12).
    Returns tensions in edge order (T1,T2,T3), normalized to mean 1.
    """
    A = np.array([a12_deg, a23_deg, a31_deg], float)
    if not np.isclose(A.sum(), 360.0, atol=1e-6):
        raise ValueError(f"tri-junction angles must sum to 360 deg, got {A.sum()}")
    T = np.sin(np.radians(np.roll(A, -1)))   # T_i <- sin(angle opposite edge i)
    return T / T.mean()


def angles_from_tensions(T1, T2, T3):
    """Forward: equilibrium opening angles (deg) for three given edge tensions.

    Each vertex angle is between the two edges adjacent to it; by force balance
    the angle facing edge i satisfies the law of sines T_i ~ sin(theta_i). We
    solve the triangle-of-forces: the exterior angles of the force triangle whose
    sides are (T1,T2,T3). Returns the three opening angles that sum to 360.
    """
    T = np.array([T1, T2, T3], float)
    # force triangle interior angles via law of cosines
    a, b, c = T
    # interior angle opposite side a: alpha = acos((b^2+c^2-a^2)/(2bc))
    def interior(opp, s1, s2):
        cosA = (s1**2 + s2**2 - opp**2) / (2 * s1 * s2)
        return np.degrees(np.arccos(np.clip(cosA, -1, 1)))
    A = interior(a, b, c); B = interior(b, a, c); C = interior(c, a, b)
    # Going-around opening angles (a12, a23, a31): the opening between edges j,k
    # equals 180 - (force-triangle interior angle opposite the THIRD side).
    #   a12 (edges 1,2) = 180 - C ;  a23 (edges 2,3) = 180 - A ;  a31 = 180 - B
    return np.array([180.0 - C, 180.0 - A, 180.0 - B])


def force_balance_residual(theta_deg, T):
    """L2 norm of the net force vector sum_i T_i t_hat_i at the vertex.

    Edges are placed at cumulative angles around the vertex; zero residual == the
    tensions are in mechanical equilibrium for that geometry.
    """
    theta = np.radians(np.asarray(theta_deg, float))
    dirs = np.cumsum(np.r_[0.0, theta[:-1]])
    fx = np.sum(np.asarray(T) * np.cos(dirs))
    fy = np.sum(np.asarray(T) * np.sin(dirs))
    return float(np.hypot(fx, fy))


def self_validate():
    """Recover the analytic limit and a synthetic asymmetric junction to <1%."""
    out = {}
    # (1) symmetric 120 deg -> equal tensions
    Tsym = tensions_from_angles(120, 120, 120)
    out["symmetric_tensions"] = Tsym.tolist()
    out["symmetric_err"] = float(np.max(np.abs(Tsym - 1.0)))
    # (2) round-trip: tensions -> angles -> tensions on an asymmetric junction
    T_true = np.array([1.0, 1.3, 0.8]); T_true = T_true / T_true.mean()
    angs = angles_from_tensions(*T_true)
    T_rec = tensions_from_angles(*angs)
    out["angles_sum"] = float(angs.sum())
    out["tension_roundtrip_rel_err"] = float(np.max(np.abs(T_rec - T_true) / T_true))
    # (3) force-balance residual at the recovered equilibrium is ~0
    out["force_balance_residual"] = force_balance_residual(angs, T_rec)
    out["passed"] = bool(out["symmetric_err"] < 0.01 and
                         out["tension_roundtrip_rel_err"] < 0.01 and
                         out["force_balance_residual"] < 1e-6)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(self_validate(), indent=2))
