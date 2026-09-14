from __future__ import annotations

from typing import Literal

from .model import PeriodWord, face_rc, face_id

Transform = Literal["I", "C", "R", "H", "CR", "CH"]


def _comp(ch: str) -> str:
    return "V" if ch == "M" else "M"


def transform_word(word: PeriodWord, op: Transform) -> PeriodWord:
    h0, h1, u0, u1, l0, l1 = word.as_tuple()
    if op == "I":
        code = word.code
    elif op == "C":
        code = "".join(_comp(x) for x in word.code)
    elif op == "R":
        code = h0 + h1 + l0 + l1 + u0 + u1
    elif op == "H":
        code = h1 + h0 + u0 + u1 + l0 + l1
    elif op == "CR":
        code = "".join(_comp(x) for x in (h0 + h1 + l0 + l1 + u0 + u1))
    elif op == "CH":
        code = "".join(_comp(x) for x in (h1 + h0 + u0 + u1 + l0 + l1))
    else:
        raise ValueError(op)
    return PeriodWord.from_code(code)


def _phi_r(state: tuple[int, ...], n: int) -> tuple[int, ...]:
    return tuple(x + n if x < n else x - n for x in state)


def _phi_h(state: tuple[int, ...], n: int) -> tuple[int, ...]:
    out: list[int] = []
    for fid in state:
        row, col = face_rc(n, fid)
        out.append(face_id(n, row, n + 1 - col))
    return tuple(out)


def transform_state(state: tuple[int, ...], n: int, op: Transform) -> tuple[int, ...]:
    if op == "I":
        return state
    if op == "C":
        return tuple(reversed(state))
    if op == "R":
        return tuple(reversed(_phi_r(state, n)))
    if op == "H":
        return tuple(reversed(_phi_h(state, n)))
    if op == "CR":
        return _phi_r(state, n)
    if op == "CH":
        return _phi_h(state, n)
    raise ValueError(op)
