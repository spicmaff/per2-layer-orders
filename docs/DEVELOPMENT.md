# Development

The central dependency firewall is enforced in code and tests:

`model/period -> semantics` and `model/period -> theory`, with `validation` as the only layer importing both.

`per2.semantics` must never import `per2.theory`. Visualization/browser code must consume explicit exported statuses rather than infer them.

Recommended local loop:

```bash
pytest -q
make figures
python tools/check_generated.py
```

Full exact replay belongs to release validation rather than every edit.

## Optional browser layout QA

After building the Pages preview, the Explorer can be rendered through the containment harness:

```bash
PYTHONPATH=src:. python tools/build_web_preview.py
python tools/check_explorer_layout.py --screenshots
```

This optional check requires Python Playwright plus a Chromium executable (or `PER2_CHROMIUM_EXECUTABLE`). It does not recompute mathematics: it embeds the already-generated scientific JSON and exercises the render-only Explorer across the approved sentinel scenes and desktop/mobile viewports.
