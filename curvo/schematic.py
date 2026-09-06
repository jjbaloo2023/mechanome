"""
curvo.schematic — an auto-generated, publication-style SVG of the orchestration
the loop found.

Generated FROM the OrchestrationRecord the loop already logs, so it is a faithful
view of the result, not a redrawing. Renders:
  - the membrane profile (flat -> dome -> Omega) implied by the achieved curvature;
  - each active player as an annotated glyph at its site, sized by magnitude
    (H0 wedge inserting into a leaflet, IDP crowding brush, coat lattice, tension arrows);
  - a contribution waterfall (how much curvature each player supplies);
  - synergy / antagonism connectors between players;
  - target vs achieved curvature + a robustness flag.

Pure-Python SVG (no dependency); vector, editable, publication-ready.
"""
from __future__ import annotations

import math

# palette threaded consistently with the matplotlib figures
COL = {
    "wedge": "#2166ac", "crowding": "#b2182b", "coat": "#7d5ba6",
    "tension": "#e08214", "membrane": "#4d4d4d", "lumen": "#d9ecff",
    "met": "#1b7837", "miss": "#b2182b", "grey": "#888888", "ink": "#222222",
}


def _membrane_path(cx, y0, width, depth, stage_op):
    """A membrane cross-section curved by the dome/Omega order parameter.
    stage_op in [0,1]: 0 flat, 0.5 hemisphere/dome, ->1 Omega (necking)."""
    half = width / 2
    pts = []
    n = 60
    for i in range(n + 1):
        x = -half + width * i / n
        # invagination: gaussian-ish well deepened by stage_op, necking near op->1
        r = x / half
        depth_eff = depth * stage_op
        prof = math.exp(-(r * 2.2) ** 2)
        # necking: pinch the mouth when op high
        neck = 1.0 - 0.5 * max(0.0, stage_op - 0.6) / 0.4 * (abs(r) > 0.45)
        y = y0 + depth_eff * prof * neck
        pts.append((cx + x, y))
    d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return d, pts


def _svg_header(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n')


def _text(x, y, s, size=12, col="#222", weight="normal", anchor="start", italic=False):
    st = "italic" if italic else "normal"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'font-weight="{weight}" font-style="{st}" text-anchor="{anchor}">{s}</text>\n')


def render_schematic(record: dict, out_path: str = "outputs/orchestration_schematic.svg") -> str:
    """Build the SVG from an OrchestrationRecord dict (loop output)."""
    W, H = 900, 620
    svg = _svg_header(W, H)

    obs = record["evaluator_result"]["observables"]
    achieved = obs["achieved_mean_curvature_inv_nm"]
    stage = obs.get("stage", "dome")
    op = obs.get("dome_omega_OP", 0.5)
    target = record["target"]["value"]
    met = record["evaluator_result"]["target_met"]
    proposals = record["proposals"]
    coupling = record.get("coupling_correction", 0.0)
    combined = record.get("combined", {})

    # --- Title ---
    svg += _text(W/2, 32, f"Orchestration for {record['case']}", 18, COL["ink"], "bold", "middle")
    svg += _text(W/2, 52, f"iteration {record['iteration']}  ·  "
                 f"achieved mean curvature {achieved:.4f} nm\u207b\u00b9  ·  stage: {stage}",
                 12, COL["grey"], "normal", "middle")

    # ================= LEFT: membrane profile with player glyphs =================
    cx, y0, mw, mdepth = 260, 150, 380, 150
    # lumen fill under the membrane
    d, pts = _membrane_path(cx, y0, mw, mdepth, op)
    # closed region for lumen shading
    fill_d = d + f" L {pts[-1][0]:.1f},{y0+mdepth+30:.1f} L {pts[0][0]:.1f},{y0+mdepth+30:.1f} Z"
    svg += f'<path d="{fill_d}" fill="{COL["lumen"]}" opacity="0.5"/>\n'
    svg += f'<path d="{d}" fill="none" stroke="{COL["membrane"]}" stroke-width="3"/>\n'
    svg += _text(cx - mw/2 + 4, y0 + mdepth + 8, "membrane profile", 11, COL["membrane"], "bold", "start")

    # magnitudes for glyph sizing
    def pget(player, key, default=0.0):
        for p in proposals:
            if p.get("player") == player:
                return p.get("parameters", {}).get(key, default)
        return default
    active_players = {p.get("player") for p in proposals}

    # WEDGE glyph (H0 amphipathic helix inserting into cis leaflet, at the rim)
    if "wedge" in active_players:
        c0w = pget("wedge", "c0_contribution_inv_nm", 0.03)
        sz = 8 + 120 * c0w
        wx, wy = cx - mw*0.28, y0 + mdepth*0.25*op + 10
        svg += (f'<polygon points="{wx-sz/2:.1f},{wy:.1f} {wx+sz/2:.1f},{wy:.1f} '
                f'{wx:.1f},{wy+sz:.1f}" fill="{COL["wedge"]}" opacity="0.9"/>\n')
        svg += _text(wx, wy-6, "H0 wedge", 10, COL["wedge"], "bold", "middle")
    # CROWDING glyph (IDP brush on the cis face near the bottom)
    if "crowding" in active_players:
        cov = pget("crowding", "coverage", 0.5)
        nb = int(4 + 8*cov)
        bx0, by0 = cx + mw*0.10, y0 + mdepth*op*0.7 + 12
        for i in range(nb):
            ang = -90 + (i - nb/2)*10
            x2 = bx0 + i*7 - nb*3.5
            svg += (f'<line x1="{x2:.1f}" y1="{by0:.1f}" x2="{x2+6*math.cos(math.radians(ang)):.1f}" '
                    f'y2="{by0-16*cov-6:.1f}" stroke="{COL["crowding"]}" stroke-width="2" opacity="0.8"/>\n')
        svg += _text(bx0, by0+16, "IDP crowding", 10, COL["crowding"], "bold", "middle")
    # COAT glyph (clathrin lattice arc above the membrane rim)
    if "coat" in active_players:
        rf = pget("coat", "rigidity_factor", 2.0)
        arc_w = mw*0.5
        ay = y0 - 4
        # hexagon-ish lattice ticks along an arc
        svg += (f'<path d="M {cx-arc_w/2:.1f},{ay:.1f} Q {cx:.1f},{ay-30-6*rf:.1f} '
                f'{cx+arc_w/2:.1f},{ay:.1f}" fill="none" stroke="{COL["coat"]}" '
                f'stroke-width="{1.5+rf*0.6:.1f}" opacity="0.85" stroke-dasharray="6,3"/>\n')
        svg += _text(cx, ay-36-6*rf, "clathrin coat", 10, COL["coat"], "bold", "middle")
    # TENSION arrows (pulling the membrane flat, at both rims)
    if "tension" in active_players:
        sig = pget("tension", "sigma_kBT_nm2", 0.0)
        al = 20 + 300*sig
        for sgn in (-1, 1):
            ex = cx + sgn*(mw/2 + 6)
            svg += (f'<line x1="{ex - sgn*al:.1f}" y1="{y0:.1f}" x2="{ex:.1f}" y2="{y0:.1f}" '
                    f'stroke="{COL["tension"]}" stroke-width="2.5" marker-end="url(#arrow)"/>\n')
        svg += _text(cx, y0+mdepth+48, f"membrane tension \u03c3 = {sig:.3f} kBT/nm\u00b2",
                     10, COL["tension"], "bold", "middle")

    # arrow marker def
    svg = svg.replace("<rect width",
        f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{COL["tension"]}"/></marker></defs>\n<rect width', 1)

    # synergy connector (wedge <-> coat, crowding <-> coat) if coupled
    if coupling and combined.get("coupled_present"):
        svg += (f'<path d="M {cx-mw*0.28:.1f},{y0+30:.1f} Q {cx:.1f},{y0-20:.1f} {cx:.1f},{y0-4:.1f}" '
                f'fill="none" stroke="{COL["grey"]}" stroke-width="1.5" stroke-dasharray="3,3"/>\n')
        svg += _text(cx-70, y0+66, f"synergy +{coupling:.0%}", 9, COL["grey"], "italic", "middle", italic=True)

    # ================= RIGHT: contribution waterfall =================
    wf_x, wf_y, wf_w, wf_h = 690, 150, 170, 200
    svg += _text(wf_x+wf_w/2, wf_y-16, "curvature contribution", 12, COL["ink"], "bold", "middle")
    # per-player contributions — use the FAITHFUL gated values the evaluator saw,
    # stored on the record under 'contribution_breakdown' if present; else recompute.
    breakdown = record.get("contribution_breakdown")
    contribs = []
    if breakdown:
        for name in ("wedge", "crowding", "coat"):
            if name in breakdown:
                contribs.append((name, breakdown[name]))
    else:
        for p in proposals:
            name = p.get("player")
            if name in ("tension",) or name not in COL:
                continue
            contribs.append((name, p.get("parameters", {}).get("c0_contribution_inv_nm", 0.0)))
    c_total = combined.get("c_eff_inv_nm", sum(v for _,v in contribs) or 1e-6)
    scale = wf_h / max(c_total*1.3, 1e-6)
    cum = wf_y + wf_h
    for name, val in contribs:
        bh = val*scale
        svg += (f'<rect x="{wf_x:.1f}" y="{cum-bh:.1f}" width="{wf_w*0.55:.1f}" height="{max(bh,1):.1f}" '
                f'fill="{COL[name]}" opacity="0.85"/>\n')
        svg += _text(wf_x+wf_w*0.6, cum-bh/2+3, f"{name} {val:.3f}", 9, COL[name], "bold", "start")
        cum -= bh
    # synergy bump
    if coupling and combined.get("coupled_present"):
        bump = (c_total - sum(v for _,v in contribs))
        if bump>0:
            bh=bump*scale
            svg += (f'<rect x="{wf_x:.1f}" y="{cum-bh:.1f}" width="{wf_w*0.55:.1f}" height="{max(bh,1):.1f}" '
                    f'fill="{COL["grey"]}" opacity="0.6"/>\n')
            svg += _text(wf_x+wf_w*0.6, cum-bh/2+3, f"synergy {bump:.3f}", 9, COL["grey"], "italic","start", italic=True)
            cum-=bh
    # total marker
    svg += (f'<line x1="{wf_x-4:.1f}" y1="{wf_y+wf_h-c_total*scale:.1f}" x2="{wf_x+wf_w*0.6:.1f}" '
            f'y2="{wf_y+wf_h-c_total*scale:.1f}" stroke="{COL["ink"]}" stroke-width="1.5" stroke-dasharray="4,2"/>\n')
    svg += _text(wf_x, wf_y+wf_h+16, f"c_eff = {c_total:.3f} nm\u207b\u00b9", 10, COL["ink"], "bold", "start")

    # ================= BOTTOM: target vs achieved + robustness =================
    by = 440
    bar_x, bar_w = 90, 500
    svg += _text(bar_x, by-8, "target vs achieved mean curvature", 12, COL["ink"], "bold", "start")
    maxc = max(target, achieved)*1.25
    tsc = bar_w/maxc
    # target bar
    svg += f'<rect x="{bar_x}" y="{by}" width="{target*tsc:.1f}" height="16" fill="{COL["grey"]}" opacity="0.5"/>\n'
    svg += _text(bar_x+target*tsc+6, by+13, f"target {target:.4f}", 10, COL["grey"], "normal", "start")
    # achieved bar
    ac = COL["met"] if met else COL["miss"]
    svg += f'<rect x="{bar_x}" y="{by+24}" width="{achieved*tsc:.1f}" height="16" fill="{ac}" opacity="0.9"/>\n'
    svg += _text(bar_x+achieved*tsc+6, by+37, f"achieved {achieved:.4f}", 10, ac, "bold", "start")
    # verdict
    verdict = "TARGET MET" if met else "below target"
    svg += _text(bar_x, by+70, f"\u25cf {verdict}  ({stage} stage)", 13, ac, "bold", "start")

    # reasoning trace (wrapped)
    trace = record.get("reasoning_trace","")
    if trace:
        svg += _text(bar_x, by+100, "orchestrator reasoning (excerpt):", 10, COL["ink"], "bold", "start")
        import textwrap
        wrapped = textwrap.wrap(trace.replace("||"," · "), 118)[:3]
        for i,ln in enumerate(wrapped):
            svg += _text(bar_x, by+116+i*14, _esc(ln), 9, COL["grey"], "normal", "start")

    # provenance footer
    svg += _text(bar_x, H-16, f"content_hash {record.get('content_hash','')}  ·  "
                 f"evaluator: {record['evaluator_result']['tier']}  ·  generated from OrchestrationRecord",
                 8, COL["grey"], "normal", "start")

    svg += "</svg>\n"
    with open(out_path, "w") as f:
        f.write(svg)
    return out_path


def _esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
