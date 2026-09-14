from __future__ import annotations

from typing import Literal

RowSign = Literal["+", "-"]


def column_word(k: int, pivot: int) -> tuple[int, ...]:
    """Column sequence W_p of the + row normal form from Proposition 6.1."""
    if k < 2:
        raise ValueError("generic row normal forms are used for k>=2")
    m = 2 * k - 1
    if not (1 <= pivot <= m):
        raise ValueError((k, pivot))
    if pivot % 2 == 1:
        s = (pivot + 1) // 2
        left_odds = list(range(2 * s - 1, 0, -2))
        left_evens = list(range(2, 2 * (s - 1) + 1, 2))
        right_odds = list(range(2 * (s + 1) - 1, 2 * k, 2))
        right_evens = list(range(2 * k, 2 * (s + 1) - 1, -2))
        cols = left_odds + left_evens + right_odds + right_evens + [2 * s]
    else:
        s = pivot // 2
        right_odds = list(range(2 * (s + 1) - 1, 2 * k, 2))
        right_evens = list(range(2 * k, 2 * (s + 1) - 1, -2))
        left_odds = list(range(2 * s - 1, 0, -2))
        left_evens = list(range(2, 2 * s + 1, 2))
        cols = right_odds + right_evens + left_odds + left_evens
    if len(cols) != 2 * k or len(set(cols)) != 2 * k:
        raise AssertionError((k, pivot, cols))
    return tuple(cols)


def row_order(k: int, pivot: int, sign: RowSign = "+") -> tuple[int, ...]:
    cols = column_word(k, pivot)
    return cols if sign == "+" else tuple(reversed(cols))


def row_formula_blocks(k: int, pivot: int) -> list[dict]:
    """Exact symbolic blocks used by the formula, for visual explanation."""
    if pivot % 2 == 1:
        s = (pivot + 1) // 2
        blocks = [
            ("odd-left", list(range(2 * s - 1, 0, -2))),
            ("even-left", list(range(2, 2 * (s - 1) + 1, 2))),
            ("odd-right", list(range(2 * (s + 1) - 1, 2 * k, 2))),
            ("even-right-desc", list(range(2 * k, 2 * (s + 1) - 1, -2))),
            ("pivot-even", [2 * s]),
        ]
    else:
        s = pivot // 2
        blocks = [
            ("odd-right", list(range(2 * (s + 1) - 1, 2 * k, 2))),
            ("even-right-desc", list(range(2 * k, 2 * (s + 1) - 1, -2))),
            ("odd-left-desc", list(range(2 * s - 1, 0, -2))),
            ("even-left", list(range(2, 2 * s + 1, 2))),
        ]
    return [{"name": name, "columns": cols} for name, cols in blocks if cols]
