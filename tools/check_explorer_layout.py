#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = [(1920,1080),(1440,900),(1366,768),(1280,720),(1024,768),(768,1024),(390,844)]
SCENES = {
    "mvmmmm-success": {"mechanism":"mvmmmm","a":"2","b":"3"},
    "mvmmmm-failure": {"mechanism":"mvmmmm","a":"2","b":"4"},
    "mmmmvv-diagonal": {"mechanism":"mmmmvv","scene":"diagonal"},
    "mmmmvv-boundary": {"mechanism":"mmmmvv","scene":"boundary"},
    "mmmmvv-obstruction-step1": {"mechanism":"mmmmvv","scene":"obstruction","step":"1"},
    "mmmmvv-obstruction-final": {"mechanism":"mmmmvv","scene":"obstruction","step":"4"},
}


def inline_harness() -> tuple[str, str]:
    html = (ROOT / "web/explorer/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/assets/css/site.css").read_text(encoding="utf-8")
    html = re.sub(r'<link rel="stylesheet"[^>]+>', f"<style>{css}</style>", html)
    html = re.sub(r'<script type="module"[^>]+></script>', '', html)

    data_root = ROOT / "build/site/data/explorer"
    mv = json.loads((data_root / "mvp-mvmmmm-k3-v1.json").read_text(encoding="utf-8"))
    mm = json.loads((data_root / "mmmmvv-scenes-v1.json").read_text(encoding="utf-8"))
    js = (ROOT / "web/assets/js/explorer.js").read_text(encoding="utf-8")
    js = re.sub(r"import \{loadJSON, qs, setQS\} from './common.js';\n", "", js)
    replacement = f"const mvData = {json.dumps(mv)};\nconst mmData = {json.dumps(mm)};"
    js = re.sub(
        r"const mvData = await loadJSON\([^\n]+\);\nconst mmData = await loadJSON\([^\n]+\);",
        lambda _: replacement,
        js,
    )
    prefix = (
        "const qs=(name,fallback=null)=>(window.__QS&&window.__QS[name]!=null?String(window.__QS[name]):fallback);"
        "const setQS=(values)=>{window.__QS={...(window.__QS||{}),...values};};\n"
    )
    return html, prefix + js


def launch_browser(p):
    explicit = os.environ.get("PER2_CHROMIUM_EXECUTABLE")
    candidates = [explicit, shutil.which("chromium"), shutil.which("chromium-browser"), shutil.which("google-chrome")]
    for exe in candidates:
        if exe:
            return p.chromium.launch(headless=True, executable_path=exe, args=["--no-sandbox"])
    return p.chromium.launch(headless=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Explorer in an inline Chromium harness and assert layout containment.")
    ap.add_argument("--screenshots", action="store_true")
    ap.add_argument("--out", default="build/layout_qa")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required for this optional visual-layout QA tool.") from exc

    if not (ROOT / "build/site/data/explorer/mvp-mvmmmm-k3-v1.json").exists():
        raise SystemExit("Run `PYTHONPATH=src:. python tools/build_web_preview.py` first.")

    html, js = inline_harness()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    failures: list[dict] = []

    eval_js = r'''() => {
      const R=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
      const doc=document.documentElement;
      const panelOf=e=>e.closest('.instrument-panel,.explorer-toolbar,.status-band,.explorer-head,.wrap');
      const selectors=['.controls label','.controls select','.check-control','#traceControls','#statusBand','.map-stage','.explorer-map-svg','.row-cards','.layer-panel','.global-layer-stack','.construction-summary','.witness-summary','.witness-panel','.cycle-witness-svg','.witness-edge-item','.proof-grid','.badge-stack','.badge'];
      const issues=[];
      if(doc.scrollWidth > doc.clientWidth + 2) issues.push({kind:'page-horizontal-overflow',scrollWidth:doc.scrollWidth,clientWidth:doc.clientWidth});
      for(const sel of selectors) for(const e of document.querySelectorAll(sel)){
        if(e.offsetParent===null) continue;
        const r=R(e), p=panelOf(e), pr=p?R(p):null, cs=getComputedStyle(e);
        if(pr && (r.left<pr.left-2||r.right>pr.right+2||r.top<pr.top-2||r.bottom>pr.bottom+2))
          issues.push({kind:'bbox-outside-panel',selector:sel,text:(e.textContent||'').trim().slice(0,80),rect:r,parentRect:pr});
        const intentionalScroll=['auto','scroll'].includes(cs.overflowX)||['auto','scroll'].includes(cs.overflowY);
        if(!intentionalScroll && (e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))
          issues.push({kind:'uncontained-scroll-size',selector:sel,text:(e.textContent||'').trim().slice(0,80),scroll:[e.scrollWidth,e.scrollHeight],client:[e.clientWidth,e.clientHeight]});
      }
      for(const e of document.querySelectorAll('svg text')){
        const svg=e.closest('svg'); if(!svg)continue; const r=R(e), sr=R(svg);
        if(r.left<sr.left-2||r.right>sr.right+2||r.top<sr.top-2||r.bottom>sr.bottom+2)
          issues.push({kind:'svg-text-outside',text:e.textContent,rect:r,svgRect:sr});
      }
      return {issues,body:{scrollWidth:doc.scrollWidth,clientWidth:doc.clientWidth}};
    }'''

    with sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_page()
        for width, height in VIEWPORTS:
            page.set_viewport_size({"width":width,"height":height})
            for scene, query in SCENES.items():
                page.set_content(html, wait_until="domcontentloaded")
                page.evaluate("q=>window.__QS=q", query)
                page.add_script_tag(type="module", content=js)
                page.wait_for_timeout(60)
                result = page.evaluate(eval_js)
                rec = {"scene":scene,"viewport":[width,height],**result}
                records.append(rec)
                if result["issues"]:
                    failures.append(rec)
                if args.screenshots and (width,height) in {(1440,900),(1024,768),(390,844)}:
                    page.screenshot(path=str(out / f"{scene}_{width}x{height}.png"), full_page=True)
        browser.close()

    report = {"viewports":VIEWPORTS,"scenes":list(SCENES),"records":records,"failure_count":len(failures)}
    (out / "layout_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if failures:
        for rec in failures:
            print(f"FAIL {rec['scene']} @ {rec['viewport']}: {len(rec['issues'])} issue(s)")
            for issue in rec["issues"][:8]:
                print("  ", issue)
        return 1
    print(f"PASS: {len(records)} scene/viewport renders; no containment failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
