from __future__ import annotations

from pathlib import Path

from per2.theory import mmmmvv_compatibility
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]


def render(out: Path, k: int = 4, selected=(2, 1)) -> None:
    m = 2 * k - 1
    s = SVG(1320, 820)
    s.text(48, 48, "Canonical MMMMVV compatibility", 30, P["ink"], 650)
    s.text(48, 82, "Compatible iff the upper pivot is on a boundary or the two pivots are equal.", 14, P["muted"])
    s.rect(1040, 36, 230, 30, "#fff", P["ink"], 1, 15)
    s.text(1155, 51, "∀k  THEOREM · all k≥2", 11, P["ink"], 650, "middle")
    panel(s, 40, 112, 730, 650, "Ordered pivot fibres", "A", f"k={k}, m={m}")
    panel(s, 790, 112, 490, 650, "Selected obstruction witness", "B", f"(a,b)={selected}")

    x0, y0, cell = 128, 190, 66
    s.text(x0 + (m * cell) / 2, y0 - 42, "lower pivot b", 12, P["muted"], 650, "middle")
    s.text(x0 - 70, y0 + (m * cell) / 2, "upper pivot a", 12, P["muted"], 650, "middle")
    for b in range(1, m + 1):
        s.text(x0 + (b - 0.5) * cell, y0 - 16, str(b), 11, P["muted"], 600, "middle")
    for a in range(1, m + 1):
        s.text(x0 - 20, y0 + (a - 0.5) * cell, str(a), 11, P["muted"], 600, "middle")
        for b in range(1, m + 1):
            rec = mmmmvv_compatibility(k, a, b)
            x, y = x0 + (b - 1) * cell, y0 + (a - 1) * cell
            fill = P["ok_fill"] if rec.compatible else "#fff"
            stroke = P["ok"] if rec.compatible else P["rule"]
            if (a, b) == selected:
                stroke = P["sel"]
            s.rect(x, y, cell - 6, cell - 6, fill, stroke, 2 if (a, b) == selected else 1, 5)
            glyph = "✓" if rec.compatible else "×"
            color = P["ok"] if rec.compatible else P["bad"]
            s.text(x + (cell - 6) / 2, y + (cell - 6) / 2, glyph, 15, color, 700, "middle")

    # boundary brackets
    s.text(x0 + m * cell + 10, y0 + cell / 2 - 3, "a=1 boundary", 10, P["sel"], 600)
    s.text(x0 + m * cell + 10, y0 + (m - 0.5) * cell - 3, "a=m boundary", 10, P["sel"], 600)
    s.text(x0 + m * cell + 10, y0 + (m / 2) * cell, "diagonal", 10, P["muted"], 600)

    rec = mmmmvv_compatibility(k, *selected)
    bx, by = 830, 184
    if rec.compatible:
        s.text(bx, by, "Selected pair is compatible.", 16, P["ok"], 650)
        for i, reason in enumerate(rec.reasons):
            s.text(bx, by + 34 + i * 24, f"✓ {reason}", 12, P["ink"], 550)
    else:
        s.text(bx, by, "Interior off-diagonal pair is impossible.", 16, P["bad"], 650)
        w = rec.witness or {}
        cyc = w.get("cycle", [])
        s.text(bx, by + 40, "Directed four-cycle", 12, P["muted"], 650)
        cx, cy, gap = bx + 42, by + 98, 92
        points = []
        for idx, label in enumerate(cyc[:-1]):
            x = cx + idx * gap
            points.append((x, cy))
            s.circle(x, cy, 27, "#fff", P["bad"], 1.5)
            s.text(x, cy, label, 12, P["ink"], 650, "middle", mono=True)
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            if i < len(points) - 1:
                s.line(x1 + 27, y1, x2 - 27, y2, P["bad"], 2)
                s.text((x1 + x2) / 2, y1 - 14, "→", 17, P["bad"], 700, "middle")
            else:
                # return edge as a lower arc
                s.path(f"M {x1} {y1+27} Q {(x1+x2)/2} {y1+115} {x2} {y2+27}", P["bad"], 2)
                s.text((x1+x2)/2, y1 + 102, "cycle closes", 10, P["bad"], 650, "middle")
        origins = w.get("edge_origins", [])
        s.text(bx, by + 194, "Edge origins", 11, P["muted"], 650)
        for i, origin in enumerate(origins):
            s.text(bx + 12, by + 220 + 24 * i, f"{i+1}. {origin}", 11, P["ink"], 500)
        s.rect(bx, by + 342, 400, 90, P["bad_fill"], P["bad"], 1, 7)
        s.text(bx + 18, by + 368, "No total layer order can contain a strict directed cycle.", 12, P["ink"], 600)
        s.text(bx + 18, by + 395, "This is a theorem witness — not a failed physical folding animation.", 11, P["muted"])

    s.finish(out, "Canonical MMMMVV compatibility lab", "Boundary-or-diagonal compatibility matrix with a directed four-cycle obstruction witness.")


if __name__ == "__main__":
    render(ROOT / "visualization/generated/03_mmmmvv_lab.svg")
