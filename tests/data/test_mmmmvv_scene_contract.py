import json
from pathlib import Path

from per2.export.site_data import write_mmmmvv_explorer_scenes
from per2.model import PeriodWord, parse_face_label
from per2.period import expand_period
from per2.semantics.validity import validate_state
from per2.theory.pivots import recover_pivots


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_mmmmvv_scene_contract_sentinels(tmp_path: Path):
    path = tmp_path / "mmmmvv-scenes-v1.json"
    write_mmmmvv_explorer_scenes(path)
    data = _load(path)

    assert data["dataset_id"] == "per2.explorer.mmmmvv.scenes.v1"
    assert data["map"]["word"] == "MMMMVV"
    assert data["map"]["k"] == 4
    assert len(data["scenes"]) == 3
    assert "not_a_physical_folding_path" in data["honesty_flags"]
    assert "browser_does_not_compute_scientific_status" in data["honesty_flags"]

    diagonal = next(s for s in data["scenes"] if (s["a"], s["b"]) == (3, 3))
    assert diagonal["compatible"] is True
    assert diagonal["scene_kind"] == "compatible_construction"
    assert diagonal["regime"] == "two_nonconstant_rows"
    assert diagonal["canonical_representative"] == "MMMMVV"
    assert diagonal["display"]["name"] == "Diagonal success"
    assert diagonal["construction"]["construction_family"] == "DIAGONAL"
    assert diagonal["construction"]["independent_semantic_check"]["accepted"] is True
    assert len(diagonal["construction"]["layer_order"]) == 16

    boundary = next(s for s in data["scenes"] if (s["a"], s["b"]) == (1, 4))
    assert boundary["compatible"] is True
    assert boundary["display"]["name"] == "Boundary success"
    assert boundary["construction"]["construction_family"] == "LEFT_EVEN"
    assert boundary["construction"]["parameter_s"] == 2
    assert boundary["construction"]["independent_semantic_check"]["accepted"] is True

    obstruction = next(s for s in data["scenes"] if (s["a"], s["b"]) == (2, 3))
    assert obstruction["compatible"] is False
    assert obstruction["scene_kind"] == "directed_cycle_obstruction"
    assert obstruction["display"]["name"] == "Interior obstruction"
    assert obstruction["construction"] is None
    assert obstruction["witness"]["type"] == "DIRECTED_FOUR_CYCLE"
    assert obstruction["witness"]["cycle_labels"] == ["A4", "A1", "B1", "B4", "A4"]
    assert [e["origin"] for e in obstruction["witness"]["edges"]] == [
        "UPPER_ROW", "HORIZONTAL_ODD", "LOWER_ROW", "HORIZONTAL_EVEN"
    ]
    assert [e["reveal_index"] for e in obstruction["witness"]["edges"]] == [1, 2, 3, 4]
    assert [e["closes_cycle"] for e in obstruction["witness"]["edges"]] == [False, False, False, True]
    assert "layer_order" not in obstruction


def test_mmmmvv_success_states_are_semantically_valid_and_recover_requested_pivots(tmp_path: Path):
    path = tmp_path / "mmmmvv-scenes-v1.json"
    write_mmmmvv_explorer_scenes(path)
    data = _load(path)
    assignment = expand_period(PeriodWord.from_code("MMMMVV"), 4)
    for scene in data["scenes"]:
        if not scene["compatible"]:
            continue
        state = tuple(parse_face_label(8, label) for label in scene["construction"]["layer_order"])
        assert validate_state(assignment, state)
        assert recover_pivots(state, 8) == (scene["a"], scene["b"])


def test_mmmmvv_scene_export_is_byte_deterministic(tmp_path: Path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    write_mmmmvv_explorer_scenes(a)
    write_mmmmvv_explorer_scenes(b)
    assert a.read_bytes() == b.read_bytes()
