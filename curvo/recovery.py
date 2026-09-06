"""
recovery.py — synthetic recovery validation: the credibility gate.

The rule (v2 decision record): NO force claim ships without passing this. We take
KNOWN ground-truth forces, push them through the full pipeline
    forces -> render_movie -> PerceptionProvider -> inverse (nested sampling)
and check the RECOVERED POSTERIOR against truth on three axes:

  1. BIAS       -- is the posterior median close to truth? (per-parameter)
  2. CALIBRATION-- do the X% credible intervals contain truth X% of the time,
                   across many independent noise realizations? A calibrated
                   posterior has ~68% of truths inside the 68% CI. Over-narrow
                   posteriors (over-confident) fail this even if unbiased.
  3. IDENTIFIABILITY HONESTY -- when an actor is genuinely unconstrained by the
                   data (e.g. active_force from H(t) alone), is it FLAGGED
                   unidentified rather than reported as a confident value?

The output is a calibration report + figure. Anything that fails calibration is
a parameter analyze() must return as a posterior, never a point value.
"""
from __future__ import annotations


import numpy as np

from . import synth_movie as sm
from . import perception as pcp
from . import inverse as inv


def _one_recovery(gt_forces, A_coat_nm2, has_actin, seed, nlive=200,
                  use_actin_channel=True):
    """Render one noisy movie from known forces, perceive it, invert it.

    Returns (posterior_result, truth_dict, mask_count)."""
    movie, gt = sm.render_movie(gt_forces, field_px=128, nm_per_px=2.0,
                                psf_sigma_nm=18.0, has_actin=has_actin, seed=seed)
    meta = dict(nm_per_px=2.0, channels=gt.channels, psf_sigma_nm=18.0,
                peak_photons=220.0, movie_id="rec%d" % seed)
    trace = pcp.PerceptionProvider(host=None).extract(movie, meta, seed=seed + 100)
    H = trace.arr("H_inv_nm"); Hs = trace.arr("H_sigma_inv_nm")
    depth = trace.arr("depth_nm"); mask = depth >= 18.0
    kw = {}
    if has_actin and use_actin_channel:
        kw = dict(actin_obs=trace.arr("actin_density"),
                  actin_sigma=trace.arr("actin_sigma"))
    res = inv.run_nested(H, Hs, A_coat_nm2, mask=mask, nlive=nlive,
                         seed=seed + 7, **kw)
    truth = dict(c_eff_max=gt_forces.get("c_eff_max_inv_nm", 0.0),
                 active_force_max=gt_forces.get("active_force_max_pN", 0.0),
                 sigma=gt_forces.get("sigma_kBT_nm2", 0.02))
    return res, truth, int(mask.sum())


def recovery_grid(A_coat_nm2=np.pi * 60 ** 2, n_noise=8, seed0=0, verbose=True):
    """Run recovery over a grid of ground-truth forces x independent noise draws.

    Grid spans wedge-dominated, actin-dominated, and mixed regimes so calibration
    is measured where each actor is / isn't identifiable. For each truth point we
    draw n_noise independent movies and record whether truth falls in the 68/95%
    CI (calibration) and the median (bias).
    """
    # (label, gt_forces, has_actin)
    grid = [
        ("wedge_lo",  dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.030, active_force_max_pN=0.0,  kappa_kBT=20, coat_rigidity_factor=3.0, T=24), False),
        ("wedge_hi",  dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.045, active_force_max_pN=0.0,  kappa_kBT=20, coat_rigidity_factor=3.0, T=24), False),
        ("actin_mid", dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.015, active_force_max_pN=30.0, kappa_kBT=20, coat_rigidity_factor=3.0, T=24), True),
        ("actin_hi",  dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.010, active_force_max_pN=45.0, kappa_kBT=20, coat_rigidity_factor=3.0, T=24), True),
        ("mixed",     dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.025, active_force_max_pN=25.0, kappa_kBT=20, coat_rigidity_factor=3.0, T=24), True),
    ]
    records = []
    for label, gtf, has_actin in grid:
        for k in range(n_noise):
            seed = seed0 + 1000 * len(records) + k
            res, truth, nmask = _one_recovery(gtf, A_coat_nm2, has_actin, seed)
            ident = inv.identifiability(res["samples"], res["params"])
            row = dict(label=label, has_actin=has_actin, seed=seed, nmask=nmask,
                       logz=res["logz"])
            for p in res["params"]:
                nm = p.name
                info = ident[nm]
                lo68, hi68 = info["ci68"]; lo95, hi95 = info["ci95"]
                tv = truth[nm]
                row[nm] = dict(
                    truth=tv, median=info["median"],
                    in68=bool(lo68 <= tv <= hi68), in95=bool(lo95 <= tv <= hi95),
                    identified=info["identified"],
                    degenerate=bool(info["degenerate_with"]))
            records.append(row)
        if verbose:
            print("done", label)
    return records


def render_recovery(records, summ, path="outputs/recovery_validation.png",
                    apply_style=None):
    """3-panel credibility figure: recovered-vs-truth, coverage, identifiability."""
    import matplotlib.pyplot as plt
    if apply_style is not None:
        apply_style(sizes=(8, 7, 6))
    params = ["c_eff_max", "active_force_max", "sigma"]
    colors = {"c_eff_max": "#c0392b", "active_force_max": "#2c6fbb", "sigma": "#27ae60"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
    # panel 1: recovered median vs truth (identified points only), y=x
    ax = axes[0]
    for nm in params:
        rows = [r[nm] for r in records if nm in r and r[nm]["identified"]]
        if not rows:
            continue
        tr = [r["truth"] for r in rows]; md = [r["median"] for r in rows]
        # normalize each param to its prior range for a shared axis
        rng = {"c_eff_max": 0.08, "active_force_max": 60.0, "sigma": 0.05}[nm]
        ax.plot(np.array(tr) / rng, np.array(md) / rng, 'o', ms=4,
                color=colors[nm], alpha=0.7, label=nm)
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.6)
    ax.set_xlabel("truth (prior-normalized)"); ax.set_ylabel("recovered median")
    ax.set_title("recovered vs truth (identified)", fontsize=9); ax.legend(fontsize=6.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    # panel 2: coverage bars (68 / 95) vs nominal
    ax = axes[1]
    x = np.arange(len(params)); w = 0.35
    # identified-conditional coverage (the real calibration metric); NaN -> 0 bar
    c68 = [summ[p]["coverage68_identified"] if not np.isnan(summ[p]["coverage68_identified"]) else 0 for p in params]
    c95 = [summ[p]["coverage95_identified"] if not np.isnan(summ[p]["coverage95_identified"]) else 0 for p in params]
    ax.bar(x - w / 2, c68, w, color="#5b8fd0", label="68% CI")
    ax.bar(x + w / 2, c95, w, color="#b0c9e8", label="95% CI")
    ax.axhline(0.68, color="#5b8fd0", ls="--", lw=1); ax.axhline(0.95, color="#888", ls="--", lw=1)
    for i, p in enumerate(params):
        if summ[p]["n_identified"] == 0:
            ax.text(i, 0.05, "never\nidentified", ha="center", fontsize=6, style="italic", color="#c0392b")
    ax.set_xticks(x); ax.set_xticklabels(["c_eff", "active", "σ"], fontsize=8)
    ax.set_ylabel("truths in CI | identified"); ax.set_ylim(0, 1.05)
    ax.set_title("posterior calibration", fontsize=9); ax.legend(fontsize=6.5)
    # panel 3: identifiability honesty -- frac flagged identified, by regime
    ax = axes[2]
    labels = sorted(set(r["label"] for r in records))
    af_id = []
    for lab in labels:
        rr = [r["active_force_max"] for r in records if r["label"] == lab]
        af_id.append(np.mean([x["identified"] for x in rr]))
    has_actin_lab = {lab: any(r["has_actin"] for r in records if r["label"] == lab)
                     for lab in labels}
    bar_c = ["#2c6fbb" if has_actin_lab[l] else "#c0392b" for l in labels]
    ax.barh(np.arange(len(labels)), af_id, color=bar_c)
    ax.set_yticks(np.arange(len(labels))); ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("frac. active_force IDENTIFIED"); ax.set_xlim(0, 1)
    ax.set_title("identifiability honesty\n(blue=actin ch, red=H-only)", fontsize=8)
    fig.suptitle("Synthetic recovery validation — the credibility gate", fontsize=10, y=1.03)
    fig.tight_layout()
    fig.savefig(path, dpi=175, bbox_inches="tight")
    return fig


def calibration_summary(records):
    """Aggregate per-parameter coverage (68/95), bias, and identifiability rate."""
    params = ["c_eff_max", "active_force_max", "sigma"]
    summ = {}
    for nm in params:
        rows = [r[nm] for r in records if nm in r]
        idr = [r for r in rows if r["identified"]]      # identified subset
        # Coverage is only a meaningful calibration check on IDENTIFIED estimates
        # (an unidentified param's CI is prior-dominated, not a data-driven
        # interval). We report BOTH the identified-conditional coverage (the real
        # calibration metric) and the all-rows coverage for completeness.
        cov68_all = float(np.mean([r["in68"] for r in rows])) if rows else np.nan
        cov95_all = float(np.mean([r["in95"] for r in rows])) if rows else np.nan
        cov68_id = float(np.mean([r["in68"] for r in idr])) if idr else np.nan
        cov95_id = float(np.mean([r["in95"] for r in idr])) if idr else np.nan
        if idr:
            rel = [(r["median"] - r["truth"]) / r["truth"]
                   for r in idr if abs(r["truth"]) > 1e-6]
            bias = float(np.mean([(r["median"] - r["truth"]) for r in idr]))
            relbias = float(np.mean(rel)) if rel else np.nan
        else:
            bias, relbias = np.nan, np.nan
        summ[nm] = dict(
            n=len(rows), n_identified=len(idr),
            frac_identified=float(len(idr) / len(rows)) if rows else np.nan,
            coverage68_identified=cov68_id, coverage95_identified=cov95_id,
            coverage68_all=cov68_all, coverage95_all=cov95_all,
            bias_identified=bias, rel_bias_identified=relbias)
    return summ
