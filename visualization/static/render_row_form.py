from __future__ import annotations

from pathlib import Path

from per2.theory import row_order
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]


def face_box(s, x, y, label, row="A", selected=False):
    fill = P["a_fill"] if row == "A" else P["b_fill"]
    accent = P["a"] if row == "A" else P["b"]
    stroke = P["sel"] if selected else P["rule"]
    s.rect(x, y, 86, 42, fill, stroke, 2 if selected else 1, 5)
    s.rect(x, y, 4, 42, accent, "none", 0, 4)
    s.text(x + 43, y + 21, label, 12, P["ink"], 650, "middle", mono=True)


def draw_case(s, x, y, k, pivot, sign, title):
    n = 2 * k
    s.text(x, y, title, 13, P["ink"], 650)
    s.text(x, y + 24, "PHYSICAL ROW", 10, P["muted"], 650, letter=0.7)
    py = y + 38
    for c in range(1, n + 1):
        face_box(s, x + (c - 1) * 92, py, f"F{c}")
    sx = x + pivot * 92 - 3
    s.line(sx, py - 7, sx, py + 49, P["sel"], 4)
    s.text(sx, py - 18, f"pivot seam p={pivot}", 10, P["sel"], 650, "middle")

    s.text(x, py + 72, f"ROW ORDER R{sign}(k,p)", 10, P["muted"], 650, letter=0.7)
    oy = py + 88
    order = row_order(k, pivot, sign)
    for i, c in enumerate(order):
        face_box(s, x + i * 92, oy, f"F{c}", selected=i in (0, len(order) - 1))
    s.text(x, oy + 60, f"first/last = F{order[0]}, F{order[-1]}  →  physical seam {pivot}", 11, P["muted"])


def render(out: Path):
    s = SVG(1320, 760)
    s.text(48, 48, "Row pivot normal-form lab", 30, P["ink"], 650)
    s.text(48, 82, "The pivot is a physical seam: it joins the first and last faces of the row layer order.", 14, P["muted"])
    s.rect(1040, 36, 230, 30, "#fff", P["ink"], 1, 15)
    s.text(1155, 51, "∀k  THEOREM · row-local", 11, P["ink"], 650, "middle")
    panel(s, 40, 112, 1240, 600, "k=3, pivot p=3 — same physical seam, opposite orientation", "A")
    draw_case(s, 82, 180, 3, 3, "+", "Effective sign +")
    s.line(82, 420, 1238, 420, P["rule"], 1)
    draw_case(s, 82, 454, 3, 3, "-", "Effective sign −")
    s.finish(out, "Row pivot normal-form lab", "Physical pivot seam and the corresponding row-local layer orders for both effective signs.")


if __name__ == "__main__":
    render(ROOT / "visualization/generated/02_row_pivot_lab.svg")
