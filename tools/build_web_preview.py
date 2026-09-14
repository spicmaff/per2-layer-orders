#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

from per2.export import write_site_classification_json
from per2.export.site_data import write_all_site_data

root = Path(__file__).resolve().parents[1]
out = root / "build/site"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(root / "web", out)
(out / "data").mkdir(parents=True, exist_ok=True)
write_site_classification_json(out / "data/classification-v1.json")
write_all_site_data(out / "data")
shutil.copytree(root / "visualization/generated", out / "visualization/generated", dirs_exist_ok=True)
shutil.copytree(root / "assets/physical_k6", out / "assets/physical_k6", dirs_exist_ok=True)
(out / "paper").mkdir(parents=True, exist_ok=True)
shutil.copy2(root / "paper/PER2_CANONICAL_MANUSCRIPT.pdf", out / "paper/PER2_CANONICAL_MANUSCRIPT.pdf")
(out / "supplements").mkdir(parents=True, exist_ok=True)
for name in ["M4_SUPPLEMENT_S1_TABLES.pdf", "M4_SUPPLEMENT_S2_VALIDATION.pdf", "M4_SUPPLEMENT_S3_REPRODUCIBILITY.pdf"]:
    shutil.copy2(root / "supplements" / name, out / "supplements" / name)

print(out)
