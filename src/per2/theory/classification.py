from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from per2.model import PeriodWord
from per2.transforms import Transform, transform_word
from .invariants import invariants

Regime = Literal["ZERO", "PLEAT", "CONSTANT_RHO_PLUS", "CONSTANT_RHO_MINUS"]


@dataclass(frozen=True)
class Classification:
    word: str
    regime: Regime
    rho: int
    tau: int
    delta0: int
    delta1: int
    canonical_source: str
    transport: Transform | None
    compatibility_rule: str | None
    count_formula: str
    state_family: str

    def as_dict(self) -> dict:
        return asdict(self)


def _choose_transport(word: PeriodWord, regime: Regime, rho: int) -> tuple[str, Transform]:
    if regime == "PLEAT":
        base = PeriodWord.from_code("MMMVVM" if rho == 1 else "MVMVMV")
        ops: tuple[Transform, ...] = ("I", "R", "CR", "C") if rho == 1 else ("I", "H", "C", "CH")
    elif regime == "CONSTANT_RHO_PLUS":
        base = PeriodWord.from_code("MMMMVV")
        ops = ("I", "R", "CR", "C")
    elif regime == "CONSTANT_RHO_MINUS":
        base = PeriodWord.from_code("MVMMMM")
        ops = ("I", "H", "C", "CH")
    else:
        raise ValueError("ZERO regime has no canonical source")
    for op in ops:
        if transform_word(base, op) == word:
            return base.code, op
    raise AssertionError((word.code, regime, rho))


def classify_period(word: PeriodWord) -> Classification:
    inv = invariants(word)
    if inv.delta0 != -1 or inv.delta1 != -1:
        return Classification(
            word.code,
            "ZERO",
            inv.rho,
            inv.tau,
            inv.delta0,
            inv.delta1,
            "",
            None,
            None,
            "0",
            "empty exact state set",
        )
    if inv.tau == -1:
        regime: Regime = "PLEAT"
        base, op = _choose_transport(word, regime, inv.rho)
        return Classification(
            word.code,
            regime,
            inv.rho,
            inv.tau,
            inv.delta0,
            inv.delta1,
            base,
            op,
            None,
            "1",
            "exact singleton transported from canonical pleat order",
        )
    if inv.rho == 1:
        regime = "CONSTANT_RHO_PLUS"
        base, op = _choose_transport(word, regime, inv.rho)
        compat = "alpha=1 OR alpha=m OR alpha=beta" if op in ("I", "C") else "beta=1 OR beta=m OR alpha=beta"
        return Classification(
            word.code,
            regime,
            inv.rho,
            inv.tau,
            inv.delta0,
            inv.delta1,
            base,
            op,
            compat,
            "6k-5",
            "exact transported MMMMVV singleton pivot fibres",
        )
    regime = "CONSTANT_RHO_MINUS"
    base, op = _choose_transport(word, regime, inv.rho)
    compat = "B_R(alpha)=B_R(beta)" if op in ("I", "C") else "B_L(alpha)=B_L(beta)"
    return Classification(
        word.code,
        regime,
        inv.rho,
        inv.tau,
        inv.delta0,
        inv.delta1,
        base,
        op,
        compat,
        "4k-3",
        "exact transported MVMMMM singleton block fibres",
    )
