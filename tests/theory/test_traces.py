from per2.theory import mvmmmm_lifo_trace


def test_mvmmmm_mvp_success_trace():
    tr = mvmmmm_lifo_trace(3, 2, 3)
    assert tr.compatible
    assert len(tr.events) == 12
    assert tr.events[-1].stack_after == ()


def test_mvmmmm_mvp_failure_trace():
    tr = mvmmmm_lifo_trace(3, 2, 4)
    assert not tr.compatible
    assert tr.failure == {
        "type": "BURIED_CLOSER",
        "requested_closer": 3,
        "blocking_label": 6,
        "stack": [3, 5, 6],
    }
    assert tr.events[-1].face == "B3"
    assert tr.events[-1].reason_code == "BURIED_CLOSER"
