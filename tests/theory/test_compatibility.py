from per2.theory import mmmmvv_compatibility, mvmmmm_compatibility, br, bl


def test_mmmmvv_k2_exact_pairs():
    got = {(a, b) for a in range(1, 4) for b in range(1, 4) if mmmmvv_compatibility(2, a, b).compatible}
    assert got == {(1,1),(1,2),(1,3),(2,2),(3,1),(3,2),(3,3)}
    bad = mmmmvv_compatibility(2, 2, 1)
    assert not bad.compatible
    assert bad.witness["cycle"] == ["A4", "A1", "B1", "B4", "A4"]


def test_mvmmmm_blocks_and_reflection():
    got = {(a, b) for a in range(1, 4) for b in range(1, 4) if mvmmmm_compatibility(2, a, b).compatible}
    assert got == {(1,1),(2,2),(2,3),(3,2),(3,3)}
    assert br(1) == 0 and br(2) == br(3) == 1
    assert [bl(p, 4) for p in (1,2,3)] == [1,1,0]
