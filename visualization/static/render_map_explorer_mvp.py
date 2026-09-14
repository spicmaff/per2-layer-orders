from __future__ import annotations

import json
from pathlib import Path

from per2.export.site_data import write_map_explorer_mvp
from visualization.svg import SVG, P, panel

ROOT = Path(__file__).resolve().parents[2]


def face_card(s: SVG, x: float, y: float, label: str, w: float = 54, h: float = 28, selected: bool = False, failed: bool = False):
    row = label[0]
    fill = P["a_fill"] if row == "A" else P["b_fill"]
    stroke = P["bad"] if failed else (P["sel"] if selected else P["rule"])
    sw = 2.4 if (selected or failed) else 1
    s.rect(x, y, w, h, fill if not failed else P["bad_fill"], stroke, sw, 5, "4 3" if failed else None)
    s.rect(x, y, 4, h, P["a"] if row == "A" else P["b"], "none", 0, 4)
    s.text(x + w/2, y + h/2 + .5, label, 10.5, P["bad"] if failed else P["ink"], 650, "middle", mono=True)


def draw_map(s: SVG, x: float, y: float, pair: dict, data: dict, selected_face: str | None = None):
    cw, ch = 86, 55
    pivots = {f"crease:U{pair['a']}", f"crease:L{pair['b']}"}
    for f in data["map"]["faces"]:
        xx = x + (f["column"]-1)*cw
        yy = y if f["row"] == "A" else y+ch
        sel = f["id"] == selected_face
        s.rect(xx, yy, cw, ch, P["a_fill"] if f["row"]=="A" else P["b_fill"], P["sel"] if sel else P["rule"], 2 if sel else 1, 2)
        s.text(xx+cw/2, yy+ch/2, f["label"], 12, P["ink"], 650, "middle", mono=True)
    # H creases
    for c in data["map"]["creases"]:
        kind, idx = c["kind"], c["index"]
        if kind == "H":
            xx1=x+(idx-1)*cw; xx2=xx1+cw; yy=y+ch
            s.line(xx1,yy,xx2,yy,P["ink"],2,"6 4" if c["mv"]=="V" else None)
            s.text((xx1+xx2)/2, yy+12, f"H{idx}:{c['mv']}", 8.5, P["muted"], 600, "middle", mono=True)
        else:
            xx=x+idx*cw; yy1=y if kind=="U" else y+ch; yy2=yy1+ch
            col=P["sel"] if c["id"] in pivots else P["ink"]
            s.line(xx,yy1,xx,yy2,col,4 if c["id"] in pivots else 2,"6 4" if c["mv"]=="V" else None)
    s.text(x, y+2*ch+28, f"upper pivot U{pair['a']} · lower pivot L{pair['b']}", 10.5, P["sel"], 650)


def draw_rows(s: SVG, x: float, y: float, pair: dict, data: dict):
    for row, py, pivot in [("A", y, pair["a"]), ("B", y+128, pair["b"])]:
        rf=next(r for r in data["row_forms"][row] if r["pivot"]==pivot)
        s.text(x, py, f"{row} row · {'R⁺' if row=='A' else 'R⁻'} · p={pivot}", 11, P["ink"], 650)
        s.text(x, py+24, "PHYSICAL", 8.5, P["muted"], 650, letter=.6)
        for i,fid in enumerate(rf["physical_order_face_ids"]):
            face_card(s,x+80+i*58,py+11,fid.replace('face:',''),50,25)
            if i==pivot-1:
                s.line(x+80+(i+1)*58-4,py+8,x+80+(i+1)*58-4,py+41,P["sel"],3)
        s.text(x, py+72, "LAYER", 8.5, P["muted"], 650, letter=.6)
        for i,fid in enumerate(rf["layer_order_face_ids"]):
            label=fid.replace('face:','')
            selected=fid in {rf["first_face_id"],rf["last_face_id"]}
            face_card(s,x+80+i*58,py+59,label,50,25,selected)


def draw_layer(s: SVG, x: float, y: float, trace: dict, step: int):
    ev = trace["events"][step-1] if step else None
    prefix = ev["emitted_prefix_after"] if ev else []
    s.text(x,y,"TOP ↓",9,P["muted"],650)
    yy=y+18
    for i,label in enumerate(prefix):
        face_card(s,x+min(i,8)*2.5,yy+i*30,label,180,25,selected=(ev is not None and label==ev["face_label"]))
    if not prefix:
        s.text(x,yy+20,"No committed events",11,P["muted"],450)
    bottom=yy+max(1,len(prefix))*30+4
    if trace["success"] and step==len(trace["events"]):
        s.text(x,bottom,"✓ complete literal order · stack ∅",10,P["ok"],650)
    elif not trace["success"] and step==len(trace["events"]):
        cand=trace["failure"]["candidate_face_id"].replace('face:','')
        s.text(x,bottom,f"× STOP before {cand}; candidate not committed",10,P["bad"],650)


def draw_trace(s: SVG, x: float, y: float, trace: dict, step: int):
    ev = trace["events"][step-1] if step else None
    if ev:
        s.text(x,y,f"step {step}/{len(trace['events'])} · {ev['face_label']} · {ev['action'].upper()}",11,P["ink"],650)
        s.text(x,y+22,f"heads before: {ev['upper_head_before'] or '∅'} / {ev['lower_head_before'] or '∅'}",9.5,P["muted"],550,mono=True)
        stack=ev["stack_after_labels"]
        s.text(x,y+44,"stack after (bottom → top)",9,P["muted"],650)
        sx=x
        if stack:
            for i,h in enumerate(stack):
                s.rect(sx,y+58,45,24,P["sel_fill"] if i==len(stack)-1 else "#F8FAFB",P["sel"] if i==len(stack)-1 else P["rule"],1,4)
                s.text(sx+22.5,y+70,h,9.5,P["ink"],650,"middle",mono=True);sx+=50
        else:s.text(x,y+70,"∅",11,P["muted"],650,mono=True)
    yy=y+106
    s.text(x,yy,"STEP",8.5,P["muted"],650);s.text(x+42,yy,"FACE",8.5,P["muted"],650);s.text(x+102,yy,"ACTION",8.5,P["muted"],650);s.text(x+178,yy,"STACK AFTER",8.5,P["muted"],650)
    yy+=20
    for i,e in enumerate(trace["events"]):
        if i>=12:break
        current=i+1==step; failed=e["status"]=="failed_candidate"
        if current or failed:s.rect(x-5,yy-11,330,25,P["bad_fill"] if failed else P["sel_fill"],P["bad"] if failed else P["sel"],1,4,"4 3" if failed else None)
        s.text(x,yy,f"{i+1:02d}",8.5,P["muted"],500,mono=True);s.text(x+42,yy,e["face_label"],9.5,P["ink"],650,mono=True);s.text(x+102,yy,e["reason_code"] if failed else e["action"].upper(),8.8,P["bad"] if failed else P["forced"],650);s.text(x+178,yy," ".join(e["stack_after_labels"]) or "∅",8.5,P["ink"],500,mono=True)
        yy+=25


def render_case(out: Path, a: int, b: int):
    cache = ROOT / "build" / "explorer-mvp-render-data.json"
    write_map_explorer_mvp(cache)
    data=json.loads(cache.read_text())
    pair=next(p for p in data["pairs"] if p["a"]==a and p["b"]==b)
    trace=data["traces"][pair["trace_id"]]
    step=len(trace["events"])
    selected=trace["events"][-1]["face_id"] if trace["events"] else None
    s=SVG(1500,960)
    status="COMPATIBLE" if pair["compatible"] else "INCOMPATIBLE"
    scol=P["ok"] if pair["compatible"] else P["bad"]
    s.text(48,48,"Map & Layer-Order Explorer · expert MVP",30,P["ink"],650)
    s.text(48,80,f"k=3 · canonical MVMMMM · (a,b)=({a},{b}) · BR={pair['br_a']}/{pair['br_b']}",13,P["muted"],450)
    s.rect(1112,34,158,28,P["ok_fill"] if pair["compatible"] else P["bad_fill"],scol,1,14);s.text(1191,48,("✓ " if pair["compatible"] else "× ")+status,10.5,scol,650,"middle")
    s.rect(1280,34,172,28,"#FFF5DF","#A56600",1,14,"5 3");s.text(1366,48,"◇ NOT PHYSICAL MOTION",10,"#7A4A00",650,"middle")
    panel(s,40,112,900,310,"Map / crease pattern","A","physical 2×6 geometry")
    draw_map(s,90,176,pair,data,selected)
    panel(s,40,442,900,350,"Row normal forms","B","physical ↔ layer order")
    draw_rows(s,72,502,pair,data)
    panel(s,960,112,500,350,"Global layer order","C","top-to-bottom prefix")
    draw_layer(s,995,174,trace,step)
    panel(s,960,482,500,420,"LIFO reconstruction trace","D","theorem-derived events")
    draw_trace(s,995,542,trace,step)
    if not pair["compatible"] and trace["failure"]:
        f=trace["failure"];s.rect(48,816,860,58,P["bad_fill"],P["bad"],1,6,"4 3");s.text(68,838,f"STOP · {f['failure_type']} · requested {f['requested_closer']} · blocking top {f['blocking_label']}",11,P["bad"],650);s.text(68,858,"Failed candidate is not inserted into the committed layer order.",10,P["bad"],500)
    else:
        s.rect(48,816,860,58,P["ok_fill"],P["ok"],1,6);s.text(68,838,"COMPLETE · 12 committed faces · horizontal stack = ∅",11,P["ok"],650);s.text(68,858,"This is a theorem-derived combinatorial reconstruction, not a physical folding path.",10,P["muted"],500)
    s.finish(out,f"Map Explorer MVP MVMMMM ({a},{b})",f"Fixed k=3 canonical MVMMMM coordinated map, row order, global layer order, and LIFO trace for pivots ({a},{b}).")


if __name__ == "__main__":
    out=ROOT/"visualization/generated"
    render_case(out/"05_map_explorer_success.svg",2,3)
    render_case(out/"06_map_explorer_failure.svg",2,4)
