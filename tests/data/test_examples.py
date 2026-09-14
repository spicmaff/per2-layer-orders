from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(name: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    cp = subprocess.run(
        [sys.executable, str(ROOT / "examples" / name)],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(cp.stdout)


def test_minimal_examples_execute() -> None:
    c = _run("classify_period_word.py")
    assert c["word"] == "MMMMVV"
    assert c["regime"] == "CONSTANT_RHO_PLUS"

    v = _run("validate_labelled_state.py")
    assert v["accepted"] is True
    assert v["violations"] == []

    m = _run("construct_mmmmvv_state.py")
    assert m["requested_pivots"] == [3, 3]
    assert m["recovered_pivots"] == [3, 3]
    assert m["independent_semantic_acceptance"] is True
