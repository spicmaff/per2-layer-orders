from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Iterator, Literal

MV = Literal["M", "V"]
CreaseKind = Literal["H", "U", "L"]


def face_id(n: int, row: int, col: int) -> int:
    if row not in (0, 1) or not (1 <= col <= n):
        raise ValueError((n, row, col))
    return row * n + (col - 1)


def face_rc(n: int, fid: int) -> tuple[int, int]:
    if not (0 <= fid < 2 * n):
        raise ValueError((n, fid))
    return fid // n, (fid % n) + 1


def face_label(n: int, fid: int) -> str:
    row, col = face_rc(n, fid)
    return f"{'A' if row == 0 else 'B'}{col}"


def parse_face_label(n: int, label: str) -> int:
    if len(label) < 2 or label[0] not in "AB":
        raise ValueError(label)
    col = int(label[1:])
    return face_id(n, 0 if label[0] == "A" else 1, col)


@dataclass(frozen=True, order=True)
class Crease:
    kind: CreaseKind
    index: int
    label: MV
    a: int
    b: int

    @property
    def key(self) -> str:
        return f"{self.kind}{self.index}"

    @property
    def wings(self) -> tuple[int, int]:
        return (self.a, self.b)


@dataclass(frozen=True)
class ExplicitMap:
    """Neutral explicit 2 x n map geometry plus prescribed M/V labels."""

    n: int
    creases: tuple[Crease, ...]

    def __post_init__(self) -> None:
        if self.n < 1:
            raise ValueError("n must be >= 1")
        expected = canonical_crease_keys(self.n)
        got = tuple(c.key for c in self.creases)
        if got != expected:
            raise ValueError(f"crease order/schema mismatch: expected {expected}, got {got}")
        expected_pairs = expected_crease_face_pairs(self.n)
        for crease in self.creases:
            if crease.label not in ("M", "V"):
                raise ValueError(f"invalid M/V label: {crease.label}")
            if tuple(sorted(crease.wings)) != tuple(sorted(expected_pairs[crease.key])):
                raise ValueError(f"wrong incident faces for {crease.key}: {crease.wings}")

    @property
    def num_faces(self) -> int:
        return 2 * self.n

    @property
    def faces(self) -> tuple[int, ...]:
        return tuple(range(self.num_faces))

    def crease_map(self) -> dict[str, Crease]:
        return {c.key: c for c in self.creases}


@dataclass(frozen=True)
class PeriodWord:
    h0: MV
    h1: MV
    u0: MV
    u1: MV
    l0: MV
    l1: MV

    def __post_init__(self) -> None:
        if any(v not in ("M", "V") for v in self.as_tuple()):
            raise ValueError(self.as_tuple())

    def as_tuple(self) -> tuple[MV, MV, MV, MV, MV, MV]:
        return (self.h0, self.h1, self.u0, self.u1, self.l0, self.l1)

    @property
    def code(self) -> str:
        return "".join(self.as_tuple())

    @classmethod
    def from_code(cls, code: str) -> "PeriodWord":
        if len(code) != 6 or any(ch not in "MV" for ch in code):
            raise ValueError("period word must be six letters M/V")
        return cls(*code)  # type: ignore[arg-type]

    @classmethod
    def from_tuple(cls, values: Iterable[MV]) -> "PeriodWord":
        vals = tuple(values)
        if len(vals) != 6:
            raise ValueError(vals)
        return cls(*vals)  # type: ignore[arg-type]


def all_period_words() -> Iterator[PeriodWord]:
    for vals in product(("M", "V"), repeat=6):
        yield PeriodWord.from_tuple(vals)


def canonical_crease_keys(n: int) -> tuple[str, ...]:
    return tuple(
        [f"H{c}" for c in range(1, n + 1)]
        + [f"U{c}" for c in range(1, n)]
        + [f"L{c}" for c in range(1, n)]
    )


def expected_crease_face_pairs(n: int) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for c in range(1, n + 1):
        out[f"H{c}"] = (face_id(n, 0, c), face_id(n, 1, c))
    for c in range(1, n):
        out[f"U{c}"] = (face_id(n, 0, c), face_id(n, 0, c + 1))
        out[f"L{c}"] = (face_id(n, 1, c), face_id(n, 1, c + 1))
    return out


def build_explicit_map(n: int, labels: dict[str, MV]) -> ExplicitMap:
    keys = canonical_crease_keys(n)
    if set(labels) != set(keys):
        raise ValueError(f"label keys differ from canonical 2 x {n} crease set")
    pairs = expected_crease_face_pairs(n)
    creases: list[Crease] = []
    for key in keys:
        kind: CreaseKind = key[0]  # type: ignore[assignment]
        idx = int(key[1:])
        a, b = pairs[key]
        creases.append(Crease(kind, idx, labels[key], a, b))
    return ExplicitMap(n=n, creases=tuple(creases))
