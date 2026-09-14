from per2.model import PeriodWord
from per2.period import expand_period
from per2.semantics import enumerate_states
from per2.theory import classify_period


def test_selected_cross_layer_counts():
    cases = {"MMMMVV": 7, "MVMMMM": 5, "MVMVMV": 1, "MMMMMM": 0}
    for code, expected in cases.items():
        states = enumerate_states(expand_period(PeriodWord.from_code(code), 2))
        assert len(states) == expected
        classification = classify_period(PeriodWord.from_code(code))
        assert classification.word == code
