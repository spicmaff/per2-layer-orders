"""Minimal theorem-side classification example."""
from __future__ import annotations

import json

from per2.model import PeriodWord
from per2.theory import classify_period

word = PeriodWord.from_code("MMMMVV")
record = classify_period(word).as_dict()
record["k_example"] = 4
print(json.dumps(record, indent=2))
