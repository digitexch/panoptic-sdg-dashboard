"""Draw the Panoptic scoring framework diagram from the live feed.

    python3 docs/build_framework.py   ->  docs/scoring_framework.svg
Numbers (weights, link counts, the worked example) come from panoptic_dashboard_data.json,
so the diagram stays in step with the workbook after every build.
"""
import json, base64, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "panoptic_dashboard_data.json"), encoding="utf-8"))
PR, SU, LK, SD = D["principles"], D["subs"], D["links"], {g["n"]: g for g in D["sdgs"]}
PCOL = {"PP1": "#2A78D6", "PP2": "#0F9B84", "PP3": "#9C3B8F", "PP4": "#D98C00"}
INK, INK2, INK3, LINE, BG = "#141B2A", "#4B5568", "#8791A2", "#DCE1E8", "#F7F8FA"
F = "Arial, Helvetica, sans-serif"; MONO = "'DejaVu Sans Mono', Menlo, Consolas, monospace"
esc = lambda t: html.escape(str(t), quote=True)
out = []
def T(x, y, t, size=13, w=400, fill=INK, anchor="start", fam=F, extra=""):
    out.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(t)}</text>')
def R(x, y, w, h, fill="#FFFFFF", stroke=LINE, rx=12, sw=1.2, extra=""):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def arrow(x1, y1, x2, y2, col=INK3, dash=None):
    out.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="1.6" fill="none" marker-end="url(#ah)" {"stroke-dasharray=%s" % chr(34) + dash + chr(34) if dash else ""}/>')
def curve(x1, y1, x2, y2, col=INK3, dash=None):
    mx = (x1 + x2) / 2
    out.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}" stroke="{col}" stroke-width="1.4" fill="none" {"stroke-dasharray=%s" % chr(34) + dash + chr(34) if dash else ""} marker-end="url(#ah)"/>')
def step(x, y, n, label):
    out.append(f'<circle cx="{x + 11}" cy="{y - 4}" r="11" fill="{INK}"/>'); T(x + 11, y, n, 12, 700, "#FFFFFF", "middle")
    T(x + 30, y, label.upper(), 11.5, 700, INK2, extra='letter-spacing="1.4"')

W, H = 1640, 1180
# ---------------------------------------------------------------- title
T(40, 58, "Panoptic scoring framework", 28, 700)
T(40, 86, "How a project score is built from the Panoptic principles, and where that score lands on the Sustainable Development Goals", 15, 400, INK2)
np_ = sum(l["a"] == "P" for l in LK); tg = sorted({l["t"] for l in LK}); gs = sorted({D["targets"][t]["g"] for t in tg})

# ---------------------------------------------------------------- lane 1: scoring
LY = 130
R(24, LY - 10, W - 48, 590, BG, "#E6E9EE", 20)
T(48, LY + 18, "SCORING", 11, 700, INK3, extra='letter-spacing="2"')
cx = [48, 330, 690, 990, 1290]
for i, (x, lab) in enumerate(zip(cx, ["Principles", "Sub-principles and weights", "Evaluators score", "Weighted points", "Project score"])):
    step(x, LY + 52, i + 1, lab)
top = LY + 76; rowh = 40; gap = 16
y = top; spans = {}
for p in PR:
    subs = [x for x in SU if x["p"] == p["id"]]
    y0 = y
    for x in subs:
        R(330, y, 320, rowh - 6, "#FFFFFF", LINE, 9)
        out.append(f'<rect x="330" y="{y}" width="5" height="{rowh - 6}" rx="2" fill="{PCOL[p["id"]]}"/>')
        T(346, y + 22, x["id"], 12, 700, INK, fam=MONO)
        T(402, y + 22, x["short"], 13, 400, INK)
        R(600, y + 7, 40, 20, "#F1F3F6", "none", 10, 0); T(620, y + 21, x["w"], 12, 700, INK, "middle", MONO)
        y += rowh
    spans[p["id"]] = (y0, y - 6); y += gap
for p in PR:
    y0, y1 = spans[p["id"]]; c = PCOL[p["id"]]
    R(48, y0, 236, y1 - y0, "#FFFFFF", c, 12, 1.6)
    out.append(f'<rect x="48" y="{y0}" width="236" height="{y1 - y0}" rx="12" fill="{c}" fill-opacity=".06"/>')
    T(66, y0 + 26, p["id"], 14, 700, c, fam=MONO); T(66, y0 + 46, p["short"], 15, 700, INK)
    T(266, y0 + 26, f"{p['w']}", 18, 700, INK, "end"); T(266, y0 + 42, "weight", 10.5, 400, INK3, "end")
    curve(284, (y0 + y1) / 2, 326, (y0 + y1) / 2, c)
T(640, y - 2, f"Total weight {sum(x['w'] for x in SU)}", 12, 700, INK2, "end")
ymid = (top + y) / 2
# evaluators
ex, ew = 690, 260
R(ex, top, ew, 300, "#FFFFFF", LINE, 14)
T(ex + 18, top + 32, "Each evaluator scores every", 14, 700); T(ex + 18, top + 52, "sub-principle from 1 to 5", 14, 700)
T(ex + 18, top + 76, "in half steps, against its", 13, 400, INK2); T(ex + 18, top + 94, "assessment question.", 13, 400, INK2)
out.append(f'<defs><linearGradient id="lik" x1="0" x2="1"><stop offset="0" stop-color="#E27B7B"/><stop offset=".375" stop-color="#F0BE55"/><stop offset=".75" stop-color="#86CC86"/><stop offset="1" stop-color="#33A633"/></linearGradient>'
           f'<linearGradient id="pg" x1="0" x2="1"><stop offset="0" stop-color="#E27B7B"/><stop offset=".5" stop-color="#F0BE55"/><stop offset=".8" stop-color="#86CC86"/><stop offset="1" stop-color="#33A633"/></linearGradient>'
           f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{INK3}"/></marker></defs>')
R(ex + 18, top + 124, ew - 36, 10, "url(#lik)", "none", 5, 0)
for k in range(5):
    xx = ex + 18 + k * (ew - 36) / 4; T(xx, top + 154, k + 1, 11, 700, INK2, "middle", MONO)
out.append(f'<circle cx="{ex + 18 + 3 * (ew - 36) / 4}" cy="{top + 129}" r="8" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>')
T(ex + 18, top + 190, "Several evaluators:", 13, 700); T(ex + 18, top + 210, "scores are averaged per", 13, 400, INK2); T(ex + 18, top + 228, "sub-principle.", 13, 400, INK2)
T(ex + 18, top + 262, "Source: Project scores sheet", 11.5, 400, INK3)
arrow(654, top + 150, ex - 4, top + 150)
# weighted points
wx, ww = 990, 270
R(wx, top, ww, 300, "#FFFFFF", LINE, 14)
T(wx + 18, top + 34, "points = score ÷ 5 × weight", 15, 700, INK, fam=MONO)
T(wx + 18, top + 60, "Each sub-principle earns up to", 13, 400, INK2); T(wx + 18, top + 78, "its weight in points.", 13, 400, INK2)
proj = (D.get("projects") or [None])[0]
def avg(sub):
    v = [e["s"][sub] for e in proj["evals"] if sub in e["s"]] if proj else []
    return sum(v) / len(v) if v else None
ex_rows = [x for x in SU if x["id"] in ("PP4.1", "PP3.3", "PP1.1")]
yy = top + 118
T(wx + 18, yy - 12, f"Worked example · {proj['id']}" if proj else "Worked example", 11, 700, INK3, extra='letter-spacing="1"')
for x in ex_rows:
    s = avg(x["id"]) or 4
    R(wx + 14, yy, ww - 28, 34, "#F7F8FA", "none", 8, 0)
    T(wx + 24, yy + 22, x["id"], 12, 700, INK, fam=MONO)
    T(wx + ww - 24, yy + 22, f"{s:g} ÷ 5 × {x['w']} = {s / 5 * x['w']:.1f}", 12.5, 400, INK, "end", MONO)
    yy += 42
T(wx + 18, top + 262, "Maximum: 100 points in total", 11.5, 400, INK3)
arrow(ex + ew + 4, top + 150, wx - 4, top + 150)
# project score + bands
px, pw = 1290, 302
R(px, top, pw, 160, "#FFFFFF", LINE, 14)
T(px + 18, top + 32, "score = Σ points ÷ Σ weights", 15, 700, INK, fam=MONO)
T(px + 18, top + 54, "of the sub-principles scored", 12.5, 400, INK2)
tot = sum((avg(x["id"]) or 0) / 5 * x["w"] for x in SU) if proj else None
if proj:
    T(px + 18, top + 92, f"{tot:.1f} ÷ 100", 22, 700, INK, fam=MONO); T(px + pw - 18, top + 92, f"= {tot:.1f}%", 22, 700, "#0A8A0A", "end", MONO)
    T(px + 18, top + 112, f"{proj['id']} · {proj['name']}", 11.5, 400, INK3)
R(px + 18, top + 128, pw - 36, 10, "url(#pg)", "none", 5, 0)
for t, lab in ((0, "0"), (.5, "50"), (.8, "80"), (1, "100")):
    xx = px + 18 + t * (pw - 36); out.append(f'<line x1="{xx}" y1="{top + 124}" x2="{xx}" y2="{top + 142}" stroke="{INK}" stroke-opacity=".3"/>')
if proj:
    out.append(f'<circle cx="{px + 18 + tot / 100 * (pw - 36)}" cy="{top + 133}" r="8" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>')
arrow(wx + ww + 4, top + 80, px - 4, top + 80)
by = top + 184
for col, soft, rng, name, txt in (("#0CA30C", "#E4F4E4", "80–100%", "Bankable portfolio", "Investor-ready summary"),
                                   ("#E0A100", "#FDF1D3", "50–79%", "Return to step 2", "Refine metrics, resubmit"),
                                   ("#D03B3B", "#F9E1E1", "0–49%", "Rework", "Complete rework")):
    R(px, by, pw, 62, soft, col, 12, 1.4)
    T(px + 18, by + 26, rng, 14, 700, INK, fam=MONO); T(px + 110, by + 26, name, 14, 700, INK)
    T(px + 110, by + 46, txt, 12, 400, INK2)
    by += 72
lane1_bottom = max(y, by) + 10

# ---------------------------------------------------------------- lane 2: SDG alignment
L2 = 750
R(24, L2 - 10, W - 48, 250, BG, "#E6E9EE", 20)
T(48, L2 + 18, "SDG ALIGNMENT", 11, 700, INK3, extra='letter-spacing="2"')
bx = [48, 390, 700]
R(bx[0], L2 + 40, 300, 150, "#FFFFFF", LINE, 14)
T(bx[0] + 18, L2 + 72, f"{len(LK)} target links", 20, 700)
T(bx[0] + 18, L2 + 98, f"{np_} primary · {len(LK) - np_} secondary", 14, 400, INK2)
T(bx[0] + 18, L2 + 128, "Each sub-principle links to the", 12.5, 400, INK2); T(bx[0] + 18, L2 + 146, "SDG targets it advances", 12.5, 400, INK2)
T(bx[0] + 18, L2 + 174, "Source: Target links sheet", 11.5, 400, INK3)
R(bx[1], L2 + 40, 270, 150, "#FFFFFF", LINE, 14)
T(bx[1] + 18, L2 + 72, f"{len(tg)} SDG targets", 20, 700)
T(bx[1] + 18, L2 + 98, "UNSD target wording", 14, 400, INK2)
T(bx[1] + 18, L2 + 128, "Several sub-principles can", 12.5, 400, INK2); T(bx[1] + 18, L2 + 146, "share one target", 12.5, 400, INK2)
arrow(bx[0] + 304, L2 + 115, bx[1] - 4, L2 + 115)
R(bx[2], L2 + 40, W - 48 - bx[2] - 24, 150, "#FFFFFF", LINE, 14)
T(bx[2] + 18, L2 + 72, f"{len(gs)} of 17 SDGs", 20, 700)
T(bx[2] + 210, L2 + 72, "Where the score lands: each sub-principle’s points are shared across its linked targets", 12.5, 400, INK2)
T(bx[2] + 210, L2 + 90, "(primary ×2, secondary ×1) and summed per goal. In the dashboard the SDG arcs rise in proportion.", 12.5, 400, INK2)
arrow(bx[1] + 274, L2 + 115, bx[2] - 4, L2 + 115)
icx = bx[2] + 18
for n in gs:
    f = os.path.join(ROOT, "assets", "sdg", f"sdg-{n:02d}.png")
    if os.path.exists(f):
        uri = "data:image/png;base64," + base64.b64encode(open(f, "rb").read()).decode()
        out.append(f'<image href="{uri}" x="{icx}" y="{L2 + 106}" width="62" height="62"><title>SDG {n} {esc(SD[n]["name"])}</title></image>')
    else:
        R(icx, L2 + 106, 62, 62, SD[n]["c"], "none", 8, 0); T(icx + 31, L2 + 144, n, 20, 700, "#FFFFFF", "middle")
    icx += 70
# connectors between lanes
out.append(f'<path d="M490,{y - 10} C490,{L2 - 30} 200,{L2 - 10} 200,{L2 + 36}" stroke="{INK3}" stroke-width="1.5" fill="none" stroke-dasharray="5 5" marker-end="url(#ah)"/>')
T(512, L2 - 40, "sub-principle → target links", 11.5, 400, INK3)
out.append(f'<path d="M{wx + ww / 2},{top + 304} C{wx + ww / 2},{L2 - 60} {wx + 120},{L2 - 30} {wx + 120},{L2 + 36}" stroke="#0CA30C" stroke-width="1.5" fill="none" stroke-dasharray="5 5" marker-end="url(#ah)"/>')
T(wx + ww / 2 + 12, L2 - 22, "points carried to the SDGs", 11.5, 400, "#0A8A0A")

# ---------------------------------------------------------------- lane 3: data stack
L3 = 1020
R(24, L3 - 10, W - 48, 140, BG, "#E6E9EE", 20)
T(48, L3 + 18, "DATA STACK", 11, 700, INK3, extra='letter-spacing="2"')
items = [("Workbook", "Panoptic_SDG_database_department.xlsx", "the only place data is edited"),
         ("build.py", "checks the data · FEATURES switches", "stops with a list if anything is wrong"),
         ("JSON feed", "panoptic_dashboard_data.json", "generated · reusable by other tools"),
         ("Template", "dashboard.template.html", "the UI · one __DATA__ slot"),
         ("Dashboard", "panoptic-sdg-dashboard.html", "generated · published page")]
bw = (W - 48 - 48 - 4 * 34) / 5; xx = 48
for i, (a, b, c) in enumerate(items):
    R(xx, L3 + 34, bw, 80, "#FFFFFF", INK if i == 0 else LINE, 12, 1.6 if i == 0 else 1.2)
    T(xx + 16, L3 + 60, a, 15, 700); T(xx + 16, L3 + 80, b, 11.5, 400, INK, fam=MONO); T(xx + 16, L3 + 99, c, 11.5, 400, INK3)
    if i < 4: arrow(xx + bw + 4, L3 + 74, xx + bw + 30, L3 + 74)
    xx += bw + 34
T(W - 40, H - 22, f"Generated from the workbook feed, {D['meta']['prepared']}. SDG icons: United Nations.", 11, 400, INK3, "end")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Panoptic scoring framework diagram">' \
      f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>' + "".join(out) + "</svg>"
open(os.path.join(ROOT, "docs", "scoring_framework.svg"), "w", encoding="utf-8").write(svg)
print("wrote docs/scoring_framework.svg", len(svg))
