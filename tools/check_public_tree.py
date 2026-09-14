#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[1]
skip_parts = {".git", ".venv", "build", ".pytest_cache", "__pycache__", "*.egg-info"}
forbidden_name_tokens = ("chat", "prompt", "handoff", "planner", "wireframe", "mockup", "internal_audit", "qa_status", "implementation_report")
forbidden_machine_strings = ("/mnt/data/", "/home/oai/", "/Users/", "C:\\Users\\", "file_000000", "github_pat_", "ghp_", "BEGIN PRIVATE KEY")
text_suffixes = {".md", ".txt", ".py", ".json", ".csv", ".yml", ".yaml", ".toml", ".html", ".js", ".css", ".tex", ".cff"}

violations: list[str] = []
for path in root.rglob("*"):
    rel = path.relative_to(root)
    if any(part in {".git", ".venv", "build", ".pytest_cache", "__pycache__"} or part.endswith(".egg-info") for part in rel.parts):
        continue
    if path.is_file():
        if path.resolve() == Path(__file__).resolve():
            continue
        lower_parts = [part.lower() for part in rel.parts]
        if path.name in {".env", ".env.local"} or path.suffix.lower() in {".pem", ".key", ".p12"}:
            violations.append(f"forbidden credential-like file: {rel}")
        if any(token in part for part in lower_parts for token in forbidden_name_tokens):
            violations.append(f"forbidden internal/planning path token: {rel}")
        if path.suffix.lower() in text_suffixes or path.name == "CITATION.cff":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for needle in forbidden_machine_strings:
                if needle in text:
                    violations.append(f"machine-local path/id leaked in {rel}: {needle}")

if violations:
    raise SystemExit("public-tree policy failed:\n" + "\n".join(sorted(set(violations))))
print("PASS: no chat/planner/handoff paths or machine-local sandbox identifiers in public tree")
