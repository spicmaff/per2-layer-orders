import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src/per2"


def _assert_no_imports(directory: Path, forbidden_prefix: str) -> None:
    for path in directory.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not n.name.startswith(forbidden_prefix) for n in node.names), (path, forbidden_prefix)
            if isinstance(node, ast.ImportFrom):
                assert not ((node.module or "").startswith(forbidden_prefix)), (path, forbidden_prefix)


def test_semantics_and_theory_are_mutually_import_independent():
    _assert_no_imports(ROOT / "semantics", "per2.theory")
    _assert_no_imports(ROOT / "theory", "per2.semantics")
