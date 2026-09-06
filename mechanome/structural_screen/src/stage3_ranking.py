"""Stage 3 - curvature-generating capacity ranking (signed). E = 0.5*k*(2c0)^2*A + gamma*|dA|."""
import pandas as pd, json

def capacity(c0_invnm, A_footprint_nm2, dA_nm2, leg, kappa, gamma):
    E_bend = 0.5*kappa*(2*abs(c0_invnm))**2*A_footprint_nm2
    E_tension = gamma*abs(dA_nm2)
    E = E_bend+E_tension
    sign = +1 if leg=="exocytic" else -1     # exocytic=outward(+), mechanosensitive=inward(-)
    return E_bend, E_tension, E, sign*E

def rank(geometry_rows, scale_json="stage0_scale.json"):
    s0=json.load(open(scale_json)); k=s0["kappa_kBT"]; g=s0["gamma_kBT_per_nm2"]; thr=s0["relevance_threshold_kBT"]
    out=[]
    for r in geometry_rows:
        Eb,Et,E,Es = capacity(r["c0_invnm"],r["A_footprint_nm2"],r.get("dA_nm2",0.0),r["leg"],k,g)
        out.append(dict(**r, E_bend_kBT=round(Eb,2), E_tension_kBT=round(Et,2),
                        E_curv_kBT=round(E,2), E_curv_signed=round(Es,2), clears_gate=bool(E>=thr)))
    df=pd.DataFrame(out).sort_values("E_curv_kBT",ascending=False).reset_index(drop=True)
    df.insert(0,"rank",df.index+1); return df
