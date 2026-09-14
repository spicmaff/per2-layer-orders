from per2.model import PeriodWord, parse_face_label
from per2.period import expand_period
from per2.semantics import validate_state
from per2.theory import mmmmvv_compatibility, mmmmvv_explicit_construction, recover_pivots


def _state_ids(k: int, labels: tuple[str, ...]) -> tuple[int, ...]:
    n = 2 * k
    return tuple(parse_face_label(n, label) for label in labels)


def test_all_allowed_mmmmvv_pairs_have_valid_explicit_constructions_small_k():
    # This is a bounded independent semantic check of the already-proved
    # Appendix-D construction formulas, not the all-k proof.
    for k in range(2, 7):
        m = 2 * k - 1
        model = expand_period(PeriodWord.from_code("MMMMVV"), k)
        for a in range(1, m + 1):
            for b in range(1, m + 1):
                comp = mmmmvv_compatibility(k, a, b)
                if not comp.compatible:
                    continue
                construction = mmmmvv_explicit_construction(k, a, b)
                assert len(construction.order_labels) == 4 * k
                assert len(set(construction.order_labels)) == 4 * k
                state = _state_ids(k, construction.order_labels)
                assert recover_pivots(state, 2 * k) == (a, b)
                assert validate_state(model, state)


def test_mmmmvv_construction_family_sentinels():
    assert mmmmvv_explicit_construction(4, 3, 3).family == "DIAGONAL"
    left = mmmmvv_explicit_construction(4, 1, 4)
    assert (left.family, left.parameter_s) == ("LEFT_EVEN", 2)
    right = mmmmvv_explicit_construction(4, 7, 5)
    assert (right.family, right.parameter_s) == ("RIGHT_ODD", 3)
