from __future__ import annotations

from per2.model import face_rc
from per2.transforms import Transform


def recover_row_pivot(state: tuple[int, ...], n: int, row: int) -> int:
    ids = set(range(row * n, (row + 1) * n))
    seq = [face for face in state if face in ids]
    if len(seq) != n:
        raise ValueError("state does not contain exactly one copy of every row face")
    c1 = face_rc(n, seq[0])[1]
    c2 = face_rc(n, seq[-1])[1]
    if abs(c1 - c2) != 1:
        raise ValueError("row extremes are not incident to a physical seam")
    return min(c1, c2)


def recover_pivots(state: tuple[int, ...], n: int) -> tuple[int, int]:
    return recover_row_pivot(state, n, 0), recover_row_pivot(state, n, 1)


def expected_pivot_transform(op: Transform, a: int, b: int, n: int) -> tuple[int, int]:
    if op in ("I", "C"):
        return a, b
    if op in ("R", "CR"):
        return b, a
    if op in ("H", "CH"):
        return n - a, n - b
    raise ValueError(op)
