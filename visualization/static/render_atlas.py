from __future__ import annotations

import csv
from pathlib import Path

from per2.model import PeriodWord
from per2.theory import classify_period
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]

REGIME_STYLE = {
    "ZERO": (P["bad_fill"], P["bad"], "×"),
    "PLEAT": ("#F3F0FA", P["sel"], "◆"),
    "CONSTANT_RHO_PLUS": ("#EDF5FC", P["a"], "■"),
    "CONSTANT_RHO_MINUS": (P["ok_fill"], P["ok"], "●"),
}


def bit_index(bits: str) -> int:
    return int("".join("0" if c == "M" else "1" for c in bits), 2)


def render(out: Path) -> None:
    rows = list(csv.DictReader((ROOT / "reference/classification/all64.csv").open()))
    s = SVG(1320, 860)
    s.text(48, 48, "64-word regime atlas", 30, P["ink"], 650)
    s.text(48, 82, "All formal period-2 assignments. Cells encode theorem regime, not state count.", 14, P["muted"])
    s.rect(1040, 36, 230, 30, "#fff", P["ink"], 1, 15)
    s.text(1155, 51, "∀k  THEOREM · k≥2", 11, P["ink"], 650, "middle")
    panel(s, 40, 112, 900, 700, "Assignment atlas", "A", "row bits h0 h1 u0 · column bits u1 l0 l1")
    panel(s, 960, 112, 320, 700, "Legend & selected sentinels", "B")

    x0, y0, cw, ch = 78, 176, 102, 68
    by_word = {r["P"]: r for r in rows}
    for r in rows:
        word = r["P"]
        ri = bit_index(word[:3])
        ci = bit_index(word[3:])
        x, y = x0 + ci * cw, y0 + ri * ch
        fill, stroke, glyph = REGIME_STYLE[r["regime"]]
        s.rect(x, y, cw - 8, ch - 8, fill, stroke, 1.4, 6)
        s.text(x + 10, y + 19, word, 11, P["ink"], 650, mono=True)
        s.text(x + cw - 22, y + 20, glyph, 16, stroke, 650, "middle")
        short = {"ZERO": "zero", "PLEAT": "pleat", "CONSTANT_RHO_PLUS": "ρ+", "CONSTANT_RHO_MINUS": "ρ−"}[r["regime"]]
        s.text(x + 10, y + 43, short, 10, P["muted"], 500)

    lx, ly = 990, 178
    for regime in ("ZERO", "PLEAT", "CONSTANT_RHO_PLUS", "CONSTANT_RHO_MINUS"):
        fill, stroke, glyph = REGIME_STYLE[regime]
        s.rect(lx, ly, 30, 30, fill, stroke, 1.2, 5)
        s.text(lx + 15, ly + 15, glyph, 13, stroke, 650, "middle")
        label = {
            "ZERO": "48 locally obstructed",
            "PLEAT": "8 pleat singletons",
            "CONSTANT_RHO_PLUS": "4 constant-row ρ=+1",
            "CONSTANT_RHO_MINUS": "4 constant-row ρ=−1",
        }[regime]
        s.text(lx + 42, ly + 15, label, 11.5, P["ink"], 550)
        ly += 46

    ly += 18
    s.text(lx, ly, "SENTINELS", 10, P["muted"], 650, letter=0.8)
    ly += 24
    for word in ("MMMMVV", "MVMMMM", "MMMVVM", "MMMMMM"):
        r = by_word[word]
        fill, stroke, glyph = REGIME_STYLE[r["regime"]]
        s.text(lx, ly, word, 12, P["ink"], 650, mono=True)
        s.text(lx + 98, ly, glyph, 13, stroke, 650)
        s.text(lx + 122, ly, r["regime"].replace("CONSTANT_", ""), 10.5, P["muted"], 500)
        ly += 26
        if r["canonical_source_family"] != "N/A":
            s.text(lx + 12, ly, f"→ {r['canonical_source_family']} via {r['exact_transport']}", 10.5, P["muted"])
            ly += 30
        else:
            ly += 8

    s.text(78, 790, "M=0 / V=1 is used only to place words in the 8×8 atlas; literal M/V labels remain primary.", 11, P["muted"])
    s.finish(out, "64-word regime atlas", "Theorem-derived classification of all 64 period-2 M/V words into four regimes.")


if __name__ == "__main__":
    render(ROOT / "visualization/generated/01_regime_atlas.svg")
