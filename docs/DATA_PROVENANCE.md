# Data provenance

Public records use these epistemic roles:

- `theorem_derived` — symbolic formulas proved in the manuscript;
- `independent_finite_validation` — exact bounded enumeration or theorem-blind single-state checking;
- `author_reproduction_output` — retained outputs from the publication reproduction package;
- `generated_view_cache` — renderer/site payload generated from an upstream scientific record.

The committed `reference/classification/*.csv` files are retained canonical theorem-derived publication records.

`reference/validation/k2_exact_states.json` has a top-level role of `independent_finite_validation` because the exact states are enumerated by the theorem-blind semantic oracle. Any pivot coordinates attached to those states are separately marked with `pivots_provenance.epistemic_role = theorem_derived`; they are annotations on the enumerated states, not part of the independent membership evidence. Per-state semantic acceptance is likewise labelled `independent_finite_validation`.

Browser/site payloads are generated caches and are never a source of scientific truth. In particular:

- `mvp-mvmmmm-k3-v1.json` contains theorem-derived compatibility/LIFO records for the fixed expert MVP;
- `mmmmvv-scenes-v1.json` contains theorem-derived Appendix-D construction records and the directed-cycle obstruction witness, plus explicitly separate theorem-blind single-state checks for the two prepared compatible constructions.
