# Minimal executable examples

These examples are intentionally small and preserve the scientific trust boundary.

Run from an installed checkout, or locally with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python examples/classify_period_word.py
PYTHONPATH=src python examples/validate_labelled_state.py
PYTHONPATH=src python examples/construct_mmmmvv_state.py
```

- `classify_period_word.py` uses the theorem/prediction layer.
- `validate_labelled_state.py` uses only the theorem-blind semantic membership oracle.
- `construct_mmmmvv_state.py` constructs an explicit theorem-side compatible state and then submits that literal order to the independent semantic validator. The semantic validator does not know the `MMMMVV` compatibility theorem.

They are examples, not alternate implementations of the mathematics.
