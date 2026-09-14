import csv
from pathlib import Path

from per2.model import PeriodWord
from per2.theory import classify_period

ROOT = Path(__file__).resolve().parents[2]


def test_committed_all64_matches_theory():
    rows = list(csv.DictReader((ROOT / "reference/classification/all64.csv").open()))
    assert len(rows) == 64
    for row in rows:
        c = classify_period(PeriodWord.from_code(row["P"]))
        assert row["regime"] == c.regime
        assert row["rho"] == str(c.rho)
        assert row["tau"] == str(c.tau)
        assert row["delta0"] == str(c.delta0)
        assert row["delta1"] == str(c.delta1)
        assert row["C_P(k)"] == c.count_formula


def test_k2_exact_state_provenance_separates_enumeration_from_theorem_annotations():
    import json
    payload = json.loads((ROOT / "reference/validation/k2_exact_states.json").read_text())
    assert payload["provenance"]["epistemic_role"] == "independent_finite_validation"
    seen_pivot_annotation = False
    for word in payload["words"]:
        for state in word["states"]:
            assert state["semantic_validation"]["accepted"] is True
            assert state["semantic_validation"]["provenance"]["epistemic_role"] == "independent_finite_validation"
            if state["features"]["pivots"] is not None:
                seen_pivot_annotation = True
                assert state["features"]["pivots_provenance"]["epistemic_role"] == "theorem_derived"
    assert seen_pivot_annotation
