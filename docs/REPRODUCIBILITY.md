# Reproducibility

## Quick scientific tests

```bash
python -m pip install -e '.[test]'
pytest -q
```

## Full retained finite validation

```bash
per2 finite-validation --full
```

This enumerates exact labelled states for all 64 words at `k=2` and all formal words at `k=1`, checks canonical pivot fibres, and checks exact labelled state-set symmetry transports.

## Generate public reference exports

```bash
per2 export-reference --root . --k2-states
python tools/make_checksums.py reference
```

## Generate deterministic static views

```bash
make figures
```

The structural and Explorer fallback SVGs consume theorem/reference records and do not perform semantic validation in their renderers.

## Canonical baseline

The immutable canonical submission package used to seed this repository has SHA-256:

`511031dc9eaff0bfc57fe32a15ff9d826d192c405908e096fec208bd643707df`

The original publication reproduction package was replayed unchanged before refactoring. Its deterministic CSV/JSON/TikZ/SVG/text outputs matched the retained baseline exactly.
