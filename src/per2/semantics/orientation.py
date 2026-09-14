from __future__ import annotations

from per2.model import Crease, ExplicitMap, face_rc


def light_up_by_checkerboard(m: ExplicitMap, fid: int) -> bool:
    row, col = face_rc(m.n, fid)
    return ((row + col - 1) % 2) == 0


def target_class(crease: Crease) -> str:
    if crease.kind == "H":
        return "S"
    if crease.kind in ("U", "L"):
        return "E" if crease.index % 2 == 1 else "W"
    raise AssertionError(crease.kind)
