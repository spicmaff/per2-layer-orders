#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
env = {**os.environ, "PYTHONPATH": str(root / "src")}
visual_env = {**env, "PYTHONPATH": f"{root / 'src'}:{root}"}


def fail(message: str) -> None:
    raise SystemExit(message)


def compare_bytes(generated: Path, committed: Path, label: str) -> None:
    if generated.read_bytes() != committed.read_bytes():
        fail(f"{label} differs from committed canonical output: {committed.relative_to(root)}")


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    subprocess.run(
        [sys.executable, "-m", "per2.cli", "export-reference", "--root", str(tmp), "--k2-states"],
        check=True,
        env=env,
        stdout=subprocess.DEVNULL,
    )

    generated = list(csv.DictReader((tmp / "reference/classification/all64.generated.csv").open()))
    canonical = list(csv.DictReader((root / "reference/classification/all64.csv").open()))
    if generated != canonical:
        fail("generated all64 table differs from committed canonical table")

    compare_bytes(
        tmp / "reference/validation/k2_exact_states.json",
        root / "reference/validation/k2_exact_states.json",
        "k=2 exact-state export",
    )
    compare_bytes(
        tmp / "web/data/classification-v1.json",
        root / "web/data/classification-v1.json",
        "site classification export",
    )

    # Site-only payloads are intentionally generated, not committed.  Generate
    # them twice and require byte-identical file sets and contents.
    site_a = tmp / "site-a"
    site_b = tmp / "site-b"
    code = (
        "from pathlib import Path; "
        "from per2.export.site_data import write_all_site_data; "
        "write_all_site_data(Path(__import__('sys').argv[1]))"
    )
    for target in (site_a, site_b):
        subprocess.run([sys.executable, "-c", code, str(target)], check=True, env=env)
    files_a = sorted(p.relative_to(site_a) for p in site_a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(site_b) for p in site_b.rglob("*") if p.is_file())
    if files_a != files_b:
        fail("site-data generation produced different file sets across two runs")
    for rel in files_a:
        if (site_a / rel).read_bytes() != (site_b / rel).read_bytes():
            fail(f"site-data generation is nondeterministic: {rel}")

# Capture the committed SVG bytes *before* regeneration.  Renderers write to
# fixed public paths, so this is the regression oracle.  If regeneration
# differs, restore the original bytes before failing to avoid dirtying a tree
# merely by running the check.
svg_names = [
    "01_regime_atlas.svg",
    "02_row_pivot_lab.svg",
    "03_mmmmvv_lab.svg",
    "04_mvmmmm_lab.svg",
    "05_map_explorer_success.svg",
    "06_map_explorer_failure.svg",
    "mmmmvv_diagonal_success.svg",
    "mmmmvv_boundary_success.svg",
    "mmmmvv_interior_obstruction.svg",
]
svg_paths = {name: root / "visualization/generated" / name for name in svg_names}
expected_svg = {name: path.read_bytes() for name, path in svg_paths.items()}

try:
    for script in [
        "render_atlas.py",
        "render_row_form.py",
        "render_mmmmvv.py",
        "render_mvmmmm.py",
        "render_map_explorer_mvp.py",
        "render_mmmmvv_explorer_scenes.py",
    ]:
        subprocess.run(
            [sys.executable, str(root / "visualization/static" / script)],
            check=True,
            cwd=root,
            env=visual_env,
            stdout=subprocess.DEVNULL,
        )

    changed = [name for name, path in svg_paths.items() if path.read_bytes() != expected_svg[name]]
    if changed:
        for name, path in svg_paths.items():
            path.write_bytes(expected_svg[name])
        fail("deterministic SVG regeneration differs from committed bytes: " + ", ".join(changed))
finally:
    # In case a renderer raised after writing only part of its output, restore
    # the pre-check snapshot so the check is side-effect free.
    for name, path in svg_paths.items():
        if path.exists() and path.read_bytes() != expected_svg[name]:
            path.write_bytes(expected_svg[name])

print(
    "PASS: theorem table, exact-state export, site payloads, and all nine static SVGs regenerate deterministically"
)
