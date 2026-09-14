#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ref = root / "reference"
manifest_path = ref / "manifests/reference-files.json"
checksums_path = ref / "manifests/SHA256SUMS.txt"

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
expected = {entry["path"]: entry for entry in manifest["entries"]}
actual_paths = sorted(
    p.relative_to(ref).as_posix()
    for p in ref.rglob("*")
    if p.is_file() and p not in {manifest_path, checksums_path} and not p.name.endswith(".generated.csv")
)
if sorted(expected) != actual_paths:
    missing = sorted(set(expected) - set(actual_paths))
    extra = sorted(set(actual_paths) - set(expected))
    raise SystemExit(f"reference manifest file-set mismatch: missing={missing}, extra={extra}")

for rel in actual_paths:
    path = ref / rel
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = expected[rel]
    if entry["sha256"] != digest or entry["bytes"] != path.stat().st_size:
        raise SystemExit(f"reference manifest mismatch: {rel}")

checksum_lines = {}
for line in checksums_path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    digest, rel = line.split("  ", 1)
    checksum_lines[rel] = digest
expected_checksum_paths = sorted(
    p.relative_to(ref).as_posix()
    for p in ref.rglob("*")
    if p.is_file() and p != checksums_path and not p.name.endswith(".generated.csv")
)
if sorted(checksum_lines) != expected_checksum_paths:
    raise SystemExit("reference SHA256SUMS file-set mismatch")
for rel in expected_checksum_paths:
    digest = hashlib.sha256((ref / rel).read_bytes()).hexdigest()
    if checksum_lines[rel] != digest:
        raise SystemExit(f"reference SHA256SUMS mismatch: {rel}")

print(f"PASS: reference manifest/checksums cover {len(actual_paths)} scientific/reference files")
