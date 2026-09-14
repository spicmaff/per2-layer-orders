from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from per2.model import Crease, ExplicitMap
from .orientation import light_up_by_checkerboard, target_class


@dataclass(frozen=True)
class CompiledConstraints:
    precedence: tuple[tuple[int, int, str], ...]
    butterfly_pairs: tuple[tuple[Crease, Crease], ...]


def compile_constraints(m: ExplicitMap) -> CompiledConstraints:
    precedence: list[tuple[int, int, str]] = []
    for crease in m.creases:
        la = light_up_by_checkerboard(m, crease.a)
        lb = light_up_by_checkerboard(m, crease.b)
        if la == lb:
            raise AssertionError(f"adjacent faces must have opposite checkerboard orientation: {crease.key}")
        light, dark = (crease.a, crease.b) if la else (crease.b, crease.a)
        above, below = (light, dark) if crease.label == "M" else (dark, light)
        precedence.append((above, below, crease.key))

    pairs: list[tuple[Crease, Crease]] = []
    for c1, c2 in combinations(m.creases, 2):
        if target_class(c1) != target_class(c2):
            continue
        if set(c1.wings) & set(c2.wings):
            continue
        pairs.append((c1, c2))
    return CompiledConstraints(tuple(precedence), tuple(pairs))
