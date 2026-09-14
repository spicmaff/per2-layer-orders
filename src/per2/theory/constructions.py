from __future__ import annotations

from dataclasses import dataclass

from .compatibility import mmmmvv_compatibility
from .row_forms import row_order


@dataclass(frozen=True)
class MMMMVVConstruction:
    """Explicit Appendix-D construction for one compatible MMMMVV pivot pair.

    ``order_labels`` is a theorem-derived strict total order written top-to-bottom.
    This object is purely combinatorial; it is not a physical folding trajectory.
    """

    k: int
    a: int
    b: int
    family: str
    parameter_s: int | None
    order_labels: tuple[str, ...]


def _q(c: int) -> tuple[str, str]:
    return (f"A{c}", f"B{c}") if c % 2 else (f"B{c}", f"A{c}")


def _odd(r: int) -> int:
    return 2 * r - 1


def _even(r: int) -> int:
    return 2 * r


def _extend_q(out: list[str], columns) -> None:
    for c in columns:
        out.extend(_q(c))


def _diagonal(k: int, p: int) -> tuple[str, ...]:
    out: list[str] = []
    for c in row_order(k, p, "+"):
        out.extend(_q(c))
    return tuple(out)


def _left_odd(k: int, s: int) -> tuple[str, ...]:
    out: list[str] = []
    out += [f"A{_odd(r)}" for r in range(1, s + 1)]
    out += [f"B{_odd(r)}" for r in range(s, 0, -1)]
    out += [f"B{_even(r)}" for r in range(1, s)]
    _extend_q(out, (_odd(r) for r in range(s + 1, k + 1)))
    _extend_q(out, (_even(r) for r in range(k, s - 1, -1)))
    out += [f"A{_even(r)}" for r in range(s - 1, 0, -1)]
    return tuple(out)


def _left_even(k: int, s: int) -> tuple[str, ...]:
    out: list[str] = []
    out += [f"A{_odd(r)}" for r in range(1, s + 2)]
    out += [f"B{_odd(s + 1)}"]
    _extend_q(out, (_odd(r) for r in range(s + 2, k + 1)))
    _extend_q(out, (_even(r) for r in range(k, s, -1)))
    out += [f"B{_odd(r)}" for r in range(s, 0, -1)]
    out += [f"B{_even(r)}" for r in range(1, s + 1)]
    out += [f"A{_even(r)}" for r in range(s, 0, -1)]
    return tuple(out)


def _right_odd(k: int, s: int) -> tuple[str, ...]:
    out: list[str] = []
    out += [f"A{_odd(r)}" for r in range(k, s - 1, -1)]
    out += [f"B{_odd(s)}"]
    _extend_q(out, (_odd(r) for r in range(s - 1, 0, -1)))
    _extend_q(out, (_even(r) for r in range(1, s)))
    out += [f"B{_odd(r)}" for r in range(s + 1, k + 1)]
    out += [f"B{_even(r)}" for r in range(k, s - 1, -1)]
    out += [f"A{_even(r)}" for r in range(s, k + 1)]
    return tuple(out)


def _right_even(k: int, s: int) -> tuple[str, ...]:
    out: list[str] = []
    out += [f"A{_odd(r)}" for r in range(k, s, -1)]
    out += [f"B{_odd(r)}" for r in range(s + 1, k + 1)]
    out += [f"B{_even(r)}" for r in range(k, s, -1)]
    _extend_q(out, (_odd(r) for r in range(s, 0, -1)))
    _extend_q(out, (_even(r) for r in range(1, s + 1)))
    out += [f"A{_even(r)}" for r in range(s + 1, k + 1)]
    return tuple(out)


def mmmmvv_explicit_construction(k: int, a: int, b: int) -> MMMMVVConstruction:
    """Return the explicit Appendix-D construction for a compatible pair.

    The compatible set is exactly ``a=1`` or ``a=2k-1`` or ``a=b``.
    Endpoint overlaps are normalized to the diagonal family when ``a=b``.
    """
    rec = mmmmvv_compatibility(k, a, b)
    if not rec.compatible:
        raise ValueError(f"MMMMVV pivots {(a, b)} are incompatible")

    m = 2 * k - 1
    if a == b:
        return MMMMVVConstruction(k, a, b, "DIAGONAL", None, _diagonal(k, a))

    if a == 1:
        if b % 2:
            s = (b + 1) // 2
            order = _left_odd(k, s)
            family = "LEFT_ODD"
        else:
            s = b // 2
            order = _left_even(k, s)
            family = "LEFT_EVEN"
        return MMMMVVConstruction(k, a, b, family, s, order)

    if a == m:
        if b % 2:
            s = (b + 1) // 2
            order = _right_odd(k, s)
            family = "RIGHT_ODD"
        else:
            s = b // 2
            order = _right_even(k, s)
            family = "RIGHT_EVEN"
        return MMMMVVConstruction(k, a, b, family, s, order)

    raise AssertionError((k, a, b, rec))
