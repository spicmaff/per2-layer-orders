from __future__ import annotations

import hashlib
import json
from pathlib import Path

from per2.model import all_period_words, face_label
from per2.period import expand_period
from per2.semantics import enumerate_states, validate_state
from per2.theory import recover_pivots
from .provenance import provenance


def _state_id(word: str, labels: list[str]) -> str:
    raw = (word + "|" + ",".join(labels)).encode()
    return f"k2:{word}:{hashlib.sha256(raw).hexdigest()[:16]}"


def build_k2_exact_states() -> dict:
    words = []
    total = 0
    for word in all_period_words():
        m = expand_period(word, 2)
        states = enumerate_states(m)
        entries = []
        for state in sorted(states):
            labels = [face_label(4, fid) for fid in state]
            upper = [label for label in labels if label.startswith("A")]
            lower = [label for label in labels if label.startswith("B")]
            pivots = None
            try:
                a, b = recover_pivots(state, 4)
                pivots = {"upper": a, "lower": b}
            except ValueError:
                pass
            features = {"pivots": pivots}
            if pivots is not None:
                features["pivots_provenance"] = provenance(
                    "theorem_derived",
                    "per2.theory.pivots.recover_pivots",
                    k=2,
                    word=word.code,
                    scope="annotation on independently enumerated state",
                )
            entries.append({
                "state_id": _state_id(word.code, labels),
                "order_labels": labels,
                "order_ids": list(state),
                "row_orders": {"upper": upper, "lower": lower},
                "features": features,
                "semantic_validation": {
                    "accepted": validate_state(m, state),
                    "provenance": provenance(
                        "independent_finite_validation",
                        "per2.semantics.validity.validate_state",
                        k=2,
                        word=word.code,
                    ),
                },
            })
        total += len(entries)
        words.append({"word": word.code, "states": entries})
    if total != 56:
        raise AssertionError(total)
    return {
        "schema_version": "1.0",
        "dataset_id": "per2.validation.k2_exact_states",
        "provenance": provenance(
            "independent_finite_validation",
            "per2.semantics.enumeration",
            k=2,
            oracle="PER2_FINAL_LAYER_ORDER_SEMANTICS",
        ),
        "total_states": total,
        "words": words,
    }


def write_k2_exact_states(path: Path) -> None:
    payload = build_k2_exact_states()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
