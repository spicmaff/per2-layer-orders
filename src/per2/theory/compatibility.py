from __future__ import annotations

from dataclasses import asdict, dataclass

from .block_coordinates import br


@dataclass(frozen=True)
class CompatibilityRecord:
    compatible: bool
    reasons: tuple[str, ...]
    witness: dict | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def mmmmvv_compatibility(k: int, a: int, b: int) -> CompatibilityRecord:
    m = 2 * k - 1
    if not (1 <= a <= m and 1 <= b <= m):
        raise ValueError((k, a, b))
    reasons: list[str] = []
    if a == 1:
        reasons.append("UPPER_LEFT_BOUNDARY")
    if a == m:
        reasons.append("UPPER_RIGHT_BOUNDARY")
    if a == b:
        reasons.append("DIAGONAL")
    if reasons:
        return CompatibilityRecord(True, tuple(reasons), None)

    # Interior off-diagonal witness from Appendix D.2.
    if a % 2 == 1:
        s = (a + 1) // 2
        i, j = s + 1, s - 1
    else:
        s = a // 2
        i, j = s, s + 1
    o = 2 * i - 1
    e = 2 * j
    witness = {
        "type": "DIRECTED_FOUR_CYCLE",
        "i": i,
        "j": j,
        "odd_column": o,
        "even_column": e,
        "cycle": [f"A{e}", f"A{o}", f"B{o}", f"B{e}", f"A{e}"],
        "edge_origins": ["UPPER_ROW", "HORIZONTAL_ODD", "LOWER_ROW", "HORIZONTAL_EVEN"],
    }
    return CompatibilityRecord(False, ("INTERIOR_OFF_DIAGONAL",), witness)


def mmmmvv_compatible(k: int, a: int, b: int) -> bool:
    return mmmmvv_compatibility(k, a, b).compatible


def mvmmmm_compatibility(k: int, a: int, b: int) -> CompatibilityRecord:
    m = 2 * k - 1
    if not (1 <= a <= m and 1 <= b <= m):
        raise ValueError((k, a, b))
    ba, bb = br(a), br(b)
    if ba == bb:
        return CompatibilityRecord(True, ("EQUAL_BR_BLOCK",), {"br_a": ba, "br_b": bb})
    return CompatibilityRecord(False, ("UNEQUAL_BR_BLOCK",), {"br_a": ba, "br_b": bb})


def mvmmmm_compatible(k: int, a: int, b: int) -> bool:
    return mvmmmm_compatibility(k, a, b).compatible
