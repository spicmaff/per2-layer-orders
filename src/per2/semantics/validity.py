from __future__ import annotations

from per2.model import Crease, ExplicitMap
from .constraints import CompiledConstraints, compile_constraints


def intervals_cross(pos: list[int], c1: Crease, c2: Crease) -> bool:
    a0, a1 = sorted((pos[c1.a], pos[c1.b]))
    b0, b1 = sorted((pos[c2.a], pos[c2.b]))
    return (a0 < b0 < a1 < b1) or (b0 < a0 < b1 < a1)


def validate_state(m: ExplicitMap, state: tuple[int, ...], compiled: CompiledConstraints | None = None) -> bool:
    if len(state) != m.num_faces or set(state) != set(m.faces):
        return False
    co = compiled or compile_constraints(m)
    pos = [0] * m.num_faces
    for i, face in enumerate(state):
        pos[face] = i
    for above, below, _ in co.precedence:
        if pos[above] >= pos[below]:
            return False
    for c1, c2 in co.butterfly_pairs:
        if intervals_cross(pos, c1, c2):
            return False
    return True


def trace_state(m: ExplicitMap, state: tuple[int, ...]) -> dict:
    co = compile_constraints(m)
    out: dict = {
        "oracle": "PER2_FINAL_LAYER_ORDER_SEMANTICS",
        "state": list(state),
        "accepted": False,
        "valid_shape": True,
        "violations": [],
    }
    if len(state) != m.num_faces or set(state) != set(m.faces):
        out["valid_shape"] = False
        out["violations"].append({"type": "MALFORMED_PERMUTATION"})
        return out
    pos = [0] * m.num_faces
    for i, face in enumerate(state):
        pos[face] = i
    for above, below, key in co.precedence:
        if pos[above] >= pos[below]:
            out["violations"].append(
                {"type": "MV_PRECEDENCE", "crease": key, "required_above": above, "required_below": below}
            )
    for c1, c2 in co.butterfly_pairs:
        if intervals_cross(pos, c1, c2):
            out["violations"].append(
                {"type": "BUTTERFLY_CROSSING", "creases": [c1.key, c2.key], "wings": [list(c1.wings), list(c2.wings)]}
            )
    out["accepted"] = not out["violations"]
    return out
