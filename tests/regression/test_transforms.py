from per2.model import PeriodWord
from per2.transforms import transform_word


def test_known_word_orbits():
    base = PeriodWord.from_code("MMMMVV")
    assert transform_word(base, "R").code == "MMVVMM"
    assert transform_word(base, "C").code == "VVVVMM"
    assert transform_word(base, "CR").code == "VVMMVV"

    base = PeriodWord.from_code("MVMMMM")
    assert transform_word(base, "H").code == "VMMMMM"
    assert transform_word(base, "C").code == "VMVVVV"
    assert transform_word(base, "CH").code == "MVVVVV"
