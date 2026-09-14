#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
js_root = root / "web/assets/js"
files = sorted(js_root.glob("*.js"))

# This is a policy tripwire, not a JavaScript theorem prover.  These patterns
# cover the specific scientific recomputations prohibited by the PER2 design.
forbidden_literals = [
    "Math.floor(",             # B_R formula must come from Python exports
    "DIRECTED_FOUR_CYCLE",    # witness types must not be fabricated in JS
    "BURIED_CLOSER",          # failure reason must come from the trace record
    "stack.push(",
    "stack.pop(",
    "classifyPeriod",
    "validateState",
    "enumerateStates",
    "recoverPivots",
]
forbidden_regex = [
    re.compile(r"\bbr_a\s*={2,3}\s*br_b\b"),
    re.compile(r"\bbr_b\s*={2,3}\s*br_a\b"),
    re.compile(r"\bfunction\s+(?:br|bl|compatible|validate|enumerate)\b", re.I),
    re.compile(r"\b(?:state|scene|s)\.a\s*={2,3}\s*(?:state|scene|s)\.b\b"),
    re.compile(r"\b(?:state|scene|s)\.a\s*={2,3}\s*1\b"),
]


violations: list[str] = []
for path in files:
    text = path.read_text(encoding="utf-8")
    for literal in forbidden_literals:
        if literal in text:
            violations.append(f"{path.relative_to(root)}: forbidden literal {literal!r}")
    for rx in forbidden_regex:
        if rx.search(text):
            violations.append(f"{path.relative_to(root)}: forbidden scientific comparison {rx.pattern!r}")

explorer = (js_root / "explorer.js").read_text(encoding="utf-8")
required_export_reads = [
    "r.compatible", "r.br_a", "r.br_b", "r.trace_id", "e.reason_code",
    "s.display.reason_label", "s.construction.layer_order_face_ids", "s.witness.edges",
]
for token in required_export_reads:
    if token not in explorer:
        violations.append(f"explorer.js missing expected exported-record read {token!r}")

if violations:
    raise SystemExit("browser trust-boundary policy failed:\n" + "\n".join(violations))

print(f"PASS: browser JS passes renderer-only scientific policy ({len(files)} modules checked)")
