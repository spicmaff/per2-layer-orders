from __future__ import annotations

from collections import Counter

from per2.model import PeriodWord, all_period_words
from per2.period import expand_period
from per2.semantics import enumerate_states, validate_state
from per2.theory import classify_period, mmmmvv_compatible, mvmmmm_compatible, recover_pivots
from per2.transforms import Transform, transform_state, transform_word


OPS: tuple[Transform, ...] = ("C", "R", "H", "CR", "CH")


def run_full_finite_validation() -> dict:
    k2_sets: dict[str, set[tuple[int, ...]]] = {}
    for word in all_period_words():
        k2_sets[word.code] = enumerate_states(expand_period(word, 2))

    dist = Counter(len(states) for states in k2_sets.values())
    if dict(dist) != {0: 48, 1: 8, 7: 4, 5: 4}:
        raise AssertionError(dist)
    if sum(map(len, k2_sets.values())) != 56:
        raise AssertionError("expected 56 total k=2 states")

    mm_pivots = {recover_pivots(state, 4) for state in k2_sets["MMMMVV"]}
    mv_pivots = {recover_pivots(state, 4) for state in k2_sets["MVMMMM"]}
    expected_mm = {(a, b) for a in range(1, 4) for b in range(1, 4) if mmmmvv_compatible(2, a, b)}
    expected_mv = {(a, b) for a in range(1, 4) for b in range(1, 4) if mvmmmm_compatible(2, a, b)}
    if mm_pivots != expected_mm or mv_pivots != expected_mv:
        raise AssertionError((mm_pivots, expected_mm, mv_pivots, expected_mv))

    symmetry_checks = 0
    for code, src in k2_sets.items():
        for op in OPS:
            target_word = transform_word(PeriodWord.from_code(code), op).code
            image = {transform_state(state, 4, op) for state in src}
            if image != k2_sets[target_word]:
                raise AssertionError((code, op, target_word))
            symmetry_checks += 1

    k1_sets: dict[str, set[tuple[int, ...]]] = {}
    for word in all_period_words():
        k1_sets[word.code] = enumerate_states(expand_period(word, 1))
    if sum(bool(states) for states in k1_sets.values()) != 32:
        raise AssertionError("expected 32 singleton formal words at k=1")
    for code, states in k1_sets.items():
        projection = code[0] + code[1] + code[2] + code[4]
        sign = lambda ch: 1 if ch == "M" else -1
        expected_nonempty = sign(projection[0]) * sign(projection[1]) * sign(projection[2]) * sign(projection[3]) == -1
        if bool(states) != expected_nonempty:
            raise AssertionError((code, projection))

    # Cross-check theorem classification against exact k=2 counts.
    for code, states in k2_sets.items():
        c = classify_period(PeriodWord.from_code(code))
        expected_count = 0 if c.regime == "ZERO" else 1 if c.regime == "PLEAT" else 7 if c.regime == "CONSTANT_RHO_PLUS" else 5
        if len(states) != expected_count:
            raise AssertionError((code, len(states), c))

    return {
        "role": "independent_finite_validation",
        "status": "PASS",
        "k2": {
            "words": 64,
            "distribution": {str(k): v for k, v in sorted(dist.items())},
            "total_states": 56,
            "exact_sets_enumerated": True,
        },
        "canonical_MMMMVV": {"pivot_fibres": [list(p) for p in sorted(mm_pivots)]},
        "canonical_MVMMMM": {"pivot_fibres": [list(p) for p in sorted(mv_pivots)]},
        "symmetry": {"checks": symmetry_checks, "exact_state_set_checks": symmetry_checks},
        "k1": {"formal_words": 64, "singleton_formal_words": 32, "empty_formal_words": 32},
    }
