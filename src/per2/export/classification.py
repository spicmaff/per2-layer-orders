from __future__ import annotations

import csv
import json
from pathlib import Path

from per2.model import all_period_words
from per2.theory import classify_period
from .provenance import provenance


def all64_records() -> list[dict]:
    rows = []
    for word in all_period_words():
        c = classify_period(word)
        rows.append({
            "P": c.word,
            "h0": c.word[0],
            "h1": c.word[1],
            "u0": c.word[2],
            "u1": c.word[3],
            "l0": c.word[4],
            "l1": c.word[5],
            "delta0": str(c.delta0),
            "delta1": str(c.delta1),
            "tau": str(c.tau),
            "rho": str(c.rho),
            "regime": c.regime,
            "canonical_source_family": c.canonical_source or "N/A",
            "exact_transport": c.transport or "N/A",
            "compatibility_rule": c.compatibility_rule or "N/A",
            "state_family_descriptor": c.state_family,
            "C_P(k)": c.count_formula,
        })
    return rows


def write_all64_csv(path: Path) -> None:
    rows = all64_records()
    fields = list(rows[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_site_classification_json(path: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "dataset_id": "per2.theorem.all64",
        "provenance": provenance("theorem_derived", "per2.theory.classification", scope="all k>=2"),
        "records": all64_records(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
