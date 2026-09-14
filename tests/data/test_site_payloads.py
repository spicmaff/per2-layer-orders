import json
from pathlib import Path

from per2.export.site_data import write_all_site_data


def test_site_payloads(tmp_path: Path):
    write_all_site_data(tmp_path)
    mm = json.loads((tmp_path / "mmmmvv-fibres-v1.json").read_text())
    mv = json.loads((tmp_path / "mvmmmm-fibres-v1.json").read_text())
    traces = json.loads((tmp_path / "mvmmmm-traces-mvp-v1.json").read_text())
    rows = json.loads((tmp_path / "row-forms-v1.json").read_text())

    g4 = next(g for g in mm["groups"] if g["k"] == 4)
    assert sum(p["compatible"] for p in g4["pairs"]) == 19
    g4m = next(g for g in mv["groups"] if g["k"] == 4)
    assert sum(p["compatible"] for p in g4m["pairs"]) == 13

    cases = {(c["a"], c["b"]): c["trace"] for c in traces["cases"]}
    assert cases[(2, 3)]["compatible"] is True
    assert len(cases[(2, 3)]["events"]) == 12
    assert cases[(2, 4)]["failure"]["type"] == "BURIED_CLOSER"
    assert cases[(2, 4)]["failure"]["requested_closer"] == 3
    assert cases[(2, 4)]["failure"]["blocking_label"] == 6

    assert any(r["k"] == 3 and r["pivot"] == 3 and r["plus"] == [3, 1, 2, 5, 6, 4] for r in rows["records"])


def test_map_explorer_mvp_payload(tmp_path: Path):
    from per2.export.site_data import write_map_explorer_mvp
    write_map_explorer_mvp(tmp_path / "explorer.json")
    d = json.loads((tmp_path / "explorer.json").read_text())
    assert d["map"]["k"] == 3
    assert d["map"]["word"] == "MVMMMM"
    assert len(d["pairs"]) == 25
    assert sum(p["compatible"] for p in d["pairs"]) == 9
    assert len(d["traces"]) == 25
    success = next(p for p in d["pairs"] if (p["a"], p["b"]) == (2, 3))
    st = d["traces"][success["trace_id"]]
    assert st["success"] is True
    assert st["final_layer_order"] == ["A3","A5","A6","A4","B4","B6","B5","A1","A2","B2","B1","B3"]
    fail = next(p for p in d["pairs"] if (p["a"], p["b"]) == (2, 4))
    ft = d["traces"][fail["trace_id"]]
    assert ft["success"] is False
    assert ft["failure"]["failure_type"] == "BURIED_CLOSER"
    assert ft["failure"]["stack_snapshot"] == ["H3","H5","H6"]
    assert ft["failure"]["blocking_label"] == "H6"
    assert ft["events"][-1]["status"] == "failed_candidate"
    assert "B3" not in ft["events"][-1]["emitted_prefix_after"]
