from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def test_static_visualizations_exist_and_carry_required_sentinels():
    expected = {
        "01_regime_atlas.svg": ["MMMMVV", "MVMMMM", "MMMVVM", "MMMMMM"],
        "02_row_pivot_lab.svg": ["pivot seam p=3", "F3", "F4"],
        "03_mmmmvv_lab.svg": ["A4", "A1", "B1", "B4", "Directed four-cycle"],
        "04_mvmmmm_lab.svg": ["(a,b)=(2,3)", "(a,b)=(2,4)", "BURIED_CLOSER"],
        "05_map_explorer_success.svg": ["(a,b)=(2,3)", "COMPLETE", "A3", "B3", "NOT PHYSICAL MOTION"],
        "06_map_explorer_failure.svg": ["(a,b)=(2,4)", "BURIED_CLOSER", "requested H3", "blocking top H6", "NOT PHYSICAL MOTION"],
        "mmmmvv_diagonal_success.svg": ["Diagonal success", "(a,b)=(3,3)", "diagonal compatible", "A3", "B3", "NOT PHYSICAL MOTION"],
        "mmmmvv_boundary_success.svg": ["Boundary success", "(a,b)=(1,4)", "boundary compatible", "A1", "B5", "NOT PHYSICAL MOTION"],
        "mmmmvv_interior_obstruction.svg": ["Interior obstruction", "(a,b)=(2,3)", "A4", "A1", "B1", "B4", "closes cycle", "NOT PHYSICAL MOTION"],
    }
    for name, needles in expected.items():
        p = ROOT / "visualization/generated" / name
        assert p.exists()
        text = p.read_text()
        for needle in needles:
            assert needle in text, (name, needle)
        assert "<svg" in text and "<title>" in text and "<desc>" in text
