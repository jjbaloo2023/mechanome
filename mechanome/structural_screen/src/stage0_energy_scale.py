"""Stage 0 - fix the mechanical energy scale that gates the whole screen."""
import json
import numpy as np

KAPPA_KBT = 20.0        # bilayer bending modulus (k_B T)
GAMMA_MN_M = 0.01       # resting membrane tension (mN/m)
KBT_J = 4.114e-21       # k_B T at 310 K (J)
NECK_RADIUS_NM = 25.0   # entry neck / bud radius
RELEVANCE_THRESHOLD_KBT = 10.0  # per-protein gate: "order tens of k_BT"

def gamma_kbt_per_nm2(gamma_mn_m=GAMMA_MN_M):
    return gamma_mn_m*1e-3*(1e-9)**2/KBT_J

def per_protein_bending(c0_inv_nm, A_nm2, kappa=KAPPA_KBT):
    """Helfrich bending energy a protein supplies imprinting curvature c0 over footprint A."""
    return 0.5*kappa*(2*np.abs(c0_inv_nm))**2*A_nm2

def run(out_json="stage0_scale.json", out_fig="fig_stage0_energy_scale.png"):
    import matplotlib.pyplot as plt

    c0 = np.linspace(0,0.08,300)
    fig,ax = plt.subplots(figsize=(5.4,4.0))
    for A,lab in [(20,"small"),(50,"medium"),(100,"large")]:
        ax.plot(c0, per_protein_bending(c0,A), lw=2, label=lab)
    ax.axhspan(RELEVANCE_THRESHOLD_KBT,60,color="0.85",alpha=0.5)
    ax.axhline(RELEVANCE_THRESHOLD_KBT,color="0.4",ls="--")
    ax.axvline(1/NECK_RADIUS_NM,color="firebrick",ls=":")
    ax.set_xlabel("generated spontaneous curvature c0 (1/nm)")
    ax.set_ylabel("per-protein bending contribution (k_BT)")
    ax.set_ylim(0,60); ax.legend()
    fig.tight_layout(); fig.savefig(out_fig,dpi=300,bbox_inches="tight")
    const = dict(kappa_kBT=KAPPA_KBT, gamma_kBT_per_nm2=gamma_kbt_per_nm2(),
                 relevance_threshold_kBT=RELEVANCE_THRESHOLD_KBT,
                 neck_radius_target_nm=NECK_RADIUS_NM,
                 full_wrap_bending_kBT=round(8*np.pi*KAPPA_KBT,2))
    json.dump(const, open(out_json,"w"), indent=2)
    return const

if __name__ == "__main__":
    print(run())
