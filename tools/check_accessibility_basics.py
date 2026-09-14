#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class Checker(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.issues: list[str] = []
        self.has_main = False
        self.has_title = False
        self.html_lang = None
        self.label_depth = 0

    @staticmethod
    def attrs_dict(attrs):
        return {k: v for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        a = self.attrs_dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "main":
            self.has_main = True
        elif tag == "title":
            self.has_title = True
        elif tag == "label":
            self.label_depth += 1
        elif tag == "img" and "alt" not in a:
            self.issues.append("img missing alt")
        elif tag == "video" and "controls" not in a:
            self.issues.append("video missing controls")
        elif tag == "button" and not a.get("type"):
            self.issues.append("button missing explicit type")
        elif tag in {"select", "input"}:
            if self.label_depth == 0 and not (a.get("aria-label") or a.get("aria-labelledby")):
                self.issues.append(f"{tag} has no enclosing label or aria label")

    def handle_endtag(self, tag):
        if tag == "label" and self.label_depth:
            self.label_depth -= 1

    def finish(self):
        if not self.html_lang:
            self.issues.append("html missing lang")
        if not self.has_main:
            self.issues.append("page missing main landmark")
        if not self.has_title:
            self.issues.append("page missing title")


issues: list[str] = []
for path in sorted(WEB.rglob("*.html")):
    c = Checker(path)
    c.feed(path.read_text(encoding="utf-8"))
    c.finish()
    issues.extend(f"{path.relative_to(ROOT)}: {item}" for item in c.issues)

if issues:
    raise SystemExit("basic accessibility policy failed:\n" + "\n".join(issues))
print(f"PASS: basic static accessibility policy ({len(list(WEB.rglob('*.html')))} HTML pages checked)")
