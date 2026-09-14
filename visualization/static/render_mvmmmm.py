from __future__ import annotations

from pathlib import Path

from per2.theory import br, mvmmmm_compatibility, mvmmmm_lifo_trace
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]


def _trace_rows(s, x, y, trace, max_rows=12):
    s.text(x, y, "STEP", 9, P["muted"], 650)
    s.text(x + 48, y, "FACE", 9, P["muted"], 650)
    s.text(x + 112, y, "EVENT", 9, P["muted"], 650)
    s.text(x + 185, y, "STACK AFTER  (bottom → top)", 9, P["muted"], 650)
    s.line(x, y + 14, x + 390, y + 14, P["rule"], 1)
    yy = y + 30
    for ev in trace.events[:max_rows]:
        bad = ev.status == "FAILED_CANDIDATE"
        if bad:
            s.rect(x - 6, yy - 13, 400, 28, P["bad_fill"], P["bad"], 1, 5, "4 3")
        s.text(x, yy, f"{ev.step:02d}", 9.5, P["muted"], 500, mono=True)
        s.text(x + 48, yy, ev.face, 10.5, P["ink"], 650, mono=True)
        s.text(x + 112, yy, ev.action, 10, P["bad"] if bad else P["forced"], 650)
        stack = " ".join(f"H{c}" for c in ev.stack_after) if ev.stack_after else "∅"
        s.text(x + 185, yy, stack, 9.5, P["ink"], 500, mono=True)
        yy += 30
    return yy


def render(out: Path, k: int = 4):
    m = 2 * k - 1
    s = SVG(1320, 980)
    s.text(48, 48, "Canonical MVMMMM — BR blocks and LIFO reconstruction", 30, P["ink"], 650)
    s.text(48, 82, "Compatible iff the two pivots lie in the same BR block. The horizontal merge is then forced.", 14, P["muted"])
    s.rect(1040, 36, 230, 30, "#fff", P["ink"], 1, 15)
    s.text(1155, 51, "∀k  THEOREM · all k≥2", 11, P["ink"], 650, "middle")
    panel(s, 40, 112, 610, 810, "Pivot block compatibility", "A", f"k={k}, m={m}")
    panel(s, 670, 112, 610, 810, "Forced stack traces", "B", "success vs first failure")

    x0, y0, cell = 110, 190, 62
    for b in range(1, m + 1):
        s.text(x0 + (b - .5) * cell, y0 - 16, str(b), 10.5, P["muted"], 600, "middle")
    for a in range(1, m + 1):
        s.text(x0 - 18, y0 + (a - .5) * cell, str(a), 10.5, P["muted"], 600, "middle")
        for b in range(1, m + 1):
            ok = mvmmmm_compatibility(k, a, b).compatible
            x, y = x0 + (b - 1) * cell, y0 + (a - 1) * cell
            fill = P["ok_fill"] if ok else "#fff"
            stroke = P["ok"] if ok else P["rule"]
            s.rect(x, y, cell - 5, cell - 5, fill, stroke, 1, 5)
            s.text(x + (cell - 5)/2, y + (cell - 5)/2, "✓" if ok else "×", 14, P["ok"] if ok else P["bad"], 700, "middle")
    s.text(x0 + m*cell/2, y0 - 42, "lower pivot b", 11, P["muted"], 650, "middle")
    s.text(x0 - 58, y0 + m*cell/2, "upper pivot a", 11, P["muted"], 650, "middle")

    # block legend
    ly = y0 + m * cell + 28
    s.text(90, ly, "BR blocks", 11, P["muted"], 650)
    x = 170
    for r in range(0, k):
        members = [1] if r == 0 else [2*r, 2*r+1]
        label = "{" + ",".join(map(str, members)) + "}"
        w = 58 if r == 0 else 78
        s.rect(x, ly - 13, w, 26, P["sel_fill"] if r == 0 else "#F7F8FA", P["sel"] if r == 0 else P["rule"], 1, 13)
        s.text(x + w/2, ly, f"Q{r}={label}", 9.5, P["ink"], 600, "middle")
        x += w + 10

    # show k=3 MVP traces even though matrix is k=4, explicitly labelled as sentinel examples
    s.text(710, 176, "k=3 EXPERT-MVP SENTINELS", 10, P["muted"], 650, letter=.7)
    success = mvmmmm_lifo_trace(3, 2, 3)
    failure = mvmmmm_lifo_trace(3, 2, 4)
    s.rect(710, 198, 530, 270, P["ok_fill"], P["ok"], 1, 7)
    s.text(730, 222, "SUCCESS  (a,b)=(2,3) · BR=1", 13, P["ok"], 650)
    y = _trace_rows(s, 730, 250, success, max_rows=7)
    s.text(730, 482, "… 12 events total. Complete: all faces consumed, stack = ∅.", 10.5, P["muted"], 550)

    s.rect(710, 510, 530, 390, P["bad_fill"], P["bad"], 1, 7)
    s.text(730, 534, "FAILURE  (a,b)=(2,4) · BR 1 ≠ 2", 13, P["bad"], 650)
    _trace_rows(s, 730, 562, type("T", (), {"events": failure.events[:-1]})(), max_rows=9)
    fail = failure.failure or {}
    s.text(730, 844, f"B{fail.get('requested_closer')} requests H{fail.get('requested_closer')}; stack is H3 H5 H6; top is H{fail.get('blocking_label')}.", 10.5, P["ink"], 600)
    s.rect(724, 862, 484, 34, "#FFFFFF", P["bad"], 1, 5, "4 3")
    s.text(742, 879, "STOP · B3 · BURIED_CLOSER ×", 10.5, P["bad"], 650)
    s.text(730, 910, "No invented events are shown after first failure.", 10.5, P["bad"], 650)
    s.text(730, 936, "H-compatible reconstruction is horizontal; full map validity is a separate theorem step.", 10, P["muted"])

    s.finish(out, "Canonical MVMMMM LIFO block lab", "BR-block compatibility matrix plus deterministic success and first-failure LIFO traces.")


if __name__ == "__main__":
    render(ROOT / "visualization/generated/04_mvmmmm_lab.svg")
