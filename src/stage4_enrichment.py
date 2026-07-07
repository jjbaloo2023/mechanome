"""Stage 4 - pre-committed enrichment test vs EXTERNAL GO labels (ranking-blind)."""
import requests, json, hashlib, numpy as np, pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

# Exactly the 9 GO IDs in the pre-registration (results/stage4_prediction_prereg.md). Do NOT add
# generic lipid-binding terms — the pre-committed test scores against this literal set only.
LABEL_GO = {"GO:0046718","GO:0007009","GO:0006897","GO:0030100","GO:0016050",
            "GO:0001778","GO:0097320","GO:0072659","GO:0030674"}

def freeze_ranking(rank_df):
    csv = rank_df[["rank","protein","E_curv_kBT","E_curv_signed","clears_gate"]].to_csv(index=False)
    return hashlib.sha256(csv.encode()).hexdigest()[:16], csv

def quickgo(acc):
    r = requests.get("https://www.ebi.ac.uk/QuickGO/services/annotation/search",
                     params={"geneProductId":acc,"limit":200}, headers={"Accept":"application/json"}, timeout=30)
    return {x["goId"] for x in r.json().get("results",[])} if r.status_code==200 else set()

def test(rank_df, go_by_uniprot):
    df=rank_df.copy()
    df["n_label_go"]=df["uniprot"].map(lambda a: len(go_by_uniprot.get(a,set()) & LABEL_GO))
    df["label_positive"]=df["n_label_go"]>=1
    pos=df.loc[df.label_positive,"E_curv_kBT"]; neg=df.loc[~df.label_positive,"E_curv_kBT"]
    U,p=mannwhitneyu(pos,neg,alternative="greater"); auroc=U/(len(pos)*len(neg))
    rho,psp=spearmanr(df["E_curv_kBT"],df["n_label_go"])
    return df, dict(auroc=auroc, p_mannwhitney=p, spearman_rho=rho, spearman_p=psp,
                    base_rate=df.label_positive.mean(), gate_rate=df[df.clears_gate].label_positive.mean())
