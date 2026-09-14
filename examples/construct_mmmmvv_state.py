"""Construct one theorem-side MMMMVV state, then check it independently."""
from __future__ import annotations

import json

from per2.model import PeriodWord, parse_face_label
from per2.period import expand_period
from per2.semantics import validate_state
from per2.theory import mmmmvv_explicit_construction, recover_pivots

k, a, b = 4, 3, 3
construction = mmmmvv_explicit_construction(k, a, b)
map_model = expand_period(PeriodWord.from_code("MMMMVV"), k)
state = tuple(parse_face_label(2 * k, label) for label in construction.order_labels)
print(json.dumps({
    "family": "MMMMVV",
    "k": k,
    "requested_pivots": [a, b],
    "recovered_pivots": list(recover_pivots(state, 2 * k)),
    "order": list(construction.order_labels),
    "construction_family": construction.family,
    "theorem_derived_construction": True,
    "independent_semantic_acceptance": validate_state(map_model, state),
}, indent=2))
