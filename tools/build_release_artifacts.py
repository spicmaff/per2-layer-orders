#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.0.0-rc1"
OUT = ROOT / "build" / "release"
FIXED_DT = (2026, 9, 14, 0, 0, 0)
SKIP_PARTS = {".git", ".venv", "build", "dist", ".pytest_cache", "__pycache__"}


def public_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_PARTS or part.endswith(".egg-info") for part in rel.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        result.append(path)
    return sorted(result, key=lambda p: p.relative_to(ROOT).as_posix())


def companion_files() -> list[Path]:
    candidates = [
        ROOT / "CITATION.cff",
        ROOT / "paper" / "PER2_CANONICAL_MANUSCRIPT.pdf",
        ROOT / "supplements" / "M4_SUPPLEMENT_S1_TABLES.pdf",
        ROOT / "supplements" / "M4_SUPPLEMENT_S2_VALIDATION.pdf",
        ROOT / "supplements" / "M4_SUPPLEMENT_S3_REPRODUCIBILITY.pdf",
        ROOT / "docs" / "REPRODUCIBILITY.md",
        ROOT / "docs" / "DATA_PROVENANCE.md",
        ROOT / "docs" / "ARCHIVAL_PROVENANCE.md",
        ROOT / "assets" / "physical_k6" / "README.md",
        ROOT / "assets" / "physical_k6" / "poster.svg",
        ROOT / "assets" / "physical_k6" / "validation.json",
        ROOT / "assets" / "physical_k6" / "physical_case.fold",
    ]
    candidates.extend(sorted((ROOT / "reference").rglob("*")))
    return sorted({p for p in candidates if p.is_file()}, key=lambda p: p.relative_to(ROOT).as_posix())


def write_zip(path: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src in files:
            rel = src.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            zf.writestr(info, src.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / f"per2-layer-orders-{VERSION}-source.zip"
    artifact = OUT / f"per2-layer-orders-{VERSION}-research-artifacts.zip"
    write_zip(source, public_files())
    write_zip(artifact, companion_files())
    lines = [f"{sha256(p)}  {p.name}" for p in (source, artifact)]
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(source)
    print(artifact)
    print(OUT / "SHA256SUMS.txt")


if __name__ == "__main__":
    main()
