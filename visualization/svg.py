from __future__ import annotations

from html import escape
from pathlib import Path

P = {
    "ink": "#17212B",
    "muted": "#66727F",
    "canvas": "#F4F6F8",
    "panel": "#FFFFFF",
    "rule": "#D9E0E6",
    "a": "#0072B2",
    "a_fill": "#EEF7FC",
    "b": "#D55E00",
    "b_fill": "#FFF4ED",
    "sel": "#6F42C1",
    "sel_fill": "#F5F0FC",
    "ok": "#008A67",
    "ok_fill": "#EAF7F2",
    "bad": "#B23A48",
    "bad_fill": "#FCEFF1",
    "forced": "#2864B7",
    "finite": "#5F6B76",
}


class SVG:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            '<style>text{font-family:Inter,Arial,Helvetica,sans-serif} .mono{font-family:"DejaVu Sans Mono",Consolas,monospace}</style>',
            f'<rect width="{width}" height="{height}" fill="{P["canvas"]}"/>',
        ]

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill, stroke="none", sw=1):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, text, size=14, fill=None, weight=400, anchor="start", mono=False, letter=None):
        cls = ' class="mono"' if mono else ""
        ls = f' letter-spacing="{letter}"' if letter is not None else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or P["ink"]}" font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="middle"{cls}{ls}>{escape(str(text))}</text>'
        )

    def path(self, d, stroke, sw=2, fill="none", dash=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}/>')

    def finish(self, path: Path, title: str, desc: str):
        self.parts.insert(2, f'<title>{escape(title)}</title><desc>{escape(desc)}</desc>')
        self.parts.append('</svg>')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts), encoding="utf-8")


def panel(s: SVG, x, y, w, h, title, letter=None, subtitle=None):
    s.rect(x, y, w, h, P["panel"], P["rule"], 1, 8)
    if letter:
        s.rect(x + 16, y + 14, 26, 26, "#fff", P["rule"], 1, 5)
        s.text(x + 29, y + 27, letter, 11, P["muted"], 650, "middle")
        tx = x + 54
    else:
        tx = x + 20
    s.text(tx, y + 27, title.upper(), 12, P["ink"], 650, letter=0.8)
    if subtitle:
        s.text(x + w - 18, y + 27, subtitle, 11, P["muted"], 450, "end")
    s.line(x + 16, y + 48, x + w - 16, y + 48, P["rule"], 1)
