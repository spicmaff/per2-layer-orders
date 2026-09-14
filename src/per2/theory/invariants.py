from __future__ import annotations

from dataclasses import dataclass

from per2.model import PeriodWord


def sign(mv: str) -> int:
    if mv == "M":
        return 1
    if mv == "V":
        return -1
    raise ValueError(mv)


@dataclass(frozen=True)
class Invariants:
    rho: int
    tau: int
    delta0: int
    delta1: int


def invariants(word: PeriodWord) -> Invariants:
    h0, h1, u0, u1, l0, l1 = map(sign, word.code)
    rho = h0 * h1
    tau = u0 * u1
    return Invariants(rho, tau, h0 * h1 * u0 * l0, h0 * h1 * u1 * l1)
