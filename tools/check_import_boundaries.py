#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

root = Path(__file__).resolve().parents[1]
checks = [
    (root / "src/per2/semantics", "per2.theory", "per2.semantics must not import per2.theory"),
    (root / "src/per2/theory", "per2.semantics", "per2.theory must not import per2.semantics"),
]
violations: list[tuple[Path, str, str]] = []
for directory, forbidden_prefix, rule in checks:
    for path in directory.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name.startswith(forbidden_prefix):
                        violations.append((path, name.name, rule))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith(forbidden_prefix):
                    violations.append((path, module, rule))
if violations:
    for path, module, rule in violations:
        print(f"ERROR {path.relative_to(root)}: imports {module} ({rule})")
    raise SystemExit(1)
print("PASS: semantics and theorem packages are mutually import-independent")
