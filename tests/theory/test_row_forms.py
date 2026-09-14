from per2.theory import column_word, row_order


def test_k3_known_row_forms():
    assert column_word(3, 3) == (3, 1, 2, 5, 6, 4)
    assert column_word(3, 4) == (5, 6, 3, 1, 2, 4)
    assert row_order(3, 3, "-") == tuple(reversed(column_word(3, 3)))


def test_all_pivots_permutations_and_endpoints():
    for k in range(2, 13):
        n = 2 * k
        seen = set()
        for p in range(1, n):
            w = column_word(k, p)
            assert set(w) == set(range(1, n + 1))
            assert {w[0], w[-1]} == {p, p + 1}
            seen.add(w)
        assert len(seen) == n - 1
