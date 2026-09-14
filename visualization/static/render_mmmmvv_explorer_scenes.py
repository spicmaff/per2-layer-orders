from __future__ import annotations

import json
from pathlib import Path

from per2.export.site_data import write_mmmmvv_explorer_scenes
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]


def face_card(s: SVG, x: float, y: float, label: str, w: float = 50, h: float = 26, selected: bool = False):
    row = label[0]
    fill = P["a_fill"] if row == "A" else P["b_fill"]
    stroke = P["sel"] if selected else P["rule"]
    s.rect(x, y, w, h, fill, stroke, 2 if selected else 1, 5)
    s.rect(x, y, 4, h, P["a"] if row == "A" else P["b"], "none", 0, 4)
    s.text(x + w / 2, y + h / 2, label, 10, P["ink"], 650, "middle", mono=True)


def draw_map(s: SVG, x: float, y: float, scene: dict, data: dict):
    cw, ch = 72, 52
    pivots = {scene["upper_row"]["pivot_crease_id"], scene["lower_row"]["pivot_crease_id"]}
    for f in data["map"]["faces"]:
        xx = x + (f["column"] - 1) * cw
        yy = y if f["row"] == "A" else y + ch
        s.rect(xx, yy, cw, ch, P["a_fill"] if f["row"] == "A" else P["b_fill"], P["rule"], 1, 2)
        s.text(xx + cw / 2, yy + ch / 2, f["label"], 11.5, P["ink"], 650, "middle", mono=True)
    for c in data["map"]["creases"]:
        if c["kind"] == "H":
            xx = x + (c["index"] - 1) * cw
            yy = y + ch
            s.line(xx, yy, xx + cw, yy, P["ink"], 1.8, "6 4" if c["mv"] == "V" else None)
            s.text(xx + cw / 2, yy + 11, f"H{c['index']}:{c['mv']}", 7.8, P["muted"], 600, "middle", mono=True)
        else:
            xx = x + c["index"] * cw
            yy1 = y if c["kind"] == "U" else y + ch
            yy2 = yy1 + ch
            active = c["id"] in pivots
            s.line(xx, yy1, xx, yy2, P["sel"] if active else P["ink"], 4 if active else 1.8, "6 4" if c["mv"] == "V" else None)
            if active:
                side = -12 if c["kind"] == "U" else 12
                s.text(xx + side, (yy1 + yy2) / 2, f"{c['label']}:{c['mv']}", 8.5, P["sel"], 650, "middle", mono=True)
    s.text(x, y + 2 * ch + 26, f"upper pivot U{scene['a']} · lower pivot L{scene['b']}", 10.5, P["sel"], 650)


def draw_rows(s: SVG, x: float, y: float, scene: dict):
    for rf, py, title in [(scene["upper_row"], y, "Upper A row"), (scene["lower_row"], y + 124, "Lower B row")]:
        s.text(x, py, f"{title} · R⁺ · p={rf['pivot']}", 11, P["ink"], 650)
        s.text(x, py + 24, "PHYSICAL", 8.2, P["muted"], 650, letter=.6)
        for i, fid in enumerate(rf["physical_order_face_ids"]):
            face_card(s, x + 76 + i * 55, py + 11, fid.replace("face:", ""), 48, 24)
            if i == rf["pivot"] - 1:
                s.line(x + 76 + (i + 1) * 55 - 4, py + 8, x + 76 + (i + 1) * 55 - 4, py + 40, P["sel"], 3)
        s.text(x, py + 70, "LAYER", 8.2, P["muted"], 650, letter=.6)
        for i, fid in enumerate(rf["layer_order_face_ids"]):
            face_card(s, x + 76 + i * 55, py + 57, fid.replace("face:", ""), 48, 24, fid in {rf["first_face_id"], rf["last_face_id"]})


def draw_exact_order(s: SVG, x: float, y: float, scene: dict):
    if not scene["construction"]:
        s.text(x, y, "No exact state exported", 12, P["bad"], 650)
        s.text(x, y + 26, "The prepared theorem record is incompatible.", 10, P["muted"], 450)
        s.text(x, y + 48, "Inspect the directed-cycle witness instead.", 10, P["muted"], 450)
        return
    order = scene["construction"]["layer_order"]
    s.text(x, y, "TOP ↓", 8.5, P["muted"], 650)
    for i, label in enumerate(order):
        col = 0 if i < 8 else 1
        row = i if i < 8 else i - 8
        xx = x + col * 205
        yy = y + 18 + row * 34
        s.text(xx, yy + 13, f"{i + 1:02d}", 8, P["muted"], 500, mono=True)
        face_card(s, xx + 28, yy, label, 150, 25)
    s.text(x, y + 306, "✓ independent semantic check accepted", 9.5, P["ok"], 650)


def _arrow(s: SVG, x1: float, y1: float, x2: float, y2: float, close: bool = False):
    color = P["bad"] if close else P["sel"]
    s.line(x1, y1, x2, y2, color, 3.2 if close else 2.6)
    # Small screen-space arrowhead; geometry is purely presentational.
    if abs(x2 - x1) > abs(y2 - y1):
        if x2 > x1:
            d = f"M {x2} {y2} L {x2-9} {y2-5} L {x2-9} {y2+5} Z"
        else:
            d = f"M {x2} {y2} L {x2+9} {y2-5} L {x2+9} {y2+5} Z"
    else:
        if y2 > y1:
            d = f"M {x2} {y2} L {x2-5} {y2-9} L {x2+5} {y2-9} Z"
        else:
            d = f"M {x2} {y2} L {x2-5} {y2+9} L {x2+5} {y2+9} Z"
    s.path(d, color, 1, color)


def draw_mechanism(s: SVG, x: float, y: float, scene: dict):
    if scene["construction"]:
        c = scene["construction"]
        s.text(x, y, scene["display"]["reason_label"], 14, P["ok"], 700)
        s.text(x, y + 30, scene["display"]["reason_summary"], 10.2, P["ink"], 450)
        s.text(x, y + 72, "CONSTRUCTION FAMILY", 8.2, P["muted"], 650, letter=.6)
        s.text(x, y + 92, c["construction_family"], 11, P["ink"], 650, mono=True)
        s.text(x, y + 126, "PARAMETER", 8.2, P["muted"], 650, letter=.6)
        s.text(x, y + 146, c["parameter_s"] if c["parameter_s"] is not None else "—", 11, P["ink"], 650, mono=True)
        s.text(x, y + 180, "SEMANTIC CHECK", 8.2, P["muted"], 650, letter=.6)
        s.text(x, y + 200, "✓ accepted", 11, P["ok"], 650)
        s.text(x, y + 246, "No event trace is implied by this construction.", 9.5, P["muted"], 450)
        return
    w = scene["witness"]
    labels = w["cycle_labels"][:-1]
    pos = [(x + 72, y + 65), (x + 338, y + 65), (x + 338, y + 205), (x + 72, y + 205)]
    # Draw edges to node boundaries so labels remain unobstructed.
    _arrow(s, pos[0][0] + 36, pos[0][1], pos[1][0] - 36, pos[1][1])
    _arrow(s, pos[1][0], pos[1][1] + 20, pos[2][0], pos[2][1] - 20)
    _arrow(s, pos[2][0] - 36, pos[2][1], pos[3][0] + 36, pos[3][1])
    _arrow(s, pos[3][0], pos[3][1] - 20, pos[0][0], pos[0][1] + 20, True)
    for label, (cx, cy) in zip(labels, pos):
        s.rect(cx - 36, cy - 20, 72, 40, P["a_fill"] if label.startswith("A") else P["b_fill"], P["a"] if label.startswith("A") else P["b"], 1.3, 6)
        s.text(cx, cy, label, 12, P["ink"], 700, "middle", mono=True)
    yy = y + 258
    for i, edge in enumerate(w["edges"]):
        s.text(x, yy + i * 24, f"{i+1}. {edge['relation_label']}", 9.3, P["bad"] if edge["closes_cycle"] else P["ink"], 650, mono=True)
        s.text(x + 150, yy + i * 24, edge["origin_label"], 8.7, P["muted"], 450)
        if edge["closes_cycle"]:
            s.text(x + 330, yy + i * 24, "closes cycle", 8.2, P["bad"], 700)


def render_scene(out: Path, scene: dict, data: dict):
    s = SVG(1500, 960)
    status = "COMPATIBLE" if scene["compatible"] else "INCOMPATIBLE"
    scol = P["ok"] if scene["compatible"] else P["bad"]
    s.text(48, 48, "Map & Layer-Order Explorer · MMMMVV prepared scene", 29, P["ink"], 650)
    s.text(48, 80, f"k=4 · canonical MMMMVV · {scene['display']['name']} · (a,b)=({scene['a']},{scene['b']})", 13, P["muted"], 450)
    s.rect(1112, 34, 158, 28, P["ok_fill"] if scene["compatible"] else P["bad_fill"], scol, 1, 14)
    s.text(1191, 48, ("✓ " if scene["compatible"] else "× ") + status, 10.5, scol, 650, "middle")
    s.rect(1280, 34, 172, 28, "#FFF5DF", "#A56600", 1, 14, "5 3")
    s.text(1366, 48, "◇ NOT PHYSICAL MOTION", 10, "#7A4A00", 650, "middle")

    panel(s, 40, 112, 900, 310, "Map / crease pattern", "A", "physical 2×8 geometry")
    draw_map(s, 92, 176, scene, data)
    panel(s, 40, 442, 900, 350, "Row normal forms", "B", "physical ↔ layer order")
    draw_rows(s, 72, 502, scene)
    panel(s, 960, 112, 500, 350, "Global layer order", "C", "literal labelled state")
    draw_exact_order(s, 992, 174, scene)
    panel(s, 960, 482, 500, 420, "Directed-cycle witness" if scene["witness"] else "Theorem construction", "D", "exported theorem record")
    draw_mechanism(s, 992, 542, scene)

    fill = P["ok_fill"] if scene["compatible"] else P["bad_fill"]
    s.rect(48, 816, 860, 58, fill, scol, 1, 6, "4 3" if not scene["compatible"] else None)
    s.text(68, 838, scene["display"]["reason_label"], 11, scol, 650)
    s.text(68, 858, scene["display"]["reason_summary"], 9.5, P["muted"], 450)
    s.finish(out, f"MMMMVV Explorer scene: {scene['display']['name']}", f"Prepared canonical MMMMVV k=4 scene for pivots ({scene['a']},{scene['b']}); theorem status and any exact state or obstruction witness come from Python exports.")


def main():
    cache = ROOT / "build" / "mmmmvv-explorer-render-data.json"
    write_mmmmvv_explorer_scenes(cache)
    data = json.loads(cache.read_text())
    by_id = {s["id"]: s for s in data["scenes"]}
    out = ROOT / "visualization" / "generated"
    render_scene(out / "mmmmvv_diagonal_success.svg", by_id[data["sentinels"]["diagonal_success"]], data)
    render_scene(out / "mmmmvv_boundary_success.svg", by_id[data["sentinels"]["boundary_success"]], data)
    render_scene(out / "mmmmvv_interior_obstruction.svg", by_id[data["sentinels"]["interior_obstruction"]], data)


if __name__ == "__main__":
    main()
