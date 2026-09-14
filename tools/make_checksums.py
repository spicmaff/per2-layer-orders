#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "reference").resolve()
out = root / "manifests" / "SHA256SUMS.txt"
out.parent.mkdir(parents=True, exist_ok=True)
lines = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and p != out and not p.name.endswith(".generated.csv")):
    rel = path.relative_to(root)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.append(f"{digest}  {rel.as_posix()}")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} ({len(lines)} files)")
