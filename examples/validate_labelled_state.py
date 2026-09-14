"""Validate one literal labelled state using theorem-blind semantics only."""
from __future__ import annotations

import json

from per2.model import PeriodWord, face_label, parse_face_label
from per2.period import expand_period
from per2.semantics import trace_state

word = PeriodWord.from_code("MVMVMV")
map_model = expand_period(word, 2)
labels = ["A1", "A2", "A3", "A4", "B4", "B3", "B2", "B1"]
state = tuple(parse_face_label(map_model.n, label) for label in labels)
trace = trace_state(map_model, state)
print(json.dumps({
    "word": word.code,
    "k": 2,
    "order": [face_label(map_model.n, fid) for fid in state],
    "accepted": trace["accepted"],
    "violations": trace["violations"],
    "epistemic_role": "independent_semantic_membership_check",
}, indent=2))
