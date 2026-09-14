#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ref = root / "reference"
out = ref / "manifests/reference-files.json"
entries = []
for path in sorted(p for p in ref.rglob("*") if p.is_file() and p != out and p.name != "SHA256SUMS.txt" and not p.name.endswith(".generated.csv")):
    entries.append({
        "path": path.relative_to(ref).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    })
payload = {
    "schema_version": "1.0",
    "canonical_baseline_sha256": "511031dc9eaff0bfc57fe32a15ff9d826d192c405908e096fec208bd643707df",
    "entries": entries,
    "generation_commands": [
        "per2 export-reference --root . --k2-states",
        "python tools/make_reference_manifest.py",
        "python tools/make_checksums.py reference"
    ]
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
print(out)
