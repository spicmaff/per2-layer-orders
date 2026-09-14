from __future__ import annotations

from .model import ExplicitMap, PeriodWord, build_explicit_map


def expand_period(word: PeriodWord, k: int) -> ExplicitMap:
    if k < 1:
        raise ValueError("k must be >= 1")
    n = 2 * k
    h = (word.h0, word.h1)
    u = (word.u0, word.u1)
    l = (word.l0, word.l1)
    labels: dict[str, str] = {}
    for c in range(1, n + 1):
        labels[f"H{c}"] = h[(c - 1) % 2]
    for c in range(1, n):
        labels[f"U{c}"] = u[(c - 1) % 2]
        labels[f"L{c}"] = l[(c - 1) % 2]
    return build_explicit_map(n, labels)  # type: ignore[arg-type]
