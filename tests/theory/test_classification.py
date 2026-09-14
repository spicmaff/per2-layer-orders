from collections import Counter

from per2.model import all_period_words, PeriodWord
from per2.theory import classify_period


def test_all64_partition():
    counts = Counter(classify_period(w).regime for w in all_period_words())
    assert counts == {"ZERO": 48, "PLEAT": 8, "CONSTANT_RHO_PLUS": 4, "CONSTANT_RHO_MINUS": 4}


def test_canonical_words():
    assert classify_period(PeriodWord.from_code("MMMMVV")).compatibility_rule == "alpha=1 OR alpha=m OR alpha=beta"
    assert classify_period(PeriodWord.from_code("MVMMMM")).compatibility_rule == "B_R(alpha)=B_R(beta)"
