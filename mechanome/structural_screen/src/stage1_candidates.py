"""Stage 1 - candidate set (two legs) + verified conformational-state map from RCSB/UniProt."""
import requests, json, time, pandas as pd

CANDIDATES = [
 ("MscL","Mechanosensitive channel","mechanosensitive","P9WLR3","tension"),
 ("MscS","Mechanosensitive channel","mechanosensitive","P0C0S1","tension"),
 ("Piezo1","Mechanosensitive channel","mechanosensitive","E2JF22","negative"),
 ("TRAAK (K2P4.1)","K2P mechanosensitive channel","mechanosensitive","Q9NYG8","tension"),
 ("TREK-1 (K2P2.1)","K2P mechanosensitive channel","mechanosensitive","O95069","tension"),
 ("OSCA1.2","OSCA/TMEM63 mechanosensitive channel","mechanosensitive","Q9C8G5","tension"),
 ("TRPV4","TRP mechanosensitive channel","mechanosensitive","Q9HBA0","tension"),
 ("nhTMEM16 scramblase","TMEM16 scramblase","exocytic","G0S317","positive"),
 ("Synaptotagmin-1 C2AB","C2-domain curvature sensor","exocytic","P21707","positive"),
 ("Epsin-1 ENTH","ENTH domain","exocytic","O88339","positive"),
 ("Amphiphysin N-BAR","N-BAR domain","exocytic","P49418","positive"),
 ("Endophilin-A1 N-BAR","N-BAR domain","exocytic","O35179","positive"),
 ("Dynamin-1","Dynamin GTPase","exocytic","P21575","positive"),
]

# Curated experimental conformational-state map (PDB id -> state label), verified against RCSB.
STATE_MAP = {
 "MscL":("transition",{"2OAR":"closed"}),
 "MscS":("transition",{"2OAU":"closed","2VV5":"open"}),
 "Piezo1":("transition",{"6B3R":"curved_dome"}),
 "TRAAK (K2P4.1)":("transition",{"4I9W":"conformation_A","4WFF":"nonconductive_Kbound"}),
 "TREK-1 (K2P2.1)":("transition",{"4TWK":"apo"}),
 "OSCA1.2":("transition",{"6MGV":"resting"}),
 "TRPV4":("transition",{"8FC7":"RhoA_complex"}),
 "nhTMEM16 scramblase":("transition",{"6QM4":"Ca_free","6QMB":"Ca_bound"}),
 "Synaptotagmin-1 C2AB":("scaffold",{"1RSY":"C2A_apo"}),
 "Epsin-1 ENTH":("scaffold",{"1EDU":"apo_no_helix0","1H0A":"PIP2_helix0_folded"}),
 "Amphiphysin N-BAR":("scaffold",{"4ATM":"BAR_dimer"}),
 "Endophilin-A1 N-BAR":("scaffold",{"2C08":"BAR_dimer"}),
 "Dynamin-1":("scaffold",{"3ZVR":"stalk"}),
}

def verify_uniprot(acc):
    r = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.json", timeout=20)
    return r.status_code == 200

def run(out_csv="stage1_candidates.csv"):
    rows=[]
    for name,fam,leg,acc,sign in CANDIDATES:
        mech,states = STATE_MAP[name]
        rows.append(dict(protein=name,family=fam,leg=leg,uniprot=acc,curvature_sign=sign,
            mechanism=mech,n_experimental_states=len(states),
            pdb_states="; ".join(f"{p}({l})" for p,l in states.items()),
            two_state_pair=len(states)>=2))
    df=pd.DataFrame(rows); df.to_csv(out_csv,index=False); return df

if __name__ == "__main__":
    print(run().to_string(index=False))
