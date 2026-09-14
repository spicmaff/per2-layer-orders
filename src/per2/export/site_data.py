from __future__ import annotations

import json
from pathlib import Path

from per2.model import PeriodWord, face_label, parse_face_label
from per2.period import expand_period
from per2.semantics.constraints import compile_constraints
from per2.semantics.validity import validate_state
from per2.semantics.orientation import light_up_by_checkerboard, target_class
from per2.theory import (
    br,
    mmmmvv_explicit_construction,
    mmmmvv_compatibility,
    mvmmmm_compatibility,
    mvmmmm_lifo_trace,
    row_formula_blocks,
    row_order,
    recover_pivots,
)
from .provenance import provenance


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_row_forms(path: Path, k_min: int = 2, k_max: int = 12) -> None:
    records = []
    for k in range(k_min, k_max + 1):
        for p in range(1, 2 * k):
            plus = row_order(k, p, "+")
            minus = row_order(k, p, "-")
            records.append({
                "k": k,
                "pivot": p,
                "physical_seam": {"left_column": p, "right_column": p + 1},
                "first_last_plus": [plus[0], plus[-1]],
                "first_last_minus": [minus[0], minus[-1]],
                "plus": list(plus),
                "minus": list(minus),
                "formula_blocks": row_formula_blocks(k, p),
            })
    _write(path, {
        "schema_version": "1.0",
        "dataset_id": "per2.theorem.row_forms",
        "provenance": provenance("theorem_derived", "per2.theory.row_forms", k_range=[k_min, k_max]),
        "records": records,
    })


def write_mmmmvv(path: Path, k_min: int = 2, k_max: int = 12) -> None:
    groups = []
    for k in range(k_min, k_max + 1):
        pairs = []
        for a in range(1, 2 * k):
            for b in range(1, 2 * k):
                rec = mmmmvv_compatibility(k, a, b)
                pairs.append({"a": a, "b": b, **rec.as_dict()})
        groups.append({"k": k, "m": 2 * k - 1, "pairs": pairs})
    _write(path, {
        "schema_version": "1.0",
        "dataset_id": "per2.theorem.mmmmvv_fibres",
        "provenance": provenance("theorem_derived", "per2.theory.compatibility", family="MMMMVV", k_range=[k_min, k_max]),
        "groups": groups,
    })


def write_mvmmmm(path: Path, k_min: int = 2, k_max: int = 12) -> None:
    groups = []
    for k in range(k_min, k_max + 1):
        pairs = []
        for a in range(1, 2 * k):
            for b in range(1, 2 * k):
                rec = mvmmmm_compatibility(k, a, b)
                pairs.append({
                    "a": a, "b": b, "br_a": br(a), "br_b": br(b),
                    "compatible": rec.compatible, "reasons": list(rec.reasons)
                })
        groups.append({"k": k, "m": 2 * k - 1, "pairs": pairs})
    _write(path, {
        "schema_version": "1.0",
        "dataset_id": "per2.theorem.mvmmmm_fibres",
        "provenance": provenance("theorem_derived", "per2.theory.compatibility", family="MVMMMM", k_range=[k_min, k_max]),
        "groups": groups,
    })


def write_mvmmmm_mvp_traces(path: Path) -> None:
    """Legacy compact sentinel payload retained for the canonical MVMMMM lab."""
    cases = []
    for a, b in [(2, 3), (2, 4)]:
        tr = mvmmmm_lifo_trace(3, a, b)
        cases.append({"a": a, "b": b, "trace": tr.as_dict()})
    _write(path, {
        "schema_version": "1.0",
        "dataset_id": "per2.theorem.mvmmmm_mvp_traces",
        "provenance": provenance("theorem_derived", "per2.theory.traces", family="MVMMMM", k=3, scope="expert MVP sentinels"),
        "cases": cases,
    })


def _face_label(row: str, column: int) -> str:
    return f"{row}{column}"


def _normalize_trace(k: int, a: int, b: int) -> dict:
    """Convert the theorem-side trace to the browser scene contract.

    This function adds presentation metadata (stream heads and emitted prefixes)
    but never decides a new mathematical event: every action/status originates in
    ``mvmmmm_lifo_trace``.
    """
    tr = mvmmmm_lifo_trace(k, a, b)
    upper = list(tr.upper_stream)
    lower = list(tr.lower_closer_stream)
    ui = 0
    li = 0
    committed: list[str] = []
    events: list[dict] = []
    for idx, ev in enumerate(tr.events):
        upper_before = _face_label("A", upper[ui]) if ui < len(upper) else None
        lower_before = _face_label("B", lower[li]) if li < len(lower) else None
        if ev.action == "PUSH" and ev.status != "FAILED_CANDIDATE":
            ui += 1
        elif ev.action == "POP" and ev.status != "FAILED_CANDIDATE":
            li += 1
        if ev.status != "FAILED_CANDIDATE":
            committed.append(ev.face)
        upper_after = _face_label("A", upper[ui]) if ui < len(upper) else None
        lower_after = _face_label("B", lower[li]) if li < len(lower) else None
        events.append({
            "event_index": idx,
            "display_step": ev.step,
            "source_row": ev.face[0],
            "face_id": f"face:{ev.face}",
            "face_label": ev.face,
            "column": ev.column,
            "horizontal_crease_id": f"crease:H{ev.column}",
            "horizontal_role": "opener" if ev.action == "PUSH" else ("closer" if ev.action == "POP" else "candidate_fail"),
            "action": ev.action.lower(),
            "stack_before": [f"crease:H{x}" for x in ev.stack_before],
            "stack_after": [f"crease:H{x}" for x in ev.stack_after],
            "stack_before_labels": [f"H{x}" for x in ev.stack_before],
            "stack_after_labels": [f"H{x}" for x in ev.stack_after],
            "upper_head_before": upper_before,
            "lower_head_before": lower_before,
            "upper_head_after": upper_after,
            "lower_head_after": lower_after,
            "status": "failed_candidate" if ev.status == "FAILED_CANDIDATE" else "forced",
            "reason_code": ev.reason_code,
            "requested_closer": f"H{ev.requested_closer}" if ev.requested_closer is not None else None,
            "blocking_label": f"H{ev.blocking_label}" if ev.blocking_label is not None else None,
            "emitted_prefix_after": list(committed),
        })

    failure = None
    if tr.failure:
        failure = {
            "failure_type": tr.failure["type"],
            "requested_closer": f"H{tr.failure['requested_closer']}" if tr.failure.get("requested_closer") is not None else None,
            "blocking_label": f"H{tr.failure['blocking_label']}" if tr.failure.get("blocking_label") is not None else None,
            "stack_snapshot": [f"H{x}" for x in tr.failure.get("stack", [])],
            "candidate_face_id": events[-1]["face_id"] if events and events[-1]["status"] == "failed_candidate" else None,
        }
    final_order = [ev["face_label"] for ev in events if ev["status"] != "failed_candidate"] if tr.compatible else None
    return {
        "id": f"trace:theorem:MVMMMM:k{k}:a{a}:b{b}",
        "trace_kind": "lifo_reconstruction",
        "success": tr.compatible,
        "upper_stream_columns": upper,
        "lower_closer_stream_columns": lower,
        "events": events,
        "failure": failure,
        "final_layer_order": final_order,
        "not_physical_motion": True,
        "provenance": provenance(
            "theorem_derived",
            "per2.theory.traces.mvmmmm_lifo_trace",
            family="MVMMMM",
            k=k,
            pivots=[a, b],
        ),
    }


def _export_map(word_code: str, k: int) -> dict:
    n = 2 * k
    word = PeriodWord.from_code(word_code)
    m = expand_period(word, k)
    constraints = compile_constraints(m)
    precedence = {key: (above, below) for above, below, key in constraints.precedence}
    faces = []
    for fid in m.faces:
        label = face_label(n, fid)
        row = label[0]
        column = int(label[1:])
        faces.append({
            "id": f"face:{label}",
            "label": label,
            "row": row,
            "column": column,
            "checkerboard_class": "light_up" if light_up_by_checkerboard(m, fid) else "dark_up",
        })
    creases = []
    for c in m.creases:
        before, after = precedence[c.key]
        creases.append({
            "id": f"crease:{c.key}",
            "label": c.key,
            "kind": c.kind,
            "index": c.index,
            "face_ids": [f"face:{face_label(n, c.a)}", f"face:{face_label(n, c.b)}"],
            "period_slot": (c.index - 1) % 2,
            "mv": c.label,
            "target_class": target_class(c),
            "precedence": {"before_face": f"face:{face_label(n, before)}", "after_face": f"face:{face_label(n, after)}"},
        })
    return {
        "id": f"map:{word_code}:k{k}",
        "k": k,
        "n": n,
        "word": word_code,
        "faces": faces,
        "creases": creases,
        "row_face_ids": {
            "A": [f"face:A{c}" for c in range(1, n + 1)],
            "B": [f"face:B{c}" for c in range(1, n + 1)],
        },
        "coordinate_convention": "2x2k_rectangular_unfolded",
        "provenance": provenance("theorem_derived", "per2.period.expand_period + per2.semantics.constraints", family=word_code, k=k),
    }


def _export_map_mvmmmm_k3() -> dict:
    return _export_map("MVMMMM", 3)


def _mmmmvv_row_scene(k: int, row: str, pivot: int) -> dict:
    columns = list(row_order(k, pivot, "+"))
    labels = [f"{row}{c}" for c in columns]
    return {
        "row": row,
        "sign": "+",
        "pivot": pivot,
        "pivot_crease_id": f"crease:{'U' if row == 'A' else 'L'}{pivot}",
        "physical_order_face_ids": [f"face:{row}{c}" for c in range(1, 2 * k + 1)],
        "layer_order_face_ids": [f"face:{label}" for label in labels],
        "first_face_id": f"face:{labels[0]}",
        "last_face_id": f"face:{labels[-1]}",
        "scope": "row_local",
    }


def _mmmmvv_scene(k: int, a: int, b: int, scene_id: str) -> dict:
    rec = mmmmvv_compatibility(k, a, b)
    if rec.compatible and "DIAGONAL" in rec.reasons:
        display_name = "Diagonal success"
        reason_label = "diagonal compatible"
        reason_summary = f"The exported theorem record marks this prepared pair as diagonal: a=b={a}."
    elif rec.compatible:
        display_name = "Boundary success"
        reason_label = "boundary compatible"
        reason_summary = "The exported theorem record marks the selected upper pivot as a boundary seam."
    else:
        display_name = "Interior obstruction"
        reason_label = "interior off-diagonal obstruction"
        reason_summary = "The exported theorem witness is a directed four-cycle, so no strict total layer order can satisfy all four inequalities."

    base = {
        "id": scene_id,
        "family": "MMMMVV",
        "k": k,
        "a": a,
        "b": b,
        "upper_pivot_id": f"pivot:A:{a}",
        "lower_pivot_id": f"pivot:B:{b}",
        "compatible": rec.compatible,
        "reason_codes": list(rec.reasons),
        "regime": "two_nonconstant_rows",
        "canonical_representative": "MMMMVV",
        "display": {
            "name": display_name,
            "compatibility_label": "compatible" if rec.compatible else "incompatible",
            "reason_label": reason_label,
            "reason_summary": reason_summary,
        },
        "upper_row": _mmmmvv_row_scene(k, "A", a),
        "lower_row": _mmmmvv_row_scene(k, "B", b),
        "not_physical_motion": True,
        "provenance": provenance("theorem_derived", "per2.theory.compatibility", family="MMMMVV", k=k, pivots=[a, b]),
    }
    if rec.compatible:
        construction = mmmmvv_explicit_construction(k, a, b)
        state = tuple(parse_face_label(2 * k, label) for label in construction.order_labels)
        if recover_pivots(state, 2 * k) != (a, b):
            raise AssertionError((a, b, construction))
        accepted = validate_state(expand_period(PeriodWord.from_code("MMMMVV"), k), state)
        if not accepted:
            raise AssertionError((a, b, construction.order_labels))
        base["scene_kind"] = "compatible_construction"
        base["construction"] = {
            "construction_family": construction.family,
            "parameter_s": construction.parameter_s,
            "layer_order": list(construction.order_labels),
            "layer_order_face_ids": [f"face:{label}" for label in construction.order_labels],
            "trace_available": False,
            "construction_provenance": provenance(
                "theorem_derived",
                "per2.theory.constructions.mmmmvv_explicit_construction",
                family="MMMMVV",
                k=k,
                pivots=[a, b],
            ),
            "independent_semantic_check": {
                "accepted": True,
                "provenance": provenance(
                    "independent_finite_validation",
                    "per2.semantics.validity.validate_state",
                    family="MMMMVV",
                    k=k,
                    pivots=[a, b],
                    scope="single theorem-constructed state",
                ),
            },
        }
        base["witness"] = None
    else:
        witness = rec.witness or {}
        cycle = list(witness.get("cycle", []))
        origins = list(witness.get("edge_origins", []))
        if len(cycle) != 5 or len(origins) != 4:
            raise AssertionError(witness)
        base["scene_kind"] = "directed_cycle_obstruction"
        base["construction"] = None
        base["witness"] = {
            "type": witness["type"],
            "cycle_labels": cycle,
            "cycle_face_ids": [f"face:{label}" for label in cycle],
            "edges": [
                {
                    "from_face_id": f"face:{cycle[i]}",
                    "to_face_id": f"face:{cycle[i + 1]}",
                    "from_label": cycle[i],
                    "to_label": cycle[i + 1],
                    "relation_label": f"{cycle[i]} ≺ {cycle[i + 1]}",
                    "origin": origins[i],
                    "origin_label": {
                        "UPPER_ROW": "upper-row order",
                        "LOWER_ROW": "lower-row order",
                        "HORIZONTAL_ODD": "odd horizontal crease",
                        "HORIZONTAL_EVEN": "even horizontal crease",
                    }[origins[i]],
                    "reveal_index": i + 1,
                    "closes_cycle": i == 3,
                }
                for i in range(4)
            ],
            "final_status_label": "obstruction complete · directed cycle closed",
            "odd_column": witness["odd_column"],
            "even_column": witness["even_column"],
            "provenance": provenance(
                "theorem_derived",
                "per2.theory.compatibility.mmmmvv_compatibility",
                family="MMMMVV",
                k=k,
                pivots=[a, b],
            ),
        }
    return base


def write_mmmmvv_explorer_scenes(path: Path) -> None:
    """Export the next approved MMMMVV Explorer batch without browser mathematics.

    The records deliberately contain two theorem constructions and one theorem
    obstruction witness.  Browser integration is downstream; this file is the
    scientific scene contract.
    """
    k = 4
    scenes = [
        _mmmmvv_scene(k, 3, 3, "scene:MMMMVV:k4:diagonal:a3:b3"),
        _mmmmvv_scene(k, 1, 4, "scene:MMMMVV:k4:boundary:a1:b4"),
        _mmmmvv_scene(k, 2, 3, "scene:MMMMVV:k4:obstruction:a2:b3"),
    ]
    _write(path, {
        "schema_version": "1.0",
        "dataset_id": "per2.explorer.mmmmvv.scenes.v1",
        "scientific_scope": "fixed k=4 canonical MMMMVV scene contract: diagonal success, boundary success, interior off-diagonal obstruction",
        "honesty_flags": ["not_a_physical_folding_path", "browser_does_not_compute_scientific_status"],
        "map": _export_map("MMMMVV", k),
        "scenes": scenes,
        "sentinels": {
            "diagonal_success": scenes[0]["id"],
            "boundary_success": scenes[1]["id"],
            "interior_obstruction": scenes[2]["id"],
        },
        "provenance": provenance("theorem_derived", "per2.export.site_data.write_mmmmvv_explorer_scenes", family="MMMMVV", k=k),
    })


def write_map_explorer_mvp(path: Path) -> None:
    """Export the complete fixed-k=3 canonical MVMMMM expert MVP.

    All 25 pivot pairs are exported.  Compatibility and traces are theorem-side
    records; the browser is only a renderer/selector.
    """
    k = 3
    n = 6
    row_forms = {"A": [], "B": []}
    for p in range(1, 2 * k):
        plus = row_order(k, p, "+")
        minus = row_order(k, p, "-")
        row_forms["A"].append({
            "id": f"rowform:MVMMMM:k3:A:p{p}",
            "row": "A",
            "sign": "+",
            "pivot": p,
            "pivot_crease_id": f"crease:U{p}",
            "physical_order_face_ids": [f"face:A{c}" for c in range(1, n + 1)],
            "layer_order_face_ids": [f"face:A{c}" for c in plus],
            "first_face_id": f"face:A{plus[0]}",
            "last_face_id": f"face:A{plus[-1]}",
            "pivot_incident_face_ids": [f"face:A{p}", f"face:A{p+1}"],
            "formula_blocks": row_formula_blocks(k, p),
            "scope": "row_local",
        })
        row_forms["B"].append({
            "id": f"rowform:MVMMMM:k3:B:p{p}",
            "row": "B",
            "sign": "-",
            "pivot": p,
            "pivot_crease_id": f"crease:L{p}",
            "physical_order_face_ids": [f"face:B{c}" for c in range(1, n + 1)],
            "layer_order_face_ids": [f"face:B{c}" for c in minus],
            "first_face_id": f"face:B{minus[0]}",
            "last_face_id": f"face:B{minus[-1]}",
            "pivot_incident_face_ids": [f"face:B{p}", f"face:B{p+1}"],
            "formula_blocks": row_formula_blocks(k, p),
            "scope": "row_local",
        })

    pairs = []
    traces = {}
    for a in range(1, 2 * k):
        for b in range(1, 2 * k):
            comp = mvmmmm_compatibility(k, a, b)
            trace = _normalize_trace(k, a, b)
            if bool(comp.compatible) != bool(trace["success"]):
                raise AssertionError((a, b, comp, trace["success"]))
            tid = trace["id"]
            traces[tid] = trace
            pairs.append({
                "id": f"compat:MVMMMM:k3:a{a}:b{b}",
                "a": a,
                "b": b,
                "upper_pivot_id": f"pivot:A:{a}",
                "lower_pivot_id": f"pivot:B:{b}",
                "br_a": br(a),
                "br_b": br(b),
                "compatible": comp.compatible,
                "reason_codes": list(comp.reasons),
                "trace_id": tid,
                "layer_order": trace["final_layer_order"],
                "provenance": provenance("theorem_derived", "per2.theory.compatibility + per2.theory.traces", family="MVMMMM", k=3, pivots=[a, b]),
            })

    payload = {
        "schema_version": "1.0",
        "dataset_id": "per2.explorer.mvp.mvmmmm.k3",
        "title": "Map & Layer-Order Explorer MVP",
        "scientific_scope": "fixed k=3 canonical MVMMMM; theorem-derived combinatorial reconstruction",
        "honesty_flags": ["not_a_physical_folding_path", "browser_does_not_compute_scientific_status"],
        "map": _export_map_mvmmmm_k3(),
        "row_forms": row_forms,
        "pairs": pairs,
        "traces": traces,
        "defaults": {"a": 2, "b": 3, "annotation_level": "basic", "stack_mode": "literal", "motion": False},
        "sentinels": {"success": {"a": 2, "b": 3}, "failure": {"a": 2, "b": 4}},
        "provenance": provenance("theorem_derived", "per2.export.site_data.write_map_explorer_mvp", family="MVMMMM", k=3),
    }
    _write(path, payload)


def write_all_site_data(root: Path) -> None:
    write_row_forms(root / "row-forms-v1.json")
    write_mmmmvv(root / "mmmmvv-fibres-v1.json")
    write_mvmmmm(root / "mvmmmm-fibres-v1.json")
    write_mvmmmm_mvp_traces(root / "mvmmmm-traces-mvp-v1.json")
    write_map_explorer_mvp(root / "explorer" / "mvp-mvmmmm-k3-v1.json")
    write_mmmmvv_explorer_scenes(root / "explorer" / "mmmmvv-scenes-v1.json")
