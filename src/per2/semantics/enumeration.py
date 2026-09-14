from __future__ import annotations

from itertools import permutations

from per2.model import ExplicitMap
from .constraints import compile_constraints
from .validity import validate_state


def enumerate_states(m: ExplicitMap, *, allow_large: bool = False) -> set[tuple[int, ...]]:
    if m.num_faces > 8 and not allow_large:
        raise ValueError(
            "full permutation enumeration is intentionally bounded to at most 8 faces by default; "
            "pass allow_large=True only for an explicitly reviewed finite experiment"
        )
    compiled = compile_constraints(m)
    out: set[tuple[int, ...]] = set()
    for order in permutations(m.faces):
        if validate_state(m, order, compiled):
            out.add(order)
    return out
