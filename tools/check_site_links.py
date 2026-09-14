#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1] / "build/site"
attr = re.compile(r'(?:href|src)="([^"]+)"')
missing = []
for html in root.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    for link in attr.findall(text):
        if link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = (html.parent / urlparse(link).path).resolve()
        if link.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            missing.append((html.relative_to(root).as_posix(), link))
if missing:
    for item in missing:
        print("MISSING", item)
    raise SystemExit(1)
print("PASS: static Pages preview has no broken local href/src targets")
