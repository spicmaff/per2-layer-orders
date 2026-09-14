#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from per2.export import write_all64_csv, write_k2_exact_states, write_site_classification_json

root = Path(__file__).resolve().parents[1]
build = root / "build/reference-replay"
build.mkdir(parents=True, exist_ok=True)
write_all64_csv(build / "all64.csv")
write_site_classification_json(build / "classification-v1.json")
write_k2_exact_states(build / "k2_exact_states.json")
print(build)
