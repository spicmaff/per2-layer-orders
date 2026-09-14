from __future__ import annotations


def br(p: int) -> int:
    if p < 1:
        raise ValueError(p)
    return 0 if p == 1 else p // 2


def bl(p: int, n: int) -> int:
    if not (1 <= p <= n - 1):
        raise ValueError((p, n))
    return br(n - p)


def br_blocks(k: int) -> list[tuple[int, ...]]:
    return [(1,)] + [(2 * r, 2 * r + 1) for r in range(1, k)]
