"""
image_to_force.py — end-to-end pixels->force validation on EXTRACTED geometry.

This closes the one gap the STED tether test left open. There, curvo inverted the
paper's REPORTED tube radii. Here the full pipeline runs from pixels: render an
actin-driven CCP movie with a KNOWN active force, then call analyze(movie), which
does perception (extracts geometry from the image) -> inverse -> mechanism with no
access to the truth. We compare the recovered active_force point estimate to the
known value across a held-out force set, reporting identified-fraction, coverage,
and bias.

active_force_max is the actor curvo's recovery-validation gate certified as
calibrated (cov68=0.96, rel_bias +2%); this test confirms that certification holds
when geometry comes from PIXELS rather than reported numbers.
"""
from __future__ import annotations

import json
import numpy as np

try:
    from curvo import synth_movie as sm
    from curvo import analyze as az
except Exception:  # pragma: no cover
    import synth_movie as sm  # type: ignore
    import analyze as az  # type: ignore


HELD_OUT_FORCES = [25.0, 40.0, 55.0, 70.0]   # pN, distinct from calibration set


def validate(forces_pN=None, n_rep=3, nlive=150, seed0=100):
    forces_pN = forces_pN or HELD_OUT_FORCES
    rows = []
    for f_true in forces_pN:
        for r in range(n_rep):
            gt_forces = dict(sigma_kBT_nm2=0.02, c_eff_max_inv_nm=0.05,
                             active_force_max_pN=f_true)
            movie, gt = sm.render_movie(gt_forces, has_actin=True,
                                        seed=seed0 + r, psf_sigma_nm=18.0,
                                        nm_per_px=2.0, peak_photons=220.0)
            res = az.analyze(movie, "is there an active pulling force?",
                             nm_per_px=2.0, psf_sigma_nm=18.0, peak_photons=220.0,
                             channels=list(gt.channels), nlive=nlive, seed=seed0 + r)
            af = res["forces"]["active_force_max"]
            med = af["posterior_median"]
            ci = af["ci68"]
            identified = af["identified"]
            covered = (ci[0] <= f_true <= ci[1]) if ci else None
            rows.append(dict(f_true=f_true, rep=r,
                             recovered=float(med) if med is not None else None,
                             point_estimate=af["point_estimate"],
                             ci68=[float(ci[0]), float(ci[1])] if ci else None,
                             identified=bool(identified),
                             covered68=bool(covered) if covered is not None else None,
                             favored=res["favored_mechanism"]["favored"]))
    # aggregate
    valid = [x for x in rows if x["recovered"] is not None]
    ident = [x for x in valid if x["identified"]]
    rel_bias = np.mean([(x["recovered"] - x["f_true"]) / x["f_true"] for x in ident]) if ident else None
    cov = np.mean([x["covered68"] for x in valid if x["covered68"] is not None]) if valid else None
    summary = dict(
        n=len(rows), n_identified=len(ident),
        identified_frac=len(ident) / len(rows) if rows else 0.0,
        rel_bias_identified=float(rel_bias) if rel_bias is not None else None,
        coverage68=float(cov) if cov is not None else None,
        forces_tested=forces_pN)
    return dict(summary=summary, rows=rows)


if __name__ == "__main__":
    out = validate()
    json.dump(out, open("outputs/image_to_force.json", "w"), indent=2)
    s = out["summary"]
    print(f"image->force on EXTRACTED geometry: {s['n_identified']}/{s['n']} identified, "
          f"rel_bias={s['rel_bias_identified']:.1%}, cov68={s['coverage68']:.2f}")
    for x in out["rows"]:
        pe = f"{x['point_estimate']:.1f}" if x["point_estimate"] is not None else "None"
        print(f"  f_true={x['f_true']:>4} rep{x['rep']} -> rec={x['recovered']:.1f} "
              f"pe={pe} id={x['identified']} cov={x['covered68']} [{x['favored']}]")
