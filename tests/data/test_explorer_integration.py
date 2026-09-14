from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_explorer_exposes_both_canonical_mechanisms_without_new_app():
    html = (ROOT / "web/explorer/index.html").read_text()
    js = (ROOT / "web/assets/js/explorer.js").read_text()
    assert 'id="mechanismSelect"' in html
    assert 'id="sceneSelect"' in html
    assert 'MVMMMM · LIFO' in html
    assert 'MMMMVV · boundary / diagonal' in html
    assert "mvp-mvmmmm-k3-v1.json" in js
    assert "mmmmvv-scenes-v1.json" in js
    assert "mechanism" in js and "scene" in js


def test_mmmmvv_browser_reads_exported_status_construction_and_witness():
    js = (ROOT / "web/assets/js/explorer.js").read_text()
    for token in [
        "s.display.reason_label",
        "s.construction.layer_order_face_ids",
        "s.witness.edges",
        "e.relation_label",
        "e.origin_label",
        "e.closes_cycle",
    ]:
        assert token in js
    # Tripwires: the prepared-scene browser must not implement the theorem tests.
    assert "state.a===state.b" not in js
    assert "scene.a===scene.b" not in js
    assert "s.a===s.b" not in js
    assert "DIRECTED_FOUR_CYCLE" not in js


def test_mmmmvv_static_fallbacks_exist():
    for name in [
        "mmmmvv_diagonal_success.svg",
        "mmmmvv_boundary_success.svg",
        "mmmmvv_interior_obstruction.svg",
    ]:
        text = (ROOT / "visualization/generated" / name).read_text()
        assert "<svg" in text and "<title>" in text and "<desc>" in text


def test_reduced_motion_policy_remains_in_site_css():
    css = (ROOT / "web/assets/css/site.css").read_text()
    assert "prefers-reduced-motion:reduce" in css
    assert "animation:none!important" in css
