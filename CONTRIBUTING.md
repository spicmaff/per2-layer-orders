# Contributing

This repository is a paper-specific research artifact. Small, reviewable fixes are preferred over broad refactors.

## Scientific boundary

- `per2.semantics` is theorem-blind and must not import theorem/prediction code.
- `per2.theory` contains symbolic classification and construction logic.
- `per2.validation` is the intentional comparison boundary.
- Browser/visualization code renders exported records and must not recompute compatibility, validity, pivots, witnesses, or forced events.

Any refactor touching scientific behavior should include characterization or regression coverage.

## Before opening a pull request

```bash
python -m pip install -e '.[test]'
pytest -q
python tools/check_import_boundaries.py
make figures
python tools/check_generated.py
make site
python tools/check_browser_trust_boundary.py
python tools/check_public_tree.py
```

For scientific-data or release changes, also run the full bounded validation described in `docs/REPRODUCIBILITY.md`.

Do not commit private audit material, chat logs, planning archives, local virtual environments, caches, credentials, or machine-local paths.
