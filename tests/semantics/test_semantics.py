from per2.model import PeriodWord, face_label
from per2.period import expand_period
from per2.semantics import enumerate_states, trace_state, validate_state


def test_k1_known_singleton_and_empty():
    m = expand_period(PeriodWord.from_code("MMMVVM"), 1)
    states = enumerate_states(m)
    assert len(states) == 1
    state = next(iter(states))
    assert [face_label(2, x) for x in state] == ["A1", "B1", "B2", "A2"]
    assert validate_state(m, state)
    assert trace_state(m, state)["accepted"] is True

    empty = enumerate_states(expand_period(PeriodWord.from_code("MMMMMM"), 1))
    assert not empty


def test_k2_canonical_counts():
    assert len(enumerate_states(expand_period(PeriodWord.from_code("MMMMVV"), 2))) == 7
    assert len(enumerate_states(expand_period(PeriodWord.from_code("MVMMMM"), 2))) == 5
    assert len(enumerate_states(expand_period(PeriodWord.from_code("MVMVMV"), 2))) == 1
